# Deep Dive: draft-ietf-wimse-http-signature

> 一言で言うと: HTTP Message Signatures のプロファイルであり、ワークロードが Workload Identity Token に結び付いた鍵でリクエスト（および任意でレスポンス）に署名することで、TLS を終端するプロキシを挟んでも証明が失われないようにする。

## 概要

HTTP で互いを呼び出すワークロードは、認証を必要とする。相互 TLS は選択肢の一つだが、認証局（Certification Authority）の基盤がない場合や、呼び出しが複数の TLS ホップを経由する場合には、アプリケーション層での保護が好まれる（Section 1）。本ドラフトは、そのようなアプリケーション層の方式を HTTP Message Signatures（[RFC9421]）のプロファイルとして定義する。呼び出し側は Workload Identity Token（WIT）を送り、WIT 内の鍵に対応する秘密鍵でリクエストに署名することで、その鍵の保持を証明する。署名はメソッド、パス、クエリ、選択したヘッダー、および本文がある場合の Content-Digest を対象とし、三つの新しい署名パラメーターを持つ。宛先を示す `wimse-aud`、署名付きレスポンスを要求する `wimse-sign-response`、レスポンスをリクエストに結び付ける `wimse-req-nonce` である。本ドラフトは（CONNECT を除き）`@authority` に署名しないため、authority を書き換えるプロキシがあっても検証は壊れない。`subject.json` の Datatracker 状態は Active、Publication Requested、Submitted to IESG for Publication である。

## 仕組み

```mermaid
sequenceDiagram
    participant C as クライアントワークロード
    participant M as TLS 終端ミドルボックス
    participant S as サーバーワークロード
    C->>C: 対象コンポーネントとパラメーターから署名ベースを構築する
    C->>M: Signature、Signature-Input、Workload-Identity-Token を付けたリクエスト
    M->>S: 新しい TLS 接続でリクエストを転送する
    S->>S: WIT を検証し、WIT の鍵で署名を検証する
    S->>S: tag、有効期間、nonce、wimse-aud を確認する
    alt 認証に失敗した場合
        S-->>C: 問題タイプ wimse-signature-invalid を付けた 400
    else 署名付きレスポンスが必須の場合
        S-->>M: wimse-req-nonce にリクエストの nonce を設定して署名したレスポンス
        M-->>C: レスポンスを転送する
        C->>C: 署名を検証し wimse-req-nonce を比較する
    else 署名が必須でない場合
        S-->>C: レスポンス（任意で署名付き）
    end
```

1. クライアントは署名ベースを構築する。Section 3 により、`@method`、`@path`、`@query`、および存在する場合は Content-Type、Content-Digest、Authorization、Txn-Token、Workload-Identity-Token を対象に含める。`created`、`expires`、`nonce`、`tag`（値は `wimse-workload-to-workload`）、`wimse-aud` を設定し、任意で `wimse-sign-response` を設定する。`keyid` と `alg` は設定してはならない。
2. クライアントは WIT と署名を付けてリクエストを送る。ドラフト自身の記述によれば、TLS を終端するミドルボックスは平文の WIT と署名を見られるが、対象コンポーネントを変更すれば検証が失敗する（Section 5.2）。
3. サーバーは、署名を検証する前にワークロード資格情報ドラフトの規定に従って WIT を検証し、完全に検証されるまでメッセージをそれ以上処理してはならない（Section 3）。
4. サーバーはラベルではなく `tag` の値で WIMSE 署名を見つけ、その tag を持つ署名が複数あればメッセージを拒否する。有効期間を確認し、`wimse-aud` を信頼済み設定と Simple String Comparison で照合する（Section 3、3.2）。
5. 失敗した場合、サーバーは問題タイプ `wimse-signature-invalid` を付けた 400 を返し、どの検査が失敗したかは示さない（Section 3.6）。
6. リクエストが `wimse-sign-response` を true として持つ場合、またはローカルポリシーが要求する場合、サーバーはレスポンスに署名する。対象は `@status`、`req` パラメーター付きのリクエストコンポーネント、Content-Type、Content-Digest、Workload-Identity-Token であり、`wimse-req-nonce` にはリクエストの nonce を設定する（Section 3.4、3.5）。署名できない場合は、署名なしの成功ではなくエラーを返す。
7. クライアントは署名付きレスポンスを検証し、`wimse-req-nonce` を自分の nonce と比較する。署名を要求した場合、署名のないレスポンスは拒否しなければならない（Section 3.5）。

## ユースケース

