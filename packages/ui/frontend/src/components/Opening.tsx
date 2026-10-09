import { motion } from "motion/react";

import { gentle } from "../motion";
import { openStatus } from "../review";
import type { OpenProgress, OpenStep } from "../types";
import { TaskProgress } from "./TaskProgress";

interface OpeningProps {
  /** The dropped file's name; unknown when it came from the open dialog. */
  name: string | null;
  progress: OpenProgress;
  usesModel: boolean;
  usesOcr: boolean;
}

const STEPS: { step: OpenStep; label: string }[] = [
  { step: "loading_ocr", label: "Loading the OCR engine" },
  { step: "reading", label: "Reading the pages" },
  { step: "loading_model", label: "Loading the name model" },
  { step: "detecting", label: "Finding personal data" },
];

/** OCR is part of reading the pages in the list; the status line tells them apart. */
const LISTED_AS: Partial<Record<OpenStep, OpenStep>> = { ocr: "reading" };

/**
 * Progress while a document opens: what is happening now with a bar (page by page
 * where the step counts pages), above the steps still to come.
 */
export function Opening({ name, progress, usesModel, usesOcr }: OpeningProps) {
  // A loading step appears only when its model is used; Python skips it once loaded.
  const steps = STEPS.filter(
    (item) =>
      (item.step !== "loading_model" || usesModel) && (item.step !== "loading_ocr" || usesOcr),
  );
  const listed = LISTED_AS[progress.step] ?? progress.step;
  const current = steps.findIndex((item) => item.step === listed);
  const stages = steps.map((item, index) => ({
    key: item.step,
    label: item.label,
    state: index < current ? ("done" as const) : index === current ? ("current" as const) : ("pending" as const),
  }));
  return (
    <motion.main
      className="opening"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={gentle}
      aria-busy="true"
    >
      <h1>{name ? `Opening ${name}` : "Opening the document"}</h1>
      <div className="opening-card">
        <TaskProgress status={openStatus(progress)} stages={stages} />
      </div>
    </motion.main>
  );
}
