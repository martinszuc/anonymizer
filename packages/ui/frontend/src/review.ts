// Review rules shared by the page view and the sidebar. Pure, so they are unit-tested.

import type {
  Box,
  ChoiceStatus,
  DocumentInfo,
  EntityInfo,
  ExportProgress,
  ExportResult,
  ExportStep,
  LeakInfo,
  LeakKind,
  NamesStatus,
  OcrStatus,
  OpenOptions,
  OpenProgress,
  OpenStep,
  PageInfo,
  ReviewState,
} from "./types";

/** Undecided items are redacted at export, so only a rejection keeps text. */
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

/**
 * Entities grouped by type in a fixed order, each group in reading order,
 * except drawn regions, which keep the order they were drawn in, as their numbers do.
 */
export function groupByType(entities: EntityInfo[]): EntityGroup[] {
  const groups = new Map<string, EntityInfo[]>();
  for (const entity of entities) {
    groups.set(entity.type, [...(groups.get(entity.type) ?? []), entity]);
  }
  const rank = (type: string) => {
    const index = TYPE_ORDER.indexOf(type);
    return index === -1 ? TYPE_ORDER.length : index;
  };
  return [...groups.entries()]
    .sort(([a], [b]) => rank(a) - rank(b) || a.localeCompare(b))
    .map(([type, members]) => ({
      type,
      label: typeLabel(type),
      entities: type === "region" ? members : members.sort(byReadingOrder),
    }));
}

/** Identical findings of one type, shown as one row and decided together. */
export interface Occurrences {
  key: string;
  /** In reading order; one member for a finding that occurs once. */
  members: EntityInfo[];
}

/**
 * Findings of one group split into identical ones: same text, ignoring case and
 * spacing. A region, and a finding in hidden data (nothing to decide), stays alone
 * unless its text repeats in hidden data too. Order follows each text's first occurrence.
 */
export function groupOccurrences(entities: EntityInfo[]): Occurrences[] {
  const byKey = new Map<string, EntityInfo[]>();
  for (const entity of entities) {
    const key = entity.is_region
      ? `region:${entity.id}`
      : `${entity.type}:${isDecidable(entity)}:${covers(entity).toLocaleLowerCase()}`;
    byKey.set(key, [...(byKey.get(key) ?? []), entity]);
  }
  return [...byKey.entries()].map(([key, members]) => ({ key, members }));
}

export type GroupDecision = "redacted" | "kept" | "mixed";

/** What export does with a group: all of it removed, all kept, or some of each. */
export function groupDecision(members: EntityInfo[]): GroupDecision {
  const removed = members.filter(isRemoved).length;
  if (removed === members.length) return "redacted";
  return removed === 0 ? "kept" : "mixed";
}

/** One switch for a group: keep everything when all is redacted, otherwise redact everything. */
export function groupToggled(members: EntityInfo[]): ReviewState {
  return groupDecision(members) === "redacted" ? "rejected" : "confirmed";
}

/** Score steps offered for finding the model's least certain findings. */
export const SCORE_STEPS = [0.4, 0.5, 0.6, 0.7] as const;

/** Identical findings share a text key: type and text, ignoring case and spacing. */
function textKey(entity: EntityInfo): string {
  return `${entity.type}:${covers(entity).toLocaleLowerCase()}`;
}

/**
 * The model's score for each text, by its best evidence: the highest score among
 * its identical findings. A text a rule or the reviewer also found has no score
 * (null): that evidence outranks any score. Repeats and hidden data add nothing.
 */
export function textScores(entities: EntityInfo[]): Map<string, number | null> {
  const scores = new Map<string, number | null>();
  for (const entity of entities) {
    if (!isDecidable(entity) || entity.source === "propagated") continue;
    const key = textKey(entity);
    if (entity.source !== "model" || entity.score === null) {
      scores.set(key, null);
    } else if (scores.get(key) !== null) {
      scores.set(key, Math.max(scores.get(key) ?? 0, entity.score));
    }
  }
  return scores;
}

/** A decidable finding's score by its text (see `textScores`); null for anything else. */
function scoreOf(entity: EntityInfo, scores: Map<string, number | null>): number | null {
  return isDecidable(entity) ? (scores.get(textKey(entity)) ?? null) : null;
}

