#!/bin/bash
# Grok (xAI) 呼び出しラッパー。X(Twitter) のリアルタイム検索が必要なときに使う。
#
# 認証方式の自動判定:
#   1. XAI_API_KEY 設定済 → そのまま実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op run で .env.xai のシークレット参照を解決
#   3. どちらも未設定 → エラー
#
# 既定モデルは llm-models.conf の GROK_DEFAULT_MODEL（申請制で自動更新）。
# xAI 直が失敗（クレジット枯渇等）した場合は GROK_OPENROUTER_MODEL:online に
# 自動フォールバックする。X ネイティブ検索データが必要なら x-search.sh を先に使う。
# 既存の TS スクリプト（scripts/grok_context_research.ts）も同じ XAI_API_KEY を使う。
#
# 使い方:
#   bash scripts/grok-call.sh "X で claude-code 関連の昨晩バズった投稿"
#   bash scripts/grok-call.sh --model grok-4-1-reasoning "AI 業界の最新動向"

set -euo pipefail

# モデル既定値は llm-models.conf（正データ・申請制で自動更新）から解決
_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/llm-models.conf"
[ -f "$_CONF" ] && . "$_CONF"
MODEL="${GROK_MODEL:-${GROK_DEFAULT_MODEL:-grok-4-1-fast}}"
PROMPT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) PROMPT="${PROMPT}${PROMPT:+ }$1"; shift ;;
  esac
done

if [ -z "$PROMPT" ]; then
  echo "ERROR: クエリを指定してください。例: bash scripts/grok-call.sh 'AI 関連で昨晩バズった投稿'" >&2
  exit 1
fi

diag_and_die() {
  local item="$1" svc="$2"
  {
    echo "ERROR: ${svc} 認証取得失敗（3段階診断）"
    echo "  - op CLI:                  $(command -v op >/dev/null 2>&1 && echo ✅ || echo ❌)"
    echo "  - OP_SERVICE_ACCOUNT_TOKEN: $([ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && echo ✅ || echo ❌)"
    echo "  - op whoami:               $(op whoami >/dev/null 2>&1 && echo ✅ || echo ❌)"
    local v
    v="$(op item get "$item" --vault claude-code-secrets --fields credential --reveal 2>&1 || true)"
    if [ -z "$v" ]; then
      echo "  - op read credential:      ❌ 空値（vault item の field 未投入の可能性）"
    elif echo "$v" | grep -qi "error\|not found"; then
      echo "  - op read credential:      ❌ ${v}"
    else
      echo "  - op read credential:      ✅ ${#v}B → ラッパーのロジックバグの可能性大"
    fi
    echo "対応: 上記が全部 ✅ ならラッパー修正、または '${item}' を直接 export して呼ぶ"
    echo "取得先: https://console.x.ai/team/default/api-keys"
  } >&2
  exit 1
}

resolve_key() {
  if [ -n "${XAI_API_KEY:-}" ]; then
    return 0
  fi
  if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
    # op item get は括弧入り title でも動作（op read の op:// 参照は括弧 NG）
    XAI_API_KEY="$(op item get 'Grok API Key (Template)' --vault claude-code-secrets --fields credential --reveal 2>/dev/null || true)"
    if [ -n "$XAI_API_KEY" ]; then
      export XAI_API_KEY
      return 0
    fi
  fi
  diag_and_die "Grok API Key (Template)" "Grok"
}

resolve_key

# Web 検索 + X 検索を有効化した Responses API 呼び出し
PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg prompt "$PROMPT" \
  '{
    model: $model,
    input: $prompt,
    tools: [
      {type: "web_search"},
      {type: "x_search"}
    ]
  }')

RESPONSE=$(curl -fsS https://api.x.ai/v1/responses \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" 2>/dev/null || true)

if [ -n "$RESPONSE" ]; then
  echo "$RESPONSE" | jq -r '
    .output[]?
    | select(.type == "message")
    | .content[]?
    | select(.type == "output_text")
    | .text
  '
  USAGE=$(echo "$RESPONSE" | jq -r '.usage | "\(.input_tokens // 0)/\(.output_tokens // 0)"')
  echo "" >&2
  echo "[grok-call] model=$MODEL tokens=$USAGE" >&2
  exit 0
fi

# ── xAI 直が失敗（クレジット枯渇等）→ OpenRouter 経由の Grok にフォールバック ──
# X ネイティブ検索（x_search）は OpenRouter では使えない。X データが必要な場合は
# x-search.sh（X API 直・クレジット不要）で取得してから本ラッパーに渡すこと。
OR_MODEL="${GROK_OPENROUTER_MODEL:-x-ai/grok-4.5}"
echo "[grok-call] xAI 直が失敗 → OpenRouter フォールバック (${OR_MODEL}:online)。X 検索は x-search.sh を使用" >&2

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
  OPENROUTER_API_KEY="$(op item get 'OpenRouter Fusion' --vault claude-code-secrets --fields credential --reveal 2>/dev/null || true)"
fi
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "ERROR: xAI 直も OpenRouter フォールバックも認証不能。クレジット/キーを確認" >&2
  exit 1
fi

OR_PAYLOAD=$(jq -n --arg model "${OR_MODEL}:online" --arg prompt "$PROMPT" \
  '{model: $model, messages: [{role: "user", content: $prompt}]}')
OR_RESPONSE=$(curl -fsS https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$OR_PAYLOAD")

echo "$OR_RESPONSE" | jq -r '.choices[0].message.content // empty'
USAGE=$(echo "$OR_RESPONSE" | jq -r '.usage | "\(.prompt_tokens // 0)/\(.completion_tokens // 0)"')
echo "" >&2
echo "[grok-call] model=${OR_MODEL}:online (openrouter fallback) tokens=$USAGE" >&2
