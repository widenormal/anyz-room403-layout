#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
numfield_outline.py — Oracle（numfield）SVG の <text> を *同じフォントのまま* <path> アウトライン化する。

目的（CIスライド表紙 Oracle が非Mac/プレビュー/PDFで消える件の恒久対策・B案=完全忠実）:
  numfield_*.svg は数字を <text font-family='Didot'…> 等のライブテキストで描いており、
  Didot / Bodoni 72 / Hoefler Text / Big Caslon / Cochin / Palatino / Baskerville といった
  Mac 専有フォントが無い環境ではグリフが描画されず Oracle が消える。
  本スクリプトは **実フォントが入っている Mac 上で** 各 <text> を、その font-family の実フォントから
  グリフ輪郭を取り出して <path> 化する。位置・サイズ・回転・数字・塗りは一切変えない＝見た目は不変、
  かつフォント非依存になりどの環境でも同一描画になる。

  ⚠️ 必ず実フォントが存在する Mac で実行すること。フォントが見つからない family があれば既定では
     中断する（--fallback を付けない限り別書体に逃がさない＝作り直しを防ぐ）。

依存: fonttools（`pip install fonttools`）。Python 3.9+。

使い方（Mac のターミナル Claude Code セッション想定）:
  cd <template リポ>
  python3 5co-CI-kit/numfield_outline.py --report          # まず全 family が解決できるか点検
  python3 5co-CI-kit/numfield_outline.py --apply           # SVG6種を path化＋テンプレ dataURI 差し替え
  python3 5co-CI-kit/numfield_outline.py --apply --verify  # 上記＋ <text> 残存ゼロを検査

挙動:
  - 入力: 5co-CI-kit/assets/numfield_*.svg（既定で6種すべて）
  - 出力: 同名で上書き（--apply）。--report/--dry-run は書き込まない。
  - テンプレ: 5co-CI-kit/5co_slide_template.html の .numfield-full 背景 dataURI を、
    新しい numfield_allover_nuki.svg（path版）の base64 で差し替える。
