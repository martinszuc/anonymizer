import { motion } from "motion/react";

import { snappy } from "../motion";

interface Segment<T extends string> {
  value: T;
  label: string;
  count?: number;
}

interface SegmentedControlProps<T extends string> {
  name: string;
  segments: Segment<T>[];
  value: T;
  onChange: (value: T) => void;
}

export function SegmentedControl<T extends string>({
  name,
  segments,
  value,
  onChange,
}: SegmentedControlProps<T>) {
  return (
    <div className="segmented" role="tablist" aria-label={name}>
      {segments.map((segment) => (
        <button
          key={segment.value}
          type="button"
          role="tab"
          aria-selected={segment.value === value}
          className="segment"
          onClick={() => onChange(segment.value)}
        >
          {segment.value === value && (
            <motion.span layoutId={`${name}-highlight`} className="segment-highlight" transition={snappy} />
          )}
          <span className="segment-label">
            {segment.label}
            {segment.count !== undefined && <span className="segment-count">{segment.count}</span>}
          </span>
        </button>
      ))}
    </div>
  );
}
