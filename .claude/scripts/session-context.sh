#!/usr/bin/env bash
# session-context.sh: SessionStart hook で 6 ブロック構造の文脈を additionalContext に投入する。
#
# 注入するブロック（詳細：docs/active-context-template.md）:
#   ① 状態層 — memory/active-context.md（進行中タスク・直近の確定事項）
#   ② 辞書層 — profile/preferences.md / profile/resources.md（"今日のルール"）
#   ③ 学習層 — learnings/insights.md の見出し（過去事例の罠インデックス）
#   ④ 除外層 — destinations/visited/ ほか（既消化アイテム・ドメイン依存・任意）
#   ⑤ 未来層 — 任意（将来の予定・締切等）
#   ⑥ ツール可用性 — scripts/probe-tools.sh の実測表（op key / wrapper 疎通）
#
# 失敗時もセッション起動を妨げないため exit 0 で抜ける。

set -u

PROJ="${CLAUDE_PROJECT_DIR:-.}"
JST_NOW=$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M (%a) JST')

# ──────────────────────────────────────────────
# ① 状態層：active-context
#
#   優先順位（user-aware loading）:
#     1. memory/active-context/<basename $HOME>.md があれば、それ 1 件だけ読む
#     2. なければ memory/active-context/ 配下の `_` で始まらない全 .md を concat（旧挙動）
#     3. それも空なら旧形式の単一ファイル memory/active-context.md にフォールバック
#
#   `_README.md` / `_template.md` 等の運用文書は常に除外。
# ──────────────────────────────────────────────
SHORTNAME=$(basename "$HOME")
USER_CTX_FILE="$PROJ/memory/active-context/${SHORTNAME}.md"

STATE=""
LOAD_MODE=""

if [ -f "$USER_CTX_FILE" ]; then
  # 1. user-specific ファイルが存在
  STATE=$(cat "$USER_CTX_FILE")
  LOAD_MODE="per-user (${SHORTNAME}.md)"
