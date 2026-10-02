# Review window design system

Target: a native-feeling macOS app (Preview, Mail, Xcode sidebars) that also looks
at home on Windows and Linux. Every value below is a CSS custom property in
`src/styles/tokens.css`. Colours, shadows, materials, type, spacing, radii,
motion and every size more than one component uses come from tokens. Only the
geometry of a single component (a switch track, a status dot, a stroke width) is
written as a literal, in that component's rule.

## Principles

1. **The page is the subject.** Chrome recedes: translucent sidebar, quiet toolbar,
   neutral canvas. Colour is reserved for entity types and the one primary action.
2. **Read while reviewing, preview before exporting.** Review mode keeps the text
   under every box readable, because deciding means reading. Preview mode (⌘Y, the
   eye button) draws exactly what export produces: opaque black boxes, kept items
   untouched. Nothing is destroyed until export.
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
| Elevation | `--shadow-page`, `--shadow-popover`, `--shadow-sheet`; `--backdrop` behind a sheet | three levels: page, popover, modal sheet |
| Control shadows | `--shadow-control` (selected segment), `--shadow-knob` (switch thumb) | not elevation: they separate a control's moving part |
| Materials | `--material-toolbar`, `--material-sidebar`, `--material-popover`, `--material-sheet` | `backdrop-filter` blur + saturation behind translucent surfaces |
| Sizes | `--toolbar-height` 52, `--sidebar-width` 300, `--control-height` 28, `--control-height-small` 24, `--hairline` 0.5 px | |
| Switch | `--switch-thumb`, `--switch-on-track`, `--switch-on-thumb` | on: ink track, white thumb; inverted in dark mode |
| Loading | `--shimmer` | placeholder sweep while a page renders |
| Motion | `--ease-out`, `--duration-fast` 120 ms, `--duration` 200 ms; springs in `src/motion.ts` | all motion off under `prefers-reduced-motion` |

Entity type colours: names red, email blue, phone green, links orange, IBAN and
bank account indigo, cards purple, birth number pink, company ID teal, address
brown, dates mint, other grey. Only a hue: text on a type colour is never used.

## Components

**Toolbar** (52 px). Document name and language; page position; zoom group (−, fit,
+); a back chevron at the far left closes the document; region tool (R, pressed = accent fill; holding Alt draws without it); locate
toggle (L, crosshair icon, pressed = a click on a box only selects it); preview
toggle (eye); open; *Save Review* (secondary);
primary *Export…* (Cmd/Ctrl+E), the final step. Controls are 28 px high.

**Sidebar** (300 px, translucent). Summary pill on top, segmented control
*Findings / Hidden*, then a grouped list. Section header: type dot, label, count.
Row: an accent dot while not reviewed (Mail's unread dot), covered text (monospace
for identifiers), meta line (page, source, score), trailing switch under a *Redact*
column label; a drawn region has a round remove button (×, `--danger` on hover)
instead of the switch, since a region is removed rather than kept. A finding in
hidden data (a link, metadata) shows a locked pill *Always removed* (`--fill`,
`--label-2`) instead, and no review dot: export clears it with the hidden item,
so there is nothing to decide.

**Models sheet.** A wide sheet (560 px) from *Manage models…* on the home
screen: one section per feature (`--fill` card), its state on the right
(*Ready* in `--keep`, otherwise `--label-2`), each model as a name over a
footnote line (size · licence · languages · source host). A missing Python
package shows a `--warning` line with the install command in `--font-mono`.
*Download <size>* is the primary button; while it runs, a progress bar
(6 px track in `--fill-active`, fill in `--accent`, pill radius) with
"received of total, then checked" replaces it. Other downloads are disabled.

**Page notices.** Above a page: a warning (`--warning` at 16 %, triangle icon)
for a scan OCR did not read, since nothing on it was detected; a quiet note
(`--fill`, `--label-2`, scan icon) for a page OCR read, reminding that OCR can
misread. Same shape for both (`.page-warning`, `.page-note`).

