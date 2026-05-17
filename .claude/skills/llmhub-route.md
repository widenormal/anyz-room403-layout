---
name: llmhub-route
description: llm-hub (5co-hub/llm-hub) の Python ルーターを呼び、タスク種別 × 機密度で最適 LLM (Qwen/Gemini/Codex/Claude) に自動ルーティング。configs/routing_rules.yaml + フォールバック + コスト降格を自動実行。引数は `<task_type>:<sensitivity>:<prompt>` 形式。
---

# /llmhub-route — llm-hub 自動ルーティング (Python)

## 既存スキルとの違い

- **`llm-router.md`** (既存): bash ラッパー、Ollama Qwen + Grok + Codex + Gemini + Haiku のシンプル振り分け、Drive エコ運用と一体化
- **このスキル**: 5co-hub/llm-hub の `route_task()` Python 関数経由、機密度ガード + フォールバック chain + 月次予算降格 + audit ログ
- 使い分け: **手元の単発判断 → `llm-router`** / **業務コードからの API 呼出・大量バッチ → `llmhub-route`**

# /llm-route — 自動ルーティング

## 入力形式

```
/llm-route <task_type>:<sensitivity>:<prompt>
```

- `task_type`: web_research / code_generation / classification / name_normalization / format_conversion / summarization / orchestration / other
- `sensitivity`: confidential / internal / public
- `prompt`: 自然文（コロンを含む場合は引用）

## 実行手順

1. 入力を 3 分割（最初の 2 つの `:` で）
2. 以下を Bash で実行:
   ```bash
   .venv/bin/python -c "
   from llm_hub import route_task
   import json, sys
   r = route_task(task_type=sys.argv[1], sensitivity=sys.argv[2], prompt=sys.argv[3])
   print(json.dumps(r, ensure_ascii=False, indent=2))
   " "$TASK_TYPE" "$SENSITIVITY" "$PROMPT"
   ```
3. 結果を `route` / `attempts` / `result` で整形して表示

## 第0判定での Claude Code 自身処理

`result == None` で `route == "claude_code"` の場合は **オーケストレーター（このセッション）が直接回答**する。
別の LLM を呼ばず、自分で考えて返す（サブスク内で完結）。

## 機密度の判断ガイド

- `confidential`: AMZ-POS、5co. 予実、契約 TakeRate、顧客個別データ → **必ず Qwen**
- `internal`: 社内資料・OKR → 原則 Claude（Anthropic は内部処理用途のため許容）
- `public`: Web 検索可能な情報 → Gemini 優先

## 失敗時の挙動

- フォールバック上限到達 → エラーメッセージと `attempts` を表示し停止
- 機密データはフォールバック先がないので即時失敗（仕様）
