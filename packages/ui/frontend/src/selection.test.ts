import { describe, expect, it } from "vitest";

import {
  guessedType,
  lineBoxes,
  nearestWord,
  selectionSpan,
  selectionText,
  wordAt,
  wordRange,
} from "./selection";
import type { WordInfo } from "./types";

// "Name: Jan Novák" on one line, "Street 12" on the next.
const WORDS: WordInfo[] = [
  { start: 0, end: 5, text: "Name:", box: [72, 100, 102, 112] },
  { start: 6, end: 9, text: "Jan", box: [106, 100, 124, 112] },
  { start: 10, end: 15, text: "Novák", box: [128, 100, 160, 112] },
  { start: 16, end: 22, text: "Street", box: [72, 118, 106, 130] },
  { start: 23, end: 25, text: "12", box: [110, 118, 122, 130] },
];

describe("wordAt", () => {
  it("finds the word under the point", () => {
    expect(wordAt(WORDS, [110, 106])).toBe(1);
  });

  it("allows a little room around a word", () => {
    expect(wordAt(WORDS, [125, 106])).toBe(1);
  });

  it("finds nothing in the margin", () => {
    expect(wordAt(WORDS, [300, 106])).toBe(-1);
    expect(wordAt([], [110, 106])).toBe(-1);
  });
});

describe("nearestWord", () => {
  it("picks the end of the line beside the pointer", () => {
    expect(nearestWord(WORDS, [300, 106])).toBe(2);
  });

  it("prefers the line the pointer is on over a word straight below", () => {
    expect(nearestWord(WORDS, [115, 113])).toBe(1);
  });

  it("finds nothing without words", () => {
    expect(nearestWord([], [0, 0])).toBe(-1);
  });
});

describe("wordRange", () => {
  it("covers both ends in reading order, dragged either way", () => {
    expect(wordRange(WORDS, 1, 3).map((word) => word.text)).toEqual(["Jan", "Novák", "Street"]);
    expect(wordRange(WORDS, 3, 1).map((word) => word.text)).toEqual(["Jan", "Novák", "Street"]);
  });

  it("is empty when an end is missing", () => {
    expect(wordRange(WORDS, -1, 2)).toEqual([]);
  });
});

describe("selectionSpan and selectionText", () => {
  it("spans from the first word's start to the last word's end", () => {
    const selected = wordRange(WORDS, 1, 2);
    expect(selectionSpan(selected)).toEqual([6, 15]);
    expect(selectionText(selected)).toBe("Jan Novák");
  });

  it("has no span without words", () => {
    expect(selectionSpan([])).toBeNull();
  });
});

describe("lineBoxes", () => {
  it("joins words on a line and starts a box per line", () => {
    expect(lineBoxes(wordRange(WORDS, 1, 4))).toEqual([
      [106, 100, 160, 112],
      [72, 118, 122, 130],
    ]);
  });
});

describe("guessedType", () => {
  it.each([
    ["jan.novak@example.com", "email"],
    ["+420 603 123 456", "phone"],
    ["900101/0009", "id_number"],
    ["Dlouhá 12", "address"],
    ["Jan Novák", "person"],
  ])("guesses %s as %s", (text, type) => {
    expect(guessedType(text)).toBe(type);
  });
});
