# Context

## きっかけ

`subject.json` にはこのリポジトリを選んだ理由がない(`ai_note` が空)。`openid` トラックで、まだディープダイブのない候補の先頭だった。本ディープダイブは、コミット `21ffd6c`(2026 年 10 月 27 日)時点のドラフトと、引用したプルリクエストで内容を確認した。

## なぜ重要か

OpenID4VCI 1.0 は OpenID Final Specification(2025 年 9 月 16 日承認)で、HAIP 1.0 がプロファイルする OpenID4VC 仕様群のうち発行を担う部分である。作業は 3 か所に分かれた。1.0 のエラッタ(メタデータ URL の規則と Transaction Code の推測対策)、1.1(OAuth 2.0 for First-Party Applications を土台にした Interactive Authorization、Credential Dataset のパラメーター、`invalid_tx_code`)、自前のバックエンドを持つウォレット提供者向けの新しい Server to Server ドラフトである。これらは通信内容が異なるので、実装者は相手がどの本文に従っているかを知る必要がある。

## 未解決の問題

- 末尾の `/` の規則(#775)は 1.0 のエラッタとして公開されるのか。それはいつか。
- 1.1 はいつ実装者向けドラフトになるのか(#687)。
- オープンな s2s の変更(#810、#816)は、識別子の名前と遅延発行をどう決着させるのか。
