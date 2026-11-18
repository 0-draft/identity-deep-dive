# Context

## きっかけ

draft のリポジトリの [PR #15](https://github.com/oauth-wg/oauth-delegate-sd-jwt/pull/15)「Move security claims to base KB-SD-JWT payload and define claim semantics」。2026-11-10 に作成され、2026-11-18 時点で open である。Issue #3 と #10 を解決するもので、`cnf`、`exp`、`nbf` などのセキュリティ claim を `delegate_payload` からベースの KB-SD-JWT ペイロードへ移し、連鎖の各段で各 claim が何を意味するかを定め、Verification 節を更新する。対象は oauth-wg トラックの draft-ietf-oauth-delegate-sd-jwt の revision 00 であり、Datatracker の状態は Active、I-D Exists、WG Document である。

## なぜ重要か

この draft は SD-JWT (RFC 9901) を拡張し、Holder が提示を別の主体へ委任できるようにする。例として AI エージェントが挙げられている (Abstract、Section 1)。KB-JWT 自体が SD-JWT になり得るように変えるため、委任に対応したい SD-JWT の Verifier やウォレットは、連鎖したトークン、新しい `typ` 値、`issuer_jwt_hash` claim を扱う必要がある (Section 5.1.4、6)。連鎖に関するセキュリティ規則は、主に Section 8.1 と Section 6 にある。

## 未解決の問題

- `delegate_payload` 配列、Delegate Payload オブジェクト、Disclosure のダイジェストの対応は、例で示されていない (Section 5.1.3、5.1.4)。PR #14 が具体例を提案している。
- 委任が前の付与を狭める方向にしか行えないかどうかは、-00 には書かれていない (Section 8.2)。Issue #8 がこれを求めており、PR #15 が狭めることを求めるのは `exp` と `nbf` だけである。
- プライバシーに関する節は RFC 9901 Section 10 を指すだけである (Section 9)。
- PR #15 はマージされていないため、-00 のどこが変わるかはまだ確定していない。
