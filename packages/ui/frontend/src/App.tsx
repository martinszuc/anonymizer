import { MotionConfig } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from "react";

import { connect, errorMessage, type ReviewBridge } from "./bridge";
import { ExportSheets, type ExportSheet } from "./components/ExportSheets";
import { Home } from "./components/Home";
import { ModelsSheet } from "./components/ModelsSheet";
import { Opening } from "./components/Opening";
import { PageView, type WordSelection } from "./components/PageView";
import { SettingsSheet } from "./components/SettingsSheet";
import { ShortcutsSheet } from "./components/ShortcutsSheet";
import { Sidebar, type SidebarTab } from "./components/Sidebar";
import { Toasts, type Toast } from "./components/Toasts";
import { Toolbar } from "./components/Toolbar";
import {
  EMPTY_HISTORY,
  additionOf,
  afterRedo,
  afterUndo,
  recorded,
  statesBefore,
  type Addition,
  type Edit,
  type History,
} from "./history";
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
  nameModelOptions,
  nextUndecided,
  findingSections,
  ocrOptions,
  pagesWithoutText,
  plural,
  scannedPages,
  steppedZoom,
  toggled,
  truncated,
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
const TOAST_TEXT_LENGTH = 40;
const CANVAS_PADDING = 48;
const MIN_SCALE = 0.25;
const MAX_FIT_SCALE = 2;

