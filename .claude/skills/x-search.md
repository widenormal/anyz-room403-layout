# Skill: X(Twitter) 検索・取得（「目」役）

> X のデータ取得は**構造化 API（XMCP / x-search.sh）が第一選択**、Grok は取得結果の
> 要約・解釈に使う（2026-07-14 再構成。旧「Grok 直行」から変更・decisions.md 参照）。

## トリガー

- 「X で調べて」「バズってる投稿」「トレンド」「このポストの内容」「X の記事を読んで」
- X の URL（x.com/…/status/…）が貼られたとき

## 優先順位（この順に試す）

1. **XMCP**（X 公式ホスト型 MCP・`/mcp` の `xmcp`）
   - `search_posts_all`（全アーカイブ検索）・`get_trends_by_woeid`（日本=woeid 23424856）・
     `search_news`・タイムライン・ユーザー等 200+ ツール
   - 接続は `.mcp.json`＋`.claude/scripts/xmcp-launch.sh`（token は op 自動解決・env 注入不要）
2. **`scripts/x-search.sh`**（X API v2 直。XMCP 未接続時・CLI 一発で済む時）
   ```bash
   bash scripts/x-search.sh "claude code lang:ja -is:retweet" -n 10   # 直近7日の検索
   bash scripts/x-search.sh --tweet <id>    # ポスト全文（X Articles 本文 plain_text 含む）
   ```
3. **要約・解釈・意味検索が必要な時だけ Grok**
   ```bash
   bash scripts/grok-call.sh "この10件の投稿から傾向を3点で要約" < 取得結果.txt
   ```
   xAI 直が失敗（クレジット枯渇等）しても OpenRouter へ自動フォールバックする。
   X ネイティブデータは 1/2 で取得してから渡すこと（フォールバック時は x_search 不可）。

## 課金・制約（実測 2026-07-14）

- XMCP / x-search.sh は**同じ X API プラン枠**（検索 450 リクエスト/15分・xAI クレジット不要）
- **X Articles（長文記事）はログイン不要で全文取得可**（`--tweet` の ARTICLE 出力＝
  `article.plain_text`。ミラー検索や Grok 経由より確実）
- 429 が続く場合はプラン上限。時間を置くか X API プラン／xAI 直経路の復活を検討
- 高度な X リサーチの既存 TS（`scripts/grok_context_research.ts`）は XAI_API_KEY 使用＝要クレジット

## 認証

- x-search.sh: 1Password「X Bearer Token」（`X_BEARER_TOKEN` env でも可・op 自動解決）
- grok-call.sh: 1Password「Grok API Key (Template)」→ 失敗時 OpenRouter「OpenRouter Fusion」

## 関連

- `memory/decisions.md` 2026-07-14（「目」の再構成・XMCP 採用・xAI クレジット不購入）
- `docs/multi-llm-orchestration.md` XMCP 節（接続構成・実測値・ゼロタッチ認証）
- `.claude/skills/llm-router.md`（全体のルーティング）
