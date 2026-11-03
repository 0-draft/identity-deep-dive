# Spec Notes

## 参照文献

ドラフトが挙げる規範的参照 (Section 10.1):

- [I-D.ietf-oauth-status-list] draft-ietf-oauth-status-list-21。
- RFC 2119、RFC 8174 (BCP 14)、RFC 2397 (data URL スキーム)、RFC 3986 (URI 構文)、RFC 5646 (言語タグ)、RFC 6890 (特別用途 IP アドレスレジストリ)。
- RFC 7515 (JWS)、RFC 7517 (JWK)、RFC 7519 (JWT)、RFC 7800 (proof-of-possession 鍵のセマンティクス)、RFC 8615 (well-known URI)。
- RFC 9110 (HTTP Semantics)、RFC 9111 (HTTP Caching)、RFC 9901 (SD-JWT)。
- [W3C.CSS-COLOR] CSS Color Module Level 3、[W3C.SRI] Subresource Integrity。

参考参照 (Section 10.2):

- [EUDIW.ARF]、[IANA.JWT]、[IANA.MediaTypes]、[IANA.well-known]、[NIST-BLOG.VDCE]、[OWASP_SSRF]。
- RFC 6901 (JSON Pointer)、RFC 9205 (Building Protocols with HTTP)、RFC 9535 (JSONPath)、[UAX9] (Unicode 双方向アルゴリズム)。

## 主な変更

-22 から -23 への変更 (`diff.txt`):

- 有効期限と文書日付の更新 (2027 年 5 月 4 日と 2026 年 10 月 31 日)。
- Figure 7、8、10、26 と Appendix A.1 の例の署名を再生成。Figure 8、26、27 の KB-JWT の `iat` と `sd_hash` が変わった。
- 編集上の修正: Section 5.5.1.1 の `text_color` の文言、Section 9.3 の "in by [RFC8615]"、OWASP の URL から末尾スラッシュを削除。
- 謝辞に Su-hyeon Forten Lee を追加。-23 の履歴は "some minor fixes" である。
- 規範的な要件に見える変更はない。

以前の改訂の背景 (Appendix C の文書履歴による): HTTP 取得の一般的な節と SSRF の一般化は -19、`aka_vcts` claim は -18、`x5c`/`iss` の明確化と RFC 7800 に関する注記は -20 で入った。

## 影響分析

- 上流: ドラフトは、SD-JWT の形式と処理を RFC 9901 に、JWT と JWS の規則を RFC 7519 と RFC 7515 に、`cnf` を RFC 7800 に、HTTP 取得とキャッシュを RFC 9110 と RFC 9111 に依存する。Section 2.2.2.3 は、`sub` または `iss` を求める RFC 7800 Section 3 の要件から逸脱しており、資料には `Updates:` ヘッダーが示されていない。status list の参照は -22 から規範的である。
- 下流: SD-JWT VC を実装するウォレット、Issuer、Verifier、および `vct` 値、Type Metadata、追加の鍵探索方式を定義するエコシステムのプロファイル (Section 2.2.2.1、2.5)。IANA には、`vct`、`vct#integrity`、`aka_vcts`、メディアタイプ `application/dc+sd-jwt`、well-known URI の接尾辞 `jwt-vc-issuer` の登録が求められている (Section 9)。本文には文書参照のプレースホルダーが残っている。
- 互換性: -23 にプロトコルの変更は見当たらないため、-22 の実装は相互運用できるはずである。異なるのはテストベクターだけである。ドラフトの `typ` 値は `dc+sd-jwt` で、`vc+sd-jwt` に関する移行期間の注記は -19 で削除された。Section 2.2.2.3 の未解決の DISCUSS がどう決着するかは分からない。
