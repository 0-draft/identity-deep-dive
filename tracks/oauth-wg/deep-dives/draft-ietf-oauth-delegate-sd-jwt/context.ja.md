# Context

## きっかけ

`subject.json` は次の理由を挙げている: 「PR #15 restructures where security claims live in the KB-SD-JWT and defines their delegation semantics.」この pull request は用意された資料に含まれず、確認していない。対象は oauth-wg トラックの draft-ietf-oauth-delegate-sd-jwt の revision 00 であり、Datatracker の状態は Active、I-D Exists、WG Document である。

## なぜ重要か

この draft は SD-JWT (RFC 9901) を拡張し、Holder が提示を別の主体へ委任できるようにする。例として AI エージェントが挙げられている (Abstract、Section 1)。KB-JWT 自体が SD-JWT になり得るように変えるため、委任に対応したい SD-JWT の Verifier やウォレットは、連鎖したトークン、新しい `typ` 値、`issuer_jwt_hash` claim を扱う必要がある (Section 5.1.4、6)。連鎖に関するセキュリティ規則は、主に Section 8.1 と Section 6 にある。

## 未解決の問題

- `delegate_payload` 配列、Delegate Payload オブジェクト、Disclosure のダイジェストの対応は、例で示されていない (Section 5.1.3、5.1.4)。
- 委任が前の付与を狭める方向にしか行えないかどうかは記載されていない (Section 8.2)。
- プライバシーに関する節は RFC 9901 を指すだけである (Section 9)。
- PR #15 の内容は資料に含まれないため、-00 との関係は不明である。
