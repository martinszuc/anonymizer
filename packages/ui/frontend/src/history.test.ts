import { describe, expect, it } from "vitest";

import {
  EMPTY_HISTORY,
  HISTORY_LIMIT,
  additionOf,
  afterRedo,
  afterUndo,
  recorded,
  statesBefore,
  type Addition,
  type Edit,
} from "./history";

const keep = (id: string): Edit => ({ kind: "decide", before: { [id]: "pending" }, after: "rejected", label: "Keep" });
const finding: Addition = { kind: "finding", pageIndex: 0, start: 4, end: 9, type: "person" };

describe("undo history", () => {
  it("undoes the last edit first and redoes in the order undone", () => {
    let history = recorded(recorded(EMPTY_HISTORY, keep("a")), keep("b"));
    history = afterUndo(history);
    expect(history.done).toEqual([keep("a")]);
    expect(history.undone).toEqual([keep("b")]);
    history = afterRedo(history);
    expect(history.done).toEqual([keep("a"), keep("b")]);
    expect(history.undone).toEqual([]);
  });

  it("forgets what was undone once a new edit is made", () => {
    const history = recorded(afterUndo(recorded(EMPTY_HISTORY, keep("a"))), keep("b"));
    expect(history).toEqual({ done: [keep("b")], undone: [] });
  });

  it("keeps a bounded number of edits", () => {
    let history = EMPTY_HISTORY;
    for (let index = 0; index <= HISTORY_LIMIT; index += 1) history = recorded(history, keep(`e${index}`));
    expect(history.done).toHaveLength(HISTORY_LIMIT);
    expect(history.done[0]).toEqual(keep("e1"));
  });

  it("does nothing with nothing to undo or redo", () => {
    expect(afterUndo(EMPTY_HISTORY)).toBe(EMPTY_HISTORY);
    expect(afterRedo(EMPTY_HISTORY)).toBe(EMPTY_HISTORY);
  });

  it("follows an item added again under the ids Python gave it, repeats included", () => {
    const added: Edit = { kind: "add", addition: finding, ids: ["f", "r1"], label: "Add" };
    let history = recorded(recorded(EMPTY_HISTORY, added), keep("r1"));
    history = afterUndo(afterUndo(history)); // the decision, then the addition
    history = afterRedo(history, ["f2", "r1b"]); // added again: new ids
    expect(history.done).toEqual([{ ...added, ids: ["f2", "r1b"] }]);
    expect(history.undone).toEqual([keep("r1b")]);
  });

  it("finds how an item was added, under its current id, to undo removing it", () => {
    const added: Edit = { kind: "add", addition: finding, ids: ["f"], label: "Add" };
    const history = afterRedo(afterUndo(recorded(EMPTY_HISTORY, added)), ["f2"]);
    expect(additionOf(history, "f2")).toEqual(finding);
    expect(additionOf(history, "f")).toBeNull();
    expect(additionOf(history, "r1")).toBeNull();
  });

  it("groups a decision's ids by the state each had before", () => {
    const edit: Extract<Edit, { kind: "decide" }> = {
      kind: "decide",
      before: { a: "pending", b: "confirmed", c: "pending" },
      after: "rejected",
      label: "Keep",
    };
    expect(statesBefore(edit)).toEqual(
      new Map([
        ["pending", ["a", "c"]],
        ["confirmed", ["b"]],
      ]),
    );
  });
});
