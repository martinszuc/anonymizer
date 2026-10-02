// Selecting words on a page, as text is selected in a PDF viewer, to add what
// detection missed. Pure, so it is unit-tested.

import type { Box, WordInfo } from "./types";

/** How far from a word's box, in points, a drag may start and still start on the word. */
export const WORD_SLOP = 2;

/** A point on a page, in points. */
export type Point = [number, number];

/** Index of the word under a point, allowing `slop` points around its box; -1 if none. */
export function wordAt(words: WordInfo[], [x, y]: Point, slop = WORD_SLOP): number {
  return words.findIndex(
    ({ box: [x0, y0, x1, y1] }) => x >= x0 - slop && x <= x1 + slop && y >= y0 - slop && y <= y1 + slop,
  );
}

/**
 * Index of the word nearest a point, for where a drag has got to; -1 without words.
 * Lines count more than columns, so a pointer just below a line's end picks the end of
 * that line rather than a word straight below on the next.
 */
export function nearestWord(words: WordInfo[], [x, y]: Point): number {
  let best = -1;
  let bestDistance = Number.POSITIVE_INFINITY;
  words.forEach(({ box: [x0, y0, x1, y1] }, index) => {
    const dx = Math.max(x0 - x, 0, x - x1);
    const dy = Math.max(y0 - y, 0, y - y1);
    const distance = dx + 4 * dy;
    if (distance < bestDistance) {
      best = index;
      bestDistance = distance;
    }
  });
  return best;
}

/** The words between two indices in reading order, both included, whichever comes first. */
export function wordRange(words: WordInfo[], from: number, to: number): WordInfo[] {
  if (from < 0 || to < 0) return [];
  return words.slice(Math.min(from, to), Math.max(from, to) + 1);
}

/** The selection's span in the page text: its first word's start to its last word's end. */
export function selectionSpan(words: WordInfo[]): [number, number] | null {
  const first = words[0];
  const last = words[words.length - 1];
  return first && last ? [first.start, last.end] : null;
}

/** The selected words as one line, as the popover quotes them. */
export function selectionText(words: WordInfo[]): string {
  return words.map((word) => word.text).join(" ");
}

/**
 * One highlight box per line of a selection: the boxes of neighbouring words on a line
 * joined, so the spaces between them are highlighted too, as in any text selection.
 */
export function lineBoxes(words: WordInfo[]): Box[] {
  const lines: Box[] = [];
  for (const { box } of words) {
    const line = lines[lines.length - 1];
    if (line && sameLine(line, box) && box[0] >= line[0]) {
      lines[lines.length - 1] = [line[0], Math.min(line[1], box[1]), Math.max(line[2], box[2]), Math.max(line[3], box[3])];
    } else {
      lines.push([...box]);
    }
  }
  return lines;
}

/** Whether two boxes share at least half the height of the shorter one. */
function sameLine(a: Box, b: Box): boolean {
  const overlap = Math.min(a[3], b[3]) - Math.max(a[1], b[1]);
  return overlap >= Math.min(a[3] - a[1], b[3] - b[1]) / 2;
}

/** What a reviewer can add, in the order the popover offers it (keys 1 to 6). */
export const ADDABLE_TYPES: { type: string; label: string }[] = [
  { type: "person", label: "Name" },
  { type: "address", label: "Address" },
  { type: "email", label: "Email" },
  { type: "phone", label: "Phone" },
  { type: "id_number", label: "ID number" },
  { type: "other", label: "Other" },
];

/**
 * A first guess at what selected text is, so the usual case takes one key: an `@` makes
 * an email; digits alone an ID number, or a phone number when it starts with `+`;
 * letters with digits an address; letters alone a name.
 */
export function guessedType(text: string): string {
  const trimmed = text.trim();
  if (trimmed.includes("@")) return "email";
  const digits = (trimmed.match(/\d/g) ?? []).length;
  const letters = (trimmed.match(/\p{L}/gu) ?? []).length;
  if (digits > 0 && letters === 0) return trimmed.startsWith("+") ? "phone" : "id_number";
  if (digits > 0) return "address";
  return "person";
}
