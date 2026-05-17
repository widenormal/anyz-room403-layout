# CLAUDE.md — {{プロジェクト名}}

{{プロジェクトの1行説明を記入}}

## セッション開始時（必須）

1. `memory/active-context.md` を読む — 前回の作業状態
2. `profile/preferences.md` を読む — 好み・要件
3. `profile/resources.md` を読む — リソース（**更新日から30日以上経過時は警告**）
4. `learnings/insights.md` を読む — 累積知見

## セッション終了時（必須）

`.claude/skills/session-handoff.md` の手順に従い、コンテキストを永続化する。

## スキル運用

- **新規作成・改善時**: `.claude/skills/skill-creator.md`（メタスキル）を起動
- **3フェーズ**: Blueprinting → Testing → Improvement
- **詳細ルール・既存スキル一覧**: `docs/claude-detailed-rules.md` の「スキル運用」セクション参照

## コアルール

- **言語**: 日本語
- **正の情報源**: `projects/*/plan.md` が各案件の唯一の確定プラン
- **即時反映**: 変更を伝えられたら該当ファイルを即座に更新
- 提案には「なぜそれを選んだか」の根拠を必ず添える
- 重要な意思決定は `memory/decisions.md` に記録する

## 禁止事項

- リソース残高を推測で記載しない（`resources.md` 参照）
- 好みの確認なしに1択で断定しない
- 案件終了後の振り返り記録をスキップしない
- 不採用プラン・旧候補をファイルに残置しない

## 回答前の自己検証（必須）

**すべての回答**（提案・実装・「完了しました」報告・雑談的回答を含む）を出す前に、
必ず次の 4 点をセルフチェックする。一つでも引っかかれば、回答前に確認 tool を
実行して埋めるか、未確認である旨を明示する。

1. **事実確認**: 「たぶん」「はず」で書こうとしていないか。ファイル状態・コマンド
   出力・実環境を **実際の tool 実行で確認** したか（会話履歴・記憶からの推論は不可）
2. **完了報告は実証ベース**: 「完了しました」「動きました」「修正しました」と書く前に、
   tests / lint / 動作確認が **実際に通った** ことを tool 出力で確認したか
   （Edit/Write 成功 ≠ 動作確認、コンパイル成功 ≠ 機能確認）
3. **既存資産の確認**: 新規実装・新規 API 統合の提案前に、`memory/active-context.md` /
   `profile/resources.md` / `learnings/insights.md` に該当情報がないか参照したか
   （R3 の 1Password 既存 key 棚卸し含む）
4. **不確実性の明示**: 確認できなかった部分は「未確認」「推測」「要再確認」と
   明示し、断定しない

詳細・アンチパターン・派生リポでの展開方法は `docs/personal-concierge-template.md`
の原則7 参照。

## 失敗しないための鉄則（過去事例からの蒸留）

travel リポの learnings/insights.md「楽天 Web Service API を 3 月以降ずっと見逃して
いた件の自己検証」（2026-05-16）から抽出した、毎セッションで守るメタルール。

- **R1: Sandbox 制約は調査対象**。egress block / 403 を見たら諦めず、**「ホスト名は
  正しいか」「別エンドポイントで API 提供されてないか」「Custom allowlist で拡張
  可能か」の3点を必ず検証する**。
  例：travel — `gora.golf.rakuten.co.jp` がブロックでも `openapi.rakuten.co.jp` は別ホストで通る／
  例：treasury — クレカ会員サイトが scrape 不可でも Plaid / Personal Finance API 経由なら可
- **R2: 公式 API 探索プリミティブ**。新規ドメインの調査時、必ず「`<service> API`」を
  1回検索する。HTML scrape より構造化 API を優先。
  例：travel — 「楽天GORA URL」で詰まったら「楽天 Web Service API」を検索／
  例：treasury — 「クレカ明細 自動取得」で詰まったら「Plaid」「Mastercard Open Banking」を検索
- **R3: ユーザーリソース棚卸し**。新規 API 統合を提案する前に「**1Password vault に
  既に key があるか**」をユーザーに必ず聞く。手元在庫を能動確認しない判断ミスは
  過去複数事例あり

詳細・R4-R6・R/G 比較表は `learnings/insights.md` 参照。

## ゴール駆動の能力拡張原則（proactive）

R シリーズ（failure 起点）と並び、**ゴール起点で能力を能動的に拡張**するメタルール。
R が「過去の罠の再発防止」（🛡️ ガードレール）なら、G は「未踏領域への進路設定」（🧭 コンパス）。
両方ないと「動いてるから直さない」罠に陥る（travel リポで楽天 API を半年見逃した実例あり）。

- **G1: ゴール起点の能力ギャップ検出**。<DOMAIN> サイクル（旅行ごと / 月次クレカ締め / 案件ごと）の
  retrospective で「もっと良くできた部分は？」を必ず1項目以上抽出 → **能力ギャップに
  変換**して次サイクルまでに埋める。「動いた / 完走した」で済ませない。retrospective
  テンプレに「次までに埋める能力ギャップ」欄を持つ
