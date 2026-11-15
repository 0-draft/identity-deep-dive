# Context

## きっかけ

draft-ietf-oauth-sd-jwt-vc-23 に対する ARTART の telechat レビューが 2026 年 11 月 3 日に Ready を返し、続いて -23 に対する IESG のバロットがあった。著者は 11 月 5 日に -24 と -25、11 月 6 日に -26 で応えた。Datatracker (2026 年 11 月 15 日に確認) では、ドラフトは -26 で Active、WG の状態は Submitted to IESG for Publication、IESG の状態は IESG Evaluation::AD Followup、action holder は Deb Cooley で、telechat の日付は設定されていない。IANA のレビュー状態は Version Changed - Review Needed、IANA の専門家レビューの状態は Expert Reviews OK である。-26 に対する SECDIR の telechat レビューは 2026 年 11 月 8 日に Ready を返した。

## なぜ重要か

このドラフトは、ウォレットや Verifier の実装が SD-JWT ベースの資格情報に使う形式を定める。その HTTP 取得規則と Type Metadata の規則は、`iss` や `vct` の URL からメタデータを取得するすべての実装に適用される。バロットを受けて、実装者にとって重要な箇所が二つ変わった。-24 で、ドラフトは RFC 7800 を更新し、どの JWT でも `sub` や `iss` なしで `cnf` を使えるようにした (Section 2.2.2.3.1)。これで Mike Bishop の DISCUSS は解消された。-24 はあわせて、JWT VC Issuer Metadata と `x5c` のどちらを使うかを選ぶのは資格情報ではなく受信者のポリシーであり、使っていない方式の入力は Issuer を識別しないと定めた (Section 2.5)。残る DISCUSS は Section 2.2.2.2 と 2.4 の SHOULD に対する Éric Vyncke のもので、-25 がその文言を変えている。

## 未解決の問題

- Éric Vyncke は -25/-26 で DISCUSS を解消するのか、それとも Section 2.4 の status 確認の SHOULD についてさらに求めるのか。
- Section 7.1 は、閉じた環境のために、許可リストのようなローカルに設定された宛先を認めるのか。-26 は認めていない。
- Mahesh Jethanandani が提案するように、後の改訂で `extends` のチェーンの深さや資格情報ごとの取得総数に上限が設けられるのか。-26 にはない。
- 後の改訂で、メタデータ文書に専用のメディアタイプが付くのか、また Section 4.3 にリダイレクトにかかわらず `issuer` が `iss` と等しくなければならないと書かれるのか。-26 はどちらもしていない。
