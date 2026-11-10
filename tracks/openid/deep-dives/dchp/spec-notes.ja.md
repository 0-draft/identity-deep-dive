# 仕様メモ

## 参照

提供された資料には仕様本文が含まれないため、規範的参照と参考参照の一覧は得られない。README は次の文書へのリンクを挙げている。

- ISO/IEC 18013-5: <https://www.iso.org/standard/69084.html>
- OpenID for Verifiable Presentations: <https://openid.net/specs/openid-4-verifiable-presentations-1_0.html>
- Editor's Copy: <https://openid.github.io/dchp/digital-credentials-harmonized-presentation-editors-copy.html>

`insights.md` の以前の概要は、RFC 7515 が規範的参照に追加されたことと、authority key identifier に RFC 5280 の名前が使われたことに言及している。これらはコミット題名のみに基づき、確認できていない。

## 主な変更

- マージ済み: #61 は credential_type を配列にする。
- マージ済み: #57 は credential 形式固有の詳細を形式別附属書に移す。
- マージ済み: #29 は最初の提案を追加し、#11、#15、#7 はビルドと管理用ファイルを追加する。
- 未マージ: #64 deterministic CBOR encoding、#77 Credential Response における 1 クエリ複数 credential と 1 credential 複数クエリ、#74 M、O、C の略語、#76 CDDL と本文の不整合、#81 verifier 用語、#65 reader authentication の X.509 証明書ヘッダー、#83 要素名の大文字小文字、#85 Security Considerations のプレースホルダーと Notices 附属書。
- マージされずにクローズ: #84（#85 の以前の版）、#82 と #73（CredentialQuery の大文字小文字）、#59（scenario_sets の大文字小文字）。

## 影響分析

- Upstream: 調和の対象は、ISO/IEC 18013-5 の Device Request / Device Response と、OpenID for Verifiable Presentations の Authorization Request / Authorization Response である。形式別附属書は ISO mdoc と IETF SD-JWT VC に依存する。
- Downstream: 対面とオンラインの提示に単一の要求プロトコルを必要とするウォレットと検証者。資料は具体的な採用者を挙げていない。
- Compatibility: credential_type の配列化とフィールド名の変更は、以前の Editor's Copy の実装を壊す。大文字小文字の変更はワイヤー上の名前に影響しうる。README は、Editor's Copy が承認された Working Group Draft ではないと述べている。
