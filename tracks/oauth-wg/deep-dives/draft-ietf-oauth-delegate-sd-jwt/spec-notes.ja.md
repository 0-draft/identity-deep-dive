# Spec Notes

## 参照

Section 10.1 に挙げられた規範的参照:

- OpenID for Verifiable Presentations 1.0 ([OIDF.OID4VP])。Section 7.1 で使用。
- RFC 2119。
- RFC 6838。メディアタイプ登録のため。
- RFC 7519。JWT。
- RFC 9901。Selective Disclosure for JSON Web Tokens。基盤となる仕様。

Section 10.2 に挙げられた参考参照:

- IANA JSON Web Token Claims レジストリ。
- IANA Media Types レジストリ。
- RFC 2046。

## 主な変更点

`diff.txt` は用意されていない。-00 は draft-gco-oauth-delegate-sd-jwt から採択された「Initial Working Group Draft」である。採択前の履歴には -01 (編集上の修正と `kb+sd-jwt+kb` から `kb-sd-jwt+kb` への名称変更) と -00 (初版) がある (Appendix C)。この draft が導入するもの:

- Compact Serialization と JSON Serialization の dSD-JWT および dSD-JWT+KB の形式 (Section 5.1、5.1.1、5.1.2)。
- KB-SD-JWT。`typ` 値は `kb+sd-jwt` と `kb-sd-jwt+kb`、`delegate_payload` claim、`sd_hash` の代替となる `issuer_jwt_hash` claim を持つ (Section 5.1.4)。
- 連鎖の検証手順 (Section 6)。
- OpenID4VP の `transaction_data` 種別 `delegate` (Section 7.1)。
- `issuer_jwt_hash` claim、およびメディアタイプ `application/kb+sd-jwt` と `application/kb-sd-jwt+kb` の IANA への登録要求 (Appendix A)。

## 影響分析

- 上流: この draft は、SD-JWT、Disclosure、KB-JWT の処理を RFC 9901 に、JWT を RFC 7519 に、Section 7.1 の委任の伝送を OpenID4VP に依存する。各要素の検証では RFC 9901 Section 7.1 を再利用する。
- 下流: SD-JWT の提示を扱うウォレット、Verifier、エージェント基盤は、連鎖したトークンを解析し、Section 6 の検査を適用する必要が出る。draft は AI エージェントをユースケースとして挙げている (Abstract、Section 1)。
- 互換性: 空の要素 `~~` と変更された KB-JWT のため、dSD-JWT は RFC 9901 の SD-JWT 提示としては有効でなく、draft にはネゴシエーションの記述がない。以前の `kb+sd-jwt+kb` という名前は、採択前に `kb-sd-jwt+kb` に置き換えられた。`delegate_payload` は Appendix A の IANA 要求に含まれていない。
