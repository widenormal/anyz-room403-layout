# 詳細ルール

> CLAUDE.md から分離した詳細設計ルール。必要時のみ参照される（Layer 3 扱い）。

## ディレクトリ構成

テンプレ管理対象ディレクトリ（`scripts/apply-template.sh` の `TEMPLATE_DIRS` で派生リポへ伝搬）:

- `19期計画/` — 全社の期次計画
- `個人OKR/` — メンバー別の個人 OKR
- `人事_Grade・職種別行動目標/` — Grade / 職種別の行動目標リファレンス

これらは現状 `.gitkeep` のみのスケルトンで、template 側にファイルが追加されると `--repair` で派生リポへ上書き同期される。

## 設計原則

1. **Single Source of Truth**: `projects/*/plan.md` のみが確定プラン。旧候補は削除する
2. **ポインタ型 CLAUDE.md**: 詳細は外部ファイルに分離し、CLAUDE.md は 3KB 以内を目標にする
3. **即時反映**: 変更を伝えられたら該当ファイルを即座に更新する
4. **振り返り必須**: 案件終了後は retrospective.md を作成し、知見を insights.md に蓄積する

## プロジェクトライフサイクル



## 技術スタック

<!-- プロジェクト固有の技術スタックをここに記載 -->

## セキュリティ

- APIキー・パスワードは memory/ や sessions/ に含めない
- `.env` ファイルは .gitignore に追加する
- 機密情報は 1Password 等のシークレット管理ツールで管理する

## スキル運用

### 既存スキル一覧

| スキル | 目的 | 起動タイミング |
|---|---|---|
| `skill-creator/SKILL.md` | スキルの新規作成・改善（Meta Skill） | 新規・改善・定期レビュー時 |
| `session-handoff.md` | セッション終了時のコンテキスト永続化 | セッション終了時必須 |
| `create-brand.md` | 新規ブランドディレクトリの作成（構造・CLAUDE.md・フック一式） | 「新規ブランド作成」「ブランド追加」 |
| `api-connector.md` | 鍵とレシピ一体の API コネクタ運用（op ＋ `.claude/connectors/*.json`） | 外部 API 呼出・401/400 詰まり時 |
| `llm-router.md` | マルチLLMオーケストレーションの司令塔 | LLM 振り分け迷い時 |
| `x-search.md` | Grok 経由の X(Twitter) リアルタイム検索 | X/Twitter 関連調査 |
| `codex-review.md` | Codex (GPT-5) でのセカンドオピニオン | 戦略判断・レビュー |
| `qwen-eco.md` | ローカル Qwen（Ollama）での軽処理 | 要約・分類・整形 |
| `drive-eco-access.md` | Google Drive 共有フォルダのエコ運用 | Drive MCP ツール使用時 |
| `llmhub-route.md` / `llmhub-qwen-secure.md` / `llmhub-health.md` / `llmhub-benchmark.md` | 5co-hub/llm-hub（MLX/Python）経由の機密対応ルーティング・疎通・比較 | llm-hub リポでの作業時 |
| `ci-weekly-deck.md`（＋`ci-weekly-deck/` キット） | 顧客週次定例デッキを CI v2 で決定論生成 | 「週次定例デッキ」「CI v2 で定例資料」 |
| `framework-recommend/SKILL.md` | スライドの型・フレームワーク図の提案（99種＋発見枠） | CI制作の本文スライド設計時 |
| `md-html-pptx-flow/SKILL.md` | MD→HTML→PPTX の3段階スライド制作フロー | 「スライド作って」「PPTX で出力」 |
| `review-loop/SKILL.md` | 5エージェント・ループレビュー | 「ループレビューして」／md-html-pptx-flow Phase 3 |
| `slide-deck-builder/SKILL.md` | SLIDE-DECK.md（設計書）生成（汎用デッキ用・任意経路） | 「プレゼンの設計書を作って」 |
| `slide-md-creator/SKILL.md` | デザインシステム SLIDE.md の新規生成（新規ブランド用） | 「SLIDE.md を生成して」 |
| `slide-pattern-creator/SKILL.md` | レイアウトパターン SLIDE-PATTERN の抽出・生成 | 「スライドパターンを抽出して」 |
| `memory-dream.md` | 記憶階層の consolidation（重複・矛盾・陳腐化の除去） | 「記憶の整理」「dream」指示時／20〜30セッション蓄積時／大規模リファクタ直後 |
| （プロジェクト固有スキルをここに追記） | | |

### マルチLLMオーケストレーション

Claude Code を司令塔として外部 LLM を呼び分ける構成。Drive 共有フォルダなど多人数利用領域では、
`.claude/hooks/eco-mode-drive.sh` が PreToolUse で発火し、自動でエコ運用に誘導する。
詳細設計: `docs/multi-llm-orchestration.md`

### スキル追加時のルール

1. `.claude/skills/skill-creator/SKILL.md` を起動し Phase 1 Step 1-1 の必要性チェックを通す
2. 配置は `.claude/skills/*.md` 直下（サブディレクトリ不要の場合）
3. 言語は日本語、最初の3行に「> 1行説明」「目的」「起動条件」を配置
4. 追加後に当表（「既存スキル一覧」）と `CLAUDE.md` Layer 3 ツリーの両方を更新（CLAUDE.md が保護対象の場合はユーザーに依頼）
