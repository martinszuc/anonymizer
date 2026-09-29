import type { ReviewBridge } from "./bridge";

/**
 * Page images for one open document, fetched once per resolution. A failed
 * render is forgotten, so scrolling back to the page tries again.
 */
export class PageImages {
  private readonly bridge: ReviewBridge;
  private readonly images = new Map<string, Promise<string>>();

  constructor(bridge: ReviewBridge) {
    this.bridge = bridge;
  }

  get(index: number, dpi: number): Promise<string> {
    const key = `${index}@${dpi}`;
    const cached = this.images.get(key);
    if (cached) return cached;
    const image = this.bridge.page_image(index, dpi);
    this.images.set(key, image);
    image.catch(() => this.images.delete(key));
    return image;
  }
}
