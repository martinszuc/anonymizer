// Review rules shared by the page view and the sidebar. Pure, so they are unit-tested.

import type { DocumentInfo, EntityInfo, ReviewState } from "./types";

/** Undecided items are redacted at export (decided in PLAN.md), so only a rejection keeps text. */
export function isRedacted(state: ReviewState): boolean {
  return state !== "rejected";
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
  const redacted = document.entities.filter((entity) => isRedacted(entity.review)).length;
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
