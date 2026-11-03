# 相互運用チェックリスト

- [ ] 署名入力が曖昧さなく定まっている。`sig` が `signature` メンバーを除いたオブジェクトの JCS 形式を対象にするかを確認し、二つの実装が同一のバイト列を生成することを確かめる（Section 3、5）。
- [ ] 検証器が、Abstract の COSE_Sign1 と Section 3 の JSON `signature` オブジェクトの食い違いを一貫して扱い、対応しない形式は推測せずに拒否する。
- [ ] JCS と Deterministic CBOR（Section 3）対 JCS のみ（Section 5）について、CBOR でエンコードされた CTA を受け取ったときの検証器の動作を確認する。
- [ ] `Agent-Ctx-Isolation` ヘッダーのエンコーディング（例えば JSON の base64url）が送信側と受信側で合意されており、`_meta.ctxIsolation` の形式が同じオブジェクトを運ぶ（Section 3）。
- [ ] CTA がない呼び出し、不正な CTA、未知の `cta_version` は、状態変更の効果クラスについて拒否される。それ以外のクラスについてはドラフトに記述がない。
- [ ] `kid`（SHA-256 ダイジェスト）が信頼できる Ed25519 鍵に解決され、未知の `kid` はフェイルクローズになる。鍵の配布はドラフトの範囲外である点に注意する。
- [ ] `iat` または `exp` が検証器の時計から 60 秒を超えてずれている CTA は拒否され、監査可能な拒否レシートが出力される（Section 5）。ちょうど 60 秒の境界と、例における `exp` と `iat` の 60 秒の差も試す。
- [ ] 有効期間内に同じ `invocation_id` で再送された CTA の扱いが定まっている。ドラフトは記録を要求していないため、実際の動作を記録する。
- [ ] `STATE_MUTATING` および `PRIVILEGED_ACTUATE` と `MIXED_TAINT` または `UNTRUSTED_INGESTED` の組み合わせは、ステップアップレシートがなければ `ERR_TAINTED_CONTROL_PLANE` を返す（Section 4、規則 2）。
- [ ] `TRUSTED_ONLY` と `STATE_MUTATING` の組み合わせは受理される。また、`TRUSTED_ONLY` の主張と空でない `data_plane_merkle_root` の組み合わせの扱いを決めて文書化する。
- [ ] `QUARANTINED`（Section 6 で登録され、Section 4 では使われない）と、ドラフトに挙げられていない `tool_effect_class` の値は、拒否されるか、文書化された方法で扱われる。
- [ ] 期限切れのステップアップレシート、エージェントランタイム自身が署名したもの、別の `invocation_id` に結び付いたものは拒否される。形式がドラフトで定義されていないため、試験では想定する形式を明記する。
- [ ] `step_up_receipt_hash` が `Agent-Step-Up-Receipt` で運ばれるレシートと一致し、不一致はフェイルクローズになる（Section 3、6）。
- [ ] マークルルートが再現可能である。同じ順序付きチャンクを与えた二つの実装が同じ `data_plane_merkle_root` を生成する。Section 4 の規則 3 が未定義のまま残すリーフのエンコードとツリーの形は書き出しておく。
- [ ] `system_prompt_digest` と `parent_trace_ref` は、Section 4 に規則がないため、検証器が確認するか、明示的に無視するかのいずれかである。
- [ ] 一つのコンテキストセッション内では、定義されたリセット境界を除き、テイントレベルが `MIXED_TAINT` または `UNTRUSTED_INGESTED` から `TRUSTED_ONLY` に戻らない（Section 4、規則 1）。
- [ ] ドラフトが示していないため、試験環境で `ERR_TAINTED_CONTROL_PLANE` を具体的な HTTP ステータスと JSON-RPC エラーコードに対応付ける。
- [ ] メディアタイプ `application/agent-ctx-isolation+json` と二つのヘッダー名を、Section 6 に書かれたとおりに使う。
