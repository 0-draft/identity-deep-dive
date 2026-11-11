# 相互運用性チェックリスト

- [ ] 実装の対象にした `openid/dchp` のコミット (例: `4ddd238`) を記録する。README は Editor's Copy が承認された Working Group Draft ではないと述べており、中核の節はどれもまだワーキンググループの合意を得ていない。
- [ ] `CredentialQuery.credential_types` (キー 2) を文字列の配列としてエンコードする (pull request #61)。n 個の type を持つクエリが n 個のクエリとして処理され、それを参照する組み合わせも同じように展開されることを確かめる。
- [ ] SD-JWT VC の `credential_format` には `vc+sd-jwt` ではなく `dc+sd-jwt` を使う (pull request #57)。`credential_types` は mdoc の `docType` または SD-JWT VC の `vct` と、大文字小文字を区別する文字列比較で照合する。
- [ ] `ChannelBinding` の整数キーは、相手と合意した 1 つの出典から取る。`main` では本文と CDDL が食い違っており、`dc_api_origin` は本文ではキー 8、CDDL ではキー 7 で、BLE のフィールドも違う。未マージの pull request #76 は本文の番号にそろえる。
- [ ] 2 種類の transaction transcript を決定的 CBOR (RFC 8949 Section 4.2。未マージの pull request #64 は Section 4.2.1 に限定する) でエンコードし、verifier と wallet が `RequestPayload` バイト列について同じ SHA-256 を得ることを確かめる。
- [ ] 応答の暗号化で HPKE の info にどちらの transcript を使うかを相手と決めておく。transcript の説明の箇条書きと CDDL のコメントは `ReaderTransactionTranscript`、「Use in Protocol Operations」の表は `WalletTransactionTranscript` としている。
- [ ] セッション層の暗号がない場合 (Digital Credentials API、スキームによる起動) は必ず応答を暗号化する。`encrypted` の各要素が復号すると `Envelope` になる `COSE_Encrypt` であること、`encryption_ref` が `additional_encryption_contexts` の正しい要素を指していることを確かめる。
- [ ] `reader_auth` を、`RequestPayload` バイト列と `ReaderTransactionTranscript` を detached payload とする `COSE_Sign` として検証する。reader の鍵の伝え方は未定で、pull request #65 は protected header に `x5chain` を入れる案を出している。
- [ ] `issuer_identifiers.x509_ref` を、mdoc の `IssuerAuth` の `x5chain` または SD-JWT VC の `x5c` ヘッダーにある各証明書の Authority Key Identifier (RFC 5280) の `keyIdentifier` と照合する。
- [ ] 鍵に束縛されていない mdoc や KB-JWT のない SD-JWT VC は、`support_no_cryptographic_binding` が `true` のときだけ返す。本文が定めているのはこの wallet 側の規則だけなので、フラグを立てていないのにそうした credential が届いた場合の verifier の扱いは自分で決める。
- [ ] SD-JWT VC の束縛ではまだ相互運用しない。KB-JWT の `nonce` は `WalletTransactionTranscript` の SHA-256 だが、その文字列エンコーディングと `aud` の値は未定である (issue #10)。SD-JWT VC の `path` も未定である (issue #52)。
- [ ] pull request #77 がマージされたら、応答の解析を `CredentialRef` をキーとする map から `query_refs` を持つ配列に移す。1 つの credential が 2 つのクエリに答える場合と、`allow_multiple` のもとで 2 つの credential が 1 つのクエリに答える場合を試験する。
- [ ] Security Considerations の本文には頼らない。`main` には存在せず、pull request #85 もプレースホルダーを足すだけである。
