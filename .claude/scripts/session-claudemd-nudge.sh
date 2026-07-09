#!/usr/bin/env bash
# session-claudemd-nudge.sh — UserPromptSubmit フック
#
# 走行中セッションの実行中に、プロジェクト直下 CLAUDE.md がディスク上で更新されたら
# 「/compact で再反映してください」と **一度だけ** 通知する。
#
# なぜ SessionStart ではなく UserPromptSubmit か:
#   SessionStart フックは 起動 / clear / compact / resume 時のみ発火し、その瞬間 CLAUDE.md は
#   新規読込される。つまり「起動後ずっと開いたままのセッション」には二度と発火せず、
#   実行中の外部更新（毎日 08:00 の drive-canonical-refresh.sh・apply-template --repair・
#   別セッションでの編集など）を検知できない。ユーザーの毎プロンプトで発火する
#   UserPromptSubmit なら、走行中セッションの外部更新を検知して /compact を促せる。
#   （新規セッションは開始時に最新版を読込済みなので通知不要＝初回はベースライン記録のみ。）
#
# 出力仕様（Claude Code hooks 公式）:
#   exit 0 + JSON の systemMessage      → ユーザー画面に警告表示（プロンプトはブロックしない）
#   同 hookSpecificOutput.additionalContext → モデルにも同内容を渡す（Claude が補足できる）
#   セッション単位（session_id）で CLAUDE.md の mtime ベースラインを保持し、増加時のみ
#   一度だけ通知する（毎ターン鳴らさない）。
#
# 失敗してもプロンプト処理を止めないため、常に exit 0 で抜ける。
set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

# --- 入力 JSON から session_id / cwd を取得（jq が無ければ素朴抽出） ---
get_field() {
  local key="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r --arg k "$key" '.[$k] // empty' 2>/dev/null
  else
    printf '%s' "$INPUT" | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1
  fi
}
SID=$(get_field session_id); [ -n "$SID" ] || SID="nosid"
CWD=$(get_field cwd)

# --- プロジェクト直下 CLAUDE.md を特定 ---
PROJ="${CLAUDE_PROJECT_DIR:-${CWD:-$(pwd)}}"
CLAUDE_MD="$PROJ/CLAUDE.md"
[ -f "$CLAUDE_MD" ] || exit 0

# --- 現在の mtime（GNU 優先→BSD フォールバック・数値ガード付き） ---
# 注: GNU stat では `-f` は「ファイルシステム情報」を指す別オプションで、`-f %m` は
#     mtime を返さない。よって GNU 形式（-c %Y）を先に試し、失敗時のみ BSD 形式（-f %m）。
MT=$(stat -c %Y "$CLAUDE_MD" 2>/dev/null || stat -f %m "$CLAUDE_MD" 2>/dev/null || echo "")
case "$MT" in ''|*[!0-9]*) MT="" ;; esac   # 数値以外（取得失敗・別値）は無効化して黙って抜ける
[ -n "$MT" ] || exit 0

# --- セッション別ベースライン ---
CACHE_DIR="${TMPDIR:-/tmp}/claude-claudemd-nudge"
mkdir -p "$CACHE_DIR" 2>/dev/null || true
SAFE_SID=$(printf '%s' "$SID" | tr -c 'A-Za-z0-9_.-' '_')
STATE="$CACHE_DIR/$SAFE_SID"

BASE=""
[ -f "$STATE" ] && BASE=$(cat "$STATE" 2>/dev/null)

# 初回（このセッションで初めて）: ベースライン記録のみ・通知なし
if [ -z "$BASE" ]; then
  printf '%s' "$MT" > "$STATE" 2>/dev/null || true
  exit 0
fi

# 変化なし / 過去方向: 何もしない
[ "$MT" = "$BASE" ] && exit 0
if [ "$MT" -le "$BASE" ] 2>/dev/null; then exit 0; fi

# --- 変化あり: ベースライン更新（次から鳴らさない）＋通知 ---
printf '%s' "$MT" > "$STATE" 2>/dev/null || true

MSG="⚠ CLAUDE.md がこのセッションの実行中にディスク上で更新されました（同期・別セッション編集など）。現在の会話には旧版が読み込まれたままです。最新ルールを反映するには、チャット欄で /compact を実行してください（会話は保持され、CLAUDE.md がディスクから再読込・再注入されます）。"

if command -v jq >/dev/null 2>&1; then
  jq -n --arg m "$MSG" \
    '{systemMessage:$m, hookSpecificOutput:{hookEventName:"UserPromptSubmit", additionalContext:$m}}'
else
  esc=$(printf '%s' "$MSG" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$esc" "$esc"
fi
exit 0