- **G2: 手段の多様性（API に限らない）**。「できない」と判断する前に **5 カテゴリを必ず
  検討**：(1) 公式 API（構造化・最優先）／ (2) ブラウザ自動化（Playwright / browser-use）
  ／ (3) MCP サーバー（既存 or 自作）／ (4) OCR・画像認識（PDF/スクショからのデータ抽出）
  ／ (5) ハイブリッド（LLM が候補生成 → 人間が実行 → 結果を repo に記録）。「API がないから
  無理」の即断は禁止
- **G3: 制約の分類と挑戦**。「できない」要因に出会ったら **3 分類**：(1) **物理制約**
  （LLM が live data に直接アクセス不可 等）→ 受容・一次ソース誘導／ (2) **policy 制約**
  （sandbox egress 403 / 公式 ToS の API access 制限 等）→ **必ず挑戦**（別エンドポイント /
  Custom 設定 / Web UI 設定 / 公式パートナー登録で外せないか確認）／ (3) **自己制約**
  （「難しそう」「面倒」）→ **30 分の調査投資で挑戦**
- **G4: 能力拡張の予算化**。本業案件と並行で **「ツール改善」の時間枠を必ず持つ**。
  retrospective ごとに「次サイクルまでに埋める能力 1 項目」を必須化し、ツール改善 PR を
  立てる。これがないと本業案件が常に優先されて infra が永遠に band-aid のままになる

### R シリーズと G シリーズの補完関係

| 軸 | R（reactive） | G（proactive） |
|---|---|---|
| 発火 | 失敗・摩擦に直面した時 | retrospective / 定期監査 / セッション開始 |
| 視線 | 🔙 過去の罠の再発防止 | 🔜 未踏領域への進路設定 |
| 失敗時の症状 | 同じ罠を繰り返す | 「動いてるから直さない」で band-aid 永続 |
| 比喩 | 🛡️ ガードレール | 🧭 コンパス |

詳細な比較表と事例は `learnings/insights.md` の同セクション参照。

---

## 【template 版・カスタマイズ箇所】

このファイルを adopt する時、以下を当該ドメインに置換すること：

| プレースホルダ / 一般化部分 | 置換例（travel） | 置換例（treasury） |
|---|---|---|
| `<DOMAIN> サイクル` | 「旅行ごと」 | 「月次クレカ締め」 |
| R1 の例文 | 楽天 GORA / openapi 別ホスト | クレカ会員サイト / Plaid |
| R2 の例文 | 楽天GORA URL / 楽天 Web Service API | クレカ明細 / Plaid・Mastercard Open Banking |
| R3 の例文 | 楽天 API key | SBI / Plaid 等の API key |
| G1 の retrospective 単位 | 旅行ごと | 月次・案件ごと |
| G2 の例 | 楽天 API / Playwright で web 操作 | Plaid API / クレカ明細 OCR / 銀行 CSV インポート |
| G3 の policy 制約例 | 楽天 GORA 公式 docs と実 API 乖離 | カード会社 ToS の API restriction |
| G4 のツール改善例 | rakuten-gora.sh 実装 | plaid-sync.sh 実装 |

## Web調査ツール: Gemini CLI 第一選択

Web検索・最新情報の調査が必要な場合、**Gemini CLI を第一選択**とする。
内蔵の `WebSearch` / `WebFetch` は Gemini CLI が使えない場合のフォールバック。

### 使い分け

| 用途 | ツール | 理由 |
|------|--------|------|
| 最新情報の検索・要約・出典付き調査 | `gemini` (Gemini CLI) | Google検索でグラウンディングされた回答が得られる。長文コンテキストに強い |
| 既知URLの内容取得・要約 | `WebFetch` | 単一ページの読み取りに十分 |
| Gemini CLI 未セットアップ・APIキー無し | `WebSearch` / `WebFetch` | フォールバック |

### 使い方

認証方式に応じて呼び出しを使い分ける（どちらも自動判定したい場合は **ラッパー推奨**）。

```bash
# 推奨: ラッパー経由（GEMINI_API_KEY と OP_SERVICE_ACCOUNT_TOKEN を自動判定）
bash scripts/gemini-call.sh -p "調べたいクエリ"

# 直接呼び出し（GEMINI_API_KEY 設定済の場合のみ）
gemini -p "調べたいクエリ"
```

セットアップ手順は `README.md` の「Gemini CLI セットアップ」を参照。
SessionStart フックが `gemini` / `op` CLI を自動インストールする。

## マルチLLMオーケストレーション

Claude Code を司令塔に、外部 LLM を役割分担で呼び分ける構成。
**Drive 共有フォルダなど多人数利用領域では、エコモデル自動選択でトークン浪費を防ぐ。**

### 役割分担

