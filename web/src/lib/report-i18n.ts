import type { Lang } from "./i18n";

/*
  The daily and weekly reports are Markdown that the track scripts
  (tracks/*/scripts/report.py) write in English. Their prose is fixed:
  headings, table headers, labels and a handful of sentences, around data
  (draft names, titles, numbers) that stays as written. For the Japanese site
  those fixed parts are swapped line by line; anything not listed here is
  shown as is.

  scripts/insights/apply.py adds a briefing block between insights:start/end
  markers. The site cuts that block (tracks.ts) and renders the same content
  from insights.json instead, so its strings need no entry here; the few
  listed below only matter for the raw Markdown.
*/

const TITLES: [RegExp, string][] = [
  [/^# WIMSE Daily Report \(/, "# WIMSE 日次レポート ("],
  [/^# WIMSE Weekly Digest \(/, "# WIMSE 週次ダイジェスト ("],
  [/^# OAuth WG Daily Report - /, "# OAuth WG 日次レポート - "],
  [/^# OAuth WG Weekly Digest - /, "# OAuth WG 週次ダイジェスト - "],
  [/^# OpenID Radar Daily - /, "# OpenID 日次レーダー - "],
  [/^# OpenID Radar Weekly - /, "# OpenID 週次レーダー - "],
];

const HEADINGS: Record<string, string> = {
  "Active Drafts": "アクティブな draft",
  "Active PRs This Week": "今週動いた PR",
  "Active WG Drafts": "アクティブな WG draft",
  "Current Hot Topics": "現在活発なトピック",
  "Deep Dive Candidates": "ディープダイブ候補",
  "Draft Movement": "draft の動き",
  "Drafts Updated This Week": "今週更新された draft",
  "Fresh Pushes (<= 3 days)": "直近 3 日以内の push",
  "Mailarchive Signals": "メーリングリストの動き",
  "Mailing List Topics": "メーリングリストのトピック",
  "Next Actions": "次にやること",
  "Next Deep-Dive Suggestions": "次のディープダイブ候補",
  Notes: "メモ",
  "Organization Events": "Organization のイベント",
  "Recent GitHub Activity": "GitHub の最近の動き",
  "Recent Issues": "最近の issue",
  "Recent Pull Requests": "最近の PR",
  "Recent Related Drafts": "最近の関連 draft",
  "Recommended Deep Dive Queue": "推奨するディープダイブ順",
  "Repo Watch": "リポジトリの動き",
  "Repositories Persistently in Top List": "上位に居続けるリポジトリ",
  Snapshot: "スナップショット",
  "Snapshot Coverage": "スナップショットの範囲",
  Summary: "概要",
  "Top Deep-Dive Candidates": "ディープダイブ候補の上位",
  "Top Focus": "注目の上位",
  "Top Priorities": "優先度の上位",
  Triage: "Triage",
  Briefing: "ブリーフィング",
  "Triage of the candidate queue": "候補キューの triage",
  "Also changed, not explained": "その他の変化 (解説なし)",
};

const TABLE_CELLS: Record<string, string> = {
  Appearances: "出現回数",
  "Avg Score": "平均スコア",
  Category: "カテゴリ",
  Date: "日付",
  Draft: "draft",
  "Key State": "主な状態",
  "Latest Commit": "最新コミット",
  "Latest Score": "最新スコア",
  "Open Issues": "未解決 issue",
  "Open PRs": "未マージ PR",
  "Push Age": "最終 push",
  Pushed: "push 日時",
  Rank: "順位",
  Reasons: "理由",
  Repo: "リポジトリ",
  Repository: "リポジトリ",
  Rev: "版",
  Score: "スコア",
  States: "状態",
  Title: "タイトル",
  Trend: "推移",
  Updated: "更新",
};

// Label at the start of a bullet: "- Label: value".
const LABELS: Record<string, string> = {
  "Active (push <= 30 days)": "アクティブ (30 日以内に push)",
  "Active (push <= 90 days)": "アクティブ (90 日以内に push)",
  "Active WG drafts": "アクティブな WG draft",
  "Archived repositories": "アーカイブ済みリポジトリ",
  "Compared with previous snapshot": "比較対象のスナップショット",
  "Drafts updated this week": "今週更新された draft",
  "First snapshot in window": "期間内の最初のスナップショット",
  "Issues touched this week": "今週動いた issue",
  "Last snapshot in window": "期間内の最後のスナップショット",
  "Mailing-list posts scanned": "確認したメーリングリストの投稿",
  "Open issues (org total)": "未解決 issue (org 全体)",
  "Open PRs (org total)": "未マージ PR (org 全体)",
  "PRs touched this week": "今週動いた PR",
  "Public repositories": "公開リポジトリ",
  "Related drafts": "関連 draft",
  "Snapshot files in window": "期間内のスナップショット数",
  "Snapshots available": "利用できるスナップショット",
  "Top list size per day": "1 日あたりの上位リスト件数",
  "Tracked GitHub repos": "追跡している GitHub リポジトリ",
  "Added/updated active draft revisions": "追加・更新されたアクティブな draft の版",
  "Removed/replaced active draft revisions": "削除・置き換えられたアクティブな draft の版",
};

const SENTENCES: Record<string, string> = {
  "No active drafts updated in the last 7 days.": "直近 7 日間に更新されたアクティブな draft はない。",
  "No active-draft list change since previous snapshot.": "前回のスナップショットからアクティブな draft の一覧に変化はない。",
  "No candidates above threshold today.": "今日は閾値を超える候補がない。",
  "No candidates above threshold.": "閾値を超える候補がない。",
  "No mailing-list topics extracted.": "メーリングリストからトピックは抽出されなかった。",
  "No PR activity in window.": "期間内に PR の動きはない。",
  "No recent pushes.": "最近の push はない。",
  "No scored candidates available.": "スコア付きの候補がない。",
  "No topic signal from mailing list.": "メーリングリストにトピックの兆候はない。",
  "Not enough snapshots to compute weekly diff.": "週次の差分を出すにはスナップショットが足りない。",
  "Previous snapshot not found; trend is partial.": "前回のスナップショットがないため、推移は部分的。",
};

// Fixed numbered steps in the OAuth WG daily report.
const STEPS: Record<string, string> = {
  "1. Evaluate the top 3 items in `Top Priorities` as weekly deep-dive candidates.":
    "1. 「優先度の上位」の上位 3 件を、今週のディープダイブ候補として検討する。",
  "2. Separately track comment deadlines for `In Last Call` / `In WG Last Call` drafts.":
    "2. `In Last Call` / `In WG Last Call` の draft は、コメント期限を別に管理する。",
  "3. For repos with a sudden spike in activity, create a scaffold in `deep-dives/` to capture key discussion points.":
    "3. 活動が急に増えたリポジトリは、`deep-dives/` に雛形を作って議論の要点を記録する。",
};

const PREFIXES: [RegExp, string][] = [
  [/^Generated at: /, "生成日時: "],
  [/^Window: /, "期間: "],
  [/^- Warning: /, "- 警告: "],
];

// Own keys only: "constructor" or "toString" in a report must not match
// Object.prototype.
const has = (table: object, key: string) => Object.hasOwn(table, key);

function translateHeaderRow(line: string): string {
  return line
    .split("|")
    .map((c) => (has(TABLE_CELLS, c.trim()) ? c.replace(c.trim(), TABLE_CELLS[c.trim()]) : c))
    .join("|");
}

// Only the OpenID report's Trend column holds words to translate; every
// other data cell stays as written.
function translateTrendCell(line: string, column: number): string {
  const cells = line.split("|");
  const key = (cells[column] ?? "").trim();
  const m = /^(up|down) (\d+)$/.exec(key);
  const to = key === "same" ? "変化なし" : key === "new" ? "新規" : m ? `${m[2]} 位${m[1] === "up" ? "上昇" : "下降"}` : null;
  if (to === null) return line;
  cells[column] = cells[column].replace(key, to);
  return cells.join("|");
}

const FENCE_LINE = /^ {0,3}(`{3,}|~{3,})(.*)$/;

export function localizeReport(markdown: string, lang: Lang): string {
  if (lang !== "ja") return markdown;
  let fence: string | null = null;
  let trendColumn = -1;
  const lines = markdown.split("\n");
  return lines
    .map((line, i) => {
      // CommonMark fences: closed by the same character, at least as long,
      // with nothing after it.
      const f = FENCE_LINE.exec(line);
      if (fence === null && f) {
        fence = f[1];
        return line;
      }
      if (fence !== null) {
        if (f && f[1][0] === fence[0] && f[1].length >= fence.length && !f[2].trim()) fence = null;
        return line;
      }
      for (const [re, to] of TITLES) if (re.test(line)) return line.replace(re, to);
      const h = /^(#{2,3}) (.+)$/.exec(line);
      if (h && has(HEADINGS, h[2])) return `${h[1]} ${HEADINGS[h[2]]}`;
      if (line.startsWith("|")) {
        if (/^\|[\s:|-]+\|$/.test(lines[i + 1] ?? "")) {
          trendColumn = line.split("|").findIndex((c) => c.trim() === "Trend");
          return translateHeaderRow(line);
        }
        return trendColumn > 0 ? translateTrendCell(line, trendColumn) : line;
      }
      trendColumn = -1;
      if (has(STEPS, line)) return STEPS[line];
      const s = /^- (.+)$/.exec(line);
      if (s && has(SENTENCES, s[1])) return `- ${SENTENCES[s[1]]}`;
      const l = /^- ([^:`]+):(.*)$/.exec(line);
      if (l && has(LABELS, l[1])) return `- ${LABELS[l[1]]}:${l[2]}`;
      for (const [re, to] of PREFIXES) if (re.test(line)) return line.replace(re, to);
      return line;
    })
    .join("\n");
}
