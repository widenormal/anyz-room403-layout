#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SLIDE-PATTERN(16:9/グレー/sans) → CI v2(A4横/3色/φ) アダプタ。

docs/SLIDE-PATTERN-CI-ADAPTER-SPEC.md を唯一の正として、パターンHTMLを CI v2 へ機械変換する。
- 配色: グレー階調 → ink/crystal/tint トークン（仕様§3）
- タイポ: sans-serif → 和文ヒラギノ明朝/欧文 EB Garamond（仕様§4）
- アスペクト: body を A4 ページ化し、960×540 の .slide を内容幅へ幅合わせ scale、余りを什器帯に（仕様§5）
- 什器: 隅ロゴ(64px・プレースホルダ)＋ CONFIDENTIAL フッター（仕様§6）

使い方: ci_pattern_adapter.py <pattern.html> -o <out.html>
"""
from __future__ import annotations
import argparse, re, pathlib

# 仕様§3 配色マッピング: グレー(R≈G≈B)を輝度バケットで CI トークンへ畳む（enumerate せず汎用）。
# 文字色は ink/ink-60（CIはグレー文字禁止）、面・罫線は crystal 階調 or ink。emoji 実体参照(&#NNNN;)は除外。
_HEX_ANY = re.compile(r"(?<![&\w])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_grey(r: int, g: int, b: int) -> bool:
    return max(r, g, b) - min(r, g, b) <= 20


def _bucket_surface(lum: int) -> str:
    if lum >= 240: return "#F0F5FB"             # crystal-25
    if lum >= 208: return "#DEE9F6"             # crystal-55
    if lum >= 160: return "#C3D7EE"             # crystal
    if lum >= 90:  return "rgba(16,24,32,.60)"  # ink-60
    return "#101820"                            # ink


def _bucket_text(lum: int) -> str:
    return "rgba(16,24,32,.60)" if lum >= 120 else "#101820"  # 薄→ink-60 / 濃→ink


def remap_colors(html: str) -> str:
    # 1) color: 文脈のグレー → 文字トークン（可読性優先・グレー文字禁止）
    def repl_color(m):
        r, g, b = _rgb(m.group(2))
        return m.group(1) + _bucket_text((r + g + b) // 3) if _is_grey(r, g, b) else m.group(0)
    html = re.sub(r"(color\s*:\s*)(#[0-9a-fA-F]{3,6})\b", repl_color, html)
    # 2) 残り全 hex のグレー → 面/罫線トークン（背景・border 等）
    def repl_any(m):
        r, g, b = _rgb(m.group(1))
        return _bucket_surface((r + g + b) // 3) if _is_grey(r, g, b) else m.group(0)
    return _HEX_ANY.sub(repl_any, html)


# §4 フォント
SERIF_JA = "'Hiragino Mincho ProN','Yu Mincho',serif"
FONT_MAP = [
    (r"font-family:\s*sans-serif", f"font-family:{SERIF_JA}"),
    (r"'Hiragino Kaku Gothic[^;]*|'Hiragino Sans'[^;]*|Meiryo[^;]*sans-serif", SERIF_JA),
]
# §1/§5 A4 ＋ アスペクト変換 ＋ §6 什器（body を A4 ページ化し .slide を scale）
CI_OVERRIDE = """
<style id="ci-v2-adapter">
:root{ --white:#FFFFFF; --crystal:#C3D7EE; --ink:#101820;
       --crystal-25:#F0F5FB; --crystal-55:#DEE9F6;
       --ink-60:rgba(16,24,32,.60); --ink-14:rgba(16,24,32,.14);
       --serif-ja:'Hiragino Mincho ProN','Yu Mincho',serif;
       --serif-en:'Garamond Premier Pro','EB Garamond','Hiragino Mincho ProN',serif; }
@page{ size:A4 landscape; margin:0; }
html,body{ margin:0; }
.slide-label{ display:none !important; }
/* body = A4 ページ（仕様§1: 297×210mm / padding 16-18-14mm） */
body{ width:297mm; height:210mm; box-sizing:border-box; padding:16mm 18mm 14mm;
      background:var(--white); color:var(--ink); font-family:var(--serif-ja);
      position:relative; overflow:hidden;
      display:flex; align-items:center; justify-content:center;
      -webkit-print-color-adjust:exact; print-color-adjust:exact; }
/* 16:9 の .slide を内容幅へ幅合わせ scale（仕様§5: 261mm/960px≈1.0276）。余りは上下の什器帯に */
.slide{ width:960px !important; height:540px !important;
        transform:scale(1.0276); transform-origin:center center;
        background:transparent !important; border:none !important; box-shadow:none !important;
        overflow:hidden; }
/* §6 什器: 隅ロゴ(64px・プレースホルダ)＋ CONFIDENTIAL フッター */
body::before{ content:'5 co.'; position:absolute; top:8mm; right:9.5mm;
              font-family:var(--serif-en); font-style:italic; font-size:18px; color:var(--ink); }
body::after{ content:'CONFIDENTIAL  —  5 co.'; position:absolute; bottom:5mm; right:9.5mm;
             font-family:var(--serif-en); letter-spacing:.16em; font-size:11px; color:var(--ink-60); }
/* 見出し/タイトル要素は ink に昇格（薄グレーのプレースホルダ見出し対策・仕様§7課題1） */
.slide h1,.slide h2,.slide h3,
.slide [class*="title"],.slide [class*="Title"],.slide [class*="heading"],.slide [class*="headline"]{
  color:var(--ink) !important; }
</style>
"""


def convert(html: str) -> str:
    html = remap_colors(html)
    for pat, rep in FONT_MAP:
        html = re.sub(pat, rep, html, flags=re.I)
    # CI オーバライドを最後に注入（後勝ちで確実に上書き）
    if "</head>" in html:
        html = html.replace("</head>", CI_OVERRIDE + "</head>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", CI_OVERRIDE + "</body>", 1)
    else:
        html += CI_OVERRIDE
    return html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    src = pathlib.Path(a.src)
    out = pathlib.Path(a.out)
    out.write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
