import { CircleAlert, CircleCheck, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef } from "react";

import { gentle } from "../motion";

export interface Toast {
  id: number;
  kind: "success" | "error";
  message: string;
  /** A button after the message, such as Undo; the toast closes when it is used. */
  action?: { label: string; run: () => void };
}

/** How long a toast stays: longer with something to read or to act on. */
const SHOWN_MS = { plain: 4000, action: 8000, error: 7000 };

export function Toasts({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  return (
    <div className="toasts" role="status" aria-live="polite">
      <AnimatePresence initial={false}>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
}

/** One toast. Its time runs out only while the pointer and the focus are elsewhere. */
function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: number) => void }) {
  const remaining = useRef(toast.action ? SHOWN_MS.action : toast.kind === "error" ? SHOWN_MS.error : SHOWN_MS.plain);
  const timer = useRef<{ handle: number; started: number } | null>(null);

  const run = () => {
    if (timer.current) return;
    timer.current = { handle: window.setTimeout(() => onDismiss(toast.id), remaining.current), started: Date.now() };
  };
  const pause = () => {
    if (!timer.current) return;
    window.clearTimeout(timer.current.handle);
    remaining.current -= Date.now() - timer.current.started;
    timer.current = null;
  };

  useEffect(() => {
    run();
    // Started once per toast; pausing keeps what is left.
    return pause;
  }, []);

  return (
    <motion.div
      layout
      className="toast"
      data-kind={toast.kind}
      initial={{ opacity: 0, y: 16, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.98 }}
      transition={gentle}
      onPointerEnter={pause}
      onPointerLeave={run}
      onFocus={pause}
      onBlur={run}
    >
      {toast.kind === "error" ? <CircleAlert size={16} /> : <CircleCheck size={16} />}
      <span>{toast.message}</span>
      {toast.action && (
        <button
          type="button"
          className="toast-action"
          onClick={() => {
            toast.action?.run();
            onDismiss(toast.id);
          }}
        >
          {toast.action.label}
        </button>
      )}
      <button type="button" className="toast-close" aria-label="Dismiss" onClick={() => onDismiss(toast.id)}>
        <X size={12} />
      </button>
    </motion.div>
  );
}
