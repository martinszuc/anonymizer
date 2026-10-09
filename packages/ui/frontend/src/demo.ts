// A stand-in for the Python side under `npm run dev` in a plain browser, so
// the interface can be worked on without pywebview. Loaded only in
// development (see bridge.ts); every value is synthetic.

import type { ReviewBridge } from "./bridge";
import type {
  AppStatus,
  Box,
  ChoiceStatus,
  DocumentInfo,
  EntityInfo,
  ExportProgress,
  ExportResult,
  LeakInfo,
  ModelState,
  FeatureModels,
  OpenOptions,
  OpenProgress,
  OpenStep,
  ReviewState,
  WordInfo,
} from "./types";

const PAGE_WIDTH = 595;
const PAGE_HEIGHT = 842;
const DEMO_PAGES = 2;
const LEFT = 72;
const FONT_SIZE = 11;

interface Line {
  text: string;
  y: number;
  size?: number;
  bold?: boolean;
}

const PAGE_ONE: Line[] = [
  { text: "Curriculum Vitae", y: 96, size: 22, bold: true },
  { text: "Jan Novák", y: 132, size: 15, bold: true },
  { text: "Address: Dlouhá 12, 110 00 Praha 1", y: 170 },
  { text: "E-mail: jan.novak@example.com", y: 188 },
  { text: "Phone: +420 603 123 456", y: 206 },
  { text: "IBAN: CZ65 0800 0000 1920 0014 5399", y: 224 },
  { text: "Profile: https://example.com/jnovak", y: 242 },
  { text: "Experience", y: 290, size: 13, bold: true },
  { text: "2019 – 2024   Software engineer, Example s.r.o.", y: 314 },
  { text: "Built document processing services for public administration.", y: 332 },
  { text: "2016 – 2019   Junior developer, Sample a.s.", y: 356 },
  { text: "References", y: 404, size: 13, bold: true },
  { text: "Available on request from Jan Novák or his former manager.", y: 428 },
];

const PAGE_TWO: Line[] = [
  { text: "Scanned certificate", y: 120, size: 18, bold: true },
  { text: "This page is an image without a text layer.", y: 160 },
];

function font(line: Line): string {
  return `${line.bold ? "600 " : ""}${line.size ?? FONT_SIZE}px Helvetica, Arial, sans-serif`;
}

const measure = document.createElement("canvas").getContext("2d");

/** The box of `part` within a line, in points, as ingest would report it. */
function boxOf(line: Line, part: string, at?: number): Box {
  const offset = at ?? line.text.indexOf(part);
  if (!measure || offset === -1) throw new Error(`demo text not found: ${part}`);
  measure.font = font(line);
  const x0 = LEFT + measure.measureText(line.text.slice(0, offset)).width;
  const x1 = x0 + measure.measureText(part).width;
  const size = line.size ?? FONT_SIZE;
  return [x0, line.y - size * 0.8, x1, line.y + size * 0.25];
}

/** A page's text as ingest would join it, one line per line, and its words with their boxes. */
function pageContent(lines: Line[]): { text: string; words: WordInfo[] } {
  let text = "";
  const words: WordInfo[] = [];
  for (const line of lines) {
    if (text) text += "\n";
    for (const found of line.text.matchAll(/\S+/g)) {
      const start = text.length + (found.index ?? 0);
      words.push({ start, end: start + found[0].length, text: found[0], box: boxOf(line, found[0], found.index) });
    }
    text += line.text;
  }
  return { text, words };
}

function overlaps(a: Box, b: Box): boolean {
  return a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
}

function lineOf(text: string): Line {
  const line = PAGE_ONE.find((candidate) => candidate.text.includes(text));
  if (!line) throw new Error(`demo line not found: ${text}`);
  return line;
}

let nextId = 0;

function found(
  type: string,
  text: string,
  overrides: Partial<EntityInfo> = {},
  line: Line = lineOf(text),
): EntityInfo {
  nextId += 1;
  return {
    id: `demo-${nextId}`,
    type,
    source: "rule",
    score: null,
    review: "pending",
    page_index: 0,
    surface_id: null,
    text,
    is_region: false,
    boxes: [boxOf(line, text)],
    ...overrides,
  };
}

