# Context

## Trigger

`subject.json` は、oauth-wg トラックの draft-ietf-oauth-first-party-apps のリビジョン 04 を示している。Datatracker の状態は "Active"、"I-D Exists"、"WG Consensus: Waiting for Write-Up" である。`ai_note` は空であり、選ばれた他の理由は記録されていない。

## Why This Matters

このドラフトは、ファーストパーティのネイティブアプリがアプリ内でサインインするための標準的なエンドポイントを OAuth サーバーに与え、ブラウザーを往復する方法の代替とする (Section 1)。リビジョン 04 は `insufficient_authorization` と `redirect_to_web` に HTTP 403 を必須とした (Section 5.2.2.1)。これは以前の例に基づいて書かれたサーバーや SDK に影響する。ドラフトは対話の詳細の大半をデプロイメント固有のプロファイルに委ねており (Section 1.2)、相互運用性は、資料の中ではまだ定義されていないプロファイルに依存する。

## Open Questions

- `invalid_session` のステータスコードは示されていない (Section 5.2.2.1)。
- トークンエンドポイントでの HTTP 403 が、[RFC6749] の Section 5.2 の参照と並んで記述されている (Section 6.2)。
- `auth_session` の IANA 登録は使用場所をトークンレスポンスのみとしている (Section 10.1)。
- 壊れた `[IANA.JWT]` 参照と OAuth 2.1 に関する TODO がテキストに残っている (Section 2.1、11.1)。
- first-partyness の検証方法は範囲外である (Section 9.1)。
