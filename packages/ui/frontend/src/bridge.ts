// The Python side, reached through pywebview's `window.pywebview.api`.

import type {
  AppStatus,
  DocumentInfo,
  EntityInfo,
  ExportResult,
  FeatureModels,
  OpenOptions,
  ReviewState,
} from "./types";

/** The methods of `anonymizer.ui.app.WindowApi`; every call returns a promise. */
export interface ReviewBridge {
  status(): Promise<AppStatus>;
  /** Each feature's models and whether they are stored. */
  models(): Promise<FeatureModels[]>;
  /** Downloads a feature's models from their official sources, verified; progress as events. */
  download_models(feature: string): Promise<FeatureModels[]>;
  current_document(): Promise<DocumentInfo | null>;
  /** Null when the reviewer cancelled the open dialog. */
  choose_pdf(options: OpenOptions): Promise<DocumentInfo | null>;
  /** Opens the PDF last dropped on the window (see `DROPPED`); null if there is none. */
  open_dropped(options: OpenOptions): Promise<DocumentInfo | null>;
  close_document(): Promise<void>;
  choose_session(): Promise<DocumentInfo | null>;
  save_session_as(): Promise<boolean>;
  /** Null when the reviewer cancelled the save dialog. */
  export_as(allowPagesWithoutText: boolean): Promise<ExportResult | null>;
  page_image(index: number, dpi: number): Promise<string>;
  set_review(entityId: string, state: ReviewState): Promise<EntityInfo>;
  /** A drawn rectangle in page points; Python clips it to the page. */
  add_region(pageIndex: number, x0: number, y0: number, x1: number, y1: number): Promise<EntityInfo>;
  /** Only for items the reviewer added; a detected one is rejected instead. */
  remove_entity(entityId: string): Promise<void>;
}

declare global {
  interface Window {
    pywebview?: { api: ReviewBridge };
  }
}

/** How long a plain browser waits for pywebview before using the demo document. */
const DEMO_FALLBACK_MS = 600;

/**
 * Resolve once pywebview has injected the API. Under `npm run dev` in a plain
 * browser, where it never arrives, a synthetic demo document stands in.
 */
export function connect(): Promise<ReviewBridge> {
  return new Promise((resolve) => {
    const ready = () => window.pywebview && resolve(window.pywebview.api);
    if (window.pywebview?.api?.current_document) {
      ready();
      return;
    }
    window.addEventListener("pywebviewready", ready, { once: true });
    if (import.meta.env.DEV) {
      setTimeout(async () => {
        if (!window.pywebview) resolve((await import("./demo")).demoBridge());
      }, DEMO_FALLBACK_MS);
    }
  });
}

/** The message of an error raised in Python, or of any other failure. */
export function errorMessage(error: unknown): string {
  if (error && typeof error === "object" && "message" in error) {
    return String((error as { message: unknown }).message);
  }
  return String(error);
}
