// Markdown layer: turn model text into safe HTML.
// marked parses Markdown -> HTML; DOMPurify strips anything unsafe (XSS).
import { marked } from "https://esm.sh/marked@14";
import DOMPurify from "https://esm.sh/dompurify@3";

marked.setOptions({
  gfm: true, // GitHub-flavored markdown (tables, ~~strikethrough~~, etc.)
  breaks: true, // treat single newlines as <br>
});

export function renderMarkdown(text) {
  const rawHtml = marked.parse(text ?? "");
  return DOMPurify.sanitize(rawHtml);
}
