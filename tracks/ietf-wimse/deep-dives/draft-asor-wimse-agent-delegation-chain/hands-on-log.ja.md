# 検証ログ

## 環境

- ランタイム: Python 3.15.2、`python3 -I` で実行（`vectors/` の各ログの 1 行目に出力される）
- ツール: Python 標準ライブラリと `cryptography` 50.0.2（Ed25519 のみ）。`vectors/` のスクリプトはどれもこのログのためにドラフト本文から書いたもので、attenu-guard、attenu-guard-ts、Cred、tenuo のコードは実行していない。`gh` は niyikiza の本文の取得に 1 回だけ使った。
- バージョン: draft-asor-wimse-agent-delegation-chain-03（テキストファイルの sha256 `270e28cb1448c0bdd14c04907932bba8a9b857574d26cf1ce9d54f704e1474df`）。attenu-guard のタグ v0.22.0 にある Appendix B のベクター JSON 36 ファイル（HS256 のテスト用署名者で、秘密鍵と kid は各ファイルの中にある。集約ハッシュは `vectors/verify_vectors.log`）をデータとして読んだ。draft-niyikiza-oauth-attenuating-agent-tokens-02 は tenuo-ai/tenuo の `ietf/` から `main` = `63ed003934f1d452601164965e6ab3b6ca23fc43` の時点で取得した（sha256 `a7e23c35362c1fb60018a63343f8b0fdc1ce4a8c01fbf73af4a85e7ecf79f0f2`）
- 日付: 2026 年 11 月 18 日

## 手順

1. -03 の本文と 36 本のベクターファイルを、リポジトリの外のローカルディレクトリ `attenu-guard-v0.22.0-draft02/` に置く。
2. ベクターを採点する: `python3 -I vectors/verify_vectors.py <dir>/attenu-guard-v0.22.0-draft02 > vectors/verify_vectors.log`。スクリプトは Section 3、4、4.1、4.2、4.4 のパース規則、Section 6 のステップ 1 から 5、ステップ 8 のうち audience の検査を実装している。続けて自己テストを実行する。変更していない `valid_chain.json` と、それを変えた 12 通りの入力について、それぞれ決まった結果名が出るかを見る。
3. Lab 1: `python3 -I vectors/three_hop.py > vectors/three_hop.log`。固定のシードから alg `Ed25519` で 3 トークンのチェーン（planner、researcher、formatter）を発行し、ステップ 1 から 5 だけを実行する。
4. Lab 2: `python3 -I vectors/overspend.py > vectors/overspend.log`。ルートの max を 100、2 つの子を 60 として発行し、両方のチェーンを検証したうえで、2 つのゲートウェイ、共有台帳、単一書き込み者の割り当て器をプロセス内でモデル化する（2 つのゲートウェイはスレッドで代用する）。
5. Lab 3: `gh api repos/tenuo-ai/tenuo/contents/ietf/draft-niyikiza-oauth-attenuating-agent-tokens-02.txt -H "Accept: application/vnd.github.raw"` で niyikiza の本文を取得し、`python3 -I vectors/depth_rules.py > vectors/depth_rules.log` を実行する。niyikiza-02 の Section 8 のうち深さの検査（ステップ 3c、3i、4b4、4d から 4g、4m、5。MAX_DELEGATION_DEPTH は 8）と asor の深さの規則だけを実装し、各事例を発行したチェーンで asor の検証器全体にも通す。
6. Lab 4: `python3 -I vectors/full_verify.py <dir>/attenu-guard-v0.22.0-draft02 > vectors/full_verify.log`。葉が 8 種類すべての制約型を持つ 3 トークンの Ed25519 チェーンを発行し、ステップ 1 から 5 を `verify_vectors.py` で実行したあと、ステップ 6（RFC 9449 Section 4.3 に従って検査し、RFC 9449 Section 6.1 と RFC 7638 に従って DT_2 の `cnf.jkt` に結び付ける DPoP 証明）、ステップ 7（有効期間を持つキャッシュ済みのステータスリスト）、ステップ 8（audience、スコープ、アクションごとの制約、累積の制約）を実行する。累積の合計値はリクエストとは別に渡す dict から読み、アクションのパラメーターからは読まない。最後に `valid_unknown_constraint_identical.json` に対してステップ 8 のアクションの検査を実行する。RFC 9449 の検査は RFC 本文（Section 4.3、6.1、11.1。2026 年 11 月 18 日に照合）に従っている。ステータスリストのドラフトは取得していない。
7. Lab 4 の自己テスト: `python3 -I vectors/full_verify.py --break <dir>/attenu-guard-v0.22.0-draft02 > vectors/full_verify.break.log` は、max_rows 101 に accept を期待する事例を 1 つ加える。この事例は FAIL と報告され、終了コードは 1 になる。
8. `python3 -m compileall -q vectors/*.py`。Lab 4 の 2 つの実行はそれぞれ 2 回行い、出力を `cmp` で比べる。

