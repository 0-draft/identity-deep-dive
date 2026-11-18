# 背景

## きっかけ

`subject.json` には選定理由がない(`ai_note` は空)。OpenID4VP は、`tracks/openid/data/normalized/candidates.json` でディープダイブのない `openid` の候補の 2 番目だった。`tracks/openid/data/normalized/insights.json` の日次ブリーフィングは、#800(ブランチ `718-age-over-nn`)のマージを差分なしで記録していた。#800 は 2026 年 11 月 11 日にマージされ、`age_over_NN` のデータ要素選択規則を 1.0 のエラッタ版ドラフトと 1.1 の両方に加えた(どちらも Section B.2.5)。このディープダイブは、1.0 Final の本文(タグ `1.0-final`)、コミット `66f5ff9`(2026 年 11 月 11 日)時点のドラフト、引用したプルリクエストと issue で確認した。

## なぜ重要か

OpenID4VP 1.0 は OpenID Final Specification であり(告知の日付は 2025 年 7 月 10 日)、OpenID4VC ファミリーのうち提示を担う仕様である。作業は 2 か所に移っている。1.0 のエラッタ版ドラフト(リビジョン `-31`、Document History に 26 件の変更)と、HPKE によるレスポンス暗号化、より厳密な型の照合、DC API の Origin についての要件を加えた 1.1(リビジョン `-01`)である。エラッタの変更のいくつかは通信上で見える。`redirect_uri` プレフィックスでの `alg: none` の Request Object、空の VP Token の禁止、`request_uri_method` での GET への切り替え、mdoc のレスポンスで別の `age_over_NN` 要素が返ることである。実装者は、相手がどの本文に従っているかを知る必要がある。

## 未解決の問題

- `1.0/` のドラフトはいつエラッタセット 1 として承認されるか。オープンな #803、#808、#726 はそこに入るか。
- #808 は、#790 が明確化した `transaction_data` の拒否の規則を置き換えるか。
- 規則が SHOULD である以上(エラッタ Section B.2.5)、Verifier は別の `age_over_NN` 識別子をどう扱うか。
- Section 5.9.3 がウォレットに任せている DC API でのリクエスト署名の検証を、どのプロファイルが必須にするか。
