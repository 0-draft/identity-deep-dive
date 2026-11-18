# 検証ログ

## 環境

- ランタイム: Python 3.15.2 (`python3 -I` で実行)
- ツール: `cryptography` 50.0.2 (Ed25519 の署名と検証) と Python 標準ライブラリのみ
- バージョン: draft-ietf-oauth-delegate-sd-jwt-00 と RFC 9901。手元の `.txt` (`draft-ietf-oauth-delegate-sd-jwt-00.txt`、`rfc9901.txt`) を読んで実装した。2026 年 11 月 18 日に実行。ドラフトのリポジトリの PR #15 はまだ open なので、このログは -00 の本文に従う。

## 手順

1. ドラフトには完全な例がないので、`vectors/delegate_labs.py` がトークンを自前で作る。鍵はすべて Ed25519 で、固定ラベルから導出する。ソルトもラベルから作り、タイムスタンプはすべて固定、Verifier の時刻は 1794960000 (2026-11-18T00:00:00Z) とした。Ed25519 の署名は決定的なので、2 回実行しても出力はバイト単位で一致する。ECDSA の署名は実行ごとに変わるため、ES256 は使っていない。
2. スクリプトには本文から書いた Verifier が 2 つある。`rfc9901_verify` は RFC 9901 Section 4 (コンパクト形式と ABNF)、7.1、7.3 に従い、委任については何も知らない。`dsd_verify` はドラフト Section 6 のプロトタイプで、Section 5.1.1、5.1.3、5.1.4 の形式ルールも見る。Lab 3 用に、Section 6 step 3.3/3.4 (`link_hash`) や step 5.3 (`kb_sd_hash`) のハッシュ検査を省いた甘い Verifier としても動かせる。
3. `python3 -I vectors/delegate_labs.py > vectors/delegate_labs.log` を実行する。各ケースは期待値 (`accept` か `reject`) と比べた `PASS` / `FAIL` を拒否理由つきで出力する。すべて一致し自己テストも通ったときだけ、最後に `ALL OK` を出して終了コード 0 で終わる。
4. スクリプトが失敗を検出できることを確かめる。自己テストでは、Issuer 署名を 1 ビット反転し (どちらの Verifier も拒否するはず)、KB-SD-JWT 内の `sd_hash` をゼロにし (拒否される)、改ざんしたトークンを受理すべきだとハーネスに伝える。最後の 1 行は `FAIL` と出るはずで、スクリプトはそうなったことを確かめる。
5. 2 回実行して出力を `cmp` で比べ、ログが再現できることを確かめる。

トークンの作り方 (-00 で決まっていない点の選択は「失敗パターン」に書いた):

- Issuer の SD-JWT: `typ` は `example+sd-jwt`。`iss`、`iat`、`exp`、`vct`、`cnf.jwk` (Holder の鍵) は見える形で置き、`given_name`、`family_name`、`card_last4` をオブジェクトプロパティの Disclosure にした (RFC 9901 Section 4.1、4.2.1)。
- KB-SD-JWT: Holder の鍵で署名し、`typ` は `kb-sd-jwt+kb`。トップレベルのペイロードには KB-JWT のクレーム `iat`、`aud`、`nonce` と、`sd_hash` か `issuer_jwt_hash`、`_sd_alg`、`delegate_payload` を置く (Section 5.1.4)。`delegate_payload` は `[{"...": <digest>}]` で、Delegate Payload の Disclosure は `[salt, {iss, exp, cnf, max_amount, _sd}]` (Section 5.1.3)。`merchant` と `item` はその中に入れ子の Disclosure として置いた。
- コンパクト形式: `<Issuer JWT>~<D>~<D>~<D>~~<KB-SD-JWT>~<DP>~<D>~<D>~<KB-JWT>`。分割すると 10 個の要素になり、KB-SD-JWT の前に空の要素が 1 つ入る (Section 5.1.1)。最後の KB-JWT は Delegate Payload の `cnf` にあるエージェントの鍵で署名し、その `sd_hash` は `<KB-SD-JWT>~<DP>~<D>~<D>~` に対して計算する (Section 5.1.3、6 step 5.3)。

## 結果

出力は `vectors/delegate_labs.log` にある。46 ケースで想定外は 0、自己テストも OK で `ALL OK`。2 回の実行結果はバイト単位で一致した。

