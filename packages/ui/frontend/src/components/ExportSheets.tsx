import { ChevronRight, CircleCheck, FileOutput, ShieldAlert, TriangleAlert } from "lucide-react";

import {
  exportStages,
  exportStatus,
  exportSummary,
  leakSections,
  pagesLabel,
  plural,
  type ExportPlan,
  type LeakRow,
} from "../review";
import type { ExportProgress, ExportResult, LeakInfo } from "../types";
import { Button } from "./Button";
import { Sheet } from "./Sheet";
import { TaskProgress } from "./TaskProgress";

/** Which sheet of an export is up. */
export type ExportSheet =
  | { kind: "confirm-pages"; pages: number[] }
  /** Running; `progress` is null until Python's first step (the save dialog may still be open). */
  | { kind: "progress"; plan: ExportPlan; progress: ExportProgress | null }
  /** The leak check refused the copy; nothing is written until the reviewer saves it anyway. */
  | { kind: "leaks"; result: ExportResult }
  /** Written; `accepted` holds the leaks the reviewer saved it with. */
  | { kind: "result"; result: ExportResult; accepted: LeakInfo[] };

interface ExportSheetsProps {
  sheet: ExportSheet | null;
  busy: boolean;
  onExportAnyway: () => void;
  onSaveAnyway: () => void;
  /** Show where a leak lies: select its finding, or scroll to its page. */
  onShowLeak: (row: LeakRow) => void;
  onClose: () => void;
}

/** The sheets around an export: consent for unreadable pages, progress, leaks, the outcome. */
export function ExportSheets({ sheet, busy, onExportAnyway, onSaveAnyway, onShowLeak, onClose }: ExportSheetsProps) {
  // Nothing can stop an export once it runs; Escape must not hide it.
  const ignore = () => {};
  return (
    <>
      <Sheet
        open={sheet?.kind === "confirm-pages"}
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
        {sheet?.kind === "confirm-pages" && (
          <p>
            {pagesLabel(sheet.pages)} {sheet.pages.length === 1 ? "is a scan" : "are scans"}{" "}
            OCR did not read. Nothing on {sheet.pages.length === 1 ? "it" : "them"} was detected, so{" "}
            {sheet.pages.length === 1 ? "it goes" : "they go"} into the copy unredacted, and the leak
            check cannot see that.
          </p>
        )}
      </Sheet>
      <Sheet
        open={sheet?.kind === "progress" && sheet.progress !== null}
        title="Exporting"
        icon={<FileOutput size={28} />}
        onClose={ignore}
      >
        {sheet?.kind === "progress" && (
          <div className="export-progress" aria-busy="true">
            <TaskProgress
              status={exportStatus(sheet.progress, sheet.plan)}
              stages={exportStages(sheet.progress, sheet.plan)}
            />
          </div>
        )}
      </Sheet>
      <Sheet
        open={sheet?.kind === "leaks"}
        title="Possible leaks in the copy"
        icon={<ShieldAlert size={28} />}
        tone="warning"
        size="wide"
        onClose={onClose}
        actions={
          <>
            <Button data-default onClick={onClose}>
              Don’t Save
            </Button>
            <Button disabled={busy} onClick={onSaveAnyway}>
              Save Anyway
            </Button>
          </>
        }
      >
        {sheet?.kind === "leaks" && <LeaksBody leaks={sheet.result.leaks} onShow={onShowLeak} />}
      </Sheet>
      <Sheet
        open={sheet?.kind === "result"}
        title="Exported"
        icon={<CircleCheck size={28} />}
        tone="success"
        onClose={onClose}
        actions={
          <Button variant="primary" onClick={onClose}>
            Done
          </Button>
        }
      >
        {sheet?.kind === "result" && <ResultBody result={sheet.result} accepted={sheet.accepted} />}
      </Sheet>
    </>
  );
}

function LeaksBody({ leaks, onShow }: { leaks: LeakInfo[]; onShow: (row: LeakRow) => void }) {
  return (
    <>
      <p>
        The leak check found {plural(leaks.length, "place")} in the redacted copy that may still
        show personal data. Nothing is saved yet: save it anyway, or go back and look.
      </p>
      {leakSections(leaks).map((section) => (
        <section key={section.kind} className="leak-section" aria-label={section.title}>
          <h3 className="leak-section-title">{section.title}</h3>
          <p className="leak-section-note">{section.note}</p>
          <ul className="leak-rows">
            {section.rows.map((row) => (
              <li key={row.key}>
                {row.page !== null || row.entityId !== null ? (
                  <button type="button" className="leak-row" title="Show it" onClick={() => onShow(row)}>
                    <LeakText row={row} />
                    <ChevronRight size={14} aria-hidden />
                  </button>
                ) : (
                  <div className="leak-row">
                    <LeakText row={row} />
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>
      ))}
      <p className="sheet-hint">The check can be turned off in Settings.</p>
    </>
  );
}

function LeakText({ row }: { row: LeakRow }) {
  return (
    <span className="leak-row-text">
      <span className="leak-row-title">{row.title}</span>
      <span className="leak-row-where">{row.where}</span>
    </span>
  );
}

function ResultBody({ result, accepted }: { result: ExportResult; accepted: LeakInfo[] }) {
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
          {accepted.length > 0 ? (
            <dd className="sheet-warned">Saved with {plural(accepted.length, "warning")}</dd>
          ) : result.leak_check === "passed" ? (
            <dd className="sheet-passed">Passed</dd>
          ) : (
            <dd>Off</dd>
          )}
        </div>
      </dl>
      {result.pages_without_text.length > 0 && (
        <p className="sheet-note">
          {pagesLabel(result.pages_without_text)}{" "}
          {result.pages_without_text.length === 1 ? "is a scan" : "are scans"} OCR did not read, and{" "}
          {result.pages_without_text.length === 1 ? "was" : "were"} not redacted.
        </p>
      )}
    </>
  );
}