- TLS を終端するロードバランサーや API ゲートウェイを経由するサービス間呼び出しで、エンドツーエンドの証明を宛先でも検証できなければならない場合（Section 1、5.2）。
- 剥がされた、または差し替えられたレスポンスを検出したいクライアントが、`wimse-sign-response` と `wimse-req-nonce` を併用する場合（Section 3.3、3.5、Appendix A.4）。
- CONNECT メソッドによるプロキシのトンネリングで、プロファイルが `@path` と `@query` の代わりに `@authority` を対象にする場合（Section 3）。
- 一つのサービスに複数の宛先名がある構成で、比較がバイト単位の完全一致であるため、受け入れる文字列をすべて受信側の設定に列挙しなければならない場合（Section 3.2）。
- 今回の版に対してメーリングリストで提案された独立のテストベクターで、適合性を確認したい実装者とテスト担当者。

## なぜ今重要か

- **きっかけ**: `subject.json` によれば、本ドラフトに対して三つの新しい issue が立てられている。テストベクター（#419）、例における nonce のエントロピー（#420）、編集上のコメント（#417）である。またドラフトは Publication Requested と Submitted to IESG for Publication の状態にあり、今の文言変更は最終形に近い。
- **根拠となる資料**: -08 の差分は、CONNECT の例外、`wimse-aud` への Simple String Comparison、64 ビット以上の nonce エントロピー、三つの登録済み問題タイプによる一様なエラー処理、およびシェパードレビューへの対応を加えている（Appendix B.1）。WIMSE メーリングリストでは、個人参加者が -08 に対するテストベクター一式（正例 6 件、負例 22 件）を投稿し、先頭の `?` を欠いていた `@query` の値を修正した。別の参加者が導入部への編集上のレビューを送り、Yaron Sheffer が issue #417 として記録した。
- **期待される影響**: 検証実装を共通の入力でテストできるようになり、これまで SHOULD や暗黙だった複数の挙動（nonce の生成とエントロピー、エラー時のステータスコード、`wimse-aud` の比較方法）が MUST になる。TLS の要件は新しくない。-07 でもすでに MUST で、Section 5.1 から Section 3 に移っただけである。-07 の実装は、nonce、エラー処理、audience の比較、CONNECT の経路を確認する必要がある。ドラフトの Implementation Status には二つの実装（Cofide、wimsey）が載っているが、どの版に従うかは記されていない。

## 変更点

- CONNECT の例外（Section 3）: 送信者は `@method` と `@authority` を対象に含めなければならず、`@path` と `@query` を含めてはならない。CONNECT リクエストに対する署名付きレスポンスでは、パスとクエリのコンポーネントの代わりに `@method;req` と `@authority;req` を用いる。それ以外のメソッドでは引き続き `@authority` を省く。
- `@request-target` の記述: -07 の「HTTP/1.1 以外では NOT RECOMMENDED」という文は、「@request-target ではなく @path と @query を別々に対象とし、[RFC9421] の Section 2.2.5 に従う」という記述に置き換えられた。
- `wimse-aud`（Section 3.2）: 受信者は、信頼済み設定にある値と Simple String Comparison（[RFC3986] の Section 6.2.1）で照合しなければならない。末尾のスラッシュや明示的な既定ポートは一致せず、許容する変種はそれぞれ設定しなければならない。受信者は Host などのリクエストフィールドから audience を導出してはならない。
- nonce（Section 3）: 送信者は暗号論的に安全な乱数生成器を用いなければならず、エントロピーは 64 ビット以上、96 ビット以上が RECOMMENDED である。
- 時間枠（Section 3）: 受信者は有効期間外の署名を拒否しなければならない。この文は、Security Considerations にあった MUST に代わるものである。
- TLS（Section 3）: サーバー認証付き TLS 接続とクライアントによるホスト名検証（[RFC9525]）の MUST は、Section 5.1 からプロトコルの節に移った。BCP 195 に従うことを求める SHOULD が新たに加わった。
- Content-Digest（Section 3）は [RFC9530] を参照するようになり、これは [RFC3986] および BCP 195 とともに新たな規範的参照である。
- エラー処理（Section 3.6）: 認証の失敗には `wimse-signature-invalid` を付けた 400 を返さなければならず、どの検査が失敗したかを示してはならない。署名が必須だが署名に対応しないサーバーは、`wimse-signed-response-unsupported` を付けた 501 を返さなければならない。署名に対応するが、このレスポンスには署名できないサーバーは、`wimse-signed-response-unavailable` を付けた 400 を返さなければならない。-07 では、検証の失敗については「400 などの」ステータスコードが適切と述べるだけで、必須の署名付きレスポンスを返せないサーバーについては 400 か 501 を返す SHOULD だった。problem details の本文は、相手が受け付けないと分かっている場合を除き SHOULD である。
- `wimse-sign-response`（Section 3.3）: true の場合、サーバーは署名するかエラーを返さなければならない。
- IANA（Section 7.2）: HTTP Problem Types への三件の登録が追加された。
- 編集上の再構成: Security Goals は本文（-07 の Section 6）から Appendix A に移り、そのぶん Document History は Appendix B、DPoP との比較は Appendix C に繰り下がった。-07 で Security Considerations の下位節だった Privacy Considerations は独立した Section 6 になり、ワークロード資格情報ドラフトへの参照だけに縮小された。Section 5 の複数の MUST は、Section 3 に戻る説明的な記述になった。Section 3.1 のアルゴリズムの記述は、「ES256 のサポートが MUST であるという要件を引き継ぐ」から、ワークロード資格情報ドラフトのアルゴリズム要件に「従う」に変わった。Section 3.2 と Section 3.3 の「定義する」という文は書き換えられた。
- 互換性と移行: 短い、または低エントロピーの nonce を使っていた -07 の送信者、URI 正規化後に `wimse-aud` を比較していた送信者または受信者、署名できないときに別の方法で 501 や 400 を返していたサーバー、およびすべての CONNECT 通信は、変更が必要になる。エラーレスポンスは、相手が problem details を受け付けないと分かっている場合を除き、登録済みの問題タイプを付ける必要がある。

