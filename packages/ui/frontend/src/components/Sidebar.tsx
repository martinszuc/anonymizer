import { EyeOff, Info, Lock, Paperclip, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, type KeyboardEvent } from "react";

import { gentle } from "../motion";
import {
  covers,
  groupByType,
  isDecidable,
  isIdentifier,
  isRemoved,
  regionNumbers,
  summarize,
  typeLabel,
} from "../review";
import type { DocumentInfo, EntityInfo, SurfaceInfo } from "../types";
import { SegmentedControl } from "./SegmentedControl";
import { Switch } from "./Switch";

export type SidebarTab = "findings" | "hidden";

interface SidebarProps {
  document: DocumentInfo;
  tab: SidebarTab;
  selectedId: string | null;
  onTab: (tab: SidebarTab) => void;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onRemove: (entity: EntityInfo) => void;
  selectedSurfaceId: string | null;
  onSelectSurface: (surface: SurfaceInfo) => void;
}

export function Sidebar({
  document,
  tab,
  selectedId,
  onTab,
  onSelect,
  onToggle,
  onRemove,
  selectedSurfaceId,
  onSelectSurface,
}: SidebarProps) {
  const summary = summarize(document);
  return (
    <aside className="sidebar" aria-label="Review">
      <div className="summary" aria-live="polite">
        <SummaryFigure value={summary.redacted} label="redacted" tone="ink" />
        <SummaryFigure value={summary.kept} label="kept" tone="keep" />
        <SummaryFigure value={summary.hidden} label="hidden" tone="muted" />
      </div>
      <SegmentedControl
        name="sidebar"
        value={tab}
        onChange={onTab}
        segments={[
          { value: "findings", label: "Findings", count: document.entities.length },
          { value: "hidden", label: "Hidden", count: document.surfaces.length },
        ]}
      />
      {tab === "findings" ? (
        <Findings
          document={document}
          selectedId={selectedId}
          onSelect={onSelect}
          onToggle={onToggle}
          onRemove={onRemove}
        />
      ) : (
        <HiddenItems
          surfaces={document.surfaces}
          entities={document.entities}
          selectedSurfaceId={selectedSurfaceId}
          onSelectSurface={onSelectSurface}
        />
      )}
    </aside>
  );
}

function SummaryFigure({ value, label, tone }: { value: number; label: string; tone: string }) {
  return (
    <div className="summary-figure" data-tone={tone}>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={value}
          className="summary-value"
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 6 }}
          transition={gentle}
        >
          {value}
        </motion.span>
      </AnimatePresence>
      <span className="summary-label">{label}</span>
    </div>
  );
}

interface FindingsProps {
  document: DocumentInfo;
  selectedId: string | null;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onRemove: (entity: EntityInfo) => void;
}

