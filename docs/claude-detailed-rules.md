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

## 運用の定型フロー（全派生リポ共通・2026-07-16 制定）

### CLAUDE.md（保護ファイル）を変更したいとき

保護フックのブロックは**正常動作**（事故防止が目的）。迂回せず、次の標準フローで：

1. 変更案の全文を PR 本文（または decisions.md）に明記し、そこで作業を止める
   ＝ブロックされた時の正しい振る舞い。**回避手段を探さない・自動化しない**
2. 反映は管理者の判断に委ねる（管理者が手動で反映するか、そのセッション内で個別に指示する。
   包括的な事前承認は存在しない＝毎回明示の承認が必要）
3. フックが無関係な操作まで妨げる（誤検知と思われる）場合も、その場で回避せず
   正本 `5co-hub/template` に issue を立てる。フックの修正は正本側の管理者承認 PR で行う

### 新規外部サービス（MCP・API）を導入するとき

「未確認」で止まらないための前提チェックリスト。導入 PR に以下を含める：

1. **契約状況**: 必要プラン（無料/有料の別）と現在の契約を確認し、`profile/resources.md` に
   プラン・更新日を記載（推測で書かない。不明なら「未確認・要管理者確認」と明記）
2. **認証方式と場所**: OAuth はリモートセッションで完了できない＝各メンバーの初回認証は
   ローカル対話セッション（/mcp → Authenticate）。API key 方式なら 1Password
   `claude-code-secrets` へ登録し op 経由で解決（R3: 登録前に既存 key の棚卸し）
3. **導入後**: 疎通を実測してから完了報告（自己検証ルール2）。決定と根拠は decisions.md へ

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
| `framework-recommend/SKILL.md` | スライドの型・フレームワーク図の提案（129種＋発見枠） | CI制作の本文スライド設計時 |
| `md-html-pptx-flow/SKILL.md` | MD→HTML→PPTX の3段階スライド制作フロー | 「スライド作って」「PPTX で出力」 |
| `review-loop/SKILL.md` | 5エージェント・ループレビュー | 「ループレビューして」／md-html-pptx-flow Phase 3 |
| `slide-deck-builder/SKILL.md` | SLIDE-DECK.md（設計書）生成（汎用デッキ用・任意経路） | 「プレゼンの設計書を作って」 |
| `slide-md-creator/SKILL.md` | デザインシステム SLIDE.md の新規生成（新規ブランド用） | 「SLIDE.md を生成して」 |
| `slide-pattern-creator/SKILL.md` | レイアウトパターン SLIDE-PATTERN の抽出・生成 | 「スライドパターンを抽出して」 |
| `5co-ci-slide.md` | 単発CIスライドを正典最新版（ci_head.py経由・2ゲート）で生成 | 「CIスライドを作成」等の単発スライド指示 |
| `op-diagnose.md` | op CLI エラーの R7 三段階診断（whoami→vault→item） | op 認証・secret 参照エラー時 |
| `memory-dream.md` | 記憶階層の consolidation（重複・矛盾・陳腐化の除去） | 「記憶の整理」「dream」指示時／20〜30セッション蓄積時／大規模リファクタ直後 |
| （プロジェクト固有スキルをここに追記） | | |

### マルチLLMオーケストレーション

Claude Code を司令塔として外部 LLM を呼び分ける構成。Drive 共有フォルダなど多人数利用領域では、
`.claude/hooks/eco-mode-drive.sh` が PreToolUse で発火し、自動でエコ運用に誘導する。
詳細設計: `docs/multi-llm-orchestration.md`

### スキル追加時のルール

1. `.claude/skills/skill-creator/SKILL.md` を起動し Phase 1 Step 1-1 の必要性チェックを通す
2. **形式は2種**（どちらかに従う・混在させない）:
   - **ファイル型**（手順のみの単純スキル）: `.claude/skills/<name>.md` 直下。言語は日本語、
     最初の3行に「> 1行説明」「目的」「起動条件」を配置
   - **ディレクトリ型**（スクリプト・アセット同梱の複合スキル）: `.claude/skills/<name>/SKILL.md`。
     YAML frontmatter（`name` / `description`＝発火条件を含む英語可）を必須とし、
     本文は日本語推奨。同梱物は同ディレクトリに置く
3. 追加後に当表（「既存スキル一覧」）と `CLAUDE.md` Layer 3 ツリーの両方を更新（CLAUDE.md が保護対象の場合はユーザーに依頼）
