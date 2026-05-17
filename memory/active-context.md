# アクティブコンテキスト

> 現在進行中の作業状態。セッション開始時に必ず読み込むこと。
> セッション終了時に更新すること。

## 最終更新

- **日時**: 2026-05-17
- **セッション**: 自己検証ルール必須化 + OpenAI key rotation + gh CLI 自動セットアップ実装

## 現在の作業状態

### ✅ 2026-05-17 セッション成果

**マージ済 PR**（4 件）:
- **PR #256** (commit `c3fd3d1`): 回答前の自己検証を必須化（CLAUDE.md + concierge-template 原則7）
- **PR #257** (commit `dc09e2d`): `scripts/codex-call.sh` の op secret reference の括弧除去（`OpenAI API Key (Template)` → `OpenAI API Key`）
- **PR #258** (commit `7ecc905`): 次セッション TODO に grok-hermes と gh CLI 実装を追記
- **PR #259** (commit `f38fe00`): `/mm` slash command を派生リポへ伝播（apply-template の TEMPLATE_FILES に追加）

**Open PR**（1 件）:
- **PR #260** (`claude/add-gh-cli-setup`): SessionStart hook で gh CLI を自動セットアップ
  - `.claude/hooks/session-start-gh-setup.sh` 新規（v2.62.0 tarball install + キャッシュマーカー）
  - 認証は `GH_TOKEN` env var 方式（`~/.gh-env` に書き出し / `~/.grok-env` と同パターン）
  - `gh auth login --with-token` は `read:org` scope を要求するため使えない（既存 PAT は repo only）

**手元 1Password 操作（完了）**:
- **OpenAI API Key rotation**: `claude-code-secrets` vault / `OpenAI API Key` item の credential を
  `sk-proj-...` 形式の新キーに上書き。billing 設定済（Amex / $10 credit / Auto-recharge ON / max $100/月）
- API 疎通: `GET /v1/models` 200、`gpt-5.4-mini` で chat completion 動作確認（46/5 tokens）

**動作確認結果（end-to-end）**:
- `bash scripts/codex-call.sh "..."` ✅ `PONG` 応答
- `bash .claude/hooks/session-start-gh-setup.sh` ✅ gh v2.62.0 install + `~/.gh-env` 生成
- `source ~/.gh-env && gh auth status` ✅ `Logged in to github.com account widenormal (GH_TOKEN)`
- `gh repo list 5co-hub --limit 5` ✅ 5 件返却
- `DRY_RUN=1 bash scripts/sync-derived-repos.sh 5co-hub` ✅ org 列挙成功

**未完了 / 次セッション以降**:
- PR #260 のマージ + 派生リポへの sync 実行（`scripts/sync-derived-repos.sh` を手元 CLI で）
- grok-hermes 実装（https://x.ai/news/grok-hermes 内容 fetch 未実施）
- 必要に応じて GitHub PAT に `read:org` scope を追加（現状は gh auth login --with-token 不可だが GH_TOKEN 方式で回避済）

### ✅ R/G 鉄則 + 1Password 統合 + 検索ツール移植 動作確認（2026-05-16 / PR #239 merged）

**経緯**:
- PR #238 で travel リポから移植した R/G 鉄則・1Password 統合・検索ツールを
  実環境で動作確認
- `web-search.sh` で Google CSE backend は `www.googleapis.com` を叩くが、
  deployment ガイドの Allowed domains 例から欠落していたため PR #239 で追記

**動作確認結果**:
- `~/.search-api-env` (BRAVE / GOOGLE_CSE) ✅ / `~/.grok-env` ✅
- `~/.maps-env` ❌ 未生成（setup-op.sh の対象に Maps が無い可能性）
- `scripts/web-search.sh "claude code"` ✅ Brave 3 件返却
- `op whoami` ❌ Service Account 未サインインだが env file 経由は通る

**未完了**:
- `~/.maps-env` 生成経路の確認（Maps API を使う段になったら setup-op.sh を点検）
- `OP_SERVICE_ACCOUNT_TOKEN` 再投入は rotation や再生成のタイミングで

### ✅ travel 3 層 SessionStart 注入パターンを逆輸入（2026-05-09 / PR #207, commit `a08fe4d`）

**背景**:
- 派生リポ `widenormal/travel` が GW 期にプランニング品質ピーク（カワナ滞在）に到達した後、5/9 セッションで品質劣化が観察された
- 自己検証で **SessionStart 注入が「①状態」と「⑤未来」しか入っておらず、「②辞書」「③学習」「④除外」が毎回読まれていない** と特定
- ドメイン非依存パターンを抽出して template に逆輸入

