// Review rules shared by the page view and the sidebar. Pure, so they are unit-tested.

import type { Box, DocumentInfo, EntityInfo, ExportResult, ReviewState } from "./types";

/** Undecided items are redacted at export (decided in PLAN.md), so only a rejection keeps text. */
export function isRedacted(state: ReviewState): boolean {
  return state !== "rejected";
}

/**
 * Whether export removes an entity. A finding in hidden data goes with the
 * hidden item, which export always clears, whatever its review says.
 */
export function isRemoved(entity: EntityInfo): boolean {
  return entity.surface_id !== null || isRedacted(entity.review);
}

/** Whether the reviewer decides on the entity; a region is removed instead, hidden data always goes. */
export function isDecidable(entity: EntityInfo): boolean {
  return entity.surface_id === null && !entity.is_region;
}

/** One click flips what export will do; toggling back is an explicit decision to redact. */
export function toggled(state: ReviewState): ReviewState {
  return isRedacted(state) ? "rejected" : "confirmed";
}

export interface Summary {
  redacted: number;
  kept: number;
  hidden: number;
}

export function summarize(document: DocumentInfo): Summary {
  const redacted = document.entities.filter(isRemoved).length;
  return {
    redacted,
    kept: document.entities.length - redacted,
    hidden: document.surfaces.length,
  };
}

const TYPE_LABELS: Record<string, string> = {
  person: "Names",
  email: "Email addresses",
  phone: "Phone numbers",
  url: "Links",
  address: "Addresses",
  birth_number: "Birth numbers",
  id_number: "ID numbers",
  iban: "IBANs",
  bank_account: "Bank accounts",
  credit_card: "Payment cards",
  company_id: "Company IDs",
  organization: "Organizations",
  date: "Dates",
  region: "Regions",
  other: "Other",
};

const TYPE_ORDER = Object.keys(TYPE_LABELS);

export function typeLabel(type: string): string {
  return TYPE_LABELS[type] ?? type;
}

/** Identifiers read better in a monospace face; names and addresses do not. */
export function isIdentifier(type: string): boolean {
  return !["person", "address", "organization", "region", "other"].includes(type);
}

export interface EntityGroup {
  type: string;
  label: string;
  entities: EntityInfo[];
}

/** Entities grouped by type in a fixed order, each group in reading order. */
export function groupByType(entities: EntityInfo[]): EntityGroup[] {
  const groups = new Map<string, EntityInfo[]>();
  for (const entity of [...entities].sort(byReadingOrder)) {
    groups.set(entity.type, [...(groups.get(entity.type) ?? []), entity]);
  }
  const rank = (type: string) => {
    const index = TYPE_ORDER.indexOf(type);
    return index === -1 ? TYPE_ORDER.length : index;
  };
  return [...groups.entries()]
    .sort(([a], [b]) => rank(a) - rank(b) || a.localeCompare(b))
    .map(([type, members]) => ({ type, label: typeLabel(type), entities: members }));
}

function byReadingOrder(a: EntityInfo, b: EntityInfo): number {
  // Document-level entities (metadata) have no page and come last.
  const pageA = a.page_index ?? Number.MAX_SAFE_INTEGER;
  const pageB = b.page_index ?? Number.MAX_SAFE_INTEGER;
  const [leftA = 0, topA = 0] = a.boxes[0] ?? [];
  const [leftB = 0, topB = 0] = b.boxes[0] ?? [];
  return pageA - pageB || topA - topB || leftA - leftB;
}

/** What a row or popover shows for an entity. */
export function covers(entity: EntityInfo): string {
  if (entity.is_region) return "Drawn region";
  return (entity.text ?? "").replace(/\s+/g, " ").trim();
}

const MIN_DPI = 72;
const MAX_DPI = 400;
const DPI_STEP = 24;

/**
 * Resolution to render a page at for a zoom (CSS pixels per point) on a
 * screen. Rounded up to a step, so small zoom changes reuse the same image.
 */
export function renderDpi(scale: number, pixelRatio: number): number {
  const exact = 72 * scale * pixelRatio;
  const stepped = Math.ceil(exact / DPI_STEP) * DPI_STEP;
  return Math.min(Math.max(stepped, MIN_DPI), MAX_DPI);
}

export const ZOOM_STEPS = [0.5, 0.75, 1, 1.25, 1.5, 2, 3];

/** The next zoom step above or below the current scale. */
export function steppedZoom(scale: number, direction: 1 | -1): number {
  if (direction === 1) return ZOOM_STEPS.find((step) => step > scale + 0.01) ?? scale;
  return [...ZOOM_STEPS].reverse().find((step) => step < scale - 0.01) ?? scale;
}

/** 1-based numbers of the pages export cannot redact: they have no text layer. */
export function pagesWithoutText(document: DocumentInfo): number[] {
  return document.pages.filter((page) => !page.has_text_layer).map((page) => page.index + 1);
}

/** "page 3", "pages 2 and 5", "pages 1, 2 and 4". */
export function pageList(pages: number[]): string {
  if (pages.length === 1) return `page ${pages[0]}`;
  return `pages ${pages.slice(0, -1).join(", ")} and ${pages[pages.length - 1]}`;
}

export function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

export interface ExportLine {
  label: string;
  value: string;
}

/** The rows of the export result sheet, in reading order. */
export function exportSummary(result: ExportResult): ExportLine[] {
  const lines: ExportLine[] = [];
  const unreviewed = result.not_reviewed > 0 ? `, ${result.not_reviewed} not reviewed` : "";
  lines.push({ label: "Redacted", value: `${plural(result.redacted, "item")}${unreviewed}` });
  if (result.regions > 0) lines.push({ label: "Regions", value: plural(result.regions, "region") });
  lines.push({ label: "Kept", value: plural(result.kept, "item") });
  lines.push({ label: "Hidden data removed", value: plural(result.hidden_removed, "item") });
  return lines;
}

const LEAK_LAYERS: Record<string, string> = {
  page_text: "Page text",
  region: "Drawn region",
  off_page_text: "Outside the page",
  surface: "Hidden data",
  thumbnail: "Page thumbnail",
  object: "PDF object",
  file_bytes: "File bytes",
};

export function leakLayerLabel(layer: string): string {
  return LEAK_LAYERS[layer] ?? layer;
}

/** A drag across a page, in page points: normalised and clamped to the page. */
export function dragBox(
  start: [number, number],
  end: [number, number],
  page: { width: number; height: number },
): Box {
  const clampX = (x: number) => Math.min(Math.max(x, 0), page.width);
  const clampY = (y: number) => Math.min(Math.max(y, 0), page.height);
  const [x0, x1] = [clampX(start[0]), clampX(end[0])].sort((a, b) => a - b) as [number, number];
  const [y0, y1] = [clampY(start[1]), clampY(end[1])].sort((a, b) => a - b) as [number, number];
  return [x0, y0, x1, y1];
}

/** Smallest region side on screen: anything smaller was a click, not a drag. */
export const MIN_REGION_PIXELS = 6;

export function isLargeEnough(box: Box, scale: number): boolean {
  const [x0, y0, x1, y1] = box;
  return (x1 - x0) * scale >= MIN_REGION_PIXELS && (y1 - y0) * scale >= MIN_REGION_PIXELS;
}
