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

const REPO_ROOT = path.resolve(import.meta.dirname ?? __dirname, "../../..");

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

function readLatestMarkdown(dir: string): ReportFile | null {
  const files = listDir(dir).filter((f) => f.endsWith(".md"));
  if (files.length === 0) return null;
  const latest = files[files.length - 1];
  const fullPath = path.join(dir, latest);
  const stat = fs.statSync(fullPath);
  return {
    name: latest,
    body: fs.readFileSync(fullPath, "utf8"),
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
      path.join(dir, "backlog.json"),
    );
    return (data?.candidates ?? []).slice(0, limit);
  }
  if (id === "openid") {
    const latest = readJsonOrNull<{ snapshot_date?: string }>(
      path.join(dir, "latest.json"),
    );
    const date = latest?.snapshot_date;
    const top = date
      ? readJsonOrNull<{ repos: any[] }>(path.join(dir, `top-${date}.json`))
      : null;
    return (top?.repos ?? []).slice(0, limit).map((r: any) => ({
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
