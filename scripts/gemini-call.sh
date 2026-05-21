#!/bin/bash
# Gemini CLI 呼び出しラッパー
#
# 認証方式を自動判定:
#   1. GEMINI_API_KEY 設定済 → そのまま gemini を実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op run で .env.gemini のシークレット参照を解決
#   3. どちらも未設定 → エラー終了
#
# 使い方:
#   bash scripts/gemini-call.sh -p "調べたいクエリ"

set -euo pipefail

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
  } >&2
  exit 1
}

if ! command -v gemini >/dev/null 2>&1; then
  echo "ERROR: gemini CLI が未インストールです。SessionStart フックの実行を確認するか、" >&2
  echo "       npm install -g @google/gemini-cli を実行してください。" >&2
  exit 127
fi

if [ -n "${GEMINI_API_KEY:-}" ]; then
  exec gemini "$@"
fi

# OP 経由で直接 credential を読みに行く（.env.gemini が無くても動く）
# op item get は括弧入り title でも動作（op read の op:// 参照は括弧 NG）
if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
  K="$(op item get 'Gemini API Key (Template)' --vault claude-code-secrets --fields credential --reveal 2>/dev/null || true)"
  if [ -n "$K" ]; then
    export GEMINI_API_KEY="$K"
    exec gemini "$@"
  fi
  # フォールバック: .env.gemini が存在する場合は op run を使う（後方互換）
  ENV_FILE="${GEMINI_OP_ENV_FILE:-.env.gemini}"
  if [ -f "$ENV_FILE" ]; then
    exec op run --env-file="$ENV_FILE" -- gemini "$@"
  fi
  diag_and_die "Gemini API Key (Template)" "Gemini"
fi

cat >&2 <<'EOF'
ERROR: 認証情報が未設定です。次のいずれかを .claude/settings.local.json に設定してください:
  - GEMINI_API_KEY (直接モード)
  - OP_SERVICE_ACCOUNT_TOKEN (1Password モード、推奨)
詳細は README.md「Gemini CLI セットアップ」を参照。
EOF
exit 1
