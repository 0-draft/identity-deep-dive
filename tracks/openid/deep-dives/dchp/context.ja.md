# 背景

## きっかけ

- radar が検出したイベント: 「4 日間で 23 コミット、フィールド名の変更と credential_types の配列化を含む」(トラック `openid`)。`main` で見ると、rebase マージされた 2 つの pull request である。#61 は 2026 年 11 月 4 日に 8 コミットを入れ、`credential_type` を配列にした。#57 は 2026 年 11 月 9 日に 23 コミットを入れ、形式固有の事項を形式別の附属書に移し、`CredentialItem.format` を `credential_format` に改名した。
- 関連するリポジトリ / PR / Issue: <https://github.com/openid/dchp>、pull request #57 と #61、issue #46。

## なぜ重要か

このリポジトリは、OpenID Foundation の Digital Credentials Harmonized Presentation Working Group の作業場所である。仕様の Foreword によれば、本文は ISO/IEC JTC 1/SC 17 WG 10 のメンバーと OpenID Foundation の DCP Working Group のメンバーが共同で作っている。定めているのは、transcript によるチャネル束縛を備えた CBOR の要求・応答モデル 1 つである。ISO/IEC 18013-5 の近接セッション、OpenID4VP、Digital Credentials API のいずれの上でも、ISO mdoc と SD-JWT VC の両方に使えることを目指している。本文は Editor's Copy で、中核の節にはワーキンググループの合意がない。未マージの pull request のいくつか (#76、#77、#81) は整数キー、構造、名前を変える。今実装するなら、どのコミットに従うかを固定する必要がある。

## 未解決の問い

- WG Draft より前に、本文と CDDL はそろうのか。現状は `ChannelBinding` のキーと `purpose_id` (本文は `controller_id`、CDDL は `controlled_id`) で食い違っている。未マージの pull request #76 がこれを直す。
- mdoc の `SessionTranscript` に transcript をどう入れるのか。KB-JWT の `nonce` と `aud` はどうエンコードするのか (issue #10)。
- 最初の Working Group Draft はいつ出るのか (issue #72。2026 年 11 月 4 日に 1〜2 か月ほど先送り)。ISO/IEC 側はどの経路で出すのか (issue #13: PAS か PSDO)。
