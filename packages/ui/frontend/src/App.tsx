import { MotionConfig } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from "react";

import { connect, errorMessage, type ReviewBridge } from "./bridge";
import { ExportSheets, type ExportStep } from "./components/ExportSheets";
import { Home } from "./components/Home";
import { ModelsSheet } from "./components/ModelsSheet";
import { Opening } from "./components/Opening";
import { PageView } from "./components/PageView";
import { Sidebar, type SidebarTab } from "./components/Sidebar";
import { Toasts, type Toast } from "./components/Toasts";
import { Toolbar } from "./components/Toolbar";
import { PageImages } from "./pageImages";
import { hasCommand } from "./platform";
import {
  groupToggled,
  isDecidable,
  lastDrawnRegion,
  pagesWithoutText,
  steppedZoom,
  toggled,
} from "./review";
import type {
  AppStatus,
  Box,
  DocumentInfo,
  FeatureModels,
  DownloadProgress,
  EntityInfo,
  OpenOptions,
  OpenProgress,
  SurfaceInfo,
} from "./types";

const TOAST_MS = 4000;
const CANVAS_PADDING = 48;
const MIN_SCALE = 0.25;
const MAX_FIT_SCALE = 2;

export function App() {
  const [bridge, setBridge] = useState<ReviewBridge | null>(null);
  const [status, setStatus] = useState<AppStatus | null>(null);
  // How the next PDF is opened; the model and OCR are on once their status says ready.
  const [options, setOptions] = useState<OpenOptions>({
    language: "auto",
    propagate: true,
    use_model: false,
    use_ocr: false,
  });
  // Set by Python's progress events once a file is chosen; null otherwise.
  const [opening, setOpening] = useState<{ name: string | null; progress: OpenProgress } | null>(null);
  const openingName = useRef<string | null>(null);
  const [dragging, setDragging] = useState(false);
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
  const [selectedSurfaceId, setSelectedSurfaceId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [exportStep, setExportStep] = useState<ExportStep | null>(null);
  const [exporting, setExporting] = useState(false);
  // The region tool, or Alt held down: a drag on a page draws a region.
  const [drawTool, setDrawTool] = useState(false);
  const [altHeld, setAltHeld] = useState(false);
  // A click on a box only finds it in the list; off by default, so a click decides.
  const [locating, setLocating] = useState(false);
  // Regions drawn since this document opened, oldest first: Cmd/Ctrl+Z removes the last.
  const drawnRegions = useRef<string[]>([]);
  // The Models sheet: its features (null while loading) and the running downloads, by feature.
  const [modelsOpen, setModelsOpen] = useState(false);
  const [models, setModels] = useState<FeatureModels[] | null>(null);
  const [downloads, setDownloads] = useState<Record<string, DownloadProgress>>({});
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
      const installed = await connected.status();
      setStatus(installed);
      setOptions((current) => ({
        ...current,
        use_model: installed.model.state === "ready",
        use_ocr: installed.ocr.state === "ready",
      }));
    });
  }, []);

  const images = useMemo(() => (bridge ? new PageImages(bridge) : null), [bridge, generation]);

  function show(opened: DocumentInfo) {
    setDocument(opened);
    setGeneration((value) => value + 1);
    setDirty(false);
    setSelectedId(null);
    setSelectedSurfaceId(null);
    drawnRegions.current = [];
    setCurrentPage(0);
    setZoom("fit");
    canvasRef.current?.scrollTo({ top: 0 });
  }

  const discardConfirmed = () =>
    !dirty || window.confirm("Your decisions on this document are not saved. Discard them?");

  /** `name` is known for a dropped file; a dialog's choice is named once it opens. */
  async function open(choose: (api: ReviewBridge) => Promise<DocumentInfo | null>, name: string | null = null) {
    if (!bridge || busy || !discardConfirmed()) return;
    setBusy(true);
    openingName.current = name;
    try {
      const opened = await choose(bridge);
      if (opened) show(opened);
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setBusy(false);
      setOpening(null);
    }
  }
  async function openModels() {
    if (!bridge) return;
    setModelsOpen(true);
    try {
      setModels(await bridge.models());
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  /** Download a feature's models, then turn the feature on if it is now usable. */
  async function downloadModels(feature: string) {
    if (!bridge || downloads[feature]) return;
    const missing = models?.find((item) => item.feature === feature)?.missing_bytes ?? 0;
    setDownloads((current) => ({ ...current, [feature]: { feature, received: 0, total: missing } }));
    try {
      setModels(await bridge.download_models(feature));
      const installed = await bridge.status();
      setStatus(installed);
      setOptions((current) => ({
        ...current,
        use_model: current.use_model || (feature === "names" && installed.model.state === "ready"),
        use_ocr: current.use_ocr || (feature === "ocr" && installed.ocr.state === "ready"),
      }));
      notify("success", "Downloaded and checked");
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setDownloads(({ [feature]: _finished, ...running }) => running);
    }
  }

  /** Store models in another folder; a feature whose models are not there turns off. */
  async function chooseModelsFolder() {
    if (!bridge) return;
    try {
      const installed = await bridge.choose_models_folder();
      if (!installed) return;
      setStatus(installed);
      setOptions((current) => ({
        ...current,
        use_model: current.use_model && installed.model.state === "ready",
        use_ocr: current.use_ocr && installed.ocr.state === "ready",
      }));
      setModels(await bridge.models());
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  const openPdf = () => open((api) => api.choose_pdf(options));
  const openReview = () => open((api) => api.choose_session());
  const openDropped = (name: string) => open((api) => api.open_dropped(options), name);

  async function closeDocument() {
    if (!bridge || !discardConfirmed()) return;
    try {
      await bridge.close_document();
      setDocument(null);
      setDirty(false);
      setPreviewing(false);
      setDrawTool(false);
      setExportStep(null);
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  // Python's events reach the latest handlers through this ref, so the
  // listeners are added once and still see current options and state.
  const onPythonEvent = useRef({ openDropped, reportError });
  onPythonEvent.current = { openDropped, reportError };

  useEffect(() => {
    const onProgress = (event: Event) => {
      const progress = (event as CustomEvent<OpenProgress>).detail;
      setOpening({ name: openingName.current, progress });
    };
    const onDropped = (event: Event) => {
      setDragging(false);
      void onPythonEvent.current.openDropped((event as CustomEvent<string>).detail);
    };
    const onRefused = (event: Event) => {
      setDragging(false);
      const name = (event as CustomEvent<string>).detail;
      onPythonEvent.current.reportError(`Only PDF files can be opened${name ? `, not ${name}` : ""}`);
    };
    const onDownload = (event: Event) => {
      const progress = (event as CustomEvent<DownloadProgress>).detail;
      // A late event must not bring back a download that has finished.
      setDownloads((current) =>
        progress.feature in current ? { ...current, [progress.feature]: progress } : current,
      );
    };
    window.addEventListener("anonymizer:progress", onProgress);
    window.addEventListener("anonymizer:download", onDownload);
    window.addEventListener("anonymizer:dropped", onDropped);
    window.addEventListener("anonymizer:drop-refused", onRefused);
    return () => {
      window.removeEventListener("anonymizer:progress", onProgress);
      window.removeEventListener("anonymizer:download", onDownload);
      window.removeEventListener("anonymizer:dropped", onDropped);
      window.removeEventListener("anonymizer:drop-refused", onRefused);
    };
  }, []);

  // Highlight while a file is dragged over the window; the drop itself is
  // Python's, which alone sees the file's path.
  useEffect(() => {
    let depth = 0;
    const carriesFiles = (event: DragEvent) => event.dataTransfer?.types.includes("Files") ?? false;
    const onEnter = (event: DragEvent) => {
      if (!carriesFiles(event)) return;
      depth += 1;
      setDragging(true);
    };
    const onLeave = () => {
      depth = Math.max(depth - 1, 0);
      if (depth === 0) setDragging(false);
    };
    const onDrop = () => {
      depth = 0;
      setDragging(false);
    };
    window.addEventListener("dragenter", onEnter);
    window.addEventListener("dragleave", onLeave);
    window.addEventListener("drop", onDrop);
    return () => {
      window.removeEventListener("dragenter", onEnter);
      window.removeEventListener("dragleave", onLeave);
      window.removeEventListener("drop", onDrop);
    };
  }, []);

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
      drawnRegions.current.push(region.id);
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
    // Hidden data always goes and a region is removed instead: nothing to toggle.
    if (!bridge || !isDecidable(entity)) return;
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

  /** One decision for every repeat of a finding; hidden-data members have none to change. */
  async function toggleGroup(members: EntityInfo[]) {
    const decidable = members.filter(isDecidable);
    if (!bridge || decidable.length === 0) return;
    const next = groupToggled(decidable);
    const ids = new Set(decidable.map((entity) => entity.id));
    const before = new Map(decidable.map((entity) => [entity.id, entity.review]));
    // Optimistic, like a single toggle: every box changes at once, and back if Python refuses.
    const apply = (reviewOf: (entity: EntityInfo) => EntityInfo["review"]) =>
      setDocument((current) =>
        current && {
          ...current,
          entities: current.entities.map((item) => (ids.has(item.id) ? { ...item, review: reviewOf(item) } : item)),
        },
      );
    apply(() => next);
    setDirty(true);
    try {
      await bridge.set_reviews([...ids], next);
    } catch (error) {
      apply((item) => before.get(item.id) ?? item.review);
      reportError(errorMessage(error));
    }
  }

  /** Show a hidden item where it sits on its page: its outline, or the page. */
  function selectSurface(surface: SurfaceInfo) {
    setSelectedSurfaceId(surface.id);
    const canvas = canvasRef.current;
    const target =
      canvas?.querySelector(`[data-surface-id="${CSS.escape(surface.id)}"]`) ??
      canvas?.querySelector(`[data-page-index="${surface.page_index}"]`);
    target?.scrollIntoView({ block: "center", behavior: "smooth" });
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
      else if (key === "z" && !event.shiftKey && document) undoRegion();
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

  /** Remove the last region drawn that is still there; there is no undo for decisions yet. */
  function undoRegion() {
    if (!document) return;
    const region = lastDrawnRegion(drawnRegions.current, document.entities);
    drawnRegions.current = drawnRegions.current.filter((id) => id !== region?.id);
    if (region) void removeEntity(region);
  }

  /** Keys without a modifier: R for the region tool, L for locating, Escape, Delete on a selected region. */
  function onPlainKey(event: KeyboardEvent) {
    if (!document || event.altKey || event.ctrlKey || event.metaKey) return;
    const selected = document.entities.find((entity) => entity.id === selectedId);
    if (event.key === "r" || event.key === "R") setDrawTool((value) => !value);
    else if (event.key === "l" || event.key === "L") setLocating((value) => !value);
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
        {opening ? (
          <Opening
            name={opening.name}
            progress={opening.progress}
            usesModel={options.use_model}
            usesOcr={options.use_ocr}
          />
        ) : document && images ? (
          <>
            <Toolbar
              name={document.name}
              language={document.language}
              languageRecognised={document.language_recognised}
              pageCount={document.pages.length}
              currentPage={currentPage}
              scale={scale}
              fitting={zoom === "fit"}
              dirty={dirty}
              previewing={previewing}
              exporting={exporting}
              drawing={drawTool}
              locating={locating}
              onOpen={openPdf}
              onZoom={zoomBy}
              onFit={() => setZoom("fit")}
              onSave={save}
              onPreview={() => setPreviewing((value) => !value)}
              onExport={startExport}
              onDrawTool={() => setDrawTool((value) => !value)}
              onLocate={() => setLocating((value) => !value)}
              onClose={() => void closeDocument()}
            />
            <div className="workspace">
              <Sidebar
                document={document}
                tab={tab}
                selectedId={selectedId}
                onTab={setTab}
                onSelect={select}
                onToggle={toggle}
                onToggleGroup={(members) => void toggleGroup(members)}
                onRemove={(entity) => void removeEntity(entity)}
                selectedSurfaceId={selectedSurfaceId}
                onSelectSurface={selectSurface}
              />
              <PageView
                ref={canvasRef}
                document={document}
                images={images}
                scale={scale}
                selectedId={selectedId}
                selectedSurfaceId={selectedSurfaceId}
                showHidden={tab === "hidden"}
                previewing={previewing}
                drawing={drawTool || altHeld}
                locating={locating}
                onSelect={(entity) => setSelectedId(entity.id)}
                onDrawRegion={(pageIndex, box) => void addRegion(pageIndex, box)}
                onToggle={toggle}
                onError={reportError}
                onCurrentPage={setCurrentPage}
              />
            </div>
            {dragging && (
              <div className="drop-overlay" aria-hidden>
                <p>Drop to open another PDF</p>
              </div>
            )}
          </>
        ) : (
          bridge && (
            <Home
              status={status}
              options={options}
              busy={busy}
              dragging={dragging}
              onOptions={setOptions}
              onOpen={openPdf}
              onOpenReview={openReview}
              onModels={() => void openModels()}
            />
          )
        )}
        <ExportSheets
          step={exportStep}
          busy={exporting}
          onExportAnyway={() => void runExport(true)}
          onClose={closeExport}
        />
        <ModelsSheet
          open={modelsOpen}
          features={models}
          downloads={downloads}
          folder={status?.models_folder ?? null}
          onChangeFolder={() => void chooseModelsFolder()}
          onDownload={(feature) => void downloadModels(feature)}
          onClose={() => setModelsOpen(false)}
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