function Findings({ document, selectedId, onSelect, onToggle, onRemove }: FindingsProps) {
  const groups = useMemo(() => groupByType(document.entities), [document.entities]);
  const numbers = useMemo(() => regionNumbers(document.entities), [document.entities]);
  const ordered = groups.flatMap((group) => group.entities);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedId) return;
    listRef.current
      ?.querySelector(`[data-entity-id="${CSS.escape(selectedId)}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [selectedId]);

  if (ordered.length === 0) {
    return (
      <div className="sidebar-empty">
        <p>Nothing was found in the text.</p>
        <p className="muted">Hidden items are still removed on export.</p>
      </div>
    );
  }

  const onKeyDown = (event: KeyboardEvent) => {
    const index = ordered.findIndex((entity) => entity.id === selectedId);
    const move = (offset: number) => {
      const next = ordered[Math.min(Math.max(index + offset, 0), ordered.length - 1)];
      if (next) onSelect(next);
    };
    if (event.key === "ArrowDown") move(1);
    else if (event.key === "ArrowUp") move(-1);
    // Delete on a selected region is handled window-wide, in App.
    else if (event.key === " " && ordered[index] && isDecidable(ordered[index])) onToggle(ordered[index]);
    else return;
    event.preventDefault();
  };

  return (
    <div
      ref={listRef}
      className="list"
      role="listbox"
      aria-label="Findings"
      aria-activedescendant={selectedId ? `row-${selectedId}` : undefined}
      tabIndex={0}
      onKeyDown={onKeyDown}
    >
      <div className="list-columns" aria-hidden>
        <span>Found</span>
        <span>Redact</span>
      </div>
      {groups.map((group) => (
        <section key={group.type} className="group" data-type={group.type} aria-label={group.label}>
          <h2 className="group-header">
            <span className="dot" aria-hidden />
            {group.label}
            <span className="group-count">{group.entities.length}</span>
          </h2>
          {group.entities.map((entity) => (
            <EntityRow
              key={entity.id}
              entity={entity}
              regionNumber={numbers.get(entity.id)}
              selected={entity.id === selectedId}
              onSelect={onSelect}
              onToggle={onToggle}
              onRemove={onRemove}
            />
          ))}
        </section>
      ))}
    </div>
  );
}

interface EntityRowProps {
  entity: EntityInfo;
  regionNumber: number | undefined;
  selected: boolean;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onRemove: (entity: EntityInfo) => void;
}

function EntityRow({ entity, regionNumber, selected, onSelect, onToggle, onRemove }: EntityRowProps) {
  const redacted = isRemoved(entity);
  // Only something the reviewer can decide on waits for review.
  const unreviewed = entity.review === "pending" && isDecidable(entity);
  const text = covers(entity, regionNumber);
  return (
    <div
      id={`row-${entity.id}`}
      role="option"
      aria-selected={selected}
      className="row"
      data-entity-id={entity.id}
      data-selected={selected}
      data-redacted={redacted}
      onClick={() => onSelect(entity)}
    >
      <span
        className="row-pending"
        data-visible={unreviewed}
        role="img"
        aria-label={unreviewed ? "Not reviewed" : undefined}
        aria-hidden={!unreviewed}
      />
      <div className="row-body">
        <span className={isIdentifier(entity.type) ? "row-text mono" : "row-text"} title={text}>
          {text}
        </span>
        <span className="row-meta">{rowMeta(entity)}</span>
      </div>
      {entity.surface_id !== null ? (
        <span
          className="row-locked"
          title="In hidden data (a link, metadata, a note...): export removes it with the hidden item, so there is nothing to decide"
        >
          <Lock size={12} aria-hidden />
          Always removed
        </span>
      ) : entity.is_region ? (
        <button
          type="button"
          className="row-remove"
          aria-label={`Remove ${text.toLowerCase()} on page ${(entity.page_index ?? 0) + 1}`}
          title="Remove region (Delete)"
          tabIndex={-1}
          onClick={(event) => {
            event.stopPropagation();
            onRemove(entity);
          }}
        >
          <X size={14} />
        </button>
      ) : (
        <Switch
          checked={redacted}
          label={redacted ? `Redacted: click to keep “${text}”` : `Kept: click to redact “${text}”`}
          onChange={() => onToggle(entity)}
        />
      )}
    </div>
  );
}

const SOURCE_LABELS: Record<string, string> = {
  rule: "Rule",
  model: "Model",
  manual: "Added",
  propagated: "Repeat",
};

function rowMeta(entity: EntityInfo): string {
  const place = entity.page_index === null ? "Document info" : `Page ${entity.page_index + 1}`;
  const parts = [place, SOURCE_LABELS[entity.source] ?? entity.source];
  if (entity.score !== null) parts.push(`${Math.round(entity.score * 100)} %`);
  if (entity.surface_id) parts.push("hidden");
  return parts.join(" · ");
}

const SURFACE_LABELS: Record<string, string> = {
  metadata: "Document info",
  xmp: "XMP metadata",
  link: "Links",
  annotation: "Comments and notes",
  form_field: "Form fields",
  bookmark: "Bookmarks",
  embedded_file: "Attached files",
  structure: "Accessibility tags",
};

const PREVIEW_LENGTH = 160;

/** What each kind is and what export does with it, in one line. */
const SURFACE_NOTES: Record<string, string> = {
  metadata: "Title, author, subject and keywords. Cleared.",
  xmp: "A second, XML copy of the document info. Removed.",
  link: "Where links point. Links to other pages of this file stay; the rest are removed.",
  annotation: "Comments, notes and their authors. Removed.",
  form_field: "Values typed into form fields. Removed.",
  bookmark: "The outline in a viewer's sidebar. Removed.",
  embedded_file: "Names of attached files; their contents are never opened. Removed.",
  structure: "Text read aloud by screen readers. Removed, with the accessibility tags.",
};

interface HiddenItemsProps {
  surfaces: SurfaceInfo[];
  entities: EntityInfo[];
  selectedSurfaceId: string | null;
  onSelectSurface: (surface: SurfaceInfo) => void;
}

function HiddenItems({ surfaces, entities, selectedSurfaceId, onSelectSurface }: HiddenItemsProps) {
  const groups = useMemo(() => {
    const byKind = new Map<string, SurfaceInfo[]>();
    for (const surface of surfaces) byKind.set(surface.kind, [...(byKind.get(surface.kind) ?? []), surface]);
    return [...byKind.entries()];
  }, [surfaces]);
  const foundIn = useMemo(() => {
    const types = new Map<string, Set<string>>();
    for (const entity of entities) {
      if (entity.surface_id === null) continue;
      types.set(entity.surface_id, (types.get(entity.surface_id) ?? new Set()).add(entity.type));
    }
    return types;
  }, [entities]);
  const hasAttachments = surfaces.some((surface) => surface.kind === "embedded_file");

  return (
    <div className="list">
      <p className="notice">
        <Info size={14} aria-hidden />
        <span>
          Data outside the visible text. All of it is removed on export, whether or not anything
          personal was found in it, so there is nothing to decide here.
        </span>
      </p>
      {hasAttachments && (
        <p className="notice" data-tone="warning">
          <Paperclip size={14} aria-hidden />
          <span>
            This file has attachments. Their contents are never opened or checked; they are
            removed on export.
          </span>
        </p>
      )}
      {groups.length === 0 && (
        <div className="sidebar-empty">
          <EyeOff size={20} aria-hidden />
          <p>No hidden items in this file.</p>
        </div>
      )}
      {groups.map(([kind, members]) => (
        <section key={kind} className="group" aria-label={SURFACE_LABELS[kind] ?? kind}>
          <h2 className="group-header">
            {SURFACE_LABELS[kind] ?? kind}
            <span className="group-count">{members.length}</span>
          </h2>
          {SURFACE_NOTES[kind] && <p className="group-note">{SURFACE_NOTES[kind]}</p>}
          {members.map((surface) => (
            <HiddenRow
              key={surface.id}
              surface={surface}
              found={[...(foundIn.get(surface.id) ?? [])]}
              selected={surface.id === selectedSurfaceId}
              onSelect={onSelectSurface}
            />
          ))}
        </section>
      ))}
    </div>
  );
}

interface HiddenRowProps {
  surface: SurfaceInfo;
  found: string[];
  selected: boolean;
  onSelect: (surface: SurfaceInfo) => void;
}

function HiddenRow({ surface, found, selected, onSelect }: HiddenRowProps) {
  const onPage = surface.page_index !== null;
  const place = onPage ? `Page ${(surface.page_index ?? 0) + 1}` : "Whole document";
  return (
    <div
      className={onPage ? "row" : "row row-static"}
      data-selected={selected}
      title={onPage ? "Show where it is on the page" : undefined}
      onClick={onPage ? () => onSelect(surface) : undefined}
    >
      <div className="row-body">
        <span className="row-text mono clamp" title={surface.value}>
          {preview(surface.value)}
        </span>
        <span className="row-meta">
          {place}
          {found.length > 0 && ` · contains ${found.map((type) => typeLabel(type).toLowerCase()).join(", ")}`}
        </span>
      </div>
    </div>
  );
}

function preview(value: string): string {
  const flat = value.replace(/\s+/g, " ").trim();
  return flat.length > PREVIEW_LENGTH ? `${flat.slice(0, PREVIEW_LENGTH - 1)}…` : flat;
}