## 結果

- ベクター: 36 本すべてが期待どおりの結果名になった。結果名ごとに accept 5/5、malformed 17/17、not_narrower 8/8、par_hash_mismatch 2/2、principal_altered 1/1、signature_invalid 1/1、expired 1/1、audience_mismatch 1/1。実行していないステップは 6（DPoP による保持者の結び付け）、7（ステータスリスト）、8 のうちアクションの検査（スコープ、アクションごとの制約、累積の制約）である。これらのステップの結果を期待するベクターはないので、採点から外したベクターはない。自己テストは、変更していないチェーンと 12 通りの変更のすべてで期待どおりの結果名を出した。その中には、セット内のどのファイルも扱っていない non_canonical、duplicate_member、non_finite も含まれる。
- 採点結果は、-03 が決めていない 4 つの読み方に依存する。(1) "del_max_depth" を持たない子は、規則 5 では親の値を引き継ぐとした。Section 3 がこのクレームを必須とするのは DT_0 だけで、規則 5 は値がない場合について何も言っていない。`reject_child_raises_del_max_depth.json` では DT_1 がクレームを持たず DT_2 が 60 を持つので、クレームを持つ隣接トークンどうしだけを比べる検証器はこれを受理する。(2) Section 7 がこのクレームは JWK サムプリントを運ぶと書いているので、"cnf" には "jkt" が必要とした。(3) Section 4.4 に従い、パースの検査をステップ 1 より前に全トークンに対して行った。(4) ステップ 1 は i > 0 の DT_i をどの鍵で検証するかを定めていないので、全トークンを 1 つの信頼済み鍵で検証した（Section 11 と同じ単一署名者）。
- ベクターのメタデータ: `reject_child_raises_del_max_depth.json` の説明は「ルートの上限 6」と書いているが、その DT_0 の "del_max_depth" は 7 である。結果名には影響しない。また全ファイルが `"draft": "02"` を持ち、Appendix B が -03 で追加したとする `reject_child_adds_detail_type.json` も同じである。
- Lab 1: 17 事例すべてが期待どおりの結果名になった。not_narrower（スコープの追加、max_rows の拡大、max_rows の削除、del_max_depth の引き上げ）、principal_altered、par_hash_mismatch（再発行された親、親の差し替え）、expired、signature_invalid、depth_invalid である。境界については、DT_2 の exp が 1900 のとき、now 1899 は受理、now 1900 は -03 の規則（now < exp）で expired、-02 の規則（now <= exp）では受理になった。親より後の exp を持つ子は、ステップ 4 の not_narrower ではなく、ステップ 5 の expired として報告される。
- Lab 2: ルートの max 100 の下に 60 の子を 2 つ置くと、両方のチェーンが検証に通り、2 つのゲートウェイが合計 120 を許可した。120 の子 1 つなら not_narrower になる。ルートに max_subtree 100、子に 60 と 60 を置いても、各辺は狭まっているので両方のチェーンが検証に通る。部分木の合計を持たないゲートウェイは拒否し（消費 0）、累積の検査を飛ばすゲートウェイは 120 を消費する。検査と引き落としを不可分に行う台帳は、2 ゲートウェイの競合 500 回のすべてで 60 だった。認可時に読み、後で引き落とす台帳（割り込みを強制）は 50 回中 50 回で 120 だった。協調しない台帳の複製 2 つでも 120 になった。単一書き込み者の割り当て器は A に 60 を割り当て、B へのさらなる 60 を拒否し、B に 40 を割り当て、ゲートウェイは合計 100 を許可した。各ハザードも再現した。オフラインの割り当て器 2 つによる重複割り当てで 120 が割り当てられた。永続化していない引き落としのローカルなロールバックで、ゲートウェイ A は 60 の割り当てに対して 120 を許可した（先に引き落としを永続化すれば拒否される）。決済前に予約を解放する早すぎる再利用で、ゲートウェイ B は 40 の割り当てに対して 80 を許可した（予約を保持している間は拒否される）。
- Lab 3: 10 の名前付き事例のうち 5 つで結果が食い違った。(a) 葉の "del_depth" がルートの "del_max_depth" に等しい（2, 2）: asor は depth_invalid、niyikiza は受理。(b) ルートの "del_max_depth" が 0: asor は malformed（正の整数が必要）、niyikiza は終端のルートとして受理。(c) 子が "del_max_depth" を持たない: asor は受理、niyikiza は 4b4 で拒否。(d) DT_1 が "del_max_depth" を 1 に下げ、ルート 5 の下で DT_2 が深さ 2 にある: asor は受理、niyikiza は 4e で拒否。(e) ルートが MAX_DELEGATION_DEPTH 8 を超える 9: asor は受理、niyikiza は 3i で拒否。全トークンが m を持つ格子では 49 マス中 7 マスが食い違い、すべて n == m の対角線上にある。これは Section 10 が述べている違いである。(d) は Section 10 にない。-03 では子は "del_max_depth" を下げられる（規則 5）が、ステップ 3 は n を DT_0 の値とだけ比べるので、下げた値はチェーンのそれより下の部分を何も制限しない。
- Lab 4: 52 事例すべてが期待どおりの結果名になり、終了コードは 0 だった。受理する事例は、8 ステップすべてを通す基準のチェーン、すべての上限・下限ちょうどの値、新しい jti を持つ 2 つ目の証明、iat が now - 60 の証明、有効期間が切れる 1 秒前のキャッシュ、古くなったリストを取得し直せた場合である。ステップ 6: 15 通りの変更（証明なし、DT_1 の保持者の鍵、htm、別のパスの htu、クエリを残した htu、61 秒前と 61 秒後の iat、DT_1 の ath、ath なし、jti なし、typ jwt、alg none、d を持つ jwk、署名の改変、jti の再利用）はすべて holder_binding_failed になった。ステップ 7: DT_1 または DT_0 の失効は revoked になった。キャッシュがなくエンドポイントにも届かない場合、ちょうど fetched_at + ttl の時点で更新できない場合、idx がリストの外にある場合、idx のない参照は status_unknown になった。"suspended" は revoked にした（この lab の選択）。ステップ 8: 別の audience は audience_mismatch になった。crm.write、mail.send（DT_0 だけが持つ）、ワイルドカードの crm.* は scope_not_granted になった。max、min、one_of、not_one_of、prefix、rank の各違反、rank の order にない値、数値の位置の文字列、アクションが示さない量、max_lifetime 5 に対する max_calls の合計 6、max_subtree 100 に対する max_spend の合計 101、合計値がない場合は ceiling_exceeded になった。合計値がない場合は、リクエスト自身が max_spend 0 と max_calls 0 を示しても拒否される。DT_1 と DT_2 が同一の {"key": "quota", "units": 5} を持つチェーンは、ステップ 1 から 5 を通り、全体では unknown_constraint になった。順序の検査では、証明なしかつ DT_1 失効は holder_binding_failed、DT_1 失効かつ crm.write は revoked、now 1900 かつ証明なしは expired、未知の型かつ max_rows 101 は unknown_constraint になった。`--break` の実行は 53 事例中 52 と報告し、終了コードは 1 だった。
- Lab 4 のベクター: `valid_unknown_constraint_identical.json` はステップ 1 から 5 と audience の検査を通った（ベクターの期待どおり accept）。ベクターに DPoP の鍵がなく、トークンにステータス参照もないので、ステップ 6 と 7 は実行していない。アクション {"scope": "crm.read", "params": {"max_rows": 10, "egress": "none", "max_spend": 5}} に、max_calls の合計 1 と max_spend の部分木の合計 5 を別に渡すと、ステップ 8 で (quota, units) について unknown_constraint として拒否された。quota の制約をメモリ上で取り除いた DT_2 のペイロード（再署名していない）に同じアクションを当てると許可されるので、拒否の原因は未知の型だけである。
- Lab 4 の結果名: Table 2 や -03 で結果が決まらないところは、この lab が名前を選んだ。どれが lab の選択かは `vectors/full_verify.log` 冒頭の A の一覧と各事例のラベルに示してある。主なものは次のとおり。ステップ 8 が MUST で拒否を求める「合計値がない」場合と、アクションが示さないアクションごとの量は ceiling_exceeded にした。"suspended" は revoked にした。使える uri と idx を持たないステータス参照は status_unknown にした。型の違う量（A9）とワイルドカードのアクションも lab の選択である。

