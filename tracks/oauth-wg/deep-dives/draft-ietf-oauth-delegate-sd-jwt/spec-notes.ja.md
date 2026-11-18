# Spec Notes

## 参照

Section 10.1 に挙げられた規範的参照:

- OpenID for Verifiable Presentations 1.0 ([OIDF.OID4VP]、2025 年 7 月 9 日)。Section 7.1 で使用。
- RFC 2119。
- RFC 6838。メディアタイプ登録のため。
- RFC 7519。JWT。
- RFC 9901。Selective Disclosure for JSON Web Tokens。基盤となる仕様。

Section 10.2 に挙げられた参考参照:

- IANA JSON Web Token Claims レジストリ。
- IANA Media Types レジストリ。
- RFC 2046。

## 主な変更点

-00 は draft-gco-oauth-delegate-sd-jwt から採択された「Initial Working Group Draft」である。採択前の履歴には -01 (編集上の修正と `kb+sd-jwt+kb` から `kb-sd-jwt+kb` への名称変更) と -00 (初版) がある (Appendix C)。リポジトリのタグ draft-gco-oauth-delegate-sd-jwt-00 と draft-ietf-oauth-delegate-sd-jwt-00 を比べると、規範的な変更もある。連鎖した KB-SD-JWT 同士の間も含め、すべての KB-SD-JWT の前に空の要素がちょうど 1 つ必要になったこと (Section 5.1.1)、JSON Serialization のダイジェストを等価な Compact Serialization に対して計算すること (Section 5.1.2)、最後の Delegate KB-JWT の `sd_hash` が REQUIRED になったこと (Section 5.1.3)、Section 6 が書き直され、`typ` 値が確定し、Key Binding が必要なときに Key Binding のない dSD-JWT を拒否するようになったことである。この draft が導入するもの:

- Compact Serialization と JSON Serialization の dSD-JWT および dSD-JWT+KB の形式 (Section 5.1、5.1.1、5.1.2)。
- KB-SD-JWT。`typ` 値は `kb+sd-jwt` と `kb-sd-jwt+kb`、`delegate_payload` claim、`sd_hash` の代替となる `issuer_jwt_hash` claim を持つ (Section 5.1.4)。
- 連鎖の検証手順 (Section 6)。
- OpenID4VP の `transaction_data` 種別 `delegate` (Section 7.1)。
- `issuer_jwt_hash` claim、およびメディアタイプ `application/kb+sd-jwt` と `application/kb-sd-jwt+kb` の IANA への登録要求 (Appendix A)。

draft のリポジトリで open の PR #15 は、セキュリティ claim (`cnf`、`exp`、`nbf` など) を Delegate Payload からベースの KB-SD-JWT ペイロードへ移し、連鎖に沿ったそれらの意味を定める節を追加する。

## 影響分析

- 上流: この draft は、SD-JWT、Disclosure、KB-JWT の処理を RFC 9901 に、JWT を RFC 7519 に、Section 7.1 の委任の伝送を OpenID4VP に依存する。各段の検証では RFC 9901 Section 7.1 を、`sd_hash` と KB-JWT の検査では RFC 9901 Section 4.3.1 と 7.3 を再利用する (-00 のテキストでは単に「Section 4.3.1」「Section 7.3」と書かれている)。
- 下流: SD-JWT の提示を扱うウォレット、Verifier、エージェント基盤は、連鎖したトークンを解析し、Section 6 の検査を適用する必要が出る。draft は AI エージェントをユースケースとして挙げている (Abstract、Section 1)。
- 互換性: RFC 9901 Section 4 の文法では Disclosure は空にできず、SD-JWT+KB は 1 つの JWT で終わるので、dSD-JWT は SD-JWT にも SD-JWT+KB にも当てはまらない。draft にはネゴシエーションの記述がない。以前の `kb+sd-jwt+kb` という名前は、採択前に `kb-sd-jwt+kb` に置き換えられた。`delegate_payload` は Appendix A の IANA 要求に含まれていない。
