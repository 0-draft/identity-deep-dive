# 仕様メモ

## 参考文献

1.0 Final の本文の規範参照のうち、相互運用で特に重要なもの:

- OAuth 2.0(RFC 6749)と、適用できる範囲での RFC 9700 の推奨(Section 5)。Request Object、`request_uri`、`oauth-authz-req+jwt` 型のための JAR(RFC 9101)(Section 5)。Response Mode のための OAuth 2.0 Multiple Response Type Encoding Practices(Section 5.2)。
- JOSE: 署名付きリクエストと `x5c`、`kid`、`jwt` ヘッダーのための JWS(RFC 7515)。暗号化レスポンスのための JWE(RFC 7516)と JWA(RFC 7518)(Section 8.3)。
- クレデンシャルのフォーマット: SD-JWT と SD-JWT VC、mdoc のための ISO/IEC 18013-5、W3C VCDM(Appendix B)。
- OpenID Federation。`openid_federation` Client Identifier Prefix が規範的に参照している。「OpenID Federation の処理規則に従わなければならない(MUST)」とあり、メタデータは Trust Chain から得て、`client_metadata` は無視しなければならない(MUST)(Section 5.9.3)。DCQL の `trusted_authorities` の型の 1 つでもある(Section 6.1.1.3)。この依存は規範本文にあり、例を直しただけの #776 の題名から推測したものではない。
- W3C Digital Credentials API(Appendix A)、DID Core(`decentralized_identifier` プレフィックス)、SIOPv2(Appendix C)。
- 特定のリビジョンに固定された Final 前の依存仕様(Section 13.4): OpenID Federation 1.0 draft -43、SIOPv2 draft -13、SD-JWT draft -22、SD-JWT VC draft -09、Fully-Specified Algorithms draft -13。issue #659 は、出力された SD-JWT VC の規範参照が -10 を指していると指摘している。オープンな #726 がこれを直す予定である。
- エラッタ版ドラフトは、Origin の定義として WHATWG HTML(#719)と、2 つの形式的セキュリティ分析(エラッタ Section 14.1、A.5)を加えた。

## 主な変更

各プルリクエストの差分と変更ファイル一覧で確認した。

- 1.0 のエラッタ版ドラフトと 1.1 の両方: mdoc の `age_over_NN` のデータ要素選択(SHOULD。#800、2026 年 11 月 11 日マージ、エラッタ Section B.2.5)。打ち切りはレスポンスを返さないことを意味し、未対応の `transaction_data` には VP Token を返さず、`invalid_transaction_data` を返すべきである(SHOULD)(#790)。空の VP Token の禁止(#745)。コンパクト形式の SD-JWT だけを使う(#782)。Holder Binding のない W3C VC はそのまま返す(#783)。署名なしのリクエストを求めるプレフィックスでは Request URI レスポンスを `alg: none` にする(#788)。未対応の `request_uri_method` の値では GET に戻らなければならない(MUST)(#798)。「Source of Verifier Metadata」(#735)。`vp_formats_supported` にないフォーマットには `invalid_request`(#801)。`encrypted_response_enc_values_supported` を Verifier メタデータに記載(#802)。`nonce` は 128 ビットのエントロピーを持つべきである(SHOULD)(#722)。`state` は RECOMMENDED(#734)。`expected_origins` は単純な文字列比較で照合する(#719)。`intent_to_retain` がない場合の意味(#730)。`origin` プレフィックスの相互参照(#775)。`invalid_request` の例の `openid_federation`(#776)。`ldp_vc` の例(#787)。信頼できない入力(1.1 は #748、1.0 は #759)。
- 1.1 だけ: `vct_values` と `doctype_value` の照合(#744)、プラットフォーム固有のアプリケーション Origin(#761、Section A.5.1)、HPKE の `session_info`(#703)と `encrypted_response_enc_values_supported` の HPKE 例外(#698)、VP Token をアクセストークンとして使わないこと(#702、Section 14.6)。
- オープン: #803(#744 の文を 1.0 へ)、#808(`transaction_data` の緩和)、#809(Section 5.4 の例、1.1 だけ)、#726(SD-JWT VC の版)、#804(Selectively Disclosable Claim、1.1 だけ)。
- マージされずにクローズ: #647(DCQL のインジェクションについての考慮事項)。コントリビューション契約がなく進展もなかったため 2026 年 6 月 18 日にクローズされ、#748 と #759 で一般化された。

## 影響分析

- 上流: OpenID4VP は、Final 前の SD-JWT VC、SD-JWT、OpenID Federation、SIOPv2 のリビジョンに依存している(Section 13.4)。#744 は、その説明によれば SD-JWT VC draft -15 の `aka_vcts` を使う。`age_over_NN` の規則は ISO 18013-5 Section 7.2.5 に委ねている。
- 下流: Section 3 は、この仕様にはプロファイルが必要だと述べている。`data/landscape-sources.json` は HAIP 1.0 を Final(2025 年 12 月承認)として挙げている。ウォレット、Verifier、OpenID の適合性テスト(Section 14.7)は、上に挙げたエラッタの変更の影響を受ける。
- 互換性: Final に従う実装とエラッタに従う実装は、`alg: none` の Request URI レスポンス(#788)、未知の `request_uri_method` の値(#798)、空の VP Token(#745)、返される `age_over_NN` の識別子(#800)で食い違いうる。1.0 と 1.1 は、#803 がマージされるまで `vct_values` の継承の扱いが違う。
