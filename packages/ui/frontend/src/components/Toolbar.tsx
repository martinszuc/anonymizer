import { FileText, FolderOpen, Maximize2, Minus, Plus } from "lucide-react";

import { shortcut } from "../platform";
import { Button } from "./Button";

interface ToolbarProps {
  name: string;
  language: string | null;
  pageCount: number;
  currentPage: number;
  scale: number;
  fitting: boolean;
  dirty: boolean;
  onOpen: () => void;
  onZoom: (direction: 1 | -1) => void;
  onFit: () => void;
  onSave: () => void;
}

export function Toolbar(props: ToolbarProps) {
  const { name, language, pageCount, currentPage, scale, fitting, dirty } = props;
  return (
    <header className="toolbar">
      <div className="toolbar-title">
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
          icon={<FolderOpen size={16} />}
          aria-label="Open"
          title={`Open a PDF (${shortcut("O")})`}
          onClick={props.onOpen}
        />
        <Button variant="primary" title={`Save the review (${shortcut("S")})`} onClick={props.onSave}>
          Save Review
        </Button>
      </div>
    </header>
  );
}
