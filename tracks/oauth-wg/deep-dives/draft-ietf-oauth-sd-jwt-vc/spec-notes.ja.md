# Spec Notes

## 参照文献

ドラフトが挙げる規範的な参照 (-26 の Section 10.1):

- [I-D.ietf-oauth-status-list] draft-ietf-oauth-status-list-21。
- RFC 2119、RFC 8174 (BCP 14)、RFC 2397 (data URL スキーム)、RFC 3986 (URI 構文)、RFC 5280 (X.509 PKI のプロファイル、-24 から規範的)、RFC 5646 (言語タグ)。
- RFC 7515 (JWS)、RFC 7517 (JWK)、RFC 7519 (JWT)、RFC 7800 (proof-of-possession 鍵のセマンティクス)、RFC 8615 (well-known URI)。
- RFC 9110 (HTTP Semantics)、RFC 9111 (HTTP Caching)、RFC 9901 (SD-JWT)。
- [W3C.CSS-COLOR] CSS Color Module Level 3、[W3C.SRI] Subresource Integrity、[W3C.SVG] SVG 1.1 Second Edition (-24 から)。

RFC 6890 は -25 までは規範的な参照だった。-26 で削除された。

参考文献 (-26 の Section 10.2):

- [EUDIW.ARF]、[IANA.IPv4-Special-Registry]、[IANA.IPv6-Special-Registry] (どちらも -26 から)、[IANA.JWT]、[IANA.MediaTypes]、[IANA.well-known]、[NIST-BLOG.VDCE]、[OWASP_SSRF]。
- RFC 6901 (JSON Pointer)、RFC 9205 (Building Protocols with HTTP)、RFC 9535 (JSONPath)、[UAX9] (Unicode 双方向アルゴリズム)。

## 主な変更

-23 から -24 (2026 年 11 月 5 日) への変更。IESG バロットへの対応:

- ヘッダーに `Updates: 7800 (if approved)`、要旨に一文を追加。
- 新しい Section 2.2.2.3.1 "Confirmation Claim Independence": ドラフトは "explicitly overrides that requirement and updates [RFC7800] to nullify that requirement" と述べ、対象は "key-bound SD-JWT VCs, SD-JWTs, and JWTs" である。
- Section 2.5: `x5c` のチェーンを "according to Section 4.1.6 of [RFC7515] and [RFC5280]" に検証する。`x5c` の証明書は "is not a trust anchor merely because it is included there"。`x5c` の下では `iss` は認証されず、受信者は証明書に結び付いていない `iss` を拒否してよく (MAY)、Issuer はそうした結び付きのない `iss` を含めるべきでない (SHOULD NOT)。"The recipient's policy determines which mechanism applies to an Issuer; the SD-JWT VC does not"。受信者は、ポリシーが結び付けてその結び付きを検証した場合を除き、別の方式の入力を Issuer の識別に使ってはならない (MUST NOT)。
- Section 7.3: Issuer は使っている方式が識別するものとなり、MUST の対象は "for any given Issuer" になり、方式は "authenticates only its own inputs" とされた。
- Section 4: `iss` のスキームとホストの小文字化を推奨 (RECOMMENDED)。
- Section 2.2、2.2.2.5、5.3.3、5.5.1.2.1、7.6 のキーワード修正。RFC 5280 と [W3C.SVG] を規範的な参照に追加。Appendix A.1 の例のデータを差し替え。

-25 (2026 年 11 月 5 日) の変更:

- Section 2.2.2.2: "SHOULD treat an SD-JWT VC as being of a given type" が "treats" になった。
- Section 2.4: status の確認は SHOULD のまま。status を確認しない Verifier は失効や一時停止を検知できず "and accepts that risk according to its policy" とする一文を追加。
- Appendix A.1 の例を拡充。履歴: "working on Éric Vyncke's Discuss"。

-26 (2026 年 11 月 6 日) の変更:

- Section 7.1 が、RFC 6890 の代わりに IANA の IPv4 と IPv6 の Special-Purpose Address Registries を引く (Éric Vyncke のコメント)。
- Section 2.2.2.2: 重複した一文 "Holders and Verifiers can treat the SD-JWT VC as a credential of these types." を削除。
- 日付以外の変更はほかにない。

Appendix C の文書履歴によるそれ以前の経緯: HTTP 取得の一般的な節と SSRF の一般化は -19、`aka_vcts` claim は -18、`x5c`/`iss` の明確化と最初の RFC 7800 の注記は -20 で入り、-23 は "some minor fixes" だった。

## 影響分析

- 上流: ドラフトは、SD-JWT の形式と処理を RFC 9901 に、JWT と JWS の規則を RFC 7519 と RFC 7515 に、`x5c` のチェーン検証を RFC 5280 に、`cnf` を RFC 7800 に、HTTP 取得とキャッシュを RFC 9110 と RFC 9111 に依存する。-24 からは RFC 7800 を更新する。`cnf` と並んで `sub` または `iss` を求める RFC 7800 Section 3 の第 2 段落は、すべての JWT について無効になる (Section 2.2.2.3.1)。status list の参照は -22 から規範的である。
- 下流: SD-JWT VC を実装するウォレット、Issuer、Verifier、および `vct` 値、Type Metadata、追加の鍵探索方式を定義するエコシステムのプロファイル (Section 2.2.2.1、2.5)。公開されれば、RFC 7800 の更新は `cnf` を使うすべての JWT プロファイルにも及ぶ。IANA には、`vct`、`vct#integrity`、`aka_vcts`、メディアタイプ `application/dc+sd-jwt`、well-known URI の接尾辞 `jwt-vc-issuer` の登録が求められている (Section 9)。-26 の本文にも、まだ文書参照のプレースホルダーが残っている。
- 互換性: JWT VC Issuer Metadata と `x5c` の両方に対応する受信者は、方式を選ぶのが資格情報ではなく自分のポリシーであること、`x5c` の下で認証されていない `iss` を Issuer として後段に渡していないことを確かめる必要がある (Section 2.5、-24 以降)。テストベクターは -24 と -25 で変わり、-26 の例は -25 と同じである。ドラフトの `typ` 値は `dc+sd-jwt` で、`vc+sd-jwt` に関する移行期間の注記は -19 で削除された。
