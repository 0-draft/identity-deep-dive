import fs from "node:fs";
import path from "node:path";
import type { Lang } from "./i18n";
import { readTrackState, recentInsightIds, type TrackId } from "./tracks";

/** Where an IETF draft is on its way to an RFC, from its Datatracker states. */
export type Stage = "individual" | "wg" | "wglc" | "iesg" | "rfced";

export const STAGES: Stage[] = ["individual", "wg", "wglc", "iesg", "rfced"];

export const STAGE_LABEL: Record<Stage, Record<Lang, string>> = {
  individual: { en: "Individual drafts", ja: "個人ドラフト" },
  wg: { en: "Working group", ja: "WG で作業中" },
  wglc: { en: "WG last call and write-up", ja: "WG ラストコール・取りまとめ" },
  iesg: { en: "With the IESG", ja: "IESG 審査中" },
  rfced: { en: "RFC Editor", ja: "RFC Editor" },
};

// Datatracker state names, furthest stage wins. The table lives in
// data/datatracker-stages.json, shared with scripts/landscape/refresh.py.
const STAGE_STATES: [Stage, string[]][] = JSON.parse(
  fs.readFileSync(path.resolve(process.cwd(), "..", "data", "datatracker-stages.json"), "utf8"),
).stages;

export function stageOf(labels: string[]): Stage {
  for (const [stage, names] of STAGE_STATES) {
    if (labels.some((l) => names.includes(l))) return stage;
  }
  return "wg";
}

export interface BoardItem {
  track: TrackId;
  name: string;
  rev: string;
  title: string;
  updated: string;
  stage: Stage;
  blocked: boolean;
  /** Anchor of a recent explanation on the track page, when there is one. */
  recentId?: string;
}

function item(track: TrackId, d: any, stage: Stage, recent: Map<string, string>): BoardItem {
  const labels: string[] = d.state_labels ?? [];
  return {
    track,
    name: d.name,
    rev: String(d.rev ?? d.revision ?? ""),
    title: d.title ?? "",
    updated: String(d.updated_at ?? d.date ?? "").slice(0, 10),
    stage,
    blocked: labels.includes("Blocked"),
    recentId: recent.get(d.name),
  };
}

/** Every IETF draft the tracks follow, by stage, newest first within a stage. */
export function board(only?: TrackId): Record<Stage, BoardItem[]> {
  const out = Object.fromEntries(STAGES.map((s) => [s, [] as BoardItem[]])) as Record<Stage, BoardItem[]>;
  const tracks: TrackId[] = only ? [only] : ["ietf-wimse", "oauth-wg"];
  for (const track of tracks) {
    const state = readTrackState(track);
    if (!state) continue;
    const recent = recentInsightIds(track);
    if (track === "ietf-wimse") {
      for (const d of state.active_drafts ?? []) out[stageOf(d.state_labels ?? [])].push(item(track, d, stageOf(d.state_labels ?? []), recent));
      for (const d of state.related_drafts ?? []) out.individual.push(item(track, d, "individual", recent));
    } else if (track === "oauth-wg") {
      for (const d of state.drafts ?? []) out[stageOf(d.state_labels ?? [])].push(item(track, d, stageOf(d.state_labels ?? []), recent));
    }
  }
  for (const s of STAGES) out[s].sort((a, b) => (a.updated < b.updated ? 1 : -1));
  return out;
}