"""
import argparse
import base64
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
TEMPLATE_HTML = os.path.join(HERE, "5co_slide_template.html")

# Mac の標準フォント探索パス
FONT_DIRS = [
    "/System/Library/Fonts",
    "/System/Library/Fonts/Supplemental",
    "/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
    # 非Mac でテストする時のフォールバック探索先（--font-dir で追加も可）
    "/usr/share/fonts",
]

try:
    from fontTools.ttLib import TTFont, TTCollection, TTLibError
    from fontTools.pens.svgPathPen import SVGPathPen
except Exception as e:  # pragma: no cover
    sys.stderr.write("fonttools が必要です: pip install fonttools\n  詳細: %s\n" % e)
    sys.exit(2)


# ---------- フォント索引 ----------
class FontIndex:
    """family 名 → (TTFont, unitsPerEm) を解決する索引。.ttc/.otf/.ttf 対応。"""

    def __init__(self, extra_dirs=None):
        self._by_family = {}   # lower(family) -> (path, fontNumber)
        self._cache = {}       # (path, fontNumber) -> TTFont
        dirs = list(FONT_DIRS)
        if extra_dirs:
            dirs = list(extra_dirs) + dirs
        for d in dirs:
            if d and os.path.isdir(d):
                self._scan_dir(d)

    def _scan_dir(self, d):
        for root, _dirs, files in os.walk(d):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in (".ttf", ".otf", ".ttc"):
                    continue
                path = os.path.join(root, fn)
                try:
                    if ext == ".ttc":
                        coll = TTCollection(path, lazy=True)
                        for i, f in enumerate(coll.fonts):
                            self._register(f, path, i)
                    else:
                        f = TTFont(path, lazy=True, fontNumber=0)
                        self._register(f, path, 0)
                except Exception:
                    continue

    def _register(self, font, path, num):
        try:
            name = font["name"]
        except Exception:
            return
        fams = set()
        for nid in (16, 1):  # Typographic family, then legacy family
            rec = name.getDebugName(nid)
            if rec:
                fams.add(rec)
        for fam in fams:
            key = fam.strip().lower()
            # 既登録は上書きしない（最初に見つかった=より標準的なパスを優先）
            self._by_family.setdefault(key, (path, num))

    def resolve(self, family):
        key = family.strip().strip('"').strip("'").lower()
        hit = self._by_family.get(key)
        if not hit:
            return None
        if hit not in self._cache:
            path, num = hit
            self._cache[hit] = TTFont(path, fontNumber=num)
        return self._cache[hit]

    def known_families(self):
        return sorted(self._by_family.keys())


def glyph_path_d(font, char):
    """font から char のアウトラインを font 単位（y-up）の SVG path d で返す。advance も返す。"""
    cmap = font.getBestCmap()
    gname = cmap.get(ord(char))
    if not gname:
        return None, None, None
    gset = font.getGlyphSet()
    pen = SVGPathPen(gset)
    gset[gname].draw(pen)
    d = pen.getCommands()
    upm = font["head"].unitsPerEm
    adv = font["hmtx"][gname][0]
    return d, upm, adv


def num(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def convert_svg(in_path, index, fallback, missing):
    """1つの numfield SVG を path 化して文字列を返す。missing には未解決 family を加える。"""
    tree = ET.parse(in_path)
    root = tree.getroot()
    text_tag = f"{{{SVG_NS}}}text"
    # 子要素を走査（numfield は <svg> 直下に <text> が並ぶ素直な構造）
    parent_map = {c: p for p in root.iter() for c in p}
    texts = [el for el in root.iter(text_tag)]
    for el in texts:
        char = (el.text or "").strip()
        if not char:
            continue
        fam = el.get("font-family", "")
        size = num(el.get("font-size"), 0.0)
        x = num(el.get("x"))
        y = num(el.get("y"))
        anchor = (el.get("text-anchor") or "start").strip()
        fill = el.get("fill", "#FFFFFF")
        fop = el.get("fill-opacity", "1")
        orig_tf = el.get("transform", "").strip()

        font = index.resolve(fam)
        used_fallback = False
        if font is None:
            if fallback:
                font = index.resolve(fallback)
                used_fallback = True
            if font is None:
                missing.add(fam)
                continue

        d, upm, adv = glyph_path_d(font, char)
        if d is None:
            missing.add(f"{fam}:glyph={char}")
            continue

        s = size / upm
        adv_scaled = adv * s
        if anchor == "middle":
            x_origin = x - adv_scaled / 2.0
        elif anchor == "end":
            x_origin = x - adv_scaled
        else:
            x_origin = x

        # glyph単位(y-up) → translate(x_origin,y) scale(s,-s)。回転は原文の transform を最外に。
        tf = f"translate({x_origin:.3f},{y:.3f}) scale({s:.6f},{-s:.6f})"
        transform = f"{orig_tf} {tf}".strip() if orig_tf else tf

        path_el = ET.Element(f"{{{SVG_NS}}}path")
        path_el.set("d", d)
        path_el.set("transform", transform)
        path_el.set("fill", fill)
        if fop is not None:
            path_el.set("fill-opacity", fop)
        if used_fallback:
            path_el.set("data-fallback-from", fam)

        # text を path に差し替え（同じ位置に挿入）
        p = parent_map.get(el, root)
        idx = list(p).index(el)
        p.remove(el)
        p.insert(idx, path_el)

    return ET.tostring(root, encoding="unicode")


def families_in(svg_path):
    fams = {}
    with open(svg_path, "r", encoding="utf-8") as fh:
        data = fh.read()
    for m in re.finditer(r"font-family='([^']*)'", data):
        fams[m.group(1)] = fams.get(m.group(1), 0) + 1
    return fams


def cmd_report(args, index):
    print("=== numfield SVG が要求する font-family の解決状況 ===")
    all_fams = {}
    for f in sorted(glob.glob(os.path.join(ASSETS, "numfield_*.svg"))):
        for fam, n in families_in(f).items():
            all_fams[fam] = all_fams.get(fam, 0) + n
    ok = True
    for fam in sorted(all_fams):
        font = index.resolve(fam)
        mark = "OK " if font else "❌ "
        if not font:
            ok = False
        print(f"  {mark} {fam}  (出現 {all_fams[fam]})")
    print()
    if ok:
        print("✅ 全 family 解決可能。--apply で忠実にアウトライン化できます。")
    else:
        print("⚠️  未解決の family があります。Mac 上で実行しているか確認してください。")
        print("    どうしても無い場合のみ --fallback 'Times New Roman' 等で代替（その path に data-fallback-from が付きます）。")
    return 0 if ok else 1


def replace_template_datauri(svg_text):
    """テンプレHTMLの .numfield-full 背景 dataURI を新SVGの base64 で差し替える。"""
    if not os.path.exists(TEMPLATE_HTML):
        print(f"  （テンプレ {TEMPLATE_HTML} が無いのでスキップ）")
        return
    with open(TEMPLATE_HTML, "r", encoding="utf-8") as fh:
        html = fh.read()
    b64 = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    new_uri = f'url("data:image/svg+xml;base64,{b64}")'
    # .numfield-full { ... background-image:url("data:image/svg+xml;base64,XXXX") ... }
    pat = re.compile(
        r'(\.numfield-full\s*\{[^}]*?background-image:\s*)url\("data:image/svg\+xml;base64,[^"]*"\)'
    )
    new_html, n = pat.subn(lambda m: m.group(1) + new_uri, html, count=0)  # 全 .numfield-full を差し替え
    if n == 0:
        print("  ⚠️ .numfield-full の dataURI を見つけられず差し替えできませんでした（HTML構造を確認）。")
        return
    with open(TEMPLATE_HTML, "w", encoding="utf-8") as fh:
        fh.write(new_html)
    print(f"  テンプレ dataURI を path版 numfield_allover_nuki.svg で差し替え（{n}箇所 / {len(b64)} bytes base64）。")


def cmd_reembed(args):
    """Illustrator で OL 済みの allover_nuki を、テンプレ dataURI に生バイトのまま再埋め込み。
    （ET 経由の再シリアライズをせず、Illustrator 出力をそのまま base64 化＝構造を一切いじらない）
    --src で OL ファイル（例 numfield_allover_nuki_ol.svg）を直接指定可。既定は assets/numfield_allover_nuki.svg。"""
    src = args.src or os.path.join(ASSETS, "numfield_allover_nuki.svg")
    if not os.path.isabs(src) and not os.path.exists(src):
        # assets 相対でも探す
        cand = os.path.join(ASSETS, src)
        if os.path.exists(cand):
            src = cand
    if not os.path.exists(src):
        print(f"  ❌ ソースSVGが見つかりません: {src}")
        return 1
    print(f"  ソース: {src}")
    raw = open(src, "r", encoding="utf-8").read()
    if "<text" in raw and not args.allow_text:
        print("  ❌ まだ <text> が残っています（Illustrator で『アウトラインを作成』済みか確認）。")
        print("     どうしても進める場合のみ --allow-text。")
        return 1
    replace_template_datauri(raw)
    print("  ✅ 再埋め込み完了（OL済み allover_nuki をテンプレへ）。")
    return 0


def cmd_apply(args, index):
    targets = sorted(glob.glob(os.path.join(ASSETS, "numfield_*.svg")))
    if not targets:
        print("対象 SVG がありません。")
        return 1
    missing = set()
    nuki_text = None
    for f in targets:
        out = convert_svg(f, index, args.fallback, missing)
        if args.apply:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(out)
        print(f"  {'書込' if args.apply else 'dry'} {os.path.basename(f)}")
        if os.path.basename(f) == "numfield_allover_nuki.svg":
            nuki_text = out
    if missing and not args.fallback:
        print("\n❌ 未解決の font-family があり中断しました（作り直し回避のため代替しません）:")
        for m in sorted(missing):
            print("   -", m)
        print("Mac 上で実行しているか確認してください。")
        return 1
    if args.apply and nuki_text is not None:
        replace_template_datauri(nuki_text)
    if args.verify and args.apply:
        bad = []
        for f in targets:
            with open(f, "r", encoding="utf-8") as fh:
                if "<text" in fh.read():
                    bad.append(os.path.basename(f))
        if bad:
            print("  ⚠️ まだ <text> が残っています:", bad)
            return 1
        print("  ✅ 検査: 全 SVG で <text> 残存ゼロ（完全にアウトライン化）。")
    print("\n完了。" + ("（apply）" if args.apply else "（dry-run / 書き込みなし）"))
    return 0


def main():
    ap = argparse.ArgumentParser(description="numfield <text> を同フォントのまま <path> 化（B案・完全忠実）")
    ap.add_argument("--report", action="store_true", help="font-family の解決状況だけ点検（書き込みなし）")
    ap.add_argument("--reembed", action="store_true", help="Illustrator で OL 済みの allover_nuki をテンプレ dataURI に再埋め込み（推奨フロー）")
    ap.add_argument("--allow-text", action="store_true", help="--reembed で <text> 残存を許容（非推奨）")
    ap.add_argument("--src", default=None, help="--reembed のソースSVG（OLファイル名/パス。既定 assets/numfield_allover_nuki.svg）")
    ap.add_argument("--apply", action="store_true", help="SVGを上書き＋テンプレ dataURI 差し替え（スクリプト単体でアウトライン化する場合）")
    ap.add_argument("--dry-run", action="store_true", help="変換を試すが書き込まない")
    ap.add_argument("--verify", action="store_true", help="apply後に <text> 残存ゼロを検査")
    ap.add_argument("--fallback", default=None, help="未解決時のみ使う代替 family（既定: なし=中断）")
    ap.add_argument("--font-dir", action="append", default=[], help="追加フォント探索ディレクトリ")
    args = ap.parse_args()

    # 再埋め込みはフォント索引不要（OL は Illustrator 側で済んでいる）
    if args.reembed:
        return cmd_reembed(args)

    index = FontIndex(extra_dirs=args.font_dir)

    if args.report:
        return cmd_report(args, index)
    if args.apply or args.dry_run:
        return cmd_apply(args, index)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