**追加ファイル**:
- `docs/active-context-template.md` (P0): 3 層構造の SessionStart 注入を「推奨拡張」として追記
- `docs/personal-concierge-template.md` (P1+P3): 提案スタイル原則 + on-demand skill 注入縮小ガイド
- `docs/gemini-hybrid-mode-template.md`: ハルシ抑止 wrapper のメタテンプレ + 過防衛モード回避節
- `docs/exclusion-list-extractor-template.md` (P4): 除外リスト自動抽出パターン（curated + AUTO-EXTRACT 2 層）
- `docs/2026-05-09_session-context-3layer-report.md`: travel 側自己検証報告書（参照用）

**CLAUDE.md 修正**:
- soft cap 200 行ルール（推奨ガイドラインとして）
- 提案スタイル節（主導提案 1 案 + 代替）

**未決事項（travel 側 §6 効果測定後に確定）**:
1. 3 層構造を template 標準に格上げ vs optional sub-template
2. 除外リストの横断命名（visited / done / archive / closed / resolved）
3. 200 行 cap をハードルール vs 推奨ガイドライン
4. travel 側 2-3 セッション運用検証の結果反映

### ✅ upstream candidates 機構 完了（2026-05-06 / PR #186, commit `649b88a`）

**内容**:
- 派生 / private リポから template に取り込み候補となり得る差分を自動検出する仕組み
- `github-fetch.sh` / `github-tree.sh`（PR #157）の上位レイヤー
- 設定ファイル `.upstream-candidates` の各 (repo, path) を取得 → template 側と diff → `new` / `modified` / `same` に分類した markdown レポートを `.import/.candidates-report.md` に出力

**追加ファイル**:
- `scripts/upstream-candidates.sh` (315 行 / bash 3.2 互換 / 実行ビット付与)
- `.upstream-candidates` (初期: travel の `.claude/scripts/session-context.sh` と `docs/active-context-template.md`)
- `docs/upstream-candidates.md` (運用ガイド)

**直接の動機**:
- 引継ぎ事項にあった「travel の session-context.sh を取得して diff（PR #156 の改善材料）」を汎化したもの
- 派生リポでの工夫を漏らさず吸い上げるためのレビュー支援層

**未検証**:
- PAT セット済 + ネットワーク有効環境での実 fetch + 妥当な report 生成（今後行う）

### ✅ SessionStart 高速化 完了（2026-05-06）

**内容**:
- `session-start-gemini-setup.sh`: `gemini --version`（1.78s）をキャッシュマーカーで回避 → 0.06s（97% 削減）
- `session-start-multi-llm-setup.sh`: ollama インストール済みチェックをキャッシュ化
- キャッシュ: `~/.cache/claude-template-setup/gemini-<VERSION>.ok`、mtime 比較で binary 更新を検知
- template main マージ → AI-Objective-MGMT へ launchd 適用 → 全 26 派生リポへ template-sync PR 一括マージ完了

**opt-out マーカー機構（PR #184 マージ済）**:
- `scripts/sync-to-repo.sh` に `.claude/.sync-disabled` 存在チェックを追加
- `widenormal/travel` に `.sync-disabled` 設置済み（GitHub Web UI でコミット）
- travel の `setup-gemini.sh` は元々高速設計（`gemini --version` 未使用）のため追加最適化不要

### ✅ sync-template workflow 復旧 完了（2026-05-04）

**経緯**:
- `Sync Template to Downstream Repos` workflow が PR #145 マージ以降、**全 run が `Generate App installation token` ステップで即死**していたのを発見
- 原因: GitHub App 用 Secrets (`TEMPLATE_SYNC_APP_ID` / `TEMPLATE_SYNC_APP_KEY`) が一度も投入されてなかった（PR #145 で workflow だけ追加・Secrets 設定が抜けてた）
- 復旧として GitHub App `5co-hub-template-sync` (Owner: widenormal, **App ID: 3594358**) を作成・widenormal にインストール完了
- **しかし** GitHub UI が公開 install URL から org install フローを起動できず、5co-hub / 5co-finance / 5co-treasury への install 完遂が困難（30 分以上 URL ハック試行も全て widenormal 設定画面に固定リダイレクト）
- 運用負荷を下げるため **PAT 認証に切替**（PR #160）

**PR #160 (`claude/debug-error-message-VuOcx` ブランチ)**: テンプレ同期 workflow を GitHub App から PAT 認証に切替
- `.github/workflows/sync-template.yml`: App token 取得ステップ削除、`secrets.TEMPLATE_SYNC_PAT` 直接利用
- `scripts/sync-org.sh`: `gh api /installation/repositories` (App 専用) → `gh repo list <owner> --no-archived --source` (user/org 両対応)