elif [ -d "$PROJ/memory/active-context" ]; then
  # 2. ディレクトリはあるが該当ユーザのファイルが無い → 全件 concat（fallback）
  PER_PERSON=""
  for f in "$PROJ/memory/active-context"/*.md; do
    case "$(basename "$f")" in
      _*) ;;  # _README.md, _template.md 等は除外
      *)
        [ -f "$f" ] && PER_PERSON+=$'\n\n--- '"$(basename "$f")"$' ---\n'"$(cat "$f")"
        ;;
    esac
  done
  if [ -n "$PER_PERSON" ]; then
    STATE="⚠️ user-specific file 'memory/active-context/${SHORTNAME}.md' が無いため全員分を読み込み中。自分専用のファイルを作成してください（_README.md 参照）。${PER_PERSON}"
    LOAD_MODE="fallback-all (no ${SHORTNAME}.md)"
  fi
fi

# 3. それでも空なら旧形式の単一ファイルを試す
if [ -z "$STATE" ] && [ -f "$PROJ/memory/active-context.md" ]; then
  STATE=$(cat "$PROJ/memory/active-context.md")
  LOAD_MODE="legacy single file"
fi

[ -z "$STATE" ] && STATE="(no active-context found)"
[ -n "$LOAD_MODE" ] && STATE=$(printf '[loaded: %s]\n\n%s' "$LOAD_MODE" "$STATE")

# ──────────────────────────────────────────────
# ② 辞書層：プロファイル（好み・残高・期限）
# section 名は派生リポの実ファイルに合わせて書き換える
# ──────────────────────────────────────────────
PREFS=""
if [ -f "$PROJ/profile/preferences.md" ]; then
  # awk のレンジ /start/,/end/ は start と end が同一行でマッチすると 1 行で ON→OFF してしまう。
  # ## レベル見出し配下を ## レベル終端で切る場合、両方とも /^## / にマッチするため
  # 見出し行だけが抽出されて本文が落ちる。フラグ方式で修正。
  PREFS=$(awk '
    /^## (好み|判断基準|制約|要件|loyalty)/ {p=1; print; next}
    /^## / && p {p=0}
    p
  ' "$PROJ/profile/preferences.md" 2>/dev/null | head -120)
fi
[ -z "$PREFS" ] && PREFS="(no preferences extracted)"

RESOURCES=""
if [ -f "$PROJ/profile/resources.md" ]; then
  RESOURCES=$(awk '
    /^## (予算|残高|利用可能|inventory|期限)/ {p=1; print; next}
    /^## / && p {p=0}
    p
  ' "$PROJ/profile/resources.md" 2>/dev/null | head -200)
fi
[ -z "$RESOURCES" ] && RESOURCES="(no resources extracted)"

# ──────────────────────────────────────────────
# ③ 学習層：learnings の見出しインデックス
# 全文ではなく見出しのみで「該当する罠を覚えている」を Claude に判断させる
# ──────────────────────────────────────────────
LEARNINGS_INDEX=""
if [ -f "$PROJ/learnings/insights.md" ]; then
  LEARNINGS_INDEX=$(grep -h '^### ' "$PROJ/learnings/insights.md" 2>/dev/null | head -50)
fi
[ -z "$LEARNINGS_INDEX" ] && LEARNINGS_INDEX="(no learnings index)"

# ──────────────────────────────────────────────
# ④ 除外層：既消化アイテム（ドメイン依存・任意）
# パスは派生リポで適宜変更：destinations/visited/ / projects/done/ / books/read/ 等
# ──────────────────────────────────────────────
VISITED=""
for visited_dir in destinations/visited projects/done books/read episodes/resolved; do
  if [ -d "$PROJ/$visited_dir" ]; then
    VISITED+=$(cat "$PROJ/$visited_dir"/*.md 2>/dev/null | head -120)
  fi
done
[ -z "$VISITED" ] && VISITED="(no exclusion list configured)"

# ──────────────────────────────────────────────
# ⑥ ツール可用性層：実測されたツール疎通テーブル
# .claude/hooks/session-start-tool-probe.sh が 24h キャッシュ付きで stdout に出す
# ──────────────────────────────────────────────
TOOL_AVAILABILITY=""
TOOL_PROBE_HOOK="$PROJ/.claude/hooks/session-start-tool-probe.sh"
if [ -x "$TOOL_PROBE_HOOK" ]; then
  TOOL_AVAILABILITY=$(bash "$TOOL_PROBE_HOOK" 2>/dev/null || true)
fi
[ -z "$TOOL_AVAILABILITY" ] && TOOL_AVAILABILITY="(tool availability probe unavailable)"

# ──────────────────────────────────────────────
# JSON 出力（jq が無い環境でも heredoc で対応）
# ──────────────────────────────────────────────
build_context() {
  printf '=== Current JST Time ===\n%s\n\n' "$JST_NOW"
  printf '=== Active Context (state) ===\n%s\n\n' "$STATE"
  printf '=== Profile Preferences (must-haves) ===\n%s\n\n' "$PREFS"
  printf '=== Resources Inventory ===\n%s\n\n' "$RESOURCES"
  printf '=== Learnings Index (見出し) ===\n%s\n\n' "$LEARNINGS_INDEX"
  printf '=== Visited / Done (除外リスト) ===\n%s\n\n' "$VISITED"
  printf '=== Tool Availability (実測) ===\n%s\n' "$TOOL_AVAILABILITY"
}

CTX=$(build_context)

if command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg ctx "$CTX" \
    '{
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: $ctx
      }
    }'
else
  # heredoc fallback: " と \ を最低限エスケープ
  esc_ctx=$(printf '%s' "$CTX" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' '\f' | sed 's/\f/\\n/g')
  cat <<JSON
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"${esc_ctx}"}}
JSON
fi

exit 0