- Lab 1 (1 段の委任):
  - RFC 9901 の Verifier は、比較用の普通の SD-JWT+KB を受理する。何でも拒否しているわけではない。
  - dSD-JWT+KB と dSD-JWT (末尾が `~`) はどちらも拒否する。KB-SD-JWT の前の空の要素が `DISCLOSURE` ではないので、RFC 9901 Section 4 の ABNF の時点で止まる。空の要素と JWT の要素を先に捨てる解析器でも、Delegate Payload の Disclosure を参照するダイジェストが Issuer 署名付き JWT にないので、RFC 9901 Section 7.1 step 5 で拒否する。
  - Section 6 のプロトタイプは dSD-JWT+KB を受理し、Issuer のペイロードと Delegate Payload (`max_amount` 50、`merchant` `shop-a`) を返す。dSD-JWT は、Key Binding を要求しないときは受理し、要求するときは拒否する (step 5.1)。
  - プロトタイプは次のものも拒否する: 普通の SD-JWT+KB (KB-SD-JWT がない)、KB-SD-JWT の前の空の要素が 2 つまたは 0 個 (5.1.1)、Holder の `cnf` ではなくエージェントの鍵で署名された KB-SD-JWT (step 3.1)、dSD-JWT+KB で `typ` が `kb+jwt` や `kb+sd-jwt` のもの (step 4.2)、Holder の鍵で署名された最後の KB-JWT (step 5.2)。
  - 1 つの署名で `delegate_payload` の要素を 2 つ作った場合 (Section 5.1.4)、1 つだけ開示すれば受理、2 つとも開示すれば拒否される (step 3.2)。Delegate Holder は `merchant` と `item` を省いてもよく、その場合も検証に通る (Section 4.1)。
- Lab 2 (`sd_hash` 版と `issuer_jwt_hash` 版で、Issuer の SD-JWT から `given_name` を除く):

  | ケース | `sd_hash` | `issuer_jwt_hash` |
  | --- | --- | --- |
  | Issuer の Disclosure 3 つすべて | 受理 | 受理 |
  | Delegate Holder が `given_name` を除く | 拒否 (step 3.3) | 受理。Verifier には `family_name` と `card_last4` が見える |
  | 完成した dSD-JWT+KB から転送中に `given_name` を除く | 拒否 (step 3.3) | 受理 |
  | Issuer の Disclosure をすべて除く | 拒否 (step 3.3) | 受理。Issuer のクレームは見えない |
  | Issuer が署名していない Disclosure を足す | 拒否 (RFC 9901 7.1 step 5) | 拒否 (RFC 9901 7.1 step 5) |

  `issuer_jwt_hash` 版では、dSD-JWT+KB のどの署名も Issuer の Disclosure を覆っていない。KB-SD-JWT は Issuer 署名付き JWT だけをハッシュし (Section 5.1.4)、最後の KB-JWT の `sd_hash` は最後の KB-SD-JWT とその Disclosure しか覆わない (Section 5.1.3、Section 6 step 5.3)。Section 4.1 は、Holder が Delegate Holder に Issuer の Disclosure を省かせる手段として `issuer_jwt_hash` を定めているので、省けること自体は意図どおりである。Lab で分かったのは、省けるのが Delegate Holder に限られないことで、完成したプレゼンテーションを扱う誰でも Issuer の Disclosure を取り除けて、それでも検証に通る。Disclosure を足すことはやはり検出される。普通の RFC 9901 の SD-JWT+KB では、KB-JWT の `sd_hash` が提示された Disclosure を覆う。`sd_hash` 版では、Delegate Holder は Holder が選んだ Issuer の Disclosure をそのまま提示するしかなく、減らすことはできない。
