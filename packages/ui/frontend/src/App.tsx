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
import type { DocumentInfo, EntityInfo } from "./types";

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
      if (!hasCommand(event) || exportStep) return;
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
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

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
              onOpen={openPdf}
              onZoom={zoomBy}
              onFit={() => setZoom("fit")}
              onSave={save}
              onPreview={() => setPreviewing((value) => !value)}
              onExport={startExport}
            />
            <div className="workspace">
              <Sidebar
                document={document}
                tab={tab}
                selectedId={selectedId}
                onTab={setTab}
                onSelect={select}
                onToggle={toggle}
              />
              <PageView
                ref={canvasRef}
                document={document}
                images={images}
                scale={scale}
                selectedId={selectedId}
                showHidden={tab === "hidden"}
                previewing={previewing}
                onSelect={(entity) => setSelectedId(entity.id)}
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
