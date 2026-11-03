# Context

## きっかけ

draft-ietf-oauth-sd-jwt-vc-23 に対する ART-ART の telechat レビューが Ready を返したため、ドラフトは公開に向かっている (`subject.json`)。`subject.json` にある Datatracker の状態は、Active、Expert Reviews OK、Version Changed - Review Needed、IESG Evaluation、Submitted to IESG for Publication である。

## なぜ重要か

このドラフトは、ウォレットや Verifier の実装が SD-JWT ベースの資格情報に使う形式を定める。その HTTP 取得規則と Type Metadata の規則は、`iss` や `vct` の URL からメタデータを取得するすべての実装に適用される。最新の -23 には規範的な変更が見当たらない (`diff.txt`)。そのため重要なのは周辺の IESG 評価であり、メールには、Section 2.2.2.3 の RFC 7800 の上書きに対する DISCUSS と、Section 7.1 および Section 2.5、7.3 へのコメント付きの支持的な No Objection がある。以前の機械による概要は -23 を整理のためのリリースとしており、差分とは一致するが、バロットの立場には触れていなかった。

## 未解決の問題

- Section 2.2.2.3 の DISCUSS は、RFC 7800 への `Updates:` の関係で解決するのか、文言の変更で解決するのか。
- Section 7.1 は、閉じた環境のために、ローカルに設定された宛先を認めるのか。
- Section 2.5 と Section 7.3 は、`x5c` と HTTPS の `iss` の選択について整合させられるのか。
- -23 より後の改訂で、メタデータ文書のメディアタイプや、Section 5.5.1.2.1、7.6 で疑問視された MUST は変わるのか。
- `mail.txt` のバロットのメッセージは途中で切れており、ほかのコメントが隠れている可能性がある。
