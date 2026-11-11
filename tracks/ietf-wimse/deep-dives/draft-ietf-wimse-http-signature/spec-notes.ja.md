# 仕様メモ

## 参照

-08 に列挙されている規範的参照（Section 8.1）:

- BCP 195（RFC 8996 と RFC 9325）。-08 で新規。
- draft-ietf-wimse-workload-creds-02（Workload Identity Token）。Section 3 と 3.6 は WIT の検証としてその「Section 5.1.4」を参照しているが、-02 に Section 5.1.4 はない（-02 の Section 5.1.3 は `iss` と鍵配布に関する注記）。検証手順は、-08 より後の 2026 年 10 月 30 日に出た workload-creds-03 の Section 5.1.3（「Validating the WIT」）にある。
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
- draft-ietf-wimse-arch-08（用語とアーキテクチャ）。-07 では規範的参照で、-08 では参考情報の参照になった。ドラフトのソースでは `{{!I-D.ietf-wimse-arch}}` が `{{?I-D.ietf-wimse-arch}}` に変わっている。理由はシェパードレビュー（issue #385）にあり、「`wimse-arch` は本当に規範的か。参考情報のはずで、規範的なら downref になる」という指摘への対応である。
- draft-ietf-wimse-mutual-tls-02。
- draft-ietf-wimse-wpt-02（DPoP に着想を得た代替方式）。
- IANA の HTTP Message Signature レジストリ。
- RFC 9449（DPoP）。
- RFC 9864（例で使う完全指定のアルゴリズム識別子 `Ed25519`）。

アルゴリズムそのものは WIT の `cnf.jwk.alg` で決まる（Section 3.1）。-08 は独自の基準を置かず、ワークロード資格情報ドラフトに従う。そちらでは汎用実装は `ES256` をサポートしなければならず（MUST）、`none`、対称鍵、暗号化のアルゴリズムを除く IANA JOSE の署名アルゴリズムが使える。`Ed25519` は例で使われているだけで必須ではなく、非推奨の `EdDSA` もどちらのドラフトでも禁止されていない。

## 主な変更

- Section 3: リクエストと署名付きレスポンスに対する CONNECT の例外（`@path` と `@query` の代わりに `@method` と `@authority`）。
- Section 3: Content-Digest が RFC 9530 を参照する。nonce には暗号論的に安全な乱数生成器と 64 ビット以上のエントロピー（96 ビット以上が RECOMMENDED）が必要になる。受信者は有効期間外の署名を拒否しなければならない（MUST）。サーバー認証付き TLS 接続とクライアントによるホスト名検証は、この節で要求される。
- Section 3.1: アルゴリズムの基準の記述が、ワークロード資格情報ドラフトのアルゴリズム要件に「従う」に変更された。
- Section 3.2: `wimse-aud` は受信者の信頼済み設定に対して Simple String Comparison で比較され、audience を Host から導出してはならない。
- Section 3.3: `wimse-sign-response` が true の場合、サーバーは署名するかエラーを返す義務を負う。
- Section 3.6: 認証の失敗にはすべて `wimse-signature-invalid` を付けた 400 を返し、どの検査が失敗したかは示さない。必須の署名に失敗した場合は、`wimse-signed-response-unsupported` を付けた 501、または `wimse-signed-response-unavailable` を付けた 400 を返す。problem details は SHOULD である。
- Section 7.2: HTTP Problem Types への三件の登録。
- 再構成: Security Goals は Section 6 から Appendix A に移り、Document History は Appendix B、DPoP との比較は Appendix C に繰り下がった。-07 の Section 5.3 だった Privacy Considerations は Section 6 になり、参照だけに縮小された。Section 5 の MUST は、Section 3 を参照する説明的な記述に言い換えられた。
- -08 の文書履歴の項目は三つで、シェパードレビュー（#385）、CONNECT の例外（#368）、Simple String Comparison（#396）である。nonce、TLS、エラー処理、問題タイプ、Privacy、付録、`wimse-arch` の変更は個別には書かれていないが、どれも issue #385 にある Justin Richer のシェパードレビューの指摘に対応している。#385 は 2026 年 10 月 20 日に全項目にチェックが付いた状態で閉じられた。
- メタデータ: 有効期限が 2027 年 4 月 23 日に変わり、第二著者の所属が Intuit から Independent に変わった。

## 影響分析

- 上流: 署名の仕組みは RFC 9421、WIT とその検証は WIMSE のワークロード資格情報ドラフト、エラー本文は RFC 9457 と HTTP Problem Types レジストリに依存する。新たに加わった RFC 9530 への参照は、Content-Digest の生成方法に影響する。
- 下流: Section 4 に挙がっている Cofide（proof-of-concept）と wimsey（alpha）の実装、および issue #419 のベクター一式を使うテスト作成者は、-08 の規則に従う必要がある。Section 4 には最終更新日（2025 年 11 月 13 日、2026 年 9 月 8 日）しかない。Cofide のリポジトリは draft-ietf-wimse-s2s-protocol の実装だと説明しており、最終 push は -08 より前の 2025 年 11 月 14 日である。-08 の後、main ブランチで wimsey の項目は「signed responses as per version -08 of the draft」に更新された（PR #406、2026 年 10 月 23 日マージ）。IANA は三つの署名メタデータパラメーターと三つの問題タイプを登録しなければならない。
- 互換性: CONNECT を除き、正しい -07 のメッセージのワイヤ形式が -08 で変わることは示されていないが、送信者が作るべきもの（CSPRNG による 64 ビット以上のエントロピーを持つ nonce）、検証側による `wimse-aud` の比較（文字列の完全一致）、サーバーが返すべきもの（問題タイプ付きの 400 または 501）は厳しくなる。有効期間外の署名の拒否は、-07 でもすでに MUST だった（当時は Section 5.1）。正規化後の audience 比較、短い nonce、別のエラーコードに依存していた送信者は失敗し得る。ドラフトは移行期間について論じていない。

