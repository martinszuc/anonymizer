import { CircleCheck, ShieldAlert, TriangleAlert } from "lucide-react";

import { exportSummary, leakLayerLabel, pageList } from "../review";
import type { ExportResult } from "../types";
import { Button } from "./Button";
import { Sheet } from "./Sheet";

export type ExportStep =
  | { kind: "confirm-pages"; pages: number[] }
  | { kind: "result"; result: ExportResult };

interface ExportSheetsProps {
  step: ExportStep | null;
  busy: boolean;
  onExportAnyway: () => void;
  onClose: () => void;
}

/** The sheets around an export: consent for unreadable pages, then the outcome. */
export function ExportSheets({ step, busy, onExportAnyway, onClose }: ExportSheetsProps) {
  return (
    <>
      <Sheet
        open={step?.kind === "confirm-pages"}
        title="Some pages cannot be redacted"
        icon={<TriangleAlert size={28} />}
        tone="warning"
        onClose={onClose}
        actions={
          <>
            <Button data-default onClick={onClose}>
              Cancel
            </Button>
            <Button disabled={busy} onClick={onExportAnyway}>
              Export Anyway…
            </Button>
          </>
        }
      >
        {step?.kind === "confirm-pages" && (
          <p>
            {capitalised(pageList(step.pages))} {step.pages.length === 1 ? "has" : "have"} no text
            layer, probably a scan. Nothing on {step.pages.length === 1 ? "it" : "them"} was detected,
            so {step.pages.length === 1 ? "it goes" : "they go"} into the copy unredacted, and the leak
            check cannot see that.
          </p>
        )}
      </Sheet>
      <Sheet
        open={step?.kind === "result"}
        title={step?.kind === "result" && !step.result.written ? "Nothing was written" : "Exported"}
        icon={
          step?.kind === "result" && !step.result.written ? (
            <ShieldAlert size={28} />
          ) : (
            <CircleCheck size={28} />
          )
        }
        tone={step?.kind === "result" && !step.result.written ? "danger" : "success"}
        onClose={onClose}
        actions={
          <Button variant="primary" onClick={onClose}>
            Done
          </Button>
        }
      >
        {step?.kind === "result" && <ResultBody result={step.result} />}
      </Sheet>
    </>
  );
}

function ResultBody({ result }: { result: ExportResult }) {
  if (!result.written) {
    return (
      <>
        <p>
          The leak check found personal data still readable in the redacted copy, so it was
          deleted. Your original and your decisions are unchanged.
        </p>
        <ul className="sheet-leaks">
          {result.leaks.map((leak, index) => (
            <li key={index}>
              <span className="sheet-leak-where">
                {leakLayerLabel(leak.layer)} · {leak.where}
              </span>
              <span className="mono">{leak.text}</span>
            </li>
          ))}
        </ul>
      </>
    );
  }
  return (
    <>
      <p className="sheet-file">{result.name}</p>
      <dl className="sheet-summary">
        {exportSummary(result).map((line) => (
          <div key={line.label}>
            <dt>{line.label}</dt>
            <dd>{line.value}</dd>
          </div>
        ))}
        <div>
          <dt>Leak check</dt>
          <dd className="sheet-passed">Passed</dd>
        </div>
      </dl>
      {result.pages_without_text.length > 0 && (
        <p className="sheet-note">
          {capitalised(pageList(result.pages_without_text))} had no text layer and{" "}
          {result.pages_without_text.length === 1 ? "was" : "were"} not redacted.
        </p>
      )}
    </>
  );
}

function capitalised(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