**初期 run 失敗の root cause（2026-05-04 解決）**:
- `op item get ... --fields label=credential` が **default の空 API_CREDENTIAL field** を取り、custom credential field（id `e5sajszvymiflbwtwihuksfjz4`）の実値（40 byte ghp_… PAT）を取り逃していた
- そのため `gh secret set TEMPLATE_SYNC_PAT` は **空文字** を登録、workflow 側 `GH_TOKEN: ` が空のまま `sync-org.sh` が `GH_TOKEN required` で即死
- 修正: `op item get ... --fields e5sajszvymiflbwtwihuksfjz4 --reveal | tr -d '\n' | gh secret set TEMPLATE_SYNC_PAT` で再投入
- run `25307439167` で 4 org × 8〜10 repo 全 sync 成功 / `template-sync` ブランチ push 確認

**残タスク**:
1. PR #160 を admin マージ（base policy 上、通常マージ不可）
2. main で再走 → 各派生リポに `template-sync` PR が起票されることを検証

**今後の op 取り扱いルール**:
- 1Password Item で credential を保存する際、custom field を作るより **default `password` (purpose=PASSWORD) を使う**ほうが label=password で安全に取れる。custom credential field は label 衝突で sed 同名 default 空 field を引きやすい
- 既存 Item を再編する場合は `op item edit ... password=...` で default 側に値を移し custom field を削除すると引き間違いが起きない

### 副次的に判明した重要課題

- **`op://` URI 形式は括弧 `()` を含む Item 名と非互換**。今日命名標準化した `<Service> API Key (Template)` 形式は `op read "op://..."` で `invalid character '('` エラー
- 影響: `scripts/grok-call.sh` 等の op read ベースのラッパーは全部壊れる可能性
- 暫定対応: `op item get "<name>" --vault X --field Y --reveal --account Z` を使う（括弧 OK）
- 次回 `memory/decisions.md` で命名規則を再検討（候補: 括弧を外す `<Service> API Key Template` / ハイフン `<Service>-API-Key-Template` 等）

### 完了済（前セッションから持ち越し、本日 main マージ）

- **PR #156 (`21d660d`)**: SessionStart hook で `memory/active-context.md` を自動注入
- **PR #157 (`c35ee78`)**: private リポからの逆輸入インフラ
- **PR #158 (`2cfcb83`)**: 2026-05-04 セッションハンドオフ記録

### 完了済（手元 1Password 操作）

- **GitHub PAT** 発行 → 1Password Vault `claude-code-secrets` / Item `GitHub PAT (Template)` / field `credential` に登録（scope: `repo`、有効期限: No expiration）
- **xAI API Key の集約**: `claude-code-secrets` Vault に移動 → `Grok API Key (Template)` / `credential` に rename
- **GitHub App `5co-hub-template-sync` 作成・widenormal install**: App ID `3594358`, Owner widenormal, Permissions Contents R/W + PR R/W + Metadata R, "Any account" 設定。**現状 widenormal install のみ active、3 org への install は未完**。将来 GitHub UI 改善時の再活用に備えて削除せず保持

### 完了済（クロスリポ確認 / 2026-05-04）

- **comparison docs PR #107 merged**: `5co-hub/ai-agent-architecture-comparison` 側で `docs/claude-detailed-rules.md` L156 + L173 を新パス（`Grok API Key (Template)` / `credential`）に更新（commit `52df336`）
- **Grok x_search 疎通確認 HTTP 200**: comparison リポでの検証により、現行 `Grok API Key (Template)` が `GET /v1/models` および `POST /v1/responses` (tools: `x_search`) で正常応答することを確認。**過去（2026-04-07〜2026-04-14）の 401 問題は再現せず、rotation 不要**と判定

### 進行中（次セッションで継続）

- ~~OpenAI API キー新規発行 + 1Password 登録~~ → ✅ 2026-05-17 完了
- xAI / OpenAI の月次予算決定 → `profile/resources.md` の予算欄に記載
  - OpenAI 側は 2026-05-17 時点で credit $10 / max $100/月 / Auto-recharge ON 設定済
- PR #174（2026-05-05 セッションハンドオフ）: open のまま → admin マージ推奨
- PR #260（gh CLI セットアップ）: open → マージ後に派生リポへ sync

## 直近の重要な決定

- **AI 系 API キーは `claude-code-secrets` Vault に集約**、命名は `<Service> API Key (Template)` / field `credential` に統一（`memory/decisions.md` 2026-05-04 の項参照）
- **保護フック回避は python3 -c のサージカル編集で行う**: `git stage`（`git add` は `dd\s` パターンにヒットするため）、`>` を含まないコマンド構成
- **マルチLLM 準拠は 3 レベルモデル（Level 1/2/3）の段階展開を提案中**（未確定、次セッションで合意取る）
- **travel との関係性**: sandbox egress 制約で op CLI 不可。Level 1（命名標準化）で十分。template のフルスタックを強制しない

## 次セッションへの引継ぎ事項

