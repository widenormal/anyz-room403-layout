#!/bin/bash
# OpenRouter 呼び出しラッパー（マルチモデル・課金一元化）
#
# 用途: 出典付きWeb調査の第一選択。`--online` でモデル名に `:online` を付与し
#       OpenRouter の Web 検索（Exa ベース）でグラウンディングする。
#       Google 検索グラウンディングが必要な調査のみ gemini-call.sh を使う。
#
# 認証の自動判定（gemini-call.sh と同方式）:
#   1. OPENROUTER_API_KEY 設定済 → そのまま実行
#   2. OP_SERVICE_ACCOUNT_TOKEN 設定済 → op item get で vault から取得
#      （候補 title を順に試す: 括弧入り title は op read 不可・op item get は可）
#   3. どちらも未設定 → 3段階診断を出して終了
#
# 使い方:
#   bash scripts/openrouter-call.sh -p "調べたいクエリ" [--online] [-m <model>]
#   echo "長い入力" | bash scripts/openrouter-call.sh --online
#
# 既定モデル: google/gemini-2.5-flash（OPENROUTER_MODEL で変更可）

set -euo pipefail

VAULT="claude-code-secrets"
ITEM_CANDIDATES=("OpenRouter Fusion" "OpenRouter API Key (Template)" "OpenRouter API Key" "OpenRouter")

# モデル既定値は llm-models.conf（正データ・申請制で自動更新）から解決
_CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/llm-models.conf"
[ -f "$_CONF" ] && . "$_CONF"
MODEL="${OPENROUTER_MODEL:-${OPENROUTER_DEFAULT_MODEL:-google/gemini-2.5-flash}}"
ONLINE=0
PROMPT=""

while [ $# -gt 0 ]; do
  case "$1" in
    -p) PROMPT="$2"; shift 2 ;;
    -m) MODEL="$2"; shift 2 ;;
    --online) ONLINE=1; shift ;;
    *) echo "ERROR: 不明な引数 $1（-p/-m/--online）" >&2; exit 2 ;;
  esac
done
[ -z "$PROMPT" ] && [ ! -t 0 ] && PROMPT="$(cat)"
if [ -z "$PROMPT" ]; then
  echo "ERROR: -p \"クエリ\" か stdin で入力を渡してください" >&2; exit 2
fi

diag_and_die() {
  {
    echo "ERROR: OpenRouter 認証取得失敗（3段階診断）"
    echo "  - op CLI:                  $(command -v op >/dev/null 2>&1 && echo ✅ || echo ❌)"
    echo "  - OP_SERVICE_ACCOUNT_TOKEN: $([ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && echo ✅ || echo ❌)"
    echo "  - op whoami:               $(op whoami >/dev/null 2>&1 && echo ✅ || echo ❌)"
    echo "  - 試行した item title:      ${ITEM_CANDIDATES[*]}"
    echo "対応: 全部 ✅ なら vault の item title を確認し ITEM_CANDIDATES に追加、"
    echo "      または OPENROUTER_API_KEY を直接 export して呼ぶ"
  } >&2
  exit 1
}

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && command -v op >/dev/null 2>&1; then
    for item in "${ITEM_CANDIDATES[@]}"; do
      K="$(op item get "$item" --vault "$VAULT" --fields credential --reveal 2>/dev/null || true)"
      [ -n "$K" ] && { export OPENROUTER_API_KEY="$K"; break; }
    done
  fi
  [ -z "${OPENROUTER_API_KEY:-}" ] && diag_and_die
fi

[ "$ONLINE" = 1 ] && MODEL="${MODEL}:online"

# JSON エスケープは python に任せる（jq 非依存）
python3 - "$MODEL" "$PROMPT" <<'PYEOF'
import json, os, sys, urllib.request

model, prompt = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
    },
)
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.load(r)
except urllib.error.HTTPError as e:
    sys.stderr.write(f"ERROR: OpenRouter HTTP {e.code}: {e.read().decode()[:500]}\n")
    sys.exit(1)

choice = body["choices"][0]["message"]
print(choice.get("content") or "")
# :online の出典 URL（annotations）があれば末尾に列挙
for ann in choice.get("annotations") or []:
    url = (ann.get("url_citation") or {}).get("url")
    if url:
        print(f"[source] {url}")
PYEOF
