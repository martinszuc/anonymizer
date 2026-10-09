import {
  ChevronDown,
  ChevronLeft,
  ChevronUp,
  Eye,
  EyeOff,
  FileOutput,
  FolderOpen,
  Keyboard,
  LocateFixed,
  Maximize2,
  Minus,
  Plus,
  Redo2,
  Settings,
  SquareDashedMousePointer,
  Undo2,
} from "lucide-react";
import { useRef, useState, type RefObject } from "react";

import { isMac, shortcut } from "../platform";
import { Button } from "./Button";

interface ToolbarProps {
  name: string;
  language: string | null;
  languageRecognised: boolean;
  pageCount: number;
  currentPage: number;
  scale: number;
  fitting: boolean;
  dirty: boolean;
  previewing: boolean;
  exporting: boolean;
  drawing: boolean;
  /** A click on a box only finds it in the list instead of also changing its decision. */
  locating: boolean;
  /** What undo and redo would do next ("Keep “Jan Novák”"); null when there is nothing. */
  undoLabel: string | null;
  redoLabel: string | null;
  /** The page field, focused by Cmd/Ctrl+G. */
  pageField: RefObject<HTMLInputElement | null>;
  onOpen: () => void;
  onZoom: (direction: 1 | -1) => void;
  onFit: () => void;
  onSave: () => void;
  onPreview: () => void;
  onExport: () => void;
  onSettings: () => void;
  onShortcuts: () => void;
  onDrawTool: () => void;
  onLocate: () => void;
  onClose: () => void;
  onUndo: () => void;
  onRedo: () => void;
  /** Scroll to a page, 0-based. */
  onPage: (index: number) => void;
}

export function Toolbar(props: ToolbarProps) {
  const { name, language, languageRecognised, scale, fitting, dirty, previewing, exporting } = props;
  return (
    <header className="toolbar">
      <div className="toolbar-title">
        <Button
          variant="plain"
          icon={<ChevronLeft size={17} />}
          aria-label="Close the document"
          title="Close the document"
          onClick={props.onClose}
        />
        <span className="toolbar-name" title={name}>
          {name}
        </span>
        <span
          className="badge"
          title={
            language === null
              ? "Rules of every language ran"
              : languageRecognised
                ? "Language recognised from the text"
                : "Language chosen on opening"
          }
        >
          {language === null ? "ALL" : language.toUpperCase()}
        </span>
        {dirty && (
          <span className="toolbar-edited" title={`Save the review to continue later (${shortcut("S")})`}>
            Not saved
          </span>
        )}
      </div>

      <PageNavigation
        currentPage={props.currentPage}
        pageCount={props.pageCount}
        field={props.pageField}
        onPage={props.onPage}
      />

      <div className="toolbar-actions">
        <div className="control-group" role="group" aria-label="Undo and redo">
          <Button
            variant="plain"
            icon={<Undo2 size={15} />}
            aria-label={props.undoLabel ? `Undo ${props.undoLabel}` : "Undo"}
            title={props.undoLabel ? `Undo ${props.undoLabel} (${shortcut("Z")})` : "Nothing to undo"}
            disabled={props.undoLabel === null}
            onClick={props.onUndo}
          />
          <Button
            variant="plain"
            icon={<Redo2 size={15} />}
            aria-label={props.redoLabel ? `Redo ${props.redoLabel}` : "Redo"}
            title={props.redoLabel ? `Redo ${props.redoLabel} (${shortcut("Z", { shift: true })})` : "Nothing to redo"}
            disabled={props.redoLabel === null}
            onClick={props.onRedo}
          />
        </div>
        <div className="control-group" role="group" aria-label="Zoom">
          <Button
            variant="plain"
            icon={<Minus size={15} />}
            aria-label="Zoom out"
            title={`Zoom out (${shortcut("−")})`}
            onClick={() => props.onZoom(-1)}
          />
          <button
            type="button"
            className="zoom-level"
            data-active={fitting}
            title={`Fit width (${shortcut("0")})`}
            onClick={props.onFit}
          >
            {fitting ? <Maximize2 size={13} aria-label="Fit width" /> : `${Math.round(scale * 100)} %`}
          </button>
          <Button
            variant="plain"
            icon={<Plus size={15} />}
            aria-label="Zoom in"
            title={`Zoom in (${shortcut("+")})`}
            onClick={() => props.onZoom(1)}
          />
        </div>
        <div className="control-group" role="group" aria-label="Tools">
          <Button
            variant="plain"
            className="toggle"
            aria-pressed={props.drawing}
            icon={<SquareDashedMousePointer size={16} />}
            aria-label="Draw a region"
            title={`Draw a region over a photo, signature or stamp (R, or hold ${isMac ? "⌥" : "Alt"})`}
            onClick={props.onDrawTool}
          />
          <Button
            variant="plain"
            className="toggle"
            aria-pressed={props.locating}
            icon={<LocateFixed size={16} />}
            aria-label="Click to find in the list"
            title={
              props.locating
                ? "A click on a box finds it in the list (L)"
                : "A click on a box keeps or redacts it; press to only find it in the list (L)"
            }
            onClick={props.onLocate}
          />
          <Button
            variant="plain"
            className="toggle"
            aria-pressed={previewing}
            icon={previewing ? <EyeOff size={16} /> : <Eye size={16} />}
            aria-label="Preview the redacted copy"
            title={`${previewing ? "Back to review" : "Preview the redacted copy"} (${shortcut("Y")})`}
            onClick={props.onPreview}
          />
        </div>
        <Button
          variant="plain"
          icon={<FolderOpen size={16} />}
          aria-label="Open"
          title={`Open another document (${shortcut("O")})`}
          onClick={props.onOpen}
        />
        <Button
          variant="plain"
          icon={<Settings size={16} />}
          aria-label="Settings"
          title={`Settings (${shortcut(",")})`}
          onClick={props.onSettings}
        />
        <Button
          variant="plain"
          icon={<Keyboard size={16} />}
          aria-label="Keyboard shortcuts"
          title="Keyboard shortcuts (?)"
          onClick={props.onShortcuts}
        />
        <Button title={`Save the review to continue later (${shortcut("S")})`} onClick={props.onSave}>
          Save Review
        </Button>
        <Button
          variant="primary"
          icon={<FileOutput size={15} />}
          disabled={exporting}
          title={`Save the redacted copy (${shortcut("E")})`}
          onClick={props.onExport}
        >
          {exporting ? "Exporting…" : "Export…"}
        </Button>
      </div>
    </header>
  );
}

