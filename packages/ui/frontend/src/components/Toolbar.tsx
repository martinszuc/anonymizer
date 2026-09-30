import {
  ChevronLeft,
  Eye,
  EyeOff,
  FileOutput,
  FileText,
  FolderOpen,
  Maximize2,
  Minus,
  Plus,
  SquareDashedMousePointer,
} from "lucide-react";

import { isMac, shortcut } from "../platform";
import { Button } from "./Button";

interface ToolbarProps {
  name: string;
  language: string | null;
  pageCount: number;
  currentPage: number;
  scale: number;
  fitting: boolean;
  dirty: boolean;
  previewing: boolean;
  exporting: boolean;
  drawing: boolean;
  onOpen: () => void;
  onZoom: (direction: 1 | -1) => void;
  onFit: () => void;
  onSave: () => void;
  onPreview: () => void;
  onExport: () => void;
  onDrawTool: () => void;
  onClose: () => void;
}

export function Toolbar(props: ToolbarProps) {
  const { name, language, pageCount, currentPage, scale, fitting, dirty, previewing, exporting } =
    props;
  return (
    <header className="toolbar">
      <div className="toolbar-title">
        <Button
          variant="plain"
          icon={<ChevronLeft size={17} />}
          aria-label="Close the document"
          title="Close the document and go back to the start"
          onClick={props.onClose}
        />
        <FileText size={16} className="toolbar-title-icon" aria-hidden />
        <span className="toolbar-name" title={name}>
          {name}
        </span>
        {language && <span className="badge">{language.toUpperCase()}</span>}
        {dirty && <span className="toolbar-edited">Edited</span>}
      </div>

      <span className="toolbar-pages" aria-live="polite">
        Page {currentPage + 1} of {pageCount}
      </span>

      <div className="toolbar-actions">
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
        <Button
          variant="plain"
          className="toggle"
          aria-pressed={props.drawing}
          icon={<SquareDashedMousePointer size={16} />}
          aria-label="Draw a region"
          title={`Draw a region over a photo, signature or stamp (R, or hold ${isMac ? "⌥" : "Alt"} and drag)`}
          onClick={props.onDrawTool}
        />
        <Button
          variant="plain"
          className="toggle"
          aria-pressed={previewing}
          icon={previewing ? <EyeOff size={16} /> : <Eye size={16} />}
          aria-label="Preview the redacted output"
          title={`${previewing ? "Back to review" : "Preview the redacted output"} (${shortcut("Y")})`}
          onClick={props.onPreview}
        />
        <Button
          variant="plain"
          icon={<FolderOpen size={16} />}
          aria-label="Open"
          title={`Open a PDF (${shortcut("O")})`}
          onClick={props.onOpen}
        />
        <Button title={`Save the review to continue later (${shortcut("S")})`} onClick={props.onSave}>
          Save Review
        </Button>
        <Button
          variant="primary"
          icon={<FileOutput size={15} />}
          disabled={exporting}
          title={`Write the redacted PDF (${shortcut("E")})`}
          onClick={props.onExport}
        >
          {exporting ? "Exporting…" : "Export…"}
        </Button>
      </div>
    </header>
  );
}
