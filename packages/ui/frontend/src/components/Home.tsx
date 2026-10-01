import { FileLock2, FileUp, ShieldCheck } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";

import { gentle } from "../motion";
import { shortcut } from "../platform";
import type { AppStatus, OpenOptions } from "../types";
import { Button } from "./Button";
import { SegmentedControl } from "./SegmentedControl";
import { Switch } from "./Switch";

interface HomeProps {
  status: AppStatus | null;
  options: OpenOptions;
  busy: boolean;
  /** A file is being dragged over the window. */
  dragging: boolean;
  onOptions: (options: OpenOptions) => void;
  onOpen: () => void;
  onOpenReview: () => void;
}

/** The window with no document: open one, and choose how it is scanned. */
export function Home({ status, options, busy, dragging, onOptions, onOpen, onOpenReview }: HomeProps) {
  const languages = status?.languages ?? [];
  const modelReady = status?.model.state === "ready";
  const ocrReady = status?.ocr.state === "ready";
  return (
    <motion.main
      className="home"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={gentle}
    >
      <header className="home-header">
        <div className="home-icon" aria-hidden>
          <FileLock2 size={30} strokeWidth={1.5} />
        </div>
        <h1>Anonymizer</h1>
        <p>Find personal data in a PDF, decide what goes, and export a redacted copy.</p>
      </header>

      <section className="drop-zone" data-dragging={dragging} aria-label="Open a PDF">
        <FileUp size={28} strokeWidth={1.5} aria-hidden />
        <p className="drop-zone-title">{dragging ? "Drop to open" : "Drop a PDF here"}</p>
        <p className="drop-zone-or">or</p>
        <Button variant="primary" disabled={busy} onClick={onOpen}>
          Open PDF…
        </Button>
        <p className="drop-zone-hint">
          <kbd>{shortcut("O")}</kbd>
        </p>
      </section>

      <section className="options" aria-label="Detection">
        <h2 className="options-title">Detection</h2>
        <div className="options-card">
          <OptionRow
            label="Language"
            note={
              options.language === null
                ? "Every language's rules run. Choosing one gives fewer false alarms."
                : "Rules for this language, plus those that work in any (email, IBAN, cards, links)."
            }
          >
            <SegmentedControl
              name="language"
              value={options.language ?? "all"}
              onChange={(value) => onOptions({ ...options, language: value === "all" ? null : value })}
              segments={[
                { value: "all", label: "All" },
                ...languages.map((language) => ({ value: language.code, label: language.name })),
              ]}
            />
          </OptionRow>
          <OptionRow label="Names and addresses" note={modelNote(status)}>
            <Switch
              checked={options.use_model && modelReady}
              disabled={!modelReady}
              tone="setting"
              label="Find names and addresses with the AI model"
              onChange={(checked) => onOptions({ ...options, use_model: checked })}
            />
          </OptionRow>
          <OptionRow label="Scanned pages" note={ocrNote(status)}>
            <Switch
              checked={options.use_ocr && ocrReady}
              disabled={!ocrReady}
              tone="setting"
              label="Read scanned pages with OCR"
              onChange={(checked) => onOptions({ ...options, use_ocr: checked })}
            />
          </OptionRow>
          <OptionRow
            label="Mark repeats"
            note="Also mark every other place the same text appears, such as a name found once."
          >
            <Switch
              checked={options.propagate}
              tone="setting"
              label="Mark every repeat of text that was found"
              onChange={(checked) => onOptions({ ...options, propagate: checked })}
            />
          </OptionRow>
        </div>
      </section>

      <Button variant="plain" disabled={busy} onClick={onOpenReview}>
        Continue a saved review… <kbd>{shortcut("O", { shift: true })}</kbd>
      </Button>

      <footer className="home-footer">
        <ShieldCheck size={14} aria-hidden />
        Everything stays on this computer{status ? ` · version ${status.version}` : ""}
      </footer>
    </motion.main>
  );
}

function OptionRow({ label, note, children }: { label: string; note: ReactNode; children: ReactNode }) {
  return (
    <div className="option-row">
      <div className="option-text">
        <span className="option-label">{label}</span>
        <span className="option-note">{note}</span>
      </div>
      <div className="option-control">{children}</div>
    </div>
  );
}

/** What OCR does here, or how to make it available. */
function ocrNote(status: AppStatus | null): ReactNode {
  switch (status?.ocr.state) {
    case "ready":
      return "Reads the text of scanned pages, so they are checked and redacted too.";
    case "not_installed":
      return (
        <>
          Not installed. Install it with <code>uv sync --group ocr-{status.ocr.engine}</code>.
        </>
      );
    case "files_missing":
      return (
        <>
          Model files missing. Fetch them with{" "}
          <code>uv run python scripts/download.py fetch {status.ocr.missing.at(-1)}</code>.
        </>
      );
    default:
      return "Checking…";
  }
}

/** What the name model can do here, or how to make it available. */
function modelNote(status: AppStatus | null): ReactNode {
  switch (status?.model.state) {
    case "ready":
      return "An AI model finds names and addresses the rules cannot. Opening takes longer.";
    case "not_installed":
      return (
        <>
          Not installed. Install it with <code>uv sync --group ner</code>.
        </>
      );
    case "files_missing":
      return (
        <>
          Model files missing. Fetch them with{" "}
          <code>uv run python scripts/download.py fetch gliner-multi-v2.1</code>.
        </>
      );
    default:
      return "Checking…";
  }
}
