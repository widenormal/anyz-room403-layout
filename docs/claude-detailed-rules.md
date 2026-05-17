# 詳細ルール

> CLAUDE.md から分離した詳細設計ルール。必要時のみ参照される（Layer 3 扱い）。

## ディレクトリ構成



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
| `skill-creator.md` | スキルの新規作成・改善（Meta Skill） | 新規・改善・定期レビュー時 |
| `session-handoff.md` | セッション終了時のコンテキスト永続化 | セッション終了時必須 |
| `create-brand.md` | ブランド画像生成 | 画像生成時 |
| `llm-router.md` | マルチLLMオーケストレーションの司令塔 | LLM 振り分け迷い時 |
| `x-search.md` | Grok 経由の X(Twitter) リアルタイム検索 | X/Twitter 関連調査 |
| `codex-review.md` | Codex (GPT-5) でのセカンドオピニオン | 戦略判断・レビュー |
| `qwen-eco.md` | ローカル Qwen での軽処理 | 要約・分類・整形 |
| `drive-eco-access.md` | Google Drive 共有フォルダのエコ運用 | Drive MCP ツール使用時 |
| （プロジェクト固有スキルをここに追記） | | |

### マルチLLMオーケストレーション

Claude Code を司令塔として外部 LLM を呼び分ける構成。Drive 共有フォルダなど多人数利用領域では、
`.claude/hooks/eco-mode-drive.sh` が PreToolUse で発火し、自動でエコ運用に誘導する。
詳細設計: `docs/multi-llm-orchestration.md`

### スキル追加時のルール

1. `.claude/skills/skill-creator.md` を起動し Phase 1 Step 1-1 の必要性チェックを通す
2. 配置は `.claude/skills/*.md` 直下（サブディレクトリ不要の場合）
3. 言語は日本語、最初の3行に「> 1行説明」「目的」「起動条件」を配置
4. 追加後に当表（「既存スキル一覧」）と `CLAUDE.md` Layer 3 ツリーの両方を更新（CLAUDE.md が保護対象の場合はユーザーに依頼）
