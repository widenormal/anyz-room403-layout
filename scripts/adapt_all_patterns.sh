#!/usr/bin/env bash
# 99種の SLIDE-PATTERN を CI v2 化（ci_pattern_adapter.py）し、3色準拠をQAする。
# 生成物は OUT_DIR（既定=一時）へ。リポにはコミットしない＝ソース+アダプタが唯一の正（ドリフト防止）。
# 使い方: adapt_all_patterns.sh [OUT_DIR]
#   --check のみ: 3色（白/crystal/ink/tint）以外の hex 残存をパターン毎に検査し pass/fail を集計。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT/docs/SLIDE-PATTERN"
OUT_DIR="${1:-$(mktemp -d)}"
mkdir -p "$OUT_DIR"
ADAPT="$ROOT/scripts/ci_pattern_adapter.py"
# CI v2 の許容色（3色＋tint＋ink不透明度）。これ以外の hex が残れば fail。
ALLOW='#ffffff|#fff\b|#c3d7ee|#101820|#f0f5fb|#dee9f6'

pass=0; fail=0; fails=()
for d in "$SRC_DIR"/SLIDE-PATTERN-*/; do
  name="$(basename "$d")"
  src="$d/$name.html"
  [ -f "$src" ] || continue
  out="$OUT_DIR/${name#SLIDE-PATTERN-}.ci.html"
  python3 "$ADAPT" "$src" -o "$out" >/dev/null
  # emoji 等の数値文字参照(&#NNNN;)を除去してから hex 色を抽出（偽陽性防止）
  residual="$(sed 's/&#[0-9]*;//g' "$out" | grep -ohiE '#[0-9a-f]{3,6}' | tr 'A-F' 'a-f' | grep -viE "$ALLOW" | sort -u | tr '\n' ' ' || true)"
  if [ -n "$residual" ]; then
    fail=$((fail+1)); fails+=("${name#SLIDE-PATTERN-}: $residual")
  else
    pass=$((pass+1))
  fi
done

echo "=== CI v2 化 3色QA: pass=$pass fail=$fail / 計 $((pass+fail)) ==="
echo "OUT_DIR=$OUT_DIR"
if [ "$fail" -gt 0 ]; then
  echo "--- 残存非CI色のあるパターン ---"
  printf '%s\n' "${fails[@]}"
fi
