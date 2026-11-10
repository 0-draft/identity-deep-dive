# 相互運用性チェックリスト

- [ ] credential_type が配列になった（pull request #61）こと、および README が Editor's Copy は承認された Working Group Draft ではないと述べていることから、実装が対象とする Editor's Copy の版を確認する。
- [ ] 配列化の後で、単一の credential type を持つ要求と複数の credential type を持つ要求の両方が正しく解析されることを試験する。
- [ ] 要素名が現在の Editor's Copy の大文字小文字（例: CredentialQuery、scenario_sets。pull request #83、#82、#73、#59）に従っていること、および旧来の大文字小文字を解析器が意図どおりに拒否または処理することを確認する。
- [ ] ISO mdoc と IETF SD-JWT VC の扱いが、古い中核本文ではなく形式別附属書（pull request #57）に従っていることを検証する。
- [ ] pull request #76 が不整合を報告しているため、実装するすべてのメッセージについて CDDL と本文を比較する。
- [ ] pull request #77 がマージされた場合、1 クエリに対する複数 credential と 1 credential に対する複数クエリを返す応答を試験する。
- [ ] pull request #64 がマージされた場合、署名またはハッシュ計算を行う CBOR が仕様の要求する deterministic encoding を用いていることを確認する。
- [ ] pull request #65 がマージされた場合、ヘッダーの配置を含め、X.509 証明書チェーンによる reader authentication を確認する。
- [ ] pull request #85 がプレースホルダーを追加するだけであるため、セキュリティ考慮事項の本文にはまだ頼らない。
