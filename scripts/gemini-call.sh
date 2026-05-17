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

if ! command -v gemini >/dev/null 2>&1; then
  echo "ERROR: gemini CLI が未インストールです。SessionStart フックの実行を確認するか、" >&2
  echo "       npm install -g @google/gemini-cli を実行してください。" >&2
  exit 127
fi

if [ -n "${GEMINI_API_KEY:-}" ]; then
  exec gemini "$@"
fi

if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  if ! command -v op >/dev/null 2>&1; then
    echo "ERROR: op (1Password CLI) が未インストールです。SessionStart フックの実行を確認してください。" >&2
    exit 127
  fi
  ENV_FILE="${GEMINI_OP_ENV_FILE:-.env.gemini}"
  if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE が見つかりません。.env.gemini.example をコピーして作成してください。" >&2
    exit 1
  fi
  exec op run --env-file="$ENV_FILE" -- gemini "$@"
fi

cat >&2 <<'EOF'
ERROR: 認証情報が未設定です。次のいずれかを .claude/settings.local.json に設定してください:
  - GEMINI_API_KEY (直接モード)
  - OP_SERVICE_ACCOUNT_TOKEN (1Password モード、推奨)
詳細は README.md「Gemini CLI セットアップ」を参照。
EOF
exit 1
