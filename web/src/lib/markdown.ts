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

// A mermaid fence of backticks or tildes (three or more), indented up to
// three spaces (inside a list item, say), closed by the same character at
// the same indent and at least the same length.
const MERMAID_FENCE = /^( {0,3})((`|~)\3{2,})mermaid[ \t]*\n([\s\S]*?)^\1\2\3*[ \t]*$/gm;

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Markdown with mermaid diagrams, for deep dives. Diagram sources are lifted
 * out before marked runs, the HTML is sanitized, and each diagram goes back
 * in as escaped text inside the same disclosure the rest of the site uses,
 * where the page script renders it. The placeholder carries a random token,
 * so text in the document cannot pose as one.
 */
export function renderDocument(src: string, diagramLabel: string): string {
  const token = `MERMAID${crypto.randomUUID().replace(/-/g, "")}X`;
  const diagrams: string[] = [];
  const lifted = src.replace(/\r\n?/g, "\n").replace(MERMAID_FENCE, (_, indent: string, _run: string, _char: string, body: string) => {
    diagrams.push(body.replace(new RegExp(`^${indent}`, "gm"), "").trimEnd());
    // Same indent, blank lines around: inside a list item marked keeps it
    // in the item as its own paragraph, so the list is not broken.
    return `\n\n${indent}${token}${diagrams.length - 1}\n\n`;
  });
  const html = renderMarkdown(lifted);
  return html.replace(new RegExp(`<p>${token}(\\d+)</p>`, "g"), (_, i: string) => {
    const body = diagrams[Number(i)] ?? "";
    return `<details class="disclosure my-4" data-diagram open><summary>${escapeHtml(diagramLabel)}</summary><div class="diagram-frame"><pre class="mermaid">${escapeHtml(body)}</pre></div></details>`;
  });
}