/**
 * Undecided findings the model scored below a threshold, with their repeats, so a
 * group of identical findings is kept whole. Nothing already decided is included.
 */
export function lowConfidence(entities: EntityInfo[], threshold: number): EntityInfo[] {
  const scores = textScores(entities);
  return entities.filter((entity) => {
    const score = scoreOf(entity, scores);
    return entity.review === "pending" && score !== null && score < threshold;
  });
}

export type SortOrder = "type" | "score-asc" | "score-desc" | "occurrences" | "page" | "text";

export const SORT_ORDERS: { value: SortOrder; label: string }[] = [
  { value: "type", label: "Type" },
  { value: "score-asc", label: "Least certain first" },
  { value: "score-desc", label: "Most certain first" },
  { value: "occurrences", label: "Most repeated first" },
  { value: "page", label: "Page order" },
  { value: "text", label: "A–Z" },
];

export type DecisionFilter = "all" | "undecided" | "redacted" | "kept";
export type SourceFilter = "rule" | "model" | "propagated" | "manual";

export interface FindingFilter {
  decision: DecisionFilter;
  /** Empty: every source. */
  sources: SourceFilter[];
  /** Only findings the model scored below this; null for any. */
  scoreBelow: number | null;
  /** Found text containing this, ignoring case and diacritics ("novak" finds "Novák"). */
  text: string;
}

export const NO_FILTER: FindingFilter = { decision: "all", sources: [], scoreBelow: null, text: "" };

/** How the findings list is shown: its order, its sections and what it leaves out. */
export interface ListView {
  sort: SortOrder;
  /** Sections per type; always for the "type" order. */
  byType: boolean;
  filter: FindingFilter;
}

export const DEFAULT_VIEW: ListView = { sort: "type", byType: true, filter: NO_FILTER };

/** The view after choosing an order: sections by type for "type", one list otherwise. */
export function sortedBy(view: ListView, sort: SortOrder): ListView {
  return { ...view, sort, byType: sort === "type" };
}

/** How many filter settings are active, the search included. */
export function activeFilters(filter: FindingFilter): number {
  return (
    Number(filter.decision !== "all") +
    Number(filter.sources.length > 0) +
    Number(filter.scoreBelow !== null) +
    Number(filter.text.trim() !== "")
  );
}

function folded(text: string): string {
  return text.normalize("NFD").replace(/\p{M}/gu, "").toLocaleLowerCase();
}

function matches(
  entity: EntityInfo,
  filter: FindingFilter,
  scores: Map<string, number | null>,
  numbers: Map<string, number>,
): boolean {
  if (filter.decision === "undecided" && !(isDecidable(entity) && entity.review === "pending")) return false;
  if (filter.decision === "redacted" && !isRemoved(entity)) return false;
  if (filter.decision === "kept" && isRemoved(entity)) return false;
  if (filter.sources.length > 0 && !filter.sources.includes(entity.source as SourceFilter)) return false;
  if (filter.scoreBelow !== null) {
    const score = scoreOf(entity, scores);
    if (score === null || score >= filter.scoreBelow) return false;
  }
  const query = folded(filter.text.trim());
  return query === "" || folded(covers(entity, numbers.get(entity.id))).includes(query);
}

/** The findings a filter lets through. */
export function filterFindings(entities: EntityInfo[], filter: FindingFilter): EntityInfo[] {
  const scores = textScores(entities);
  const numbers = regionNumbers(entities);
  return entities.filter((entity) => matches(entity, filter, scores, numbers));
}

/** A row of the list: one finding, or several identical ones decided together. */
export interface FindingRow {
  key: string;
  /** In reading order. */
  members: EntityInfo[];
  /** The model's score for the text (see `textScores`); null without one. */
  score: number | null;
}

/** A section of the list: one type, or (type null) every finding in one list. */
export interface FindingSection {
  type: string | null;
  label: string;
  rows: FindingRow[];
}

/**
 * The findings list as a view shows it: filtered, grouped into rows of identical
 * findings, in sections by type or one list, in the chosen order. Rows without a
 * score (rules, regions, hidden data) come after scored ones in either score order;
 * ties keep page order.
 */
