# 仕様ノート

## 参考文献

Section 7 に挙げられている引用規格:

- RFC 2119, Key words for use in RFCs to Indicate Requirement Levels (BCP 14)
- RFC 8174, Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (BCP 14)
- RFC 8785, JSON Canonicalization Scheme (JCS)
- RFC 8032, Edwards-Curve Digital Signature Algorithm (EdDSA)

参考規格: ドラフトには参考文献の節がない。

本文で言及されているが Section 7 に挙げられていないもの:

- RFC 8693, OAuth 2.0 Token Exchange（Section 1）
- RFC 8949, Concise Binary Object Representation (CBOR)。決定的エンコーディングのため（Section 3）
- OAuth 2.1、GNAP、「WIMSE Wit/Wpt tokens」（Abstract）と WIMSE Workload Identity Token（Section 1）。参照なしで名前だけが挙げられている。
- COSE_Sign1（Abstract）。参照なしで名前だけが挙げられている。
- draft-durga-agenttrust-trace-verification-00。本ドラフトが補完する「foundational execution-trace verification architecture」として述べられている（Section 1）。

## 主な変更点

リビジョン 00 であり、以前のリビジョンも `diff.txt` もない。導入されるもの:

- `cta_version`、`invocation_id`、`parent_trace_ref`、`system_prompt_digest`、`data_plane_merkle_root`、`taint_lattice_level`、`tool_effect_class`、`step_up_receipt_hash`、`iat`、`exp`、および `alg`、`kid`、`sig` を持つ `signature` メンバーからなる Context Taint Attestation オブジェクト（Section 3）
- `Agent-Ctx-Isolation` ヘッダー、または JSON-RPC/MCP の `_meta.ctxIsolation` による運搬（Section 3）
- 三つの不変条件: `TAINT_LATTICE_MONOTONICITY`、エラー `ERR_TAINTED_CONTROL_PLANE` を伴う `CONFUSED_DEPUTY_FAIL_CLOSED`、`CONTEXT_MERKLE_BINDING`（Section 4）
- 60 秒を超える時計のずれ、ダイジェストの不一致、バインディングの欠落に対するフェイルクローズの処理と、監査可能な拒否レシート（Section 5）
- IANA への要求: メディアタイプ `application/agent-ctx-isolation+json`、テイントレベルのレジストリ（`TRUSTED_ONLY`、`MIXED_TAINT`、`UNTRUSTED_INGESTED`、`QUARANTINED`）、ヘッダーフィールド `Agent-Ctx-Isolation` と `Agent-Step-Up-Receipt`（Section 6）

本文から見える欠落: Abstract は COSE_Sign1 とするが Section 3 は JSON の署名オブジェクトを示す。マークルツリーの構築、ステップアップレシートの形式、ヘッダーのエンコーディングは定義されていない。例では何に署名するのかが明確でない。例の値はプレースホルダーで、ダイジェストは短い文字列の SHA-256（`data_plane_merkle_root` は空入力、`parent_trace_ref` は `test`、`kid` は `test1`）、`exp` は `iat` の 60 秒後である。

## 影響分析

- 上流: 正規化と署名は JCS（RFC 8785）と EdDSA（RFC 8032）に、テイントレベルの追跡はエージェントランタイムに依存する。RFC 8693 や WIMSE トークンとの対比を述べるが、それらとの結び付けは定義していない。関連ドラフト draft-durga-agenttrust-trace-verification-00 は Section 1 で名前が挙がるが、参考文献には挙げられていない。`parent_trace_ref` がそのドラフトを指すとはどちらのドラフトにも書かれておらず、関連ドラフト側のレコードのフィールドは `parent_record_hash` である。
- 下流: Section 4 を強制したいすべての MCP または A2A のツールサーバーやゲートウェイは、ヘッダーの解析と検証、署名者の鍵の管理、ステップアップ承認経路の実装が必要になる。メディアタイプ、テイントのレジストリ、二つのヘッダーについて、新たな IANA 登録が必要になる。
- 互換性: 制御プレーンのすべてのツール呼び出しで必須であり（Section 3）、ネゴシエーションやフォールバックは述べられていない。Section 3 は Deterministic CBOR を認めるが Section 5 は JCS を要求するため、実装が分かれ得る。メールは `ctx_isolation_witness` と `policy_manifest_sha256` に言及するが、これらはどちらのドラフトのリビジョン 00 にもないため、今後のリビジョンで構造が変わる可能性がある。
