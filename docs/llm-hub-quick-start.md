# llm-hub クイックスタート

> **何**: 機密データ大量処理・32B Qwen 推論・並列バッチ・コスト追跡が必要なときに使う Python パッケージ
> **どこ**: `https://github.com/5co-hub/llm-hub`（Private、5co. 全社員 + Org member 利用可）
> **既存 Ollama 経路との違い**: bash ラッパー (`qwen-call.sh`) は **Drive エコ運用 + 軽量タスク**用、llm-hub は **機密 + 大規模 + Python ライブラリ統合**用。両者は補完。

## 5 分セットアップ（各社員マシン）

### 前提
- macOS（M-series + 64GB RAM 推奨、Mac mini M4 Pro 等）
- Python 3.10+ 利用可
- Anthropic API キー（任意、フォールバック・並列で必要）
- ChatGPT Team サブスク（Codex CLI を使う場合）

### Step 1. リポを clone

```bash
mkdir -p ~/work && cd ~/work
git clone https://github.com/5co-hub/llm-hub.git
cd llm-hub
```

### Step 2. venv 作成 + 依存インストール

```bash
uv venv .venv          # CPython 3.10 で .venv 作成
.venv/bin/python -V

# Python 依存（mlx-lm 等）
bash scripts/install_qwen.sh
# → 最初の実行で Qwen3-32B-4bit を 17GB ダウンロード（10〜30 分）
```

### Step 3. Qwen サーバー起動

```bash
bash servers/start_qwen.sh
bash servers/status.sh   # → /v1/models で疎通 OK 確認
```

サーバーは `127.0.0.1:8001` にバインド。外部接続不可。

### Step 4. 認証セットアップ（任意機能を使う場合）

#### A. Codex（コード生成）

```bash
codex login   # ChatGPT Team サブスクでログイン、追加課金なし
```

#### B. Anthropic API（並列サブタスク・benchmark）

```bash
# 1Password に Anthropic API キーを保存（既存運用に合わせる）
# 2. ~/.zshrc に追記:
export LLM_HUB_ANTHROPIC_KEY="$(op read 'op://claude-code-secrets/Anthropic API Key/credential' 2>/dev/null)"

# Claude Code 自身のサブスク認証への副作用回避のため LLM_HUB_ 接頭辞を使用
```

#### C. Gemini（Web リサーチ）

既存の `GEMINI_API_KEY` 環境変数が有効なら追加設定不要。

### Step 5. 業務プロジェクトに連携

業務リポ（AI-shelpha 等）の venv で:

```bash
cd ~/work/AI-shelpha
uv pip install --python .venv/bin/python -e ~/work/llm-hub

# Python から呼出
.venv/bin/python -c "
from llm_hub import route_task

# 機密データ → Qwen ローカル強制（明示なしでも保守的に confidential 扱い）
result = route_task(
    task_type='classification',
    sensitivity='confidential',
    prompt='以下のブランドを外資/国内で分類: Happy Dog, ロイヤルカナン, ニュートロ',
)
print(result['route'], '/', result['result'])
"
```

## 使い分け（既存 Ollama 経路と llm-hub）

| シーン | 推奨経路 | 理由 |
|-------|---------|------|
| Drive 共有フォルダの大量ファイル要約 | **既存 `qwen-eco`** (Ollama 7B/14B) | 軽量、エコモード hook と統合済 |
| Slack スレッドの分類・整形 | **既存 `qwen-eco`** | 軽量タスク向き |
| AMZ-POS / 5co. 予実 等の機密データ大量分類 | **llm-hub `llmhub-qwen-secure`** | 32B、機密度ガード、並列、audit 対応 |
| Python パッケージから直接呼出 | **llm-hub `route_task()`** | API として組込みやすい |
| 4 LLM の速度・品質横並び比較 | **llm-hub `llmhub-benchmark`** | Sonnet/Gemini/Codex/Qwen 統一実行 |
| ベンチマーク 1 回でコスト把握 | **llm-hub `llmhub-benchmark`** | usage_log + cost_calculator 連結 |
| X (Twitter) リアルタイム検索 | **既存 `x-search` + Grok** | llm-hub には Grok ルートなし |

## 関連スキル

- **既存（template 標準）**:
  - `.claude/skills/llm-router.md` — 軽量 bash ルーター
  - `.claude/skills/qwen-eco.md` — Ollama Qwen エコ処理
  - `.claude/skills/codex-review.md` — Codex レビュー
  - `.claude/skills/x-search.md` — Grok X 検索
  - `.claude/skills/drive-eco-access.md` — Drive エコ運用
- **llm-hub（このドキュメント）**:
  - `.claude/skills/llmhub-qwen-secure.md` — Qwen 32B 機密処理
  - `.claude/skills/llmhub-route.md` — Python ルーター（自動判定）
  - `.claude/skills/llmhub-health.md` — 4 LLM 疎通確認
  - `.claude/skills/llmhub-benchmark.md` — 4 LLM 横並び実呼出

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| `qwen_local: ok=false` | Qwen サーバー停止中 | `bash servers/start_qwen.sh` |
| `claude_sonnet: ok=false` | `LLM_HUB_ANTHROPIC_KEY` 未設定 | Step 4-B 参照 |
| `codex_cli: ok=false` | `codex login` 未実施 | Step 4-A 参照 |
| `gemini_cli: trusted directory` | `GEMINI_CLI_TRUST_WORKSPACE` 不在 | env で `=true` を設定（llm-hub の gemini.py は自動注入） |
| 並列処理タイムアウト | mlx_lm.server の prompt-concurrency が低い | `timeout=240` に伸ばす、batch_size を絞る |
| Qwen 回答が空 | thinking モードで max_tokens 不足 | `max_tokens=1500` 以上を推奨 |

## 関連ドキュメント

- `~/work/llm-hub/docs/cto-share-rutzbo-sandbox-integrated.md` — CTO 統合運用ガイド v3
- `~/work/llm-hub/docs/phase5-ssh-gateway-design.md` — Phase 5 SSH gateway 統合（CTO レビュー後着手）
- `~/work/llm-hub/CLAUDE.md` — llm-hub 内部運用ルール
- `~/work/llm-hub/configs/routing_rules.yaml` — ルーティング規則（4 段判定）

## 全社展開ロードマップ（2026-05 時点）

| Phase | 内容 | 状態 |
|-------|------|------|
| Phase 4 | Python パッケージ + 4 LLM 認証経路 + benchmark | ✅ 完了 |
| Phase 5 | SSH gateway 統合（shelpha と同パターン）、Tailnet 経由 | CTO レビュー待ち |
| Phase 6 | 社員 5〜10 人へ拡大、members マスタ運用 | 計画中 |
| Phase 7 | Mac Studio 移行、Qwen 70B 等の併設 | 計画中 |

## 開発・利用時の問い合わせ先

- リポ: `https://github.com/5co-hub/llm-hub`
- Slack: #llm-hub（要作成）
- Owner: 若松（@TakeshiWakamatsu）
