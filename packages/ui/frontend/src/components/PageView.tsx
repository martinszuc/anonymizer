import { TriangleAlert } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { forwardRef, useEffect, useRef, useState, type RefObject, type UIEvent } from "react";

import { errorMessage } from "../bridge";
import { gentle } from "../motion";
import type { PageImages } from "../pageImages";
import { covers, isRedacted, renderDpi, typeLabel } from "../review";
import type { Box, DocumentInfo, EntityInfo, PageInfo, SurfaceInfo } from "../types";

interface PageViewProps {
  document: DocumentInfo;
  images: PageImages;
  scale: number;
  selectedId: string | null;
  showHidden: boolean;
  onSelect: (entity: EntityInfo) => void;
  onToggle: (entity: EntityInfo) => void;
  onError: (message: string) => void;
  onCurrentPage: (index: number) => void;
}

/** Every page of the document, stacked, with its proposed redactions drawn over it. */
export const PageView = forwardRef<HTMLDivElement, PageViewProps>(function PageView(props, ref) {
  const { document, onCurrentPage } = props;

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
    <main ref={ref} className="canvas" onScroll={onScroll} aria-label="Pages">
      {document.pages.map((page) => (
        <Page
          key={page.index}
          page={page}
          entities={document.entities.filter((entity) => entity.page_index === page.index && entity.boxes.length > 0)}
          surfaces={document.surfaces.filter((surface) => surface.page_index === page.index && surface.box)}
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
}

function Page({ page, entities, surfaces, images, scale, selectedId, showHidden, onSelect, onToggle, onError }: PageProps) {
  const pageRef = useRef<HTMLDivElement>(null);
  const nearby = useNearViewport(pageRef);
  const [image, setImage] = useState<string | null>(null);
  const [hovered, setHovered] = useState<EntityInfo | null>(null);
  const dpi = renderDpi(scale, window.devicePixelRatio || 1);

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

  return (
    <section className="page-slot" data-page-index={page.index} aria-label={`Page ${page.index + 1}`}>
      {!page.has_text_layer && (
        <p className="page-warning">
          <TriangleAlert size={14} aria-hidden />
          No text layer: this page looks like a scan. Nothing on it is detected until OCR is supported.
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
          onMouseLeave={() => setHovered(null)}
        >
          {showHidden &&
            surfaces.map((surface) => surface.box && <HiddenBox key={surface.id} box={surface.box} />)}
          {entities.map((entity) => (
            <Redaction
              key={entity.id}
              entity={entity}
              selected={entity.id === selectedId}
              onHover={setHovered}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
        </svg>
        <AnimatePresence>
          {hovered && <Popover key={hovered.id} entity={hovered} scale={scale} pageHeight={height} />}
        </AnimatePresence>
      </div>
      <span className="page-number">{page.index + 1}</span>
    </section>
  );
}

interface RedactionProps {
  entity: EntityInfo;
  selected: boolean;
  onHover: (entity: EntityInfo | null) => void;
  onToggle: (entity: EntityInfo) => void;
  onSelect: (entity: EntityInfo) => void;
}

function Redaction({ entity, selected, onHover, onToggle, onSelect }: RedactionProps) {
  return (
    <g
      className="redaction"
      data-entity-id={entity.id}
      data-type={entity.type}
      data-state={entity.review}
      data-redacted={isRedacted(entity.review)}
      data-propagated={entity.source === "propagated"}
      data-selected={selected}
      onMouseEnter={() => onHover(entity)}
      onClick={() => {
        onSelect(entity);
        onToggle(entity);
      }}
    >
      {entity.boxes.map(([x0, y0, x1, y1], index) => (
        <rect key={index} x={x0} y={y0} width={x1 - x0} height={y1 - y0} rx={1} />
      ))}
    </g>
  );
}

function HiddenBox({ box: [x0, y0, x1, y1] }: { box: Box }) {
  return <rect className="hidden-box" x={x0} y={y0} width={x1 - x0} height={y1 - y0} />;
}

const POPOVER_GAP = 8;
const POPOVER_HEIGHT = 64;

function Popover({ entity, scale, pageHeight }: { entity: EntityInfo; scale: number; pageHeight: number }) {
  const first = entity.boxes[0];
  if (!first) return null;
  const left = Math.min(...entity.boxes.map((box) => box[0])) * scale;
  const bottom = Math.max(...entity.boxes.map((box) => box[3])) * scale;
  const top = Math.min(...entity.boxes.map((box) => box[1])) * scale;
  // Below the box, or above it when the page ends first.
  const below = bottom + POPOVER_GAP + POPOVER_HEIGHT < pageHeight;
  const redacted = isRedacted(entity.review);
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
      <span className="popover-text">{covers(entity)}</span>
      <span className="popover-hint">{redacted ? "Redacted · click to keep" : "Kept · click to redact"}</span>
    </motion.div>
  );
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
