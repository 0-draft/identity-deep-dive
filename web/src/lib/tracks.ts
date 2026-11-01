import fs from "node:fs";
import path from "node:path";

export type TrackId = "ietf-wimse" | "oauth-wg" | "openid";

export interface TrackMeta {
  id: TrackId;
  name: string;
  scope: string;
  org: string;
  href?: string;
}

export const TRACKS: TrackMeta[] = [
  {
    id: "ietf-wimse",
    name: "IETF WIMSE",
    scope: "Workload Identity in Multi-System Environments",
    org: "IETF Working Group",
    href: "https://datatracker.ietf.org/wg/wimse/",
  },
  {
    id: "oauth-wg",
    name: "OAuth WG",
    scope: "OAuth Working Group drafts and implementations",
    org: "IETF Working Group",
    href: "https://datatracker.ietf.org/wg/oauth/",
  },
  {
    id: "openid",
    name: "OpenID",
    scope: "OpenID Foundation specifications and repositories",
    org: "OpenID Foundation",
    href: "https://github.com/openid",
  },
];

const REPO_ROOT = path.resolve(process.cwd(), "..");

export function trackDir(id: TrackId): string {
  return path.join(REPO_ROOT, "tracks", id);
}

function listDir(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).sort();
}

export interface ReportFile {
  name: string;
  body: string;
  mtime: string;
}

// The briefing block apply.py writes into the daily report is rendered from
// insights.json instead, so it is cut out of the Markdown here.
// Markers count only on a line of their own, matching apply.py: the section
// cannot contain one, and a third-party title that does sits inside a table
// row or list item, so it can neither end the cut early nor hide report text.
const BRIEFING_BLOCK = /^<!-- insights:start -->$[\s\S]*?^<!-- insights:end -->$\n*/m;

function readLatestMarkdown(dir: string): ReportFile | null {
  const files = listDir(dir).filter((f) => f.endsWith(".md"));
  if (files.length === 0) return null;
  const latest = files[files.length - 1];
  const fullPath = path.join(dir, latest);
  const stat = fs.statSync(fullPath);
  return {
    name: latest,
    body: fs.readFileSync(fullPath, "utf8").replace(BRIEFING_BLOCK, ""),
    mtime: stat.mtime.toISOString(),
  };
}

export function latestDaily(id: TrackId): ReportFile | null {
  return readLatestMarkdown(path.join(trackDir(id), "reports/daily"));
}

export function latestWeekly(id: TrackId): ReportFile | null {
  return readLatestMarkdown(path.join(trackDir(id), "reports/weekly"));
}

export interface Candidate {
  title: string;
  score: number;
  state_labels?: string[];
  draft_name?: string;
  url?: string;
  ai_priority?: "high" | "normal" | "low";
  ai_note?: string;
}

function readJsonOrNull<T = unknown>(p: string): T | null {
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, "utf8")) as T;
  } catch {
    return null;
  }
}

// URLs come from collected data, not from the model, but they still end up in
// href attributes: only http(s) gets through.
export function safeUrl(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : undefined;
  } catch {
    return undefined;
  }
}

export function topCandidates(id: TrackId, limit = 12): Candidate[] {
  const data = readJsonOrNull<{ candidates: any[] }>(path.join(trackDir(id), "data/normalized/candidates.json"));
  return (data?.candidates ?? []).slice(0, limit).map((c: any) => ({
    // OpenID candidates are repositories; the IETF tracks' are drafts.
    title: id === "openid" ? c.full_name ?? c.name : c.title,
    score: id === "openid" ? Math.round((c.score ?? 0) * 10) / 10 : c.score,
    state_labels: c.state_labels,
    draft_name: c.draft_name,
    url: safeUrl(c.html_url ?? c.url),
    ai_priority: c.ai_priority,
    ai_note: c.ai_note ? plain(c.ai_note) : undefined,
  }));
}

export type Significance = "substantive" | "new-proposal" | "discussion" | "editorial" | "routine";

export const SIGNIFICANCE_LABEL: Record<Significance, string> = {
  substantive: "Substantive change",
  "new-proposal": "New proposal",
  discussion: "Discussion",
  editorial: "Editorial",
  routine: "Routine",
};

export const SIGNIFICANCE_RANK: Record<Significance, number> = {
  substantive: 0,
  "new-proposal": 1,
  discussion: 2,
  editorial: 3,
  routine: 4,
};

export interface Insight {
  id: string;
  track: TrackId;
  kind: string;
  title: string;
  url?: string;
  first_seen: string;
  updated_at: string;
  headline: string;
  summary: string;
  significance: Significance;
  use_cases: string[];
  diagram: string;
  related: { track: TrackId; name: string; note: string }[];
}

export interface TrackBriefing {
  brief: { at: string; text: string } | null;
  items: Insight[];
}

// apply.py escapes text for Markdown (HTML entities, \[ \]). Astro escapes on
// output itself, so undo that here or the page shows "&lt;".
export function plain(s: string): string {
  return (s ?? "")
    .replace(/\\([\[\]])/g, "$1")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function byDateThenSignificance(a: Insight, b: Insight): number {
  if (a.first_seen !== b.first_seen) return a.first_seen < b.first_seen ? 1 : -1;
  return SIGNIFICANCE_RANK[a.significance] - SIGNIFICANCE_RANK[b.significance] || a.id.localeCompare(b.id);
}

export function briefing(id: TrackId): TrackBriefing {
  const data = readJsonOrNull<{
    items?: Record<string, Omit<Insight, "track">>;
    briefs?: { at: string; text: string }[];
  }>(path.join(trackDir(id), "data/normalized/insights.json"));
  const items = Object.values(data?.items ?? {}).map((i) => ({
    ...i,
    track: id,
    headline: plain(i.headline).replace(/^in short,\s*/i, "").replace(/^./, (c) => c.toUpperCase()),
    summary: plain(i.summary),
    title: plain(i.title),
    url: safeUrl(i.url),
    use_cases: (i.use_cases ?? []).map(plain),
    related: (i.related ?? []).map((r) => ({ ...r, note: plain(r.note) })),
    significance: (i.significance in SIGNIFICANCE_RANK ? i.significance : "routine") as Significance,
  }));
  items.sort(byDateThenSignificance);
  const briefs = data?.briefs ?? [];
  const last = briefs[briefs.length - 1];
  return { brief: last ? { at: last.at, text: plain(last.text) } : null, items };
}

export function allInsights(): Insight[] {
  return TRACKS.flatMap((t) => briefing(t.id).items).sort(byDateThenSignificance);
}

export function trackName(id: TrackId): string {
  return TRACKS.find((t) => t.id === id)?.name ?? id;
}
