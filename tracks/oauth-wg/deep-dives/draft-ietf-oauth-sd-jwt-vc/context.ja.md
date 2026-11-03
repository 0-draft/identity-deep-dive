# Context

## きっかけ

draft-ietf-oauth-sd-jwt-vc-23 に対する ARTART の telechat レビューが 2026 年 11 月 3 日に Ready を返したため、ドラフトは公開に向かっている (`subject.json`)。Datatracker (2026 年 11 月 4 日時点) では、ドラフトは Active、WG の状態は Submitted to IESG for Publication、IESG の状態は IESG Evaluation で、2026 年 11 月 5 日の telechat の議題に載っている。IANA のレビュー状態は Version Changed - Review Needed で、これは 2026 年 10 月 31 日に -23 が投稿された時点で Datatracker が設定したものである (-22 では IANA OK - Actions Needed だった)。IANA の専門家レビューの状態は Expert Reviews OK である。

## なぜ重要か

このドラフトは、ウォレットや Verifier の実装が SD-JWT ベースの資格情報に使う形式を定める。その HTTP 取得規則と Type Metadata の規則は、`iss` や `vct` の URL からメタデータを取得するすべての実装に適用される。最新の -23 には規範的な変更が見当たらない (`diff.txt`)。そのため重要なのは周辺の IESG 評価である。Mike Bishop は Section 2.2.2.3 の RFC 7800 の上書きに DISCUSS を出しており、Mahesh Jethanandani と Roman Danyliw が No Objection のコメントでそれを支持している。Mahesh Jethanandani はあわせて Section 7.1 と Section 2.5、7.3 にも触れ、Roman Danyliw も Section 2.5、7.3 の指摘を支持している。以前に自動生成された概要は -23 を整理のためのリリースとしており、差分とは一致するが、バロットの立場には触れていなかった。

## 未解決の問題

- Section 2.2.2.3 の DISCUSS は、RFC 7800 への `Updates:` の関係で解決するのか、文言の変更で解決するのか。
- Section 7.1 は、閉じた環境のために、ローカルに設定された宛先を認めるのか。
- Section 2.5 と Section 7.3 は、`x5c` と HTTPS の `iss` の選択について整合させられるのか。
- -23 より後の改訂で、メタデータ文書のメディアタイプや、Section 5.5.1.2.1、7.6 で疑問視された MUST は変わるのか。
- Mahesh Jethanandani が提案するように、後の改訂で `extends` のチェーンの深さや資格情報ごとの取得総数に上限が設けられるのか。
