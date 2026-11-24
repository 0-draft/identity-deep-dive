# Spec Notes

## References

ドラフトが挙げる規範的参考文献 (Section 11.1):

- [RFC6749]、[RFC7636]、[RFC8414]、[RFC8259]、[RFC9126]、[RFC9449]、[RFC9470]、[RFC8628]、[RFC8707]、[RFC7591]、[RFC7515]、[RFC7519]、[RFC2119]、[RFC8174]。
- [OpenID]、[OpenID.Native-SSO]、[IANA.oauth-parameters]、[SHS]、[USASCII]。
- [I-D.ietf-oauth-cross-device-security] (-16)。
- [IANA.JWT] は壊れた参照として表示されている。

ドラフトが挙げる参考情報としての文献 (Section 11.2):

- [I-D.ietf-oauth-attestation-based-client-auth] (-09)。
- [I-D.ietf-oauth-browser-based-apps] (-26)。
- [RFC6750]、[RFC8252]、[RFC9207]、[RFC9700]。

## Key Changes

03 と比較したリビジョン 04:

- `insufficient_authorization` と `redirect_to_web` は HTTP 403 でなければならない (Section 5.2.2.1)。Appendix B の `otp_required` の例は 401 から 403 に変わった。
- `request_uri` を含む `redirect_to_web` の例が追加され、[RFC9700] と [RFC9207] に従うべきとする SHOULD が加わった (Section 5.2.2.1.1)。
- クライアントはログアウト時に `auth_session` を破棄すべきである (Section 5.3.1)。
- リクエスト例に `response_type=code` が追加された (Section 5.1)。
- IANA の参照先が Section 5.3.1 と Section 8 に修正された (Section 10)。
- [RFC7159] の参照は削除されて [RFC8259] になり、2 つの RFC が参考文献として追加された。
- Appendix D はこのリビジョンを、編集上の明確化とレスポンスコードの更新と説明している。

## Impact Analysis

- Upstream: [RFC6749] とそのトークンエンドポイントを土台とし、PKCE [RFC7636]、Pushed Authorization Request [RFC9126]、DPoP [RFC9449]、ステップアップ通知 [RFC9470]、サーバーメタデータ [RFC8414] を再利用する。[RFC9470] を変更しないと明記している (Section 3.3、7)。
- Downstream: 認可サーバーはチャレンジエンドポイントとメタデータ値 `authorization_challenge_endpoint` を追加する (Section 8)。クライアントと SDK は `auth_session` の処理を実装する。デプロイメントはリクエストとエラーコードの独自プロファイルを定義する必要がある (Section 1.2、Appendix B)。
- Compatibility: 2 つのエラーコードに 400 や 401 を返していた実装は -04 と異なる。ドラフトはファーストパーティのネイティブアプリ向けであり、ブラウザーベースのアプリでの利用は推奨されない (Section 9.8)。トークンエンドポイントでの 403 が [RFC6749] のクライアントとどう作用するかは資料に書かれていない (Section 6.2)。
