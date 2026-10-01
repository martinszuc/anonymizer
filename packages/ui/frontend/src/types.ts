// The data `anonymizer.ui.api.ReviewApi` returns; keep in step with its payloads.

export type ReviewState = "pending" | "confirmed" | "rejected";

export type DetectionSource = "rule" | "model" | "manual" | "propagated";

/** `[x0, y0, x1, y1]` in PDF points, origin top-left, y downward. */
export type Box = [number, number, number, number];

export interface PageInfo {
  index: number;
  width: number;
  height: number;
  has_text_layer: boolean;
  /** Resolution OCR read the page at; null when OCR did not read it. */
  raster_dpi: number | null;
}

export interface EntityInfo {
  id: string;
  type: string;
  source: DetectionSource;
  score: number | null;
  review: ReviewState;
  page_index: number | null;
  surface_id: string | null;
  text: string | null;
  is_region: boolean;
  boxes: Box[];
}

export interface SurfaceInfo {
  id: string;
  kind: string;
  value: string;
  page_index: number | null;
  box: Box | null;
}

export interface DocumentInfo {
  name: string;
  language: string | null;
  pages: PageInfo[];
  entities: EntityInfo[];
  surfaces: SurfaceInfo[];
}

export interface LeakInfo {
  layer: string;
  where: string;
  text: string;
}

/** What `ReviewApi.export` did; nothing was written unless `written`. */
export interface ExportResult {
  written: boolean;
  name: string;
  redacted: number;
  regions: number;
  kept: number;
  not_reviewed: number;
  hidden_removed: number;
  /** 1-based numbers of scanned pages left unredacted because OCR did not read them. */
  pages_without_text: number[];
  leaks: LeakInfo[];
}

export type ModelState = "ready" | "not_installed" | "files_missing";

/** What `ReviewApi.status` says about the installation, for the home screen. */
export interface AppStatus {
  version: string;
  languages: { code: string; name: string }[];
  model: { state: ModelState; missing: string[] };
  ocr: { engine: string; state: ModelState; missing: string[] };
}

/** How a PDF is opened; each is a detection option (see `ReviewApi.open_pdf`). */
export interface OpenOptions {
  /** Null runs every language's rules. */
  language: string | null;
  propagate: boolean;
  use_model: boolean;
  /** Read scanned pages with the OCR engine. */
  use_ocr: boolean;
}

/** A step of opening a PDF, told by Python as it starts. */
export type OpenStep = "loading_ocr" | "reading" | "loading_model" | "detecting";
