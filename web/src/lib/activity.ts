import fs from "node:fs";
import path from "node:path";
import type { Lang } from "./i18n";
import type { Spec } from "./landscape";
import { allInsights, trackDir, TRACKS, type Insight, type TrackId } from "./tracks";

/*
  What has been happening around a spec, from data the tracks already
  collect: its revision history (Datatracker, via scripts/landscape/refresh.py),
  the explanations that mention it, and mailing-list subjects that name its
  draft. The same signals, counted over the last 90 days, rank the map's
  "moving now" list.
*/

export const WINDOW_DAYS = 90;

export interface Revision {
  rev: string;
  date: string;
}

export interface MailMention {
  date?: string;
  subject: string;
  url: string;
  track: TrackId;
}

export interface Activity {
  draft?: string;
  rfc?: number;
  revisions: Revision[];
  /** Date the RFC was published, when the status carries it. */
  published?: string;
  insights: Insight[];
  mail: MailMention[];
  /** Signals inside the window: revisions + explanations + mail subjects. */
  score: number;
  /** Most recent signal date, if any. */
  latest?: string;
}

function readJson<T>(p: string): T | null {
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, "utf8")) as T;
  } catch {
    return null;
  }
}

/** Names that identify the spec in free text: its draft name and RFC number,
 *  plus a one-word name (DPoP, PKCE, SPIFFE, CIBA) when it has one. */
export function keysOf(spec: Spec): { draft?: string; rfc?: number; words: string[] } {
  const draft = spec.ietf?.draft ?? spec.status.from_draft;
  const rfc = spec.ietf?.rfc ?? (spec.status.stage === "rfc" ? Number(/RFC (\d+)/.exec(spec.status.label)?.[1]) || undefined : undefined);
  const words: string[] = [];
  const name = spec.name;
  if (/^[A-Za-z0-9-]{4,}$/.test(name)) words.push(name);
  const abbr = /\(([A-Z0-9-]{4,})\)\s*$/.exec(name);
  if (abbr) words.push(abbr[1]);
  return { draft, rfc, words };
}

function mentions(text: string, keys: ReturnType<typeof keysOf>): boolean {
  if (keys.draft && text.includes(keys.draft)) return true;
  if (keys.rfc && new RegExp(`RFC\\s?${keys.rfc}\\b`).test(text)) return true;
  return keys.words.some((w) => new RegExp(`(^|[^A-Za-z0-9-])${w}([^A-Za-z0-9-]|$)`).test(text));
}

let insightCache: Insight[] | null = null;
let mailCache: MailMention[] | null = null;

function mailSubjects(): MailMention[] {
  if (mailCache) return mailCache;
  const out: MailMention[] = [];
  for (const t of TRACKS) {
    const data = readJson<any>(path.join(trackDir(t.id), "data/normalized/mailarchive.json"));
    if (!data) continue;
    const items: any[] = data.posts ?? data.messages ?? [];
    for (const m of items) {
      if (!m?.subject || !m?.url) continue;
      out.push({ date: m.date, subject: String(m.subject), url: String(m.url), track: t.id });
    }
  }
  return (mailCache = out);
}

export function activity(spec: Spec): Activity {
  const keys = keysOf(spec);
  const cutoff = new Date(Date.now() - WINDOW_DAYS * 864e5).toISOString().slice(0, 10);
  const status = spec.status;
  const revisions = [...(status.history ?? [])].sort((a, b) => (a.date < b.date ? 1 : -1));

  insightCache ??= allInsights();
  const insights = insightCache.filter(
    (i) =>
      mentions(i.id, keys) ||
      i.related.some((r) => keys.draft !== undefined && r.name === keys.draft) ||
      mentions(`${i.title ?? ""} ${i.headline} ${i.summary}`, keys),
  );
  const mail = mailSubjects().filter((m) => keys.draft !== undefined && m.subject.includes(keys.draft));

  const dates = [
    ...revisions.map((r) => r.date),
    ...insights.map((i) => i.first_seen),
    ...mail.map((m) => m.date ?? ""),
    ...(status.published ? [status.published] : []),
  ].filter(Boolean);
  const recent = dates.filter((d) => d >= cutoff);
  return {
    draft: keys.draft,
    rfc: keys.rfc,
    revisions,
    published: status.published,
    insights,
    mail,
    score: recent.length,
    latest: dates.length ? dates.sort().at(-1) : undefined,
  };
}

/** Working-group drafts the tracks follow that are not on the map. */
export interface Newcomer {
  name: string;
  title: string;
  rev: string;
  date: string;
  track: TrackId;
  url: string;
}

export function newcomers(onMap: Set<string>): Newcomer[] {
  const out: Newcomer[] = [];
  const seen = new Set<string>();
  for (const t of TRACKS) {
    const data = readJson<any>(path.join(trackDir(t.id), "data/normalized/datatracker.json"));
    if (!data) continue;
    const drafts: any[] = [...(data.drafts ?? []), ...(data.active_drafts ?? [])];
    for (const d of drafts) {
      const name: string = d?.name ?? "";
      if (!name.startsWith("draft-ietf-") || onMap.has(name) || seen.has(name)) continue;
      const labels: string[] = d.state_labels ?? [];
      if (labels.some((l) => ["Expired", "Dead", "Replaced"].includes(l))) continue;
      seen.add(name);
      out.push({
        name,
        title: d.title ?? "",
        rev: String(d.rev ?? d.revision ?? ""),
        date: String(d.date ?? d.updated_at ?? "").slice(0, 10),
        track: t.id,
        url: d.datatracker_url ?? `https://datatracker.ietf.org/doc/${name}/`,
      });
    }
  }
  return out.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function formatRev(lang: Lang, r: Revision): string {
  return lang === "ja" ? `-${r.rev} (${r.date})` : `-${r.rev} on ${r.date}`;
}
