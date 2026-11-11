# 仕様メモ

## 参照

`4ddd238` 時点の `draft/digital-credentials-harmonized-presentation.md` にある規範的参照 (一覧の最後は「To be completed」):

- ISO/IEC 18013-5、Mobile driving licence (mDL) application。
- RFC 5280 (X.509 証明書と CRL のプロファイル)。発行者照合で使う Authority Key Identifier のため。
- RFC 7515 (JWS)。SD-JWT VC の Issuer-signed JWT の `x5c` ヘッダーのため。
- RFC 9901 (SD-JWT) と draft-ietf-oauth-sd-jwt-vc (SD-JWT VC)。

これらはすべて pull request #57 で追加された (RFC 7515 はコミット `13ca44e`)。本文はこの一覧の外でも、RFC 8610 (CDDL、socket を含む)、RFC 9052 (`COSE_Sign`、`COSE_Key`、`COSE_Encrypt`)、RFC 9360 (`COSE_X509`)、RFC 8949 Section 4.2 (決定的 CBOR)、RFC 8943 (`full-date`)、draft-ietf-cose-hpke、ISO/IEC TS 23220-2 (`age_over_NN`) を引いている。「shall/should/may/can」の使い方は ISO/IEC Directives, Part 2 に従う。

README は ISO/IEC 18013-5 (<https://www.iso.org/standard/69084.html>)、OpenID for Verifiable Presentations 1.0 (<https://openid.net/specs/openid-4-verifiable-presentations-1_0.html>)、Editor's Copy (<https://openid.github.io/dchp/digital-credentials-harmonized-presentation-editors-copy.html>) にリンクしている。

## 主な変更

マージ済み:

- #61 (2026 年 11 月 4 日、8 コミット、issue #46 を close): `credential_type: tstr` が `credential_types: [ + tstr ]` (キー 2) になった。配列に n 個の値があるときの要求の処理方法も定めている。
- #57 (2026 年 11 月 9 日、23 コミット、issue #21、#22、#36 を close): 「Credential Formats」節と、format definition に課す 10 項目の要件。ISO mdoc と SD-JWT VC の附属書。`$formatExtensions` と `$CredentialData` の socket。`CredentialItem.format` から `credential_format` への改名 (map のキーは同じ)。`vc+sd-jwt` から `dc+sd-jwt` への変更。新しい規範的参照。個々のコミットでは、SD-JWT VC の path の意味論を issue #52 に回し (`c029b57`)、authority key identifier に RFC 5280 の名前を使い (`4fae852`)、`support_no_cryptographic_binding` から `DocRequestInfo` への対応付けを削除した (`dfd7dd4`)。
- #29 (2026 年 8 月 16 日): 初期提案。出発点として受け入れられたが、「内容全体についての合意ではまだない」。#7、#11、#15 はリポジトリとビルドの整備である。

未マージ (2026 年 11 月 11 日時点、各 diff の中身):

- #64: 「CBOR Encoding」節を追加する。RFC 8949 Section 4.2.1 の core deterministic encoding を必須にし、NaN と無限大を禁じ、transcript は送信されないと明記する。
- #65: reader authentication に X.509 を使う場合、証明書は `COSE_Signature` の protected header の `x5chain` (RFC 9360) に入れる。先頭の証明書が reader の鍵を持つ。
- #74: M (Mandatory)、C (Conditional)、O (Optional) の略語表を追加する。
- #76 (issue #75 を close): CDDL を本文に合わせる。`ChannelBinding` の番号を振り直し、`cce_handover` を足し、`oidc4vp_*` を `openid4vp_*` に、`nfcv2` を `cce` に改名する。`controlled_id` を `controller_id` に直し、使われていない `full-date` を消し、`* (int / tstr) => any` と括弧付きで書く。
- #77 (issue #69 と #70 を close): `Envelope.credentials` を map から配列にし、`CredentialItem` に `query_refs` (キー 3) を足し、`CredentialRef` を `QueryRef` に改名する。1 つのクエリに複数の item を返してよいかは `allow_multiple` で決まる。
- #81 (issue #67 を close): 「reader」を「verifier」に置き換える。`reader_auth` は `verifier_auth` に、`ReaderTransactionTranscript` は `VerifierTransactionTranscript` になる。
- #83 (issue #58 を修正): `scenario_sets` や `credential_queries` を snake_case にするなど、大文字小文字をそろえる。ワーキンググループは「map のキーは整数なので」編集上の変更と判断した。
- #85 (issue #72 を参照): 「To be completed」とだけ書いた Security Considerations 節と、OIDF の Notices 附属書を追加する。WG Draft を公開できるようにするためである。

マージされずにクローズ:

- #84: 2026 年 11 月 4 日に作られ、1 分以内にクローズされた。#85 は同じブランチ (`72-required-sections`) から、同じ題名、同じ diff で出されている。
- #59、#73、#82: 大文字小文字を直す修正の前の版。#59 と #73 は次の pull request に引き継ぐ形でクローズされ、#82 はマージ競合のため #83 に置き換えられた。

## 影響分析

- Upstream: mdoc の附属書は ISO/IEC 18013-5 の構造 (`Document`、`DeviceAuth`、`SessionTranscript`、`KeyAuthorizations`) をそのまま使う。18013-5 第 2 版との関係を示すのは編集者注の 2 か所である。発行者識別子は「第 2 版で定義中の `IssuerIdentifiers` 構造と同じ規則」に従い、鍵に束縛されていない mdoc は「DIS 投票向けに提案された変更」に従う (issue #56)。SD-JWT VC の附属書は RFC 9901 と draft-ietf-oauth-sd-jwt-vc の上に立つ。issue #53 は `vct` の継承を OpenID4VP と同じように扱うべきかを問い、issue #52 は `path` を OpenID4VP と 18013-5 の claims path pointer にそろえようとしている。
- Downstream: 近接提示とオンライン提示で 1 つのモデルを使いたい wallet と verifier、そしてこのメッセージを運ぶプロトコル。`ChannelBinding` には OpenID4VP と Digital Credentials API のフィールドがすでにある。リポジトリは実装を挙げていない。
- Compatibility: #61 より前に作った要求はキー 2 に文字列を入れているので、配列型に合わない。#57 より前の SD-JWT VC のクエリは `vc+sd-jwt` を使っている。#77 がマージされれば、それ以前に作った応答は `Envelope` の CDDL に合わなくなる。#76 がマージされれば、`main` の CDDL から作った `ChannelBinding` のキーが変わり、transcript のバイト列とハッシュ値も変わる。
