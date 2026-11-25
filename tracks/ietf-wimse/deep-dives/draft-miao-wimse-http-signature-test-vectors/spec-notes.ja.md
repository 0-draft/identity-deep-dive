# 仕様ノート

## 参考文献

Section 9.1 に挙げられている規範的参照:

- RFC 2119 と RFC 8174（BCP 14）。要件のキーワード。
- RFC 6979。決定的 ECDSA。ES256 の署名に使う。
- RFC 8032。EdDSA。Ed25519 の署名に使う。
- RFC 9421。HTTP Message Signatures。署名ベース（Section 2.5）と派生コンポーネントのため。
- draft-ietf-wimse-http-signature-08（2026 年 10 月）。基底仕様。-09 は本ドラフトより後の 2026 年 11 月 20 日に出た。

Section 9.2 に挙げられている参考文献:

- RFC 8792。図中の行の折り返しのため。
- draft-ietf-wimse-workload-creds。リビジョンの指定はない。N-20 は基底仕様から WIT 検証の手順への参照を引用し、どのベクターも WIT を検証するが、参照は参考扱いである。

本文で言及されているが挙げられていないもの:

- RFC 3986 Section 6.2.1（Simple String Comparison）。N-10 の引用の中にある。
- ietf-wg-wimse/draft-ietf-wimse-s2s-protocol の issue #419 と、v3（DOI 10.5281/zenodo.24184599）と v4（DOI 10.5281/zenodo.24203971）の Zenodo の記録（Section 1、Appendix B）。

## 主な変更点

リビジョン -00 なので、以前のリビジョンも差分もない。含まれるもの:

- 約束事（Section 2）: T0 = 1795000000、既定の検証時刻は T0+60、`expires` = `created`+300。正例と N-15 はリテラルの署名、ほかの変更型の負例は、エントリーの記載に従い、ランナーが署名し直すか基のベクターの署名をそのまま引き継ぐ。期待結果は、受理、`wimse-signature-invalid` 付きの HTTP 400、クライアントによる拒否、適合性の判定のいずれかで示す。判定対象は 29 件で、O- のエントリーは判定しない。
- テスト用の素材（Section 3）: issuer、svcA、svcB と囮の署名者 other の Ed25519 鍵、svcC の P-256 鍵。どれも公開のシードから導出する。WIT-A、WIT-B、WIT-C は `iat` が T0-60、`exp` が T0+3600。svcB は 4 つの `wimse-aud` 値を信頼する。
- 正例（Section 4）: P-01 は `wimse-sign-response` 付きの署名済み GET。P-02 は P-01 への署名済み 404 レスポンス。P-03 は本文と Content-Digest 付きの ES256 の POST。P-04 は `@method` と `@authority` を覆う CONNECT。P-05 はクエリなし（`@query` は `?`）。P-06 は署名が 2 つで、WIMSE の署名をタグで選ぶ。
- 負例（Section 5）。それぞれ基底 -08 の 1 つの要件に対応する:

| ベクター | 変更 | 基底 -08 の節 | 期待結果 |
| --- | --- | --- | --- |
| N-01 | P-01 のカバー範囲から `@query` を外し、署名は引き継ぐ | 3 | 拒否（400） |
| N-02 | P-04 に `@path` を足して署名し直す | 3 | 拒否（400） |
| N-03 | P-03 から Content-Digest とそのカバー範囲を外し、署名は引き継ぐ | 3 | 拒否（400） |
| N-04 | P-03 の本文だけを変え、Content-Digest と署名はそのまま | 3 | 拒否（400） |
| N-05 | P-01 から `expires` を外し、署名は引き継ぐ | 3 | 拒否（400） |
| N-06 | P-01 に `keyid` を足して署名し直す | 3 | 拒否（400） |
| N-07 | P-01 に `alg` を足して署名し直す | 3、3.1 | 拒否（400） |
| N-08 | P-06 の囮にも `wimse-workload-to-workload` のタグを付ける | 3 | 拒否（400） |
| N-09 | P-01 を T0+3600 に検証する | 3 | 拒否（400） |
| N-09b | P-01 を T0+300 と T0+301 に検証する | 3 | 受理、次に拒否（400） |
| N-10 | P-01 の `wimse-aud` の末尾にスラッシュを足して署名し直す | 3.2 | 拒否（400） |
| N-11 | P-01 から `wimse-aud` を外して署名し直す | 3 | 拒否（400） |
| N-12 | P-02 から `wimse-req-nonce` を外して署名し直す | 3、3.4 | クライアントが拒否 |
| N-13 | P-02 の `wimse-req-nonce` をゼロ列にして署名し直す | 3.5 | クライアントが拒否 |
| N-14 | P-02 のステータスと本文だけで、署名のヘッダーがない | 3.5 | クライアントが拒否 |
| N-15 | P-01 の形を svcC の ES256 鍵で署名したもの。リテラル | 3.1 | 拒否（400） |
| N-16 | 送信者が 32 ビットの空間から nonce を作る | 3 | 送信者が不適合 |
| N-17 | サーバーが WIT の失敗と署名の失敗を区別する、または 401 を返す | 3.6 | サーバーが不適合 |
| N-18 | 署名付きレスポンスが必要なのに、サーバーが署名なしの 200 を返す | 3.5、3.6 | サーバーが不適合 |
| N-19 | クライアントの Accept-Signature が `@status` だけを求める | 3.5 | 送信者が不適合 |
| N-20 | 検証者が WIT の検証前にメッセージを処理する | 3 | 検証者が不適合 |
| N-21 | P-02 の形を CONNECT のやり取りに移し、`@path;req` を足して署名し直す | 3 | クライアントが拒否 |
| N-22 | 検証者がラベルで署名を選ぶ | 3 | 検証者が不適合 |

