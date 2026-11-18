# 相互運用チェックリスト

どの項目も MUST または MUST NOT を確かめるものである。節番号は、エラッタ(`66f5ff9` 時点の `1.0/` のドラフト)または 1.1 と書いたもの以外は 1.0 Final のものである。`age_over_NN` の選択や HTTP リダイレクトの扱いのような SHOULD の挙動は、ここではなく README の「実験」に置いた。

- [ ] `typ: oauth-authz-req+jwt` のない Request Object を送り、ウォレットがそれを処理しないことを確かめる(Section 5)。
- [ ] プレフィックスの違いも含め、`client_id` が URL パラメーターの `client_id` と違う Request Object を送り、ウォレットがリクエストの処理を打ち切ることを確かめる(Section 5.10.1)。エラッタの本文では、打ち切りはウォレットが一切レスポンスを返さないことを意味する(エラッタ Section 5.10.1、#790)。
- [ ] `request_uri_method=post` で `wallet_nonce` を送らせ、それを含まない Request Object を返す。次に POST に HTTP エラーで応える。どちらの場合もウォレットは打ち切らなければならない(MUST)(Section 5.10.1、5.10.2)。
- [ ] `x509_san_dns`、`x509_hash`、`decentralized_identifier`、`verifier_attestation` について、ウォレットがプレフィックスの示す鍵で署名を検証し、証明書チェーンまたは証明を検証することを確かめる。それぞれで署名なしのリクエストを送り、`invalid_request` を期待する(Section 5.9.3、8.5)。
- [ ] DC API 以外での `x509_san_dns` について、FQDN が Client Identifier と違う `redirect_uri` が、ウォレットがその Client Identifier を信頼していない限り拒否されることを確かめる(Section 5.9.3)。
- [ ] `openid_federation` について、Trust Chain と食い違う `client_metadata` を送り、ウォレットがそれを無視することを確かめる(Section 5.9.3)。
- [ ] リクエストで `client_id=origin:...` を送り、ウォレットが拒否することを確かめる(Section 5.9.3)。
- [ ] Request URI を使う `redirect_uri` について、`alg: none` の Request Object を返し、エラッタまたは 1.1 に従うウォレットが受け入れることを確かめる。Final の本文に従うウォレットは署名付きのオブジェクトを期待するが、`redirect_uri` プレフィックスでは署名できない(Section 5.10.1、エラッタ Section 5.10.1、#788)。
- [ ] 別のトランザクションの Verifiable Presentation と、別の Client Identifier 向けに作られた Verifiable Presentation を再送し、Verifier がレスポンスを拒否することを確かめる(Section 14.1.2)。
- [ ] DC API 以外で `require_cryptographic_holder_binding: false` のクレデンシャルを要求し、Verifier が新しい `state` を送り、`state` が違うレスポンスを拒否することを確かめる(Section 5.3)。
- [ ] VP Token の形を確かめる。キーは Credential Query の `id` で、`multiple` が `true` でない限りキーごとに Presentation はちょうど 1 つ、一致するものがない任意のクエリにはキーがない(Section 8.1)。エラッタの本文では VP Token は空であってはならず(MUST NOT)、返すものがないウォレットはエラーレスポンスを送る(エラッタ Section 8、8.1、#745)。
- [ ] ウォレットが満たせない `claim_sets` を持つ DCQL クエリと、満たせない必須の `credential_sets` の選択肢を持つクエリを送る。前者ではウォレットがそのクレデンシャルを返さず、後者ではクレデンシャルを 1 つも返さないことを確かめる(Section 6.4.1、6.4.2)。
- [ ] クエリの `values` や `trusted_authorities` に反するクレデンシャルを返し、Verifier が自分の確認でそれを拒否することを確かめる(Section 6.4.1、14.9)。
- [ ] `response_mode=direct_post` で `response_uri` と `redirect_uri` の両方を送り、`invalid_request` を期待する(Section 8.2)。Response URI が 200 と JSON で応え、JSON に `redirect_uri` があればウォレットがリダイレクトすることを確かめる(Section 8.2)。
- [ ] `direct_post` で `redirect_uri` が返された場合に、Response Code なしで Verifier のフロントエンドからレスポンスを取り出そうとし、Verifier が拒むことを確かめる(Section 14.2)。
- [ ] `direct_post.jwt` または `dc_api.jwt` で、JWE の `alg` が選んだ JWK の `alg` と同じであること、鍵に `kid` があれば JWE ヘッダーがそれを繰り返すこと、`encrypted_response_enc_values_supported` がなければ `enc` が `A128GCM` であることを確かめる(Section 8.3)。
- [ ] `transaction_data` に対応しないウォレットにそれを送り、リクエストを拒否することを確かめる(Section 5、8.4)。エラッタの本文では VP Token を返してはならない(MUST NOT)(エラッタ Section 8.4、8.5、#790)。どのエラーコードを使うかは SHOULD の水準なので、ここでは確かめない。オープンな #808 の後に再確認する。
- [ ] DC API: リクエストがその形に合わせて `openid4vp-v1-unsigned`、`openid4vp-v1-signed`、`openid4vp-v1-multisigned` のいずれかを使うことを確かめる(Section A.1)。
- [ ] DC API の署名付きリクエスト: `client_id` と `expected_origins` を含むことを確かめ、次に呼び出し元の Origin を含まない `expected_origins` のリクエストを送り、ウォレットがエラーを返すことを確かめる(Section A.2)。エラッタの本文では比較は単純な文字列比較なので、`https://verifier.example.com/` は `https://verifier.example.com` に一致しない(エラッタ Section A.2、#719)。
- [ ] DC API: Presentation の audience が、署名付きリクエストの場合も、Client Identifier ではなく `origin:` に Origin を続けたものであることを確かめる(Section A.4)。
- [ ] エラッタの本文での SD-JWT VC: 各 Presentation がコンパクト形式の SD-JWT または SD-JWT+KB の文字列で、JWS JSON Serialization を使っていないことを確かめる(エラッタ Section B.3.6、#782)。
- [ ] `require_cryptographic_holder_binding: false` の W3C VC: ウォレットが Verifiable Presentation に包まず、Verifiable Credential そのものを返すことを確かめる(Section B.1、エラッタ Section B.1、#783)。
- [ ] 1.1 だけ: `vct` も `aka_vcts` も `vct_values` にないクレデンシャルと、`docType` が `doctype_value` でない mdoc が、Credential Query を満たさないことを確かめる(1.1 Section B.3.5、B.2.3、#744)。1.0 の実装には、#803 がマージされるまでこの規則はない。
