#!/bin/bash
# Claude Code PreToolUse フック
# 保護対象ファイルへの Edit/Write をブロックする

PROTECTED_FILES=(
  "CLAUDE.md"
  ".claude/settings.json"
  ".claude/hooks/"
)

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

for pattern in "${PROTECTED_FILES[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "ブロック: $FILE_PATH は保護対象ファイルです。変更には管理者の承認が必要です。" >&2
    exit 2
  fi
done

exit 0