## 失敗パターン

- 末尾が `$` の正規表現でスコープを検査する: `crm.read\n` が `crm.*` の下のリテラルとして通る。完全一致を使う（`reject_newline_scope.json`）。
- Python の `json` は既定で NaN と Infinity を受け付け、重複したメンバーは後のものを残す。フックを入れないと、検証器は non_finite も duplicate_member も報告しない。
- ステップ 4 で導出した有効期間を比べると、`reject_child_exp_exceeds_parent.json` を not_narrower と報告してしまう。規則 4 はステップ 5（expired）に属する。
- -02 の時刻規則（now <= exp）を使うと、now == exp のチェーンを受理してしまう。
- `python3 -I` はスクリプトのディレクトリを `sys.path` から外すので、`three_hop.py`、`overspend.py`、`depth_rules.py` は `verify_vectors.py` をパスで読み込む。
- Lab 2 はプロセス内のモデルである。割り込みを強制したスレッドであり、ネットワーク上の実際の 2 つのゲートウェイではない。
- Lab 4: htu をリクエストの URI 全体と比べると、クエリを持つリクエストはすべて失敗する。RFC 9449 Section 4.3 では、クエリとフラグメントを除いて比べる。
- Lab 4: 累積の合計値をアクション自身のパラメーターから読むと、リクエストが自分の消費量を申告できてしまう。Section 4.2 とステップ 8 は合計値を別の経路に置く。スクリプトは合計値を (型, DT_n の jti, key) をキーにした dict に置き、アクションからは届かないようにした。
- Lab 4: アクションがキーを名指ししたときだけ未知の制約型を検査すると、(quota, units) の下でアクションを許可してしまう。Section 4.2 はすべてのアクションを拒否する。
- -03 が決めていない点についての Lab 4 の選択（`vectors/full_verify.log` の冒頭に A1 から A12 として出力される）: (A1) ath は DT_n のコンパクト形式のハッシュとした。-03 は、チェーンのどのトークンがアクセストークンなのかも、チェーンをどう送るのかも書いていない。(A2) DPoP の iat の許容幅は前後 60 秒とし、nonce は発行しない。(A3) htu はクエリとフラグメントを除いたうえでバイト単位で比べ、RFC 3986 の正規化はしない。(A4) 一度使われた証明の jti は拒否する（RFC 9449 Section 11.1 では、再利用の記録はサーバーに任されている）。(A5) ステータス参照は `"status": {"status_list": {"uri", "idx"}}` とした。-03 はクレーム名を決めていない。キャッシュしたリストはメモリ上のモデルで、署名付きのステータスリストトークンではない。(A6) キャッシュした答えは now < fetched_at + ttl の間だけ信頼する。(A7) 使える uri と idx を持たない参照と、リストの外を指す idx は status_unknown とした。(A8) "suspended" は revoked とした。(A9) アクションごとの量がない、または型が違う場合は ceiling_exceeded とした。(A10) 渡される合計値は A を含むものとし、合計値がない場合は ceiling_exceeded とした。(A11) ステップ 8 の中の順序は audience、スコープ、未知の型、アクションごとの制約、累積の制約とした。このため未知の型が上限違反より先に報告される。ステップ 8 は audience の検査の「あと」にスコープ、アクションごとの制約、累積の制約を挙げているが、Section 4.2 の未知の型による拒否をその中のどこに置くかは書いていない。(A12) 合計値は DT_n の jti についてだけ引く。ステップ 8 が見るのは DT_n の権限なので、祖先の max_subtree の合計は参照しない。Lab 2 の兄弟による過剰消費は、Section 9.4 が述べる仕組みに任される。（A13）DPoP 証明の alg は "Ed25519"（RFC 9864）だけを受け入れる。Section 3 が Delegation Token に求める値である。"EdDSA"（RFC 8037）の証明は拒否する。-03 は DPoP 証明に使える alg を決めていない。

