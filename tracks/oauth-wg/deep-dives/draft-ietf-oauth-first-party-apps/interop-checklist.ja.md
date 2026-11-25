# Interop Checklist

- [ ] チャレンジエンドポイントの URL は `https` スキームを使い、UTF-8 の `application/x-www-form-urlencoded` の POST ボディーを受け付ける (Section 4.1)。
- [ ] `response_type=code` のないリクエストは拒否され、`client_id` は、クライアントが認証または `auth_session` で識別できる場合を除き必須として扱われる (Section 5.1)。
- [ ] `client_id` と、認証またはセッションから得たクライアントの識別が両方あって一致しない場合、リクエストは拒否される (Section 5.1)。
- [ ] サーバーがあるクライアントにトークンエンドポイントでクライアント認証を要求する場合、チャレンジエンドポイントでも要求する (Section 4.1)。
- [ ] `insufficient_authorization` と `redirect_to_web` は HTTP 403 で返され、400 や 401 を想定して書かれたクライアントもこれを処理できる (Section 5.2.2.1、Appendix B)。
- [ ] `invalid_session` とその他のエラーのステータスコードは既定で 400 であり、クライアントは別のコードに依存しない (Section 5.2.2)。
- [ ] `error`、`error_description`、`error_uri` は許可された ASCII 文字だけを含む (Section 5.2.2)。
- [ ] クライアントは保存した `auth_session` を以降のチャレンジリクエストごとに送り、レスポンスに新しい値があれば置き換える (Section 5.3.1)。
- [ ] 別のデバイスから、または別の DPoP 鍵で提示された `auth_session` は拒否される (Section 5.3.1、9.6.1)。
- [ ] クライアントは `auth_session` の有効期間を仮定せず、ログアウト時に値を破棄する (Section 5.3.1、9.6.2)。
- [ ] DPoP を使う場合、すべてのチャレンジリクエストとトークンリクエストで同じ鍵が必要であり、異なる鍵は拒否される (Section 9.5.1)。
- [ ] 最初のリクエストに `code_challenge` がなかった場合、`redirect_to_web` は `request_uri` を含まない (Section 5.2.2.1.1)。
- [ ] `redirect_to_web` に `request_uri` がない場合、クライアントは PKCE を使った通常の認可コードフローを開始する (Section 5.2.2.1.1)。
- [ ] トークンリクエストに `redirect_uri` は含まれず、トークンレスポンスには `auth_session` が含まれることがある (Section 6、6.1)。
- [ ] リフレッシュトークンのリクエストは `insufficient_authorization` を返すことがあり (Section 6.2 と Appendix B.4 の例では 403、ステータスコードの規定はない)、クライアントはチャレンジエンドポイントで続行する (Section 6.2)。
- [ ] リソースサーバーからの [RFC9470] のエラーを受けて、クライアントは `acr_values`、`max_age`、`scope` をチャレンジエンドポイントへ送る (Section 7)。
- [ ] 認可サーバーメタデータは `authorization_challenge_endpoint` を公開している (Section 4.1、8)。
- [ ] レート制限は `auth_session` ごとに適用され、使用する追加パラメーターとエラーコードについて認可サーバー独自のプロファイルが存在する (Section 9.3、Appendix B)。
