import fs from "node:fs";
import path from "node:path";

export type TrackId = "ietf-wimse" | "oauth-wg" | "openid";

export interface TrackMeta {
  id: TrackId;
  name: string;
  scope: string;
  scope_ja: string;
  org: string;
  href?: string;
}

export const TRACKS: TrackMeta[] = [
  {
    id: "ietf-wimse",
    name: "IETF WIMSE",
    scope: "Workload Identity in Multi-System Environments",
    scope_ja: "マルチシステム環境におけるワークロードアイデンティティ",
    org: "IETF Working Group",
    href: "https://datatracker.ietf.org/wg/wimse/",
  },
  {
    id: "oauth-wg",
    name: "OAuth WG",
    scope: "OAuth Working Group drafts and implementations",
    scope_ja: "OAuth WG の draft と実装",
    org: "IETF Working Group",
    href: "https://datatracker.ietf.org/wg/oauth/",
  },
  {
    id: "openid",
    name: "OpenID",
    scope: "OpenID Foundation specifications and repositories",
    scope_ja: "OpenID Foundation の仕様とリポジトリ",
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
  ai_note_ja?: string;
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
    // Only the two values that move a candidate are shown; anything else in
    // the data is treated as untriaged.
    ...(c.ai_priority === "high" || c.ai_priority === "low"
      ? {
          ai_priority: c.ai_priority,
          ai_note: c.ai_note ? plain(c.ai_note) : "",
          ai_note_ja: c.ai_note_ja ? plain(c.ai_note_ja) : "",
        }
      : {}),
  }));
}

export type Significance = "substantive" | "new-proposal" | "discussion" | "editorial" | "routine";

export const SIGNIFICANCE_LABEL: Record<Significance, { en: string; ja: string }> = {
  substantive: { en: "Substantive change", ja: "実質的な変更" },
  "new-proposal": { en: "New proposal", ja: "新しい提案" },
  discussion: { en: "Discussion", ja: "議論" },
  editorial: { en: "Editorial", ja: "編集上の変更" },
  routine: { en: "Routine", ja: "定例" },
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
  headline_ja?: string;
  summary: string;
  summary_ja?: string;
  significance: Significance;
  use_cases: string[];
  use_cases_ja?: string[];
  diagram: string;
  related: { track: TrackId; name: string; note: string; note_ja?: string }[];
}

export interface TrackBriefing {
  brief: { at: string; text: string; text_ja?: string } | null;
  items: Insight[];
}

/** An HTML id for an explanation, used as the anchor picks and the board link to. */
export function anchorId(insightId: string): string {
  return "x-" + insightId.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
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
    briefs?: { at: string; text: string; text_ja?: string }[];
  }>(path.join(trackDir(id), "data/normalized/insights.json"));
  const items = Object.values(data?.items ?? {}).map((i) => ({
    ...i,
    track: id,
    headline: plain(i.headline).replace(/^in short,\s*/i, "").replace(/^./, (c) => c.toUpperCase()),
    headline_ja: i.headline_ja ? plain(i.headline_ja) : undefined,
    summary: plain(i.summary),
    summary_ja: i.summary_ja ? plain(i.summary_ja) : undefined,
    // title is stored as collected (apply.py does not escape it), so it is
    // not run through plain().
    url: safeUrl(i.url),
    use_cases: (i.use_cases ?? []).map(plain),
    use_cases_ja: (i.use_cases_ja ?? []).map(plain),
    related: (i.related ?? []).map((r) => ({ ...r, note: plain(r.note), note_ja: r.note_ja ? plain(r.note_ja) : undefined })),
    significance: (i.significance in SIGNIFICANCE_RANK ? i.significance : "routine") as Significance,
  }));
  items.sort(byDateThenSignificance);
  const briefs = data?.briefs ?? [];
  const last = briefs[briefs.length - 1];
  return {
    brief: last ? { at: last.at, text: plain(last.text), text_ja: last.text_ja ? plain(last.text_ja) : undefined } : null,
    items,
  };
}

export function allInsights(): Insight[] {
  return TRACKS.flatMap((t) => briefing(t.id).items).sort(byDateThenSignificance);
}

export function trackName(id: TrackId): string {
  return TRACKS.find((t) => t.id === id)?.name ?? id;
}

export function readTrackState(id: TrackId): any | null {
  return readJsonOrNull(path.join(trackDir(id), "data/normalized/state.json"));
}

/** Draft name -> anchor of its most recent explanation from the last seven days. */
export function recentInsightIds(id: TrackId): Map<string, string> {
  const cutoff = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
  const out = new Map<string, string>();
  for (const i of briefing(id).items) {
    const m = /^draft:(draft-[a-z0-9-]+?)-\d{2}$/.exec(i.id);
    if (m && i.first_seen >= cutoff && !out.has(m[1])) out.set(m[1], anchorId(i.id));
  }
  return out;
}

export interface Pick {
  insight: Insight;
  why: string;
  why_ja?: string;
}

export interface Topic {
  id: string;
  name: string;
  name_ja?: string;
  summary: string;
  summary_ja?: string;
  members: { track: TrackId; name: string }[];
  related: string[];
}

export interface Synthesis {
  generatedAt: string | null;
  picks: Pick[];
  topics: Topic[];
}

/** data/synthesis.json, with picks resolved to explanations that still exist. */
export function synthesis(): Synthesis {
  const data = readJsonOrNull<any>(path.join(REPO_ROOT, "data/synthesis.json"));
  if (!data) return { generatedAt: null, picks: [], topics: [] };
  const byId = new Map(allInsights().map((i) => [i.id, i]));
  const picks = (data.picks ?? [])
    .filter((p: any) => byId.has(p.id))
    .map((p: any) => ({ insight: byId.get(p.id)!, why: String(p.why ?? ""), why_ja: p.why_ja || undefined }));
  const valid = new Set(TRACKS.map((t) => t.id));
  const topics = (data.topics ?? []).map((t: any) => ({
    id: String(t.id),
    name: String(t.name ?? ""),
    name_ja: t.name_ja || undefined,
    summary: String(t.summary ?? ""),
    summary_ja: t.summary_ja || undefined,
    members: (t.members ?? []).filter((m: any) => valid.has(m.track)),
    related: (t.related ?? []).map(String),
  }));
  return { generatedAt: data.generated_at ?? null, picks, topics };
}
