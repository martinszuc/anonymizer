import { CircleAlert, CircleCheck } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";

import { gentle } from "../motion";

export interface Toast {
  id: number;
  kind: "success" | "error";
  message: string;
}

export function Toasts({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="toasts" role="status" aria-live="polite">
      <AnimatePresence initial={false}>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            layout
            className="toast"
            data-kind={toast.kind}
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={gentle}
          >
            {toast.kind === "error" ? <CircleAlert size={16} /> : <CircleCheck size={16} />}
            <span>{toast.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
