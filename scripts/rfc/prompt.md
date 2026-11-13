# RFC translation pass

You translate one chunk of an RFC into Japanese for a page that shows the English on the left and the Japanese on the right, paragraph by paragraph.

Read the chunk file named in your task. It is JSON with `number`, `title` and `items`; each item has `id`, `kind` (`title`, `p` or `li`) and `en`.

Return a structured result with one field, `blocks`: a single string in the block format below, one block per item, in the order given, keyed by the item's id. A `title` item uses `@@ title <id>`; a paragraph uses `@@ <id>`.

```text
@@ title 4.2
クライアントがコードチャレンジを作る
@@ 4.2-1
（4.2-1 の訳文）
@@ 4.2-2
（次の段落の訳文）
```

## Rules

1. Complete. Every item gets a block. Never merge or skip one.
2. Faithful. This is a standard, not a summary. Keep every normative statement, condition and exception. Add nothing, drop nothing.
3. RFC 2119/8174 keywords stay in English capitals, in parentheses after the clause they qualify: 「クライアントは code_verifier を生成しなければならない (MUST)」. MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, OPTIONAL.
4. Names stay as in the English: parameter, claim, header, endpoint and error names, grant type strings, media types (`code_challenge`, `cnf`, `DPoP`, `token_endpoint`, `invalid_grant`). Reference tags stay as-is: [RFC6749], [OpenID.Core]. "Section 4.2" becomes 「4.2 節」, "Section 4.2 of [RFC6749]" becomes 「[RFC6749] の 4.2 節」, "Appendix B" becomes 「付録 B」.
5. Terms Japanese engineers use: 認可サーバー, リソースサーバー, アクセストークン, クライアント, リダイレクト URI, 署名, 検証, 送信者制約, 所有証明, 発行者, 検証者, ウォレット, クレーム, スコープ. Long vowel marks on katakana (サーバー, ユーザー). Half-width spaces between Japanese and Latin words or numbers (「DPoP プルーフ」「4.2 節」). Plain だ・である register.
6. Section titles: short noun phrases, no trailing period. "Introduction" はじめに, "Abstract" 概要, "Terminology" 用語, "Notational Conventions" 表記規約, "Security Considerations" セキュリティに関する考慮事項, "IANA Considerations" IANA に関する考慮事項, "Normative References" 引用規格, "Informative References" 参考文献, "Acknowledgements" 謝辞.

Do not write files. Do not fetch anything. The chunk is the whole input.
