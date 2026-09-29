import { FileLock2 } from "lucide-react";
import { motion } from "motion/react";

import { gentle } from "../motion";
import { shortcut } from "../platform";
import { Button } from "./Button";

interface EmptyStateProps {
  busy: boolean;
  onOpen: () => void;
  onOpenReview: () => void;
}

export function EmptyState({ busy, onOpen, onOpenReview }: EmptyStateProps) {
  return (
    <motion.main
      className="empty"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={gentle}
    >
      <div className="empty-icon" aria-hidden>
        <FileLock2 size={40} strokeWidth={1.5} />
      </div>
      <h1>Review a document</h1>
      <p>
        Open a PDF to see what would be redacted, keep what should stay, and save your decisions.
        Nothing leaves this computer.
      </p>
      <div className="empty-actions">
        <Button variant="primary" disabled={busy} onClick={onOpen}>
          {busy ? "Opening…" : "Open PDF…"}
        </Button>
        <Button disabled={busy} onClick={onOpenReview}>
          Open Review…
        </Button>
      </div>
      <p className="empty-hint">
        <kbd>{shortcut("O")}</kbd> open a PDF · <kbd>{shortcut("O", { shift: true })}</kbd> open a
        saved review
      </p>
    </motion.main>
  );
}
