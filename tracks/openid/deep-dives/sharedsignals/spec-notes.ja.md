# Spec Notes

## References

投入された資料は README であり、規範的参照や参考参照は列挙されていない。リポジトリが保持する文書として次が挙げられている。

- Shared Signals Framework 1.1（草案）と 1.0（最終版）
- CAEP 1.1（草案）と 1.0（最終版）
- CAEP Interoperability Profile 1.0（草案）
- RISC 1.0（最終版）

挙げられているビルドツールは `xml2rfc` と `kramdown-rfc` である。

## Key Changes

- #310（マージ済み）: 1.0 から 1.1 の草案文書を作成し、1.0 を保持する。
- #368（マージ済み）: "Drop event signatures"。差分は投入されていないため、範囲は未検証である。
- #343（マージ済み）: OIDF レビュー用に CAEP Interoperability Profile の Draft-01 を作成する。
- #349（マージ済み）: CAEP Interoperability Profile にリスクレベル変更のユースケースを追加する。
- #315（マージ済み）: CAEP Interoperability Profile に Receiver 要件を追加する。
- 未マージの提案: #366 複合サブジェクト、#355 SET 署名アルゴリズムのネゴシエーション、#369 JSON null の扱い、#367 CORS の推奨、#362 サブジェクトまたはプリンシパルとしてのエージェントとワークロード、#363 CAEP Interoperability Profile の仕様バージョンの節、#329 デバイスコンプライアンス変更におけるデバイス管理状態。

## Impact Analysis

- Upstream: 資料はビルドツール以外の依存を挙げていない。SET 形式や JWT および JWS の仕様への依存はあり得るが、資料には述べられていない。
- Downstream: SSF と CAEP の Transmitter および Receiver の実装者、ならびに CAEP Interoperability Profile に従う導入者。
- Compatibility: 1.0 の文書は保持され、1.1 は別のフォルダーである。1.1 が 1.0 と互換かどうか、#368 が 1.0 の Receiver にとって何を意味するかは示されていない。