- Lab 3 (カード `1111` の SD-JWT A と カード `2222` の SD-JWT B が同じ Holder の `cnf` を持つ。委任 A は `max_amount` 50、委任 B は 5000 で、どちらも同じエージェントの鍵に委任する):
  - どちらの連鎖も単独なら検証に通る。
  - SD-JWT A に KB-SD-JWT B をつないだものは、Section 6 どおりの Verifier では拒否される (`sd_hash` 版は step 3.3、`issuer_jwt_hash` 版は step 3.4)。前の `cnf` での署名しか見ない甘い Verifier は受理し、カード `1111` と `max_amount` 5000 を出力する。Section 8.1 が警告している取り違えがこれにあたる。
  - 逆向き: エージェントの鍵も使い回されているので、連鎖 B の最後の KB-JWT を連鎖 A につなぐと step 5.3 で拒否され、5.3 を省くと受理される。
  - 対照実験: A と 3 つ目のクレデンシャル C で Holder の鍵を変えると、甘い Verifier でも署名 (step 3.1) で入れ替えを拒否する。Section 8.1 のとおり、ハッシュ検査が効いてくるのは `cnf` が使い回されたときに限られる。
  - 同じ SD-JWT を同じ Disclosure で 2 回委任すると、2 つの KB-SD-JWT は同じ `sd_hash` を持つので、ハッシュのつながりでは区別できない。Key Binding があれば、agent は agent-2 宛ての KB-SD-JWT を提示できない (step 5.2 で拒否)。Key Binding のない dSD-JWT なら、KB-SD-JWT #2 を持っている誰でもそれを提示できる。

## 失敗パターン

-00 が複数の読み方を許す箇所。スクリプトはここに書いたとおりに動く。

- クレームの置き場所。Section 5.1.4 は「Issuer 署名付き JWT のペイロードにあるはずのクレームは `_sd_alg` を除いてすべて」Delegate Payload に移すと言う一方で、KB-SD-JWT は KB-JWT の要件をすべて満たさなければならない (MUST) とも言う。スクリプトは KB-JWT のクレーム (`iat`、`aud`、`nonce`、`sd_hash`/`issuer_jwt_hash`) と `_sd_alg`、`delegate_payload` をトップレベルに置き、`iss`、`exp`、`cnf` は Delegate Payload に置いた。PR #15 は `cnf`、`exp`、`nbf` をトップレベルに移す。
- `delegate_payload` の要素が 1 つの場合。Section 5.1.4 が Disclosure を要求するのは要素が 2 つ以上のときだけだが、Section 5.1.3 は Delegate Payload を Array Disclosure として書き、Section 6 step 3.2 は「開示された要素がちょうど 1 つ」を求める。スクリプトは Delegate Payload を常に Disclosure にし、Verifier は RFC 9901 Section 7.1 の処理後に残った要素の数を数える。
- KB-SD-JWT の `aud` と `nonce`。Section 6 step 3 はこれらを Verifier と照合せず、KB-SD-JWT の宛先は Delegate Holder である。スクリプトは存在と型だけを確かめ、`aud` と `nonce` の照合は最後の KB-JWT でだけ行う。PR #15 はこれらが委任のステップに対するものだと書く。
- `issuer_jwt_hash` の入力。Section 5.1.4 は「直前の Issuer 署名付き jwt または KB-SD-JWT+KB だけ」のダイジェストと言う。スクリプトは末尾の `~` を含まないコンパクト JWS の US-ASCII バイト列をハッシュする。
- KB-SD-JWT の `sd_hash` の入力。スクリプトは RFC 9901 Section 4.3.1 と同じ `<直前の JWT>~<D.1>~...~<D.N>~` を使い、連鎖の区切りに入る追加の空の要素は含めない。
- Delegate Payload の有効期間。step 3.1 は Delegate Payload を JWT のペイロードとして扱えと言うので、スクリプトは RFC 9901 Section 7.1 step 6 (`exp`、`nbf`) をそれにも適用する。
- Section 8.1 の「両方向」。スクリプトは、直前の `cnf` による署名 (step 3.1) と直前のトークンのハッシュ (step 3.3/3.4) と読んだ。Lab 3 は、`cnf` が使い回されると署名だけでは通ってしまうことを示す。
- Section 5.1.4 と 6 の「Section 4.3.1」「Section 7.3」は、README に書いたとおり RFC 9901 の節として読んだ。
- 最後の KB-JWT の `iat` の許容幅は 300 秒とした (RFC 9901 Section 7.3 step 5.e。値は独自の選択)。

## 次にやること

- KB-SD-JWT が 2 つ以上ある連鎖 (Section 5.1.1)。途中の KB-SD-JWT が `kb+sd-jwt` のとき step 3.5 で拒否されることも確かめる。
- JSON Serialization (Section 5.1.2) と OpenID4VP の `delegate` トランザクションデータ型 (Section 7.1)。
- PR #15 がマージされたら Lab をやり直し、PR #14 が提案している例とトークンを比べる。
- `issuer_jwt_hash` 版では dSD-JWT+KB の中の Issuer の Disclosure をどの署名も覆っていないことを、upstream に提起する。
