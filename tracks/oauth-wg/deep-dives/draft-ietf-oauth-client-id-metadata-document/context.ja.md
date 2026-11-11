# 背景

## きっかけ

選定理由はドラフトの GitHub リポジトリの動きである。-03 が公開された 2026 年 11 月 2 日に 11 件の issue がクローズされ、PR #99「Add Client Authentication section」がマージされた。11 月 8 日には、Section 6 の response_types の共通部分の規則に関する issue #131 が立てられた。ドラフトはリビジョン 03（2026 年 11 月 2 日）であり、Datatracker の状態は Active、I-D Exists、WG Document で、oauth-wg トラックにある。

## なぜ重要か

本ドラフトは、クライアントが HTTPS の URL を client_id として使い、認可サーバーがそこからメタデータを取得する方式を定める（Section 3、6）。リビジョン 03 では、規範的な規則がいくつも追加または強化された。たとえば、クライアント認証のデフォルト（Section 5）、失敗時の扱い（Section 6.1）、iss パラメーターの必須化（Section 7）、ロゴの自前配信（-02 の SHOULD から MUST へ）（Section 10.9）である。URL 形式の client_id に依存する認可サーバーとクライアントの実装者は直接影響を受け、Section 5 以降の節番号もすべて変わった。

## 未解決の論点

- Section 5 の jwks または jwks_uri の要件は、private_key_jwt を実際に使う場合だけに適用されるのか。それとも、複数の方式の 1 つとして private_key_jwt を提示するすべての文書に適用されるのか。
- 文書に grant_types や response_types がない場合、サーバーはどう扱うのか（Section 6）。ドラフトは述べておらず、RFC 7591 の既定値（`authorization_code` と `code`）が適用されるかも書かれていない。issue #131 はこの点を含めて規則の見直しを求めている。
- OAuth 2.1 の issue 266 に関する編集上の注記を踏まえると、認可エンドポイントでの invalid_client はどう対応付けるべきか（Section 5）。
- メーリングリストで一参加者が出した提案、すなわち取得前の検証手順、クエリ成分の MUST NOT 化、サーバーメタデータの登録タイプ一覧を、ワーキンググループは取り上げるのか（Section 3、6、8、9.2）。
