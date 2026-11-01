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
const BRIEFING_BLOCK = /<!-- insights:start -->[\s\S]*?<!-- insights:end -->\n*/;

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
  reasons?: string[];
  rationales?: string[];
  evidence?: string[];
  state_labels?: string[];
  draft_name?: string;
  repo?: string;
  url?: string;
  updated_at?: string;
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

export function topCandidates(id: TrackId, limit = 10): Candidate[] {
  const dir = path.join(trackDir(id), "data/normalized");
  if (id === "ietf-wimse") {
    const data = readJsonOrNull<{ candidates: Candidate[] }>(
      path.join(dir, "candidates.json"),
    );
    return (data?.candidates ?? []).slice(0, limit);
  }
  if (id === "oauth-wg") {
    const data = readJsonOrNull<{ candidates: Candidate[] }>(
      path.join(dir, "candidates.json"),
    );
    return (data?.candidates ?? []).slice(0, limit);
  }
  if (id === "openid") {
    const data = readJsonOrNull<{ candidates: any[] }>(
      path.join(dir, "candidates.json"),
    );
    return (data?.candidates ?? []).slice(0, limit).map((r: any) => ({
      title: r.full_name ?? r.name,
      score: Math.round((r.score ?? 0) * 10) / 10,
      reasons: [
        r.watch_note ? `watch: ${r.watch_note}` : "",
        r.open_prs != null ? `open PRs: ${r.open_prs}` : "",
        r.open_issues != null ? `open issues: ${r.open_issues}` : "",
        r.merged_prs_30d != null ? `merged 30d: ${r.merged_prs_30d}` : "",
      ].filter(Boolean),
      url: r.html_url,
      updated_at: r.pushed_at,
      ai_priority: r.ai_priority,
      ai_note: r.ai_note,
    }));
  }
  return [];
}

export interface TrackSummary {
  id: TrackId;
  meta: TrackMeta;
  dailyName: string | null;
  weeklyName: string | null;
  candidateCount: number;
  topScore: number | null;
}

export function summary(id: TrackId): TrackSummary {
  const meta = TRACKS.find((t) => t.id === id)!;
  const daily = latestDaily(id);
  const weekly = latestWeekly(id);
  const cands = topCandidates(id, 100);
  return {
    id,
    meta,
    dailyName: daily?.name?.replace(/\.md$/, "") ?? null,
    weeklyName: weekly?.name?.replace(/\.md$/, "") ?? null,
    candidateCount: cands.length,
    topScore: cands[0]?.score ?? null,
  };
}

export type Significance = "substantive" | "new-proposal" | "discussion" | "editorial" | "routine";

export const SIGNIFICANCE_LABEL: Record<Significance, string> = {
  substantive: "Substantive change",
  "new-proposal": "New proposal",
  discussion: "Discussion",
  editorial: "Editorial",
  routine: "Routine",
};

const SIGNIFICANCE_RANK: Record<Significance, number> = {
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
  url: string;
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
function plain(s: string): string {
  return (s ?? "")
    .replace(/\\([\[\]])/g, "$1")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function bySignificanceThenDate(a: Insight, b: Insight): number {
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
    use_cases: (i.use_cases ?? []).map(plain),
    related: (i.related ?? []).map((r) => ({ ...r, note: plain(r.note) })),
    significance: (i.significance in SIGNIFICANCE_RANK ? i.significance : "routine") as Significance,
  }));
  items.sort(bySignificanceThenDate);
  const briefs = data?.briefs ?? [];
  const last = briefs[briefs.length - 1];
  return { brief: last ? { at: last.at, text: plain(last.text) } : null, items };
}

export function allInsights(): Insight[] {
  return TRACKS.flatMap((t) => briefing(t.id).items).sort(bySignificanceThenDate);
}

export function trackName(id: TrackId): string {
  return TRACKS.find((t) => t.id === id)?.name ?? id;
}
