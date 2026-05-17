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

MODEL="grok-4.3"
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
    if op_value="$(op read 'op://claude-code-secrets/Grok API Key (Template)/credential' 2>/dev/null)" && [[ -n "$op_value" ]]; then
      export XAI_API_KEY="$op_value"
      return 0
    fi
  fi

  echo "Error: XAI_API_KEY が見つかりません。https://console.x.ai/ で API key を取得し、XAI_API_KEY を設定するか ~/.grok-env を用意するか 1Password(op) を設定してください。" >&2
  exit 1
}

resolve_xai_api_key

hermes -z "$PROMPT" --provider "$PROVIDER" -m "$MODEL"
echo "[hermes-call] model=$MODEL provider=$PROVIDER" >&2
