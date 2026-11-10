# 仕様メモ

## 参照

-08 に列挙されている規範的参照（Section 8.1）:

- BCP 195（RFC 8996 と RFC 9325）。-08 で新規。
- draft-ietf-wimse-workload-creds-02（Workload Identity Token。WIT の検証はその Section 5.1.4）。
- RFC 2119 と RFC 8174（キーワード）。
- RFC 3986（Simple String Comparison、Section 6.2.1）。-08 で新規。
- RFC 7942（Implementation Status の節）。
- RFC 9110（HTTP Semantics。CONNECT は Section 9.3.6、対象 URI は Section 7.1）。
- RFC 9421（HTTP Message Signatures）。
- RFC 9457（Problem Details for HTTP APIs）。
- RFC 9525（ホスト名検証、Section 6.3）。
- RFC 9530（Digest Fields）。-08 で新規。

参考情報の参照（Section 8.2）:

- draft-ietf-oauth-transaction-tokens-11（Txn-Token ヘッダー）。
- draft-ietf-wimse-arch-08（用語とアーキテクチャ）。-07 の差分では規範的参照の一覧に、-08 の本文では参考情報の一覧にあり、提供された資料からは移動が見て取れるが、ドラフトはその理由を説明していない。
- draft-ietf-wimse-mutual-tls-02。
- draft-ietf-wimse-wpt-02（DPoP に着想を得た代替方式）。
- IANA の HTTP Message Signature レジストリ。
- RFC 9449（DPoP）。
- RFC 9864（例で用いる Ed25519）。

## 主な変更

- Section 3: リクエストと署名付きレスポンスに対する CONNECT の例外（`@path` と `@query` の代わりに `@method` と `@authority`）。
- Section 3: Content-Digest が RFC 9530 を参照する。nonce には暗号論的に安全な乱数生成器と 64 ビット以上のエントロピー（96 ビット以上が RECOMMENDED）が必要になる。受信者は有効期間外の署名を拒否しなければならない（MUST）。サーバー認証付き TLS 接続とクライアントによるホスト名検証は、この節で要求される。
- Section 3.1: アルゴリズムの基準の記述が、ワークロード資格情報ドラフトのアルゴリズム要件に「従う」に変更された。
- Section 3.2: `wimse-aud` は受信者の信頼済み設定に対して Simple String Comparison で比較され、audience を Host から導出してはならない。
- Section 3.3: `wimse-sign-response` が true の場合、サーバーは署名するかエラーを返す義務を負う。
- Section 3.6: 認証の失敗にはすべて `wimse-signature-invalid` を付けた 400 を返し、どの検査が失敗したかは示さない。必須の署名に失敗した場合は、`wimse-signed-response-unsupported` を付けた 501、または `wimse-signed-response-unavailable` を付けた 400 を返す。problem details は SHOULD である。
- Section 7.2: HTTP Problem Types への三件の登録。
- 再構成: Security Goals は Appendix A、Document History は Appendix B、DPoP との比較は Appendix C になった。Section 6 の Privacy Considerations は参照のみに縮小された。Section 5 の MUST は、Section 3 を参照する説明的な記述に言い換えられた。
- -08 の文書履歴には、シェパードレビュー（#385）、CONNECT の例外（#368）、Simple String Comparison（#396）が挙がっている。nonce、TLS、エラー処理、IANA の変更は、差分には現れているものの、この履歴には記載されていない。
- メタデータ: 有効期限が 2027 年 4 月 23 日に変わり、第二著者の所属が Intuit から Independent に変わった。

## 影響分析

- 上流: 署名の仕組みは RFC 9421、WIT とその検証はWIMSE のワークロード資格情報ドラフト、エラー本文は RFC 9457 と HTTP Problem Types レジストリに依存する。新たに加わった RFC 9530 への参照は、Content-Digest の生成方法に影響する。
- 下流: Section 4 に挙がっている Cofide と wimsey のプルーフオブコンセプト実装の実装者、およびリストで議論されているベクター一式を使うテスト作成者は、-08 の規則に従う必要がある。ドラフトは、どちらの実装がどの版に追随しているかを述べていない。IANA は三つの署名メタデータパラメーターと三つの問題タイプを登録しなければならない。
- 互換性: CONNECT を除き、正しい -07 のメッセージのワイヤ形式が -08 で変わることは示されていないが、検証側が受け入れ得るもの（nonce のエントロピー、audience の完全一致、有効期間）と、サーバーが返さなければならないもの（問題タイプ付きの 400 または 501）は厳しくなる。正規化後の audience 比較、短い nonce、別のエラーコードに依存していた送信者は失敗し得る。ドラフトは移行期間について論じていない。
