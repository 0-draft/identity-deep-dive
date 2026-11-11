# 仕様ノート

## 参考文献

ドラフトが挙げる規範的参考文献（Section 13.1）:

- [OpenID.RPMetadataChoices] OpenID Connect Relying Party Metadata Choices 1.0（-03 で追加）
- [RFC2119] および [RFC8174]（BCP 14）
- [RFC3986] URI の汎用構文
- [RFC6749] OAuth 2.0
- [RFC6819] OAuth 2.0 の脅威モデル
- [RFC6890] 特殊用途 IP アドレスレジストリ
- [RFC7523] OAuth 2.0 クライアント認証のための JWT プロファイル（-02 では参考情報、-03 では規範的参考文献）
- [RFC7591] Dynamic Client Registration
- [RFC8259] JSON
- [RFC8414] Authorization Server Metadata
- [RFC8725] JWT のベストカレントプラクティス（-03 で追加）
- [RFC9110] HTTP のセマンティクス（-03 で追加）
- [RFC9207] 認可サーバーの発行者識別（-03 で追加）
- [RFC9700] OAuth 2.0 セキュリティのベストカレントプラクティス

参考情報の参考文献（Section 13.2）:

- [I-D.draft-ietf-oauth-attestation-based-client-auth]（-12。-02 では -09）
- [I-D.draft-ietf-oauth-rfc7523bis]（新規、-11）
- [I-D.draft-ietf-oauth-spiffe-client-auth]（-03。-02 では -02）
- [IndieAuth]
- [OpenID] Connect Core 1.0
- [OpenID.Federation]（1.1。-02 では 1.0）
- [OWASP.SSRF]（新規）
- [RFC9111] HTTP キャッシュ
- [Solid-OIDC]

## 主な変更

- Section 3: パス `/` は禁止され、クライアントは [RFC3986] の Section 6.2.2、6.2.3 に従って URL を正規化することが推奨され（SHOULD）、サーバーは正規化してはならない（MUST NOT）。
- Section 4.1: 制限が token_endpoint_auth_methods_supported と software_statement の内容にも及び、jwks と jwks_uri を同時に含めてはならない（MUST NOT）。
- Section 4.4、4.5: 機能的 URI と情報提供的 URI の区別、および信頼できない外部入力から文書の内容を導くことの禁止。
- Section 5（セキュリティ上の考慮事項の -02 Section 8.2 から移設し、拡充）: 認証は既定で none となり、token_endpoint_auth_method は推奨されず、RFC7591 の既定値は適用されず、宣言された方式を 1 つも扱えないサーバーは invalid_client で拒否する。
- Section 6: grant_types と response_types の共通部分を求め、空なら invalid_client とする。あわせて Accept ヘッダーの推奨がある。
- Section 6.1: 一時的な失敗と恒久的な失敗の区分、ユーザーエージェントをクライアントへ戻さないこと、トークンエンドポイントと PAR エンドポイントでの invalid_client または HTTP 503。
- Section 6.2: -02 ではサーバーがキャッシュ期間の上限と下限を独自に定めてもよい（MAY）とされていたが、実効的な最大期間を適用すること、指示がない場合に最小期間を適用することがそれぞれ推奨（SHOULD）になった。Expires には従わなくてよく、キャッシュの対象は jwks_uri や logo_uri から取得したデータにも及び、レート制限も認められる（MAY）。エラーや不正な文書をキャッシュしないことは変わらない。
- Section 7（新設）: 認可レスポンスには iss を含めなければならない（MUST）。
- Section 10: URL 混同（10.1）、Accept ヘッダー（10.7.1）、クライアントの提示（10.10）、リソース単位で範囲を限定した永続状態（10.12）の各小節を追加。ロゴの事前取得と自前配信は SHOULD から MUST になり、画像の検証も MUST になった（10.9）。Section 10.7 には OWASP の SSRF チートシートに従うことの推奨（SHOULD）が加わった。
- Section 11.1: 問い合わせ元ごとに文書を変えることへの警告を追加。
- Section 12.1: 仕様文書の参照先が -03 の Section 8 になった。

## 影響分析

- 上流: OAuth 2.0 [RFC6749]、Dynamic Client Registration のメタデータ [RFC7591]、Authorization Server Metadata [RFC8414]、セキュリティのベストカレントプラクティス [RFC9700]、発行者識別 [RFC9207]、および token_endpoint_auth_methods_supported のための OpenID メタデータ選択仕様に依存する。JWT の `typ` に関する推奨は作業中のドラフト（rfc7523bis）を指しており、確定したものではない。
- 下流: URL 形式の client_id を受け入れる認可サーバーの実装、クライアントライブラリ、メタデータ文書の公開者、CIMD Service の運営者。今後の仕様が文書の内容に追加の制限を課す可能性がある（Section 4）。IANA への依頼は、認可サーバーメタデータ名 client_id_metadata_document_supported のみである（Section 12.1）。
- 互換性: Section 5 以降の節番号が -02 と異なる。既定の認証方式、ロゴ、iss の要件により、観測できる挙動が変わる。token_endpoint_auth_method は代替として引き続き読み取れる。本ドラフトは作業中であり、再び変わる可能性がある。
