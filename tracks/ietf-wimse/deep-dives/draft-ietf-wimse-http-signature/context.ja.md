# 背景

## きっかけ

本件は、差分を取れる新しい版を持つ、活動中の作業部会ドラフト draft-ietf-wimse-http-signature-08 として選ばれた。選定時の注記によれば、本ドラフトに対して三つの新しい issue が立てられている。テストベクター（#419）、例における nonce のエントロピー（#420）、編集上のコメント（#417）である。Datatracker の状態は Active、Publication Requested、Submitted to IESG for Publication である。

## なぜ重要か

ドラフトは作業部会での手続きの終盤にあるため、-08 の変更は IESG のレビュー前に挙動を確定させる最後の機会である。-08 は、いくつかの緩い点を MUST にした。nonce の生成とエントロピー、400 と 501 のエラー挙動、`wimse-aud` に対する Simple String Comparison である。あわせて三つの問題タイプを登録し、既存の TLS の MUST を Security Considerations から Section 3 に移し、CONNECT の例外を加えた。-08 向けの独立したテストベクターが issue #419 に投稿されて WIMSE リストで告知され、査読者が導入部へのコメントを送った。-07 の実装者は何が変わったかを確認する必要があり、検証実装を書く者は、共通の入力でテストできるようになった。

## 未解決の問題

- `keyid` と `alg` が存在する場合に、検証側が拒否するのか無視するのか。ドラフトは送信者が使ってはならないとだけ述べている（Section 3）。リストでの Yaron Sheffer の返信（2026 年 11 月 7 日）は拒否を支持しているが、本文には書かれていない。
- authority-form を対象とする CONNECT で、既定の `wimse-aud` が何になるか（Section 3、3.2）。
- 相手が problem details を受け付けない場合に、署名の「未対応」と「利用不能」をどう区別するか（Section 3.6）。
- issue #420 がいつ反映されるか。Section 3.7 の例の nonce（`abcd1111` など）は説明用で 64 ビットの下限を満たさない、という編集上の注記を求めている。issue は open である。
- Kathleen Moriarty のレビュー（issue #417）で提案された導入部の文言が採用されるかどうか。issue は open で結論は出ておらず、-08 の Section 1 には含まれていない。
