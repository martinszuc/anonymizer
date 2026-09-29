// Spring presets (DESIGN.md → Motion). MotionConfig in App turns them off
// under prefers-reduced-motion.

/** Controls: a switch thumb, the segmented highlight. Quick, no overshoot. */
export const snappy = { type: "spring", stiffness: 560, damping: 40, mass: 0.7 } as const;

/** Layout: rows settling, popovers and toasts appearing. */
export const gentle = { type: "spring", stiffness: 340, damping: 32 } as const;
