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
