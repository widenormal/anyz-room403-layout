#!/bin/bash
# x-search.sh — X(Twitter) API v2 直叩きラッパー（構造化 API・R2 原則）
#
# xAI(Grok) を経由せず X のデータを直接取得する。「目」役の実データ部分を担う。
# クレジット不要（X API の Bearer Token のみ）。要約・解釈が必要な場合は
# 取得結果を grok-call.sh / openrouter-call.sh 等に渡す2段構成で使う。
#
# 使い方:
#   bash scripts/x-search.sh "claude code" -n 10        # 直近7日の検索
#   bash scripts/x-search.sh --tweet 2076605444819390743  # ポスト全文（X Articles 本文含む）
#   bash scripts/x-search.sh "query" --raw               # 生 JSON
#
# 認証: X_BEARER_TOKEN（env）または 1Password「X Bearer Token」（op item get）。
# 注意: 検索のレート上限は X API のプラン依存（未計測）。429 が続く場合は
#       プラン確認 or xAI 直経路（grok-call.sh）の復活を検討する。
#
# 2026-07-14 実測: search/recent・tweets/:id（article.plain_text）とも
# vault の Bearer Token で HTTP 200 を確認済み。

set -euo pipefail

QUERY=""
TWEET_ID=""
MAX=10
RAW=0

while [ $# -gt 0 ]; do
  case "$1" in
    --tweet) TWEET_ID="${2:-}"; shift 2 ;;
    -n) MAX="${2:-10}"; shift 2 ;;
    --raw) RAW=1; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) QUERY="${QUERY}${QUERY:+ }$1"; shift ;;
  esac
done

if [ -z "$QUERY" ] && [ -z "$TWEET_ID" ]; then
  echo "ERROR: 検索クエリ か --tweet <id> を指定してください" >&2
  exit 1
fi

# ── Bearer Token 解決（env > op） ──
if [ -z "${X_BEARER_TOKEN:-}" ]; then
  if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
    X_BEARER_TOKEN="$(op item get 'X Bearer Token' --vault claude-code-secrets --fields credential --reveal 2>/dev/null || true)"
  fi
fi
if [ -z "${X_BEARER_TOKEN:-}" ]; then
  echo "ERROR: X_BEARER_TOKEN を解決できません（env か 1Password「X Bearer Token」）" >&2
  exit 1
fi

api_get() {
  local url="$1" out http
  out="$(mktemp)"
  http="$(curl -sS -o "$out" -w '%{http_code}' "$url" \
    -H "Authorization: Bearer $X_BEARER_TOKEN" || echo 000)"
  if [ "$http" != "200" ]; then
    echo "ERROR: X API HTTP $http" >&2
    head -c 300 "$out" >&2; echo >&2
    rm -f "$out"
    [ "$http" = "429" ] && echo "HINT: レート上限。時間を置くかプランを確認" >&2
    exit 1
  fi
  cat "$out"
  rm -f "$out"
}

if [ -n "$TWEET_ID" ]; then
  # ── 単一ポスト取得（長文 note・X Articles 本文込み） ──
  URL="https://api.x.com/2/tweets/${TWEET_ID}?tweet.fields=created_at,public_metrics,note_tweet,article&expansions=author_id&user.fields=name,username"
  RES="$(api_get "$URL")"
  if [ "$RAW" = 1 ]; then echo "$RES"; exit 0; fi
  python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
t = d.get('data', {})
u = (d.get('includes', {}).get('users') or [{}])[0]
m = t.get('public_metrics', {})
print(f\"@{u.get('username','?')} ({u.get('name','')}) {t.get('created_at','')} ♡{m.get('like_count',0)} RT{m.get('retweet_count',0)}\")
print(f\"https://x.com/{u.get('username','i')}/status/{t.get('id','')}\")
print()
print(t.get('text', ''))
nt = t.get('note_tweet', {})
if nt.get('text'):
    print('\n--- NOTE（長文本文） ---')
    print(nt['text'])
a = t.get('article', {})
if a:
    print(f\"\n--- ARTICLE: {a.get('title','')} ---\")
    print(a.get('plain_text', a.get('preview_text', '')))
" <<<"$RES"
else
  # ── 直近7日の検索 ──
  ENC="$(python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$QUERY")"
  [ "$MAX" -lt 10 ] && MAX=10
  [ "$MAX" -gt 100 ] && MAX=100
  URL="https://api.x.com/2/tweets/search/recent?query=${ENC}&max_results=${MAX}&tweet.fields=created_at,public_metrics&expansions=author_id&user.fields=name,username"
  RES="$(api_get "$URL")"
  if [ "$RAW" = 1 ]; then echo "$RES"; exit 0; fi
  python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
users = {u['id']: u for u in d.get('includes', {}).get('users', [])}
data = d.get('data', [])
if not data:
    print('（該当なし）')
for i, t in enumerate(data, 1):
    u = users.get(t.get('author_id'), {})
    m = t.get('public_metrics', {})
    print(f\"{i}. @{u.get('username','?')} {t.get('created_at','')[:16]} ♡{m.get('like_count',0)}\")
    print(f\"   {t.get('text','')[:280]}\")
    print(f\"   https://x.com/{u.get('username','i')}/status/{t.get('id','')}\")
" <<<"$RES"
fi

echo "" >&2
echo "[x-search] mode=$([ -n "$TWEET_ID" ] && echo tweet || echo search) $([ -n "$TWEET_ID" ] && echo "id=$TWEET_ID" || echo "q=$QUERY n=$MAX")" >&2
