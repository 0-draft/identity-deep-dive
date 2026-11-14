# Context

## きっかけ

`subject.json` にはこのリポジトリを選んだ理由がない(`ai_note` が空)。`openid` トラックで、まだディープダイブのない候補の先頭だった。本ディープダイブは、コミット `41c8c66`(2026 年 11 月 10 日)時点のドラフトと、引用したプルリクエストと issue で内容を確認した。

## なぜ重要か

OpenID4VCI 1.0 は OpenID Final Specification(2025 年 9 月 16 日承認)で、HAIP 1.0 がプロファイルする OpenID4VC 仕様群のうち発行を担う部分である。作業は 3 か所に分かれた。1.0 のエラッタ(メタデータ URL の規則と Transaction Code の推測対策)、1.1(OAuth 2.0 for First-Party Applications を土台にした Interactive Authorization、Credential Dataset のパラメーター、`invalid_tx_code`)、自前のバックエンドを持つウォレット提供者向けの新しい Server to Server ドラフトである。これらは通信内容が異なるので、実装者は相手がどの本文に従っているかを知る必要がある。

## 未解決の問題

- 末尾の `/` の規則(#775)は 1.0 のエラッタとして公開されるのか。それはいつか。
- 1.1 はいつ実装者向けドラフトになるのか(#687)。
- 識別子の名前変更(#810)がマージされた今、s2s の遅延発行(#816)はどう決着するのか。
- 1.0 のエラッタは、Section 6.3(Transaction Code の誤りに `invalid_grant`)と Section 13.6.3(Transaction Code が無効だと分かるエラー)を整合させるのか。
- 1.1 の識別子の綴り(#811)とフォーマットごとの提示の束縛(#812)はどう決着するのか。
