---
name: llmhub-benchmark
description: 5co-hub/llm-hub 経由で同一プロンプトを Qwen MLX / Gemini / Codex / Claude Sonnet の 4 LLM に投げ、速度・品質・コスト・機密データ取扱可否を横並び比較。引数はプロンプト文字列。結果は logs/benchmark_<ts>.json に保存。Anthropic 課金が発生する点に注意。
---

# /llmhub-benchmark — llm-hub 4 LLM 横並び比較

## 実行内容

`scripts/benchmark.py` を venv の python で実行。

```bash
.venv/bin/python scripts/benchmark.py "$PROMPT"
```

## 評価軸

| 軸 | 内容 |
|----|------|
| 速度 | latency, tokens/sec |
| 品質 | 既知答えとの一致率（複数質問時）/ Claude による review |
| コスト | ¥/1Mトークン換算（Qwen=0、Gemini=実費、Claude/Codex=API実費） |
| 機密データ取扱可否 | local / external（**最重要**） |

## 注意

- ベンチマークプロンプトには **機密データを含めない**（Claude/Gemini/Codex に流れる）
- 結果 `logs/benchmark_<ts>.json` は `chmod 600` を維持（プロンプト全文が残る）
- 月次コスト上限（`configs/routing_rules.yaml` の `monthly_jpy`）を超えていないことを事前確認

## 出力例

```json
{
  "prompt": "...",
  "results": {
    "qwen_local":    {"latency_ms": 1240, "tokens_per_sec": 42, "cost_jpy": 0,    "external": false, "answer": "..."},
    "gemini":        {"latency_ms": 2100, "tokens_per_sec": 80, "cost_jpy": 0.5,  "external": true,  "answer": "..."},
    "codex":         {"latency_ms": 1850, "tokens_per_sec": 70, "cost_jpy": 1.2,  "external": true,  "answer": "..."},
    "claude_sonnet": {"latency_ms": 1620, "tokens_per_sec": 65, "cost_jpy": 2.4,  "external": true,  "answer": "..."}
  }
}
```
