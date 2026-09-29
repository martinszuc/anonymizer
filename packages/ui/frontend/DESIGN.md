# Review window design system

Target: a native-feeling macOS app (Preview, Mail, Xcode sidebars) that also looks
at home on Windows and Linux. Every value below is a CSS custom property in
`src/styles/tokens.css`; components use tokens, never literal colors or sizes.

## Principles

1. **The page is the subject.** Chrome recedes: translucent sidebar, quiet toolbar,
   neutral canvas. Colour is reserved for entity types and the one primary action.
2. **What you see is what export does.** A redacted item is a black box, as in the
   output. Hovering peeks underneath; nothing is destroyed until export.
3. **Every decision is one click and reversible.** Clicking a box or a row switch
   toggles redact / keep. Motion confirms the change without delaying it.
4. **Nothing leaves the machine.** No web fonts, no remote assets, a strict CSP.

## Tokens

| Group | Tokens | Light / dark |
|---|---|---|
| Surfaces | `--canvas` (behind pages), `--sidebar`, `--toolbar`, `--elevated` (popovers, toasts), `--page` | neutral greys; sidebar and toolbar translucent with `backdrop-filter` |
| Labels | `--label`, `--label-2`, `--label-3` | Apple's label / secondary / tertiary opacities |
| Lines and fills | `--separator`, `--fill`, `--fill-hover`, `--fill-active` | grey at 12 / 16 / 22 % |
| Accent | `--accent`, `--accent-fill`, `--on-accent` | system blue `#007aff` / `#0a84ff` |
| Status | `--keep`, `--warning`, `--danger` | system green / orange / red |
| Redaction | `--ink` | near-black in both modes: redaction is black in the output |
| Entity types | `--type` set per `[data-type]` | Apple system colours, see below |
| Type scale | `--text-caption` 11, `--text-footnote` 12, `--text-body` 13, `--text-title` 15, `--text-large` 22 px | macOS sizes; weights 400 / 500 / 600 |
| Fonts | `--font` system stack, `--font-mono` `ui-monospace` for identifiers | no downloads |
| Spacing | `--space-1`..`--space-8` = 2, 4, 8, 12, 16, 20, 24, 32 px | 4 px grid |
| Radius | `--radius-box` 3, `--radius-control` 6, `--radius-row` 8, `--radius-card` 12, `--radius-pill` 999 | |
| Elevation | `--shadow-page`, `--shadow-popover` | two levels only |
| Motion | `--ease-out`, `--duration-fast` 120 ms, `--duration` 200 ms; springs in `src/motion.ts` | all motion off under `prefers-reduced-motion` |

Entity type colours: names red, email blue, phone green, links orange, IBAN and
bank account indigo, cards purple, birth number pink, company ID teal, address
brown, dates mint, other grey. Only a hue: text on a type colour is never used.

## Components

**Toolbar** (52 px). Document name and language; page position; zoom group (−, fit,
+); primary *Save Review*. Controls are 28 px high.

**Sidebar** (300 px, translucent). Summary pill on top, segmented control
*Findings / Hidden*, then a grouped list. Section header: type dot, label, count.
Row: an accent dot while not reviewed (Mail's unread dot), covered text (monospace
for identifiers), meta line (page, source, score), trailing switch under a *Redact*
column label. Meta text uses `--label-2`: `--label-3` fails AA contrast at 11 px
and is for decoration only. Rows: hover `--fill`, selected `--accent-fill`.
Keyboard: ↑/↓ moves the selection, Space toggles, Return scrolls to it.

**Redaction box** on the page, one per word box of an entity:

| State | Fill | Outline | Meaning |
|---|---|---|---|
| Proposed (pending) | `--ink`, opaque | 1.5 px `--type` ring | will be redacted; not yet looked at |
| Redact (confirmed) | `--ink` | none | will be redacted |
| Keep (rejected) | `--type` at 12 % | 1 px dashed `--type` | stays in the output |
| Propagated | as its state | dotted ring | found as a repeat of other marked text |
| Hover | `--ink` at 25 % (peek) | 2 px `--type` | popover with type, text, next action |
| Selected | as its state | 2 px `--accent` focus ring, one pulse | chosen in the list |

**Summary pill.** "12 redacted · 2 kept · 6 hidden removed"; counts animate.

**Empty state.** Centered icon, title, one sentence on privacy, *Open PDF…* (primary)
and *Open Review…* (secondary), shortcut hints.

**Toast.** Bottom centre, `--elevated` with blur, icon + one line, 4 s; errors use
`--danger` for the icon only.

**Buttons.** Primary (accent fill), secondary (`--fill`), plain icon (transparent,
hover `--fill`). 28 px, radius `--radius-control`, focus ring 3 px `--accent` at 40 %.

**Switch.** 32 × 18 px, on = `--ink` track (it means "redact"), off = `--fill-active`;
thumb moves on a spring.
