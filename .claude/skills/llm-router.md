# Skill: LLM ルーター（マルチLLMオーケストレーションの司令塔）

> Claude Code から外部 LLM を呼ぶ際、用途に応じた最適な呼び先を選ぶ。
> **既定はエコ運用**: 軽い処理はローカル Qwen、重い判断のみ有料 LLM へ。

## トリガー

- ユーザーが「Grok で…」「Codex に聞いて」「Qwen で要約」など特定の LLM を指名したとき
- Drive 共有フォルダ操作後の二次処理（要約・分類）が必要なとき
- 何の LLM が適切か迷ったとき

## 役割分担表

| 呼び先 | 用途 | コスト目安 | 使用ラッパー |
|------|------|----------|------------|
| **qwen** | 要約・分類・フォーマット変換・プロンプトドラフト | $0（ローカル） | `scripts/qwen-call.sh` |
| **haiku** | qwen で精度不足な軽処理 | 低（Claude Haiku 4.5） | Claude Code 内で `model: haiku` 指定 |
| **grok** | X(Twitter) リアルタイム検索・トレンド | $0.20/Mtoken | `scripts/grok-call.sh` |
| **codex** | 戦略判断・コードレビュー・リスクチェック | 中（GPT-5 系） | `scripts/codex-call.sh` |
| **gemini** | 別バイアスのレビュー・画像/マルチモーダル | 中 | `scripts/gemini-call.sh` |
| **claude** | オーケストレーション・複雑実装 | 高（既定） | デフォルト |

## 判断フロー

```
1. ECO_MODE=1 または DRIVE_CONTEXT=1 ?
   └─ Yes → qwen（軽処理）または haiku（中規模）
2. 用途が明示？
   - x-search/twitter/trend     → grok
   - review/judge/strategy      → codex
   - second-opinion/multimodal  → gemini
   - drive-summary/classify     → qwen
3. キーワード検出
   - 「X で」「Twitter」「バズ」「トレンド」 → grok
   - 「レビュー」「セカンドオピニオン」      → codex
   - 「画像」「デザイン」「マルチモーダル」  → gemini
   - 「要約」「分類」「整形」「ドラフト」     → qwen
4. デフォルト → claude
```

## 使い方（コマンド）

```bash
# どこに振るかだけ判定
bash scripts/llm-router.sh --task "X で claude-code がバズってる投稿"
# → grok\tX/Twitter キーワード検出

# 直接呼ぶ
bash scripts/grok-call.sh "AI 業界で昨晩バズった投稿"
bash scripts/codex-call.sh "この PR の設計をレビュー" < diff.txt
bash scripts/qwen-call.sh --task summarize < long_doc.txt
bash scripts/gemini-call.sh -p "別視点でこの設計を批判して"
```

## エコモードの強制

Drive 共有フォルダ操作時は `.claude/hooks/eco-mode-drive.sh` が PreToolUse で発火し、
ECO_MODE=1 相当の運用に切り替えるよう Claude に通知する。
- ファイル本文の処理は **必ず qwen で先に要約** してから Claude に渡すこと
- 1 セッションで 10 ファイル以上の中身を Claude のコンテキストに展開しない

## 関連スキル

- `x-search.md` — Grok でリアルタイム X 検索
- `codex-review.md` — Codex に戦略・コードレビュー依頼
- `qwen-eco.md` — Qwen での軽処理パターン集
- `drive-eco-access.md` — Drive 共有フォルダのエコ操作手順

## 関連ファイル

- `scripts/llm-router.sh` — 判定ロジック本体
- `docs/multi-llm-orchestration.md` — 設計の全体像
- `.claude/hooks/eco-mode-drive.sh` — Drive MCP の発火点
