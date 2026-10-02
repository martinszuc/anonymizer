import { describe, expect, it } from "vitest";

import {
  covers,
  dragBox,
  exportSummary,
  groupByType,
  groupDecision,
  groupOccurrences,
  groupToggled,
  isDecidable,
  isLargeEnough,
  isRedacted,
  isRemoved,
  leakLayerLabel,
  pageList,
  formatBytes,
  isUnreadScan,
  lastDrawnRegion,
  pagesWithoutText,
  regionNumbers,
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

  it("counts a rejected finding in hidden data as removed", () => {
    const document: DocumentInfo = {
      name: "cv.pdf",
      language: "cs",
      pages: [],
      entities: [entity({ id: "link", surface_id: "link:0:7/uri", review: "rejected" })],
      surfaces: [],
    };
    expect(summarize(document)).toEqual({ redacted: 1, kept: 0, hidden: 0 });
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
    expect(covers(entity({ is_region: true, text: null }), 3)).toBe("Region 3");
  });
});

function drawn(id: string, box: [number, number, number, number]): EntityInfo {
  return entity({ id, type: "region", source: "manual", is_region: true, text: null, boxes: [box] });
}

describe("region numbers", () => {
  // Drawn bottom first, then top: numbers follow the drawing, not the page.
  const lower = drawn("lower", [72, 500, 200, 600]);
  const upper = drawn("upper", [72, 100, 200, 200]);
  const email = entity({ id: "email" });

  it("counts regions in the order they were drawn, skipping other findings", () => {
    const numbers = regionNumbers([lower, email, upper]);
    expect([...numbers.entries()]).toEqual([
      ["lower", 1],
      ["upper", 2],
    ]);
  });

  it("closes the gap when a region is removed", () => {
    const third = drawn("third", [72, 300, 200, 400]);
    expect(regionNumbers([lower, third]).get("third")).toBe(2);
  });

  it("lists regions in drawing order, other findings in reading order", () => {
    const later = entity({ id: "later", boxes: [[72, 700, 200, 712]] });
    const groups = groupByType([later, lower, email, upper]);
    expect(groups.map((group) => group.entities.map((item) => item.id))).toEqual([
      ["email", "later"],
      ["lower", "upper"],
    ]);
  });
});

