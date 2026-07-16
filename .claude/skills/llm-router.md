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
| **xmcp / x-search** | X(Twitter) の一次データ取得（検索・トレンド・記事全文）＝**X 系の第一選択** | X API プラン枠（xAI クレジット不要） | XMCP（MCP ツール）／ `scripts/x-search.sh` |
| **grok** | X データの要約・解釈・意味検索（一次取得は xmcp/x-search で） | $0.20/Mtoken（xAI 直不可時は OpenRouter 自動フォールバック） | `scripts/grok-call.sh` |
| **codex** | 戦略判断・コードレビュー・デバッグ委譲・完成時検品 | 中（モデルは `scripts/llm-models.conf` 参照） | `scripts/codex-call.sh`（重い判断は `--frontier`） |
| **brave** | リンク・所在の特定（Web検索の第一選択） | 低（無料枠 月2,000クエリ） | `scripts/brave-search.sh` |
| **openrouter** | 出典付き調査・要約（Web調査の第一選択） | 低（プリペイド） | `scripts/openrouter-call.sh --online` |
| **gemini** | 別バイアスのレビュー・画像/マルチモーダル・**Google grounding が必要な調査のみ** | 中 | `scripts/gemini-call.sh` |
| **claude** | オーケストレーション・複雑実装 | 高（既定） | デフォルト |

## 判断フロー

```
1. ECO_MODE=1 または DRIVE_CONTEXT=1 ?
   └─ Yes → qwen（軽処理）または haiku（中規模）
2. 用途が明示？
   - x-search/twitter/trend     → xmcp / x-search.sh（データ取得）→ grok（解釈が要る時のみ）
   - review/judge/strategy      → codex
   - link-search/URL特定        → brave
   - web-research/出典付き調査  → openrouter（--online）
   - google-grounding 必須の調査 → gemini
   - second-opinion/multimodal  → gemini
   - drive-summary/classify     → qwen
3. キーワード検出
   - 「X で」「Twitter」「バズ」「トレンド」 → xmcp / x-search.sh（解釈のみ grok）
   - 「レビュー」「セカンドオピニオン」      → codex
   - 「リンク探して」「URL」「どこにある」   → brave
   - 「調べて（出典付き）」「リサーチ」       → openrouter
   - 「画像」「デザイン」「マルチモーダル」  → gemini
   - 「要約」「分類」「整形」「ドラフト」     → qwen
4. デフォルト → claude
```

## Web調査の第一選択（本スキルが正・旧 CLAUDE.md「Web調査ツール」節を引き取り）

| 用途 | ツール | 理由 |
|------|--------|------|
| リンク・所在の特定（生検索） | `scripts/brave-search.sh` | 最速・最安（無料枠 月2,000クエリ）。vault に key 有 |
| 出典付きリサーチ（要約・調査） | `scripts/openrouter-call.sh --online` | key 1本・プリペイドで課金一元化（残高切れ＝自動停止が安全網）。Web検索は Exa ベース |
| Google 検索の鮮度・網羅が要る調査 | `scripts/gemini-call.sh` | Google 検索グラウンディング。従量課金なので必要時のみ |
| X(Twitter) の調査 | XMCP / `scripts/x-search.sh` | 構造化 API（`x-search.md` スキル参照） |
| 既知 URL の内容取得・要約 | `WebFetch` | 単一ページの読み取りに十分 |
| 上記が未セットアップ・key 無し | `WebSearch` / `WebFetch` | フォールバック |

```bash
bash scripts/brave-search.sh "調べたいクエリ" -n 10
bash scripts/openrouter-call.sh -p "調べたいクエリ" --online
bash scripts/gemini-call.sh -p "調べたいクエリ"   # Google grounding が必要な時のみ
```

- key はすべて env または 1Password（`OP_SERVICE_ACCOUNT_TOKEN` 経由）で自動解決。
  セットアップ手順は `README.md`、SessionStart フックが `gemini`/`op` CLI を自動導入
- Gemini のコスト最適化（キャッシュ・モデル切替・予算ガード・プロンプトのバッチ化）は
  `docs/gemini-hybrid-mode-template.md` を正とする（`gemini-checked.sh` の使い分け表含む）
- OpenRouter / Gemini とも**オートチャージ OFF のプリペイド**運用（残高枯渇＝自動停止が安全網）

## 使い方（コマンド）

```bash
# どこに振るかだけ判定
bash scripts/llm-router.sh --task "X で claude-code がバズってる投稿"
# → grok\tX/Twitter キーワード検出

# 直接呼ぶ
bash scripts/x-search.sh "claude code lang:ja" -n 10      # X 一次データ（第一選択）
bash scripts/grok-call.sh "この検索結果の傾向を要約" < results.txt
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

- `x-search.md` — X 検索・取得（XMCP / x-search.sh 第一選択・Grok は解釈）
- `codex-review.md` — Codex に戦略・コードレビュー依頼
- `qwen-eco.md` — Qwen での軽処理パターン集
- `drive-eco-access.md` — Drive 共有フォルダのエコ操作手順

## 関連ファイル

- `scripts/llm-router.sh` — 判定ロジック本体
- `docs/multi-llm-orchestration.md` — 設計の全体像
- `.claude/hooks/eco-mode-drive.sh` — Drive MCP の発火点
