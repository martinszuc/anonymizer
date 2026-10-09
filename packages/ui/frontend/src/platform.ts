// Shortcut labels follow the platform: ⌘ on macOS, Ctrl elsewhere.

export const isMac = /Mac|iPhone|iPad/.test(navigator.userAgent);

/** What the system's file manager is called, for "Show in …". */
export const fileManager = isMac ? "Finder" : /Windows/.test(navigator.userAgent) ? "Explorer" : "Folder";

export function shortcut(key: string, { shift = false } = {}): string {
  if (isMac) return `${shift ? "⇧" : ""}⌘${key}`;
  return `Ctrl+${shift ? "Shift+" : ""}${key}`;
}

/** Whether a keyboard event carries the platform's command modifier. */
export function hasCommand(event: KeyboardEvent): boolean {
  return isMac ? event.metaKey : event.ctrlKey;
}
