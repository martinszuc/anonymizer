import { EyeOff, Info } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, type KeyboardEvent } from "react";

import { gentle } from "../motion";
import { covers, groupByType, isIdentifier, isRedacted, summarize } from "../review";
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
}

export function Sidebar({ document, tab, selectedId, onTab, onSelect, onToggle }: SidebarProps) {
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
        <Findings document={document} selectedId={selectedId} onSelect={onSelect} onToggle={onToggle} />
      ) : (
        <HiddenItems surfaces={document.surfaces} />
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
}

function Findings({ document, selectedId, onSelect, onToggle }: FindingsProps) {
  const groups = useMemo(() => groupByType(document.entities), [document.entities]);
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
    else if (event.key === " " && ordered[index]) onToggle(ordered[index]);
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
              selected={entity.id === selectedId}
              onSelect={onSelect}
              onToggle={onToggle}
            />
          ))}
        </section>
      ))}
    </div>
  );
}

interface EntityRowProps {
  entity: EntityInfo;
  selected: boolean;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
}

function EntityRow({ entity, selected, onSelect, onToggle }: EntityRowProps) {
  const redacted = isRedacted(entity.review);
  const text = covers(entity);
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
        data-visible={entity.review === "pending"}
        role="img"
        aria-label={entity.review === "pending" ? "Not reviewed" : undefined}
        aria-hidden={entity.review !== "pending"}
      />
      <div className="row-body">
        <span className={isIdentifier(entity.type) ? "row-text mono" : "row-text"} title={text}>
          {text}
        </span>
        <span className="row-meta">{rowMeta(entity)}</span>
      </div>
      <Switch
        checked={redacted}
        label={redacted ? `Redacted: click to keep “${text}”` : `Kept: click to redact “${text}”`}
        onChange={() => onToggle(entity)}
      />
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

function HiddenItems({ surfaces }: { surfaces: SurfaceInfo[] }) {
  const groups = useMemo(() => {
    const byKind = new Map<string, SurfaceInfo[]>();
    for (const surface of surfaces) byKind.set(surface.kind, [...(byKind.get(surface.kind) ?? []), surface]);
    return [...byKind.entries()];
  }, [surfaces]);

  return (
    <div className="list">
      <p className="notice">
        <Info size={14} aria-hidden />
        <span>
          Data outside the visible text. All of it is removed on export, whether or not anything
          personal was found in it.
        </span>
      </p>
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
          {members.map((surface) => (
            <div key={surface.id} className="row row-static">
              <div className="row-body">
                <span className="row-text mono clamp" title={surface.value}>
                  {preview(surface.value)}
                </span>
                <span className="row-meta">
                  {surface.page_index === null ? "Whole document" : `Page ${surface.page_index + 1}`}
                </span>
              </div>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}

function preview(value: string): string {
  const flat = value.replace(/\s+/g, " ").trim();
  return flat.length > PREVIEW_LENGTH ? `${flat.slice(0, PREVIEW_LENGTH - 1)}…` : flat;
}
