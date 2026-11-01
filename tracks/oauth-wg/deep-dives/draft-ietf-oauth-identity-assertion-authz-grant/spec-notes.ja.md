# 仕様メモ

## 参照文献

Section 12.1 に挙げられている規範的参照:

- 策定中のもの: draft-ietf-oauth-identity-chaining-17 (OAuth Identity and Authorization Chaining Across Domains) と draft-parecki-oauth-jwt-dpop-grant-02 (OAuth 2.0 JWT Authorization Grant with DPoP Binding)。
- OAuth のコアとアサーションのフレームワーク: RFC 6749、RFC 7521、RFC 7523、RFC 8693 (Token Exchange)、RFC 8707 (Resource Indicators)、RFC 8414 (Authorization Server Metadata)、RFC 9728 (Protected Resource Metadata。-05 で規範的参照に移った)、RFC 7591 (Dynamic Client Registration)。
- トークンと鍵: RFC 7518、RFC 7519、RFC 7638、RFC 7800、RFC 8725 (JWT BCP)、RFC 9449 (DPoP)、RFC 8705 (mutual TLS)、RFC 9396 (Rich Authorization Requests)、RFC 9493 (Subject Identifiers for Security Event Tokens)。
- その他: RFC 2046、RFC 2119、RFC 3986、RFC 6838、RFC 8174、OASIS SAML Core 2.0、OpenID Connect Core 1.0、OpenID Connect Discovery 1.0、OpenID Connect Enterprise Extensions 1.0 draft 01、および JWT、Media Types、OAuth Parameters の IANA レジストリ。

Section 12.2 に挙げられている参考参照:

- draft-ietf-oauth-client-id-metadata-document-02、RFC 9068 (JWT Profile for OAuth 2.0 Access Tokens)、RFC 9470 (Step Up Authentication Challenge)。

## 主な変更

-06 での変更 (差分: <https://author-tools.ietf.org/iddiff?url1=draft-ietf-oauth-identity-assertion-authz-grant-05&url2=draft-ietf-oauth-identity-assertion-authz-grant-06>):

- 検証に失敗した subject token に対する IdP のエラーが、RFC 8693 Section 2.2.2 を根拠に `invalid_grant` から `invalid_request` に変わった。以前は成功していたリクエストで `invalid_request` を受け取ったクライアントは、新しい subject token を取得して再試行できる (Section 4.3.4.3)。
- クライアントまたはエンドユーザーが対象に対して認可されていない場合に `invalid_target` ではなく `access_denied` を使うことについて、クライアントが禁止された対象と認識されない対象を区別できるようにするためだという説明が新たに加わった (Section 4.3.4.3)。
- Document History のみの変更: 本文がすでに -05 にあった変更について、-05 の項目としてエントリが追加された (下に列挙)。
- 日付とバージョン文字列が 2026 年 10 月 31 日に、有効期限が 2027 年 5 月 4 日に更新された。

-05 で導入されたもの (-04 の本文になく、-05 にある):

- IdP でのクライアント認証の必須化と `invalid_client` (Section 4.3.3)。
- 単一の `audience` 値、`invalid_target` の扱い、Simple String Comparison によるリソースの比較、Token Exchange リクエストでの `resource` の RECOMMENDED 化 (Section 4.3.3)。
- DPoP と並ぶ mTLS の証明書束縛 (Section 9.11.2)。
- `id_jag_signing_alg_values_supported` メタデータと、RS256 の実装必須化 (Section 3、7.1)。
- subject token の保管に関するガイダンス (Section 9.2)。
- Privacy Considerations (Section 10)。

-04 にすでにあり、-05 で拡張されたもの: DPoP に束縛された ID-JAG のための `jwt-dpop` グラントタイプ、-05 で NameID の規則が追加された `saml-nameid` Subject Identifier Format、そして -05 で Client ID Metadata Document と結び付けられたメールおよびカレンダーの例。

## 影響分析

- 上流: 本プロファイルは、RFC 8693 (Token Exchange)、RFC 7523 (JWT bearer グラント)、SSO アサーションのための OpenID Connect または SAML、ディスカバリーのための RFC 8414 と RFC 9728、送信者制約のための RFC 9449 と RFC 8705、そして `identity_chaining_requested_token_types_supported` を定義する Identity Chaining ドラフト (-17 として引用) の上に成り立っている。これらの文書、とくに 2 つの Work in Progress のドラフトの変更は、本ドラフトを変えうる。
- 下流: IdP は、必須のクライアント認証、subject token の種別判定、audience とリソースのポリシー、必要なエラーコードを備えた Token Exchange のプロファイルを実装しなければならない。Resource Authorization Server は、ID-JAG の検証、テナントの扱い、リソースとスコープのポリシー、任意の送信者制約の経路を実装しなければならない。クライアントは両方のサーバーに登録し (または Client ID Metadata Document を使い)、ディスカバリーのメタデータを検証し、subject token の保管を管理しなければならない。要求されている IANA 登録は、メディアタイプ `oauth-id-jag+jwt`、トークンタイプ URI `urn:ietf:params:oauth:token-type:id-jag`、グラントプロファイル URI `urn:ietf:params:oauth:grant-profile:id-jag`、メタデータ名 `authorization_grant_profiles_supported` と `id_jag_signing_alg_values_supported`、JWT クレーム `resource` と `aud_tenant`、そして Subject Identifier Format `saml-nameid` である。
- 互換性: 不正な subject token に対して `invalid_grant` を返す IdP、未認証の Token Exchange リクエストを受け入れる IdP、複数の audience を受け入れる IdP は -06 に適合しない。Resource Authorization Server は、クライアント認証も送信者制約付き ID-JAG もないリクエストを拒否しなければならず、サポートしていない `cnf` 方式の ID-JAG を拒否しなければならない。本ドラフトはまだワーキンググループのドラフトであるため、公開までにワイヤ上の詳細が変わる可能性がある。