## 技術的分析

- 脅威モデルへの含意: WIT はベアラートークンとして使われないが、取得されたトークンと署名は署名の有効期間内であれば再送され得る（Section 5.1）。短い `expires`、nonce、任意のリプレイキャッシュがこれを軽減する。ただしドラフトは、攻撃者がどのクラスターメンバーが検証するかを選べる場合、リプレイ検出は有効でないと述べている（Section 5.1、Appendix A.4）。ミドルボックスは平文の WIT と署名を見られ、それを取得して再送したり、署名されていないヘッダーを変更したりできる（Section 5.2）。ドラフトは、ミドルボックスが対象コンポーネントを検出されずに変更することはできないとし、中間者での再署名は対象外としている。`@authority` ではなく署名付きパラメーターに audience を結び付けることが、authority の書き換えがあっても検証を維持する方法である（Section 3、5.1）。Appendix A.4 は、リクエストとレスポンスの組の削除が検出されずに済まないのは、クライアントが `wimse-sign-response` で署名を要求し、署名のないレスポンスを拒否する場合に限ると述べている。したがって、サーバーのローカルポリシーによる署名だけでは日和見的である（Section 3.5）。
- プロトコルフローへの含意: 検証の順序は固定されている。まず WIT、次に HTTP メッセージ署名であり、両方が通るまでそれ以上の処理は行わない（Section 3）。WIMSE 署名は tag で見つけるため、中間者による他の署名と共存できる（Section 3、5.2）。`wimse-sign-response` は Accept-Signature より優先され、Accept-Signature でプロファイルより弱い対象範囲を要求してはならない（Section 3.5）。アルゴリズムは `alg` パラメーターではなく WIT の `cnf.jwk.alg` から決まり、ローカルポリシーで許容されないアルゴリズムは受信者が拒否する（Section 3.1）。署名に関する二つのエラー経路は、ステータスコードと問題タイプだけで区別される。未対応は 501、利用不能は 400 である（Section 3.6）。
- 相互運用上の懸念: `wimse-aud` は完全一致の文字列として比較されるため、「送信者が知る」既定の対象 URI を使う送信者は、設定された値とバイト単位で一致させなければならない（Section 3.2）。`@query` はクエリが空でも含めなければならず、その値は `?` である。メールのやり取りは、署名ベースで先頭の `?` を省くことがテストベクターで実際に起きた実装上の誤りだったことを示している（Section 3、メール）。本文がある場合、Content-Digest は必ず存在し、検証されなければならない。CONNECT のリクエストとレスポンスは、異なる対象集合を用いる（Section 3）。Section 3 と 3.6 は WIT の検証についてワークロード資格情報ドラフトの「Section 5.1.4」を参照しているが、参照先の版（-02）に Section 5.1.4 はない。検証手順は、-08 より後に出た workload-creds-03 の Section 5.1.3 にある。Section 3.7 の例は短い nonce 文字列を使っており、リストのスレッドによれば Section 3 の下限より短いため、実装者はそれを真似してはならない。問題タイプの URI は IANA の Problem Types レジストリの名前空間にあり、Section 7.2 の登録が完了している必要がある（Section 7.2）。

