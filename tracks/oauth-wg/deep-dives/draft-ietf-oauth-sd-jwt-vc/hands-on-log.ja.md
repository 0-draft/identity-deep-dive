# 検証ログ

## 環境

- ランタイム: Python 3.15.2
- ツール: `cryptography` 50.0.2 (ECDSA P-256 の検証)、ドラフト本文の取得に `curl`
- バージョン: draft-ietf-oauth-sd-jwt-vc-24、-25、-26 (`https://www.ietf.org/archive/id/` の `.txt`)。2026 年 11 月 15 日に実行

## 手順

1. ドラフトを取得する: `curl -sfL -o draft-ietf-oauth-sd-jwt-vc-26.txt https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-26.txt` (-24、-25 も同様)。
2. 各版で `python3 -I vectors/verify_examples.py draft-ietf-oauth-sd-jwt-vc-26.txt 7 8 10 24 26` を実行する。スクリプトは各 Figure の見出しの直前にあるコンパクト形式を読み、Figure 14 から Issuer の鍵を取り、ES256 の Issuer 署名を検証する。各 Disclosure の SHA-256 ダイジェストを、ペイロードの `_sd` 配列、配列の `...` 要素、入れ子の Disclosure の中から探す。KB-JWT があれば `cnf.jwk` で検証し、最後の `~` までの SD-JWT から `sd_hash` を計算し直す。
3. スクリプトが失敗を検出できることを確かめる。Figure 7 の Disclosure を 1 文字変えると `digests-not-found=1`、Figure 10 の署名を 1 文字変えると `issuer-sig=FAIL` になる。

## 結果

- 出力は `vectors/verify_examples.log` にある。3 つの版すべてで `ALL OK` が出た。
- -26: Figure 7、8、10、24、26 の `typ` は `dc+sd-jwt` で、Issuer 署名は `doc-signer-05-25-2022` で検証できる (`kid` でこれを名指ししているのは Figure 7 と 8 だけ)。Disclosure は 9、2、2、28、3 個で、どれもダイジェストが所定の場所にある。Figure 8 と 26 の KB-JWT は検証でき、`sd_hash` も一致する (`iat` は 1793905352)。
- -25 は -26 と同じ出力になる。
- -24 も検証には通るが、エンコード済みの例はすべて `typ` が `vc+sd-jwt` で、KB-JWT の `iat` は 1724705969 (2024 年 8 月 26 日)、Figure 24 の Disclosure は 28 個ではなく 21 個である。

## 失敗パターン

- -24 から例を取る: `typ` が `vc+sd-jwt` で、-24 の本文自体がもう認めていない値である。
- すべての例に `kid` があると思い込む: Figure 10、24、26 にはないので、Figure 14 の鍵を順に試す必要がある。

## 次にやること

- Appendix A.2 の Type Metadata の例 (Figure 30) と `vct#integrity` の値を、対応する文書と突き合わせる。
