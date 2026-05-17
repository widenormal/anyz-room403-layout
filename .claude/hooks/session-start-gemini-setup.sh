#!/bin/bash
# Claude Code SessionStart フック
# Gemini CLI と 1Password CLI を未インストールなら自動セットアップする。
#
# 認証は 2 通り（どちらか 1 つ）:
#   1. GEMINI_API_KEY を直接 settings.local.json に設定
#   2. OP_SERVICE_ACCOUNT_TOKEN を設定 → op read で動的に取得（推奨）

set -u

log() { printf '[gemini-setup] %s\n' "$*" >&2; }

# --- 1. gemini CLI ---
GEMINI_CLI_VERSION="${GEMINI_CLI_VERSION:-0.40.0}"
SETUP_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/claude-template-setup"
GEMINI_MARKER="$SETUP_CACHE_DIR/gemini-${GEMINI_CLI_VERSION}.ok"
mkdir -p "$SETUP_CACHE_DIR" 2>/dev/null || true

gemini_install() {
  if ! command -v npm >/dev/null 2>&1; then
    log "npm が無いため gemini CLI を入れられません。Node.js を導入してください。"
    return 1
  fi
  if npm install -g "@google/gemini-cli@${GEMINI_CLI_VERSION}" >/tmp/gemini-install.log 2>&1; then
    log "gemini CLI インストール完了: $(gemini --version 2>/dev/null || echo unknown)"
    touch "$GEMINI_MARKER" 2>/dev/null || true
  else
    log "gemini CLI インストール失敗。/tmp/gemini-install.log を確認。"
    return 1
  fi
}

# キャッシュマーカーが gemini 実体と整合していれば version 起動を省略する。
# マーカーが gemini 実体より古い場合は実体差し替えとみなし再検証。
gemini_marker_valid() {
  [ -f "$GEMINI_MARKER" ] || return 1
  local bin
  bin="$(command -v gemini 2>/dev/null)" || return 1
  [ -e "$bin" ] || return 1
  [ "$bin" -nt "$GEMINI_MARKER" ] && return 1
  return 0
}

if ! command -v gemini >/dev/null 2>&1; then
  log "gemini CLI 未検出。npm i -g @google/gemini-cli@${GEMINI_CLI_VERSION} を実行します。"
  gemini_install || true
elif gemini_marker_valid; then
  log "gemini CLI 確認: ${GEMINI_CLI_VERSION} (cached)"
else
  CURRENT_GEMINI_VERSION="$(gemini --version 2>/dev/null | tr -d '[:space:]' || echo unknown)"
  if [ "$CURRENT_GEMINI_VERSION" = "$GEMINI_CLI_VERSION" ]; then
    log "gemini CLI 確認: ${CURRENT_GEMINI_VERSION} (一致)"
    touch "$GEMINI_MARKER" 2>/dev/null || true
  else
    log "gemini CLI バージョン不一致 (現在: ${CURRENT_GEMINI_VERSION} / 期待: ${GEMINI_CLI_VERSION})。再インストールします。"
    gemini_install || true
  fi
fi

# --- 2. op (1Password) CLI ---
if ! command -v op >/dev/null 2>&1; then
  log "op (1Password) CLI 未検出。インストールを試行します。"
  OP_VERSION="${OP_CLI_VERSION:-2.30.0}"
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64|amd64) OP_ARCH="amd64" ;;
    aarch64|arm64) OP_ARCH="arm64" ;;
    *) OP_ARCH="" ;;
  esac
  if [ -n "$OP_ARCH" ]; then
    TMPDIR_OP="$(mktemp -d)"
    URL="https://cache.agilebits.com/dist/1P/op2/pkg/v${OP_VERSION}/op_linux_${OP_ARCH}_v${OP_VERSION}.zip"
    if curl -fsSL "$URL" -o "$TMPDIR_OP/op.zip" 2>/tmp/op-install.log && \
       unzip -q "$TMPDIR_OP/op.zip" -d "$TMPDIR_OP" 2>>/tmp/op-install.log; then
      INSTALL_DIR="${OP_INSTALL_DIR:-$HOME/.local/bin}"
      mkdir -p "$INSTALL_DIR"
      install -m 0755 "$TMPDIR_OP/op" "$INSTALL_DIR/op"
      case ":$PATH:" in
        *":$INSTALL_DIR:"*) ;;
        *) export PATH="$INSTALL_DIR:$PATH" ;;
      esac
      log "op CLI インストール完了: $($INSTALL_DIR/op --version 2>/dev/null || echo unknown) ($INSTALL_DIR)"
      log "PATH に $INSTALL_DIR を恒久追加することを推奨"
    else
      log "op CLI インストール失敗。/tmp/op-install.log を確認。"
    fi
    rm -rf "$TMPDIR_OP"
  else
    log "未対応アーキテクチャ ($ARCH)。op CLI を手動で入れてください。"
  fi
else
  log "op CLI 確認: $(op --version 2>/dev/null || echo unknown)"
fi

# --- 3. 認証情報チェック ---
if [ -n "${GEMINI_API_KEY:-}" ]; then
  log "認証: GEMINI_API_KEY 設定済 (直接モード)"
elif [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  log "認証: OP_SERVICE_ACCOUNT_TOKEN 設定済 (1Password モード)。gemini 呼び出しは scripts/gemini-call.sh 経由を推奨"
else
  log "警告: GEMINI_API_KEY も OP_SERVICE_ACCOUNT_TOKEN も未設定。gemini は動作しません。"
  log "       設定例は settings.local.json.example を参照してください。"
fi

exit 0