## 未解決の問題

- `keyid` と `alg` に対する検証側の挙動（Section 3）: ドラフトは送信者に対して「使ってはならない」と述べているが、検証側がそれらを含むメッセージを拒否するのか無視するのかは、ドラフトの本文に書かれていない。テストベクターの作者は「reject」と記録し、リストで作業部会に尋ねた。メールによれば Yaron Sheffer が回答し、作者は「ベクターは作者が述べた意図に基づく」と書いているが、ドラフトの本文にはまだ明記されていない。
- 例の nonce（Section 3.7）: リストのスレッドは、例の nonce は説明用であるという編集上の注記を提案している。`subject.json` は例における nonce のエントロピーに関する issue（#420）を挙げているが、提供された資料にはその内容が示されていない。
- nonce の形式（Section 3）: ドラフトはエントロピーのビット数を定めているが、nonce 文字列の符号化や長さは定めておらず、受信者がエントロピーをどう確認できるかも述べていない。
- CONNECT の audience（Section 3、3.2）: `wimse-aud` の既定値はクエリとフラグメントを除いた対象 URI だが、CONNECT の対象は authority-form である。CONNECT の場合の既定の audience が何かは、ドラフトに書かれていない。
- 一様な 400 と別個の問題タイプ（Section 3.6）: サーバーはどの検査が失敗したかを示してはならないが、署名付きレスポンスが利用できない場合の 400 は別のエラーである。problem details を受け付けないクライアントは両者を区別できず、ドラフトはこれを論じていない。
- 中間者による再署名（Section 5.2）: WIMSE 署名を剥がして置き換えることは、ドラフトでは展開環境のポリシーに委ねられている。
- 導入部の文言（Section 1）: リスト上のレビューは、最初の文に HTTP を明記し、複数の TLS ホップにまたがるオブジェクトレベルの認証を説明することを提案している。-08 の Section 1 にはその文言はなく、issue 番号は #417 である。
- リプレイキャッシュの範囲（Section 3、5.1、Appendix A.4）: 何をどれだけの期間記憶するかはローカルポリシーであり、別のクラスターメンバーへのリプレイは成功し得る。
- Appendix C は、将来の版で署名付きレスポンスを必須にするかどうかを決められると、依然として述べている。

## 実験

- [ ] Lab 1: Section 3.7.1 の Figure 2 のリクエストと Figure 4 のレスポンスについて、RFC 9421 のライブラリで署名ベースを再構築し、WIT 内の公開鍵で署名を検証して、`@query` が先頭の `?` を含む `?flavor=vanilla` になっていることを確認する。
- [ ] Lab 2: issue #419 からリンクされたテストベクター一式に対して検証実装を実行し、受理と拒否の判断を期待結果と比較する。特に `wimse-aud` の変種（末尾のスラッシュ、明示的な既定ポート）、`wimse-workload-to-workload` の tag の重複、`keyid` と `alg` の存在、CONNECT の各ケースを見る。
- [ ] Lab 3: `Host` を書き換える TLS 終端プロキシをサーバーの前に置き、`wimse-sign-response` を true にした署名付きリクエストを送る。検証が引き続き成功すること、署名できない（ストリーミングの）サーバーが `wimse-signed-response-unavailable` を付けた 400 を返すこと、署名に対応しないサーバーが `wimse-signed-response-unsupported` を付けた 501 を返すことを確認する。

## 情報源

- [draft-ietf-wimse-http-signature-08](https://datatracker.ietf.org/doc/draft-ietf-wimse-http-signature/08/)
- [WIMSE リスト: Test vectors for draft-ietf-wimse-http-signature-08, request for review](https://mailarchive.ietf.org/arch/msg/wimse/4oCoc4IePmmc1cCm1FthFanNNRc/)
- [WIMSE リスト: Re: Test vectors for draft-ietf-wimse-http-signature-08](https://mailarchive.ietf.org/arch/msg/wimse/VCH1w0y6OuR-koGRiJYakzmtGAo/)
- [WIMSE リスト: Re: Review of draft-ietf-wimse-http-signature](https://mailarchive.ietf.org/arch/msg/wimse/Vd1-lCWYXdJYkIMMV2z98f3IL5s/)
- [ドラフトのリポジトリにあるテストベクターの issue #419](https://github.com/ietf-wg-wimse/draft-ietf-wimse-s2s-protocol/issues/419)
- [ドラフトのソースリポジトリと issue トラッカー](https://github.com/ietf-wg-wimse/draft-ietf-wimse-s2s-protocol)
