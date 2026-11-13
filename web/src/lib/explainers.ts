import fs from "node:fs";
import path from "node:path";
import type { Lang } from "./i18n";

/*
  Spec explainers: data/specs/<id>/README.md (English) and README.ja.md
  (Japanese), written to templates/spec-explainer. The page shows the file's
  body under its own header, so the H1 and the one-line quote are lifted out.
*/

const SPECS = path.resolve(process.cwd(), "..", "data", "specs");

export interface Explainer {
  /** True when this is the Japanese edition; false when it fell back to English. */
  translated: boolean;
  oneLiner: string;
  /** Markdown without the H1 and the one-liner. */
  body: string;
}

function readIf(p: string): string | null {
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : null;
}

function split(md: string): { oneLiner: string; body: string } {
  const text = md.replace(/\r\n?/g, "\n");
  const one = /^>\s*(?:In one line:|一言で言うと[:：])\s*(.+)$/m.exec(text);
  const body = text
    .replace(/^\s*#\s+.+\n+/, "")
    .replace(/^>\s*(?:In one line:|一言で言うと[:：]).+\n+/m, "")
    .trim();
  return { oneLiner: one ? one[1].trim() : "", body };
}

export function explainer(id: string, lang: Lang): Explainer | null {
  const en = readIf(path.join(SPECS, id, "README.md"));
  const ja = lang === "ja" ? readIf(path.join(SPECS, id, "README.ja.md")) : null;
  const src = ja ?? en;
  if (!src) return null;
  return { translated: ja !== null, ...split(src) };
}

export function hasExplainer(id: string): boolean {
  return fs.existsSync(path.join(SPECS, id, "README.md"));
}

/** Markdown section headings, for the in-page navigation. */
export function sectionsOf(body: string): string[] {
  return [...body.matchAll(/^##\s+(.+)$/gm)].map((m) => m[1].trim());
}
