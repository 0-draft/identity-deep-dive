import fs from "node:fs";
import path from "node:path";
import type { Lang } from "./i18n";

/*
  The identity-spec map: data/landscape.json (curated specs, layers and
  relations), data/landscape-sources.json (sourced OpenID statuses and
  adoption claims) and data/landscape-status.json (what CI last checked:
  Datatracker states, and whether each claim's evidence is still on its
  page). Only claims whose evidence was seen are shown as adoption.
*/

const DATA = path.resolve(process.cwd(), "..", "data");

function read<T>(name: string, fallback: T): T {
  const p = path.join(DATA, name);
  if (!fs.existsSync(p)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(p, "utf8")) as T;
  } catch {
    return fallback;
  }
}

export type RelationKind = "builds-on" | "profiles" | "extends" | "replaces" | "alternative" | "complements";

export interface Layer {
  id: string;
  name: string;
  name_ja: string;
}

export interface SpecStatus {
  stage: string;
  label: string;
  title?: string;
  url?: string;
  states?: string[];
  updated?: string;
  verified?: boolean;
  stale?: boolean;
  note?: string;
  note_ja?: string;
}

export interface Claim {
  spec: string;
  who: string;
  kind: string;
  what: string;
  what_ja?: string;
  url: string;
  evidence: string;
  verified: boolean;
  verified_on?: string;
  /** Pre-GA support, as the cited page states it. Absent means generally available. */
  maturity?: "experimental" | "alpha" | "beta";
}

export interface Spec {
  id: string;
  name: string;
  layer: string;
  summary: string;
  summary_ja: string;
  relations: { to: string; kind: RelationKind }[];
  deep_dive?: { track: string; slug: string };
  status: SpecStatus;
  adoption: Claim[];
  /** Claims whose evidence was not found at the last check. */
  unverified: Claim[];
}

export interface Landscape {
  generatedAt: string | null;
  layers: Layer[];
  specs: Spec[];
}

export function landscape(): Landscape {
  const cat = read<{ layers: Layer[]; specs: any[] }>("landscape.json", { layers: [], specs: [] });
  const status = read<{ generated_at?: string; specs?: Record<string, SpecStatus>; adoption?: Claim[] }>(
    "landscape-status.json",
    {},
  );
  const claims = status.adoption ?? [];
  const specs: Spec[] = cat.specs.map((s) => ({
    id: s.id,
    name: s.name,
    layer: s.layer,
    summary: s.summary,
    summary_ja: s.summary_ja,
    relations: s.relations ?? [],
    deep_dive: s.deep_dive,
    status: status.specs?.[s.id] ?? { stage: "unknown", label: "" },
    adoption: claims.filter((c) => c.spec === s.id && c.verified),
    unverified: claims.filter((c) => c.spec === s.id && !c.verified),
  }));
  return { generatedAt: status.generated_at ?? null, layers: cat.layers, specs };
}

/** Status groups for colour and legend, in lifecycle order. */
export type StatusGroup = "rfc" | "near" | "draft" | "draft-inactive" | "openid-final" | "openid-draft" | "other" | "unknown";

export function statusGroup(s: SpecStatus): StatusGroup {
  if (s.stage === "rfc") return "rfc";
  if (s.stage === "rfced" || s.stage === "iesg") return "near";
  if (s.stage === "wg" || s.stage === "wglc") return "draft";
  if (s.stage === "individual" || s.stage === "expired") return "draft-inactive";
  if (s.stage === "openid-final") return "openid-final";
  if (s.stage.startsWith("openid-")) return "openid-draft";
  if (s.stage === "external") return "other";
  return "unknown";
}

export const STATUS_GROUP_LABEL: Record<StatusGroup, Record<Lang, string>> = {
  rfc: { en: "IETF RFC", ja: "IETF RFC" },
  near: { en: "IETF, with the IESG or RFC Editor", ja: "IETF、IESG 審査中または RFC Editor 待ち" },
  draft: { en: "IETF working-group draft", ja: "IETF WG ドラフト" },
  "draft-inactive": { en: "IETF individual, or no longer active, draft", ja: "IETF 個人ドラフト・失効などで止まったドラフト" },
  "openid-final": { en: "OpenID Final", ja: "OpenID Final" },
  "openid-draft": { en: "OpenID draft", ja: "OpenID ドラフト" },
  other: { en: "Other body", ja: "その他の団体" },
  unknown: { en: "Status unknown", ja: "状態不明" },
};

export const STAGE_DETAIL: Record<string, Record<Lang, string>> = {
  rfc: { en: "Published RFC", ja: "RFC として公開済み" },
  rfced: { en: "Approved, with the RFC Editor", ja: "承認済み、RFC Editor 待ち" },
  iesg: { en: "With the IESG", ja: "IESG 審査中" },
  wglc: { en: "WG last call or write-up", ja: "WG ラストコール・取りまとめ" },
  wg: { en: "Working-group draft", ja: "WG ドラフト" },
  individual: { en: "Individual draft, not adopted by a WG", ja: "個人ドラフト（WG 未採択）" },
  expired: { en: "Expired, replaced or withdrawn draft", ja: "失効・置き換え・取り下げ済みのドラフト" },
  external: { en: "Outside the IETF and OpenID", ja: "IETF・OpenID 以外" },
  unknown: { en: "Status unknown", ja: "状態不明" },
};

export const RELATION_LABEL: Record<RelationKind, Record<Lang, string>> = {
  "builds-on": { en: "Builds on", ja: "土台とする仕様" },
  profiles: { en: "Profiles", ja: "プロファイル対象" },
  extends: { en: "Extends", ja: "拡張対象" },
  replaces: { en: "Replaces", ja: "置き換え対象" },
  alternative: { en: "Alternative to", ja: "代替" },
  complements: { en: "Works with", ja: "組み合わせ" },
};

/** "Replaces" from a spec that is not yet published is only an intent. */
export function relationLabel(from: Spec, kind: RelationKind, lang: Lang): string {
  if (kind === "replaces" && from.status.stage !== "rfc" && from.status.stage !== "openid-final") {
    return { en: "Would replace", ja: "置き換え予定" }[lang];
  }
  return RELATION_LABEL[kind][lang];
}

export const KIND_LABEL: Record<string, Record<Lang, string>> = {
  idp: { en: "Identity provider", ja: "IdP" },
  cloud: { en: "Cloud", ja: "クラウド" },
  library: { en: "Library", ja: "ライブラリ" },
  product: { en: "Product", ja: "製品" },
  spec: { en: "Specification", ja: "仕様" },
  wallet: { en: "Wallet", ja: "ウォレット" },
  government: { en: "Government", ja: "政府" },
};

export const MATURITY_LABEL: Record<NonNullable<Claim["maturity"]>, Record<Lang, string>> = {
  experimental: { en: "experimental", ja: "実験的" },
  alpha: { en: "alpha", ja: "アルファ" },
  beta: { en: "beta", ja: "ベータ" },
};
