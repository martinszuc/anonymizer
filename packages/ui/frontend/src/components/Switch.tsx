import { motion } from "motion/react";

import { snappy } from "../motion";

interface SwitchProps {
  checked: boolean;
  label: string;
  onChange: (checked: boolean) => void;
}

/** On means "redact": the track takes the redaction ink, as in DESIGN.md. */
export function Switch({ checked, label, onChange }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      title={label}
      className="switch"
      data-on={checked}
      tabIndex={-1}
      onClick={(event) => {
        event.stopPropagation();
        onChange(!checked);
      }}
    >
      <motion.span className="switch-thumb" layout transition={snappy} />
    </button>
  );
}
