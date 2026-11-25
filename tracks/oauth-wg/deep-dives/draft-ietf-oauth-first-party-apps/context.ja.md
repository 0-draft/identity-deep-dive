# Context

## Trigger

draft-ietf-oauth-first-party-apps のリビジョン 04 は、oauth-wg でまだ deep dive のない候補の先頭だった。Datatracker の状態は "Active"、"I-D Exists"、"WG Consensus: Waiting for Write-Up" である。-03 の WG Last Call は 2026 年 6 月 25 日から 7 月 13 日までで、その途中の 7 月 1 日に -04 が出た。WG の状態は 7 月 15 日に "Waiting for Write-Up" に移った。

## Why This Matters

このドラフトは、ファーストパーティのネイティブアプリがアプリ内でサインインするための標準的なエンドポイントを OAuth サーバーに与え、ブラウザーを往復する方法の代替とする (Section 1)。リビジョン 04 は `insufficient_authorization` と `redirect_to_web` に HTTP 403 を必須とした (Section 5.2.2.1)。これは -03 (既定は 400、Appendix B.3 の例は 401) に合わせて書かれたサーバーや SDK に影響する。ドラフトは対話の詳細の大半をデプロイメント固有のプロファイルに委ねており (Section 1.2)、相互運用性は、Appendix B の例以外はドラフトが定義していないプロファイルに依存する。

## Open Questions

- `invalid_session` にはステータスコードが示されていないため、Section 5.2.2 の既定の 400 になる (Section 5.2.2.1)。
- トークンエンドポイントでの `insufficient_authorization` にはステータスコードが定められていない。例は 403 だが、[RFC6749] の Section 5.2 の既定は 400 である (Section 6.2)。
- `auth_session` の IANA 登録は使用場所をトークンレスポンスのみとしている (Section 10.1)。
- 壊れた `[IANA.JWT]` 参照と OAuth 2.1 に関する TODO がテキストに残っている (Section 2.1、11.1)。
- first-partyness の検証方法は範囲外である (Section 9.1)。
