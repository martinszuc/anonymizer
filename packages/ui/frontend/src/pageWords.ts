import type { ReviewBridge } from "./bridge";
import type { WordInfo } from "./types";

/**
 * Page words for one open document, fetched once per page when a selection
 * needs them. A failed fetch is forgotten, so the next selection tries again.
 */
export class PageWords {
  private readonly bridge: ReviewBridge;
  private readonly words = new Map<number, Promise<WordInfo[]>>();

  constructor(bridge: ReviewBridge) {
    this.bridge = bridge;
  }

  get(index: number): Promise<WordInfo[]> {
    const cached = this.words.get(index);
    if (cached) return cached;
    const words = this.bridge.page_words(index);
    this.words.set(index, words);
    words.catch(() => this.words.delete(index));
    return words;
  }
}
