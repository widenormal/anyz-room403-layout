#!/bin/bash
# Claude Code PreToolUse フック
# 個人情報パターンを含む書き込みをブロックする

INPUT=$(cat)
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

if [ -z "$CONTENT" ]; then
  exit 0
fi

# 電話番号パターン（日本）
if echo "$CONTENT" | grep -qP '0[0-9]{1,4}-[0-9]{1,4}-[0-9]{4}'; then
  echo "ブロック: 電話番号と思われるパターンが含まれています。個人情報の記載は禁止です。" >&2
  exit 2
fi

# メールアドレスパターン（社内ドメイン以外）
if echo "$CONTENT" | grep -qP '[a-zA-Z0-9._%+-]+@(?!5inc\.jp)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'; then
  echo "警告: 外部メールアドレスが含まれています。個人情報でないか確認してください。" >&2
  # 警告のみ（exit 0）— 厳格にする場合は exit 2 に変更
  exit 0
fi

# マイナンバー（12桁数字）
if echo "$CONTENT" | grep -qP '\b[0-9]{12}\b'; then
  echo "ブロック: マイナンバーと思われる12桁の数字が含まれています。" >&2
  exit 2
fi

# クレジットカード番号（16桁）
if echo "$CONTENT" | grep -qP '\b[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}\b'; then
  echo "ブロック: クレジットカード番号と思われるパターンが含まれています。" >&2
  exit 2
fi

exit 0
