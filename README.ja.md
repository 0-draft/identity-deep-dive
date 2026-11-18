# Identity Deep Dive

OAuth WG、WIMSE、OpenID Foundation の仕様を集めてスコアを付け、深掘りの候補を挙げる。

**サイト: <https://0-draft.github.io/identity-deep-dive/ja/>** ([English](https://0-draft.github.io/identity-deep-dive/)) · README: [English](README.md)

この repo は ID 系標準の動きを監視し、何が変わったかを Claude に解説させ、その結果をデータとサイトに残す:

- **ブリーフィング**: 6 時間ごとに、新しいドラフトの改訂、メーリングリストのスレッド、PR を要約・図・ユースケース付きで解説する。週ごとの注目も出す。
- **仕様マップ**: OAuth、OpenID、ワークロード ID の仕様をレイヤーごとに並べ、状態、関係、解説、採用状況を載せる。採用状況は引用元ページと毎日照合する。
- **深掘り**: トピックごとの調査 (背景、仕様メモ、相互運用チェックリスト、ハンズオンログ)。毎週ソースの原文から下書きし、レビューしてからマージする。

## トラック

| トラック                         | 対象                                           | ソース                            |
| -------------------------------- | ---------------------------------------------- | --------------------------------- |
| [IETF WIMSE](tracks/ietf-wimse/) | Workload Identity in Multi-System Environments | Datatracker, Mail Archive, GitHub |
| [OAuth WG](tracks/oauth-wg/)     | OAuth WG のドラフトと実装                      | Datatracker, Mail Archive, GitHub |
| [OpenID](tracks/openid/)         | OpenID Foundation の仕様とリポジトリ           | GitHub                            |

どのトラックも同じパイプラインで動く:

```text
Collect  ->  Normalize  ->  Score  ->  Report  ->  Explain  ->  Synthesize
```

## クイックスタート

```bash
cd tracks/ietf-wimse
python3 -m venv .venv && source .venv/bin/activate
make install
make update        # collect + normalize + score + 日次レポート
make weekly        # collect + normalize + score + 週次ダイジェスト
```

トラックを足すときは `templates/new-track` を `tracks/<name>` にコピーし、[docs/automation.md](docs/automation.md#wiring-a-new-track) の手順で配線する。深掘りを始めるときは `templates/deep-dive` を `tracks/<track>/deep-dives/<topic>` にコピーする。

## 構成

```text
tracks/              トラックごとのパイプライン、レポート、深掘り
data/                仕様マップ、解説、RFC 本文、synthesis
templates/           トラック、深掘り、仕様解説、ラボレポートの雛形
scripts/             共通コード (insights、深掘りの下書き、仕様マップ、RFC 翻訳)
web/                 サイト
.github/workflows/   CI
```

## ドキュメント (英語)

- [docs/automation.md](docs/automation.md): パイプラインの各段階、全ワークフロー、トラックの追加手順
- [docs/site.md](docs/site.md): サイトの各ページと、そのデータの置き場所

## ライセンス

[MIT](LICENSE)