function demoDocument(readScans = false): DocumentInfo {
  const reference = PAGE_ONE[PAGE_ONE.length - 1] as Line;
  const emailLine = lineOf("jan.novak@example.com");
  return {
    name: "demo-cv.pdf",
    language: "cs",
    language_recognised: true,
    pages: [
      { index: 0, width: PAGE_WIDTH, height: PAGE_HEIGHT, has_text_layer: true, raster_dpi: null },
      {
        index: 1,
        width: PAGE_WIDTH,
        height: PAGE_HEIGHT,
        has_text_layer: false,
        raster_dpi: readScans ? 300 : null,
      },
    ],
    entities: [
      found("person", "Jan Novák", { source: "model", score: 0.94 }),
      found("address", "Dlouhá 12, 110 00 Praha 1", { source: "model", score: 0.81 }),
      found("email", "jan.novak@example.com"),
      found("phone", "+420 603 123 456"),
      found("iban", "CZ65 0800 0000 1920 0014 5399"),
      found("url", "https://example.com/jnovak", { review: "confirmed" }),
      found("organization", "Example s.r.o.", { source: "model", score: 0.62, review: "rejected" }),
      // Uncertain model findings that are not names, as job titles often are.
      found("person", "Software engineer", { source: "model", score: 0.38 }),
      found("person", "Junior developer", { source: "model", score: 0.46 }),
      found("person", "Jan Novák", { source: "propagated" }, reference),
      found("email", "jan.novak@example.com", {
        surface_id: "link:0:12",
        boxes: [boxOf(emailLine, "jan.novak@example.com")],
      }),
      found("person", "Jan Novák", { page_index: null, surface_id: "metadata:title", boxes: [] }),
    ],
    surfaces: [
      { id: "metadata:title", kind: "metadata", value: "CV – Jan Novák", page_index: null, box: null },
      { id: "metadata:author", kind: "metadata", value: "jnovak", page_index: null, box: null },
      {
        id: "xmp",
        kind: "xmp",
        value: '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF><dc:creator>Jan Novák</dc:creator></rdf:RDF></x:xmpmeta>',
        page_index: null,
        box: null,
      },
      {
        id: "link:0:12",
        kind: "link",
        value: "mailto:jan.novak@example.com",
        page_index: 0,
        box: boxOf(emailLine, "jan.novak@example.com"),
      },
      { id: "bookmark:1", kind: "bookmark", value: "Jan Novák – CV", page_index: 0, box: null },
      { id: "embedded:0/desc", kind: "embedded_file", value: "original CV (cv.docx)", page_index: null, box: null },
    ],
  };
}

function renderPage(index: number, dpi: number): string {
  const scale = dpi / 72;
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(PAGE_WIDTH * scale);
  canvas.height = Math.round(PAGE_HEIGHT * scale);
  const context = canvas.getContext("2d");
  if (!context) return "";
  context.scale(scale, scale);
  context.fillStyle = index === 1 ? "#f4f1ea" : "#ffffff";
  context.fillRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
  context.fillStyle = "#1d1d1f";
  for (const line of index === 0 ? PAGE_ONE : PAGE_TWO) {
    context.font = font(line);
    context.fillText(line.text, LEFT, line.y);
  }
  return canvas.toDataURL("image/png");
}

const LATENCY_MS = 180;

/**
 * Every result is a copy, as pywebview's JSON round trip makes it; sharing
 * objects with the page would let a mutation here change React state.
 */
const copied = <T,>(value: T): T => structuredClone(value);
const pause = () => new Promise((resolve) => setTimeout(resolve, LATENCY_MS));

/** Tell the page how far opening is, as `WindowApi._progress` does. */
function progress(step: OpenStep, done = 0, total = 0) {
  const detail: OpenProgress = { step, done, total };
  window.dispatchEvent(new CustomEvent("anonymizer:progress", { detail }));
}

/** Tell the page how far an export is, as `WindowApi._export_progress` does. */
function exportProgress(step: ExportProgress["step"], done = 0, total = 0) {
  const detail: ExportProgress = { step, done, total };
  window.dispatchEvent(new CustomEvent("anonymizer:export", { detail }));
}

const CHECK_LAYERS: ExportProgress["step"][] = [
  "page_text",
  "region",
  "off_page_text",
  "surface",
  "thumbnail",
  "object",
  "file_bytes",
];

