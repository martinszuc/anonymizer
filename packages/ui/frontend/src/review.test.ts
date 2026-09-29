import { describe, expect, it } from "vitest";

import {
  covers,
  groupByType,
  isRedacted,
  renderDpi,
  steppedZoom,
  summarize,
  toggled,
} from "./review";
import type { DocumentInfo, EntityInfo } from "./types";

function entity(overrides: Partial<EntityInfo>): EntityInfo {
  return {
    id: "e",
    type: "email",
    source: "rule",
    score: null,
    review: "pending",
    page_index: 0,
    surface_id: null,
    text: "jan.novak@example.com",
    is_region: false,
    boxes: [[72, 100, 200, 112]],
    ...overrides,
  };
}

describe("review states", () => {
  it("redacts everything not rejected", () => {
    expect(isRedacted("pending")).toBe(true);
    expect(isRedacted("confirmed")).toBe(true);
    expect(isRedacted("rejected")).toBe(false);
  });

  it("toggles between keep and an explicit redact", () => {
    expect(toggled("pending")).toBe("rejected");
    expect(toggled("confirmed")).toBe("rejected");
    expect(toggled("rejected")).toBe("confirmed");
  });
});

describe("summarize", () => {
  it("counts redacted, kept and hidden items", () => {
    const document: DocumentInfo = {
      name: "cv.pdf",
      language: "cs",
      pages: [],
      entities: [
        entity({ id: "a" }),
        entity({ id: "b", review: "confirmed" }),
        entity({ id: "c", review: "rejected" }),
      ],
      surfaces: [{ id: "s", kind: "metadata", value: "CV", page_index: null, box: null }],
    };
    expect(summarize(document)).toEqual({ redacted: 2, kept: 1, hidden: 1 });
  });
});

describe("groupByType", () => {
  it("orders groups by type and members by reading order", () => {
    const groups = groupByType([
      entity({ id: "late-email", boxes: [[72, 300, 100, 312]] }),
      entity({ id: "metadata-email", page_index: null, boxes: [] }),
      entity({ id: "name", type: "person" }),
      entity({ id: "early-email", boxes: [[72, 100, 100, 112]] }),
      entity({ id: "page-two-email", page_index: 1, boxes: [[72, 50, 100, 62]] }),
      entity({ id: "custom", type: "zzz_custom" }),
    ]);
    expect(groups.map((group) => group.type)).toEqual(["person", "email", "zzz_custom"]);
    expect(groups[0]?.label).toBe("Names");
    expect(groups[1]?.entities.map((member) => member.id)).toEqual([
      "early-email",
      "late-email",
      "page-two-email",
      "metadata-email",
    ]);
    expect(groups[2]?.label).toBe("zzz_custom");
  });
});

describe("covers", () => {
  it("collapses whitespace from line breaks", () => {
    expect(covers(entity({ text: "Jan\n  Novak" }))).toBe("Jan Novak");
  });

  it("names a drawn region", () => {
    expect(covers(entity({ is_region: true, text: null }))).toBe("Drawn region");
  });
});

describe("renderDpi", () => {
  it("steps up so nearby zooms share one image", () => {
    expect(renderDpi(1, 2)).toBe(144);
    expect(renderDpi(1.01, 2)).toBe(168);
  });

  it("stays within the bounds the Python side accepts", () => {
    expect(renderDpi(0.1, 1)).toBe(72);
    expect(renderDpi(10, 2)).toBe(400);
  });
});

describe("steppedZoom", () => {
  it("moves to the neighbouring step", () => {
    expect(steppedZoom(1, 1)).toBe(1.25);
    expect(steppedZoom(1, -1)).toBe(0.75);
    expect(steppedZoom(0.9, 1)).toBe(1);
  });

  it("stops at the ends", () => {
    expect(steppedZoom(3, 1)).toBe(3);
    expect(steppedZoom(0.5, -1)).toBe(0.5);
  });
});
