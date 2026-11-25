# 背景

## きっかけ

リビジョン -00 は 2026 年 11 月 18 日に、想定ステータス Informational の個人提出として公開された。Datatracker ではワーキンググループに属していない。これは、2026 年 11 月 6 日に ietf-wg-wimse/draft-ietf-wimse-s2s-protocol の issue #419 で最初に公開され、同じ日に WIMSE メーリングリストで「Test vectors for draft-ietf-wimse-http-signature-08 — request for review」として告知されたベクター集の v4 を、Internet-Draft の形にしたものである（Section 1、Appendix B）。

Section 1 のリポジトリー名は正しい。ietf-wg-wimse/draft-ietf-wimse-s2s-protocol は WIMSE の作業用リポジトリーで、draft-ietf-wimse-http-signature、draft-ietf-wimse-workload-creds、draft-ietf-wimse-wpt、draft-ietf-wimse-mutual-tls など複数のドラフトをビルドする（リポジトリーの README）。名前は draft-ietf-wimse-s2s-protocol に由来し、draft-ietf-wimse-http-signature-00 はそこから切り出された（基底 -08 Appendix B.9）。

レビューは issue とメーリングリストで行われた。2026 年 11 月 7 日に基底仕様の共著者 Yaron Sheffer が、`@query` の行に先頭の `?` を付けるよう求め、メーリングリストで「a MUST NOT in any security RFC should be rejected by the recipient」と答え、例の nonce の注記のために issue #420 を開いた。issue には独立した実行結果が 2 件投稿され（2026 年 11 月 7 日と 11 日）、11 月 13 日に P-04 の `@authority` の値が直され、issue は 2026 年 11 月 16 日にクローズされた（「Closing, nothing more to address in the draft.」）。2026 年 11 月 20 日には draft-ietf-wimse-http-signature-09 が出た。その変更履歴は、CONNECT の `@authority` の文言について #419 を、例の nonce の注記について #420 を挙げている（-09 Appendix B.1）。

## なぜ重要か

基底ドラフトは IESG で AD Evaluation の段階にあり（Datatracker、UTC で 2026 年 11 月 25 日に確認）、文面はほぼ固まっている。基底仕様の例は正例のやり取り 2 つだけである（基底 Section 3.7.1、3.7.2）。このセットは、それぞれ 1 つの MUST に対応する負例 23 件と公開の鍵を加え、署名の比較だけでなく判定の比較もできるようにする。ベクターを書いたことで基底はすでに動き、2 点が -09 に入った。また、基底が送信者向けにしか書いていない規則（`keyid`、`alg`、カバー範囲、CONNECT）があり、検証者がそれを強制するかどうかを自分で決める必要があることも見えてくる。ドラフト自身の文面にも、使う前に確かめるべき点がある。署名ベースのプレースホルダーは実際に署名される内容ではなく、N-04 の注記は署名が失敗すると書いているが、実際には失敗しない。

## 未解決の問い

- WIMSE ワーキンググループはこのセットを引き取るか。引き取るならどの形か。Yaron Sheffer は issue #419（2026 年 11 月 7 日）で、chair に相談するよう作者に勧めている。
- -01 で、基底の参照を -09 に移し、O-2 を外し（注記は -09 Section 3.7 に入った）、N-20 の相互参照を workload credentials ドラフトの Section 5.1.3 に直すか。
- 送信者向けの規則に反するメッセージ（N-01、N-02、N-06、N-07、N-21）を受信者が拒否することを、基底に書くべきか。11 月 7 日のメーリングリストでの返信はそう述べているが、-09 にその文言はない。
- WIT プレースホルダーの「deterministic expansion」（Section 2）は正確には何か。issue #419 の v4 の告知が触れている関連の適合性テストスイートはどこにあるか。
- N-04 の注記は直されるか。cred-ninja の実行は 29 件すべてでやり直されるか。
