import { FileLock2, FileUp, Settings, ShieldCheck } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";

import { gentle } from "../motion";
import { shortcut } from "../platform";
import { nameModelReady, ocrReady } from "../review";
import type { AppStatus, ChoiceStatus, OpenOptions } from "../types";
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
  onModels: () => void;
  onSettings: () => void;
}

/** The window with no document: open one, and choose how it is scanned. */
export function Home({
  status,
  options,
  busy,
  dragging,
  onOptions,
  onOpen,
  onOpenReview,
  onModels,
  onSettings,
}: HomeProps) {
  const languages = status?.languages ?? [];
  const models = status?.names.models ?? [];
  const modelAvailable = models.some((model) => model.state === "ready");
  const modelOn = options.use_model && status !== null && nameModelReady(status.names, options.name_model);
  const ocrAvailable = status?.ocr.engines.some((engine) => engine.state === "ready") ?? false;
  const ocrOn = options.use_ocr && status !== null && ocrReady(status.ocr, options.ocr_engine);
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
        <p>Find personal data in a PDF or an image, decide what goes, export a redacted copy.</p>
      </header>

      <section className="drop-zone" data-dragging={dragging} aria-label="Open a document">
        <FileUp size={28} strokeWidth={1.5} aria-hidden />
        <p className="drop-zone-title">{dragging ? "Drop to open" : "Drop a PDF or an image here"}</p>
        <p className="drop-zone-or">or</p>
        <Button variant="primary" disabled={busy} onClick={onOpen}>
          Open document…
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
              options.language === "auto"
                ? "Recognised from the text. If it is unclear, every language's rules run."
                : options.language === null
                  ? "Every language's rules run. Choosing one gives fewer false alarms."
                  : "Rules for this language, plus those that work in any (email, IBAN, cards, links)."
            }
          >
            <SegmentedControl
              name="language"
              value={options.language ?? "all"}
              onChange={(value) => onOptions({ ...options, language: value === "all" ? null : value })}
              segments={[
                { value: "auto", label: "Auto" },
                { value: "all", label: "All" },
                ...languages.map((language) => ({ value: language.code, label: language.name })),
              ]}
            />
          </OptionRow>
          <OptionRow label="Names and addresses" note={modelNote(status, modelAvailable)}>
            <Switch
              checked={modelOn}
              disabled={!modelAvailable}
              tone="setting"
              label="Find names and addresses with the AI model"
              onChange={(checked) => onOptions({ ...options, use_model: checked })}
            />
          </OptionRow>
          {models.length > 1 && (modelOn || !modelAvailable) && (
            <Choices
              label="Name model"
              group="name-model"
              choices={models}
              chosen={options.name_model}
              onChoose={(name) => onOptions({ ...options, name_model: name })}
            />
          )}
          <OptionRow label="Scanned pages" note={ocrNote(status, ocrAvailable)}>
            <Switch
              checked={ocrOn}
              disabled={!ocrAvailable}
              tone="setting"
              label="Read scanned pages with OCR"
              onChange={(checked) => onOptions({ ...options, use_ocr: checked })}
            />
          </OptionRow>
          {status && (ocrOn || !ocrAvailable) && (
            <Choices
              label="OCR engine"
              group="ocr-engine"
              choices={status.ocr.engines}
              chosen={options.ocr_engine}
              onChoose={(name) => onOptions({ ...options, ocr_engine: name })}
            />
          )}
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
        <div className="options-links">
          <Button variant="plain" onClick={onModels}>
            Manage models…
          </Button>
          <Button variant="plain" icon={<Settings size={15} />} onClick={onSettings}>
            Settings…
          </Button>
        </div>
      </section>

      <Button variant="plain" disabled={busy} onClick={onOpenReview}>
        Continue a saved review… <kbd>{shortcut("O", { shift: true })}</kbd>
      </Button>

      <footer className="home-footer">
        <ShieldCheck size={14} aria-hidden />
        Works offline{status ? ` · version ${status.version}` : ""}
      </footer>
    </motion.main>
  );
}

/** A labelled option with a note under its label and its control on the right. */
export function OptionRow({ label, note, children }: { label: string; note: ReactNode; children: ReactNode }) {
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

/** What OCR does here; when no engine can read, the engines below say what each needs. */
function ocrNote(status: AppStatus | null, available: boolean): ReactNode {
  if (status === null) return "Checking…";
  return available
    ? "Reads the text of scanned pages and images, so they are checked and redacted too."
    : "No OCR engine is ready yet. What each needs is listed below.";
}

interface ChoicesProps {
  /** Names the group for assistive technology. */
  label: string;
  /** The radio group's form name. */
  group: string;
  choices: ChoiceStatus[];
  chosen: string;
  onChoose: (name: string) => void;
}

/** OCR engines or name models to choose from, each with what it is for; one that cannot run says why. */
function Choices({ label, group, choices, chosen, onChoose }: ChoicesProps) {
  return (
    <div className="option-choices" role="radiogroup" aria-label={label}>
      {choices.map((choice) => {
        const ready = choice.state === "ready";
        return (
          <label key={choice.name} className="option-choice" data-disabled={!ready}>
            <input
              type="radio"
              name={group}
              value={choice.name}
              checked={ready && choice.name === chosen}
              disabled={!ready}
              onChange={() => onChoose(choice.name)}
            />
            <span className="option-text">
              <span className="option-label">{choice.title}</span>
              <span className="option-note">{choice.description}</span>
              {!ready && <span className="option-note">{choiceReason(choice)}</span>}
            </span>
          </label>
        );
      })}
    </div>
  );
}

const FILES_MISSING = "Model files missing: download them in Manage models.";

/** Why an engine or a model cannot run yet, and what to do about it. */
function choiceReason(choice: ChoiceStatus): ReactNode {
  return choice.state === "not_installed" ? (
    <>
      Not installed. Install it with <code>{choice.install_command}</code>.
    </>
  ) : (
    FILES_MISSING
  );
}

/**
 * What the name model can do here, or how to make it available. With several models, the
 * list below says what each needs; with one, the note says it.
 */
function modelNote(status: AppStatus | null, available: boolean): ReactNode {
  if (status === null) return "Checking…";
  if (available) return "An AI model finds names and addresses the rules cannot. Opening takes longer.";
  const [first, ...others] = status.names.models;
  if (first === undefined) return "No name model is in the catalog.";
  return others.length > 0 ? "No name model is ready yet. What each needs is listed below." : choiceReason(first);
}
