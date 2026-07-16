#!/bin/bash
# Codex (OpenAI GPT-5 系) 呼び出しラッパー。
# 用途: 戦略判断・コードレビュー・リスクチェックのセカンドオピニオン。
#
# 認証方式の自動判定:
#   1. OPENAI_API_KEY 設定済 → そのまま実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op read で動的取得
#   3. どちらも未設定 → エラー
#
# 既定モデルは llm-models.conf の CODEX_DEFAULT_MODEL（申請制で自動更新）。
# 重い判断は --frontier で CODEX_FRONTIER_MODEL に切替。
#
# 使い方:
#   bash scripts/codex-call.sh "この PR の設計をレビュー" < diff.txt
#   echo "Q: SEO 戦略の優先順位は?" | bash scripts/codex-call.sh --frontier

set -euo pipefail

# モデル既定値は llm-models.conf（正データ・申請制で自動更新）から解決
_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/llm-models.conf"
[ -f "$_CONF" ] && . "$_CONF"
MODEL="${CODEX_MODEL:-${CODEX_DEFAULT_MODEL:-gpt-5.6-terra}}"
SYSTEM="You are a careful code & strategy reviewer. Answer concisely in Japanese unless asked otherwise. Identify risks, edge cases, and unstated assumptions."
PROMPT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="${2:-}"; shift 2 ;;
    --frontier) MODEL="${CODEX_FRONTIER_MODEL:-gpt-5.6-sol}"; shift ;;
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

# 一時的な 401/429/5xx に備えて最大3回リトライ（2s/4s バックオフ）。
# 2026-07-14 実測: gpt-5.6-sol で断続的 401（再試行で解消）が複数回観測されたため。
RESPONSE=""
for _try in 1 2 3; do
  RESPONSE=$(curl -fsS https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD") && break
  [ "$_try" -lt 3 ] && { echo "[codex-call] HTTP エラー → リトライ ${_try}/2" >&2; sleep $((2 ** _try)); }
done
[ -n "$RESPONSE" ] || { echo "[codex-call] 3回失敗。認証・クレジット・モデル権限を確認" >&2; exit 1; }

echo "$RESPONSE" | jq -r '.choices[0].message.content // empty'

USAGE=$(echo "$RESPONSE" | jq -r '.usage | "\(.prompt_tokens // 0)/\(.completion_tokens // 0)"')
echo "" >&2
echo "[codex-call] model=$MODEL tokens=$USAGE" >&2
