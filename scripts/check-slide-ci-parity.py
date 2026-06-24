#!/usr/bin/env python3
"""
check-slide-ci-parity.py — SLIDE 成果物 ⇔ 5co CI v2 トークンのパリティ検査

目的: デザインドリフト（2026-06-24 の SLIDE.md「古い見た目」事故）の再発防止。
SLIDE.md / sample.html が CI v2 の正データから乖離していないかを機械照合する。

検査するドリフトの型（過去に実際に起きたもの）:
  - 矩形が A4 でない（16:9 / 1280x720 の混入）
  - 廃止トークン名の混入（--ice / --powder / --navy）
  - パレット外の色（グレー・#000・他色相）
  - 旧 hex（#0E1A38 / #A9CFDF）の混入
  - 書体スタックに Georgia フォールバック（数表崩れの原因）

正データ（CI v2・実納品デッキ準拠）:
  palette = 白 #FFFFFF / クリスタル #C3D7EE / 墨 #101820 + ティント #DEE9F6 #F0F5FB
  geometry = A4 landscape 297mm x 210mm
  token names = --crystal / --ink（青は --crystal が正）
  fonts = Hiragino Mincho ProN / EB Garamond（Georgia フォールバック禁止）

使い方:
  python3 scripts/check-slide-ci-parity.py            # 既定対象を検査
  python3 scripts/check-slide-ci-parity.py <file ...> # 任意の HTML/MD を検査
終了コード: 0=適合 / 1=ドリフト検出（CI/pre-commit で落とせる）
"""
import sys, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- CI v2 正データ（ここが唯一の宣言。変えるときは実納品デッキに合わせる） ----
PALETTE = {"#FFFFFF", "#C3D7EE", "#101820", "#DEE9F6", "#F0F5FB"}
DEPRECATED_TOKENS = ["--ice", "--powder", "--navy"]      # 廃止された変数名
DEPRECATED_HEX = ["#0E1A38", "#A9CFDF"]                  # 旧 CI の色
A4 = ("297mm", "210mm")

DEFAULT_TARGETS = [
    "docs/SLIDE-md/SLIDE-md-5co/sample.html",
    "docs/SLIDE-md/SLIDE-md-5co/SLIDE.md",
]

def strip_base64(t):
    # 埋め込み画像/フォントの base64 は誤検知の元なので除去
    return re.sub(r'base64,[A-Za-z0-9+/=\s]+', 'base64,', t)

def check_html(path, t):
    issues = []
    # 1) A4 幾何（.slide の width/height）
    m = re.search(r'\.slide\s*\{[^}]*?width:\s*([0-9.]+(?:mm|px))\s*;\s*height:\s*([0-9.]+(?:mm|px))', t)
    if m:
        if (m.group(1), m.group(2)) != A4:
            issues.append(f"矩形が A4 でない: .slide = {m.group(1)} x {m.group(2)}（正: 297mm x 210mm）")
    elif "1280px" in t or "720px" in t:
        issues.append("16:9 由来の寸法（1280px/720px）を検出")
    # 2) 廃止トークン名
    for tok in DEPRECATED_TOKENS:
        if re.search(re.escape(tok) + r'\b', t):
            issues.append(f"廃止トークン名 {tok} を使用（正: --crystal / --ink）")
    # 3) 旧 hex
    for h in DEPRECATED_HEX:
        if h.lower() in t.lower():
            issues.append(f"旧 CI の色 {h} を検出")
    # 4) パレット外の色（markup/style 中の #rrggbb のみ・base64除去後）
    hexes = set(x.upper() for x in re.findall(r'#[0-9A-Fa-f]{6}', t))
    extra = hexes - PALETTE
    if extra:
        issues.append(f"パレット外の色: {', '.join(sorted(extra))}（許可: {', '.join(sorted(PALETTE))}）")
    # 5) Georgia フォールバック
    if re.search(r'Georgia', t):
        issues.append("Georgia フォールバックを検出（数表崩れの原因・禁止）")
    return issues

def check_md(path, t):
    # 仕様書(.md)は本文で廃止トークン/16:9 を「警告として」言及するのが正常なので、
    # 否定検査（〜が無いこと）はせず、正データを正しく宣言しているかの肯定検査のみ行う。
    # 厳密なクリーン検査は成果物(sample.html)側で担保する。
    issues = []
    if "--crystal" not in t:
        issues.append("仕様書に --crystal の宣言が無い（青の正式トークン）")
    if not re.search(r'297\s*mm|A4\s*(横|landscape)', t):
        issues.append("仕様書に A4/297mm の記載が無い（正: A4 横 297x210mm）")
    if not re.search(r'#101820', t):
        issues.append("仕様書に墨 #101820 の宣言が無い")
    return issues

def main():
    targets = sys.argv[1:] or [os.path.join(REPO, p) for p in DEFAULT_TARGETS]
    total = 0
    for path in targets:
        if not os.path.isfile(path):
            print(f"  ! 見つからない: {path}")
            total += 1
            continue
        t = strip_base64(open(path, encoding="utf-8", errors="replace").read())
        issues = check_md(path, t) if path.endswith(".md") else check_html(path, t)
        rel = os.path.relpath(path, REPO)
        if issues:
            print(f"  ✗ {rel}")
            for i in issues:
                print(f"      - {i}")
            total += len(issues)
        else:
            print(f"  ✓ {rel}")
    print()
    if total:
        print(f"NG: {total} 件のドリフトを検出。正データ（CI v2・実納品デッキ）に合わせて是正してください。")
        return 1
    print("OK: SLIDE 成果物は CI v2 トークンに適合しています。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
