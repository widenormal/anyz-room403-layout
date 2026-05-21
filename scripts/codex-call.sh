#!/bin/bash
# Codex (OpenAI GPT-5 系) 呼び出しラッパー。
# 用途: 戦略判断・コードレビュー・リスクチェックのセカンドオピニオン。
#
# 認証方式の自動判定:
#   1. OPENAI_API_KEY 設定済 → そのまま実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op read で動的取得
#   3. どちらも未設定 → エラー
#
# 既定モデルは gpt-5.4-mini（戦略判断には gpt-5.4 を推奨）。
#
# 使い方:
#   bash scripts/codex-call.sh "この PR の設計をレビュー" < diff.txt
#   echo "Q: SEO 戦略の優先順位は?" | bash scripts/codex-call.sh --model gpt-5.4

set -euo pipefail

MODEL="gpt-5.4-mini"
SYSTEM="You are a careful code & strategy reviewer. Answer concisely in Japanese unless asked otherwise. Identify risks, edge cases, and unstated assumptions."
PROMPT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2 ;;
    --system) SYSTEM="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) PROMPT="${PROMPT}${PROMPT:+ }$1"; shift ;;
  esac
done

# stdin に追加コンテキストがあれば結合
if [ ! -t 0 ]; then
  STDIN_CTX="$(cat)"
  if [ -n "$STDIN_CTX" ]; then
    PROMPT="${PROMPT}

---
${STDIN_CTX}"
  fi
fi

if [ -z "$PROMPT" ]; then
  echo "ERROR: プロンプトを指定してください（引数または stdin）" >&2
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
    echo "取得先: https://platform.openai.com/api-keys"
  } >&2
  exit 1
}

resolve_key() {
  if [ -n "${OPENAI_API_KEY:-}" ]; then
    return 0
  fi
  if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
    OPENAI_API_KEY="$(op read 'op://claude-code-secrets/OpenAI API Key/credential' 2>/dev/null || true)"
    if [ -n "$OPENAI_API_KEY" ]; then
      export OPENAI_API_KEY
      return 0
    fi
  fi
  diag_and_die "OpenAI API Key" "Codex"
}

resolve_key

PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg system "$SYSTEM" \
  --arg prompt "$PROMPT" \
  '{
    model: $model,
    messages: [
      {role: "system", content: $system},
      {role: "user", content: $prompt}
    ]
  }')

RESPONSE=$(curl -fsS https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESPONSE" | jq -r '.choices[0].message.content // empty'

USAGE=$(echo "$RESPONSE" | jq -r '.usage | "\(.prompt_tokens // 0)/\(.completion_tokens // 0)"')
echo "" >&2
echo "[codex-call] model=$MODEL tokens=$USAGE" >&2
