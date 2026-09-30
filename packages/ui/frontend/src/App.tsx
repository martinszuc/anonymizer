import { MotionConfig } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from "react";

import { connect, errorMessage, type ReviewBridge } from "./bridge";
import { EmptyState } from "./components/EmptyState";
import { ExportSheets, type ExportStep } from "./components/ExportSheets";
import { PageView } from "./components/PageView";
import { Sidebar, type SidebarTab } from "./components/Sidebar";
import { Toasts, type Toast } from "./components/Toasts";
import { Toolbar } from "./components/Toolbar";
import { PageImages } from "./pageImages";
import { hasCommand } from "./platform";
import { pagesWithoutText, steppedZoom, toggled } from "./review";
import type { Box, DocumentInfo, EntityInfo } from "./types";

const TOAST_MS = 4000;
const CANVAS_PADDING = 48;
const MIN_SCALE = 0.25;
const MAX_FIT_SCALE = 2;

export function App() {
  const [bridge, setBridge] = useState<ReviewBridge | null>(null);
  const [document, setDocument] = useState<DocumentInfo | null>(null);
  // Bumped per opened document, so page images of the previous one are dropped.
  const [generation, setGeneration] = useState(0);
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [zoom, setZoom] = useState<number | "fit">("fit");
  // Review shows what is under each box; preview shows the output's black boxes.
  const [previewing, setPreviewing] = useState(false);
  const [tab, setTab] = useState<SidebarTab>("findings");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [exportStep, setExportStep] = useState<ExportStep | null>(null);
  const [exporting, setExporting] = useState(false);
  // The region tool, or Alt held down: a drag on a page draws a region.
  const [drawTool, setDrawTool] = useState(false);
  const [altHeld, setAltHeld] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);
  const canvasWidth = useElementWidth(canvasRef, document !== null);

  const notify = useCallback((kind: Toast["kind"], message: string) => {
    const id = Date.now() + Math.random();
    setToasts((current) => [...current, { id, kind, message }]);
    setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), TOAST_MS);
  }, []);
  const reportError = useCallback((message: string) => notify("error", message), [notify]);

  useEffect(() => {
    connect().then(async (connected) => {
      setBridge(connected);
      const opened = await connected.current_document();
      if (opened) show(opened);
    });
  }, []);

  const images = useMemo(() => (bridge ? new PageImages(bridge) : null), [bridge, generation]);

  function show(opened: DocumentInfo) {
    setDocument(opened);
    setGeneration((value) => value + 1);
    setDirty(false);
    setSelectedId(null);
    setCurrentPage(0);
    setZoom("fit");
    canvasRef.current?.scrollTo({ top: 0 });
  }

  const discardConfirmed = () =>
    !dirty || window.confirm("Your decisions on this document are not saved. Discard them?");

  async function open(choose: (api: ReviewBridge) => Promise<DocumentInfo | null>) {
    if (!bridge || busy || !discardConfirmed()) return;
    setBusy(true);
    try {
      const opened = await choose(bridge);
      if (opened) show(opened);
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setBusy(false);
    }
  }
  const openPdf = () => open((api) => api.choose_pdf(null));
  const openReview = () => open((api) => api.choose_session());

  async function save() {
    if (!bridge || !document) return;
    try {
      if (await bridge.save_session_as()) {
        setDirty(false);
        notify("success", "Review saved");
      }
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  /** Ask for consent first when some pages cannot be redacted, then export. */
  function startExport() {
    if (!document || exporting) return;
    const pages = pagesWithoutText(document);
    if (pages.length > 0) setExportStep({ kind: "confirm-pages", pages });
    else void runExport(false);
  }

  async function runExport(allowPagesWithoutText: boolean) {
    if (!bridge) return;
    setExportStep(null);
    setExporting(true);
    try {
      const result = await bridge.export_as(allowPagesWithoutText);
      if (result) setExportStep({ kind: "result", result });
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  const closeExport = useCallback(() => setExportStep(null), []);

  async function addRegion(pageIndex: number, box: Box) {
    if (!bridge) return;
    try {
      const region = await bridge.add_region(pageIndex, ...box);
      setDocument((current) => current && { ...current, entities: [...current.entities, region] });
      setSelectedId(region.id);
      setDirty(true);
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  async function removeEntity(entity: EntityInfo) {
    if (!bridge) return;
    // Optimistic, like toggling: it goes at once and comes back if Python refuses.
    setDocument((current) => current && { ...current, entities: current.entities.filter((item) => item.id !== entity.id) });
    setSelectedId((current) => (current === entity.id ? null : current));
    setDirty(true);
    try {
      await bridge.remove_entity(entity.id);
    } catch (error) {
      setDocument((current) => current && { ...current, entities: [...current.entities, entity] });
      reportError(errorMessage(error));
    }
  }

  async function toggle(entity: EntityInfo) {
    if (!bridge) return;
    const next = toggled(entity.review);
    // Optimistic: the box changes at once, and changes back if Python refuses.
    const setState = (review: EntityInfo["review"]) =>
      setDocument((current) =>
        current && {
          ...current,
          entities: current.entities.map((item) => (item.id === entity.id ? { ...item, review } : item)),
        },
      );
    setState(next);
    setDirty(true);
    try {
      await bridge.set_review(entity.id, next);
    } catch (error) {
      setState(entity.review);
      reportError(errorMessage(error));
    }
  }

  function select(entity: EntityInfo) {
    setSelectedId(entity.id);
    canvasRef.current
      ?.querySelector(`[data-entity-id="${CSS.escape(entity.id)}"]`)
      ?.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  const widest = Math.max(...(document?.pages.map((page) => page.width) ?? [1]));
  const fitScale = Math.min(Math.max((canvasWidth - 2 * CANVAS_PADDING) / widest, MIN_SCALE), MAX_FIT_SCALE);
  const scale = zoom === "fit" ? fitScale : zoom;
  const zoomBy = (direction: 1 | -1) => setZoom(steppedZoom(scale, direction));

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      // A sheet is modal: its own keys only.
      if (exportStep) return;
      if (event.key === "Alt") setAltHeld(true);
      if (!hasCommand(event)) {
        onPlainKey(event);
        return;
      }
      const key = event.key.toLowerCase();
      if (key === "o") void (event.shiftKey ? openReview() : openPdf());
      else if (key === "s" && document) void save();
      else if ((key === "=" || key === "+") && document) zoomBy(1);
      else if (key === "-" && document) zoomBy(-1);
      else if (key === "0" && document) setZoom("fit");
      else if (key === "y" && document) setPreviewing((value) => !value);
      else if (key === "e" && document) startExport();
      else return;
      event.preventDefault();
    };
    const onKeyUp = (event: KeyboardEvent) => {
      if (event.key === "Alt") setAltHeld(false);
    };
    const onBlur = () => setAltHeld(false);
    window.addEventListener("keydown", onKey);
    window.addEventListener("keyup", onKeyUp);
    window.addEventListener("blur", onBlur);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("keyup", onKeyUp);
      window.removeEventListener("blur", onBlur);
    };
  });

  /** Keys without a modifier: R for the region tool, Escape, Delete on a selected region. */
  function onPlainKey(event: KeyboardEvent) {
    if (!document || event.altKey || event.ctrlKey || event.metaKey) return;
    const selected = document.entities.find((entity) => entity.id === selectedId);
    if (event.key === "r" || event.key === "R") setDrawTool((value) => !value);
    else if (event.key === "Escape" && drawTool) setDrawTool(false);
    else if (event.key === "Escape") setSelectedId(null);
    else if ((event.key === "Delete" || event.key === "Backspace") && selected?.is_region) {
      void removeEntity(selected);
    } else return;
    event.preventDefault();
  }

  return (
    <MotionConfig reducedMotion="user">
      <div className="app" data-ready={bridge !== null}>
        {document && images ? (
          <>
            <Toolbar
              name={document.name}
              language={document.language}
              pageCount={document.pages.length}
              currentPage={currentPage}
              scale={scale}
              fitting={zoom === "fit"}
              dirty={dirty}
              previewing={previewing}
              exporting={exporting}
              drawing={drawTool}
              onOpen={openPdf}
              onZoom={zoomBy}
              onFit={() => setZoom("fit")}
              onSave={save}
              onPreview={() => setPreviewing((value) => !value)}
              onExport={startExport}
              onDrawTool={() => setDrawTool((value) => !value)}
            />
            <div className="workspace">
              <Sidebar
                document={document}
                tab={tab}
                selectedId={selectedId}
                onTab={setTab}
                onSelect={select}
                onToggle={toggle}
                onRemove={(entity) => void removeEntity(entity)}
              />
              <PageView
                ref={canvasRef}
                document={document}
                images={images}
                scale={scale}
                selectedId={selectedId}
                showHidden={tab === "hidden"}
                previewing={previewing}
                drawing={drawTool || altHeld}
                onSelect={(entity) => setSelectedId(entity.id)}
                onDrawRegion={(pageIndex, box) => void addRegion(pageIndex, box)}
                onToggle={toggle}
                onError={reportError}
                onCurrentPage={setCurrentPage}
              />
            </div>
          </>
        ) : (
          bridge && <EmptyState busy={busy} onOpen={openPdf} onOpenReview={openReview} />
        )}
        <ExportSheets
          step={exportStep}
          busy={exporting}
          onExportAnyway={() => void runExport(true)}
          onClose={closeExport}
        />
        <Toasts toasts={toasts} />
      </div>
    </MotionConfig>
  );
}

/** The element's content width, tracked as the window resizes. */
function useElementWidth(ref: RefObject<HTMLElement | null>, mounted: boolean): number {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry?.contentRect.width ?? 0));
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, mounted]);
  return width;
}
