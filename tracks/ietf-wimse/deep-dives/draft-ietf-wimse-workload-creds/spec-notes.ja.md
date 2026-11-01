# Spec Notes

## 参照文献

Section 12.1 に挙げられた規範的参照文献:

- [I-D.ietf-oauth-rfc8725bis] JSON Web Token Best Current Practices（ドラフトのリビジョン 10）。03 で追加され、RFC 8725 を置き換えた。
- [I-D.ietf-wimse-mutual-tls] Workload Authentication Using Mutual TLS（ドラフトのリビジョン 03）。
- [WIMSE-ID] Workload Identifier（draft-ietf-wimse-identifier のリビジョン 04）。
- RFC 2119、RFC 8174、RFC 5234、RFC 7515、RFC 7517、RFC 7518、RFC 7519、RFC 7800、RFC 7942、RFC 9110。
- RFC 9525（Service Identity in TLS）。03 で追加された。

Section 12.2 に挙げられた参考参照文献:

- [I-D.ietf-wimse-arch]（リビジョン 08）、[I-D.ietf-wimse-wpt]（リビジョン 02）、[I-D.ietf-wimse-http-signature]（リビジョン 08）、[I-D.ietf-oauth-transaction-tokens]（リビジョン 11）。
- [I-D.ietf-oauth-status-list]（リビジョン 21）、RFC 6960（OCSP）、RFC 9864（fully-specified algorithms）。いずれも 03 で追加された。
- RFC 9457、および HTTP フィールド、JOSE アルゴリズム、JWT クレーム、メディアタイプの各 IANA レジストリ。
- RFC 8414 は参照文献から削除された。

## 主な変更

- 構成: 「Use In Other Protocols」の節が削除され、Section 5 と 6 は「Application-Layer Credentials」と「Transport-Layer Credentials」に改題され、audience に関する Section 5.2 と WIT の検証に関する Section 5.1.3 が追加され、セキュリティ上の考慮事項が番号振り直しされた（新しい Section 9.2）。
- Section 1.2: 対応付け API の要件は、呼び出し側と被呼び出し側の条件、およびサーバーの同一性に関する RFC 9525 への参照に置き換えられた。
- Section 3: Workload Identifier のトラストドメインに結び付けられたアンカーに対してのみ検証する。発行者は既知かつ事前設定済みでなければならない。`iss` に基づく鍵の検索の明示的な禁止は削除され、Section 9.1 と `iss` に基づく鍵配布の削除に委ねられた。
- Section 4: 1 つのランタイムに複数のラベルがある場合の段落は削除された。資格情報ごとにちょうど 1 つの識別子とする規則は維持された。
- Section 5.1: `sub` と `jti` の定義が書き換えられ、`jti` は拒否リストやステータスリストを運用するデプロイメントと結び付けられ、`typ` の指針は RFC 8725 の後継ドラフトを引用するようになった。
- Section 5.3: `WWW-Authenticate` の仕組みがある場合に HTTP 401 を認める。
- Section 9: WIT と WIC の失効に関する方針、プロビジョニング解除後の露出、鍵保護に関する文言、および WIT と PoP は相互 TLS に使わないという明確化。
- 例では `cnf.jwk.alg` に `Ed25519` を使い、WIT の例は再署名された。実装状況には wimsey の項目が加わった。

## 影響分析

- 上流: 用語とトラストドメインは WIMSE アーキテクチャのドラフトに、識別子の構文と `wimse` URI スキームは WIMSE Workload Identifier のドラフトに、JWT ベストプラクティスの後継ドラフトに依存する。規範的参照文献のうち 3 つがまだインターネットドラフトであるため、これらのいずれかの変更がこのドラフトに影響し得る。
- 下流: 相互 TLS、WPT、HTTP 署名の各ドラフトが proof of possession を提供し、Section 5.2 を満たす audience の扱いを定めなければならない。これらが引用しているこのドラフトのセクション番号は移動している可能性がある。WIT と WIC を発行する Identity Server や SPIFFE 系の実装が主な実装者である。
- 互換性: `typ` が `wit+jwt` で、`sub` と `cnf.jwk.alg` を持つ WIT は、引き続き検証できるはずである。挙動が変わるのは、`iss` による鍵検索（サポートされなくなった）、例中のアルゴリズム名（`Ed25519`）、401 に関する指針、削除された対応付け要件である。`EdDSA` がなお受理されるかどうかは、ドラフトには書かれていない。