| 役割 | LLM | コスト | 主な用途 | ラッパー |
|------|-----|------|---------|---------|
| 目 | Grok | $0.20/Mtoken | X(Twitter) リアルタイム検索 | `scripts/grok-call.sh` |
| 手足 | Qwen (local) | $0 | 要約・分類・整形 | `scripts/qwen-call.sh` |
| 参謀 | Codex (GPT-5) | 中 | 戦略判断・レビュー | `scripts/codex-call.sh` |
| 別視点 | Gemini | 中 | マルチモーダル・別バイアス | `scripts/gemini-call.sh` |
| 司令塔 | Claude | 高 | オーケストレーション | デフォルト |

### エコモデル自動選択（二層防御）

1. **PreToolUse フック**: `.claude/hooks/eco-mode-drive.sh` が Drive MCP ツールを検知し、Qwen 経由要約への誘導ガイドを stderr に出力
2. **ECO_MODE 環境変数**: `ECO_MODE=1` または `DRIVE_CONTEXT=1` で `scripts/llm-router.sh` が軽処理を Qwen→Haiku に強制ルーティング

### 振り分け判定

```bash
# どこに振るかだけ確認
bash scripts/llm-router.sh --task "X で claude-code がバズってる投稿"
# → grok\tX/Twitter キーワード検出
```

詳細設計: `docs/multi-llm-orchestration.md`
関連スキル: `.claude/skills/llm-router.md` / `x-search.md` / `codex-review.md` / `qwen-eco.md` / `drive-eco-access.md`

## Git ワークフロー

- **デフォルトブランチ**: `main`（直接push禁止、PR経由）
- **コミットメッセージ**: 日本語で簡潔に

## 主要ファイル

- `docs/claude-detailed-rules.md` — フォルダ構成・設計原則・技術スタック等の詳細ルール
- `docs/multi-llm-orchestration.md` — マルチLLMオーケストレーション設計

## コンテキスト管理（3層構造）

| Layer | 場所 | 役割 | 注入タイミング |
|---|---|---|---|
| 1 | `CLAUDE.md` | コアルール（本ファイル） | 毎ターン自動注入 |
| 2 | `memory/` ＋ `profile/` ＋ `learnings/` ＋ `<domain>/visited/` | セッション状態・辞書・学習・除外（5 ブロック構造） | セッション開始時に `.claude/scripts/session-context.sh` で連結注入 |
| 3 | `.claude/skills/` | 手順スキル | キーワード発火時にオンデマンド |

> Layer 2 の SessionStart 注入は **①状態・②辞書・③学習・④除外・⑤未来** の 5 ブロックに分解される。
> 詳細：[`docs/active-context-template.md`](docs/active-context-template.md#sessionstart-注入の-3-層構造推奨拡張)

## 状態の鮮度を保つルール（active-context 連動）

セッション内で日時・状態がずれる「状態ドリフト」を防ぐため、以下を厳守：

### 時刻参照前は必ず実時刻を取得

時刻に依存する発言（"今"・"明日"・"締切まで" 等）の前は、必ず Bash で実時刻を取得する：

```bash
TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M (%a) JST"
```

会話履歴の流れだけで日付・曜日を推定しない。
SessionStart hook が起動時に注入する `=== Current JST Time ===` も信頼源として参照する。

### 状態変化は memory/active-context.md に即時反映

ユーザーから状態変化（意思決定・タスク完了・候補確定・条件変更）を受けたら、
即座に `memory/active-context.md` を更新する。

更新後は短くてよいのでコミット＆プッシュして、
次セッションで自動注入されるようにする。

### 不確かな状態は推測せず確認

意思決定の変更・進行の中断・要件の解釈ぶれ等で**現状が曖昧**になった場合、
勘で続けず1〜2点に絞って確認質問する。

## CLAUDE.md の運用ガイドライン

### soft cap 200 行（推奨）

CLAUDE.md は **毎ターン全文注入** されるため、肥大化すると：

- 重要なルールが他のテキストに埋もれる
- 「リスク回避＞ユーザー価値」の過防衛モードに入りやすくなる
- 注入トークンが他の文脈を圧迫する

**運用ルール**：

- soft cap：**200 行**
- 経緯・失敗事例・歴史的判断 → `learnings/insights.md` に追い出す
- 検証ルールの**見出し**は CLAUDE.md に残し、**詳細**は learnings/ に置く
- 200 行を超えたら「active rules のみ残す・経緯は別ファイル」を検討する
- 〜250 行程度は許容、300 行を超えたら緊急整理対象

> **TODO（要レビュー）**：200 行をハードルールにするか、推奨ガイドラインに留めるか。
> 現状は推奨ガイドラインとして記述している（派生リポでの運用検証後に判断）。

### 提案スタイル（決断負担の押し付けを避ける）

3 層 SessionStart 注入（状態・辞書・学習・除外）が機能していれば、
プロファイルから決め打ちした **主導提案 1 案 + 代替 1〜2 案** を先に出せる。

- AskUserQuestion の連発（3 回以上）は **3 層注入が活用されていない劣化サイン**
- 候補比較表を出して「どれにしますか？」と丸投げするのも劣化サイン
- 確認ループは原則 1 回（提案 → ユーザー確認 → 確定）

詳細：`docs/personal-concierge-template.md` の原則6 参照。