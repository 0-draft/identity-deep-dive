# 検証ログ

## 環境

- ランタイム: Python 3.15.2
- ツール: `cryptography` 50.0.2（Ed25519、RFC 6979 の決定論的署名による ECDSA P-256）、ドラフトのソース取得に `gh`
- バージョン: draft-ietf-wimse-http-signature-08（ietf-wg-wimse/draft-ietf-wimse-s2s-protocol のタグ `draft-ietf-wimse-http-signature-08`）、issue #419 のベクター（2026 年 11 月 7 日の再生成後の値）

## 手順

1. Section 3.7 の例が使う `sigs-*.txt` のインクルードファイルを、タグ `draft-ietf-wimse-http-signature-08` からローカルの `includes/` に取得する（`gh api repos/ietf-wg-wimse/draft-ietf-wimse-s2s-protocol/contents/<file>?ref=draft-ietf-wimse-http-signature-08 -H "Accept: application/vnd.github.raw"`）。
2. `python3 -I vectors/verify_419.py includes/ > vectors/verify_419.log` を実行する。issue #419 のベクターの入力とテスト用の鍵はスクリプトに書き込んであるので、インクルードファイルが要るのは Section 3.7 の例の検査だけである。
3. ログ末尾の集計表と、N-01、N-04、N-06、N-07、N-09、N-15 の個別の注記を読む。

## 結果

- ログの 0 節: テスト用の鍵はどれも `SHA-256("s01-validation-vectors:<name>")` から導かれ（svcC は n-1 で割った余りに 1 を足す）、三つの WIT は発行者の鍵で検証に通る。
- 1 節: スクリプトは公開されている 8 本の署名（P-01〜P-05、P-06 の 2 本、N-15）をバイト単位で再現する。
- 負例の多くは、issue が説明する変更をこのリポジトリが再構成したもので、issue のバイト列ではない。どのベクターがどの入力を使ったかは仕様メモに書いた。
- 期待結果と食い違ったベクターはなかった。受理か拒否かを判定する 22 本と、振る舞いを扱う 4 本が一致した。N-17 と N-20 は採点していない。所見は仕様メモの「テストベクターの再実行」にまとめた。

## 失敗パターン

- P-01、P-02、P-06、N-15 に、11 月 7 日の値ではなく issue 本文の元の署名を使う: 元の署名は、先頭の `?` を欠いた `@query` でしか検証に通らない。
- N-04 を署名の失敗として報告する: 署名は正しく、失敗するのは計算し直したダイジェストだけである。

## 次にやること

- N-17 と N-20 を、エラー本文と検査の順序を観測できる実際のサーバーに対して採点する。
- スクリプトの WIT 検証を、ワークロード資格情報ドラフトの本文と突き合わせる。スクリプトはこのリポジトリの読み方に従っており、条項ごとの照合はしていない。
