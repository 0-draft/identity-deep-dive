import fs from "node:fs";
import path from "node:path";
import type { Lang } from "./i18n";
import { TRACKS, trackDir, type TrackId } from "./tracks";

/*
  Deep dives live in tracks/<track>/deep-dives/<slug>/ as Markdown files. A
  Japanese edition of a file sits next to it as <name>.ja.md. README.md comes
  first; the other files follow in a fixed order, then anything else.
*/

const ORDER = ["README.md", "context.md", "spec-notes.md", "interop-checklist.md", "timeline.md", "hands-on-log.md"];

export interface DeepDiveFile {
  /** Path inside the deep-dive directory, English name (e.g. "hands-on/notes.md"). */
  name: string;
  body: string;
  /** True when this is the Japanese edition. */
  translated: boolean;
}

export interface DeepDive {
  track: TrackId;
  slug: string;
  title: string;
  oneLiner: string;
  files: DeepDiveFile[];
  hasJapanese: boolean;
}

function walk(dir: string, prefix = ""): string[] {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const rel = prefix ? `${prefix}/${e.name}` : e.name;
    if (e.isDirectory()) return walk(path.join(dir, e.name), rel);
    return e.name.endsWith(".md") && !e.name.endsWith(".ja.md") ? [rel] : [];
  });
}

function sortFiles(names: string[]): string[] {
  return [...names].sort((a, b) => {
    const ia = ORDER.indexOf(a), ib = ORDER.indexOf(b);
    if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    return a.localeCompare(b);
  });
}

function oneLinerOf(readme: string): string {
  const m = /^>\s*(?:In one line:|一言で言うと[:：])\s*(.+)$/m.exec(readme);
  return m ? m[1].trim() : "";
}

function titleOf(readme: string, slug: string): string {
  const m = /^#\s+(?:Deep Dive:\s*|ディープダイブ[:：]\s*)?(.+)$/m.exec(readme);
  return m ? m[1].trim() : slug;
}

export function deepDiveSlugs(track: TrackId): string[] {
  const root = path.join(trackDir(track), "deep-dives");
  if (!fs.existsSync(root)) return [];
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith("_") && fs.existsSync(path.join(root, e.name, "README.md")))
    .map((e) => e.name)
    .sort();
}

export function deepDive(track: TrackId, slug: string, lang: Lang): DeepDive {
  const dir = path.join(trackDir(track), "deep-dives", slug);
  const names = sortFiles(walk(dir));
  let hasJapanese = false;
  const files = names.map((name) => {
    const ja = path.join(dir, name.replace(/\.md$/, ".ja.md"));
    if (fs.existsSync(ja)) hasJapanese = true;
    const useJa = lang === "ja" && fs.existsSync(ja);
    return { name, body: fs.readFileSync(useJa ? ja : path.join(dir, name), "utf8"), translated: useJa };
  });
  const readme = files.find((f) => f.name === "README.md")?.body ?? "";
  return { track, slug, title: titleOf(readme, slug), oneLiner: oneLinerOf(readme), files, hasJapanese };
}

export function allDeepDives(lang: Lang): DeepDive[] {
  return TRACKS.flatMap((t) => deepDiveSlugs(t.id).map((s) => deepDive(t.id, s, lang)));
}

/** Draft names (slugs) that have a deep dive, for linking the board. */
export function deepDiveIndex(track: TrackId): Set<string> {
  return new Set(deepDiveSlugs(track));
}
