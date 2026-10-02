import { Plus } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useRef, useState, type KeyboardEvent } from "react";

import { gentle } from "../motion";
import { ADDABLE_TYPES, guessedType, lineBoxes, selectionText } from "../selection";
import type { WordInfo } from "../types";
import { Button } from "./Button";

const GAP = 8;
const WIDTH = 304;
const HEIGHT = 132;

interface AddFindingPopoverProps {
  words: WordInfo[];
  adding: boolean;
  scale: number;
  /** The page's size on screen, to keep the popover on it. */
  pageWidth: number;
  pageHeight: number;
  onAdd: (type: string) => void;
  onCancel: () => void;
}

/**
 * Asks what the selected words are and adds them as a finding. Keys: 1–6 or the arrows
 * choose the type, Return adds, Escape cancels.
 */
export function AddFindingPopover({ words, adding, scale, pageWidth, pageHeight, onAdd, onCancel }: AddFindingPopoverProps) {
  const text = selectionText(words);
  const [type, setType] = useState(() => guessedType(text));
  const addRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    addRef.current?.focus({ preventScroll: true });
  }, []);

  const lines = lineBoxes(words);
  const left = Math.min(Math.min(...lines.map((box) => box[0])) * scale, Math.max(pageWidth - WIDTH, 0));
  const bottom = Math.max(...lines.map((box) => box[3])) * scale;
  const top = Math.min(...lines.map((box) => box[1])) * scale;
  // Below the selection, or above it when the page ends first.
  const below = bottom + GAP + HEIGHT < pageHeight;

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const index = ADDABLE_TYPES.findIndex((item) => item.type === type);
    const number = Number(event.key);
    if (Number.isInteger(number) && number >= 1 && number <= ADDABLE_TYPES.length) {
      setType(ADDABLE_TYPES[number - 1]?.type ?? type);
    } else if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      setType(ADDABLE_TYPES[(index + 1) % ADDABLE_TYPES.length]?.type ?? type);
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      setType(ADDABLE_TYPES[(index - 1 + ADDABLE_TYPES.length) % ADDABLE_TYPES.length]?.type ?? type);
    } else if (event.key === "Enter") {
      if (!adding) onAdd(type);
    } else if (event.key === "Escape") {
      onCancel();
    } else {
      return;
    }
    // The window's own shortcuts (Escape, arrows in the list) must not act as well.
    event.preventDefault();
    event.stopPropagation();
  };

  return (
    <motion.div
      className="add-popover"
      role="dialog"
      aria-label="Add as a finding"
      style={below ? { left, top: bottom + GAP } : { left, bottom: pageHeight - top + GAP }}
      initial={{ opacity: 0, y: below ? -4 : 4, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.1 } }}
      transition={gentle}
      onKeyDown={onKeyDown}
      onPointerDown={(event) => event.stopPropagation()}
    >
      <span className="add-popover-text" title={text}>
        {text}
      </span>
      <div className="type-picker" role="radiogroup" aria-label="What it is">
        {ADDABLE_TYPES.map((item, index) => (
          <button
            key={item.type}
            type="button"
            role="radio"
            className="type-option"
            data-type={item.type}
            aria-checked={item.type === type}
            title={`${item.label} (${index + 1})`}
            tabIndex={-1}
            onClick={() => setType(item.type)}
          >
            <span className="dot" aria-hidden />
            {item.label}
          </button>
        ))}
      </div>
      <div className="add-popover-actions">
        <span className="add-popover-hint">
          <kbd>1</kbd>–<kbd>{ADDABLE_TYPES.length}</kbd> type · <kbd>↩</kbd> add
        </span>
        <Button variant="plain" onClick={onCancel}>
          Cancel
        </Button>
        <Button ref={addRef} variant="primary" icon={<Plus size={14} />} disabled={adding} onClick={() => onAdd(type)}>
          {adding ? "Adding…" : "Add"}
        </Button>
      </div>
    </motion.div>
  );
}
