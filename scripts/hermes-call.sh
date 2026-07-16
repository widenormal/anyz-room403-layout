#!/usr/bin/env bash
set -euo pipefail

# hermes-call.sh
# 用途:
#   Hermes CLI を使って xAI(grok) プロバイダ経由でプロンプトを送信します。
#
# 認証方式:
#   以下の順で XAI_API_KEY を解決します。
#     1. 環境変数 XAI_API_KEY
#     2. ~/.grok-env を source して再判定
#     3. OP_SERVICE_ACCOUNT_TOKEN がある場合、op CLI で
#        op://claude-code-secrets/Grok API Key (Template)/credential
#        から取得
#
# 使い方:
#   scripts/hermes-call.sh [--model MODEL] [--provider PROVIDER] [PROMPT...]
#   echo "prompt" | scripts/hermes-call.sh --model grok-4.3
#
# 備考:
#   - 引数の残りはスペース区切りで 1 つの PROMPT に連結します。
#   - PROMPT 引数が空で stdin が tty でない場合は stdin を読み取ります。

# モデル既定値は llm-models.conf（正データ・申請制で自動更新）から解決
_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/llm-models.conf"
[ -f "$_CONF" ] && . "$_CONF"
MODEL="${HERMES_MODEL:-${HERMES_DEFAULT_MODEL:-grok-4.3}}"
PROVIDER="xai"
PROMPT=""

usage() {
  cat <<'EOF'
使い方:
  scripts/hermes-call.sh [--model MODEL] [--provider PROVIDER] [PROMPT...]

オプション:
  --model MODEL         使用するモデル名（既定: grok-4.3）
  --provider PROVIDER   使用する provider（既定: xai）
  -h, --help            このヘルプを表示

認証:
  1. XAI_API_KEY 環境変数
  2. ~/.grok-env
  3. OP_SERVICE_ACCOUNT_TOKEN + op CLI
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      [[ $# -ge 2 ]] || { echo "Error: --model には値が必要です" >&2; exit 1; }
      MODEL="$2"
      shift 2
      ;;
    --provider)
      [[ $# -ge 2 ]] || { echo "Error: --provider には値が必要です" >&2; exit 1; }
      PROVIDER="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      if [[ $# -gt 0 ]]; then
        if [[ -n "$PROMPT" ]]; then
          PROMPT+=" "
        fi
        PROMPT+="$*"
      fi
      break
      ;;
    *)
      if [[ -n "$PROMPT" ]]; then
        PROMPT+=" "
      fi
      PROMPT+="$1"
      shift
      ;;
  esac
done

if [[ -z "$PROMPT" && ! -t 0 ]]; then
  STDIN_CONTENT="$(cat)"
  if [[ -n "$STDIN_CONTENT" ]]; then
    PROMPT="$STDIN_CONTENT"
  fi
fi

if [[ -z "$PROMPT" ]]; then
  echo "Error: PROMPT が必要です" >&2
  exit 1
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "Error: hermes コマンドが見つかりません。PATH を確認してください。" >&2
  exit 127
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
    echo "取得先: https://console.x.ai/"
  } >&2
  exit 1
}

resolve_xai_api_key() {
  if [[ -n "${XAI_API_KEY:-}" ]]; then
    return 0
  fi

  if [[ -f "${HOME}/.grok-env" ]]; then
    # shellcheck disable=SC1090
    source "${HOME}/.grok-env"
    if [[ -n "${XAI_API_KEY:-}" ]]; then
      export XAI_API_KEY
      return 0
    fi
  fi

  if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]] && command -v op >/dev/null 2>&1; then
    local op_value
    # op item get は括弧入り title でも動作（op read の op:// 参照は括弧 NG）
    if op_value="$(op item get 'Grok API Key (Template)' --vault claude-code-secrets --fields credential --reveal 2>/dev/null)" && [[ -n "$op_value" ]]; then
      export XAI_API_KEY="$op_value"
      return 0
    fi
  fi

  diag_and_die "Grok API Key (Template)" "Grok"
}

resolve_xai_api_key

hermes -z "$PROMPT" --provider "$PROVIDER" -m "$MODEL"
echo "[hermes-call] model=$MODEL provider=$PROVIDER" >&2
