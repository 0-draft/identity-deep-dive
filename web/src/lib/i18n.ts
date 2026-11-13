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
  themeDark: { en: "Dark", ja: "ダーク" },
  themeLight: { en: "Light", ja: "ライト" },
  themeToggle: { en: "Switch colour theme", ja: "配色を切り替える" },
  navMap: { en: "Spec map", ja: "仕様マップ" },
  mapTitle: { en: "The identity spec map", ja: "アイデンティティ仕様マップ" },
  mapIntro: {
    en: "OAuth, OpenID, workload identity and credential specifications by layer: where each one stands, what it builds on, and who documents support for it.",
    ja: "OAuth、OpenID、ワークロードアイデンティティ、クレデンシャルの仕様をレイヤー別に並べた。各仕様の進捗、土台にしている仕様、対応を公式に文書化している製品をまとめている。",
  },
  mapAdoptionRule: {
    en: "Adoption lists only support stated in official documentation (the vendor's or project's own, or a standards body's page naming it), and a weekly check confirms the cited phrase is still on that page. Experimental, alpha and beta support is counted separately as preview.",
    ja: "利用状況には、公式のドキュメント（ベンダーやプロジェクト自身のもの、または標準化団体がその名前を挙げているページ）に対応が明記されているものだけを載せている。引用した文言がそのページにまだあるかは毎週確認している。実験的・アルファ・ベータの対応は「プレビュー」として別に数える。",
  },
  mapChecked: { en: "Statuses and sources checked", ja: "状態と出典の確認日時" },
  mapRelations: { en: "Relations diagram", ja: "関係図" },
  mapAdopters: { en: "documented adopters", ja: "件の公式な対応" },
  mapLegend: { en: "Legend", ja: "凡例" },
  mapPreview: { en: "in preview", ja: "件のプレビュー" },
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
  mapMoving: { en: "Moving now", ja: "いま動いている仕様" },
  mapMovingNote: {
    en: "Ranked by what the last 90 days brought: new revisions, explanations on this site, and mailing-list threads that name the draft.",
    ja: "直近 90 日の動き (新しい revision、このサイトの解説、draft 名を挙げた ML スレッド) の多い順。",
  },
  mapSignals: { en: "signals in 90 days", ja: "件の動き (90 日)" },
  mapNewcomers: { en: "Adopted by a working group, not on the map yet", ja: "WG 採択済みでまだ map にない draft" },
  mapNewcomersNote: {
    en: "Working-group drafts the tracks follow that have no entry here. Adding one is a pull request to data/landscape.json.",
    ja: "トラックが追っている WG draft のうち、ここに項目がないもの。追加は data/landscape.json への pull request で行う。",
  },
  mapExplainer: { en: "Explainer", ja: "解説" },
  mapOpenSpec: { en: "Open", ja: "開く" },
  specBack: { en: "Spec map", ja: "仕様マップ" },
  specOfficial: { en: "Official text", ja: "公式本文" },
  specWhere: { en: "Where it stands", ja: "現在地" },
  specLayer: { en: "Layer", ja: "レイヤー" },
  specNoExplainer: {
    en: "No explainer written for this spec yet. The summary, relations and documented support below are maintained.",
    ja: "この仕様の解説はまだ書かれていない。下の要約・関係・対応状況は維持されている。",
  },
  specExplainerUntranslated: { en: "", ja: "解説は英語版のみ。日本語訳はまだない。" },
  specExplainerSource: { en: "Explainer source on GitHub", ja: "解説の元ファイル (GitHub)" },
  specRelations: { en: "How it relates to other specs", ja: "他の仕様との関係" },
  specActivity: { en: "Activity", ja: "動き" },
  specActivityNote: {
    en: "Revisions from the Datatracker, explanations from this site's daily runs, and mailing-list subjects naming the draft.",
    ja: "Datatracker の revision 履歴、このサイトの日次 run が書いた解説、draft 名を挙げた ML の件名。",
  },
  specRevisions: { en: "Revisions", ja: "Revision 履歴" },
  specPublished: { en: "Published", ja: "公開" },
  specNoRevisions: { en: "Revision history appears after the next status refresh.", ja: "Revision 履歴は次回の状態更新後に表示される。" },
  specRecentExplanations: { en: "Explanations on this site", ja: "このサイトの解説" },
  specMail: { en: "On the mailing list", ja: "メーリングリスト" },
  specNoActivity: { en: "Nothing collected about this spec yet.", ja: "この仕様についてはまだ何も収集していない。" },
  specProducts: { en: "Products, identity providers and services", ja: "製品・IdP・サービス" },
  specOss: { en: "Open-source implementations", ja: "OSS 実装" },
  specRfc: { en: "Read the RFC side by side", ja: "RFC を英日対訳で読む" },
  specRfcNote: { en: "English on the left, Japanese on the right, paragraph by paragraph.", ja: "左に英語、右に日本語、段落単位で並べたもの。" },
  rfcTitle: { en: "side by side", ja: "英日対訳" },
  rfcContents: { en: "Contents", ja: "目次" },
  rfcEnglish: { en: "English", ja: "English" },
  rfcJapanese: { en: "Japanese", ja: "日本語" },
  rfcUntranslated: { en: "not translated yet", ja: "未訳" },
  rfcCoverage: { en: "of paragraphs translated", ja: "の段落を翻訳済み" },
  rfcStale: {
    en: "The English text was refreshed after this translation was made; some paragraphs may no longer line up.",
    ja: "翻訳後に英語本文が更新されている。対応がずれている段落があるかもしれない。",
  },
  rfcTranslatedBy: { en: "Machine translation by", ja: "機械翻訳:" },
  rfcTranslatedOn: { en: "on", ja: "日付" },
  rfcNoTranslation: { en: "No Japanese translation yet. The English text is shown on both sides.", ja: "日本語訳はまだない。両側に英語を表示している。" },
  rfcNotice: {
    en: "The English text is the RFC as published by the RFC Editor, copyright the IETF Trust and the persons identified as the document authors, reproduced under the IETF Trust Legal Provisions. The Japanese is an unofficial machine translation; only the English is authoritative. Examples, figures and references are shown in English only.",
    ja: "英語本文は RFC Editor が公開した RFC そのもので、著作権は IETF Trust と文書の著者にあり、IETF Trust Legal Provisions に基づいて転載している。日本語は非公式の機械翻訳で、正文は英語のみ。例・図・参考文献は英語のまま表示する。",
  },
  rfcOfficial: { en: "Official text at the RFC Editor", ja: "RFC Editor の公式本文" },
  rfcBack: { en: "Spec page", ja: "仕様のページ" },
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
