# Spec Notes

## 参考文献

`21ffd6c` 時点のドラフトが挙げる規範参照のうち、相互運用に特に効くもの:

- API 全体の土台である OAuth 2.0(RFC 6749)、`authorization_details` のための Rich Authorization Requests(RFC 9396)、Pushed Authorization Requests(RFC 9126)、DPoP(RFC 9449)。
- 特定の版に固定された、Final になっていない依存仕様(1.0 Section 14.7): OpenID Federation 1.0 draft -43、SD-JWT VC draft -11、Attestation-Based Client Authentication draft -07、Token Status List draft -12。1.1 はこれに OAuth 2.0 for First-Party Applications draft -04 を加える(1.1 Section 15.9)。
- Interactive Authorization のプレゼンテーションの段階で使う OpenID4VP(1.1 Section 6.2.1.1)。
- s2s: 全エンドポイントでの mutual TLS(RFC 8705)、エラー用の Problem Details(RFC 9457)、API の版の廃止を知らせる `Sunset`(RFC 8594)(s2s Sections 5.1、5.3、5.4)。

## 主な変更

各プルリクエストの差分で確認した。

- 1.0 エラッタ `-19`: Section 12.2.2 に末尾の `/` を取り除く規則が戻った(#775)。Section 13.6.3「Transaction Code Guessing」が加わった(#686)。
- 1.1 の Interactive Authorization(Section 6): Authorization Challenge Endpoint を使う First-Party Applications のプロファイルになった(#736)。401 ではなく 403 を返す(#781)。インタラクション種別は URN になった(#712)。
- 1.1 の `auth_session`: インタラクション種別が求める場合だけ必須(#706)。ウォレットは最新の値を送る(#710)。DPoP を使う場合、AS はこれを DPoP 公開鍵と結び付けなければならない(MUST)(#803)。
- 1.1 の `auth_via_web`: ウォレットは `request_uri` を一度だけ使い(#704)、並行セッションを持つときは `state` を送る(#797)。
- 1.1 の Credential Response: `credential_metadata`(#721)、`credential_dataset_id` と `credential_dataset_tag`(#472)。Token Error Response: `invalid_tx_code`(#686)。
- 1.0 と 1.1: 遅延発行の例が `202 Accepted` になった(#722)。鍵バインディングが不要なら `cryptographic_binding_methods_supported` を省く(#714)。
- s2s: 最初のドラフト(#753)、snake_case のプロパティ(#809)。オープン: 識別子の名前変更(#810)、遅延クレデンシャル(#816)。
- 1.0 と 1.1 でオープン: `issuer_redirect_uri`(#759)、proof の種類ごとの `nonce` の条件(#678)。1.1 でオープン: `error_code` の記述の修正(#819)。

## 影響分析

- 上流: Interactive Authorization は First-Party Applications ドラフトに依存し、-04 に固定している。#819 が記述の修正で済むのは、そのエラー形式(`error`、Section 5.2.2)のためである。SD-JWT VC のフォーマットプロファイルは、固定された Final 前の SD-JWT VC の版に依存する。
- 下流: HAIP 1.0 は OpenID4VCI をプロファイルしている(OpenID DCP WG の仕様一覧ページ)。1.0 Final で作ったウォレットと発行者は、エラッタのメタデータ規則の影響を受ける。1.1 も追う実装は、`invalid_tx_code` と Credential Dataset のパラメーターの影響を受ける。
- 互換性: #775 は末尾が `/` の識別子のメタデータ URL を変え、#744 はこれを技術的には破壊的変更だとしている。#686 は Transaction Code の誤りに返すエラーを `invalid_grant`(1.0)から `invalid_tx_code`(1.1)に変えた。#819 は通信内容を変えない。s2s の名前変更は、安定版のないドラフトの中で JSON の名前を変える。
