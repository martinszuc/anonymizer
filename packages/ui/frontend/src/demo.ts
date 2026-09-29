// A stand-in for the Python side under `npm run dev` in a plain browser, so
// the interface can be worked on without pywebview. Loaded only in
// development (see bridge.ts); every value is synthetic.

import type { ReviewBridge } from "./bridge";
import type { Box, DocumentInfo, EntityInfo, ReviewState } from "./types";

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

function demoDocument(): DocumentInfo {
  const reference = PAGE_ONE[PAGE_ONE.length - 1] as Line;
  const emailLine = lineOf("jan.novak@example.com");
  return {
    name: "demo-cv.pdf",
    language: "cs",
    pages: [
      { index: 0, width: PAGE_WIDTH, height: PAGE_HEIGHT, has_text_layer: true },
      { index: 1, width: PAGE_WIDTH, height: PAGE_HEIGHT, has_text_layer: false },
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
const pause = () => new Promise((resolve) => setTimeout(resolve, LATENCY_MS));

export function demoBridge(): ReviewBridge {
  let current: DocumentInfo | null = null;
  const open = async () => {
    await pause();
    current = demoDocument();
    return current;
  };
  return {
    current_document: async () => current,
    choose_pdf: open,
    choose_session: open,
    save_session_as: async () => {
      await pause();
      return true;
    },
    page_image: async (index, dpi) => {
      await pause();
      return renderPage(index, dpi);
    },
    set_review: async (entityId: string, state: ReviewState) => {
      const entity = current?.entities.find((item) => item.id === entityId);
      if (!entity) throw new Error(`no entity with id ${entityId}`);
      entity.review = state;
      return { ...entity };
    },
  };
}