/** Kept in memory only, as a stand-in for the settings file. */
let leakCheck = true;
let openOptions: OpenOptions | null = null;

/** What the demo has "downloaded" this session, by feature. */
const downloaded = new Set<string>();
/** Set once the reviewer "chose" another folder, which starts empty. */
let emptyFolder = false;
let modelsFolder = "/Users/demo/Library/Application Support/anonymizer/models";

interface DemoFeature {
  title: string;
  description: string;
  group: string;
  models: [string, string, number][];
}

const DEMO_MODELS: Record<string, DemoFeature> = {
  "names-gliner-multi-v2.1": {
    title: "Names and addresses: GLiNER multilingual v2.1",
    description: "Zero-shot and multilingual. Finds names and addresses the rules cannot.",
    group: "ner",
    models: [
      ["mdeberta-v3-base-tokenizer", "mDeBERTa-v3 base: config and tokenizer", 4_309_802],
      ["gliner-multi-v2.1", "GLiNER multilingual v2.1", 1_155_830_112],
    ],
  },
  "names-gliner-cs-demo": {
    title: "Names and addresses: fine-tuned GLiNER (demo)",
    description: "A stand-in for a model trained on Czech and Slovak names.",
    group: "ner",
    models: [
      ["mdeberta-v3-base-tokenizer", "mDeBERTa-v3 base: config and tokenizer", 4_309_802],
      ["gliner-cs-demo", "Fine-tuned GLiNER (demo)", 1_155_830_112],
    ],
  },
  "ocr-onnxtr": {
    title: "Scanned pages: OnnxTR",
    description: "Fast. Reads printed text, not handwriting.",
    group: "ocr-onnxtr",
    models: [
      ["onnxtr-fast-base", "OnnxTR FAST base: text detection", 42_343_230],
      ["onnxtr-parseq-multilingual-v1", "OnnxTR PARSeq multilingual v1: text recognition", 96_713_181],
    ],
  },
  "ocr-kraken": {
    title: "Scanned pages: kraken",
    description: "Also reads handwriting and misreads print less, but takes about four times as long.",
    group: "ocr-kraken",
    models: [
      ["kraken-blla", "kraken BLLA: baseline and region segmentation", 5_047_020],
      ["kraken-ppocr-v6-medium", "PP-OCRv6 medium for kraken: handwritten and printed line recognition", 63_779_644],
    ],
  },
};

/**
 * The demo's name models: their name, title and feature. The second, a stand-in for a model
 * trained here, is offered with `?name_models=2`, so the choice between models shows.
 */
function demoNameModels() {
  const models = [
    { name: "gliner-multi-v2.1", title: "GLiNER multilingual v2.1", feature: "names-gliner-multi-v2.1" },
    { name: "gliner-cs-demo", title: "Fine-tuned GLiNER (demo)", feature: "names-gliner-cs-demo" },
  ];
  return new URLSearchParams(window.location.search).get("name_models") === "2" ? models : models.slice(0, 1);
}

/** The demo's OCR engines: their name, title and feature. */
const DEMO_ENGINES = [
  { name: "onnxtr", title: "OnnxTR", feature: "ocr-onnxtr" },
  { name: "kraken", title: "kraken", feature: "ocr-kraken" },
];

/**
 * A feature's state. The home screen's states can be tried in the address: `?model=`
 * (GLiNER), `?ocr=` (OnnxTR) or `?kraken=`, each `ready`, `not_installed` or
 * `files_missing`. kraken and the demo's second name model start with their files missing,
 * so both kinds of row show.
 */
function featureState(feature: string): ModelState {
  if (downloaded.has(feature)) return "ready";
  if (emptyFolder) return "files_missing";
  if (feature === "names-gliner-multi-v2.1") return requestedState("model", "ready");
  if (feature === "names-gliner-cs-demo") return "files_missing";
  return feature === "ocr-onnxtr" ? requestedState("ocr", "ready") : requestedState("kraken", "files_missing");
}

function demoStatus(): AppStatus {
  return {
    version: "demo",
    models_folder: modelsFolder,
    languages: [
      { code: "cs", name: "Czech" },
      { code: "sk", name: "Slovak" },
      { code: "en", name: "English" },
    ],
    names: { default: "gliner-multi-v2.1", models: demoNameModels().map(demoChoice) },
    ocr: {
      default: "onnxtr",
      engines: DEMO_ENGINES.map(demoChoice),
    },
    settings: { leak_check: leakCheck, open_options: openOptions },
  };
}

