# Interop Checklist

節番号は、1.1 または s2s と書いたもの以外は 1.0 のもので、コミット `21ffd6c` 時点である。

- [ ] 各ピアがどの本文を実装しているかを確認する: 1.0 Final、1.0 のエラッタ版ドラフト、1.1、s2s。以下の項目でそれぞれ挙動が違う。
- [ ] `https://<host>/tenant` と `https://<host>/tenant/` からメタデータ URL を組み立てる。エラッタ版と 1.1 では、どちらも `/.well-known/openid-credential-issuer/tenant` になる。1.0 Final には末尾の `/` の規則がなく、文字どおり読めば後者は末尾に `/` が残る(Section 12.2.2、#744、#775)。
- [ ] Credential Offer を値渡し(`credential_offer`)と参照渡し(`credential_offer_uri`)で送り、両方を含む Offer をウォレットが拒否することを確認する(Section 4.1)。
- [ ] 誤った `tx_code` で Pre-Authorized Code の Token Request を送る。1.0 の AS は `invalid_grant`、1.1 の AS は `invalid_tx_code` を返すはずである(1.0 Section 6.3、1.1 Section 7.3)。
- [ ] 誤った `tx_code` を繰り返し送り、上限を超えたら AS が Pre-Authorized Code を無効にし、以後は `invalid_grant` を返すことを確認する(エラッタ版 Section 13.6.3)。
- [ ] 発行者が Nonce Endpoint を持つ場合、`nonce` のない `jwt` proof が `invalid_proof` で、古い `c_nonce` を使った proof が `invalid_nonce` で拒否されることを確認する(Section 8.3.1.2、Appendix F.1)。
- [ ] `cryptographic_binding_methods_supported` のない設定で、ウォレットが `proofs` を省き、発行者がそのリクエストを受け付けることを確認する(Section 14.2、#714)。
- [ ] 遅延レスポンスを返し、ウォレットが `202`、`transaction_id`、`interval` に従い、Deferred Credential Endpoint からクレデンシャルを受け取ることを確認する(Sections 8.3 と 9)。
- [ ] 1.1 の Interactive Authorization: `insufficient_authorization` が 403 Forbidden で返り、エラーのキーが例と同じく `error` であって `error_code` ではないことを確認する(Section 6.2.1、#781、#819)。
- [ ] 1.1: ウォレットが常に最新の `auth_session` を送ること、DPoP を使う場合は別の DPoP 鍵で送られたその `auth_session` を AS が拒否することを確認する(Section 6.2.1、#710、#803)。
- [ ] 1.1 の `auth_via_web`: ウォレットが `request_uri` を一度だけ使い、並行セッションを持つときに `state` を送ること、AS が期限切れの `request_uri` を拒否することを確認する(Section 6.2.1.2、#704、#797)。
- [ ] 1.1: プレゼンテーション要求に `expected_origins` がある場合、それが Authorization Challenge Endpoint から導いた Origin だけを含み、ウォレットがそれを検証することを確認する(Section 6.2.1.1)。
- [ ] 1.1: `credential_dataset_id` があるときは `credential_dataset_tag` もあること、タグが変わったらウォレットが保存済みのクレデンシャルを置き換えることを確認する(Sections 9.3 と 15.4)。
- [ ] s2s: 両方のサーバーが mTLS を使い、`Api-Version` を送り、未対応の版には HTTP 400 と Problem Details で応答することを確認する(s2s Sections 5.1 と 5.3)。
