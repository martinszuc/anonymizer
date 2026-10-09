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
  DEFAULT_VIEW,
  NO_FILTER,
  activeFilters,
  filterFindings,
  findingSections,
  keepable,
  nextUndecided,
  reviewProgress,
  lowConfidence,
  chooseOcrEngine,
  nameModelOptions,
  nameModelReady,
  ocrOptions,
  ocrReady,
  scoreRange,
  sortedBy,
  type ListView,
  openStatus,
  exportStages,
  exportStatus,
  leakSections,
  scannedPages,
  pagesWithoutText,
  regionNumbers,
  renderDpi,
  steppedZoom,
  summarize,
  toggled,
} from "./review";
import type { DocumentInfo, EntityInfo, LeakInfo, ModelState, NamesStatus, OcrStatus } from "./types";

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
      language_recognised: false,
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
      language_recognised: false,
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

describe("review progress", () => {
  const pending = (id: string, top: number) => entity({ id, text: `${id}@example.com`, boxes: [[72, top, 200, top + 12]] });
  const kept = (id: string, top: number) => ({ ...pending(id, top), review: "rejected" as const });
  const hidden = entity({ id: "hidden", surface_id: "s", page_index: 0 });

  it("counts the findings with a choice and those decided", () => {
    const region = drawn("region", [72, 300, 200, 400]);
    expect(reviewProgress([pending("a", 100), kept("b", 200), hidden, region])).toEqual({ decided: 1, total: 2 });
  });

  it("walks the undecided findings in the list's order, wrapping around", () => {
    const sections = findingSections([pending("a", 100), kept("b", 200), pending("c", 300), hidden], DEFAULT_VIEW);
    expect(nextUndecided(sections, null)?.id).toBe("a");
    expect(nextUndecided(sections, "a")?.id).toBe("c");
    expect(nextUndecided(sections, "c")?.id).toBe("a");
    expect(nextUndecided(sections, "b")?.id).toBe("c");
    expect(nextUndecided(sections, "a", -1)?.id).toBe("c");
    expect(nextUndecided(sections, null, -1)?.id).toBe("c");
  });

  it("stops once at a group of repeats", () => {
    const repeat = (id: string, top: number) => entity({ id, text: "Jan Novák", type: "person", boxes: [[72, top, 200, top + 12]] });
    const sections = findingSections([repeat("a", 100), repeat("b", 200), pending("c", 300)], DEFAULT_VIEW);
    expect(nextUndecided(sections, null)?.id).toBe("a");
    expect(nextUndecided(sections, "a")?.id).toBe("c");
    expect(nextUndecided(sections, "b")?.id).toBe("c");
    expect(nextUndecided(sections, "c")?.id).toBe("a");
  });

  it("finds nothing once everything is decided", () => {
    const sections = findingSections([kept("a", 100), hidden], DEFAULT_VIEW);
    expect(nextUndecided(sections, "a")).toBeNull();
    expect(nextUndecided([], null)).toBeNull();
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
    leak_check: "passed" as const,
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
      language_recognised: false,
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

describe("openStatus", () => {
  it("counts pages for a step that goes page by page", () => {
    expect(openStatus({ step: "detecting", done: 3, total: 12 })).toEqual({
      label: "Finding personal data",
      count: "3 of 12 pages",
      fraction: 0.25,
    });
    expect(openStatus({ step: "ocr", done: 1, total: 1 }).count).toBe("1 of 1 page");
  });

  it("leaves the bar indeterminate while a model loads", () => {
    expect(openStatus({ step: "loading_model", done: 0, total: 0 })).toEqual({
      label: "Loading the names model",
      count: null,
      fraction: null,
    });
  });
});

describe("lowConfidence", () => {
  const name = (id: string, text: string, score: number | null, extra: Partial<EntityInfo> = {}) =>
    entity({ id, type: "person", source: "model", score, text, ...extra });
  const ids = (entities: EntityInfo[]) => entities.map((item) => item.id);

  it("takes undecided model findings under the threshold, not rules", () => {
    const found = [name("low", "Kupující", 0.35), name("high", "Jan Novák", 0.92), entity({ id: "rule" })];
    expect(ids(lowConfidence(found, 0.5))).toEqual(["low"]);
    expect(ids(lowConfidence(found, 0.3))).toEqual([]);
  });

  it("takes the repeats of a low finding with it", () => {
    const found = [
      name("model", "Kupující", 0.4),
      name("repeat", "kupující", null, { source: "propagated" }),
      name("other", "Novák", null, { source: "propagated" }),
    ];
    expect(ids(lowConfidence(found, 0.5))).toEqual(["model", "repeat"]);
  });

  it("judges identical findings by their best evidence", () => {
    const scored = [name("weak", "Jan Novák", 0.35), name("strong", "jan  novák", 0.8)];
    expect(lowConfidence(scored, 0.5)).toEqual([]);
    const ruled = [entity({ id: "rule", type: "person", text: "Jan Novák" }), name("weak", "Jan Novák", 0.35)];
    expect(lowConfidence(ruled, 0.5)).toEqual([]);
  });

  it("leaves decided findings and hidden data alone", () => {
    const found = [
      name("kept", "Prodávající", 0.3, { review: "rejected" }),
      name("confirmed", "Spotřebitel", 0.3, { review: "confirmed" }),
      name("hidden", "Kupující", 0.3, { surface_id: "metadata:Title" }),
    ];
    expect(lowConfidence(found, 0.7)).toEqual([]);
  });
});

describe("the findings list", () => {
  // Page 1 top to bottom: Kupující (model 35 %, three times), Jan Novák (model 92 %),
  // an email (rule), Novák (model 55 %, kept); a drawn region on page 2.
  const at = (top: number, page = 0) => ({ page_index: page, boxes: [[72, top, 200, top + 12]] as [number, number, number, number][] });
  const findings: EntityInfo[] = [
    entity({ id: "k1", type: "person", source: "model", score: 0.35, text: "Kupující", ...at(100) }),
    entity({ id: "jan", type: "person", source: "model", score: 0.92, text: "Jan Novák", ...at(120) }),
    entity({ id: "k2", type: "person", source: "propagated", text: "Kupující", ...at(140) }),
    entity({ id: "mail", ...at(160) }),
    entity({ id: "novak", type: "person", source: "model", score: 0.55, text: "Novák", review: "rejected", ...at(180) }),
    entity({ id: "k3", type: "person", source: "propagated", text: "kupující", ...at(200) }),
    entity({ id: "region", type: "region", source: "manual", text: null, is_region: true, review: "confirmed", ...at(50, 1) }),
  ];
  const view = (changes: Partial<ListView>): ListView => ({ ...DEFAULT_VIEW, ...changes });
  const rowIds = (v: ListView) =>
    findingSections(findings, v).flatMap((section) => section.rows.map((row) => row.members.map((m) => m.id).join("+")));

  it("groups by type in reading order by default", () => {
    const sections = findingSections(findings, DEFAULT_VIEW);
    expect(sections.map((section) => section.type)).toEqual(["person", "email", "region"]);
    expect(rowIds(DEFAULT_VIEW)).toEqual(["k1+k2+k3", "jan", "novak", "mail", "region"]);
  });

  it("orders by score either way, unscored rows last", () => {
    const flat = (sort: ListView["sort"]) => sortedBy(DEFAULT_VIEW, sort);
    expect(rowIds(flat("score-asc"))).toEqual(["k1+k2+k3", "novak", "jan", "mail", "region"]);
    expect(rowIds(flat("score-desc"))).toEqual(["jan", "novak", "k1+k2+k3", "mail", "region"]);
  });

  it("orders by repeats, page and text", () => {
    expect(rowIds(sortedBy(DEFAULT_VIEW, "occurrences"))[0]).toBe("k1+k2+k3");
    expect(rowIds(sortedBy(DEFAULT_VIEW, "page"))).toEqual(["k1+k2+k3", "jan", "mail", "novak", "region"]);
    expect(rowIds(sortedBy(DEFAULT_VIEW, "text"))).toEqual(["region", "jan", "mail", "k1+k2+k3", "novak"]);
  });

  it("keeps sections by type for another order when asked", () => {
    const sections = findingSections(findings, view({ sort: "score-desc", byType: true }));
    expect(sections.map((section) => section.type)).toEqual(["person", "email", "region"]);
    expect(sections[0]?.rows.map((row) => row.members[0]?.id)).toEqual(["jan", "novak", "k1"]);
  });

  it("chooses sections with the order", () => {
    expect(sortedBy(DEFAULT_VIEW, "score-asc").byType).toBe(false);
    expect(sortedBy(view({ sort: "page", byType: false }), "type").byType).toBe(true);
  });

  it("filters by decision, source and score", () => {
    const ids = (filter: Partial<typeof NO_FILTER>) => filterFindings(findings, { ...NO_FILTER, ...filter }).map((e) => e.id);
    expect(ids({ decision: "undecided" })).toEqual(["k1", "jan", "k2", "mail", "k3"]);
    expect(ids({ decision: "kept" })).toEqual(["novak"]);
    expect(ids({ decision: "redacted" })).toEqual(["k1", "jan", "k2", "mail", "k3", "region"]);
    expect(ids({ sources: ["rule", "manual"] })).toEqual(["mail", "region"]);
    expect(ids({ scoreBelow: 0.6 })).toEqual(["k1", "k2", "novak", "k3"]);
  });

  it("searches the found text ignoring case and diacritics", () => {
    const ids = (text: string) => filterFindings(findings, { ...NO_FILTER, text }).map((e) => e.id);
    expect(ids("novak")).toEqual(["jan", "mail", "novak"]); // the email holds it too
    expect(ids("  KUPUJICI ")).toEqual(["k1", "k2", "k3"]);
    expect(ids("region 1")).toEqual(["region"]);
  });

  it("keeps only the undecided findings shown", () => {
    const shown = findingSections(findings, view({ filter: { ...NO_FILTER, scoreBelow: 0.6 } }));
    expect(keepable(shown).map((e) => e.id)).toEqual(["k1", "k2", "k3"]);
  });

  it("counts active filters and shows score ranges", () => {
    expect(activeFilters(NO_FILTER)).toBe(0);
    expect(activeFilters({ decision: "kept", sources: ["model"], scoreBelow: 0.5, text: " a " })).toBe(4);
    expect(scoreRange(findings.slice(0, 2))).toBe("35–92 %");
    expect(scoreRange([findings[1] as EntityInfo])).toBe("92 %");
    expect(scoreRange([findings[3] as EntityInfo])).toBeNull();
  });
});

describe("export progress", () => {
  const checked = { check: true, scannedPages: 0 };

  it("lists the stages, each pending until Python's first step", () => {
    expect(exportStages(null, checked).map((stage) => [stage.label, stage.state])).toEqual([
      ["Redacting the pages", "pending"],
      ["Removing hidden data", "pending"],
      ["Writing the copy", "pending"],
      ["Checking the copy for leaks", "pending"],
    ]);
  });

  it("re-reads scans only when the check runs and OCR read some", () => {
    const stages = (plan: { check: boolean; scannedPages: number }) =>
      exportStages(null, plan).map((stage) => stage.key);
    expect(stages({ check: true, scannedPages: 2 })).toContain("reread");
    expect(stages({ check: false, scannedPages: 2 })).toEqual(["redact", "clear", "save"]);
  });

  it("marks the stage a leak layer belongs to as current", () => {
    const progress = { step: "object" as const, done: 0, total: 0 };
    expect(exportStages(progress, checked).map((stage) => stage.state)).toEqual([
      "done",
      "done",
      "done",
      "current",
    ]);
  });

  it("says what runs now and counts pages", () => {
    const status = exportStatus({ step: "redacting", done: 3, total: 12 }, checked);
    expect(status.label).toBe("Removing what you marked from each page");
    expect(status.count).toBe("3 of 12 pages");
  });

  it("fills one bar across the whole export", () => {
    const at = (step: "redacting" | "saving" | "file_bytes", done = 0, total = 0) =>
      exportStatus({ step, done, total }, checked).fraction ?? -1;
    expect(exportStatus(null, checked).fraction).toBe(0);
    expect(at("redacting", 0, 4)).toBe(0);
    expect(at("redacting", 4, 4)).toBeGreaterThan(at("redacting", 2, 4));
    expect(at("saving")).toBeGreaterThan(at("redacting", 4, 4));
    expect(at("file_bytes")).toBeLessThan(1);
  });

  it("gives re-reading scans most of the bar", () => {
    const plan = { check: true, scannedPages: 10 };
    expect(exportStatus({ step: "ocr", done: 0, total: 10 }, plan).fraction).toBeLessThan(0.5);
    expect(exportStatus({ step: "ocr", done: 10, total: 10 }, plan).fraction).toBe(1);
  });

  it("counts the pages OCR read", () => {
    const page = { index: 0, width: 1, height: 1, has_text_layer: false };
    const document = {
      pages: [
        { ...page, raster_dpi: 300 },
        { ...page, index: 1, raster_dpi: null },
      ],
    } as DocumentInfo;
    expect(scannedPages(document)).toBe(1);
  });
});

describe("leakSections", () => {
  const leak = (fields: Partial<LeakInfo>): LeakInfo => ({
    layer: "page_text",
    where: "page 0",
    page: 1,
    text: "Novák",
    entity_id: "e1",
    kind: "text",
    ...fields,
  });

  it("puts faults of redaction before text found again", () => {
    const sections = leakSections([
      leak({}),
      leak({ kind: "leftover", layer: "surface", where: "metadata Author", page: null, text: "Jan", entity_id: null }),
      leak({ kind: "under_box", layer: "region", where: "page 0 region", text: "drawing" }),
    ]);
    expect(sections.map((section) => section.kind)).toEqual(["under_box", "leftover", "text"]);
  });

  it("makes one row of a text however many places hold it", () => {
    const [section] = leakSections([
      leak({ page: 4 }),
      leak({ page: 1 }),
      leak({ layer: "ocr", page: 2 }),
      leak({ layer: "object", where: "object 7", page: null }),
      leak({ layer: "file_bytes", where: "the file's bytes", page: null }),
    ]);
    expect(section?.rows).toEqual([
      {
        key: "text:Novák",
        title: "Novák",
        where: "Pages 1 and 4 · Page 2, read by OCR · in the file's data",
        page: 1,
        entityId: "e1",
      },
    ]);
  });

  it("counts repeats of something left in one place", () => {
    const left = leak({ kind: "under_box", layer: "ocr", where: "page 0 under a box", text: "word 'Adult'" });
    const [section] = leakSections([left, left]);
    expect(section?.rows.map((row) => [row.title, row.where])).toEqual([
      ["word 'Adult' ×2", "Page 1 · Re-read by OCR"],
    ]);
  });

  it("names where hidden content lies when it is on no page", () => {
    const [section] = leakSections([
      leak({ kind: "leftover", layer: "surface", where: "metadata Author", page: null, text: "Jan", entity_id: null }),
    ]);
    expect(section?.rows[0]).toMatchObject({ where: "Hidden data · metadata Author", page: null, entityId: null });
  });
});

describe("choosing the OCR engine", () => {
  function ocr(onnxtr: ModelState, kraken: ModelState): OcrStatus {
    const engine = (name: string, state: ModelState) => ({
      name,
      title: name,
      description: "",
      feature: `ocr-${name}`,
      state,
      missing: [],
      install_command: `uv sync --group ocr-${name}`,
    });
    return { default: "onnxtr", engines: [engine("onnxtr", onnxtr), engine("kraken", kraken)] };
  }
  const start = { use_ocr: true, ocr_engine: "onnxtr" };

  it("starts with the default when it is ready, else with a ready engine", () => {
    expect(ocrOptions(ocr("ready", "ready"), start)).toEqual(start);
    expect(ocrOptions(ocr("files_missing", "ready"), start)).toEqual({ use_ocr: true, ocr_engine: "kraken" });
    expect(ocrOptions(ocr("not_installed", "files_missing"), start)).toEqual({ use_ocr: false, ocr_engine: "onnxtr" });
  });

  it("keeps a ready choice, on or off", () => {
    const kraken = { use_ocr: false, ocr_engine: "kraken" };
    expect(ocrOptions(ocr("ready", "ready"), kraken)).toEqual(kraken);
  });

  it("moves to a ready engine when the chosen one is gone, and turns off when none is left", () => {
    const kraken = { use_ocr: true, ocr_engine: "kraken" };
    expect(ocrOptions(ocr("ready", "files_missing"), kraken)).toEqual({ use_ocr: true, ocr_engine: "onnxtr" });
    expect(ocrOptions(ocr("files_missing", "files_missing"), kraken)).toEqual({ use_ocr: false, ocr_engine: "kraken" });
  });

  it("chooses an engine whose models just arrived and turns OCR on", () => {
    const off = { use_ocr: false, ocr_engine: "onnxtr" };
    expect(ocrOptions(ocr("ready", "ready"), off, "kraken")).toEqual({ use_ocr: true, ocr_engine: "kraken" });
    // Downloaded, but its package is missing: nothing changes.
    expect(ocrOptions(ocr("ready", "not_installed"), off, "kraken")).toEqual(off);
  });

  it("reads readiness per engine and prefers in the order given", () => {
    const status = ocr("files_missing", "ready");
    expect(ocrReady(status, "kraken")).toBe(true);
    expect(ocrReady(status, "onnxtr")).toBe(false);
    expect(ocrReady(status, "tesseract")).toBe(false);
    expect(chooseOcrEngine(status, [null, "onnxtr"])).toBe("kraken");
    expect(chooseOcrEngine(ocr("ready", "ready"), ["kraken"])).toBe("kraken");
  });
});

describe("choosing the name model", () => {
  function names(zeroShot: ModelState, tuned: ModelState): NamesStatus {
    const model = (name: string, state: ModelState) => ({
      name,
      title: name,
      description: "",
      feature: `names-${name}`,
      state,
      missing: [],
      install_command: "uv sync --group ner",
    });
    return { default: "gliner-multi-v2.1", models: [model("gliner-multi-v2.1", zeroShot), model("tuned", tuned)] };
  }
  const start = { use_model: true, name_model: "gliner-multi-v2.1" };

  it("starts with the default when it is ready, else with a ready model, else off", () => {
    expect(nameModelOptions(names("ready", "ready"), start)).toEqual(start);
    expect(nameModelOptions(names("files_missing", "ready"), start)).toEqual({ use_model: true, name_model: "tuned" });
    expect(nameModelOptions(names("not_installed", "files_missing"), start)).toEqual({
      use_model: false,
      name_model: "gliner-multi-v2.1",
    });
  });

  it("keeps a ready choice, on or off, and turns on a model whose files just arrived", () => {
    const tunedOff = { use_model: false, name_model: "tuned" };
    expect(nameModelOptions(names("ready", "ready"), tunedOff)).toEqual(tunedOff);
    const off = { use_model: false, name_model: "gliner-multi-v2.1" };
    expect(nameModelOptions(names("ready", "ready"), off, "tuned")).toEqual({ use_model: true, name_model: "tuned" });
    // A download of an OCR engine names no model: nothing changes.
    expect(nameModelOptions(names("ready", "ready"), off, null)).toEqual(off);
  });

  it("reads readiness per model", () => {
    const status = names("files_missing", "ready");
    expect(nameModelReady(status, "tuned")).toBe(true);
    expect(nameModelReady(status, "gliner-multi-v2.1")).toBe(false);
    expect(nameModelReady(status, "other")).toBe(false);
  });
});
