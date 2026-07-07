#!/bin/bash
# Claude Code PreToolUse フック
# Google Drive MCP ツール（list_recent_files / search_files / read_file_content /
# download_file_content / get_file_metadata / get_file_permissions / copy_file / create_file）
# が呼ばれた瞬間に、ECO_MODE=1 相当の運用へ Claude を誘導する。
#
# 目的:
#   Drive 共有フォルダは多人数が利用するため、
#   - 大きなファイルを丸ごと Claude のコンテキストに読み込ませてトークンを浪費するのを防ぐ
#   - 要約・分類は scripts/qwen-call.sh（ローカル無料）に倒す
#   - 既定で「軽量モデル経由で処理」する旨を Claude に明示する
#
# 動作:
#   - 終了コード 0 で常に通す（ブロックはしない）
#   - stderr に運用ガイドを出して Claude にエコ運用を選ばせる
#   - download_file_content / read_file_content では警告レベルを強める

set -u

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
FILE_ID="$(echo "$INPUT" | jq -r '.tool_input.file_id // .tool_input.fileId // empty')"
QUERY="$(echo "$INPUT" | jq -r '.tool_input.query // empty')"

# Drive MCP 以外は素通り
case "$TOOL_NAME" in
  mcp__*__list_recent_files|\
  mcp__*__search_files|\
  mcp__*__read_file_content|\
  mcp__*__download_file_content|\
  mcp__*__get_file_metadata|\
  mcp__*__get_file_permissions|\
  mcp__*__copy_file|\
  mcp__*__create_file)
    ;;
  *)
    exit 0
    ;;
esac

case "$TOOL_NAME" in
  *download_file_content|*read_file_content)
    SEVERITY="strong"
    ;;
  *)
    SEVERITY="info"
    ;;
esac

cat >&2 <<EOF
[eco-mode-drive] Drive 共有フォルダ操作を検知しました（tool=${TOOL_NAME}）。
                 ECO_MODE=1 相当の運用に切り替えてください。

  推奨ワークフロー:
    1. Drive ツールでファイル一覧/メタデータだけ取得
    2. 内容の要約・分類は \`bash scripts/qwen-call.sh --task summarize\` でローカル処理
    3. それでも要判断の部分のみ Claude/Codex に渡す

  禁止事項:
    - download_file_content の結果を Claude に丸ごと渡す（数万トークン浪費）
    - 1 セッション内で 10 ファイル以上を Claude のコンテキストに展開する
EOF

if [ "$SEVERITY" = "strong" ]; then
  cat >&2 <<EOF

  ⚠️ このツールはファイル本文を取得します。
     大きなファイルなら必ず qwen で要約してから Claude に渡してください。
     ECO_MODE=1 として今後の処理を進めてください。
EOF
fi

if [ -n "$QUERY" ]; then
  echo "  検索クエリ: $QUERY" >&2
fi
if [ -n "$FILE_ID" ]; then
  echo "  対象 file_id: $FILE_ID" >&2
fi

exit 0
