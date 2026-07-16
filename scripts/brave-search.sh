#!/bin/bash
# Brave Search API ラッパー（リンク検索の第一選択）
#
# 用途: URL・情報の所在を速く安く特定する生リンク検索（無料枠 月2,000クエリ）。
#       出典付きの要約調査は openrouter-call.sh --online / gemini-call.sh を使う。
#
# 認証の自動判定:
#   1. BRAVE_API_KEY 設定済 → そのまま実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op item get 'Brave Search API Key' で取得
#   3. どちらも未設定 → 3段階診断を出して終了
#
# 使い方:
#   bash scripts/brave-search.sh "検索クエリ" [-n 件数(既定5・最大20)]

set -euo pipefail

VAULT="claude-code-secrets"
ITEM="Brave Search API Key"

QUERY=""
COUNT=5
while [ $# -gt 0 ]; do
  case "$1" in
    -n) COUNT="$2"; shift 2 ;;
    *) QUERY="$1"; shift ;;
  esac
done
if [ -z "$QUERY" ]; then
  echo "ERROR: 検索クエリを渡してください（例: brave-search.sh \"5co CI kit\" -n 10）" >&2; exit 2
fi

diag_and_die() {
  {
    echo "ERROR: Brave Search 認証取得失敗（3段階診断）"
    echo "  - op CLI:                  $(command -v op >/dev/null 2>&1 && echo ✅ || echo ❌)"
    echo "  - OP_SERVICE_ACCOUNT_TOKEN: $([ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && echo ✅ || echo ❌)"
    echo "  - op whoami:               $(op whoami >/dev/null 2>&1 && echo ✅ || echo ❌)"
    echo "対応: 全部 ✅ なら vault の '${ITEM}' の credential field を確認、"
    echo "      または BRAVE_API_KEY を直接 export して呼ぶ"
  } >&2
  exit 1
}

if [ -z "${BRAVE_API_KEY:-}" ]; then
  if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
    K="$(op item get "$ITEM" --vault "$VAULT" --fields credential --reveal 2>/dev/null || true)"
    [ -n "$K" ] && export BRAVE_API_KEY="$K"
  fi
  [ -z "${BRAVE_API_KEY:-}" ] && diag_and_die
fi

python3 - "$QUERY" "$COUNT" <<'PYEOF'
import json, os, sys, urllib.parse, urllib.request

query, count = sys.argv[1], min(int(sys.argv[2]), 20)
url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(
    {"q": query, "count": count}
)
req = urllib.request.Request(url, headers={
    "X-Subscription-Token": os.environ["BRAVE_API_KEY"],
    "Accept": "application/json",
})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
except urllib.error.HTTPError as e:
    sys.stderr.write(f"ERROR: Brave HTTP {e.code}: {e.read().decode()[:300]}\n")
    sys.exit(1)

results = (body.get("web") or {}).get("results") or []
if not results:
    print("(検索結果なし)")
for i, res in enumerate(results, 1):
    print(f"{i}. {res.get('title', '')}")
    print(f"   {res.get('url', '')}")
    desc = (res.get("description") or "").replace("<strong>", "").replace("</strong>", "")
    if desc:
        print(f"   {desc[:160]}")
PYEOF
