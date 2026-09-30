import { AnimatePresence, motion } from "motion/react";
import { useEffect, useId, useRef, type ReactNode } from "react";

import { gentle } from "../motion";

interface SheetProps {
  open: boolean;
  title: string;
  icon?: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger";
  children: ReactNode;
  actions: ReactNode;
  onClose: () => void;
}

/**
 * A modal sheet that drops from under the toolbar, as macOS sheets do. Escape
 * closes it. On open, focus goes to the action marked `data-default`, or the
 * last one; mark Cancel when the other choice carries a risk.
 */
export function Sheet({ open, title, icon, tone = "neutral", children, actions, onClose }: SheetProps) {
  const titleId = useId();
  const actionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const actions = actionsRef.current;
    const buttons = actions?.querySelectorAll("button");
    const preferred = actions?.querySelector<HTMLButtonElement>("button[data-default]");
    (preferred ?? buttons?.[buttons.length - 1])?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="sheet-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
        >
          <motion.section
            className="sheet"
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            data-tone={tone}
            initial={{ y: -24, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: -16, opacity: 0, transition: { duration: 0.14 } }}
            transition={gentle}
          >
            {icon && <div className="sheet-icon">{icon}</div>}
            <h2 id={titleId} className="sheet-title">
              {title}
            </h2>
            <div className="sheet-body">{children}</div>
            <div ref={actionsRef} className="sheet-actions">
              {actions}
            </div>
          </motion.section>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
