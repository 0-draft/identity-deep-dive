# 検証ログ

## 環境

- ランタイム: Python 3.15.2 (標準ライブラリのみ、`python3 -I` で実行)
- ツール: git 2.56.1、gh 2.104.0。mmark と xml2rfc は使わず、出力された本文ではなく markdown のソースを直接比べた。
- バージョン: `openid/OpenID4VP` のクローン。比較元はタグ `1.0-final` (コミット `e819ed379abe9b0f6e93037e22d678837992e8b2`、2025 年 7 月 10 日)。比較先は `main` の `66f5ff93130128d1662cc60fcd79185ffe0a2d30` (#800 のマージ、2026 年 11 月 11 日) で、実行した 2026 年 11 月 18 日時点の最新コミットである。

## 手順

1. リポジトリをクローンしてタグを取得する: `git clone https://github.com/openid/OpenID4VP` と `git -C OpenID4VP fetch --tags`。`git -C OpenID4VP rev-parse main` は `66f5ff9…` を返す。
2. マージコミットを PR 番号に対応づけるため、マージ済み PR を保存する: `gh pr list -R openid/OpenID4VP --state merged --limit 400 --json number,title,mergeCommit,mergedAt,baseRefName > prs.json` (280 件)。
3. `python3 -I vectors/errata_history_check.py OpenID4VP 1.0-final 66f5ff9 prs.json` を実行する。スクリプトは次のことをする。
   - ルート (Final) または `1.0/` (#699 が内容を変えずに移した後) の `openid-4-verifiable-presentations-1_0.md` を読む。
   - フロントマター、フェンスで囲んだコードブロック、Document History を除き、残りを節 (見出しのアンカーかタイトル) と文に分け、空白を正規化する。
   - 大文字の RFC 2119 キーワードを含む文を規範的な文とみなし、Final と先頭を比べる。追加、削除、変更 (類似度で対にし、キーワードの組み合わせが変わったものと文言だけのものに分ける)、別の節への移動に分類する。
   - 両者の間で 1.0 の本文か `1.0/examples/` に触れた first-parent のコミット 34 件をたどり、それぞれを親と比べ、追加された Document History の項目を記録して、PR ごとに状態を付ける: `ok`、`NO HISTORY ENTRY` (規範的な文が変わったが項目の追加がない)、`HISTORY, PROSE CHANGE` (項目は追加されたが、変わったのはキーワードのない文だけ)、`HISTORY ONLY`、どちらの変更もなし。
4. スクリプトが失敗を検出できることを確かめる。`python3 -I vectors/errata_history_check.py --self-test` (手順 3 の最後でも実行される) は、小さな仕様を 9 通りに改変したものを同じコードに通す。空白だけの変更、コードブロック内の変更、節内の並べ替えは検出してはならない。`MAY` から `SHOULD` への変更、新しい `MUST NOT` の文、キーワードを含む文の別の節への移動は、どれも項目なしなら `NO HISTORY ENTRY` にならなければならない。リポジトリの外に置いたスクリプトの改変版 3 つはこのテストに失敗する: キーワードの正規表現から `MUST` を外したもの (9 件中 2 件が失敗、終了コード 1)、コードフェンスを読み飛ばさないもの (1 件が失敗)、移動を数えないもの (1 件が失敗、終了コード 1)。
5. 検出された PR すべてと、規範的な文の変更が 2 件以上ある `ok` の PR を、その項目と突き合わせて読む。#719、#731、#735、#745 については `gh pr view <n> -R openid/OpenID4VP --json title,mergedAt,files,commits` で、各 PR に含まれるコミットを確かめた。

## 結果

- 出力は `vectors/errata_history_check.log` にある。自己テストは 9 件中 9 件が通る。
- 規範的な文は Final に 379 文、エラッタ版ドラフトに 404 文ある。Final から先頭までで、追加 33、削除 8、キーワードの組み合わせが変わった変更 4、文言だけの変更 11、別の節への移動 2 (計 58)。どれも PR に対応づけられた。
- `-31` の下の 26 項目は 23 件の PR から来ている (#719、#745、#790 がそれぞれ 2 項目)。どの項目もその PR の本文の変更と一致する。本文にない変更を書いた項目はない。
- 1.0 の本文か例に触れた PR は 34 件。18 件が `ok`。5 件はキーワードを含まない変更に項目を付けている (#698 `encrypted_response_enc_values_supported` の適用範囲、#724「Verifier Info」、#729 `invalid_scope` の削除、#730 `intent_to_retain` がない場合、#801 `invalid_request` の新しいケース)。#700 は `-31` のプレースホルダと `-final` のリンクを足しただけ。8 件は規範的な文を変えず項目も足していない: #699 (ファイルの移動)、#663 (例のクレーム名)、#712 (形式的安全性解析の参照)、#725 (例のファイル 1 つ)、#728 (冒頭の `scope`)、#775 (相互参照)、#776 (エラー例の `openid_federation`)、#787 (`ldp_vc` の例の説明文)。
- Document History に項目がない規範的な変更:
  - #735 (2026 年 9 月 22 日マージ) には項目がまったくない。Verifier のメタデータ (署名付きプレフィックスでは鍵以外) は `client_metadata` から得なければならない (MUST) という文を 5 つ削除している。Section 5.9.3 の `redirect_uri`、`decentralized_identifier`、`verifier_attestation`、`x509_san_dns`、`x509_hash` に 1 つずつあったものである。代わりに「Source of Verifier Metadata」の節 (エラッタ Section 14.12) を追加した。プロファイルが `client_metadata` のパラメータを追加してよい (MAY)、それらは信頼しなくても安全に使える値に限ることを推奨する (RECOMMENDED)、ほかの信頼できる情報源を使ってよい (MAY)、という内容である。1.1 の Document History にもこの項目はない。
  - #745 は「SHOULD NOT return any OpenID4VP protocol errors」の 2 文を、DC API のプライバシーの節 (Final Section 15.9.2) から一般的な「Error Responses」の節 (エラッタ Section 15.9) に移した。これで 2 文はすべての呼び出し方法に適用される。#745 の 2 項目は空の VP Token と `vp_token` の書き直しにしか触れていない。
  - #719 は `expected_origins` の値について MUST NOT を 2 つ追加した。`ftp`、`javascript`、`data`、`ws`、`wss` のスキームは使わない、`http` は開発環境などを除いて使わない、というもの (エラッタ Section A.2)。#719 の 2 項目は文字列比較と、プラットフォームを信頼する前提にしか触れていない。
- #731 は `NO HISTORY ENTRY` と判定されるが、変更は `vp_formats_supported` の「a list of name/value pairs」を「name/value pairs」にしただけで、編集上のものである。

## 失敗パターン

- キーワードだけで判定すると、キーワードのない規範的な文を見落とす。#730 の「If absent, the Verifier makes no statement」や #801 の `invalid_request` の新しいケースがそうである。`HISTORY, PROSE CHANGE` の状態とログのキーワードなしの文の差分で拾えるが、1 件ずつ読む必要がある。
- 節をまたぐ移動は、適用範囲が広がるなら規範的な変更である (#745)。移動を無視していた初期版のスクリプトはこれを見落とした。
- 短い断片: `` `state` is OPTIONAL. `` は 5 語未満なので次の文とつなげている。そのため #734 は 1 件の変更ではなく、変更 1 件と追加 1 件として出る。
- PR をまたぐ類似度での対応づけ: Final から先頭までの一覧では、#735 で削除された `redirect_uri` の文が、#802 が追加した `encrypted_response_enc_values_supported` の項目と対にされている。どちらも `client_metadata` と (#new_parameters) を含むためである。PR ごとの一覧は 1 つの PR の中で対にするので、正しく削除として出る。
- 比べるのは 1.0 の markdown と `1.0/examples/` だけである。mmark が解決する参照の版 (#726、オープン) のように、出力された本文にしか現れない変更は見えない。

## 次にやること

- エラッタセット 1 が承認される前に、#735 の項目の欠落と、#745 と #719 で項目が触れていない部分を OpenID4VP のエディターに伝える。
- #803、#808、#726 の扱いが決まった後、エラッタセット 1 として承認される先頭でスクリプトを再実行する。
- 実験 2 から 5 は未実施のまま。実際のウォレット (`age_over_NN` を持つ mDL、`request_uri_method` の扱い、Request URI と Response URI での HTTP 307) か OpenID 適合性テストが必要で、どちらも用意できなかった。解析規則を手元で適用するスクリプトではウォレットのテストにならない。
