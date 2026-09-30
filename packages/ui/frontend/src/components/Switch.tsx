import { motion } from "motion/react";

import { snappy } from "../motion";

interface SwitchProps {
  checked: boolean;
  label: string;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  /**
   * `redact` (a finding's row): on means redact, so the track takes the
   * redaction ink, and the list's arrow keys and Space drive it, so it is not
   * a Tab stop. `setting`: an ordinary option with the accent track, reached
   * with Tab.
   */
  tone?: "redact" | "setting";
}

export function Switch({ checked, label, onChange, disabled = false, tone = "redact" }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      title={label}
      className="switch"
      data-on={checked}
      data-tone={tone}
      disabled={disabled}
      tabIndex={tone === "setting" ? 0 : -1}
      onClick={(event) => {
        event.stopPropagation();
        onChange(!checked);
      }}
    >
      <motion.span className="switch-thumb" layout transition={snappy} />
    </button>
  );
}