interface PageNavigationProps {
  currentPage: number;
  pageCount: number;
  field: RefObject<HTMLInputElement | null>;
  onPage: (index: number) => void;
}

/** The page in view, which can be typed over to go to another, with previous and next. */
function PageNavigation({ currentPage, pageCount, field, onPage }: PageNavigationProps) {
  // While the field is being typed in, it shows what is typed rather than the page in view.
  const [typed, setTyped] = useState<string | null>(null);
  // Set once Return or Escape has dealt with what was typed, so leaving the field does nothing more.
  const settled = useRef(false);
  const go = (index: number) => onPage(Math.min(Math.max(index, 0), pageCount - 1));
  const finish = (follow: boolean) => {
    const number = Number.parseInt(typed ?? "", 10);
    if (follow && !settled.current && Number.isFinite(number)) go(number - 1);
    settled.current = false;
    setTyped(null);
  };
  return (
    <div className="page-navigation" role="group" aria-label="Pages">
      <Button
        variant="plain"
        icon={<ChevronUp size={15} />}
        aria-label="Previous page"
        title="Previous page"
        disabled={currentPage === 0}
        onClick={() => go(currentPage - 1)}
      />
      <label className="page-field" title={`Go to a page (${shortcut("G")})`}>
        <span className="visually-hidden">Page</span>
        <input
          ref={field}
          type="text"
          inputMode="numeric"
          value={typed ?? String(currentPage + 1)}
          size={String(pageCount).length}
          onFocus={(event) => {
            settled.current = false;
            event.currentTarget.select();
          }}
          onChange={(event) => setTyped(event.target.value.replace(/\D/g, ""))}
          onBlur={() => finish(true)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === "Escape") {
              finish(event.key === "Enter");
              settled.current = true;
              event.currentTarget.blur();
            }
            event.stopPropagation();
          }}
        />
        <span className="page-count">of {pageCount}</span>
      </label>
      <Button
        variant="plain"
        icon={<ChevronDown size={15} />}
        aria-label="Next page"
        title="Next page"
        disabled={currentPage >= pageCount - 1}
        onClick={() => go(currentPage + 1)}
      />
    </div>
  );
}
