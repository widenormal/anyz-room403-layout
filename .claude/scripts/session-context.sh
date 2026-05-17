#!/usr/bin/env bash
# session-context.sh: SessionStart hook で 3 層構造の文脈を additionalContext に投入する。
#
# 注入する 3 層（詳細：docs/active-context-template.md）:
#   ① 状態層 — memory/active-context.md（進行中タスク・直近の確定事項）
#   ② 辞書層 — profile/preferences.md / profile/resources.md（"今日のルール"）
#   ③ 学習層 — learnings/insights.md の見出し（過去事例の罠インデックス）
#   ④ 除外層 — destinations/visited/ ほか（既消化アイテム・ドメイン依存・任意）
#
# 失敗時もセッション起動を妨げないため exit 0 で抜ける。

set -u

PROJ="${CLAUDE_PROJECT_DIR:-.}"
JST_NOW=$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M (%a) JST')

# ──────────────────────────────────────────────
# ① 状態層：active-context（単一ファイル形式 + 1人1ファイル形式の両対応）
# ──────────────────────────────────────────────
ACTIVE_CONTEXT=""
if [ -f "$PROJ/memory/active-context.md" ]; then
  ACTIVE_CONTEXT=$(cat "$PROJ/memory/active-context.md")
fi

PER_PERSON=""
if [ -d "$PROJ/memory/active-context" ]; then
  for f in "$PROJ/memory/active-context"/*.md; do
    case "$(basename "$f")" in
      _*) ;;  # _README.md, _template.md 等の運用ルール文書は除外
      *)
        [ -f "$f" ] && PER_PERSON+=$'\n\n--- '"$(basename "$f")"$' ---\n'"$(cat "$f")"
        ;;
    esac
  done
fi

STATE="${ACTIVE_CONTEXT}${PER_PERSON}"
[ -z "$STATE" ] && STATE="(no active-context found)"

# ──────────────────────────────────────────────
# ② 辞書層：プロファイル（好み・残高・期限）
# section 名は派生リポの実ファイルに合わせて書き換える
# ──────────────────────────────────────────────
PREFS=""
if [ -f "$PROJ/profile/preferences.md" ]; then
  PREFS=$(awk '/^## (好み|判断基準|制約|要件|loyalty)/,/^## /' \
            "$PROJ/profile/preferences.md" 2>/dev/null | head -80)
fi
[ -z "$PREFS" ] && PREFS="(no preferences extracted)"

RESOURCES=""
if [ -f "$PROJ/profile/resources.md" ]; then
  RESOURCES=$(awk '/^## (予算|残高|利用可能|inventory|期限)/,/^## /' \
                "$PROJ/profile/resources.md" 2>/dev/null | head -40)
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
# JSON 出力（jq が無い環境でも heredoc で対応）
# ──────────────────────────────────────────────
build_context() {
  printf '=== Current JST Time ===\n%s\n\n' "$JST_NOW"
  printf '=== Active Context (state) ===\n%s\n\n' "$STATE"
  printf '=== Profile Preferences (must-haves) ===\n%s\n\n' "$PREFS"
  printf '=== Resources Inventory ===\n%s\n\n' "$RESOURCES"
  printf '=== Learnings Index (見出し) ===\n%s\n\n' "$LEARNINGS_INDEX"
  printf '=== Visited / Done (除外リスト) ===\n%s\n' "$VISITED"
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
