import { Check, Circle, LoaderCircle } from "lucide-react";

import type { OpenStatus, StageState } from "../review";

interface TaskProgressProps {
  /** What is running now, with its count and the bar's share. */
  status: OpenStatus;
  /** The stages in order: done, the current one, those still to come. */
  stages: StageState[];
}

/** A task Python runs in steps: what is happening now above a bar, then the stages. */
export function TaskProgress({ status, stages }: TaskProgressProps) {
  return (
    <>
      <div className="task-status" aria-live="polite">
        <span>{status.label}</span>
        {status.count && <span className="task-count">{status.count}</span>}
      </div>
      <div
        className="progress-track"
        role="progressbar"
        aria-label={status.label}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={status.fraction === null ? undefined : Math.round(status.fraction * 100)}
        data-indeterminate={status.fraction === null}
      >
        <div
          className="progress-fill"
          style={status.fraction === null ? undefined : { width: `${status.fraction * 100}%` }}
        />
      </div>
      <ol className="task-steps">
        {stages.map((stage) => (
          <li key={stage.key} data-state={stage.state}>
            {stage.state === "done" && <Check size={16} aria-hidden />}
            {stage.state === "current" && <LoaderCircle size={16} className="spinning" aria-hidden />}
            {stage.state === "pending" && <Circle size={16} aria-hidden />}
            <span>{stage.label}</span>
          </li>
        ))}
      </ol>
    </>
  );
}
