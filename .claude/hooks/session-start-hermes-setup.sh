#!/bin/bash
# Claude Code SessionStart フック
# Hermes Agent (Nous Research の自律型エージェント CLI) を未インストールならセットアップする。
#
# xAI Grok との統合は 2 通りの認証をサポート:
# 1. SuperGrok OAuth (推奨・サブスクリプション枠消費・ブラウザ必須)
# 2. XAI_API_KEY env var (従量課金)
#
# sandbox 環境ではブラウザ不可のため (2) の XAI_API_KEY モードのみ動作。
# XAI_API_KEY は setup-op.sh が イ ~/.grok-env に書き出すため、本 hook では
# install のみ行う。
#
# 手元 PC で hermes --tui を使う際は OAuth モード推奨:
#   hermes auth add xai-oauth

set -u

log() { printf '[hermes-setup] %s\n' "$*" >&2; }

SETUP_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/claude-template-setup"
HERMES_MARKER="$SETUP_CACHE_DIR/hermes-installed.ok"
mkdir -p "$SETUP_CACHE_DIR" 2>/dev/null || true

# Python 3.11+ 必須
if ! command -v python3 >/dev/null 2>&1; then
  log "python3 未検出。Hermes Agent を入れるには Python 3.11+ が必要。skip。"
  exit 0
fi

PY_VER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo 0.0)"
PY_MAJOR="${PY_VER%%.*}"
PY_MINOR="${PY_VER##*.}"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  log "Python $PY_VER では不足 (Hermes Agent は 3.11+ 要求)。skip。"
  exit 0
fi

hermes_marker_valid() {
  [ -f "$HERMES_MARKER" ] || return 1
  local bin
  bin="$(command -v hermes 2>/dev/null)" || return 1
  [ -e "$bin" ] || return 1
  [ "$bin" -nt "$HERMES_MARKER" ] && return 1
  return 0
}

hermes_install() {
  log "Hermes Agent を install します（初回は数十秒かかります）..."

  # 公式 installer を --skip-setup で走らせる（インタラクティブ setup wizard を省略）
  # HERMES_INSTALL_DIR と HERMES_HOME は デフォルトの ~/.hermes / ~/.local/share/hermes-agent
  # パターンに任せる。
  if curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
     2>/tmp/hermes-install.log | bash -s -- --skip-setup >>/tmp/hermes-install.log 2>&1; then
    log "Hermes Agent install 完了: $(hermes --version 2>/dev/null | head -1 || echo unknown)"
    touch "$HERMES_MARKER" 2>/dev/null || true
    return 0
  else
    log "Hermes Agent install 失敗。/tmp/hermes-install.log を確認。"
    return 1
  fi
}

if command -v hermes >/dev/null 2>&1 && hermes_marker_valid; then
  log "Hermes Agent 確認: $(hermes --version 2>/dev/null | head -1 || echo unknown) (cached)"
elif command -v hermes >/dev/null 2>&1; then
  CURRENT_HERMES="$(hermes --version 2>/dev/null | head -1 || echo unknown)"
  log "Hermes Agent 確認: $CURRENT_HERMES (marker 更新)"
  touch "$HERMES_MARKER" 2>/dev/null || true
else
  hermes_install || true
fi

# 認証状態チェック
if command -v hermes >/dev/null 2>&1; then
  if [ -n "${XAI_API_KEY:-}" ]; then
    log "認証: XAI_API_KEY 設定済 (従量課金モード)"
  elif [ -f "$HOME/.grok-env" ]; then
    log "認証: ~/.grok-env あり。使用時は 'source ~/.grok-env && hermes ...' で起動"
  else
    log "認証: XAI_API_KEY 未設定。hermes 使用前に setup-op.sh を実行するか 'hermes auth add xai-oauth' (要ブラウザ) を実行。"
  fi
fi

exit 0
