---
name: llmhub-health
description: 5co-hub/llm-hub 配下の全 LLM (Qwen MLX サーバー / Gemini CLI / Codex CLI / Anthropic API) の疎通を確認し JSON で返す。引数なし。サーバー起動状態の把握、障害切り分け、benchmark 前の事前確認に使用。
---

# /llmhub-health — llm-hub 全 LLM 疎通確認

## 実行内容

`scripts/health_check.py` を venv の python で実行し、結果 JSON を `logs/health_<ts>.json` に保存しつつ画面に表示。

```bash
.venv/bin/python scripts/health_check.py
```

## チェック項目

| LLM | 確認内容 |
|-----|----------|
| Qwen ローカル | `GET http://127.0.0.1:8001/v1/models` (2 秒タイムアウト) |
| Gemini CLI | `gemini --version` の戻り値 |
| Codex CLI | `codex --version` + `OPENAI_API_KEY` 環境変数 |
| Anthropic API | `ANTHROPIC_API_KEY` 環境変数のみ確認（API 呼出は課金回避のため省略） |

## 出力例

```json
{
  "timestamp": "2026-05-07T17:30:00+09:00",
  "results": {
    "qwen_local": {"ok": true, "latency_ms": 12, "model_id": "..."},
    "gemini_cli": {"ok": true, "version": "0.40.0"},
    "codex_cli":  {"ok": false, "reason": "OPENAI_API_KEY not set"},
    "anthropic_api": {"ok": true, "via": "env"}
  }
}
```

## 失敗時の対処

- Qwen ダウン → `bash servers/start_qwen.sh` を案内
- Codex 未認証 → `~/.zshrc` に 1Password 連携の追記を案内
- Anthropic 失敗 → 一時的に claude_haiku → claude_sonnet にフォールバック