/** An OCR engine or a name model as `status` describes it. */
function demoChoice({ name, title, feature }: { name: string; title: string; feature: string }): ChoiceStatus {
  const entry = DEMO_MODELS[feature];
  const state = featureState(feature);
  return {
    name,
    title,
    description: entry?.description ?? "",
    feature,
    state,
    missing: state === "files_missing" ? (entry?.models.map(([id]) => id) ?? []) : [],
    install_command: `uv sync --group ${entry?.group ?? feature}`,
  };
}

function demoModels(): FeatureModels[] {
  const offered = new Set(demoNameModels().map((model) => model.feature));
  const features = Object.entries(DEMO_MODELS).filter(
    ([feature]) => !feature.startsWith("names-") || offered.has(feature),
  );
  return features.map(([feature, entry]) => {
    const state = featureState(feature);
    const stored = state !== "files_missing";
    return {
      feature,
      title: entry.title,
      description: entry.description,
      installed: state !== "not_installed",
      install_command: `uv sync --group ${entry.group}`,
      missing_bytes: stored ? 0 : entry.models.reduce((sum, [, , size]) => sum + size, 0),
      models: entry.models.map(([id, name, size]) => ({
        id,
        name,
        uses: [],
        licence: "Apache-2.0",
        languages: ["mul"],
        source: `https://huggingface.co/${id}`,
        version: "demo",
        size,
        state: stored ? "present" : "absent",
      })),
    };
  });
}

function requestedState(parameter: string, fallback: ModelState): ModelState {
  const requested = new URLSearchParams(window.location.search).get(parameter);
  return requested === "ready" || requested === "not_installed" || requested === "files_missing"
    ? requested
    : fallback;
}

/** Run through an export's steps, as Python tells them. */
async function demoExport(document: DocumentInfo, check: boolean) {
  for (let page = 0; page <= document.pages.length; page += 1) {
    exportProgress("redacting", page, document.pages.length);
    await pause();
  }
  exportProgress("clearing");
  await pause();
  exportProgress("saving");
  await pause();
  if (!check) return;
  for (const layer of CHECK_LAYERS) {
    exportProgress(layer);
    await pause();
  }
  const scans = document.pages.filter((page) => page.raster_dpi !== null).length;
  if (scans === 0) return;
  for (let page = 0; page <= scans; page += 1) {
    exportProgress("ocr", page, scans);
    await pause();
    await pause();
  }
}

function exportResult(
  document: DocumentInfo,
  unreadable: number[],
  leakCheck: ExportResult["leak_check"],
  leaks: LeakInfo[],
): ExportResult {
  const applied = document.entities.filter((entity) => entity.review !== "rejected");
  return {
    written: leaks.length === 0,
    name: "demo-cv-redacted.pdf",
    redacted: applied.filter((entity) => !entity.is_region).length,
    regions: applied.filter((entity) => entity.is_region).length,
    kept: document.entities.length - applied.length,
    not_reviewed: applied.filter((entity) => entity.review === "pending").length,
    hidden_removed: document.surfaces.length,
    pages_without_text: unreadable,
    leak_check: leakCheck,
    leaks,
  };
}

/** One leak of each kind, built from the demo's own synthetic findings. */
function demoLeaks(document: DocumentInfo): LeakInfo[] {
  const redacted = document.entities.find((entity) => entity.review !== "rejected" && entity.text !== null);
  const text = redacted?.text ?? "Jana Dvořáková";
  return [
    { layer: "page_text", where: "page 0", page: 1, text, entity_id: redacted?.id ?? null, kind: "text" },
    { layer: "object", where: "object 12", page: null, text, entity_id: redacted?.id ?? null, kind: "text" },
    { layer: "file_bytes", where: "the file's bytes", page: null, text, entity_id: redacted?.id ?? null, kind: "text" },
    { layer: "surface", where: "metadata Author", page: null, text: "J. Dvořáková", entity_id: null, kind: "leftover" },
  ];
}

