// A stand-in for the Python side under `npm run dev` in a plain browser, so
// the interface can be worked on without pywebview. Loaded only in
// development (see bridge.ts); every value is synthetic.

import type { ReviewBridge } from "./bridge";
import type {
  AppStatus,
  Box,
  DocumentInfo,
  EntityInfo,
  ExportResult,
  ModelState,
  FeatureModels,
  OpenOptions,
  OpenStep,
  ReviewState,
} from "./types";

const PAGE_WIDTH = 595;
const PAGE_HEIGHT = 842;
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
function boxOf(line: Line, part: string): Box {
  const offset = line.text.indexOf(part);
  if (!measure || offset === -1) throw new Error(`demo text not found: ${part}`);
  measure.font = font(line);
  const x0 = LEFT + measure.measureText(line.text.slice(0, offset)).width;
  const x1 = x0 + measure.measureText(part).width;
  const size = line.size ?? FONT_SIZE;
  return [x0, line.y - size * 0.8, x1, line.y + size * 0.25];
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

/** Every result is a copy, as pywebview's JSON round trip makes it; sharing
 * objects with the page would let a mutation here change React state. */
const copied = <T,>(value: T): T => structuredClone(value);
const pause = () => new Promise((resolve) => setTimeout(resolve, LATENCY_MS));

/** Tell the page a step of opening has started, as `WindowApi._progress` does. */
function progress(step: OpenStep) {
  window.dispatchEvent(new CustomEvent("anonymizer:progress", { detail: step }));
}

/**
 * The home screen's model and OCR states can be tried with `?model=not_installed`,
 * `?model=files_missing`, `?ocr=not_installed` or `?ocr=files_missing` in the address.
 */
/** What the demo has "downloaded" this session. */
const downloaded = new Set<string>();
/** Set once the reviewer "chose" another folder, which starts empty. */
let emptyFolder = false;
let modelsFolder = "/Users/demo/Library/Application Support/anonymizer/models";

function demoStatus(): AppStatus {
  const state = downloaded.has("names") ? "ready" : emptyFolder ? "files_missing" : requestedState("model");
  const ocrState = downloaded.has("ocr") ? "ready" : emptyFolder ? "files_missing" : requestedState("ocr");
  return {
    version: "demo",
    models_folder: modelsFolder,
    languages: [
      { code: "cs", name: "Czech" },
      { code: "sk", name: "Slovak" },
      { code: "en", name: "English" },
    ],
    model: {
      state,
      missing: state === "files_missing" ? ["mdeberta-v3-base-tokenizer", "gliner-multi-v2.1"] : [],
    },
    ocr: {
      engine: "onnxtr",
      state: ocrState,
      missing: ocrState === "files_missing" ? ["onnxtr-fast-base", "onnxtr-parseq-multilingual-v1"] : [],
    },
  };
}

const DEMO_MODELS: Record<string, { title: string; group: string; models: [string, string, number][] }> = {
  names: {
    title: "Names and addresses",
    group: "ner",
    models: [
      ["mdeberta-v3-base-tokenizer", "mDeBERTa-v3 base: config and tokenizer", 4_309_802],
      ["gliner-multi-v2.1", "GLiNER multilingual v2.1", 1_155_830_112],
    ],
  },
  ocr: {
    title: "Scanned pages",
    group: "ocr-onnxtr",
    models: [
      ["onnxtr-fast-base", "OnnxTR FAST base: text detection", 42_343_230],
      ["onnxtr-parseq-multilingual-v1", "OnnxTR PARSeq multilingual v1: text recognition", 96_713_181],
    ],
  },
};

function demoModels(): FeatureModels[] {
  const status = demoStatus();
  return Object.entries(DEMO_MODELS).map(([feature, entry]) => {
    const state = feature === "names" ? status.model.state : status.ocr.state;
    const stored = state !== "files_missing";
    return {
      feature,
      title: entry.title,
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

function requestedState(parameter: string): ModelState {
  const requested = new URLSearchParams(window.location.search).get(parameter);
  return requested === "not_installed" || requested === "files_missing" ? requested : "ready";
}

export function demoBridge(): ReviewBridge {
  let current: DocumentInfo | null = null;
  let dropped = false;
  let ocrLoaded = false;
  const open = async (options?: OpenOptions) => {
    if (options?.use_ocr && !ocrLoaded) {
      progress("loading_ocr");
      await pause();
      ocrLoaded = true;
    }
    progress("reading");
    await pause();
    if (options?.use_model) {
      progress("loading_model");
      await pause();
      await pause();
    }
    progress("detecting");
    await pause();
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
    export_as: async (allowPagesWithoutText: boolean): Promise<ExportResult | null> => {
      await pause();
      if (!current) throw new Error("no document is open");
      const unreadable = current.pages
        .filter((page) => !page.has_text_layer && page.raster_dpi === null)
        .map((page) => page.index + 1);
      if (unreadable.length > 0 && !allowPagesWithoutText) {
        throw new Error(`page ${unreadable.join(", ")} is a scan OCR has not read; nothing on it would be redacted`);
      }
      const applied = current.entities.filter((entity) => entity.review !== "rejected");
      return {
        written: true,
        name: "demo-cv-redacted.pdf",
        redacted: applied.filter((entity) => !entity.is_region).length,
        regions: applied.filter((entity) => entity.is_region).length,
        kept: current.entities.length - applied.length,
        not_reviewed: applied.filter((entity) => entity.review === "pending").length,
        hidden_removed: current.surfaces.length,
        pages_without_text: unreadable,
        leaks: [],
      };
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
    remove_entity: async (entityId: string) => {
      if (!current) throw new Error("no document is open");
      const entity = current.entities.find((item) => item.id === entityId);
      if (!entity) throw new Error(`no entity with id ${entityId}`);
      if (entity.source !== "manual") throw new Error("only items you added can be removed");
      current.entities = current.entities.filter((item) => item.id !== entityId);
    },
    set_review: async (entityId: string, state: ReviewState) => {
      const entity = current?.entities.find((item) => item.id === entityId);
      if (!entity) throw new Error(`no entity with id ${entityId}`);
      entity.review = state;
      return copied(entity);
    },
  };
}