## テストベクターの再実行

2026 年 11 月 11 日、このリポジトリは issue #419 の 28 本のベクターを、-08 の本文と RFC 9421 から書いた検証器にかけた。P-01、P-02、P-06、N-15 には、11 月 7 日のコメントにある再生成後の値を使った。issue がバイト列そのものを載せているのは、正例と N-15 だけである。それ以外の負例は、正例にどんな変更を加えるかを説明しているだけなので、スクリプトが入力を自分で組み立てた。これらはこのリポジトリによる再構成で、issue のバイト列ではない。スクリプトは [`vectors/verify_419.py`](https://github.com/0-draft/identity-deep-dive/blob/main/tracks/ietf-wimse/deep-dives/draft-ietf-wimse-http-signature/vectors/verify_419.py)、出力は [`vectors/verify_419.log`](https://github.com/0-draft/identity-deep-dive/blob/main/tracks/ietf-wimse/deep-dives/draft-ietf-wimse-http-signature/vectors/verify_419.log) にあり、再現手順は検証ログに書いた。検証器が正しく動いていることは、次のように確かめた。公開されているテスト用の鍵で signature base を組み直して署名し直すと、公開されている 8 本の署名とバイト単位で一致する（ログの 1 節）。

- 入力: P-01〜P-06 と N-15 は公開されているメッセージそのもので、スクリプトはその 8 本の署名をバイト単位で再現する。N-04（本文の差し替え）と N-09（検証時刻を後ろにずらす）は、公開されているメッセージを元の署名のまま使う。N-14 は、公開されている P-02 のレスポンスから署名を取り除いたものである。N-01、N-02、N-03、N-05、N-06、N-07、N-08、N-10、N-11、N-12、N-13 は、変更を加えたあと公開されているテスト用の鍵で署名し直す。N-21 は値が示されていない issue の説明文から組み立て、同じ方法で署名する。N-16〜N-22 は振る舞いを扱うもので、スクリプト自身の送信側・サーバー側・検証側の処理に対する検査として実行する。
- 結果: 受理か拒否かを判定する 22 本（P-01〜P-06、N-01〜N-15、N-21）は、この検証器ですべて期待どおりの判定になった。N-16、N-18、N-19、N-22 は送信側・サーバー側・検証側の振る舞いを扱う。スクリプトはこれらを自分の nonce 生成器、レスポンスの検査、署名の選び方に対して実行している。そのため一致しても、スクリプトの読み方での -08 の本文と期待結果が食い違わないことを示すだけで、他の実装については何も言えない。N-17（どの検査で失敗したかをエラーで明かさない）と N-20（何より先に WIT を検証する）は、メッセージ 1 本からは判定できないため採点していない。
- N-04: issue には、本文の変更で "also makes the signature fail" と書かれている。今回の実行ではそうならなかった。変わるのは本文だけで、`Content-Digest` ヘッダーは元の値のままであり、署名が対象にしているのはそのヘッダーである。検証器が報告した失敗は、受信した本文から計算し直したダイジェストの不一致だけだった（Section 3: "the receiver MUST compute the `Content-Digest` value for the message content received and compare it with the `Content-Digest` value provided in the message"）。
- N-09: 検証時刻 T0+3600 が WIT-A の `exp` と同じなので、WIT の期限切れと署名の有効期間外が同時に起きる。スクリプトは T0+301 でも検査しており、この時刻では有効期間の検査だけが失敗し、やはり拒否される。
- N-15: ES256 の署名は `cnf.jwk` の Ed25519 鍵では署名不正として失敗し、svcC の ES256 鍵では検証に通る。そのため `cnf.jwk` から鍵を取る検証器では、このベクターは Section 3.1 の「ローカルポリシーで許可されないアルゴリズム」の検査まで届かない。
- -08 の本文が送信側の規則としてしか書いていない期待結果: N-06 と N-07（`keyid` と `alg` は "MUST NOT be used"）、N-01（必須のコンポーネントは "MUST be signed"）、N-02 と N-21（CONNECT の送信者は "MUST NOT cover `@path` or `@query`"）。この検証器でこれらの規則を受信側で強制しない設定にすると、署名そのものは正しいので、この 5 本（N-01、N-02、N-06、N-07、N-21）はすべて受理される。他の検証器が拒否するかどうかは、送信側の規則をどう読むかによる。
- P-04 は `@authority` を `svcb.example.com:443` として署名している。-08 の Section 3 は "The `@authority` value is the host and port of the CONNECT target (Section 2.2.3 of RFC9421)" と書く。RFC 9421 の Section 2.2.3 は "The component value MUST be normalized according to the rules provided in [HTTP], Section 4.2.3. Namely, the hostname is normalized to lowercase, and the default port is omitted." と書く。authority 形式の CONNECT の対象にはスキームがなく、443 をその既定のポートとみなすかどうかはどちらにも書かれていない。そのため、この値は実装によって分かれ得る。
