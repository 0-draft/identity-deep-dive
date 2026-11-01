export type Lang = "en" | "ja";
export const LANGS: Lang[] = ["en", "ja"];

const STRINGS = {
  siteTitle: { en: "Identity Deep Dive", ja: "Identity Deep Dive" },
  siteDescription: {
    en: "What changed this week in IETF WIMSE, the OAuth WG and the OpenID Foundation: the picks, where each spec stands, and how the drafts fit together.",
    ja: "IETF WIMSE・OAuth WG・OpenID Foundation の今週の動きを、要点・各仕様の進捗・draft 同士の関係の 3 つで追う。",
  },
  intro: {
    en: "What changed in identity standards this week, where each spec stands, and how the drafts fit together.",
    ja: "アイデンティティ標準の今週の変化と、各仕様の進捗、draft 同士の関係をまとめる。",
  },
  thisWeek: { en: "This week", ja: "今週の要点" },
  thisWeekNote: {
    en: "The changes worth five minutes, most important first.",
    ja: "5 分で押さえておくべき変化。重要な順に並べている。",
  },
  noPicks: {
    en: "No picks yet. They appear after the next collection run.",
    ja: "まだ要点はない。次の収集 run の後に表示される。",
  },
  readExplanation: { en: "Read the explanation", ja: "解説を読む" },
  board: { en: "Where the specs stand", ja: "仕様の進捗" },
  boardNote: {
    en: "IETF drafts by Datatracker state. Highlighted ones changed in the last seven days.",
    ja: "IETF の draft を Datatracker の state で並べたもの。強調表示はこの 7 日間に変化があったもの。",
  },
  boardOpenId: {
    en: "OpenID Foundation specifications follow their own process and are tracked by repository activity on the OpenID page.",
    ja: "OpenID Foundation の仕様は独自のプロセスで進むため、OpenID のページでリポジトリの動きとして追っている。",
  },
  andMore: { en: "more", ja: "件ほか" },
  blocked: { en: "blocked", ja: "保留中" },
  topics: { en: "Topics", ja: "トピック" },
  topicsNote: {
    en: "How the drafts and repositories group, and which topics build on each other.",
    ja: "draft とリポジトリのまとまりと、トピック同士のつながり。",
  },
  topicMap: { en: "Map of related topics", ja: "トピックの関係図" },
  relatedTopics: { en: "Related", ja: "関連" },
  allChanges: { en: "Everything else from the last few days", ja: "直近のその他の変化" },
  nothingElse: { en: "Nothing else yet.", ja: "ほかにはまだない。" },
  noExplanations: {
    en: "No explanations yet. They appear after the next collection run finds a new draft revision, mailing-list thread or pull request.",
    ja: "解説はまだない。次の収集 run で draft の改版・メーリングリストのスレッド・PR が見つかると表示される。",
  },
  whatChanged: { en: "What changed", ja: "変化の解説" },
  minorChanges: { en: "Minor or unclear changes", ja: "軽微・詳細不明の変化" },
  noTrackExplanations: {
    en: "No explanations in the last seven days. The board and reports below still show the latest collected state.",
    ja: "この 7 日間の解説はない。下のボードとレポートは最新の収集結果を表示している。",
  },
  howItWorks: { en: "How it works", ja: "仕組み" },
  diagram: { en: "Diagram", ja: "図" },
  reportDataEnglish: { en: "", ja: "(見出しは日本語、データは原文の英語)" },
  whoAffects: { en: "Who this affects", ja: "影響を受ける人" },
  relatedIn: { en: "Related in", ja: "関連:" },
  queue: { en: "Deep-dive queue", ja: "ディープダイブ候補" },
  queueNote: {
    en: "Ranked by activity and lifecycle. Triage then moves raised candidates above the rest and lowered ones below.",
    ja: "活動量とライフサイクルで順位付けし、triage で上げた候補を上に、下げた候補を下に移している。",
  },
  raised: { en: "Raised", ja: "優先度を上げた" },
  lowered: { en: "Lowered", ja: "優先度を下げた" },
  noCandidates: { en: "Nothing scores above the threshold right now.", ja: "現在、閾値を超える候補はない。" },
  dailyReport: { en: "Full daily report for", ja: "日次レポート全文" },
  weeklyDigest: { en: "Weekly digest", ja: "週次ダイジェスト" },
  updated: { en: "Updated", ja: "更新" },
  sourcePage: { en: "page", ja: "のページ" },
  dataOnGithub: { en: "Collected data on GitHub", ja: "収集データ (GitHub)" },
  footerBuilt: { en: "Built from", ja: "生成元:" },
  footerProvenance: {
    en: "Explanations are machine-drafted from the linked sources, which stay authoritative.",
    ja: "解説はリンク先の一次情報をもとに機械生成したもの。正確な内容は一次情報を確認すること。",
  },
  footerCadence: { en: "Collected every 6 hours. Weekly digest on Mondays.", ja: "6 時間ごとに収集。週次ダイジェストは月曜。" },
  switchLang: { en: "日本語", ja: "English" },
  navMap: { en: "Spec map", ja: "仕様マップ" },
  mapTitle: { en: "The identity spec map", ja: "アイデンティティ仕様マップ" },
  mapIntro: {
    en: "OAuth, OpenID, workload identity and credential specifications by layer: where each one stands, what it builds on, and who documents support for it.",
    ja: "OAuth、OpenID、ワークロードアイデンティティ、クレデンシャルの仕様をレイヤー別に並べた。各仕様の進捗、土台にしている仕様、対応を公式に文書化している製品をまとめている。",
  },
  mapAdoptionRule: {
    en: "Adoption lists only support stated in official documentation (the vendor's or project's own, or a standards body's page naming it), and a weekly check confirms the cited phrase is still on that page.",
    ja: "利用状況には、公式のドキュメント（ベンダーやプロジェクト自身のもの、または標準化団体がその名前を挙げているページ）に対応が明記されているものだけを載せている。引用した文言がそのページにまだあるかは毎週確認している。",
  },
  mapChecked: { en: "Statuses and sources checked", ja: "状態と出典の確認日時" },
  mapRelations: { en: "Relations diagram", ja: "関係図" },
  mapAdopters: { en: "documented adopters", ja: "件の公式な対応" },
  mapAdoption: { en: "Documented support", ja: "公式に文書化された対応" },
  mapNoAdoption: {
    en: "No sourced support entries collected yet. This says nothing about how widely it is used.",
    ja: "出典付きの対応情報はまだ集めていない。普及していないという意味ではない。",
  },
  mapNotReverified: { en: "Not re-verified at the last check", ja: "前回の確認で再確認できなかった" },
  mapStatusNotReverifiedShort: { en: "not re-verified", ja: "未再確認" },
  mapStatusNotReverified: {
    en: "this status could not be re-confirmed at the last check",
    ja: "前回の確認でこの状態を再確認できなかった",
  },
  mapLastVerified: { en: "last verified", ja: "最終確認" },
  mapVerifiedOn: { en: "verified", ja: "確認" },
  mapSource: { en: "source", ja: "出典" },
  mapDetails: { en: "Every spec", ja: "仕様ごとの詳細" },
  deepDives: { en: "Deep dives", ja: "ディープダイブ" },
  deepDivesNote: {
    en: "Longer write-ups of one draft or repository: how it works, who it affects, what changed and what is still open.",
    ja: "1 つの draft やリポジトリを掘り下げた解説。仕組み、影響を受ける人、変更点、未解決の論点をまとめている。",
  },
  deepDive: { en: "Deep dive", ja: "ディープダイブ" },
  docUntranslated: {
    en: "",
    ja: "このディープダイブの日本語版はまだない。英語の原文を表示している。",
  },
  docSource: { en: "Source files on GitHub", ja: "元ファイル (GitHub)" },
  docOverview: { en: "Overview", ja: "概要" },
  docContext: { en: "Context", ja: "背景" },
  docSpecNotes: { en: "Spec notes", ja: "仕様メモ" },
  docInterop: { en: "Interop checklist", ja: "相互運用チェックリスト" },
  docTimeline: { en: "Timeline", ja: "経緯" },
  docHandsOn: { en: "Hands-on log", ja: "検証ログ" },
  docHandsOnNotes: { en: "Hands-on notes", ja: "検証メモ" },
  untranslated: { en: "", ja: "(英語のみ)" },
} as const;

export type StringKey = keyof typeof STRINGS;

export function t(lang: Lang, key: StringKey): string {
  return STRINGS[key][lang];
}

/** The Japanese text when there is one, otherwise the English. */
export function pick(lang: Lang, en: string, ja?: string): string {
  return lang === "ja" && ja ? ja : en;
}

export function pickList(lang: Lang, en: string[], ja?: string[]): string[] {
  return lang === "ja" && ja && ja.length ? ja : en;
}

/** Site-relative path for a language: "/" + path for English, "/ja/" + path for Japanese. */
export function href(lang: Lang, path = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const clean = path.replace(/^\//, "");
  return `${base}/${lang === "ja" ? "ja/" : ""}${clean}`;
}

export function formatDay(lang: Lang, isoDate: string, withWeekday = false): string {
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString(lang === "ja" ? "ja-JP" : "en-GB", {
    ...(withWeekday ? { weekday: "long" } : {}),
    day: "numeric",
    month: "long",
    timeZone: "UTC",
  });
}

export function formatDateTime(lang: Lang, iso: string): string {
  return (
    new Date(iso).toLocaleString(lang === "ja" ? "ja-JP" : "en-GB", {
      day: "numeric",
      month: "long",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
    }) + " UTC"
  );
}
