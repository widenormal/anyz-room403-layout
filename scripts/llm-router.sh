#!/bin/bash
# LLM ルーター: タスク内容と環境から最も「エコ」な呼び先を決定する。
#
# 役割分担:
#   qwen   = 軽処理（要約、分類、フォーマット変換、プロンプトドラフト）。ローカル無料
#   haiku  = qwen で対応不能なテキスト処理。Claude Haiku 4.5 で安価
#   grok   = X(Twitter) 検索・トレンド・リアルタイム情報
#   codex  = 戦略判断・コードレビュー（GPT-5 系のセカンドオピニオン）
#   gemini = 別バイアスのレビュー・画像/マルチモーダル
#   claude = デフォルト（オーケストレーション・複雑実装）
#
# 発火条件:
#   ECO_MODE=1 が立っているとき、または DRIVE_CONTEXT=1 のとき、
#   軽処理は qwen→haiku に強制ルーティングする。
#
# 使い方:
#   bash scripts/llm-router.sh --task "X で AI 業界の最新トレンドを拾って"
#   bash scripts/llm-router.sh --task "この PR の設計をレビュー" --tokens 8000
#   bash scripts/llm-router.sh --task "Drive のフォルダ要約" --drive
#
# 出力形式（stdout、1 行）:
#   <llm>\t<reason>
# 例:
#   grok\tX/Twitter キーワード検出
#   qwen\tECO_MODE 中の軽処理 (~800 tokens)

set -euo pipefail

TASK=""
TOKENS=0
DRIVE=0
PURPOSE=""
JSON_OUT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --task) TASK="${2:-}"; shift 2 ;;
    --tokens) TOKENS="${2:-0}"; shift 2 ;;
    --drive) DRIVE=1; shift ;;
    --purpose) PURPOSE="${2:-}"; shift 2 ;;
    --json) JSON_OUT=1; shift ;;
    -h|--help)
      sed -n '2,30p' "$0"
      exit 0
      ;;
    *) shift ;;
  esac
done

# 環境からの ECO 判定
ECO="${ECO_MODE:-0}"
if [ "${DRIVE_CONTEXT:-0}" = "1" ] || [ "$DRIVE" = "1" ]; then
  ECO=1
fi

# キーワードルール（小文字化して判定）
LC_TASK="$(printf '%s' "$TASK $PURPOSE" | tr '[:upper:]' '[:lower:]')"

decide() {
  local llm="$1"; local reason="$2"
  if [ "$JSON_OUT" = "1" ]; then
    printf '{"llm":"%s","reason":"%s","eco_mode":%s}\n' "$llm" "$reason" "$ECO"
  else
    printf '%s\t%s\n' "$llm" "$reason"
  fi
  exit 0
}

# 1. 用途が明示されている場合は最優先
case "$PURPOSE" in
  x-search|twitter|trend) decide grok "purpose=$PURPOSE" ;;
  review|judge|opinion|strategy) decide codex "purpose=$PURPOSE" ;;
  second-opinion|design|image|multimodal) decide gemini "purpose=$PURPOSE" ;;
  drive-summary|drive-list|drive-classify) decide qwen "purpose=$PURPOSE (Drive eco)" ;;
  code-implement|orchestrate) decide claude "purpose=$PURPOSE" ;;
esac

# 2. キーワード検出
case "$LC_TASK" in
  *"x で"*|*"twitter"*|*" x "*|*"x投稿"*|*"トレンド"*|*"リアルタイム"*|*"バズ"*)
    decide grok "X/Twitter キーワード検出"
    ;;
  *"レビュー"*|*"セカンドオピニオン"*|*"これでいいか"*|*"判断"*|*"戦略"*)
    if [ "$ECO" = "1" ]; then
      decide gemini "ECO中: codex の代わりに gemini で代替（非有料の場合あり）"
    fi
    decide codex "判断・レビュー系"
    ;;
  *"画像"*|*"デザイン"*|*"マルチモーダル"*|*"og:image"*)
    decide gemini "マルチモーダル系"
    ;;
  *"要約"*|*"分類"*|*"整形"*|*"フォーマット変換"*|*"プロンプト"*"ドラフト"*)
    decide qwen "軽処理キーワード検出"
    ;;
esac

# 3. ECO_MODE / Drive 文脈下では軽処理を qwen→haiku に倒す
if [ "$ECO" = "1" ]; then
  if [ "$TOKENS" -le 2000 ]; then
    decide qwen "ECO_MODE 中の軽処理 (~${TOKENS} tokens)"
  else
    decide haiku "ECO_MODE 中の中規模処理 (~${TOKENS} tokens)"
  fi
fi

# 4. 通常モードのトークン量ヒューリスティクス
if [ "$TOKENS" -gt 0 ] && [ "$TOKENS" -le 1500 ]; then
  decide qwen "短文タスク (~${TOKENS} tokens)"
fi

# 5. デフォルト
decide claude "デフォルト（オーケストレーション）"
