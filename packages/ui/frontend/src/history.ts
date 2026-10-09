// Undo and redo of the reviewer's edits. Pure: App carries each step out through the bridge
// and reports back the ids Python gave to anything added again.

import type { Box, ReviewState } from "./types";

/** Something the reviewer added, with enough to add it again. */
export type Addition =
  | { kind: "finding"; pageIndex: number; start: number; end: number; type: string }
  | { kind: "region"; pageIndex: number; box: Box };

export type Edit =
  /** Decisions: each entity's state before, and the one state they all got. */
  | { kind: "decide"; before: Record<string, ReviewState>; after: ReviewState; label: string }
  /** Added: the item's id first, then its repeats, in the order Python returned them. */
  | { kind: "add"; addition: Addition; ids: string[]; label: string }
  /** Removed an item the reviewer added; undo adds it again. */
  | { kind: "remove"; addition: Addition; ids: string[]; label: string };

export interface History {
  /** Oldest first; the last is undone next. */
  done: Edit[];
  /** Most recently undone last; it is redone next. */
  undone: Edit[];
}

export const EMPTY_HISTORY: History = { done: [], undone: [] };

/** Edits kept; older ones drop off, as they would in any editor. */
export const HISTORY_LIMIT = 200;

/** The history after a new edit: it can be undone, and nothing undone can be redone any more. */
export function recorded(history: History, edit: Edit): History {
  return { done: [...history.done, edit].slice(-HISTORY_LIMIT), undone: [] };
}

/** What a step re-added got from Python: the new ids, in the order of the old ones. */
export type Renamed = string[] | null;

/** The history once its last edit is undone; `renamed` holds the ids of anything added back. */
export function afterUndo(history: History, renamed: Renamed = null): History {
  const edit = history.done.at(-1);
  if (!edit) return history;
  const moved = { done: history.done.slice(0, -1), undone: [...history.undone, edit] };
  return renamed ? withIds(moved, addedIds(edit), renamed) : moved;
}

/** The history once its last undone edit is redone; `renamed` holds the ids of anything added again. */
export function afterRedo(history: History, renamed: Renamed = null): History {
  const edit = history.undone.at(-1);
  if (!edit) return history;
  const moved = { done: [...history.done, edit], undone: history.undone.slice(0, -1) };
  return renamed ? withIds(moved, addedIds(edit), renamed) : moved;
}

/**
 * Every edit with old ids replaced by new ones, position by position. An item added again
 * gets new ids from Python, and later edits must reach it under them.
 */
export function withIds(history: History, old: string[], renamed: string[]): History {
  const names = new Map(old.map((id, index) => [id, renamed[index] ?? id]));
  if (names.size === 0) return history;
  const rename = (id: string) => names.get(id) ?? id;
  const edit = (item: Edit): Edit =>
    item.kind === "decide"
      ? { ...item, before: Object.fromEntries(Object.entries(item.before).map(([id, state]) => [rename(id), state])) }
      : { ...item, ids: item.ids.map(rename) };
  return { done: history.done.map(edit), undone: history.undone.map(edit) };
}

function addedIds(edit: Edit): string[] {
  return edit.kind === "decide" ? [] : edit.ids;
}

/** How the item with an id was added, if this history added it; needed to undo its removal. */
export function additionOf(history: History, id: string): Addition | null {
  for (const edit of [...history.done, ...history.undone].reverse()) {
    if (edit.kind !== "decide" && edit.ids[0] === id) return edit.addition;
  }
  return null;
}

/** The ids of a decision, grouped by the state each had before, to set them back in few calls. */
export function statesBefore(edit: Extract<Edit, { kind: "decide" }>): Map<ReviewState, string[]> {
  const groups = new Map<ReviewState, string[]>();
  for (const [id, state] of Object.entries(edit.before)) groups.set(state, [...(groups.get(state) ?? []), id]);
  return groups;
}