export function findingSections(entities: EntityInfo[], view: ListView): FindingSection[] {
  const scores = textScores(entities);
  const shown = filterFindings(entities, view.filter);
  const rows = (members: EntityInfo[]): FindingRow[] =>
    sortRows(
      groupOccurrences(members).map((found) => ({
        key: found.key,
        members: found.members,
        score: scoreOf(found.members[0] as EntityInfo, scores),
      })),
      view.sort,
    );
  if (view.byType || view.sort === "type") {
    return groupByType(shown).map((group) => ({ type: group.type, label: group.label, rows: rows(group.entities) }));
  }
  return [{ type: null, label: "Findings", rows: rows([...shown].sort(byReadingOrder)) }];
}

function sortRows(rows: FindingRow[], sort: SortOrder): FindingRow[] {
  const first = (row: FindingRow) => row.members[0] as EntityInfo;
  const page = (a: FindingRow, b: FindingRow) => byReadingOrder(first(a), first(b));
  const byScore = (direction: 1 | -1) => (a: FindingRow, b: FindingRow) => {
    if (a.score === null || b.score === null) return Number(a.score === null) - Number(b.score === null) || page(a, b);
    return direction * (a.score - b.score) || page(a, b);
  };
  const compare: Record<SortOrder, ((a: FindingRow, b: FindingRow) => number) | null> = {
    type: null, // reading order, and drawing order for regions, as grouped
    "score-asc": byScore(1),
    "score-desc": byScore(-1),
    occurrences: (a, b) => b.members.length - a.members.length || page(a, b),
    page,
    text: (a, b) => covers(first(a)).localeCompare(covers(first(b)), undefined, { sensitivity: "base" }) || page(a, b),
  };
  const order = compare[sort];
  return order ? [...rows].sort(order) : rows;
}

/** The scores of a group as a reader sees them: "38 %" or "38–46 %"; null without any. */
export function scoreRange(members: EntityInfo[]): string | null {
  const scores = members.flatMap((member) => (member.score === null ? [] : [Math.round(member.score * 100)]));
  if (scores.length === 0) return null;
  const [low, high] = [Math.min(...scores), Math.max(...scores)];
  return low === high ? `${low} %` : `${low}–${high} %`;
}

/** What "Keep" acts on: the undecided findings a list shows; decisions already made stay. */
export function keepable(sections: FindingSection[]): EntityInfo[] {
  return sections.flatMap((section) =>
    section.rows.flatMap((row) => row.members.filter((member) => isDecidable(member) && member.review === "pending")),
  );
}

/** Drawn regions numbered 1, 2, … in the order they were drawn, as the page and the list show them. */
export function regionNumbers(entities: EntityInfo[]): Map<string, number> {
  const numbers = new Map<string, number>();
  for (const entity of entities) {
    if (entity.is_region) numbers.set(entity.id, numbers.size + 1);
  }
  return numbers;
}

function byReadingOrder(a: EntityInfo, b: EntityInfo): number {
  // Document-level entities (metadata) have no page and come last.
  const pageA = a.page_index ?? Number.MAX_SAFE_INTEGER;
  const pageB = b.page_index ?? Number.MAX_SAFE_INTEGER;
  const [leftA = 0, topA = 0] = a.boxes[0] ?? [];
  const [leftB = 0, topB = 0] = b.boxes[0] ?? [];
  return pageA - pageB || topA - topB || leftA - leftB;
}

/** What a row or popover shows for an entity; a region by its number when it has one. */
export function covers(entity: EntityInfo, regionNumber?: number): string {
  if (entity.is_region) return regionNumber === undefined ? "Drawn region" : `Region ${regionNumber}`;
  return (entity.text ?? "").replace(/\s+/g, " ").trim();
}

/**
 * The last item the reviewer added (a drawn region or selected text) that is still in the
 * document, for Cmd/Ctrl+Z; ids are in the order they were added.
 */
