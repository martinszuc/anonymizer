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

/** A word of a page's text (`ReviewApi.page_words`); offsets are into the page text. */
export interface WordInfo {
  start: number;
  end: number;
  text: string;
  box: Box;
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
  /** What detection ran with; null when every language's rules ran. */
  language: string | null;
  /** Whether the language was recognised from the text rather than chosen. */
  language_recognised: boolean;
  pages: PageInfo[];
  entities: EntityInfo[];
  surfaces: SurfaceInfo[];
}

export interface LeakInfo {
  layer: string;
  where: string;
  /** 1-based page the leak lies on; null outside the pages (hidden data, objects, file bytes). */
  page: number | null;
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
  /** Where models are stored and looked for; the reviewer can choose another folder. */
  models_folder: string;
  model: { state: ModelState; missing: string[] };
  ocr: { engine: string; state: ModelState; missing: string[] };
}

/** How a PDF is opened; each is a detection option (see `ReviewApi.open_pdf`). */
export interface OpenOptions {
  /** A language code, "auto" to recognise it from the text, or null for every language's rules. */
  language: string | null;
  propagate: boolean;
  use_model: boolean;
  /** Read scanned pages with the OCR engine. */
  use_ocr: boolean;
}

/** Which of a model's files are on disk (checked by existence, not hashed). */
export type ModelFiles = "present" | "partial" | "absent";

/** A model the window can download (`ReviewApi.models`). */
export interface ModelInfo {
  id: string;
  name: string;
  uses: string[];
  licence: string;
  languages: string[];
  /** The official page the files come from. */
  source: string;
  version: string;
  /** Bytes. */
  size: number;
  state: ModelFiles;
}

/** A feature whose models can be downloaded, with what it still needs. */
export interface FeatureModels {
  /** The name `download_models` takes. */
  feature: string;
  title: string;
  /** Whether its Python package is installed; the window cannot install it. */
  installed: boolean;
  install_command: string;
  /** Bytes still to download; 0 when every model is stored. */
  missing_bytes: number;
  /** Requirements first. */
  models: ModelInfo[];
}

/** How far a download is, told by Python as it goes. */
export interface DownloadProgress {
  feature: string;
  received: number;
  total: number;
}

/** A step of opening a PDF, told by Python as it starts. */
export type OpenStep = "loading_ocr" | "reading" | "ocr" | "loading_model" | "detecting";

/** How far opening a PDF is, told by Python as it goes. */
export interface OpenProgress {
  step: OpenStep;
  /** Pages done so far, of `total`; both 0 for a step that has no pages (loading a model). */
  done: number;
  total: number;
}
