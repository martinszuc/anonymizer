import { ScanText, TriangleAlert } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import {
  forwardRef,
  useEffect,
  useRef,
  useState,
  type MouseEvent,
  type PointerEvent,
  type RefObject,
  type UIEvent,
} from "react";

import { errorMessage } from "../bridge";
import { gentle } from "../motion";
import type { PageImages } from "../pageImages";
import type { PageWords } from "../pageWords";
import {
  covers,
  dragBox,
  isDecidable,
  isLargeEnough,
  isRemoved,
  isUnreadScan,
  regionNumbers,
  renderDpi,
  typeLabel,
} from "../review";
import { lineBoxes, nearestWord, wordAt, wordRange, type Point } from "../selection";
import type { Box, DocumentInfo, EntityInfo, PageInfo, SurfaceInfo, WordInfo } from "../types";
import { AddFindingPopover } from "./AddFinding";

/** Words selected on a page, waiting for the reviewer to add them as a finding. */
export interface WordSelection {
  pageIndex: number;
  words: WordInfo[];
}

/** How far the pointer moves, in screen pixels, before a press on a word becomes a selection. */
const SELECT_THRESHOLD = 4;

interface PageViewProps {
  document: DocumentInfo;
  images: PageImages;
  words: PageWords;
  scale: number;
  selectedId: string | null;
  /** The hidden item chosen in the Hidden tab, outlined on its page. */
  selectedSurfaceId: string | null;
  showHidden: boolean;
  previewing: boolean;
  /** The region tool is on (or Alt is held): a drag draws a region. */
  drawing: boolean;
  /** A click on a box only selects it; otherwise it also changes the decision. */
  locating: boolean;
  /** Findings the list's filter shows; the others are dimmed. Null when nothing is filtered. */
  shownIds: Set<string> | null;
  /** Words selected to add as a finding, shown with the popover that adds them. */
  selection: WordSelection | null;
  /** Adding the selection is under way. */
  adding: boolean;
  onSelect: (entity: EntityInfo) => void;
  onDrawRegion: (pageIndex: number, box: Box) => void;
  /** Words were selected on a page, or the selection was dropped (null). */
  onSelectWords: (selection: WordSelection | null) => void;
  onAddFinding: (type: string) => void;
  onToggle: (entity: EntityInfo) => void;
  onError: (message: string) => void;
  onCurrentPage: (index: number) => void;
}

/** Every page of the document, stacked, with its proposed redactions drawn over it. */
export const PageView = forwardRef<HTMLDivElement, PageViewProps>(function PageView(props, ref) {
  const { document, previewing, drawing, onCurrentPage } = props;
  const numbers = regionNumbers(document.entities);

  const onScroll = (event: UIEvent<HTMLDivElement>) => {
    const scroller = event.currentTarget;
    const middle = scroller.scrollTop + scroller.clientHeight / 2;
    const pages = scroller.querySelectorAll<HTMLElement>("[data-page-index]");
    for (const page of pages) {
      if (page.offsetTop + page.offsetHeight >= middle) {
        onCurrentPage(Number(page.dataset.pageIndex));
        return;
      }
    }
  };

  return (
    <main
      ref={ref}
      className="canvas"
      data-previewing={previewing}
      data-drawing={drawing}
      onScroll={onScroll}
      aria-label="Pages"
    >
      {document.pages.map((page) => (
        <Page
          key={page.index}
          page={page}
          entities={document.entities.filter((entity) => entity.page_index === page.index && entity.boxes.length > 0)}
          surfaces={document.surfaces.filter((surface) => surface.page_index === page.index && surface.box)}
          regionNumbers={numbers}
          {...props}
        />
      ))}
    </main>
  );
});

interface PageProps extends PageViewProps {
  page: PageInfo;
  entities: EntityInfo[];
  surfaces: SurfaceInfo[];
  /** Every drawn region's number, by entity id. */
  regionNumbers: Map<string, number>;
}