export function lastAdded(addedIds: string[], entities: EntityInfo[]): EntityInfo | null {
  for (const id of [...addedIds].reverse()) {
    const added = entities.find((entity) => entity.id === id && entity.source === "manual");
    if (added) return added;
  }
  return null;
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

/** Whether a page is a scan OCR has not read: nothing on it was detected. */
export function isUnreadScan(page: PageInfo): boolean {
  return !page.has_text_layer && page.raster_dpi === null;
}

/** 1-based numbers of the pages export cannot redact: scans OCR has not read. */
export function pagesWithoutText(document: DocumentInfo): number[] {
  return document.pages.filter(isUnreadScan).map((page) => page.index + 1);
}

/** Whether a choice can run now: installed, with its models stored. */
export function choiceReady(choices: ChoiceStatus[], name: string): boolean {
  return choices.some((choice) => choice.name === name && choice.state === "ready");
}

/**
 * The choice to run: the first ready one of `preferred`, then the default, then any ready
 * one. With none ready, the first preferred, so a choice outlasts a missing model.
 */
export function chooseReady(choices: ChoiceStatus[], fallback: string, preferred: (string | null)[]): string {
  const order = [...preferred, fallback, ...choices.map((choice) => choice.name)].filter(
    (name): name is string => name !== null,
  );
  return order.find((name) => choiceReady(choices, name)) ?? order[0] ?? fallback;
}

/** OCR's part of the options a PDF opens with. */
export type OcrOptions = Pick<OpenOptions, "use_ocr" | "ocr_engine">;

/** Whether an engine can read now: installed, with its models stored. */
export function ocrReady(ocr: OcrStatus, name: string): boolean {
  return choiceReady(ocr.engines, name);
}

/** The engine to read with (see `chooseReady`). */
export function chooseOcrEngine(ocr: OcrStatus, preferred: (string | null)[]): string {
  return chooseReady(ocr.engines, ocr.default, preferred);
}

/**
 * OCR's options once the installation changed. The choice stays while its engine is ready,
 * otherwise a ready one takes its place; OCR stays on only with a ready engine. `downloaded`
 * names an engine whose models just arrived: it is chosen and OCR turns on.
 */
export function ocrOptions(ocr: OcrStatus, current: OcrOptions, downloaded: string | null = null): OcrOptions {
  const engine = chooseOcrEngine(ocr, [downloaded, current.ocr_engine]);
  const turnedOn = downloaded !== null && ocrReady(ocr, downloaded);
  return { ocr_engine: engine, use_ocr: (current.use_ocr || turnedOn) && ocrReady(ocr, engine) };
}

/** The name model's part of the options a PDF opens with. */
export type NameModelOptions = Pick<OpenOptions, "use_model" | "name_model">;

/** Whether a name model can run now: installed, with its files stored. */
export function nameModelReady(names: NamesStatus, name: string): boolean {
  return choiceReady(names.models, name);
}

/** The name model's options once the installation changed, as `ocrOptions` keeps OCR's. */
export function nameModelOptions(
  names: NamesStatus,
  current: NameModelOptions,
  downloaded: string | null = null,
): NameModelOptions {
  const model = chooseReady(names.models, names.default, [downloaded, current.name_model]);
  const turnedOn = downloaded !== null && nameModelReady(names, downloaded);
  return { name_model: model, use_model: (current.use_model || turnedOn) && nameModelReady(names, model) };
}

/** A size for people: "980 B", "42.3 MB", "1.16 GB" (decimal units, as downloads show). */
export function formatBytes(bytes: number): string {
  const units = ["B", "kB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1000 && unit < units.length - 1) {
    value /= 1000;
    unit += 1;
  }
  const digits = unit === 0 ? 0 : value < 10 ? 2 : 1;
  return `${value.toFixed(digits)} ${units[unit]}`;
}

/** "page 3", "pages 2 and 5", "pages 1, 2 and 4". */
export function pageList(pages: number[]): string {
  if (pages.length === 1) return `page ${pages[0]}`;
  return `pages ${pages.slice(0, -1).join(", ")} and ${pages[pages.length - 1]}`;
}

/** A text cut to `length` characters, an ellipsis marking the cut. */
export function truncated(text: string, length: number): string {
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
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
  ocr: "Re-read by OCR",
};

export function leakLayerLabel(layer: string): string {
  return LEAK_LAYERS[layer] ?? layer;
}

/** A leak, or several of one text, as a row of the export's warning sheet. */
export interface LeakRow {
  key: string;
  /** What was found: the text, or what is left ("drawing", "page thumbnail"). */
  title: string;
  /** Where it was found, in words. */
  where: string;
  /** 1-based page to show, or null when it lies in no page. */
  page: number | null;
  /** A finding to select, when one is involved. */
  entityId: string | null;
}

export interface LeakSection {
  kind: LeakKind;
  title: string;
  /** What it means and what the reviewer can do. */
  note: string;
  rows: LeakRow[];
}

const LEAK_SECTIONS: Record<LeakKind, { title: string; note: string }> = {
  under_box: {
    title: "Left under a box",
    note: "Redaction did not remove what lies under these boxes. Look at the page before saving.",
  },
  leftover: {
    title: "Hidden content still in the file",
    note: "Export removes these whatever was found, so they should be gone.",
  },
  text: {
    title: "Redacted text found again",
    note:
      "Text you redacted also appears in these places. Mark it if it is the same personal data; " +
      "a common word or an OCR misreading is harmless.",
  },
};

/** The order sections appear in: faults of redaction first, then what the reviewer judges. */
const LEAK_ORDER: LeakKind[] = ["under_box", "leftover", "text"];

/**
 * The leak check's findings as the warning sheet lists them. A redacted text is one row
 * however many places hold it; anything else is a row per place, repeats counted.
 */
export function leakSections(leaks: LeakInfo[]): LeakSection[] {
  return LEAK_ORDER.map((kind) => {
    const ofKind = leaks.filter((leak) => leak.kind === kind);
    const rows = kind === "text" ? textRows(ofKind) : placeRows(ofKind);
    return { kind, ...LEAK_SECTIONS[kind], rows };
  }).filter((section) => section.rows.length > 0);
}

function textRows(leaks: LeakInfo[]): LeakRow[] {
  const byText = new Map<string, LeakInfo[]>();
  for (const leak of leaks) byText.set(leak.text, [...(byText.get(leak.text) ?? []), leak]);
  return [...byText].map(([text, found]) => {
    const pagesOf = (layer: string) =>
      [...new Set(found.filter((leak) => leak.layer === layer && leak.page !== null).map((leak) => leak.page as number))].sort(
        (a, b) => a - b,
      );
    const onPages = pagesOf("page_text");
    const reread = pagesOf("ocr");
    const where = [
      onPages.length > 0 ? pagesLabel(onPages) : null,
      reread.length > 0 ? `${pagesLabel(reread)}, read by OCR` : null,
      found.some((leak) => leak.page === null) ? "in the file's data" : null,
    ].filter((part) => part !== null);
    const pages = [...onPages, ...reread];
    return {
      key: `text:${text}`,
      title: text,
      where: where.join(" · "),
      page: pages.length > 0 ? Math.min(...pages) : null,
      entityId: found.find((leak) => leak.entity_id !== null)?.entity_id ?? null,
    };
  });
}

function placeRows(leaks: LeakInfo[]): LeakRow[] {
  const rows = new Map<string, LeakRow & { count: number }>();
  for (const leak of leaks) {
    const where =
      leak.page === null
        ? `${leakLayerLabel(leak.layer)} · ${leak.where}`
        : `Page ${leak.page} · ${leakLayerLabel(leak.layer)}`;
    const key = `${leak.kind}:${where}:${leak.text}`;
    const row = rows.get(key);
    if (row) row.count += 1;
    else rows.set(key, { key, title: leak.text, where, page: leak.page, entityId: leak.entity_id, count: 1 });
  }
  return [...rows.values()].map(({ count, ...row }) => (count > 1 ? { ...row, title: `${row.title} ×${count}` } : row));
}

/** "Page 3" or "Pages 1, 4 and 9". */
export function pagesLabel(pages: number[]): string {
  const listed = pageList(pages);
  return listed.charAt(0).toUpperCase() + listed.slice(1);
}

/** What an export will do, known before it starts: whether it checks, and the scans OCR re-reads. */
export interface ExportPlan {
  check: boolean;
  scannedPages: number;
}

/** The scanned pages the leak check re-reads: those OCR read when the document opened. */
export function scannedPages(document: DocumentInfo): number {
  return document.pages.filter((page) => page.raster_dpi !== null).length;
}

const CHECK_STEPS: ExportStep[] = ["page_text", "region", "off_page_text", "surface", "thumbnail", "object", "file_bytes"];

/** The stages the export sheet lists, each covering one or more of Python's steps. */
const EXPORT_STAGES: { key: string; label: string; steps: ExportStep[] }[] = [
  { key: "redact", label: "Redacting the pages", steps: ["redacting"] },
  { key: "clear", label: "Removing hidden data", steps: ["clearing"] },
  { key: "save", label: "Writing the copy", steps: ["saving"] },
  { key: "check", label: "Checking the copy for leaks", steps: CHECK_STEPS },
  { key: "reread", label: "Re-reading the scans with OCR", steps: ["ocr"] },
];

const EXPORT_STATUS: Record<ExportStep, string> = {
  redacting: "Removing what you marked from each page",
  clearing: "Removing links, metadata, attachments and other hidden data",
  saving: "Writing the redacted file",
  page_text: "Searching each page's text for what was redacted",
  region: "Checking that nothing is left under drawn regions",
  off_page_text: "Looking for text outside the visible page",
  surface: "Checking that hidden data is gone",
  thumbnail: "Looking for page thumbnails",
  object: "Searching the file's objects for redacted text",
  file_bytes: "Searching the file's raw bytes for redacted text",
  ocr: "Reading the redacted scans again with OCR",
};

/** Python's steps in the order an export runs them. */
function exportSteps(plan: ExportPlan): ExportStep[] {
  return EXPORT_STAGES.filter((stage) => isPlanned(stage.key, plan)).flatMap((stage) => stage.steps);
}

function isPlanned(stage: string, plan: ExportPlan): boolean {
  if (stage === "check") return plan.check;
  if (stage === "reread") return plan.check && plan.scannedPages > 0;
  return true;
}

/** A step's share of the bar: re-reading a scan with OCR takes far longer than anything else. */
function stepWeight(step: ExportStep, plan: ExportPlan): number {
  if (step === "redacting") return 2;
  if (step === "ocr") return 3 * plan.scannedPages;
  return 1;
}

export interface StageState {
  key: string;
  label: string;
  state: "done" | "current" | "pending";
}

/** The export's stages with how far each is; all pending before Python's first step. */
export function exportStages(progress: ExportProgress | null, plan: ExportPlan): StageState[] {
  const stages = EXPORT_STAGES.filter((stage) => isPlanned(stage.key, plan));
  const current = progress ? stages.findIndex((stage) => stage.steps.includes(progress.step)) : -1;
  return stages.map((stage, index) => ({
    key: stage.key,
    label: stage.label,
    state: current === -1 || index > current ? "pending" : index === current ? "current" : "done",
  }));
}

/** The status line and the bar of the whole export, which always counts. */
export function exportStatus(progress: ExportProgress | null, plan: ExportPlan): OpenStatus {
  if (!progress) return { label: "Preparing the export", count: null, fraction: 0 };
  const steps = exportSteps(plan);
  const index = Math.max(steps.indexOf(progress.step), 0);
  const total = steps.reduce((sum, step) => sum + stepWeight(step, plan), 0);
  const before = steps.slice(0, index).reduce((sum, step) => sum + stepWeight(step, plan), 0);
  const within = progress.total > 0 ? Math.min(progress.done / progress.total, 1) : 0;
  return {
    label: EXPORT_STATUS[progress.step],
    count: progress.total > 0 ? `${progress.done} of ${plural(progress.total, "page")}` : null,
    fraction: Math.min((before + within * stepWeight(progress.step, plan)) / total, 1),
  };
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

const OPEN_STATUS: Record<OpenStep, string> = {
  loading_ocr: "Loading the OCR engine",
  reading: "Reading the text layer",
  ocr: "Reading scanned pages with OCR",
  loading_model: "Loading the names model",
  detecting: "Finding personal data",
};

export interface OpenStatus {
  /** What is happening now. */
  label: string;
  /** "3 of 12 pages", or null when the step cannot count (a model loads in one go). */
  count: string | null;
  /** Share done, 0 to 1; null for a step without pages, whose bar runs indeterminately. */
  fraction: number | null;
}

/** The status line and bar while a document opens. */
export function openStatus(progress: OpenProgress): OpenStatus {
  const label = OPEN_STATUS[progress.step];
  if (progress.total === 0) return { label, count: null, fraction: null };
  return {
    label,
    count: `${progress.done} of ${plural(progress.total, "page")}`,
    fraction: Math.min(progress.done / progress.total, 1),
  };
}
