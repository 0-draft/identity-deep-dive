# Spec Notes

## References

`d8f89ab` 時点でリポジトリにある文書:

- Shared Signals Framework 1.0（Final）と 1.1（草案）。kramdown-rfc の Markdown
- CAEP 1.0（Final）と 1.1（草案）。kramdown-rfc の Markdown
- CAEP Interoperability Profile 1.0 の draft 01。kramdown-rfc の Markdown
- RISC 1.0（Final）。xml2rfc の XML

SSF の規範的参照には、SET（RFC 8417）、SET のための Subject Identifier（RFC 9493）、push 配送（RFC 8935）、poll 配送（RFC 8936）、JWT（RFC 7519）、JWK（RFC 7517）、OAuth 2.0（RFC 6749）、well-known URI（RFC 8615）、HTTP Semantics（RFC 9110）、OpenID Connect Core、CAEP、RISC が入っている。JWS（RFC 7515）と JWA（RFC 7518）は入っておらず、#355 が両方を加える提案をしている。プロファイルの規範的参照は SSF 1.0 Final を指しており、1.1 の草案ではない。

## Key Changes

- #310（2026 年 11 月 13 日マージ）: 1.0 の本文を変更せずに `SSF_1.0/`、`CAEP_1.0/`、`RISC_1.0/` へ移し、そこから `SSF_1.1/` と `CAEP_1.1/` を作る。SSF 1.1 で変わったのはタイトルと `docname` だけ。CAEP 1.1 は、新規または更新したイベントのためのベース URI `https://schemas.openid.net/secevent/caep/event-type/v1.1` を加え、1.0 のイベントも有効なままにしている。
- #368（2026 年 11 月 17 日マージ）: プロファイルの "Event Signatures" の節（"All events MUST be signed using the `RS256` algorithm with a minimum of 2048-bit keys."）を削除する。ほかのファイルは変わらない。
- #356（2026 年 11 月 16 日にマージされずにクローズ）: RS256 に固定せずに、JWS 署名の必須化、`none` の禁止、RSA 鍵の 2048 ビット以上を残す代案だった。
- #343（2026 年 7 月 21 日マージ）: OIDF 会員レビューに向けてプロファイルの Draft-01 を用意する。
- #349（2026 年 9 月 1 日マージ）: プロファイルに Risk Level Change のユースケースを追加する。
- #315（2026 年 2 月 17 日マージ）: プロファイルに Receiver 要件を追加する。
- オープンな提案: #355 SET 署名アルゴリズムのネゴシエーション（SSF 1.1）、#367 `ssf-configuration` と `jwks_uri` の CORS（SSF 1.1）、#369 ストリーム設定での JSON `null`（SSF 1.1）、#366 プロファイルの Event Subjects への複合サブジェクト、#363 プロファイルでの版ごとの well-known パス、#362 agent と workload のサブジェクト（SSF と CAEP の 1.0 ファイルが対象で、コンフリクトあり）、#329 デバイスの `unmanaged` 状態（CAEP 1.1）。

## Impact Analysis

- Upstream: SSF は SET とその配送の RFC をプロファイルし、JWT と JWK を使う。JWS を直接は参照しておらず、SET への署名も必須にしていない（7.1 節: `jwks_uri` は "MUST be specified if the Transmitter intends to generate signed JWTs"）。
- Downstream: SSF と CAEP の Transmitter および Receiver の実装者と、CAEP Interoperability Profile に従う導入者。
- Compatibility: 現在の SSF 1.1 の規則は 1.0 と同じで、CAEP 1.1 は 1.0 のイベント型を残している。今後の 1.1 の変更についての互換性方針は書かれていない。プロファイルについては、#368 は制約を外す変更なので、RS256 で署名する Transmitter は引き続き準拠する。一方、プロファイルに従って RS256 だけを受け入れていた Receiver は、ほかのアルゴリズムを使う Transmitter に出会う可能性がある。