describe("lastDrawnRegion", () => {
  const first = drawn("first", [72, 100, 200, 200]);
  const second = drawn("second", [72, 300, 200, 400]);

  it("finds the region drawn last", () => {
    expect(lastDrawnRegion(["first", "second"], [first, second])?.id).toBe("second");
  });

  it("skips regions already removed", () => {
    expect(lastDrawnRegion(["first", "second"], [first])?.id).toBe("first");
  });

  it("finds nothing when no drawn region is left", () => {
    expect(lastDrawnRegion(["first"], [entity({ id: "first" })])).toBeNull();
    expect(lastDrawnRegion([], [first])).toBeNull();
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

describe("export helpers", () => {
  const result = {
    written: true,
    name: "cv-redacted.pdf",
    redacted: 12,
    regions: 0,
    kept: 1,
    not_reviewed: 3,
    hidden_removed: 6,
    pages_without_text: [],
    leaks: [],
  };

  it("lists pages in words", () => {
    expect(pageList([3])).toBe("page 3");
    expect(pageList([2, 5])).toBe("pages 2 and 5");
    expect(pageList([1, 2, 4])).toBe("pages 1, 2 and 4");
  });

  it("finds scans OCR has not read, numbered from one", () => {
    const document: DocumentInfo = {
      name: "scan.pdf",
      language: null,
      pages: [
        { index: 0, width: 595, height: 842, has_text_layer: true, raster_dpi: null },
        { index: 1, width: 595, height: 842, has_text_layer: false, raster_dpi: null },
        { index: 2, width: 595, height: 842, has_text_layer: false, raster_dpi: 300 },
      ],
      entities: [],
      surfaces: [],
    };
    expect(pagesWithoutText(document)).toEqual([2]);
    expect(document.pages.map(isUnreadScan)).toEqual([false, true, false]);
  });

  it("formats sizes in decimal units", () => {
    expect(formatBytes(980)).toBe("980 B");
    expect(formatBytes(42_342_927)).toBe("42.3 MB");
    expect(formatBytes(1_155_830_112)).toBe("1.16 GB");
    expect(formatBytes(4_819_576)).toBe("4.82 MB");
  });

  it("summarizes what was exported", () => {
    expect(exportSummary(result)).toEqual([
      { label: "Redacted", value: "12 items, 3 not reviewed" },
      { label: "Kept", value: "1 item" },
      { label: "Hidden data removed", value: "6 items" },
    ]);
  });

  it("mentions regions only when there are some", () => {
    const labels = exportSummary({ ...result, regions: 1, not_reviewed: 0 }).map((line) => line.value);
    expect(labels).toEqual(["12 items", "1 region", "1 item", "6 items"]);
  });

  it("names leak layers", () => {
    expect(leakLayerLabel("surface")).toBe("Hidden data");
    expect(leakLayerLabel("new_layer")).toBe("new_layer");
  });
});

describe("drawing a region", () => {
  const page = { width: 595, height: 842 };

  it("normalises a drag in any direction", () => {
    expect(dragBox([300, 200], [100, 120], page)).toEqual([100, 120, 300, 200]);
  });

  it("clamps to the page", () => {
    expect(dragBox([-40, -10], [700, 900], page)).toEqual([0, 0, 595, 842]);
  });

  it("treats a tiny drag as a click", () => {
    expect(isLargeEnough([100, 100, 102, 150], 1)).toBe(false);
    expect(isLargeEnough([100, 100, 102, 150], 4)).toBe(true);
    expect(isLargeEnough([100, 100, 160, 150], 1)).toBe(true);
  });
});

describe("what the reviewer decides", () => {
  it("removes hidden data whatever its review says", () => {
    expect(isRemoved(entity({ surface_id: "link:0:7/uri", review: "rejected" }))).toBe(true);
    expect(isRemoved(entity({ review: "rejected" }))).toBe(false);
    expect(isRemoved(entity({ review: "pending" }))).toBe(true);
  });

  it("lets the reviewer decide only on page text", () => {
    expect(isDecidable(entity({}))).toBe(true);
    expect(isDecidable(entity({ surface_id: "link:0:7/uri" }))).toBe(false);
    expect(isDecidable(entity({ type: "region", is_region: true, text: null }))).toBe(false);
  });
});

describe("groupOccurrences", () => {
  const name = (id: string, text: string, overrides: Partial<EntityInfo> = {}) =>
    entity({ id, type: "person", text, ...overrides });

  it("puts identical findings together, ignoring case and spacing", () => {
    const groups = groupOccurrences([
      name("a", "Jan Novák"),
      name("b", "Petr"),
      name("c", "JAN  novák"),
      name("d", "Jan\nNovák", { source: "propagated" }),
    ]);
    expect(groups.map((group) => group.members.map((member) => member.id))).toEqual([
      ["a", "c", "d"],
      ["b"],
    ]);
  });

  it("keeps hidden-data findings and regions apart from what can be decided", () => {
    const hidden = name("h", "Jan Novák", { surface_id: "s1", page_index: null });
    const region = (id: string) => entity({ id, type: "region", is_region: true, text: null });
    const groups = groupOccurrences([name("a", "Jan Novák"), hidden, region("r1"), region("r2")]);
    expect(groups.map((group) => group.members.map((member) => member.id))).toEqual([
      ["a"],
      ["h"],
      ["r1"],
      ["r2"],
    ]);
  });

  it("says what export does with a group and what its switch does", () => {
    const redacted = name("a", "Jan");
    const kept = name("b", "Jan", { review: "rejected" });
    expect(groupDecision([redacted, { ...redacted, id: "c" }])).toBe("redacted");
    expect(groupDecision([kept])).toBe("kept");
    expect(groupDecision([redacted, kept])).toBe("mixed");
    expect(groupToggled([redacted])).toBe("rejected");
    // A mixed group redacts everything: the safe direction.
    expect(groupToggled([redacted, kept])).toBe("confirmed");
    expect(groupToggled([kept])).toBe("confirmed");
  });
});