**Hidden tab.** A notice saying everything here is removed; a warning-tone notice
(`--warning` at 12 %) when the file has attachments, whose contents are never
checked. Each kind has a one-line note under its header (what it is, what export
does). A row names its place and the findings it contains; a row with a place on
a page is selectable and outlines the item there (`--accent`, one pulse). Meta text uses `--label-2`: `--label-3` fails AA contrast at 11 px
and is for decoration only. Rows: hover `--fill`, selected `--accent-fill`.
Keyboard: ↑/↓ moves the selection, Space toggles, Return scrolls to it.

**Redaction box** on the page, one per word box of an entity:

| State | Review mode | Preview mode | Meaning |
|---|---|---|---|
| Proposed (pending) | `--type` at 24 %, 1.5 px solid `--type` | opaque `--ink` | will be redacted; not yet looked at |
| Redact (confirmed) | `--type` at 34 %, 1.5 px solid `--type` | opaque `--ink` | will be redacted |
| Keep (rejected) | no fill, 1 px dashed `--type` | nothing drawn | stays in the output |
| Propagated | as its state, dotted outline | as its state | a repeat of other marked text |
| Hover | fill 40 %, 2 px outline, popover | `--ink` at 25 % (peek) | what a click will do |
| Selected | 2.5 px `--accent`, one pulse | same | chosen in the list |
| Drawn region | hatched (`.hatch-line`), 1.5 px `--label-2`, numbered | opaque `--ink`, no number | drawn by the reviewer; a click selects it, Delete removes it, Cmd/Ctrl+Z removes the last drawn |
| Region number | 18 px pill on the region's top-left corner, `--elevated`, `--shadow-control`, caption weight 600 | hidden | the region's place in drawing order, as its sidebar row ("Region 2") says; renumbered when one is removed |
| Drawing (draft) | `--accent` at 12 %, dashed `--accent` | same | the rectangle being dragged |

**Summary pill.** "12 redacted · 2 kept · 6 hidden removed"; counts animate.

**Empty state.** Centered icon, title, one sentence on privacy, *Open PDF…* (primary)
and *Open Review…* (secondary), shortcut hints.

**Home** (no document). A centred column (560 px): app icon, name and one
line; the **drop area** (dashed `--separator` border, `--elevated`, *Open PDF…*
primary; while a file is dragged over the window: `--accent` border on
`--accent-fill`, "Drop to open"); a **Detection** card of option rows (label,
one-line note in `--label-2`, control on the right: the language segmented
control, setting switches); *Continue a saved review…* as a plain button; a
footer "Everything stays on this computer · version". The model's row says why
its switch is disabled and what to run.

**Opening.** A step list in an `--elevated` card: done (check, `--keep`),
current (spinning loader, `--accent`, label in `--label`), pending (circle,
`--label-3`). Shown from Python's first progress event until the document
opens; a model step appears only when the model is used.

**Drop overlay.** Over an open document while a file is dragged: dashed
`--accent` border on `--accent-fill` below the toolbar, a pill "Drop to open
another PDF".

**Switch tones.** `redact` (findings): on is `--ink`, not a Tab stop (the list
drives it). `setting` (home options): on is `--accent`, a Tab stop, can be
disabled (40 % opacity).

**Sheet.** Modal, drops from under the toolbar (macOS sheet), backdrop `--backdrop`
below the toolbar only. Icon in a tinted circle (`success` → `--keep`, `warning`,
`danger`), title, body, actions right-aligned with the default last. Escape closes;
focus goes to the action marked `data-default`, otherwise the last one; mark Cancel
when the other choice carries a risk. While a sheet is open, window shortcuts are off.
Used for export: consent for pages without a text layer, then the result (summary
rows and "Leak check: Passed", or the leaks and "Nothing was written").

**Toast.** Bottom centre, `--elevated` with blur, icon + one line, 4 s; errors use
`--danger` for the icon only.

**Buttons.** Primary (accent fill), secondary (`--fill`), plain icon (transparent,
hover `--fill`). 28 px, radius `--radius-control`, focus ring 3 px `--accent` at 40 %.

**Switch.** 32 × 18 px, on = `--ink` track (it means "redact"), off = `--fill-active`;
thumb moves on a spring.
