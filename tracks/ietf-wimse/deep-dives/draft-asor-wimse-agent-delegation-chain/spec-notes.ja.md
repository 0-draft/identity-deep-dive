# Spec Notes

## 参照文献

ドラフトが列挙する規範的参照文献（Section 12.1）:

- [I-D.ietf-oauth-status-list] Token Status List、draft-ietf-oauth-status-list-21
- RFC 2119 と RFC 8174（BCP 14）、RFC 5234（ABNF）、RFC 6749（OAuth 2.0）
- RFC 7515（JWS）、RFC 7519（JWT）、RFC 7800（proof-of-possession key semantics）
- RFC 8032 と RFC 8037（JOSE における Ed25519）、RFC 8785（JCS）
- RFC 9068（JWT アクセストークン）、RFC 9396（Rich Authorization Requests）、RFC 9449（DPoP）
- RFC 9728（Protected Resource Metadata）、RFC 9864（fully-specified algorithms）

参考的参照文献（Section 12.2）には次のものが含まれる:

- 権限委譲トークンの系譜: Macaroons、Biscuit、RFC 2693（SPKI）
- 関連ドラフト: draft-niyikiza-oauth-attenuating-agent-tokens-02、draft-coetzee-oauth-spt-txn-tokens-03、draft-sweeney-wimse-credential-delegation-01、draft-ietf-wimse-aims-00、draft-ietf-wimse-identifier-04、draft-reece-wimse-cross-org-delegation-02、draft-jackson-wimse-evaluation-04、draft-hamr-oauth-agent-delegation-03、draft-ietf-oauth-identity-chaining-17
- -03 で新規: draft-mcguinness-oauth-actor-profile-01、draft-mw-oauth-actor-chain-02、draft-gilda-audit-agent-audit-record-02
- その他: RFC 7009（失効）、RFC 7942（実装状況）、RFC 8693（Token Exchange）、RFC 8705（mTLS）、RFC 9964（ML-DSA）

## 主な変更

- Section 1.2 を追加。OAuth の "act" クレームを使う actor ドラフトとの関係を扱う。
- Table 1 に行を追加し、その後に段落を置いた。Principal の資格は、チェーンからもリクエストからも確立されないと述べている（Section 6.1）。
- Section 6.4 はバインディングの隙間と記録の隙間を分け、draft-gilda-audit-agent-audit-record を参照する。アンカーのトポロジーは強制しない。
- Section 10 は "del_depth"、"del_max_depth"、"par_hash" の登録要求を取り下げた。"Agent Delegation Constraint Types" レジストリの要求は残る。
- Section 6 のステップ 5 は、now が exp 未満であることを要求する。
- Section 7 は DPoP による保持者バインディングのみを規定する。mTLS は後のリビジョンに委ねられる。
- Section 4.4 は、親が持たない詳細型を子が加えた場合は拡大として扱うという規則を、後のリビジョン向けに記録している。-03 ではそのトークンは不正（malformed）である。
- Appendix B のベクターは 36 個で、-01 の 20 個の集合は変更されない。Appendix C は「Changes Since -02」に改称され、従来の一覧は Appendix D になった。
- Section 11 は、ライブラリのバージョン attenu-guard 0.22.0 と attenu-guard-ts 0.16.0、および -02 のベクターに対する独立した実行結果（成功 20、失敗 5、宣言済みの未対応 10）を報告している。

## 影響分析

- 上流: RFC 9068、RFC 9396、RFC 9449、RFC 7800、RFC 8785、RFC 9864 の上に構築され、失効には draft-ietf-oauth-status-list を用いる。draft-reece-wimse-cross-org-delegation の要件 R1 と R5 を満たすと主張し、"client_id" と "sub" については draft-ietf-wimse-aims に従う。クレーム名は draft-niyikiza-oauth-attenuating-agent-tokens と重なる。
- 下流: エージェントのチェーンを検証するゲートウェイや執行点、記録済みのチェーンを再検査する監査者、スコープの語彙や監査記録に関する補完文書。ドラフトはスコープの語彙について補完文書を想定しており（Section 4.5）、ルート鍵の材料の保持には draft-gilda-audit-agent-audit-record を参照している。
- 互換性: -03 は -01 の形のチェーンのための移行モードを定義していない。-01 の 20 個のベクターは新しいリビジョンに適合せず、バイト単位で固定されている。now が exp 未満という変更と mTLS の削除は、-02 からの挙動の変更である。"del_max_depth" の意味は niyikiza のドラフトと異なるため、同じ深さの値がそちらでは通り、本ドラフトのステップ 3 では失敗しうる。
