#!/bin/bash
# Claude Code PreToolUse フック (Bash ツール用)
# Bash コマンドによる保護対象ファイルの変更・削除をブロックする

PROTECTED_FILES=(
  "CLAUDE.md"
  ".claude/settings.json"
  ".claude/hooks/"
)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# 破壊的コマンドパターン（読み取り専用コマンドは許可）
DESTRUCTIVE='(sed\s+-i|awk\s.*-i\s|rm\s|rm$|mv\s|truncate|dd\s|tee\s|>\s|>$|>>|chmod|chown|cp\s.*>\s|echo\s.*>\s|cat\s.*>\s|perl\s+-.*-i)'

for pattern in "${PROTECTED_FILES[@]}"; do
  if echo "$COMMAND" | grep -q "$pattern"; then
    if echo "$COMMAND" | grep -qE "$DESTRUCTIVE"; then
      echo "ブロック: Bash 経由での保護対象ファイル ($pattern) の変更・削除は禁止されています。Edit/Write ツールと同様、管理者の承認が必要です。" >&2
      exit 2
    fi
  fi
done

exit 0
