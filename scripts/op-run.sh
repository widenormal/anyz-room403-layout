#!/bin/bash
# op-run.sh — secrets.map の参照を解決し、secret を **メモリ注入のみ**でコマンド実行する。
#
# Codex レビュー Go 条件: 平文 .env をファイル化しない。
#   本ラッパーは gen-env-ref.sh で「ID 参照テンプレ（非 secret）」を一時生成し、
#   `op run --env-file` で子プロセス env に直接注入する。解決済み secret はディスクに書かない。
#   一時ファイルは参照のみ（非 secret）だが、$HOME/$TMPDIR 配下で chmod 600・trap で必ず削除。
#   ※ Drive 同期フォルダ配下では実行しないこと（秘匿構成情報・op キャッシュ拡散防止）。
#
# 使い方:
#   bash scripts/op-run.sh -- printenv GEMINI_API_KEY        # （値はマスク非対象なので本番では出さない）
#   bash scripts/op-run.sh -- python app.py
#   bash scripts/op-run.sh --map other.map -- ./task.sh
#
# 必須: OP_SERVICE_ACCOUNT_TOKEN（env）/ op CLI / jq

set -uo pipefail

MAP_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --) shift; break ;;
    --map) MAP_ARGS+=(--map "${2:?}"); shift 2 ;;
    --strict) MAP_ARGS+=(--strict); shift ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "不明な引数: $1（コマンドは -- の後ろに）" >&2; exit 1 ;;
  esac
done
[ $# -gt 0 ] || { echo "使い方: bash scripts/op-run.sh [--map M] [--strict] -- <command...>" >&2; exit 1; }

HERE="$(cd "$(dirname "$0")" && pwd)"

# 一時ファイルは TMPDIR（既定 /tmp、$HOME 系）配下。Drive 同期パスを避ける。
REF_FILE="$(mktemp "${TMPDIR:-/tmp}/op-ref.XXXXXX.env")"
chmod 600 "$REF_FILE"
cleanup() { rm -f "$REF_FILE"; }
trap cleanup EXIT INT TERM

if ! bash "$HERE/gen-env-ref.sh" "${MAP_ARGS[@]}" > "$REF_FILE" 2>/tmp/op-run.gen.err; then
  echo "ERROR: 参照生成に失敗:" >&2; cat /tmp/op-run.gen.err >&2; exit 1
fi
# 生成器の警告(SKIP 等)は通す
grep -E '^# SKIP|^ERROR' /tmp/op-run.gen.err >&2 2>/dev/null || true

exec op run --env-file="$REF_FILE" -- "$@"
