import fs from "node:fs";
import path from "node:path";

/*
  Bilingual RFC text: data/rfc/<number>/en.json (sections and paragraphs cut
  from the RFC Editor's text by scripts/rfc/fetch.py) and ja.json (a
  translation keyed by paragraph id, from scripts/rfc/import_ja.py). The page
  lines the two up paragraph by paragraph; a paragraph with no translation
  shows the English on both sides, marked.
*/

const RFC = path.resolve(process.cwd(), "..", "data", "rfc");

export type ParagraphKind = "p" | "li" | "pre";

export interface RfcParagraph {
  id: string;
  kind: ParagraphKind;
  en: string;
  ja?: string;
}

export interface RfcSection {
  id: string;
  title: string;
  title_ja?: string;
  /** Heading depth from the section number: "4" is 1, "4.2" is 2. */
  depth: number;
  paragraphs: RfcParagraph[];
}

export interface RfcDocument {
  number: number;
  title: string;
  url: string;
  fetched_at: string;
  sections: RfcSection[];
  translation: null | {
    translated_at: string;
    model: string;
    /** True when the English text changed after the translation was made. */
    stale: boolean;
    /** Translated share of the translatable paragraphs, 0 to 1. */
    coverage: number;
  };
}

function readJson<T>(p: string): T | null {
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8")) as T;
}

export function rfcNumbers(): number[] {
  if (!fs.existsSync(RFC)) return [];
  return fs
    .readdirSync(RFC)
    .filter((n) => /^\d+$/.test(n) && fs.existsSync(path.join(RFC, n, "en.json")))
    .map(Number)
    .sort((a, b) => a - b);
}

export function rfc(number: number): RfcDocument | null {
  const en = readJson<{
    number: number;
    title: string;
    url: string;
    fetched_at: string;
    content_hash: string;
    sections: { id: string; title: string; paragraphs: RfcParagraph[] }[];
  }>(path.join(RFC, String(number), "en.json"));
  if (!en) return null;
  const ja = readJson<{
    source_hash: string;
    translated_at: string;
    model: string;
    titles: Record<string, string>;
    paragraphs: Record<string, string>;
  }>(path.join(RFC, String(number), "ja.json"));

  let translatable = 0;
  let translated = 0;
  const sections: RfcSection[] = en.sections.map((s) => ({
    id: s.id,
    title: s.title,
    title_ja: ja?.titles[s.id],
    depth: /^\d/.test(s.id) || /^[A-Z](\.\d+)*$/.test(s.id) ? s.id.split(".").length : 1,
    paragraphs: s.paragraphs.map((p) => {
      if (p.kind !== "pre") translatable++;
      // A repeated paragraph (same text twice in a section) carries a
      // numeric suffix and shares the first one's translation.
      const t = ja?.paragraphs[p.id] ?? ja?.paragraphs[p.id.replace(/-\d+$/, "")];
      if (t) translated++;
      return { ...p, ja: t };
    }),
  }));
  return {
    number: en.number,
    title: en.title,
    url: en.url,
    fetched_at: en.fetched_at,
    sections,
    translation: ja
      ? {
          translated_at: ja.translated_at,
          model: ja.model,
          stale: ja.source_hash !== en.content_hash,
          coverage: translatable ? translated / translatable : 0,
        }
      : null,
  };
}
