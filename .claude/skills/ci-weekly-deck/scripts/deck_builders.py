#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deck_builders.py — 週次定例デッキの各テーブル(skテーブル)ビルダー群。

元の制作スクリプトの全ビルダーを移植し、**顧客固有の定数を引数化** した:
  - skyu()        … S級フル表(目標/実績/着地/日販/広告)
  - dsp_tbl()     … DSP 18列
  - sa_tbl()      … SA 15列
  - sa_funnel_tbl() … SA ファネル別(一般/指名)
  - lavon_tbls()  … 香調別 月別売上(レシピ駆動)
  - emrg_tbl()    … エマージング シリーズ別ドリルダウン
  - emrg_all_tbl()… エマージング 全ブランド一覧

入力は「集計用シートの行(list of list)」。列インデックスは原本の列構成に合わせている。
ブランド名・市場シェア・ハイライト・PD行などの顧客固有値は、呼び出し側(build_deck.py /
config / sample_data)から渡す。整形は ci_v2_lib のヘルパ(mm/man/f_*)を共通利用する。
"""
import re
from itertools import groupby
import ci_v2_lib as ci


def _g(rows, r, c):
    return (rows[r][c] if r < len(rows) and c < len(rows[r]) else "") or ""


def _grow(r, c):
    return (r[c] if c < len(r) else "") or ""


def _pct(s):
    m = re.sub(r"[¥,%]", "", str(s))
    try:
        return float(m)
    except ValueError:
        return None


# --------------------------------------------------------------- S級フル表
def skyu(rows, market=None, highlight=None, total_cat="全体（発送）", grand_label="合算（計）"):
    """
    rows: skyu_full 相当(rows[2:] を本体とする)。
    market: {カテゴリ名: 推計当年市場月商(百万円)} 推計シェア列用(無ければ '–')。
    highlight: {(brand, cat)} ハイライトする行。
    """
    market = market or {}
    highlight = highlight or set()
    recs = []
    brand = ""
    for r in rows[2:]:
        cat = _grow(r, 6).strip()
        if not cat:
            continue
        if cat == total_cat:
            brand = _grow(r, 5).strip()
        recs.append((brand, cat, cat == total_cat, r))

    H = '<tr><th class="l" rowspan="2">ブランド</th><th class="l" rowspan="2">カテゴリ別</th><th class="l" rowspan="2">推計シェア率</th>'
    H += '<th class="g" colspan="7">Object：POS売上（百万円）</th><th class="g" colspan="3">通常期日販推移</th>'
    H += '<th class="g" colspan="3">広告経由売上（百万円）</th><th class="g" colspan="2">広告費比率</th></tr>'
    H += "<tr>" + "".join(f"<th>{c}</th>" for c in [
        "目標売上", "目標YoY", "実績", "比率", "達成率", "着地見込", "YoY見込",
        "今月(万円)", "MoM", "YoY", "実績", "比率", "ROAS", "計画", "実績"]) + "</tr>"

    totrows = [r for (b, c, t, r) in recs if t]

    def S(i):
        return sum((ci.num(_grow(r, i)) or 0) for r in totrows)

    def ys(vc, yc):
        s = 0
        for r in totrows:
            v = ci.num(_grow(r, vc))
            y = _pct(_grow(r, yc))
            if v and y:
                s += v / (y / 100)
        return s

    a_t, a_a, a_m, a_n, a_ad = S(7), S(9), S(12), S(21), S(33)
    a_ty = (a_t / ys(7, 8) * 100) if ys(7, 8) else 0
    a_my = (a_m / ys(12, 13) * 100) if ys(12, 13) else 0
    grand = ('<tr class="grand"><td class="l bd" colspan="2">' + grand_label + '</td><td class="bd">–</td>'
             f'<td>{ci.mm(a_t)}</td><td>{a_ty:.0f}%</td><td>{ci.mm(a_a)}</td><td class="dim">–</td>'
             f'<td>{(a_a / a_t * 100) if a_t else 0:.1f}%</td><td>{ci.mm(a_m)}</td><td>{a_my:.0f}%</td>'
             f'<td>{ci.man(a_n)}</td><td>–</td><td>–</td>'
             f'<td>{ci.mm(a_ad)}</td><td class="dim">–</td><td>–</td><td>–</td><td>–</td></tr>')
    out = grand
    for b, grp in groupby(recs, key=lambda x: x[0]):
        gl = list(grp)
        totrow = next((x[3] for x in gl if x[2]), None)
        bh = ""
        if totrow is not None:
            _t = ci.num(_grow(totrow, 7))
            _mk = ci.num(_grow(totrow, 12))
            if _t is not None and _mk is not None:
                _d = _mk - _t
                bh = f'着地{"▲" if _d < 0 else "+"}{abs(_d) / 1e4:,.0f}万'
        for k, (brand, cat, tot, r) in enumerate(gl):
            hl = " hl" if (brand, cat) in highlight else ""
            out += f'<tr class="tot{hl}">' if tot else (f'<tr class="hl">' if hl else "<tr>")
            if k == 0:
                out += f'<td class="bd l" rowspan="{len(gl)}">{brand}<br><span style="font-size:8.5px">{bh}</span></td>'

            def Y(i):
                return f"<td>{ci.mm(_grow(r, i))}</td>"

            def M(i):
                return f"<td>{ci.man(_grow(r, i))}</td>"

            def C(i, c=""):
                return f'<td class="{c}">{_grow(r, i) or "–"}</td>'

            out += f'<td class="l">{cat}</td>'
            _mv = ci.num(_grow(r, 12))
            _ms = market.get(cat)
            out += f'<td class="bd">{(f"{_mv / (_ms * 1e6) * 100:.1f}%" if (_mv and _ms) else "–")}</td>'
            out += Y(7) + C(8) + Y(9) + C(10, "dim") + C(11) + Y(12) + C(13)
            out += M(21) + C(22) + C(23)
            out += Y(33) + C(34, "dim") + C(35)
            out += C(36) + C(37)
            out += "</tr>"
    unit = ('<p class="sk-unit">単位：百万円（日販のみ万円）　／　端数は四捨五入、△＝マイナス、－＝該当なし　'
            '／　ブランド名下＝着地差分（着地見込−目標、▲＝ビハインド）</p>')
    return '<div class="skyu">' + unit + '<table class="sk">' + H + out + "</table></div>"


# --------------------------------------------------------------- DSP
def dsp_tbl(rows, s_rows=(6, 7, 8), s_tot=9, em_rows=(11, 12, 13, 14, 15), em_tot=16, grand=18, note="", tcls="wide"):
    # 実デッキ準拠：フラット単一ヘッダ20列(Total接頭辞)
    cols = ["区分", "ブランド", "ご予算(万)", "投下金額(万)", "ご予算進捗", "Total DPV", "DPVR", "eCPDPV",
            "Total Purchases", "CVR", "Total Sales(万)", "Average Price", "Total ROAS", "前週Total ROAS",
            "Total NtB Purchases", "新規CPP", "目標新規CPP", "前週新規CPP", "Total SnSS", "Total eCPSnSS"]
    H = "<tr>" + "".join((f'<th class="l">{c}</th>' if i < 2 else f"<th>{c}</th>") for i, c in enumerate(cols)) + "</tr>"

    def row(i, seg, cls=""):
        def G(c):
            return _g(rows, i, c)
        return (f'<tr class="{cls}"><td class="l">{seg}</td><td class="l bd">{G(2)}</td>'
                f'<td>{ci.f_man(G(3))}</td><td>{ci.f_man(G(4))}</td><td>{ci.f_pc(G(5))}</td>'
                f'<td>{ci.f_cnt(G(6))}</td><td>{ci.f_pc(G(7), 2)}</td><td>{ci.f_yen(G(8))}</td>'
                f'<td>{ci.f_cnt(G(9))}</td><td>{ci.f_pc(G(10), 1)}</td><td>{ci.f_man(G(11))}</td>'
                f'<td>{ci.f_yen(G(12))}</td><td>{ci.f_pc(G(13))}</td><td class="dim">{ci.f_pc(G(14))}</td>'
                f'<td>{ci.f_cnt(G(16))}</td><td>{ci.f_yen(G(17))}</td><td class="dim">{ci.f_yen(G(18))}</td>'
                f'<td class="dim">{ci.f_yen(G(19))}</td><td>{ci.f_cnt(G(21))}</td><td>{ci.f_yen(G(22))}</td></tr>')

    out = "".join(row(i, "S級") for i in s_rows) + row(s_tot, "S級", "tot")
    out += "".join(row(i, "EM") for i in em_rows) + row(em_tot, "EM", "tot")
    out += row(grand, "総合計", "grand")
    unit = f'<p class="sk-unit">{note or "■DSP 通常＋Performance+合算　／　金額＝万円・客単価/CPP/eCPDPV＝円・DPV/購入/NtB/SnSS＝件・他＝％"}</p>'
    return '<div class="skyu">' + unit + f'<table class="sk {tcls}">' + H + out + "</table></div>"


# --------------------------------------------------------------- SA
def sa_tbl(rows, s_rows=(5, 6, 7), s_tot=8, em_rows=(10, 11, 12, 13, 14, 15, 16, 17, 18), em_tot=19, grand=21, note=""):
    # 実デッキ準拠：フラット単一ヘッダ17列
    cols = ["区分", "ブランド", "ご予算", "投下金額", "ご予算進捗", "一般Kw比率", "Impression", "Click",
            "CTR", "CPC", "注文数", "CVR", "CPP", "売上", "平均注文単価", "ROAS", "前週ROAS"]
    H = "<tr>" + "".join((f'<th class="l">{c}</th>' if i < 2 else f"<th>{c}</th>") for i, c in enumerate(cols)) + "</tr>"

    def row(i, seg, cls=""):
        def G(c):
            return _g(rows, i, c)
        return (f'<tr class="{cls}"><td class="l">{seg}</td><td class="l bd">{G(2)}</td>'
                f'<td>{ci.f_man(G(3))}</td><td>{ci.f_man(G(4))}</td><td>{ci.f_pc(G(5), 1)}</td>'
                f'<td>{ci.f_pc(G(6), 1)}</td><td>{ci.f_cnt(G(7))}</td><td>{ci.f_cnt(G(8))}</td>'
                f'<td>{ci.f_pc(G(9), 2)}</td><td>{ci.f_yen(G(10))}</td><td>{ci.f_cnt(G(11))}</td>'
                f'<td>{ci.f_pc(G(12), 1)}</td><td>{ci.f_yen(G(13))}</td><td>{ci.f_man(G(14))}</td>'
                f'<td>{ci.f_yen(G(15))}</td><td>{ci.f_pc(G(16))}</td><td class="dim">{ci.f_pc(G(17))}</td></tr>')

    out = "".join(row(i, "S級") for i in s_rows) + row(s_tot, "S級", "tot")
    out += "".join(row(i, "EM") for i in em_rows) + row(em_tot, "EM", "tot")
    out += row(grand, "全体", "grand")
    unit = f'<p class="sk-unit">{note or "■SA 全体予算　／　金額＝万円・CPC/CPP/客単価＝円・Imp/Click/注文数＝件・他＝％"}</p>'
    return '<div class="skyu">' + unit + '<table class="sk wide">' + H + out + "</table></div>"


# --------------------------------------------------------------- SA ファネル別
def sa_funnel_tbl(rows, groups, total_row, note=""):
    """groups: [(brand, 一般行index, 指名行index), ...] / total_row: S級合計の行index。"""
    H = '<tr><th class="l" rowspan="2">ブランド</th><th class="l" rowspan="2">ファネル</th>'
    H += '<th class="g" colspan="2">投下</th><th class="g" colspan="9">配信実績</th><th class="g" colspan="2">ROAS</th></tr>'
    sub = ["投下(万)", "Kw比率", "Imp", "Click", "CTR", "CPC", "注文数", "CVR", "CPP", "売上(万)", "客単価", "ROAS", "前週"]
    H += "<tr>" + "".join(f"<th>{c}</th>" for c in sub) + "</tr>"

    def cells(i):
        def G(c):
            return _g(rows, i, c)
        return (f'<td>{ci.f_man(G(5))}</td><td>{ci.f_pc(G(6), 1)}</td>'
                f'<td>{ci.f_cnt(G(7))}</td><td>{ci.f_cnt(G(8))}</td><td>{ci.f_pc(G(9), 2)}</td>'
                f'<td>{ci.f_yen(G(10))}</td><td>{ci.f_cnt(G(11))}</td><td>{ci.f_pc(G(12), 1)}</td>'
                f'<td>{ci.f_yen(G(13))}</td><td>{ci.f_man(G(14))}</td><td>{ci.f_yen(G(15))}</td>'
                f'<td>{ci.f_pc(G(16))}</td><td class="dim">{ci.f_pc(G(17))}</td>')

    out = ""
    for brand, gi, bi in groups:
        out += f'<tr><td class="bd l" rowspan="2">{brand}</td><td class="l">一般</td>' + cells(gi) + "</tr>"
        out += f'<tr class="hl"><td class="l">指名</td>' + cells(bi) + "</tr>"
    out += '<tr class="grand"><td class="l bd" colspan="2">S級 合計</td>' + cells(total_row) + "</tr>"
    unit = f'<p class="sk-unit">{note or "■SA ファネル別（一般／指名）　／　金額＝万円・CPC/CPP/客単価＝円・他＝％　／　指名は高ROAS・高CVRで刈り取り効率が高い"}</p>'
    return '<div class="skyu">' + unit + '<table class="sk wide">' + H + out + "</table></div>"


# --------------------------------------------------------------- 香調別 月別
def lavon_tbls(v, sections, hdr_row=3, recent=6):
    """
    v: 月別シート相当。hdr_row行に月ラベル。
    sections: [{"head":章タイトル, "title":表頭ラベル, "rows":[(表示名, 本体ラベル, 詰替ラベル), ...]}, ...]
    """
    hdr = v[hdr_row]
    mcols = [j for j, c in enumerate(hdr) if c and c != "年"]
    recent_cols = mcols[-recent:]
    mlabels = [hdr[j] for j in recent_cols]
    # YoY = 最新月 vs 12ヶ月前(無ければ先頭月)
    last = recent_cols[-1]
    yoy_base = mcols[mcols.index(last) - 12] if mcols.index(last) - 12 >= 0 else mcols[0]

    def val(row, j):
        try:
            return float(re.sub(r"[¥,]", "", str(row[j]))) if row and j < len(row) and row[j] else 0
        except ValueError:
            return 0

    def find(lbl):
        return next((r for r in v if len(r) > 1 and str(r[1]).strip() == lbl), None)

    def kacho_row(name, body, refill):
        rb, rr = find(body), find(refill)
        tot = [(val(rb, j) + val(rr, j)) for j in recent_cols]
        y_new = val(rb, last) + val(rr, last)
        y_old = val(rb, yoy_base) + val(rr, yoy_base)
        yoy = f"{y_new / y_old * 100:.0f}%" if y_old else "–"
        cells = "".join(f"<td>{round(x / 1e4):,}</td>" for x in tot)
        return f'<tr><td class="l bd">{name}</td>{cells}<td class="bd">{yoy}</td></tr>'

    def tbl(title, body_rows):
        H = f'<tr><th class="l">{title}（万円/月）</th>' + "".join(f"<th>{m}</th>" for m in mlabels) + "<th>YoY</th></tr>"
        return f'<div class="skyu"><table class="sk">{H}{body_rows}</table></div>'

    out = ""
    for sec in sections:
        body = "".join(kacho_row(*r) for r in sec["rows"])
        out += f'<p class="sho-h" style="margin-top:10px">▼ {sec["head"]}</p>' + tbl(sec["title"], body)
    return out


# --------------------------------------------------------------- エマージング ドリルダウン(ブランド単位＋PV列)
def emrg_tbl(rows, highlight=None, note=""):
    """
    実デッキ準拠：ブランド単位ドリルダウン。列インデックス:
      4=brand, 5='grand'なら合算行 / 6=目標 7=目標YoY 8=実績 10=達成率 11=着地見込 12=YoY見込
      13=PV目標 14=PV実績 15=PV達成 16=計画(万) 17=実績(万) 18=ROAS 19=TACoS
    highlight: {brand} ハイライトするブランド名。販促未実施ブランドは 16-19 を空にすると '–' 表示。
    """
    highlight = highlight or set()
    H = ('<tr><th class="l" rowspan="2">ブランド</th>'
         '<th class="g" colspan="6">Object：POS売上（百万円）</th>'
         '<th class="g" colspan="3">KR:1 集客（PV数）</th>'
         '<th class="g" colspan="4">販促広告費</th></tr>')
    sub = ["目標", "目標YoY", "実績", "達成率", "着地見込", "YoY見込",
           "PV目標", "PV実績", "PV達成", "計画(万)", "実績(万)", "ROAS", "TACoS"]
    H += "<tr>" + "".join(f"<th>{c}</th>" for c in sub) + "</tr>"

    def line(r):
        def G(c):
            return _grow(r, c)
        grand = str(_grow(r, 5)).strip() == "grand"
        brand = _grow(r, 4).strip()
        hl = (not grand) and (brand in highlight)
        _t, _mk = ci.num(G(6)), ci.num(G(11))
        bh = (f'{"▲" if (_mk - _t) < 0 else "+"}{abs(_mk - _t) / 1e4:,.0f}万'
              if (_t is not None and _mk is not None) else "")
        cls = "grand" if grand else ("hl" if hl else "")
        nm = (f'<td class="l bd">{brand}</td>' if grand
              else f'<td class="l bd">{brand}<br><span style="font-size:8.5px">{bh}</span></td>')
        return (f'<tr class="{cls}">{nm}'
                f"<td>{ci.mm(G(6))}</td><td>{ci.f_pc(G(7))}</td><td>{ci.mm(G(8))}</td>"
                f'<td>{ci.f_pc(G(10), 1)}</td><td>{ci.mm(G(11))}</td><td>{ci.f_pc(G(12))}</td>'
                f"<td>{ci.f_cnt(G(13))}</td><td>{ci.f_cnt(G(14))}</td><td>{ci.f_pc(G(15), 1)}</td>"
                f"<td>{ci.f_man(G(16))}</td><td>{ci.f_man(G(17))}</td>"
                f"<td>{ci.f_pc(G(18))}</td><td>{ci.f_pc(G(19), 1)}</td></tr>")

    # grand行(col5=='grand')を先頭、以降はブランド行
    grands = [r for r in rows if str(_grow(r, 5)).strip() == "grand"]
    others = [r for r in rows if str(_grow(r, 5)).strip() != "grand" and _grow(r, 4).strip()]
    out = "".join(line(r) for r in grands + others)
    unit = f'<p class="sk-unit">{note or "エマージング ブランド単位ドリルダウン　／　POS売上＝百万円・PV＝件・広告費＝万円・他＝％　／　PV達成＝KR:1集客"}</p>'
    return '<div class="skyu">' + unit + '<table class="sk wide">' + H + out + "</table></div>"


# --------------------------------------------------------------- エマージング 全ブランド一覧
def emrg_tbl_all(rows, grand_label="EM合計", annotate=None, note=""):
    """annotate: {ブランド名: 接尾辞} 例 {'CLEVER':'（別定例）'}。"""
    annotate = annotate or {}
    H = ('<tr><th class="l">ブランド</th><th>目標</th><th>目標YoY</th><th>実績</th><th>達成率</th>'
         '<th>着地見込</th><th>着地YoY</th><th>PV達成</th><th>着地差分</th></tr>')
    out = ""
    for r in rows:
        b = _grow(r, 4).strip()
        if not b or "¥" not in "".join(str(c) for c in r):
            continue
        cls = ' class="grand"' if b == grand_label else ""
        nm = b + annotate.get(b, "") + ("（合計）" if b == grand_label else "")
        _t = ci.num(_grow(r, 6))
        _mk = ci.num(_grow(r, 10))
        bh = (f'{"▲" if (_mk - _t) < 0 else "+"}{abs(_mk - _t) / 1e4:,.0f}万' if (_t is not None and _mk is not None) else "–")
        out += (f"<tr{cls}><td class=\"l bd\">{nm}</td><td>{ci.mm(_grow(r, 6))}</td><td>{ci.f_pc(_grow(r, 7))}</td>"
                f"<td>{ci.mm(_grow(r, 8))}</td><td>{ci.f_pc(_grow(r, 9), 1)}</td><td>{ci.mm(_grow(r, 10))}</td>"
                f"<td>{ci.f_pc(_grow(r, 11))}</td><td>{ci.f_pc(_grow(r, 15), 1)}</td><td class=\"bd\">{bh}</td></tr>")
    unit = f'<p class="sk-unit">{note or "エマージング 全ブランド（ブランドレベル・百万円）　／　PV達成＝KR:1　／　着地差分＝着地見込−目標"}</p>'
    return '<div class="skyu">' + unit + '<table class="sk dense">' + H + out + "</table></div>"


# --------------------------------------------------------------- PD目標表
def pd_tbl(rows, note=""):
    """rows: [(name, cls, 合計円, アーリー円, 本セール円, YoY, eYoY, mYoY, 本ｾﾙ割合, 昨対成長円, 備考), ...]"""
    def mm(v):
        return f"{v / 1e6:,.1f}"

    def smm(v):
        return f"+{v / 1e6:,.1f}"

    H = ('<tr><th class="l" rowspan="2">ブランド</th>'
         '<th class="g" colspan="3">PD目標（百万円）</th>'
         '<th class="g" colspan="2">アーリー</th>'
         '<th class="g" colspan="2">本セール</th>'
         '<th class="l" rowspan="2">備考</th></tr>'
         '<tr><th>合計</th><th>YoY</th><th>昨対成長</th>'
         '<th>金額</th><th>YoY</th><th>金額</th><th>YoY</th><th>本ｾﾙ割合</th></tr>')
    out = ""
    for (nm, cls, tot, erl, mn, yoy, eyoy, myoy, ratio, grw, memo) in rows:
        trcls = ' class="tot"' if cls == "tot" else ""
        nmcell = f"<b>{nm}</b>" if cls == "bold" else nm
        out += (f"<tr{trcls}><td class=\"l\">{nmcell}</td>"
                f"<td>{mm(tot)}</td><td>{yoy}</td><td>{smm(grw)}</td>"
                f"<td>{mm(erl)}</td><td>{eyoy}</td>"
                f"<td>{mm(mn)}</td><td>{myoy}</td><td>{ratio}</td>"
                f"<td class=\"l\">{memo}</td></tr>")
    unit = f'<p class="sk-unit">{note or "単位：百万円（整数・四捨五入）　／　YoY・割合＝％"}</p>'
    return '<div class="skyu">' + unit + '<table class="sk wide">' + H + out + "</table></div>"
