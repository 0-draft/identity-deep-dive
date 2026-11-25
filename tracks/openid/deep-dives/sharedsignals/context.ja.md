# Context

## Trigger

`tracks/openid/data/normalized/candidates.json`（2026-11-24 のスナップショット）で、openid/sharedsignals は deep dive のない `openid` の候補の中で最上位だった（3 位、スコア 14.4）。`tracks/openid/data/normalized/insights.json` には、`main` への新しいコミット "Drop event signatures (#368)"（`d8f89ab`、2026 年 11 月 17 日）が記録されていた。

## Why This Matters

このリポジトリには、SSF、CAEP、RISC の 1.0 Final Specification（承認は 2025 年 9 月 2 日に発表）、2026 年 11 月 13 日に #310 が作った SSF 1.1 と CAEP 1.1 の草案、CAEP Interoperability Profile の草案がある。#368 が変更したのはプロファイルだけで、すべてのイベントを `RS256` と 2048 ビット鍵で署名しなければならない（MUST）という規則を削除した。SSF 自体はもともと署名を必須にしておらず、アルゴリズムも指定していない（SSF 1.0 の 4.1.4 節と 7.1 節）。そのため #368 以降、リポジトリの中に SET の署名方法を固定する規則はない。#355 は SSF 1.1 にストリーム単位のアルゴリズムのネゴシエーションを入れる提案で、まだオープンである。

## Open Questions

- ワーキンググループはプロファイルでイベントの署名そのものを求めるつもりなのか。プロファイルは今も `jwks_uri` で署名鍵を提供することを求めている（プロファイルの 2.3.3 節と 2.4.2 節）。
- #355 は SSF 1.1 に入るのか。プロファイルは SSF 1.1 を参照するように移るのか。
- SSF 1.1 の本文が 1.0 から離れたとき、互換性の方針はどうなるのか。`d8f89ab` 時点で二つの本文はタイトルと文書名しか違わない。
