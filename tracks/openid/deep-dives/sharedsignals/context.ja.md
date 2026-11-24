# Context

## Trigger

`subject.json` には選定理由が記録されていない（`ai_note` は空である）。以前のシグナルは、`insights.md` にある、デフォルトブランチへの新しいコミット一つ "Drop event signatures (#368)" についての概要のみである。

## Why This Matters

このリポジトリは SSF、CAEP、RISC の開発の場であり、現在は保持されている 1.0 Final Specifications と並んで SSF 1.1 と CAEP 1.1 の草案を持つ。ここでの変更は 1.0 を実装する Transmitter と Receiver に影響し得る。資料にあるのはプルリクエストのタイトルだけであるため、各変更の大きさは分からない。

## Open Questions

- #368 は何を削除するのか。その理由は何か。
- 未マージの署名アルゴリズムのネゴシエーション（#355）とクローズされたアルゴリズム厳格性の変更（#356）は、これとどう関係するのか。
- 1.1 は 1.0 と後方互換か。
