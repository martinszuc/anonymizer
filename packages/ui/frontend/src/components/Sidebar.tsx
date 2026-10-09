import { ArrowDownUp, ChevronDown, ChevronRight, EyeOff, Info, ListFilter, Lock, Paperclip, Search, TextSelect, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState, type KeyboardEvent, type ReactNode } from "react";

import { gentle } from "../motion";
import {
  NO_FILTER,
  SCORE_STEPS,
  SORT_ORDERS,
  activeFilters,
  covers,
  findingSections,
  groupDecision,
  isDecidable,
  isIdentifier,
  isRemoved,
  keepable,
  lowConfidence,
  pagesLabel,
  regionNumbers,
  reviewProgress,
  scoreRange,
  sortedBy,
  summarize,
  truncated,
  typeLabel,
  type DecisionFilter,
  type FindingFilter,
  type FindingRow,
  type FindingSection,
  type GroupDecision,
  type ListView,
  type SortOrder,
  type SourceFilter,
} from "../review";
import type { DocumentInfo, EntityInfo, SurfaceInfo } from "../types";
import { Button } from "./Button";
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
  /** One decision for every member of a group of identical findings. */
  onToggleGroup: (members: EntityInfo[]) => void;
  /** Keep every finding given: the undecided ones the list shows. */
  onKeep: (entities: EntityInfo[]) => void;
  /** Order, sections and filter of the findings list. */
  view: ListView;
  onView: (view: ListView) => void;
  onRemove: (entity: EntityInfo) => void;
  selectedSurfaceId: string | null;
  onSelectSurface: (surface: SurfaceInfo) => void;
  /** Select the next undecided finding in the list's order. */
  onNext: () => void;
}