export function App() {
  const [bridge, setBridge] = useState<ReviewBridge | null>(null);
  const [status, setStatus] = useState<AppStatus | null>(null);
  // How the next document is opened; the model and OCR are on once their status says ready.
  const [options, setOptions] = useState<OpenOptions>({
    language: "auto",
    propagate: true,
    use_model: false,
    name_model: "gliner-multi-v2.1",
    use_ocr: false,
    ocr_engine: "onnxtr",
  });
  // Set by Python's progress events once a file is chosen; null otherwise.
  const [opening, setOpening] = useState<{ name: string | null; progress: OpenProgress } | null>(null);
  const openingName = useRef<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [document, setDocument] = useState<DocumentInfo | null>(null);
  // For steps that run after an await or from a toast, which must see the latest entities.
  const documentRef = useRef(document);
  documentRef.current = document;
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
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const pageField = useRef<HTMLInputElement>(null);
  const [savingSetting, setSavingSetting] = useState(false);
  // The region tool, or Alt held down: a drag on a page draws a region.
  const [drawTool, setDrawTool] = useState(false);
  const [altHeld, setAltHeld] = useState(false);
  // A click on a box only finds it in the list; off by default, so a click decides.
  const [locating, setLocating] = useState(false);
  // The reviewer's edits on this document, for undo and redo; a step runs one at a time.
  const [history, setHistory] = useState<History>(EMPTY_HISTORY);
  const historyRef = useRef(history);
  historyRef.current = history;
  const stepping = useRef(false);
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
  const updateEntities = (change: (entities: EntityInfo[]) => EntityInfo[]) =>
    setDocument((current) => current && { ...current, entities: change(current.entities) });

  useEffect(() => {
    connect().then(async (connected) => {
      setBridge(connected);
      const opened = await connected.current_document();
      if (opened) show(opened);
      const installed = await connected.status();
      setStatus(installed);
      // The options as last left, or the defaults with every ready model on; either way only
      // what is ready now is turned on.
      const kept = installed.settings.open_options;
      setOptions((current) => {
        const start = kept ?? {
          ...current,
          use_model: true,
          name_model: installed.names.default,
          use_ocr: true,
          ocr_engine: installed.ocr.default,
        };
        return { ...start, ...nameModelOptions(installed.names, start), ...ocrOptions(installed.ocr, start) };
      });
    });
  }, []);

  // Closing the window asks first while the review has unsaved changes.
  useEffect(() => {
    bridge?.set_unsaved_changes(dirty).catch((error: unknown) => reportError(errorMessage(error)));
  }, [bridge, dirty, reportError]);

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
    setHistory(EMPTY_HISTORY);
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
      const model = installed.names.models.find((item) => item.feature === feature);
      const engine = installed.ocr.engines.find((item) => item.feature === feature);
      setOptions((current) => ({
        ...current,
        ...nameModelOptions(installed.names, current, model?.name ?? null),
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
        ...nameModelOptions(installed.names, current),
        ...ocrOptions(installed.ocr, current),
      }));
      setModels(await bridge.models());
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  /** Change the home screen's options, kept for later runs. */
  function changeOptions(next: OpenOptions) {
    setOptions(next);
    bridge?.set_open_options(next).catch((error: unknown) => reportError(errorMessage(error)));
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
      onPythonEvent.current.reportError(
        `Only PDF, JPEG, PNG and TIFF files can be opened${name ? `, not ${name}` : ""}`,
      );
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
    const listeners: [string, (event: Event) => void][] = [
      ["anonymizer:progress", onProgress],
      ["anonymizer:export", onExport],
      ["anonymizer:download", onDownload],
      ["anonymizer:dropped", onDropped],
      ["anonymizer:drop-refused", onRefused],
    ];
    for (const [name, listener] of listeners) window.addEventListener(name, listener);
    return () => {
      for (const [name, listener] of listeners) window.removeEventListener(name, listener);
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

  /** Remember an edit for undo. An Undo offered by a toast belongs to the edit before it. */
  function record(edit: Edit) {
    setHistory((current) => recorded(current, edit));
    setToasts((current) => current.filter((toast) => !toast.action));
    setDirty(true);
  }

  async function addRegion(pageIndex: number, box: Box) {
    if (!bridge) return;
    try {
      const addition: Addition = { kind: "region", pageIndex, box };
      const [region] = await addAgain(addition);
      if (!region) return;
      record({ kind: "add", addition, ids: [region.id], label: "Draw a region" });
      setSelectedId(region.id);
    } catch (error) {
      reportError(errorMessage(error));
    }
  }

  /** Add an item through Python; the new entities, the item first. */
  async function addAgain(addition: Addition): Promise<EntityInfo[]> {
    if (!bridge) return [];
    const added =
      addition.kind === "region"
        ? [await bridge.add_region(addition.pageIndex, ...addition.box)]
        : await bridge.add_finding(addition.pageIndex, addition.start, addition.end, addition.type);
    updateEntities((entities) => [...entities, ...added]);
    return added;
  }

  /** Add the selected words as a finding of a type, with the repeats Python proposes. */
  async function addFinding(type: string) {
    const span = selection && selectionSpan(selection.words);
    if (!bridge || !selection || !span || adding) return;
    setAdding(true);
    try {
      const addition: Addition = { kind: "finding", pageIndex: selection.pageIndex, start: span[0], end: span[1], type };
      const added = await addAgain(addition);
      const [finding] = added;
      if (!finding) return;
      const text = truncated(covers(finding), TOAST_TEXT_LENGTH);
      const edit: Edit = { kind: "add", addition, ids: added.map((item) => item.id), label: `Add “${text}”` };
      record(edit);
      setSelection(null);
      setSelectedId(finding.id);
      const repeats = added.length - 1;
      notify("success", `Added “${text}”${repeats > 0 ? ` and ${plural(repeats, "repeat")}` : ""}`, undoAction(edit));
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      setAdding(false);
    }
  }

  /** Remove an item the reviewer added; undoable when it was added since the document opened. */
  async function removeEntity(entity: EntityInfo) {
    const addition = additionOf(historyRef.current, entity.id);
    if (!(await removeNow(entity))) return;
    const text = entity.is_region ? "a region" : `“${truncated(covers(entity), TOAST_TEXT_LENGTH)}”`;
    if (addition) record({ kind: "remove", addition, ids: [entity.id], label: `Remove ${text}` });
    else setDirty(true);
  }

  /** Remove an item through Python, with the repeats only it explained; false if refused. */
  async function removeNow(entity: EntityInfo): Promise<boolean> {
    if (!bridge) return false;
    // Optimistic, like toggling: it goes at once and comes back if Python refuses.
    updateEntities((entities) => entities.filter((item) => item.id !== entity.id));
    setSelectedId((current) => (current === entity.id ? null : current));
    try {
      const removed = new Set(await bridge.remove_entity(entity.id));
      updateEntities((entities) => entities.filter((item) => !removed.has(item.id)));
      setSelectedId((current) => (current !== null && removed.has(current) ? null : current));
      return true;
    } catch (error) {
      updateEntities((entities) => [...entities, entity]);
      reportError(errorMessage(error));
      return false;
    }
  }

  async function toggle(entity: EntityInfo) {
    // Hidden data always goes and a region is removed instead: nothing to toggle.
    if (!bridge || !isDecidable(entity)) return;
    const next = toggled(entity.review);
    const text = truncated(covers(entity), TOAST_TEXT_LENGTH);
    await decideAll([entity], next, `${next === "rejected" ? "Keep" : "Redact"} “${text}”`);
  }

  /** One decision for every repeat of a finding; hidden-data members have none to change. */
  async function toggleGroup(members: EntityInfo[]) {
    const decidable = members.filter(isDecidable);
    if (decidable.length === 0) return;
    const next = groupToggled(decidable);
    const text = truncated(covers(decidable[0] as EntityInfo), TOAST_TEXT_LENGTH);
    await decideAll(decidable, next, `${next === "rejected" ? "Keep" : "Redact"} every “${text}”`);
  }

  /** Keep the undecided findings a filter shows, with an Undo on the toast. */
  async function keepAll(entities: EntityInfo[]) {
    const label = `Keep ${plural(entities.length, "finding")}`;
    const edit = entities.length > 0 ? await decideAll(entities, "rejected", label) : null;
    if (edit) notify("success", `Kept ${plural(entities.length, "finding")}`, undoAction(edit));
  }

  /** A toast's Undo: it undoes its own edit, and only while that edit is the last one. */
  function undoAction(edit: Edit): Toast["action"] {
    return { label: "Undo", run: () => historyRef.current.done.at(-1) === edit && void undo() };
  }

  /** One decision for several decidable entities, recorded for undo; null if Python refused it. */
  async function decideAll(entities: EntityInfo[], next: EntityInfo["review"], label: string): Promise<Edit | null> {
    if (!(await setReviews(entities, next))) return null;
    const edit: Edit = {
      kind: "decide",
      before: Object.fromEntries(entities.map((entity) => [entity.id, entity.review])),
      after: next,
      label,
    };
    record(edit);
    return edit;
  }

  /** Set one state on entities, at once on screen and back if Python refuses; false then. */
  async function setReviews(entities: EntityInfo[], next: EntityInfo["review"]): Promise<boolean> {
    if (!bridge) return false;
    const ids = new Set(entities.map((entity) => entity.id));
    const before = new Map(entities.map((entity) => [entity.id, entity.review]));
    // Optimistic, like a single toggle: every box changes at once, and back if Python refuses.
    const apply = (reviewOf: (entity: EntityInfo) => EntityInfo["review"]) =>
      updateEntities((entities) =>
        entities.map((item) => (ids.has(item.id) ? { ...item, review: reviewOf(item) } : item)),
      );
    apply(() => next);
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

  /** Bring a page to the top of the canvas. */
  function goToPage(index: number) {
    canvasRef.current?.querySelector(`[data-page-index="${index}"]`)?.scrollIntoView({ block: "start" });
  }

  const widest = Math.max(...(document?.pages.map((page) => page.width) ?? [1]));
  const fitScale = Math.min(Math.max((canvasWidth - 2 * CANVAS_PADDING) / widest, MIN_SCALE), MAX_FIT_SCALE);
  const scale = zoom === "fit" ? fitScale : zoom;
  const zoomBy = (direction: 1 | -1) => setZoom(steppedZoom(scale, direction));

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      // A sheet is modal: its own keys only.
      if (exportSheet || settingsOpen || modelsOpen || shortcutsOpen) return;
      if (event.key === "Alt") setAltHeld(true);
      if (!hasCommand(event)) {
        // Letters typed into a field are text, not shortcuts.
        if (!isTyping(event.target)) onPlainKey(event);
        return;
      }
      const key = event.key.toLowerCase();
      if (key === ",") setSettingsOpen(true);
      else if (key === "o") void (event.shiftKey ? openReview() : openPdf());
      else if (key === "s" && document) void save();
      else if ((key === "=" || key === "+") && document) zoomBy(1);
      else if (key === "-" && document) zoomBy(-1);
      else if (key === "0" && document) setZoom("fit");
      else if (key === "g" && document) pageField.current?.focus();
      else if (key === "y" && document) setPreviewing((value) => !value);
      else if (key === "e" && document) startExport();
      else if (key === "z" && document) void (event.shiftKey ? redo() : undo());
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

  /** Undo the last edit: decisions back to what they were, an addition removed, a removal added back. */
  async function undo() {
    const edit = historyRef.current.done.at(-1);
    if (!edit || stepping.current) return;
    stepping.current = true;
    try {
      const renamed = await carryOut(edit, "undo");
      setHistory((current) => afterUndo(current, renamed));
      setDirty(true);
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      stepping.current = false;
    }
  }

  /** Redo the last edit undone. */
  async function redo() {
    const edit = historyRef.current.undone.at(-1);
    if (!edit || stepping.current) return;
    stepping.current = true;
    try {
      const renamed = await carryOut(edit, "redo");
      setHistory((current) => afterRedo(current, renamed));
      setDirty(true);
    } catch (error) {
      reportError(errorMessage(error));
    } finally {
      stepping.current = false;
    }
  }

  /**
   * Carry an edit out again (redo) or reverse it (undo) through Python. Returns the ids of
   * anything added back, which Python names anew; null otherwise. Throws when Python refuses.
   */
  async function carryOut(edit: Edit, direction: "undo" | "redo"): Promise<string[] | null> {
    const entities = documentRef.current?.entities ?? [];
    const present = (ids: string[]) => entities.filter((entity) => ids.includes(entity.id));
    if (edit.kind === "decide") {
      const steps =
        direction === "redo" ? new Map([[edit.after, Object.keys(edit.before)]]) : statesBefore(edit);
      for (const [state, ids] of steps) {
        const targets = present(ids);
        if (targets.length > 0 && !(await setReviews(targets, state))) throw new Error("The change was refused");
      }
      return null;
    }
    // Undoing an addition, or redoing a removal, removes the item; the other two add it back.
    const removes = (edit.kind === "add") === (direction === "undo");
    if (removes) {
      const [item] = present(edit.ids.slice(0, 1));
      if (item && !(await removeNow(item))) throw new Error("The change was refused");
      return null;
    }
    return (await addAgain(edit.addition)).map((entity) => entity.id);
  }

  /** Select the next undecided finding in the list's order, or the one before it. */
  function selectUndecided(direction: 1 | -1) {
    if (!document) return;
    const next = nextUndecided(findingSections(document.entities, view), selectedId, direction);
    if (next) select(next);
    else notify("success", "Every finding is decided");
  }

  /**
   * Keys without a modifier: R for the region tool, L for locating, Escape, Delete on a
   * selected item the reviewer added.
   */
  function onPlainKey(event: KeyboardEvent) {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === "?") {
      event.preventDefault();
      setShortcutsOpen(true);
      return;
    }
    if (!document) return;
    const selected = document.entities.find((entity) => entity.id === selectedId);
    if (event.key === "r" || event.key === "R") setDrawTool((value) => !value);
    else if (event.key === "l" || event.key === "L") setLocating((value) => !value);
    else if (event.key === "n" || event.key === "N") selectUndecided(event.shiftKey ? -1 : 1);
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
              undoLabel={history.done.at(-1)?.label ?? null}
              redoLabel={history.undone.at(-1)?.label ?? null}
              onUndo={() => void undo()}
              onRedo={() => void redo()}
              pageField={pageField}
              onPage={goToPage}
              onShortcuts={() => setShortcutsOpen(true)}
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
                onNext={() => selectUndecided(1)}
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
                <p>Drop to open another document</p>
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
              onOptions={changeOptions}
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
        <ShortcutsSheet open={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />
        <Toasts toasts={toasts} onDismiss={dismissToast} />
      </div>
    </MotionConfig>
  );
}

/** Whether a key went to a text field, where letters are typed rather than shortcuts. */
function isTyping(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  if (target instanceof HTMLInputElement) return !["checkbox", "radio", "button"].includes(target.type);
  return target.isContentEditable || ["TEXTAREA", "SELECT"].includes(target.tagName);
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
