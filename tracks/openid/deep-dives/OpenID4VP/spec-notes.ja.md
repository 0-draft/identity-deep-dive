# 仕様メモ

## 参考文献

入力資料はドラフトではなく README とプルリクエストの一覧であるため、規範的参照も参考情報としての参照も挙げられていない。資料が名前で言及している項目は次のとおりである。

- JAR（JWT-Secured Authorization Request）。#798 の題名に現れる。
- SD-JWT VC。#782 と #726 に現れる。
- Digital Credentials API（DC API）。#761 に現れる。
- DCQL。#647 に現れる。
- OpenID Federation。#776 の `openid_federation` プレフィックスから示唆される。

1.0 と 1.1 のドラフトの参考文献一覧は資料に示されておらず、ドラフト本体から読み取る必要がある。

## 主な変更

このリポジトリは二つの仕様、すなわち OpenID for Verifiable Presentations の 1.0 と 1.1 のワーキンググループドラフトを持ち、どちらも main ブランチからビルドされる。README にはプルリクエストの題名しかない。マージ済みのものは、age_over_nn クレームの照合（#800）、検証者メタデータに対する `invalid_request`（#801）、client metadata 内の `encrypted_response_enc_values_supported`（#802）、terminate/reject/return の挙動（#790）、`vct` と `doctype` の照合（#744）、JAR のフォールバック文言（#798）、client_metadata のセキュリティ考慮事項（#735）、`vp_token` での SD-JWT VC の規範的な符号化（#782）、Holder Binding のない VC を直接返すこと（#783）、一部のプレフィックスで Request URI の応答を署名なしにできること（#788）、DC API の origin に関する指針（#761）、空オブジェクトをエラーに使えないこと（#745）、信頼できない入力に関する文言（#748、#759）、expected_origins の処理（#719）、未指定時の `intent_to_retain`（#730）、nonce のエントロピー（#722）、direct post 要求とユーザーセッションの対応付け（#734）である。未マージのものは #808、#809、#803、#726、#804 である。マージされずにクローズされたものは #647 である。

## 影響分析

- 上流: 資料は上流仕様の本文を示していない。題名からは、JAR、SD-JWT VC、DC API、OpenID Federation への依存が示唆される。
- 下流: ウォレット、検証者、および README がリンクする適合性テストが、照合規則、エラー挙動、`vp_token` の符号化の影響を受ける。資料は、具体的な下流の実装を挙げていない。
- 互換性: 資料は、どの変更が非互換かを述べていない。#803 は 1.0 への文言追加に触れ、#726 は 1.0 final のバージョン不整合に触れているため、レビュー担当者は各変更が各バージョンにどう適用されるかを確認する必要がある。