- 観察事項（Section 6）: O-1 はリプレイキャッシュが SHOULD にとどまること。O-2 は基底 Section 3.7 の例の nonce が 32 ビットであること。O-3 は CONNECT 以外で `@authority` を覆うことが必須でも禁止でもないこと。

基底の本文との照合（-08 と -09、UTC で 2026 年 11 月 25 日）: 引用された要件はどれも、ベクターが挙げる節にある。N-05 は箇条書きを縮めて引用しており、N-17 は 401 の「NOT RECOMMENDED」を言い換えている。-09 でも引用はすべて残っているが、N-20 の「Section 5.1.4 of [workload-creds]」だけは -09 で Section 5.1.3 に変わった（issue #422）。workload-creds-03 に Section 5.1.4 はない。

-00 の文面のうち、ベクターの実際と合わないもの:

- N-04 は、変更によって署名も無効になる（「also invalidates the signature」）と書く。署名が覆うのは本文ではなく Content-Digest ヘッダーで、ヘッダーは変わらないので、署名は検証に通り、失敗するのは再計算したダイジェストだけである（Section 5.4）。
- Section 2 は WIT のプレースホルダーが「retained verbatim in the signed material」だとするが、P-01 の Signature 値は WIT-A の全文に対して計算されている（検証ログ）。印刷されたプレースホルダー `[WIT-A，§2 全文]` も、Section 2 が説明する形と違う。
- P-04 の `@authority` の値 `svcb.example.com` は RFC 9421 Section 2.2.3 と -09 の文言に従っている。引用している基底の -08 は「the host and port of the CONNECT target」と書いている。
- N-15 は基底 Section 3.1 の「algorithm not acceptable」の規則を試すつもりのベクターである。鍵を `cnf.jwk` から取る検証者から見ると、ES256 の署名が Ed25519 の鍵で検証に失敗するので、その規則に届く前に無効な署名として拒否される（このリポジトリーでのセットの実行、draft-ietf-wimse-http-signature の deep dive）。
- Section 1 は Change Log を Appendix A としているが、実際は Appendix B である。

## 影響分析

- 上流: draft-ietf-wimse-http-signature-08 の文面と、ベースの組み立てについて RFC 9421 に依存する。基底は本ドラフトの 2 日後に -09 になった。引用した要件は残り、-09 は O-2 と P-04 の問題に答えている。WIT の検証は draft-ietf-wimse-workload-creds に依存するが、リビジョンを指定せずに引用している。
- 下流: プロファイルの実装なら、P-01 から P-06 とメッセージ型の負例をそのままテストの入力に使える。基底は実装として Cofide と wimsey を挙げている（-08 Section 4）。cred-ninja は issue #419 のベクター 28 件が通ったと報告している（cred-ninja/sdk PR #136）。動作を判定する 6 件のベクターには、動いている送信者、サーバー、検証者を囲むハーネスが要り、N-20 には内部の確認や計測も要る。
- 互換性: 期待する拒否には `wimse-signature-invalid` の問題タイプが含まれるが、基底 Section 3.6 では problem details の本文は SHOULD なので、本文のない 400 を返すサーバーは基底には適合しつつ、ベクターを厳密に読むと不合格になる。受信者向けに書かれた規則だけを強制する検証者は、署名が有効な N-01、N-02、N-06、N-07、N-21 を受理しうる。CONNECT の `@authority` について -08 を字義どおりに実装すると P-04 に失敗する。