export function demoBridge(): ReviewBridge {
  let current: DocumentInfo | null = null;
  /** Page 2 is a scan: its words exist once "OCR" has read it. */
  const contentOf = (index: number) =>
    pageContent(index === 0 ? PAGE_ONE : current?.pages[1]?.raster_dpi ? PAGE_TWO : []);
  let dropped = false;
  // OCR engines stay loaded for the session, as in Python.
  const loadedEngines = new Set<string>();
  // The last export the leak check refused, which the reviewer may save anyway.
  let refused = false;
  const open = async (options?: OpenOptions) => {
    const engine = options?.use_ocr ? options.ocr_engine : null;
    if (engine && !loadedEngines.has(engine)) {
      progress("loading_ocr");
      await pause();
      loadedEngines.add(engine);
    }
    progress("reading");
    await pause();
    if (engine) {
      progress("ocr", 0, 1);
      // kraken takes about four times as long per page.
      for (let wait = 0; wait < (engine === "kraken" ? 4 : 1); wait += 1) await pause();
      progress("ocr", 1, 1);
    }
    if (options?.use_model) {
      progress("loading_model");
      await pause();
      await pause();
    }
    for (let page = 0; page <= DEMO_PAGES; page += 1) {
      progress("detecting", page, DEMO_PAGES);
      await pause();
    }
    current = demoDocument(options?.use_ocr ?? false);
    return copied(current);
  };

  // A plain browser gives no file paths; a drop just stands in for pywebview's.
  window.addEventListener("dragover", (event) => event.preventDefault());
  window.addEventListener("drop", (event) => {
    event.preventDefault();
    const file = event.dataTransfer?.files[0];
    if (!file) return;
    const isPdf = file.name.toLowerCase().endsWith(".pdf");
    dropped = isPdf;
    const name = isPdf ? "anonymizer:dropped" : "anonymizer:drop-refused";
    window.dispatchEvent(new CustomEvent(name, { detail: file.name }));
  });

  return {
    status: async () => demoStatus(),
    models: async () => demoModels(),
    choose_models_folder: async () => {
      await pause();
      // A new, empty folder: nothing is downloaded there yet.
      modelsFolder = "/Volumes/Models/anonymizer/models";
      emptyFolder = true;
      downloaded.clear();
      return demoStatus();
    },
    download_models: async (feature: string) => {
      const total = demoModels().find((item) => item.feature === feature)?.missing_bytes ?? 0;
      for (let step = 0; step <= 20; step += 1) {
        const detail = { feature, received: Math.round((total * step) / 20), total };
        window.dispatchEvent(new CustomEvent("anonymizer:download", { detail }));
        await pause();
      }
      downloaded.add(feature);
      return demoModels();
    },
    current_document: async () => copied(current),
    choose_pdf: open,
    open_dropped: async (options: OpenOptions) => {
      if (!dropped) return null;
      dropped = false;
      return open(options);
    },
    close_document: async () => {
      current = null;
    },
    choose_session: () => open(),
    save_session_as: async () => {
      await pause();
      return true;
    },
    page_image: async (index, dpi) => {
      await pause();
      return renderPage(index, dpi);
    },
    set_leak_check: async (enabled: boolean) => {
      await pause();
      leakCheck = enabled;
      return demoStatus();
    },
    set_open_options: async (options: OpenOptions) => {
      openOptions = structuredClone(options);
      return demoStatus();
    },
    set_unsaved_changes: async () => {},
    show_export: async () => {},
    export_as: async (allowPagesWithoutText: boolean): Promise<ExportResult | null> => {
      await pause();
      if (!current) throw new Error("no document is open");
      const unreadable = current.pages
        .filter((page) => !page.has_text_layer && page.raster_dpi === null)
        .map((page) => page.index + 1);
      if (unreadable.length > 0 && !allowPagesWithoutText) {
        throw new Error(`page ${unreadable.join(", ")} is a scan OCR has not read; nothing on it would be redacted`);
      }
      await demoExport(current, leakCheck);
      // Keeping a finding stands in for a review that leaves something behind.
      const leaks = leakCheck && current.entities.some((entity) => entity.review === "rejected") ? demoLeaks(current) : [];
      refused = leaks.length > 0;
      return exportResult(current, unreadable, leakCheck ? (refused ? "failed" : "passed") : "off", leaks);
    },
    export_unchecked: async (): Promise<ExportResult> => {
      if (!current || !refused) throw new Error("there is no refused export to save");
      refused = false;
      await demoExport(current, false);
      return exportResult(current, [], "off", []);
    },
    add_region: async (pageIndex, x0, y0, x1, y1) => {
      if (!current) throw new Error("no document is open");
      nextId += 1;
      const region: EntityInfo = {
        id: `demo-${nextId}`,
        type: "region",
        source: "manual",
        score: null,
        review: "confirmed",
        page_index: pageIndex,
        surface_id: null,
        text: null,
        is_region: true,
        boxes: [[Math.min(x0, x1), Math.min(y0, y1), Math.max(x0, x1), Math.max(y0, y1)]],
      };
      current.entities.push(region);
      return copied(region);
    },
    page_words: async (index: number) => copied(contentOf(index).words),
    add_finding: async (pageIndex, start, end, type) => {
      await pause();
      if (!current) throw new Error("no document is open");
      const document = current;
      const selected = contentOf(pageIndex).words.filter((word) => word.start < end && start < word.end);
      const first = selected[0];
      const last = selected[selected.length - 1];
      if (!first || !last) throw new Error("the selection covers no word");
      const text = contentOf(pageIndex).text.slice(first.start, last.end).replace(/^\W+|\W+$/gu, "");
      const marked = (page: number, boxes: Box[]) =>
        document.entities.some(
          (entity) =>
            entity.page_index === page &&
            entity.surface_id === null &&
            entity.review !== "rejected" &&
            boxes.every((box) => entity.boxes.some((other) => overlaps(box, other))),
        );
      if (marked(pageIndex, selected.map((word) => word.box))) throw new Error("this text is already marked for redaction");
      const entityOf = (page: number, words: WordInfo[], source: EntityInfo["source"]): EntityInfo => {
        nextId += 1;
        return {
          id: `demo-${nextId}`,
          type,
          source,
          score: null,
          review: source === "manual" ? "confirmed" : "pending",
          page_index: page,
          surface_id: null,
          text,
          is_region: false,
          boxes: words.map((word) => word.box),
        };
      };
      const added = [entityOf(pageIndex, selected, "manual")];
      // Repeats: the same words in a row elsewhere, unless something already covers them.
      const wanted = text.split(/\s+/);
      for (const page of document.pages) {
        const words = contentOf(page.index).words;
        words.forEach((_, index) => {
          const run = words.slice(index, index + wanted.length);
          const same = run.length === wanted.length && run.every((word, at) => word.text.replace(/^\W+|\W+$/gu, "") === wanted[at]);
          const boxes = run.map((word) => word.box);
          if (!same || (page.index === pageIndex && run[0]?.start === first.start) || marked(page.index, boxes)) return;
          if (added.some((entity) => entity.page_index === page.index && boxes.every((box) => entity.boxes.includes(box)))) return;
          added.push(entityOf(page.index, run, "propagated"));
        });
      }
      document.entities.push(...added);
      return copied(added);
    },
    remove_entity: async (entityId: string) => {
      if (!current) throw new Error("no document is open");
      const entity = current.entities.find((item) => item.id === entityId);
      if (!entity) throw new Error(`no entity with id ${entityId}`);
      if (entity.source !== "manual") throw new Error("only items you added can be removed");
      current.entities = current.entities.filter((item) => item.id !== entityId);
      const stillMarked = current.entities.some((item) => item.source !== "propagated" && item.text === entity.text);
      const repeats = current.entities.filter(
        (item) =>
          entity.text !== null &&
          !stillMarked &&
          item.source === "propagated" &&
          item.review !== "confirmed" &&
          item.text === entity.text,
      );
      current.entities = current.entities.filter((item) => !repeats.includes(item));
      return [entityId, ...repeats.map((item) => item.id)];
    },
    set_review: async (entityId: string, state: ReviewState) => {
      const entity = current?.entities.find((item) => item.id === entityId);
      if (!entity) throw new Error(`no entity with id ${entityId}`);
      entity.review = state;
      return copied(entity);
    },
    set_reviews: async (entityIds: string[], state: ReviewState) => {
      const entities = entityIds.map((id) => current?.entities.find((item) => item.id === id));
      const missing = entityIds.find((_, index) => !entities[index]);
      if (missing !== undefined) throw new Error(`no entity with id ${missing}`);
      for (const entity of entities) if (entity) entity.review = state;
      return copied(entities.filter((entity) => entity !== undefined));
    },
  };
}
