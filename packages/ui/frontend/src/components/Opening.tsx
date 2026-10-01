import { Check, Circle, LoaderCircle } from "lucide-react";
import { motion } from "motion/react";

import { gentle } from "../motion";
import type { OpenStep } from "../types";

interface OpeningProps {
  /** The dropped file's name; unknown when it came from the open dialog. */
  name: string | null;
  step: OpenStep;
  usesModel: boolean;
  usesOcr: boolean;
}

const STEPS: { step: OpenStep; label: string }[] = [
  { step: "loading_ocr", label: "Loading OCR (once per session)" },
  { step: "reading", label: "Reading the pages" },
  { step: "loading_model", label: "Loading the AI model (once per session)" },
  { step: "detecting", label: "Finding personal data" },
];

/** Progress while a PDF opens: a slow model load shows steps, not a frozen window. */
export function Opening({ name, step, usesModel, usesOcr }: OpeningProps) {
  // A loading step appears only when its model is used; Python skips it once loaded.
  const steps = STEPS.filter(
    (item) =>
      (item.step !== "loading_model" || usesModel) && (item.step !== "loading_ocr" || usesOcr),
  );
  const current = steps.findIndex((item) => item.step === step);
  return (
    <motion.main
      className="opening"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={gentle}
      aria-live="polite"
      aria-busy="true"
    >
      <h1>{name ? `Opening ${name}` : "Opening the document"}</h1>
      <ol className="opening-steps">
        {steps.map((item, index) => {
          const state = index < current ? "done" : index === current ? "current" : "pending";
          return (
            <li key={item.step} data-state={state}>
              {state === "done" && <Check size={16} aria-hidden />}
              {state === "current" && <LoaderCircle size={16} className="spinning" aria-hidden />}
              {state === "pending" && <Circle size={16} aria-hidden />}
              <span>{item.label}</span>
            </li>
          );
        })}
      </ol>
    </motion.main>
  );
}