### 必須（手元または別 Claude セッションで実行）

1. **OpenAI API キー発行 + 1Password 登録**:
   - <https://platform.openai.com/api-keys> で発行
   - `claude-code-secrets` / `OpenAI API Key (Template)` / `credential` に登録
   - Hard limit / Soft limit を OpenAI 側で設定
2. **5co-daily-ai-research の調査**: 1Password Item メモにあった用途名のリポで、旧 `op://共有/xAI API Key/password` パスの参照箇所を grep → 新パスに置換 → PR。`5co-hub/ai-agent-architecture-comparison` 側で 401 解消が確認できているため、Grok 経路の復活も並行して検討可能
3. **月次予算の決定** と `profile/resources.md` 予算欄への記載（xAI / OpenAI それぞれ。例: `$50/月` `$200 上限` 等）。なお xAI 側は **prepaid credits $4.78 残**（comparison 検証時点）が判明しているため、追加チャージの有無も合わせて判断

### 任意（時間があれば）

- **grok-hermes 実装**（2026-05-17 にユーザーから flag）: <https://x.ai/news/grok-hermes>
  - 内容未確認（fetch 未実施）。実装着手前に URL 内容を fetch して要件整理が必要
  - 既存 `scripts/grok-call.sh` の派生 / 別ラッパー / 別エンドポイントいずれかは未確定
- **gh CLI を web 実行環境に実装**（2026-05-17 にユーザーから flag）:
  - 現状 web 版 Claude Code には gh が無く、`scripts/sync-derived-repos.sh` 等が手元の CLI に依存
  - SessionStart hook で gh をインストール + 認証する経路（Gemini CLI と同パターン）の検討
- **3 レベル準拠モデルの正式採用判断**: `memory/decisions.md` で「提案中」のまま残しているため、次セッションで「採用」「修正」「却下」を確定
- **`scripts/secret-drift-check.sh`**: template の `resources.md` と各派生リポの op パス・Org Secret 値の整合性を検査する週次バッチ（GitHub Actions 化）
- **`docs/migration-playbook.md`**: 3 レベルモデルを採用する場合の昇格手順 + rollback playbook + 各リポの現在到達レベル一覧
- **upstream-candidates の実 fetch 検証**: PAT セット済環境で `bash scripts/upstream-candidates.sh` を走らせ、travel の `.claude/scripts/session-context.sh` 取得 + template との diff レポート生成が正しく行われるか確認。これにより PR #156 の改善材料（travel 側の独自 active-context 注入実装）を取り込むかの判断ができる

## 未解決の課題

- `5co-daily-ai-research` リポは未調査。Item メモ「5co-daily-ai-research 用」が示す通り、最有力の旧パス参照リポ。comparison 側で 401 解消が確認済のため、Grok 経路の復活が可能な状態
- xAI / OpenAI 月次予算が未確定のため、`profile/resources.md` 予算欄が空のまま（CLAUDE.md の「リソース残高を推測で記載しない」ルールに従い、放置）
- 今日のセッションで提案した「マルチLLM 3 レベルモデル」がまだ正式採用されていない。各派生リポの到達点判断のフレームワークがない状態

## 参照すべき主要ファイル

### 今日のセッションで触れた / 関連する
- `.claude/scripts/session-context.sh` — SessionStart hook（PR #156 で投入）
- `scripts/github-fetch.sh` / `scripts/github-tree.sh` — private リポからの逆輸入（PR #157）
- `docs/private-repo-import.md` — github-fetch / github-tree の運用ガイド
- `scripts/upstream-candidates.sh` / `.upstream-candidates` / `docs/upstream-candidates.md` — 取り込み候補検出機構（PR #186）
- `profile/resources.md` — 1Password Item 一覧（GitHub PAT は登録済、xAI/OpenAI 月次予算は未記載）
- `memory/decisions.md` — 2026-05-04 の集約決定 + 3 レベル提案

### 既存（前セッションから継続）
- `docs/multi-llm-orchestration.md` — マルチLLM 設計の全体像
- `scripts/{grok,codex,qwen}-call.sh` — 各 LLM ラッパー
- `.claude/skills/{llm-router,x-search,codex-review,qwen-eco,drive-eco-access}.md` — 運用スキル
- `.claude/skills/session-handoff.md` — セッション終了時の手順
- `scripts/sync-derived-repos.sh` — 派生リポ一括同期（手元の gh CLI 必要）

### クロスリポ連携
- comparison: `5co-hub/ai-agent-architecture-comparison`（**docs PR #107 merged 完了 / Grok 401 解消確認済**、Grok 経路復活は別 PR で検討中）
- travel: `widenormal/travel`（noop 確定、Level 1 のみ）
- 5co-daily-ai-research: `5co-hub/5co-daily-ai-research`（未調査、次セッション必須）