function Page({
  page,
  entities,
  surfaces,
  regionNumbers,
  images,
  words,
  scale,
  selectedId,
  selectedSurfaceId,
  showHidden,
  previewing,
  drawing,
  locating,
  shownIds,
  selection,
  adding,
  onSelect,
  onToggle,
  onError,
  onDrawRegion,
  onSelectWords,
  onAddFinding,
}: PageProps) {
  const pageRef = useRef<HTMLDivElement>(null);
  const nearby = useNearViewport(pageRef);
  const [image, setImage] = useState<string | null>(null);
  // The id, not the entity: the popover must follow a decision made while it is open.
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const hovered = entities.find((entity) => entity.id === hoveredId) ?? null;
  // The drag lives in a ref: pointer events can arrive before React re-renders,
  // and a handler reading state would see the previous event's value.
  const drag = useRef<{ start: [number, number]; box: Box } | null>(null);
  const [draft, setDraft] = useState<Box | null>(null);
  // Selecting words: the page's words once loaded, the press that may become a
  // selection, and the words dragged over so far.
  const pageWords = useRef<WordInfo[] | null>(null);
  const press = useRef<{ client: Point; anchor: number; selecting: boolean } | null>(null);
  const [dragged, setDragged] = useState<WordInfo[] | null>(null);
  // A selection ends with a click on whatever is under the pointer; it must not toggle a box.
  const swallowClick = useRef(false);
  const [overWord, setOverWord] = useState(false);
  const selecting = !previewing && !drawing;
  const selected = selection?.pageIndex === page.index ? selection.words : null;
  const dpi = renderDpi(scale, window.devicePixelRatio || 1);

  useEffect(() => {
    if (!nearby || pageWords.current) return;
    let current = true;
    words
      .get(page.index)
      .then((list) => {
        if (current) pageWords.current = list;
      })
      .catch((error: unknown) => current && onError(`Page ${page.index + 1}: ${errorMessage(error)}`));
    return () => {
      current = false;
    };
  }, [nearby, words, page.index, onError]);

  useEffect(() => {
    if (!nearby) return;
    let current = true;
    images
      .get(page.index, dpi)
      .then((url) => current && setImage(url))
      .catch((error: unknown) => current && onError(`Page ${page.index + 1}: ${errorMessage(error)}`));
    return () => {
      current = false;
    };
  }, [nearby, images, page.index, dpi, onError]);

  const width = page.width * scale;
  const height = page.height * scale;
  const hatchId = `region-hatch-${page.index}`;

  /** The pointer's position in page points. */
  const toPoints = (event: MouseEvent<SVGSVGElement>): Point => {
    const bounds = event.currentTarget.getBoundingClientRect();
    return [
      ((event.clientX - bounds.left) * page.width) / bounds.width,
      ((event.clientY - bounds.top) * page.height) / bounds.height,
    ];
  };

  const onPointerDown = (event: PointerEvent<SVGSVGElement>) => {
    if (event.button !== 0) return;
    if (!(drawing || event.altKey)) {
      startSelecting(event);
      return;
    }
    event.preventDefault();
    capturePointer(event);
    const start = toPoints(event);
    drag.current = { start, box: dragBox(start, start, page) };
    setDraft(drag.current.box);
    setHoveredId(null);
  };

  /** A press on a word may become a selection once the pointer moves; a click stays a click. */
  const startSelecting = (event: PointerEvent<SVGSVGElement>) => {
    if (selection) onSelectWords(null);
    const list = pageWords.current;
    if (!selecting || !list) return;
    const anchor = wordAt(list, toPoints(event));
    if (anchor !== -1) press.current = { client: [event.clientX, event.clientY], anchor, selecting: false };
  };

  const onPointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (press.current) {
      moveSelection(event, press.current);
      return;
    }
    if (!drag.current) {
      const list = pageWords.current;
      setOverWord(selecting && list !== null && wordAt(list, toPoints(event)) !== -1);
      setHoveredId(hoveredBox(event.target));
      return;
    }
    drag.current.box = dragBox(drag.current.start, toPoints(event), page);
    setDraft(drag.current.box);
  };

  const moveSelection = (event: PointerEvent<SVGSVGElement>, current: NonNullable<typeof press.current>) => {
    const list = pageWords.current;
    if (!list) return;
    const [x, y] = current.client;
    if (!current.selecting && Math.hypot(event.clientX - x, event.clientY - y) < SELECT_THRESHOLD) return;
    if (!current.selecting) {
      current.selecting = true;
      setHoveredId(null);
      capturePointer(event);
    }
    setDragged(wordRange(list, current.anchor, nearestWord(list, toPoints(event))));
  };

  const onPointerUp = (event: PointerEvent<SVGSVGElement>) => {
    if (press.current) {
      const current = press.current;
      press.current = null;
      const list = pageWords.current;
      setDragged(null);
      if (!current.selecting || !list) return;
      swallowClick.current = true;
      onSelectWords({ pageIndex: page.index, words: wordRange(list, current.anchor, nearestWord(list, toPoints(event))) });
      return;
    }
    if (!drag.current) return;
    const box = dragBox(drag.current.start, toPoints(event), page);
    drag.current = null;
    setDraft(null);
    if (isLargeEnough(box, scale)) onDrawRegion(page.index, box);
  };

  /** A double click on a word outside every box selects that word. */
  const onDoubleClick = (event: MouseEvent<SVGSVGElement>) => {
    const list = pageWords.current;
    if (!selecting || !list || (event.target as Element).closest(".redaction")) return;
    const word = list[wordAt(list, toPoints(event))];
    if (word) onSelectWords({ pageIndex: page.index, words: [word] });
  };

  const highlighted = dragged ?? selected;
  // SVG paints in order: the selected box last, so no box overlapping it hides its outline.
  const drawOrder = [
    ...entities.filter((entity) => entity.id !== selectedId),
    ...entities.filter((entity) => entity.id === selectedId),
  ];

  return (
    <section className="page-slot" data-page-index={page.index} aria-label={`Page ${page.index + 1}`}>
      {isUnreadScan(page) && (
        <p className="page-warning">
          <TriangleAlert size={14} aria-hidden />
          A scan OCR did not read: nothing on it was found, and export leaves it as it is. To read
          it, turn on Scanned pages and open the document again.
        </p>
      )}
      {page.raster_dpi !== null && (
        <p className="page-note">
          <ScanText size={14} aria-hidden />
          Read by OCR, which can misread words.
        </p>
      )}
      <div ref={pageRef} className="page" style={{ width, height }}>
        {image ? (
          <motion.img
            src={image}
            alt=""
            draggable={false}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          />
        ) : (
          <div className="page-placeholder" aria-hidden />
        )}
        <svg
          className="overlay"
          viewBox={`0 0 ${page.width} ${page.height}`}
          preserveAspectRatio="none"
          data-over-word={overWord}
          onMouseLeave={() => {
            setHoveredId(null);
            setOverWord(false);
          }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          // Scrolling moves the page under a still pointer without a pointer
          // event; the next move shows the popover of whatever box is there.
          onWheel={() => setHoveredId(null)}
          onDoubleClick={onDoubleClick}
          onClickCapture={(event) => {
            if (!swallowClick.current) return;
            swallowClick.current = false;
            event.stopPropagation();
          }}
        >
          <defs>
            {/* Drawn regions are hatched in review mode, so what they cover stays visible. */}
            <pattern id={hatchId} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <line className="hatch-line" x1="0" y1="0" x2="0" y2="6" />
            </pattern>
          </defs>
          {showHidden &&
            surfaces.map(
              (surface) =>
                surface.box && (
                  <HiddenBox
                    key={surface.id}
                    id={surface.id}
                    box={surface.box}
                    selected={surface.id === selectedSurfaceId}
                  />
                ),
            )}
          {drawOrder.map((entity) => (
            <Redaction
              key={entity.id}
              entity={entity}
              hatch={entity.is_region && !previewing ? `url(#${hatchId})` : undefined}
              selected={entity.id === selectedId}
              dimmed={shownIds !== null && !shownIds.has(entity.id)}
              locating={locating}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
          {highlighted &&
            lineBoxes(highlighted).map(([x0, y0, x1, y1], index) => (
              <rect key={index} className="word-selection" x={x0} y={y0} width={x1 - x0} height={y1 - y0} rx={1.5} />
            ))}
          {draft && (
            <rect
              className="draft-region"
              x={draft[0]}
              y={draft[1]}
              width={draft[2] - draft[0]}
              height={draft[3] - draft[1]}
            />
          )}
        </svg>
        {!previewing &&
          entities.map(
            (entity) =>
              entity.is_region && (
                <RegionNumber
                  key={entity.id}
                  entity={entity}
                  number={regionNumbers.get(entity.id)}
                  scale={scale}
                />
              ),
          )}
        <AnimatePresence>
          {hovered && !previewing && !draft && !highlighted && (
            <Popover
              key={hovered.id}
              entity={hovered}
              regionNumber={regionNumbers.get(hovered.id)}
              locating={locating}
              scale={scale}
              pageHeight={height}
            />
          )}
        </AnimatePresence>
        <AnimatePresence>
          {selected && !previewing && (
            <AddFindingPopover
              key={selected.map((word) => word.start).join(",")}
              words={selected}
              adding={adding}
              scale={scale}
              pageWidth={width}
              pageHeight={height}
              onAdd={onAddFinding}
              onCancel={() => onSelectWords(null)}
            />
          )}
        </AnimatePresence>
      </div>
      <span className="page-number">{page.index + 1}</span>
    </section>
  );
}

interface RedactionProps {
  entity: EntityInfo;
  /** Fill for a drawn region in review mode: the page's hatch pattern. */
  hatch?: string;
  selected: boolean;
  /** Outside the list's filter: drawn faint in review mode. */
  dimmed: boolean;
  locating: boolean;
  onToggle: (entity: EntityInfo) => void;
  onSelect: (entity: EntityInfo) => void;
}

function Redaction({ entity, hatch, selected, dimmed, locating, onToggle, onSelect }: RedactionProps) {
  return (
    <g
      className="redaction"
      data-entity-id={entity.id}
      data-type={entity.type}
      data-state={entity.review}
      data-redacted={isRemoved(entity)}
      data-propagated={entity.source === "propagated"}
      data-selected={selected}
      data-dimmed={dimmed}
      onClick={() => {
        onSelect(entity);
        // A drawn region is removed and hidden data always goes: a click only selects them.
        if (!locating && isDecidable(entity)) onToggle(entity);
      }}
    >
      {entity.boxes.map(([x0, y0, x1, y1], index) => (
        <rect
          key={index}
          x={x0}
          y={y0}
          width={x1 - x0}
          height={y1 - y0}
          rx={1}
          style={hatch ? { fill: hatch } : undefined}
        />
      ))}
    </g>
  );
}

/**
 * Keep a drag going when the pointer leaves the page. A nicety: a browser that
 * refuses it must not stop the drag, which works while the pointer stays on the page.
 */
function capturePointer(event: PointerEvent<SVGSVGElement>): void {
  try {
    event.currentTarget.setPointerCapture(event.pointerId);
  } catch {
    // Without capture the drag still works on the page.
  }
}

/**
 * The box under the pointer, read from the topmost element on every move: the
 * popover goes as soon as the pointer leaves a box for the bare page, and
 * follows the top box where boxes overlap.
 */
function hoveredBox(target: EventTarget): string | null {
  if (!(target instanceof Element)) return null;
  return target.closest(".redaction")?.getAttribute("data-entity-id") ?? null;
}

function HiddenBox({ id, box: [x0, y0, x1, y1], selected }: { id: string; box: Box; selected: boolean }) {
  return (
    <rect
      className="hidden-box"
      data-surface-id={id}
      data-selected={selected}
      x={x0}
      y={y0}
      width={x1 - x0}
      height={y1 - y0}
    />
  );
}

/** A drawn region's number at its top-left corner, matching its row in the sidebar. */
function RegionNumber({ entity, number, scale }: { entity: EntityInfo; number: number | undefined; scale: number }) {
  const first = entity.boxes[0];
  if (!first || number === undefined) return null;
  return (
    <span className="region-number" style={{ left: first[0] * scale, top: first[1] * scale }} aria-hidden>
      {number}
    </span>
  );
}

const POPOVER_GAP = 8;
const POPOVER_HEIGHT = 64;

interface PopoverProps {
  entity: EntityInfo;
  regionNumber: number | undefined;
  locating: boolean;
  scale: number;
  pageHeight: number;
}

function Popover({ entity, regionNumber, locating, scale, pageHeight }: PopoverProps) {
  const first = entity.boxes[0];
  if (!first) return null;
  const left = Math.min(...entity.boxes.map((box) => box[0])) * scale;
  const bottom = Math.max(...entity.boxes.map((box) => box[3])) * scale;
  const top = Math.min(...entity.boxes.map((box) => box[1])) * scale;
  // Below the box, or above it when the page ends first.
  const below = bottom + POPOVER_GAP + POPOVER_HEIGHT < pageHeight;
  const redacted = isRemoved(entity);
  return (
    <motion.div
      className="popover"
      data-type={entity.type}
      style={below ? { left, top: bottom + POPOVER_GAP } : { left, bottom: pageHeight - top + POPOVER_GAP }}
      initial={{ opacity: 0, y: below ? -4 : 4, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.1 } }}
      transition={gentle}
    >
      <span className="popover-type">
        <span className="dot" aria-hidden />
        {typeLabel(entity.type)}
        {entity.source === "propagated" && <span className="muted"> · repeat</span>}
      </span>
      <span className="popover-text">{covers(entity, regionNumber)}</span>
      <span className="popover-hint">{popoverHint(entity, redacted, locating)}</span>
    </motion.div>
  );
}

function popoverHint(entity: EntityInfo, redacted: boolean, locating: boolean): string {
  if (entity.is_region) return "Drawn by you · click to select, Delete removes it";
  if (entity.surface_id !== null) return "In hidden data · always removed on export";
  if (locating) {
    return redacted ? "Will be redacted · its switch in the list keeps it" : "Kept · its switch in the list redacts it";
  }
  return redacted ? "Will be redacted · click to keep" : "Kept · click to redact";
}

/** Whether an element is within a screen or two of the viewport, so its image is worth loading. */
function useNearViewport(ref: RefObject<HTMLElement | null>): boolean {
  const [near, setNear] = useState(false);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new IntersectionObserver(([entry]) => setNear(entry?.isIntersecting ?? false), {
      rootMargin: "1200px 0px",
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref]);
  return near;
}
