import react from "@vitejs/plugin-react";
import type { Plugin } from "vite";
import { defineConfig } from "vitest/config";

// The built page may load nothing but its own files and the page images the
// Python side sends as data: URLs. Development skips it, since Vite injects
// inline styles and a live-reload socket. 'unsafe-eval' is required: pywebview
// hands every API result back to the page through eval(), and without it each
// call silently never resolves.
const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-eval'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:",
  "connect-src 'none'",
  "form-action 'none'",
].join("; ");

function contentSecurityPolicy(): Plugin {
  return {
    name: "content-security-policy",
    apply: "build",
    transformIndexHtml: (html) =>
      html.replace(
        '<meta charset="utf-8">',
        `<meta charset="utf-8">\n    <meta http-equiv="Content-Security-Policy" content="${CONTENT_SECURITY_POLICY}">`,
      ),
  };
}

export default defineConfig({
  plugins: [react(), contentSecurityPolicy()],
  // Relative asset paths: pywebview serves the build from its own directory.
  base: "./",
  build: { outDir: "../src/anonymizer/ui/static", emptyOutDir: true },
  server: { host: "127.0.0.1", port: 5173, strictPort: true },
  test: { environment: "node" },
});
