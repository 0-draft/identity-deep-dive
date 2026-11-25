# 検証ログ

## 環境

- ランタイム: Python 3.15.2
- ツール: `cryptography` 50.0.2（Ed25519、ECDSA P-256）
- バージョン: draft-miao-wimse-http-signature-test-vectors-00（IETF アーカイブのテキスト、2026 年 11 月 26 日に取得）

## 手順

1. -00 の Section 3 と 4.1 から、5 つのテスト鍵、WIT-A、P-01 のメッセージを、RFC 8792 の折り返しを外して `vectors/lab1.py` に写す。
2. `python3 -I vectors/lab1.py > vectors/lab1.log` を実行する。
3. `vectors/lab1.log` を読む。鍵ごとに 1 行、WIT-A の確認、P-01 を署名し直した結果 2 行が出る。

## 結果

- 2026 年 11 月 26 日: どの鍵も Section 3 のとおりシードから導出できた。issuer、svcA、svcB、other は、`d` が `SHA-256("s01-validation-vectors:<name>")` の base64url で、公開鍵の `x` も一致した。svcC は、スカラー `SHA-256("s01-validation-vectors:svcC") mod (n-1) + 1` から公開の `d`、`x`、`y` が得られた。
- WIT-A は発行者の鍵で検証に通り、ペイロードは Section 3 のとおり `iat` が T0-60、`exp` が T0+3600、`cnf.jwk` が vec-a-key だった。
- P-01 のベースを svcA の鍵で署名し直すと、公開の Signature 値とバイト単位で一致するのは、`workload-identity-token` の行に WIT-A の全文を入れたときだけだった。印刷どおりのプレースホルダー `[WIT-A，§2 全文]` では値が違った。

## 失敗パターン

- -00 の本文に印刷されたとおりのプレースホルダーで署名ベースを組むと、P-01 の署名は一致しない。Section 2 は、プレースホルダーが署名対象にそのまま残ると書いている。

## 次にやること

- 動いているサーバーに対して Lab 2 を実行し、ベクターごとの HTTP ステータスを記録する。
- 実際のサーバーに対して Lab 3（N-17、N-18、N-20）を実行する。
