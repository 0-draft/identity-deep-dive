import { marked } from "marked";
import sanitizeHtml from "sanitize-html";

// Reports carry text written by third parties: draft titles, PR and issue
// titles, mailing-list subjects. marked passes raw HTML through, so its output
// is sanitized before it reaches the page.
const ALLOWED: sanitizeHtml.IOptions = {
  allowedTags: [
    "h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "blockquote", "pre", "code",
    "em", "strong", "del", "a", "table", "thead", "tbody", "tr", "th", "td", "hr", "br",
  ],
  allowedAttributes: { a: ["href", "title", "rel"], th: ["align"], td: ["align"] },
  allowedSchemes: ["http", "https"],
  allowProtocolRelative: false,
  transformTags: {
    a: sanitizeHtml.simpleTransform("a", { rel: "noreferrer" }),
  },
};

export function renderMarkdown(src: string): string {
  return sanitizeHtml(marked.parse(src, { async: false }) as string, ALLOWED);
}

const MERMAID_FENCE = /^```mermaid\n([\s\S]*?)^```$/gm;

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Markdown with mermaid diagrams, for deep dives. Diagram sources are lifted
 * out before marked runs, the HTML is sanitized, and each diagram goes back
 * in as escaped text inside the same disclosure the rest of the site uses,
 * where the page script renders it.
 */
export function renderDocument(src: string, diagramLabel: string): string {
  const diagrams: string[] = [];
  const lifted = src.replace(MERMAID_FENCE, (_, body: string) => {
    diagrams.push(body.trimEnd());
    return `\n\nMERMAIDPLACEHOLDER${diagrams.length - 1}\n\n`;
  });
  const html = renderMarkdown(lifted);
  return html.replace(/<p>MERMAIDPLACEHOLDER(\d+)<\/p>/g, (_, i: string) => {
    const body = diagrams[Number(i)] ?? "";
    return `<details class="disclosure my-4" data-diagram open><summary>${escapeHtml(diagramLabel)}</summary><div class="diagram-frame"><pre class="mermaid">${escapeHtml(body)}</pre></div></details>`;
  });
}
