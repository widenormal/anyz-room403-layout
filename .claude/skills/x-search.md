# Skill: X(Twitter) 検索 — Grok 経由

> Claude Code 単体では X のツイート本文を取得できない。
> X のリアルタイム情報・トレンド・特定アカウント調査は **Grok（xAI）** に振る。

## トリガー

- 「X で…調べて」「Twitter で○○が話題か確認」
- 「自分のアカウントへのリプライを拾って」
- 「昨晩バズった投稿」
- 競合・話題の人物・特定ハッシュタグの調査

## 実行コマンド

```bash
# シンプルクエリ
bash scripts/grok-call.sh "claude-code 関連で昨晩バズった投稿 (impression 1000+)"

# モデル指定（推論強化）
bash scripts/grok-call.sh --model grok-4-1-reasoning "AI 業界の今週の動向"

# 既存 TS スクリプト（複数トピック・ファイル出力対応）
npx tsx scripts/grok_context_research.ts "OpenAI GPT-5" --output research.md
```

## 認証

- 1Password Vault: `claude-code-secrets` / Item: `Grok API Key (Template)` / field: `credential`
- ローカル env 直接指定: `XAI_API_KEY`
- `OP_SERVICE_ACCOUNT_TOKEN` 設定時はラッパーが op 経由で自動取得

## 出力の使い方

- Grok の応答は出典 URL を含む。**そのままユーザーに見せて OK**
- 大量の情報を取得した場合は **scripts/qwen-call.sh --task summarize** で要約してから Claude に渡す（トークン節約）

## 注意

- API は従量課金（grok-4-1-fast で $0.20/Mtoken クラス）
- Drive 共有フォルダから呼ばれた場合（ECO_MODE=1）は qwen に先に整形させる運用
