# 利用可能なリソース・残高・予算

> このファイルは手動更新。AIはここに記載された情報のみを参照し、推測で残高を記載してはならない。
> **更新日から30日以上経過している場合、AIは警告を出すこと。**

## 最終更新日

- **更新日: 2026-05-02**

## 予算・残高

<!-- 例:
| 項目 | 残高・上限 | 備考 |
|------|-----------|------|
| GCP クレジット | ¥XX,XXX | 有効期限: YYYY-MM-DD |
| API利用枠 | $XX/月 | OpenAI, Anthropic等 |
-->

## 利用可能なツール・サービス

### API キー・認証情報

| サービス | ローカル保管先 | バックアップ・正本 | 備考 |
|---------|--------------|------------------|------|
| Gemini API キー | `.claude/settings.local.json` の `env.GEMINI_API_KEY` (直接) または `env.OP_SERVICE_ACCOUNT_TOKEN` (op 経由) | 1Password Business: `5co` アカウント / Vault `claude-code-secrets` / Item `Gemini API Key (Template)` / field `credential`。発行元は <https://aistudio.google.com/apikey> | `.gitignore` 済み。`scripts/gemini-call.sh` が認証方式を自動判定 |
| Grok (xAI) API キー | `.claude/settings.local.json` の `env.XAI_API_KEY` (直接) または `env.OP_SERVICE_ACCOUNT_TOKEN` (op 経由) | 1Password Business: Vault `claude-code-secrets` / Item `Grok API Key (Template)` / field `credential`。発行元は <https://console.x.ai/team/default/api-keys> | `scripts/grok-call.sh` / `scripts/grok_context_research.ts` が参照。X(Twitter) リアルタイム検索用 |
| OpenAI (Codex) API キー | `.claude/settings.local.json` の `env.OPENAI_API_KEY` (直接) または `env.OP_SERVICE_ACCOUNT_TOKEN` (op 経由) | 1Password Business: Vault `claude-code-secrets` / Item `OpenAI API Key (Template)` / field `credential`。発行元は <https://platform.openai.com/api-keys> | `scripts/codex-call.sh` が参照。GPT-5 系セカンドオピニオン用 |
| GitHub PAT (private リポ read) | `.claude/settings.local.json` の `env.GITHUB_TOKEN` (直接) または `env.OP_SERVICE_ACCOUNT_TOKEN` (op 経由) | 1Password Business: Vault `claude-code-secrets` / Item `GitHub PAT (Template)` / field `credential`。発行元は <https://github.com/settings/tokens/new>。スコープ: `repo`、有効期限: No expiration | `scripts/github-fetch.sh` / `scripts/github-tree.sh` が参照。private リポからの逆輸入用。詳細は `docs/private-repo-import.md` |
| Qwen (ローカル) | 認証不要（Ollama 経由） | — | `scripts/qwen-call.sh` が `localhost:11434` の Ollama サーバを呼ぶ。SessionStart フックが自動セットアップ |
| 1Password Service Account | `.claude/settings.local.json` の `env.OP_SERVICE_ACCOUNT_TOKEN` (`ops_eyJ...`) | 1Password Business: Service Account `claude-code-template`（Vault `claude-code-secrets` への read 権限） | トークンは発行時のみ表示。失念時は再発行（既存トークンは閲覧不可） |

#### `op` 経由の取得例

```bash
# Service Account トークンが env に設定済の前提
op read "op://claude-code-secrets/Gemini API Key (Template)/credential"
op read "op://claude-code-secrets/Grok API Key (Template)/credential"
op read "op://claude-code-secrets/OpenAI API Key (Template)/credential"
op read "op://claude-code-secrets/GitHub PAT (Template)/credential"

# ラッパー経由（推奨）。各ラッパーが認証方式を自動判定
bash scripts/gemini-call.sh -p "クエリ"
bash scripts/grok-call.sh "X 検索したい内容"
bash scripts/codex-call.sh "戦略レビュー" < diff.txt
bash scripts/qwen-call.sh --task summarize < doc.txt   # 認証不要
bash scripts/github-fetch.sh widenormal/travel docs/foo.md   # private リポから取得
```

<!-- その他のツール・サービス例:
- 1Password Business（全社導入済み）
- GCP Cloud Storage + IAP
- GitHub（Privateリポジトリ）
-->
