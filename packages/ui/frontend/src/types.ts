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
