#!/bin/bash
# Claude Code PreToolUse フック
# 個人情報パターンを含む書き込みをブロックする

INPUT=$(cat)
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

if [ -z "$CONTENT" ]; then
  exit 0
fi

# 電話番号ブロックは撤去（2026-07-06・管理者承認）:
# 店舗・施設の代表番号は公開情報であり、派生リポの中核ルール（ゴルフ3点リンク・
# レストラン4点情報の tel: 必須）と矛盾していた。正規表現で個人携帯と店舗番号は
# 判別不能のため撤去。真の PII（マイナンバー12桁・クレカ16桁）のブロックは維持。

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
