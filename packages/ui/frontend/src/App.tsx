import { MotionConfig } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from "react";

import { connect, errorMessage, type ReviewBridge } from "./bridge";
import { ExportSheets, type ExportSheet } from "./components/ExportSheets";
import { Home } from "./components/Home";
import { ModelsSheet } from "./components/ModelsSheet";
import { Opening } from "./components/Opening";
import { PageView, type WordSelection } from "./components/PageView";
import { SettingsSheet } from "./components/SettingsSheet";
import { Sidebar, type SidebarTab } from "./components/Sidebar";
import { Toasts, type Toast } from "./components/Toasts";
import { Toolbar } from "./components/Toolbar";
import { PageImages } from "./pageImages";
import { PageWords } from "./pageWords";
import { hasCommand } from "./platform";
import {
  DEFAULT_VIEW,
  NO_FILTER,
  activeFilters,
  covers,
  filterFindings,
  groupToggled,
  isDecidable,
  lastAdded,
  ocrOptions,
  pagesWithoutText,
  plural,
  scannedPages,
  steppedZoom,
  toggled,
  type LeakRow,
  type ListView,
} from "./review";
import { selectionSpan } from "./selection";
import type {
  AppStatus,
  Box,
  DocumentInfo,
  FeatureModels,
  DownloadProgress,
  EntityInfo,
  ExportProgress,
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
    ocr_engine: "onnxtr",
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
  // How the findings list is ordered and filtered; the order lasts the session, the filter one document.
  const [view, setView] = useState<ListView>(DEFAULT_VIEW);
  const [selectedSurfaceId, setSelectedSurfaceId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [exportSheet, setExportSheet] = useState<ExportSheet | null>(null);
  const [exporting, setExporting] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [savingSetting, setSavingSetting] = useState(false);
  // The region tool, or Alt held down: a drag on a page draws a region.
  const [drawTool, setDrawTool] = useState(false);
  const [altHeld, setAltHeld] = useState(false);
  // A click on a box only finds it in the list; off by default, so a click decides.
  const [locating, setLocating] = useState(false);
  // Items added since this document opened (regions drawn, text selected), oldest first:
  // Cmd/Ctrl+Z removes the last.
  const addedItems = useRef<string[]>([]);
  // Words selected on a page, waiting to be added as a finding.
  const [selection, setSelection] = useState<WordSelection | null>(null);
  const [adding, setAdding] = useState(false);
  // The Models sheet: its features (null while loading) and the running downloads, by feature.
  const [modelsOpen, setModelsOpen] = useState(false);
  const [models, setModels] = useState<FeatureModels[] | null>(null);
  const [downloads, setDownloads] = useState<Record<string, DownloadProgress>>({});
  const canvasRef = useRef<HTMLDivElement>(null);
  const canvasWidth = useElementWidth(canvasRef, document !== null);

  const dismissToast = useCallback(
    (id: number) => setToasts((current) => current.filter((toast) => toast.id !== id)),
    [],
  );
  const notify = useCallback(
    (kind: Toast["kind"], message: string, action?: Toast["action"]) => {
      const id = Date.now() + Math.random();
      setToasts((current) => [...current, { id, kind, message, action }]);
      setTimeout(() => dismissToast(id), TOAST_MS);
    },
    [dismissToast],
  );
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
        ...ocrOptions(installed.ocr, { use_ocr: true, ocr_engine: installed.ocr.default }),
      }));
    });
  }, []);

  // Preview and the region tool have no use for selected words.
  useEffect(() => {
    if (previewing || drawTool) setSelection(null);
  }, [previewing, drawTool]);

  const images = useMemo(() => (bridge ? new PageImages(bridge) : null), [bridge, generation]);
  const words = useMemo(() => (bridge ? new PageWords(bridge) : null), [bridge, generation]);
  // The findings a filter lets through, whose boxes stay bright on the page; null without a filter.
  const shownIds = useMemo(
    () =>
      document && activeFilters(view.filter) > 0
        ? new Set(filterFindings(document.entities, view.filter).map((entity) => entity.id))
        : null,
    [document, view.filter],
  );

  function show(opened: DocumentInfo) {
    setDocument(opened);
    setGeneration((value) => value + 1);
    setDirty(false);
    setSelectedId(null);
    setView((current) => ({ ...current, filter: NO_FILTER }));
    setSelectedSurfaceId(null);
    setSelection(null);
    addedItems.current = [];
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
      const engine = installed.ocr.engines.find((item) => item.feature === feature);
      setOptions((current) => ({
        ...current,
        use_model: current.use_model || (feature === "names" && installed.model.state === "ready"),
        ...ocrOptions(installed.ocr, current, engine?.name ?? null),
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
        ...ocrOptions(installed.ocr, current),
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
      setSelection(null);
      setExportSheet(null);
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
    const onExport = (event: Event) => {
      const progress = (event as CustomEvent<ExportProgress>).detail;
      // Only a running export shows its steps; a late event changes nothing after it ends.
      setExportSheet((current) => (current?.kind === "progress" ? { ...current, progress } : current));
    };
    const onDownload = (event: Event) => {
      const progress = (event as CustomEvent<DownloadProgress>).detail;
      // A late event must not bring back a download that has finished.
      setDownloads((current) =>
        progress.feature in current ? { ...current, [progress.feature]: progress } : current,
      );
    };
    window.addEventListener("anonymizer:progress", onProgress);
    window.addEventListener("anonymizer:export", onExport);
    window.addEventListener("anonymizer:download", onDownload);
    window.addEventListener("anonymizer:dropped", onDropped);
    window.addEventListener("anonymizer:drop-refused", onRefused);
    return () => {
      window.removeEventListener("anonymizer:progress", onProgress);
      window.removeEventListener("anonymizer:export", onExport);
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
    if (pages.length > 0) setExportSheet({ kind: "confirm-pages", pages });
    else void runExport(false);
  }

  /** Export through the save dialog; the progress sheet appears with Python's first step. */
  async function runExport(allowPagesWithoutText: boolean) {
    if (!bridge || !document) return;
    const plan = { check: status?.settings.leak_check ?? true, scannedPages: scannedPages(document) };
    setExportSheet({ kind: "progress", plan, progress: null });
    setExporting(true);
    try {
      const result = await bridge.export_as(allowPagesWithoutText);
      if (!result) setExportSheet(null);
      else if (result.written) setExportSheet({ kind: "result", result, accepted: [] });
      else setExportSheet({ kind: "leaks", result });
    } catch (error) {
      setExportSheet(null);
      reportError(errorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  /** Write the copy the leak check refused, after the reviewer has seen what it found. */
  async function saveAnyway() {
    if (!bridge || exportSheet?.kind !== "leaks") return;
    const accepted = exportSheet.result.leaks;
    setExportSheet({ kind: "progress", plan: { check: false, scannedPages: 0 }, progress: null });
    setExporting(true);
    try {
      const result = await bridge.export_unchecked();
      setExportSheet({ kind: "result", result, accepted });
    } catch (error) {
      setExportSheet(null);
      reportError(errorMessage(error));
    } finally {
      setExporting(false);
    }
  }

  /** Leave the leak sheet for the place a leak lies: its finding, or its page. */
  function showLeak(row: LeakRow) {
    setExportSheet(null);
    const entity = document?.entities.find((item) => item.id === row.entityId);
    if (entity && entity.page_index !== null) {
      select(entity);
      return;
    }
    if (row.page !== null) {
      canvasRef.current
        ?.querySelector(`[data-page-index="${row.page - 1}"]`)
        ?.scrollIntoView({ block: "start", behavior: "smooth" });
    }
  }

  const closeExport = useCallback(() => setExportSheet(null), []);

  async function setLeakCheck(enabled: boolean) {
    if (!bridge) return;
    setSavingSetting(true);
    try {
      setStatus(await bridge.set_leak_check(enabled));
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setSavingSetting(false);
    }
  }

  async function addRegion(pageIndex: number, box: Box) {
    if (!bridge) return;
    try {
      const region = await bridge.add_region(pageIndex, ...box);
      setDocument((current) => current && { ...current, entities: [...current.entities, region] });
      addedItems.current.push(region.id);
      setSelectedId(region.id);
      setDirty(true);
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  /** Add the selected words as a finding of a type, with the repeats Python proposes. */
  async function addFinding(type: string) {
    const span = selection && selectionSpan(selection.words);
    if (!bridge || !selection || !span || adding) return;
    setAdding(true);
    try {
      const added = await bridge.add_finding(selection.pageIndex, ...span, type);
      const [finding] = added;
      if (!finding) return;
      setDocument((current) => current && { ...current, entities: [...current.entities, ...added] });
      addedItems.current.push(finding.id);
      setSelection(null);
      setSelectedId(finding.id);
      setDirty(true);
      const repeats = added.length - 1;
      notify("success", `Added “${clipped(covers(finding))}”${repeats > 0 ? ` and ${plural(repeats, "repeat")}` : ""}`, {
        label: "Undo",
        run: () => void removeEntity(finding),
      });
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setAdding(false);
    }
  }

  async function removeEntity(entity: EntityInfo) {
    if (!bridge) return;
    // Optimistic, like toggling: it goes at once and comes back if Python refuses.
    setDocument((current) => current && { ...current, entities: current.entities.filter((item) => item.id !== entity.id) });
    setSelectedId((current) => (current === entity.id ? null : current));
    setDirty(true);
    try {
      // Repeats proposed only because of an added text go with it.
      const removed = new Set(await bridge.remove_entity(entity.id));
      setDocument((current) => current && { ...current, entities: current.entities.filter((item) => !removed.has(item.id)) });
      setSelectedId((current) => (current !== null && removed.has(current) ? null : current));
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
    if (decidable.length === 0) return;
    await decideAll(decidable, groupToggled(decidable));
  }

  /** Keep the model's uncertain findings, with an Undo that makes them undecided again. */
  async function keepAll(entities: EntityInfo[]) {
    if (entities.length === 0 || !(await decideAll(entities, "rejected"))) return;
    notify("success", `Kept ${plural(entities.length, "finding")}`, {
      label: "Undo",
      // Kept by now: a refused undo leaves them kept, as Python has them.
      run: () => void decideAll(entities.map((entity) => ({ ...entity, review: "rejected" })), "pending"),
    });
  }

  /** One decision for several decidable entities; false if Python refused it. */
  async function decideAll(entities: EntityInfo[], next: EntityInfo["review"]): Promise<boolean> {
    if (!bridge) return false;
    const ids = new Set(entities.map((entity) => entity.id));
    const before = new Map(entities.map((entity) => [entity.id, entity.review]));
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
      return true;
    } catch (error) {
      apply((item) => before.get(item.id) ?? item.review);
      reportError(errorMessage(error));
      return false;
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
      if (exportSheet || settingsOpen || modelsOpen) return;
      if (event.key === "Alt") setAltHeld(true);
      if (!hasCommand(event)) {
        onPlainKey(event);
        return;
      }
      const key = event.key.toLowerCase();
      if (key === ",") setSettingsOpen(true);
      else if (key === "o") void (event.shiftKey ? openReview() : openPdf());
      else if (key === "s" && document) void save();
      else if ((key === "=" || key === "+") && document) zoomBy(1);
      else if (key === "-" && document) zoomBy(-1);
      else if (key === "0" && document) setZoom("fit");
      else if (key === "y" && document) setPreviewing((value) => !value);
      else if (key === "e" && document) startExport();
      else if (key === "z" && !event.shiftKey && document) undoAdded();
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

  /** Remove the last item added that is still there; there is no undo for decisions yet. */
  function undoAdded() {
    if (!document) return;
    const added = lastAdded(addedItems.current, document.entities);
    addedItems.current = addedItems.current.filter((id) => id !== added?.id);
    if (added) void removeEntity(added);
  }

  /**
   * Keys without a modifier: R for the region tool, L for locating, Escape, Delete on a
   * selected item the reviewer added.
   */
  function onPlainKey(event: KeyboardEvent) {
    if (!document || event.altKey || event.ctrlKey || event.metaKey) return;
    const selected = document.entities.find((entity) => entity.id === selectedId);
    if (event.key === "r" || event.key === "R") setDrawTool((value) => !value);
    else if (event.key === "l" || event.key === "L") setLocating((value) => !value);
    else if (event.key === "Escape" && selection) setSelection(null);
    else if (event.key === "Escape" && drawTool) setDrawTool(false);
    else if (event.key === "Escape") setSelectedId(null);
    else if ((event.key === "Delete" || event.key === "Backspace") && selected?.source === "manual") {
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
        ) : document && images && words ? (
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
              onSettings={() => setSettingsOpen(true)}
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
                onKeep={(entities) => void keepAll(entities)}
                view={view}
                onView={setView}
                onRemove={(entity) => void removeEntity(entity)}
                selectedSurfaceId={selectedSurfaceId}
                onSelectSurface={selectSurface}
              />
              <PageView
                ref={canvasRef}
                document={document}
                images={images}
                words={words}
                scale={scale}
                selectedId={selectedId}
                selectedSurfaceId={selectedSurfaceId}
                showHidden={tab === "hidden"}
                previewing={previewing}
                drawing={drawTool || altHeld}
                locating={locating}
                shownIds={shownIds}
                selection={altHeld ? null : selection}
                adding={adding}
                onSelect={(entity) => setSelectedId(entity.id)}
                onDrawRegion={(pageIndex, box) => void addRegion(pageIndex, box)}
                onSelectWords={setSelection}
                onAddFinding={(type) => void addFinding(type)}
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
              onSettings={() => setSettingsOpen(true)}
            />
          )
        )}
        <ExportSheets
          sheet={exportSheet}
          busy={exporting}
          onExportAnyway={() => void runExport(true)}
          onSaveAnyway={() => void saveAnyway()}
          onShowLeak={showLeak}
          onClose={closeExport}
        />
        <SettingsSheet
          open={settingsOpen}
          status={status}
          saving={savingSetting}
          downloading={Object.keys(downloads).length > 0}
          onLeakCheck={(enabled) => void setLeakCheck(enabled)}
          onChangeFolder={() => void chooseModelsFolder()}
          onModels={() => {
            setSettingsOpen(false);
            void openModels();
          }}
          onClose={() => setSettingsOpen(false)}
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
        <Toasts toasts={toasts} onDismiss={dismissToast} />
      </div>
    </MotionConfig>
  );
}

/** A finding's text short enough for a toast. */
function clipped(text: string, length = 40): string {
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
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