## 次にやること

- ステップ 7 はメモリ上のリストに対して動いている。このログのためにステータスリストのドラフトを読んだうえで、署名付きのステータスリストトークンに置き換える。
- Lab 4 の RFC 9449 の側は、2026 年 11 月 18 日に RFC 本文と照合した。検査は Section 4.3 の一覧に従っており（nonce は発行しないので nonce の検査は対象外）、節番号 4.3、6.1、11.1 も正しい。-03 の側は本文を検索して確かめた。"ath"、"htu"、"nonce"、"idx"、"suspend" はどれも出てこず、ステータス参照のクレーム名もなく、DPoP に触れているのは Section 3、6（ステップ 6）、7、参考文献、変更履歴だけである。
- Lab 4 で選択が必要だった -03 の点（ath がどのトークンを対象とするか、ステータスのクレーム、ステップ 8 の中の順序、合計値がない場合・量がない場合・"suspended" の結果名）は、下の "del_max_depth" の 2 点とあわせて著者に伝える候補である。まだ何も送っていない。
- 新しいセットが作り直していない事例（"del_max_depth" より長いチェーン、裸のワイルドカードと末尾以外のワイルドカード、RFC 8785 の数値の形式）について、-01 の 20 ファイルのセットを採点する。-01 のクレーム規則が要る。
- "del_max_depth" に関する 2 点（規則 5 でクレームを持たない子、ステップ 3 が一切適用しない子の下げた値）は著者に伝える候補である。まだ何も送っていない。