export function Sidebar({
  document,
  tab,
  selectedId,
  onTab,
  onSelect,
  onToggle,
  onToggleGroup,
  onKeep,
  onRemove,
  selectedSurfaceId,
  onSelectSurface,
  view,
  onView,
  onNext,
}: SidebarProps) {
  const sections = useMemo(() => findingSections(document.entities, view), [document.entities, view]);
  return (
    <aside className="sidebar" aria-label="Review">
      <ReviewStatus document={document} onNext={onNext} />
      <SegmentedControl
        name="sidebar"
        value={tab}
        onChange={onTab}
        segments={[
          { value: "findings", label: "Findings", count: document.entities.length },
          { value: "hidden", label: "Hidden", count: document.surfaces.length },
        ]}
      />
      {tab === "findings" && (
        <ListTools entities={document.entities} sections={sections} view={view} onView={onView} onKeep={onKeep} />
      )}
      {tab === "findings" ? (
        <Findings
          document={document}
          sections={sections}
          filtering={activeFilters(view.filter) > 0}
          onClearFilters={() => onView({ ...view, filter: NO_FILTER })}
          selectedId={selectedId}
          onSelect={onSelect}
          onToggle={onToggle}
          onToggleGroup={onToggleGroup}
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
      {tab === "findings" && document.entities.length > 0 && (
        <p className="list-footer">
          <TextSelect size={13} aria-hidden />
          To add a missed word, drag across it on the page.
        </p>
      )}
    </aside>
  );
}

/**
 * How far the review is (findings with a decision, of those that take one), with a way to
 * the next undecided one, over what export will do: redacted, kept, hidden items removed.
 */
function ReviewStatus({ document, onNext }: { document: DocumentInfo; onNext: () => void }) {
  const summary = summarize(document);
  const { decided, total } = reviewProgress(document.entities);
  const left = total - decided;
  return (
    <section className="review-status" aria-label="Review progress">
      <div className="review-status-line">
        <span className="review-status-title">
          {total === 0 ? "Nothing to decide" : left === 0 ? "All decided" : `${decided} of ${total} decided`}
        </span>
        {left > 0 && (
          <button type="button" className="link-button" title="Select the next undecided finding (N)" onClick={onNext}>
            Next undecided
          </button>
        )}
      </div>
      <div
        className="progress-track"
        data-size="thin"
        role="progressbar"
        aria-label="Findings decided"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={decided}
      >
        <div className="progress-fill" style={{ width: `${total === 0 ? 100 : (100 * decided) / total}%` }} />
      </div>
      <div className="summary" aria-live="polite">
        <SummaryFigure value={summary.redacted} label="redacted" tone="ink" />
        <SummaryFigure value={summary.kept} label="kept" tone="keep" />
        <SummaryFigure value={summary.hidden} label="hidden removed" tone="muted" />
      </div>
    </section>
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

/** The score step the hint above the list offers when nothing is filtered. */
const HINT_SCORE = 0.5;

const DECISIONS: { value: DecisionFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "undecided", label: "Undecided" },
  { value: "redacted", label: "Redacted" },
  { value: "kept", label: "Kept" },
];

const SOURCES: { value: SourceFilter; label: string }[] = [
  { value: "rule", label: "Rules" },
  { value: "model", label: "Model" },
  { value: "propagated", label: "Repeats" },
  { value: "manual", label: "Added" },
];

type ScoreStep = "any" | `${(typeof SCORE_STEPS)[number]}`;

interface ListToolsProps {
  entities: EntityInfo[];
  sections: FindingSection[];
  view: ListView;
  onView: (view: ListView) => void;
  onKeep: (entities: EntityInfo[]) => void;
}

/**
 * Search, order and filter for the findings list. While anything is filtered, a
 * strip keeps the undecided findings shown in one go, so a bulk decision covers
 * exactly what the reviewer sees.
 */
function ListTools({ entities, sections, view, onView, onKeep }: ListToolsProps) {
  const [open, setOpen] = useState(false);
  const { filter } = view;
  const active = activeFilters(filter);
  const shown = sections.reduce((count, section) => count + section.rows.reduce((n, row) => n + row.members.length, 0), 0);
  const keep = keepable(sections);
  const uncertain = useMemo(() => lowConfidence(entities, HINT_SCORE).length, [entities]);
  const setFilter = (changes: Partial<FindingFilter>) => onView({ ...view, filter: { ...filter, ...changes } });
  const toggleSource = (source: SourceFilter) =>
    setFilter({
      sources: filter.sources.includes(source)
        ? filter.sources.filter((item) => item !== source)
        : [...filter.sources, source],
    });

  return (
    <section className="list-tools" aria-label="Search, sort and filter findings">
      <label className="search-field">
        <Search size={14} aria-hidden />
        <input
          type="search"
          placeholder="Search findings"
          aria-label="Search findings"
          value={filter.text}
          onChange={(event) => setFilter({ text: event.target.value })}
          onKeyDown={(event) => {
            if (event.key === "Escape" && filter.text) {
              event.stopPropagation();
              setFilter({ text: "" });
            }
          }}
        />
        {filter.text && (
          <button type="button" className="search-clear" aria-label="Clear the search" onClick={() => setFilter({ text: "" })}>
            <X size={12} />
          </button>
        )}
      </label>
      <div className="list-tools-line">
        <label className="sort-field" title="Order of the list">
          <ArrowDownUp size={14} aria-hidden />
          <select
            aria-label="Sort findings"
            value={view.sort}
            onChange={(event) => onView(sortedBy(view, event.target.value as SortOrder))}
          >
            {SORT_ORDERS.map((order) => (
              <option key={order.value} value={order.value}>
                {order.label}
              </option>
            ))}
          </select>
          <ChevronDown size={12} aria-hidden />
        </label>
        <button
          type="button"
          className="filter-toggle"
          aria-expanded={open}
          aria-controls="finding-filters"
          data-active={active > 0}
          onClick={() => setOpen((value) => !value)}
        >
          <ListFilter size={14} aria-hidden />
          Filter
          {active > 0 && <span className="filter-count">{active}</span>}
        </button>
        <span className="list-tools-count" aria-live="polite">
          {active > 0 ? `${shown} of ${entities.length}` : entities.length}
        </span>
      </div>
      {open && (
        <div id="finding-filters" className="filter-panel">
          <FilterGroup label="Decision">
            <SegmentedControl
              name="decision"
              value={filter.decision}
              onChange={(decision) => setFilter({ decision })}
              segments={DECISIONS}
            />
          </FilterGroup>
          <FilterGroup label="Found by">
            <div className="chips">
              {SOURCES.map((source) => (
                <button
                  key={source.value}
                  type="button"
                  className="chip"
                  aria-pressed={filter.sources.includes(source.value)}
                  onClick={() => toggleSource(source.value)}
                >
                  {source.label}
                </button>
              ))}
            </div>
          </FilterGroup>
          <FilterGroup label="Model score below">
            <SegmentedControl
              name="score-below"
              value={(filter.scoreBelow === null ? "any" : `${filter.scoreBelow}`) as ScoreStep}
              onChange={(step) => setFilter({ scoreBelow: step === "any" ? null : Number(step) })}
              segments={[
                { value: "any" as ScoreStep, label: "Any" },
                ...SCORE_STEPS.map((step) => ({ value: `${step}` as ScoreStep, label: `${Math.round(step * 100)} %` })),
              ]}
            />
          </FilterGroup>
          <label className="check-row" data-disabled={view.sort === "type"}>
            <input
              type="checkbox"
              checked={view.byType || view.sort === "type"}
              disabled={view.sort === "type"}
              onChange={(event) => onView({ ...view, byType: event.target.checked })}
            />
            Sections by type
          </label>
        </div>
      )}
      {active === 0 && uncertain > 0 && (
        <p className="list-hint">
          <span>
            <span className="list-hint-count">{uncertain}</span> {uncertain === 1 ? "finding" : "findings"} scored
            below {Math.round(HINT_SCORE * 100)} %
          </span>
          <button type="button" className="link-button" onClick={() => setFilter({ scoreBelow: HINT_SCORE })}>
            Show them
          </button>
        </p>
      )}
      {active > 0 && (
        <div className="list-actions">
          <Button
            disabled={keep.length === 0}
            title="Keep the undecided findings shown; decisions you made stay as they are"
            onClick={() => onKeep(keep)}
          >
            {keep.length > 0 ? `Keep ${keep.length}` : "Nothing to keep"}
          </Button>
          <Button variant="plain" onClick={() => onView({ ...view, filter: NO_FILTER })}>
            Clear filters
          </Button>
        </div>
      )}
    </section>
  );
}

function FilterGroup({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="filter-group" role="group" aria-label={label}>
      <span className="filter-label">{label}</span>
      {children}
    </div>
  );
}

interface FindingsProps {
  document: DocumentInfo;
  /** The list as the view shows it (see `findingSections`). */
  sections: FindingSection[];
  filtering: boolean;
  onClearFilters: () => void;
  selectedId: string | null;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onToggleGroup: (members: EntityInfo[]) => void;
  onRemove: (entity: EntityInfo) => void;
}

/** A row of the list: one finding, or the head of a group of identical ones. */
type ListRow = { kind: "entity"; entity: EntityInfo } | { kind: "group"; group: FindingRow };

function Findings({
  document,
  sections,
  filtering,
  onClearFilters,
  selectedId,
  onSelect,
  onToggle,
  onToggleGroup,
  onRemove,
}: FindingsProps) {
  const numbers = useMemo(() => regionNumbers(document.entities), [document.entities]);
  // Groups of repeats are collapsed until opened, so a word found 30 times is one row.
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const listRef = useRef<HTMLDivElement>(null);

  const rows: ListRow[] = sections.flatMap((section) =>
    section.rows.flatMap((found): ListRow[] => {
      const [only] = found.members;
      if (found.members.length === 1 && only) return [{ kind: "entity", entity: only }];
      const head: ListRow = { kind: "group", group: found };
      if (!expanded.has(found.key)) return [head];
      return [head, ...found.members.map((entity): ListRow => ({ kind: "entity", entity }))];
    }),
  );
  const holds = (row: ListRow) =>
    selectedId !== null &&
    (row.kind === "entity"
      ? row.entity.id === selectedId
      : !expanded.has(row.group.key) && row.group.members.some((member) => member.id === selectedId));

  useEffect(() => {
    if (!selectedId) return;
    const list = listRef.current;
    const id = CSS.escape(selectedId);
    // A finding inside a closed group is shown by its group's row.
    (list?.querySelector(`[data-entity-id="${id}"]`) ?? list?.querySelector(`[data-entity-ids~="${id}"]`))
      ?.scrollIntoView({ block: "nearest" });
  }, [selectedId]);

  if (rows.length === 0) {
    return filtering ? (
      <div className="sidebar-empty">
        <p>No findings match.</p>
        <Button variant="plain" onClick={onClearFilters}>
          Clear filters
        </Button>
      </div>
    ) : (
      <div className="sidebar-empty">
        <p>Nothing was found in the text.</p>
        <p className="muted">Hidden items are still removed on export.</p>
        <p className="muted">Missed something? Select its words on the page to add it.</p>
      </div>
    );
  }

  const setOpen = (key: string, open: boolean) =>
    setExpanded((current) => {
      const next = new Set(current);
      if (open) next.add(key);
      else next.delete(key);
      return next;
    });

  const onKeyDown = (event: KeyboardEvent) => {
    const index = rows.findIndex(holds);
    const current = rows[index];
    const move = (offset: number) => {
      const next = rows[Math.min(Math.max(index + offset, 0), rows.length - 1)];
      if (next) onSelect(next.kind === "entity" ? next.entity : (next.group.members[0] as EntityInfo));
    };
    if (event.key === "ArrowDown") move(1);
    else if (event.key === "ArrowUp") move(-1);
    else if (event.key === "ArrowRight" && current?.kind === "group") setOpen(current.group.key, true);
    else if (event.key === "ArrowLeft" && current?.kind === "group") setOpen(current.group.key, false);
    // Delete on a selected region is handled window-wide, in App.
    else if (event.key === " " && current?.kind === "group" && current.group.members.some(isDecidable)) {
      onToggleGroup(current.group.members);
    } else if (event.key === " " && current?.kind === "entity" && isDecidable(current.entity)) {
      onToggle(current.entity);
    } else return;
    event.preventDefault();
  };

  const active = rows.find(holds);
  return (
    <div
      ref={listRef}
      className="list"
      role="listbox"
      aria-label="Findings"
      aria-activedescendant={
        active === undefined
          ? undefined
          : active.kind === "entity"
            ? `row-${active.entity.id}`
            : `group-${active.group.members[0]?.id}`
      }
      tabIndex={0}
      onKeyDown={onKeyDown}
    >
      <div className="list-columns" aria-hidden>
        <span>Found</span>
        <span>Redact</span>
      </div>
      {sections.map((section) => (
        <section
          key={section.type ?? "all"}
          className="group"
          data-type={section.type ?? undefined}
          aria-label={section.label}
        >
          {section.type !== null && (
            <h2 className="group-header">
              <span className="dot" aria-hidden />
              {section.label}
              <span className="group-count">{section.rows.reduce((count, row) => count + row.members.length, 0)}</span>
            </h2>
          )}
          {section.rows.map((found) => {
            const [only] = found.members;
            if (found.members.length === 1 && only) {
              return (
                <EntityRow
                  key={only.id}
                  entity={only}
                  regionNumber={numbers.get(only.id)}
                  showType={section.type === null}
                  selected={only.id === selectedId}
                  onSelect={onSelect}
                  onToggle={onToggle}
                  onRemove={onRemove}
                />
              );
            }
            const open = expanded.has(found.key);
            return (
              <div key={found.key} className="occurrences" data-open={open}>
                <GroupRow
                  group={found}
                  open={open}
                  showType={section.type === null}
                  selected={holds({ kind: "group", group: found })}
                  selectedId={selectedId}
                  onOpen={(value) => setOpen(found.key, value)}
                  onSelect={onSelect}
                  onToggleGroup={onToggleGroup}
                />
                {open &&
                  found.members.map((entity) => (
                    <EntityRow
                      key={entity.id}
                      entity={entity}
                      regionNumber={undefined}
                      showType={false}
                      selected={entity.id === selectedId}
                      onSelect={onSelect}
                      onToggle={onToggle}
                      onRemove={onRemove}
                    />
                  ))}
              </div>
            );
          })}
        </section>
      ))}
    </div>
  );
}

interface GroupRowProps {
  group: FindingRow;
  open: boolean;
  /** In a list without sections by type, the meta line names the type. */
  showType: boolean;
  selected: boolean;
  selectedId: string | null;
  onOpen: (open: boolean) => void;
  onSelect: (entity: EntityInfo) => void;
  onToggleGroup: (members: EntityInfo[]) => void;
}

/** Identical findings in one row: how often and where, one switch for all of them. */
function GroupRow({ group, open, showType, selected, selectedId, onOpen, onSelect, onToggleGroup }: GroupRowProps) {
  const { members } = group;
  const first = members[0] as EntityInfo;
  const decision = groupDecision(members);
  const decidable = members.some(isDecidable);
  const unreviewed = members.some((member) => member.review === "pending" && isDecidable(member));
  const text = covers(first);
  // Each click goes to the next occurrence, so the page shows them one by one.
  const current = members.findIndex((member) => member.id === selectedId);
  const next = members[(current + 1) % members.length] ?? first;
  return (
    <div
      id={`group-${first.id}`}
      role="option"
      aria-selected={selected}
      aria-expanded={open}
      className="row row-group"
      data-entity-ids={members.map((member) => member.id).join(" ")}
      data-selected={selected}
      data-redacted={decision !== "kept"}
      title="Click again to go to the next occurrence"
      onClick={() => onSelect(next)}
    >
      <span
        className="row-pending"
        data-visible={unreviewed}
        role="img"
        aria-label={unreviewed ? "Not all reviewed" : undefined}
        aria-hidden={!unreviewed}
      />
      <button
        type="button"
        className="row-disclosure"
        aria-label={open ? "Hide each occurrence" : "Show each occurrence"}
        tabIndex={-1}
        onClick={(event) => {
          event.stopPropagation();
          onOpen(!open);
        }}
      >
        <ChevronRight size={14} aria-hidden />
      </button>
      <div className="row-body">
        <span className={isIdentifier(first.type) ? "row-text mono" : "row-text"} title={text}>
          {text}
          <span className="row-times">×{members.length}</span>
        </span>
        <span className="row-meta">{groupMeta(members, decision, showType)}</span>
      </div>
      {decidable ? (
        <Switch
          checked={decision === "redacted"}
          mixed={decision === "mixed"}
          label={
            decision === "redacted"
              ? `Redacted ${members.length} times: click to keep every “${text}”`
              : `Click to redact every “${text}” (${members.length} times)`
          }
          onChange={() => onToggleGroup(members)}
        />
      ) : (
        <span className="row-locked" title="In hidden data: export removes it with the hidden item">
          <Lock size={12} aria-hidden />
          Always removed
        </span>
      )}
    </div>
  );
}

function groupMeta(members: EntityInfo[], decision: GroupDecision, showType: boolean): string {
  const pages = [...new Set(members.flatMap((member) => (member.page_index === null ? [] : [member.page_index + 1])))];
  const places = pages.length > 0 ? pagesLabel(pages.sort((a, b) => a - b)) : "Document info";
  const parts = showType ? [typeLabel((members[0] as EntityInfo).type), places] : [places];
  const scores = scoreRange(members);
  if (scores) parts.push(scores);
  if (decision === "mixed") {
    const kept = members.filter((member) => !isRemoved(member)).length;
    parts.push(`${kept} kept`);
  }
  return parts.join(" · ");
}

interface EntityRowProps {
  entity: EntityInfo;
  regionNumber: number | undefined;
  /** In a list without sections by type, the meta line names the type. */
  showType: boolean;
  selected: boolean;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onRemove: (entity: EntityInfo) => void;
}

function EntityRow({ entity, regionNumber, showType, selected, onSelect, onToggle, onRemove }: EntityRowProps) {
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
        <span className="row-meta">{rowMeta(entity, showType)}</span>
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
        <>
          {entity.source === "manual" && (
            <button
              type="button"
              className="row-remove"
              data-quiet
              aria-label={`Remove “${text}”, added by you, on page ${(entity.page_index ?? 0) + 1}`}
              title="Remove what you added, with its repeats (Delete)"
              tabIndex={-1}
              onClick={(event) => {
                event.stopPropagation();
                onRemove(entity);
              }}
            >
              <X size={14} />
            </button>
          )}
          <Switch
            checked={redacted}
            label={redacted ? `Redacted: click to keep “${text}”` : `Kept: click to redact “${text}”`}
            onChange={() => onToggle(entity)}
          />
        </>
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

function rowMeta(entity: EntityInfo, showType: boolean): string {
  const place = entity.page_index === null ? "Document info" : `Page ${entity.page_index + 1}`;
  const parts = [place, SOURCE_LABELS[entity.source] ?? entity.source];
  if (showType) parts.unshift(typeLabel(entity.type));
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
  return truncated(value.replace(/\s+/g, " ").trim(), PREVIEW_LENGTH);
}
