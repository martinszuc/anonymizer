import { Keyboard } from "lucide-react";

import { isMac, shortcut } from "../platform";
import { Button } from "./Button";
import { Sheet } from "./Sheet";

const ALT = isMac ? "⌥" : "Alt";

/** Every shortcut of the window, by where it acts; the keys as this platform names them. */
const SECTIONS: { title: string; keys: [string, string][] }[] = [
  {
    title: "Document",
    keys: [
      ["Open a document", shortcut("O")],
      ["Continue a saved review", shortcut("O", { shift: true })],
      ["Save the review", shortcut("S")],
      ["Export the redacted copy", shortcut("E")],
      ["Settings", shortcut(",")],
    ],
  },
  {
    title: "Deciding",
    keys: [
      ["Next undecided finding", "N"],
      ["Previous undecided finding", "⇧N"],
      ["Move through the list", "↑ ↓"],
      ["Keep or redact the selected finding", "Space"],
      ["Show or hide each repeat", "→ ←"],
      ["Undo", shortcut("Z")],
      ["Redo", shortcut("Z", { shift: true })],
      ["Remove an item you added", "Delete"],
      ["Clear the selection", "Esc"],
    ],
  },
  {
    title: "Pages",
    keys: [
      ["Preview the redacted copy", shortcut("Y")],
      ["Go to a page", shortcut("G")],
      ["Zoom in, out, fit width", `${shortcut("+")} ${shortcut("−")} ${shortcut("0")}`],
      ["Draw a region", `R, or hold ${ALT}`],
      ["Click a box to find it in the list", "L"],
      ["Type of a word you add", "1–6"],
      ["Add it", "Return"],
    ],
  },
];

export function ShortcutsSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Sheet
      open={open}
      title="Keyboard Shortcuts"
      size="wide"
      icon={<Keyboard size={28} />}
      onClose={onClose}
      actions={
        <Button data-default onClick={onClose}>
          Done
        </Button>
      }
    >
      <div className="shortcuts">
        {SECTIONS.map((section) => (
          <section key={section.title} aria-label={section.title}>
            <h3 className="options-title">{section.title}</h3>
            <dl className="shortcut-list">
              {section.keys.map(([action, keys]) => (
                <div key={action}>
                  <dt>{action}</dt>
                  <dd>
                    <kbd>{keys}</kbd>
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
      </div>
    </Sheet>
  );
}
