---
name: llmhub-qwen-secure
description: llm-hub (5co-hub/llm-hub リポ、MLX ベース) のローカル Qwen 3-32B-4bit サーバーに即座にプロンプトを投げる。機密データ前処理・分類・名寄せ・大規模並列バッチに最適。引数はプロンプト文字列。
---

# /llmhub-qwen-secure — llm-hub Qwen (MLX/32B) 即実行

## 既存スキルとの違い

- **`qwen-eco.md`** (既存): Ollama 上の Qwen 7B/14B、軽量エコ運用、bash ラッパー (`scripts/qwen-call.sh`)
- **このスキル**: 5co-hub/llm-hub の Qwen3-32B-4bit (MLX)、機密処理・大規模・Python 経由
- 使い分け: **Drive 共有フォルダのエコ要約 → `qwen-eco`** / **AMZ-POS など機密 + 大規模 → `llmhub-qwen-secure`**

# /llm-qwen — Qwen 即実行

## 用途

- 機密データを **絶対に外部 LLM に渡したくない** とき
- 大量データの分類・名寄せ・要約・整形を高速並列で
- thinking モードでの推論

## 実行手順

ユーザーが `/llm-qwen <prompt>` を呼んだら:

1. **疎通確認**: `bash servers/status.sh` を実行し、Qwen サーバーが応答するか確認。
   - 応答なし → ユーザーに `bash servers/start_qwen.sh` の実行を案内し停止
2. **クエリ実行**: 以下を Bash で実行（venv の python を使用）:
   ```bash
   .venv/bin/python -c "
   from llm_hub.clients.qwen import qwen_query
   import sys
   ans = qwen_query(sys.argv[1], max_tokens=1500, temperature=0.2)
   print(ans)
   " "$ARGS"
   ```
3. **応答整形**: 改行を保ちつつ、長すぎる場合は最初の 80 行で切る。

## 機密性ガード

- このスキルは **常に Qwen ローカル経由**。外部 API には絶対に流さない
- ログ（`logs/usage_*.jsonl`）に prompt 全文を残さず、先頭 100 文字 + ハッシュのみ記録

## 失敗時のフォールバック

- 機密データ判定の場合: フォールバックなし（要件「機密はフォールバック禁止」）
- 公開データかつサーバーダウン: ユーザー確認の上、`route_task` 経由で claude_haiku に切替
