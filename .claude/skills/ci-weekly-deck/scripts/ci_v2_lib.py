#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ci_v2_lib.py — 週次定例デッキ(5co. CI v2)を組み立てる再利用ライブラリ。

このファイルは **顧客非依存** の共通部品のみを持つ:
  - CI基盤HTML(5co-CIスライド/が唯一の正)のHEAD(CSS＋ロックアップsymbol)を読み込むローダ
  - IR作法の数値整形ヘルパ(百万円/万円/円/件/%・四捨五入・マイナス△)
  - CI v2レイアウトヘルパ(表紙/ヘッダ/章扉/OKRノード)
  - CI 3色のみで安全な追加CSS(EXTRA_CSS)

顧客固有(ブランド名・実数値・所見文・スプレッドシートID・ロゴ)は **一切持たない**。
それらは build_deck.py 側の「顧客ごとに書き換える領域」と config.json に置く。

CI制約(厳守・SLIDE.md準拠): 配色は 白#FFFFFF / 水色 --crystal #C3D7EE / 紺 --ink #101820 の3色のみ
(旧名 --navy/--powder・旧hex #A9CFDF/#0E1A38 は廃止)。
増減セマンティクス(達成/未達)以外で緑・赤・グレー・他色相を使わない。
CSSは0から書かず CI基盤を複製・参照する(EXTRA_CSSは基盤を壊さない最小の上書きのみ)。
"""
import re
import json
import base64
import os
import subprocess


# ---------------------------------------------------------------- config / IO
def load_config(path):
    """config.json を読む。相対パスは config の置き場基準で解決する。"""
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    base = os.path.dirname(os.path.abspath(path))

    def _resolve(p):
        p = os.path.expanduser(p)
        return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

    for k in ("ci_base_html", "client_logo", "output_html", "oauth_token", "numfield_svg"):
        if cfg.get(k):
            cfg[k] = _resolve(cfg[k])
    return cfg


def img_data_uri(path):
    """画像をdata URI化(HTMLを単一ファイルで完結させ、Drive取込・PDF印刷を安定させる)。"""
    ext = os.path.splitext(path)[1].lstrip(".").lower() or "png"
    mime = {"svg": "svg+xml", "jpg": "jpeg"}.get(ext, ext)
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def load_ci_head(ci_base_html, title, lockup_id="lockup"):
    """
    CI基盤HTML(5co-CIスライド/の標準テンプレ)の先頭〜ロックアップsymbol終端までを
    HEADとして取り出す。CSS全部＋ロックアップSVGを丸ごと流用する(=テンプレ複製)。
    title だけ差し替える。
    lockup_id: 基盤の <symbol id="..."> のID(標準テンプレは "lockup"、旧sampleは "lk")。
    """
    s = open(ci_base_html, encoding="utf-8").read()
    end = s.find("</symbol>")
    if end < 0:
        raise ValueError(f"CI基盤に <symbol> が見つかりません: {ci_base_html}")
    head = s[: end + len("</symbol>")] + "</svg>\n"
    m = re.search(r"<title>.*?</title>", head, re.S)
    head = head.replace(m.group(0) if m else "<title></title>", f"<title>{title}</title>")
    return head


# ---------------------------------------------------------------- formatters (IR作法)
def num(s):
    """セル文字列を数値へ。非数値/空はNone。"""
    s = str(s)
    if not s or s in ("–", "-", "-%", "#DIV/0!"):
        return None
    try:
        return float(re.sub(r"[¥,]", "", s))
    except ValueError:
        return None


def rhu(x):
    """四捨五入(round half up・符号対応)。"""
    import math
    return -math.floor(-x + 0.5) if x < 0 else math.floor(x + 0.5)


def mm(s):
    """百万円・小数1桁・カンマ・マイナス△(単位は表頭に書く)。CI: 百万円は0.1まで記載。"""
    n = num(s)
    if n is None:
        return "–" if str(s).strip() in ("", "–", "-", "-%", "#DIV/0!") else str(s)
    v = n / 1e6
    return f"△{abs(v):,.1f}" if v < 0 else f"{v:,.1f}"


def man(s):
    """万円・整数・カンマ(日販など小桁列、単位は表頭)。"""
    n = num(s)
    if n is None:
        return "–" if str(s).strip() in ("", "–", "-", "-%", "#DIV/0!") else str(s)
    v = rhu(n / 1e4)
    return f"△{abs(v):,.0f}" if v < 0 else f"{v:,.0f}"


def f_man(s):
    n = num(s)
    return "–" if n is None else f"{round(n / 1e4):,}"


def f_yen(s):
    n = num(s)
    return "–" if n is None else f"¥{round(n):,}"


def f_cnt(s):
    n = num(s)
    return "–" if n is None else f"{round(n):,}"


def f_pc(s, dec=0):
    """%整形。元が非数値ならそのまま(または–)。"""
    m = re.sub(r"[¥,%]", "", str(s))
    try:
        return f"{float(m):.{dec}f}%"
    except ValueError:
        return str(s) or "–"


# ---------------------------------------------------------------- layout helpers
def _corner(lockup_id):
    return f'<svg class="corner" viewBox="0 0 50.857 36.507"><use href="#{lockup_id}"/></svg>'


def period(text):
    """フッター左の『日進捗・集計期間』1行。text例: '日進捗 <b>70%</b> ・ 集計期間 YYYY-MM-DD〜MM-DD'"""
    return f'<div class="period">{text}</div>'


def header(kicker, title, sub="", *, client_logo_uri, lockup_id="lockup", period_html=""):
    """本文スライドのヘッダ(顧客ロゴ＋キッカー＋タイトル＋アクセントバー＋サブ)。"""
    h = _corner(lockup_id) + period_html
    h += (
        f'<div class="hdr"><img class="client-logo" src="{client_logo_uri}" alt="client logo">'
        f'<span class="kicker">{kicker}</span></div>'
    )
    h += f'<h2 class="title">{title}</h2><div class="accent-bar"></div>'
    if sub:
        h += f'<p class="sub">{sub}</p>'
    return h


def cover(kicker, title_html, lead_html, *, client_logo_uri, lockup_id="lockup"):
    """表紙(数字フィールド背景＋顧客ロゴ＋5coロックアップ＋タイトル)。"""
    return f"""<section class="slide cover-full">
  <div class="numfield-full"></div>
  <div class="cf-corner"><svg viewBox="0 0 50.857 36.507"><use href="#{lockup_id}"/></svg></div>
  <div class="cf-logo"><img src="{client_logo_uri}" alt="client logo" style="width:100%"></div>
  <div class="cf-block">
    <span class="kicker">{kicker}</span>
    <h1>{title_html}</h1>
    <p class="lead">{lead_html}</p>
  </div>
</section>"""


def divider(secno, title, sub, *, lockup_id="lockup"):
    """章扉(dark・左に縦バー)。"""
    return (
        f'<section class="slide dark divider">{_corner(lockup_id)}'
        f'<div class="dv-bar"></div><div><span class="secno">{secno}</span>'
        f'<h2 class="dv-title">{title}</h2><p class="dv-sub">{sub}</p></div></section>'
    )


def pd_divider(secno, title, sub_html, *, lockup_id="lockup"):
    """章扉(表紙の数字フィールド背景に扉レイアウトの文字をノセ・明色背景=ink文字)。"""
    return f"""<section class="slide cover-full pd-divider">
  <div class="numfield-full"></div>
  <div class="cf-corner"><svg viewBox="0 0 50.857 36.507"><use href="#{lockup_id}"/></svg></div>
  <div class="pd-text"><div class="dv-bar"></div><div><span class="secno">{secno}</span>
    <h2 class="dv-title">{title}</h2>
    <p class="dv-sub">{sub_html}</p></div>
  </div>
</section>"""


def oknode(name, target, actual, forecast, mark, cls="", shr=""):
    """OKRツリーのノード(目標/実績/見込を別の四角に分割)。mark: 'ok'(○) or 'bh'(△)。"""
    sh = f'<span class="shr">{shr}</span>' if shr else ""
    return (
        f'<div class="nd {cls}"><span class="nm">{name}{sh}</span>'
        f'<div class="box"><span class="lbl">目標</span>{target}</div>'
        f'<div class="box"><span class="lbl">実績</span>{actual}</div>'
        f'<div class="box mk"><span class="lbl">見込</span>{forecast} <span class="{mark}"></span></div></div>'
    )


# ---------------------------------------------------------------- render / export
def numfield_style(svg_path, opacity=0.75):
    """
    表紙(cover-full)・PD章扉の全面数字フィールド背景。CI基盤は assets/ を相対参照するため
    単一HTMLでは表示されない → CI正本の numfield SVG を data URI で埋め込む(実デッキと同方式)。
    svg_path が無ければ空文字を返す(数字背景なしで動作継続)。
    """
    if not svg_path or not os.path.exists(svg_path):
        return ""
    uri = img_data_uri(svg_path)
    return ("<style>.cover-full .numfield-full,.cover-full.pd-divider .numfield-full{"
            f'position:absolute;inset:0;z-index:0;pointer-events:none;background-image:url("{uri}");'
            f"background-size:cover;background-position:center;opacity:{opacity};}}</style>")


def render(head_html, slides, *, tail="\n</body>\n</html>\n", extra_head=""):
    """HEAD ＋ EXTRA_CSS ＋ 追加head ＋ スライド列 ＋ TAIL を結合して完成HTMLを返す。"""
    return head_html + EXTRA_CSS + (extra_head or "") + "\n".join(slides) + tail


def to_pdf(html_path, pdf_path, chrome=None):
    """Chrome --headless --print-to-pdf でA4横PDFを出力(任意・印刷確認用)。"""
    candidates = [chrome] if chrome else [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome", "chromium", "chromium-browser",
    ]
    for exe in candidates:
        if not exe:
            continue
        try:
            subprocess.run(
                [exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                 f"--print-to-pdf={pdf_path}", f"file://{os.path.abspath(html_path)}"],
                check=True, capture_output=True,
            )
            return pdf_path
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError("Chromeが見つからずPDF化に失敗。chrome引数で実行パスを指定してください。")


# ---------------------------------------------------------------- EXTRA CSS (CI 3色のみ・基盤を壊さない最小上書き)
EXTRA_CSS = r"""
<style>
/* --- CIトークン互換シム ---
   正規CI(SLIDE.md / sample.html)のトークンは --ink #101820 / --crystal #C3D7EE。本シムは
   同値で再定義し、--ink/--crystal を持たない基盤を指定された場合でも罫線・網掛け・級数が
   無効化されないようにする保険(sample.html基盤ではネイティブ定義と同値で無害)。
   白混ぜの濃淡(#DEE9F6/#F0F5FB)は3色CIの許容範囲。旧名 --navy/--powder は使わない。 */
:root{
  --ink:#101820; --ink-14:rgba(16,24,32,.14); --ink-55:rgba(16,24,32,.55);
  --ink-60:rgba(16,24,32,.60); --ink-85:rgba(16,24,32,.85);
  --crystal:#C3D7EE; --crystal-55:#DEE9F6; --crystal-25:#F0F5FB;
  --fs-body:18px; --fs-lg:47px; --fs-note:11px;
}
/* ヘッダー＝クライアントロゴ＋キッカーを横並び(ロゴを少し下げ、キッカーは右隣) */
.hdr{display:flex; align-items:center; gap:20px; margin:18px 0 6px;}
.hdr .client-logo{height:34px; width:auto; display:block;}
.hdr .kicker{margin:0;}
/* ヘッダー右上の5coロゴ：左ブロックと天地を揃える(CI 64px上書き)。
   新CI基盤は右上ロックアップを .corner-logo で絶対配置するが、本ビルダーは .corner をemitするため
   ここで position:absolute を自前指定する(これが無いと左上にインライン表示で崩れる)。 */
svg.corner{position:absolute; top:78px; right:50px; width:102px; height:auto; display:block;
  color:var(--ink); fill:currentColor; z-index:3;}
/* ダーク地スライド：新CI基盤は .reverse で定義し .slide.dark の地色が無いため自前定義 */
.slide.dark{background:var(--ink); color:var(--crystal);}
.slide.dark h1,.slide.dark h2,.slide.dark h3,.slide.dark .title{color:var(--crystal);}
.slide.dark .kicker,.slide.dark .sub,.slide.dark small,.slide.dark .note{color:rgba(195,215,238,.78);}
.slide.dark .accent-bar,.slide.dark ul.clean li::before{background:var(--crystal);}
.slide.dark svg.corner{color:var(--crystal);}
.slide.dark::before,.slide.dark::after{color:rgba(195,215,238,.65);}
/* 横長の顧客ロゴは cf-logo 既定32mmでは小さい→表紙で適正サイズに拡大 */
.cover-full .cf-logo{width:62mm; top:20mm;}
.cover-full .cf-logo img{width:100%; display:block;}
/* 表紙テキストブロック・タイトル級数を実デッキに合わせる(bottom:28mm/max-width:64%/h1:46px) */
.cover-full .cf-block{bottom:28mm; max-width:64%;}
.cover-full .cf-block h1{font-size:46px; line-height:1.22; letter-spacing:.04em; margin:.3em 0 .5em;}
/* 表紙の5co正規ロックアップ：右側・集計期間の下端ラインに下揃え */
.cover-full .cf-corner{position:absolute; right:18mm; bottom:34mm; width:30mm; color:var(--ink); z-index:2;}
.cover-full .cf-corner svg{width:100%; height:auto; display:block; fill:currentColor;}
/* 章扉(表紙の数字フィールド背景に扉文字をノセ・明色背景=ink文字) */
.cover-full.pd-divider .pd-text{position:absolute; left:64px; top:50%; transform:translateY(-50%); z-index:2; display:flex; align-items:center; gap:42px; max-width:74%;}
.cover-full.pd-divider .dv-bar{width:8px; height:150px; background:var(--ink); flex:none;}
.cover-full.pd-divider .secno{font-family:var(--serif-en); letter-spacing:.3em; font-size:var(--fs-note); color:var(--ink); opacity:.55; display:block; margin-bottom:16px;}
.cover-full.pd-divider .dv-title{font-size:var(--fs-lg); line-height:1.2; margin:0; color:var(--ink);}
.cover-full.pd-divider .dv-sub{font-size:var(--fs-body); color:var(--ink); opacity:.8; margin-top:18px; max-width:62ch;}
.ok{font-weight:700;} .bh{font-weight:700;}
.ok::after{content:"○";} .bh::after{content:"△";}
/* OKRツリー(入れ子ul・コネクタ=ink-14) */
.okr{--ln:var(--ink-60); text-align:center; margin-top:2px;}
.okr ul{display:flex; justify-content:center; padding:9px 0 0; margin:0; list-style:none; position:relative;}
.okr li{position:relative; padding:9px 4px 0;}
.okr li::before,.okr li::after{content:""; position:absolute; top:0; right:50%; width:50%; height:9px; border-top:1.5px solid var(--ln);}
.okr li::after{right:auto; left:50%; border-left:1.5px solid var(--ln);}
.okr li:only-child::before,.okr li:only-child::after{display:none;}
.okr li:only-child{padding-top:0;}
.okr li:first-child::before,.okr li:last-child::after{border:0;}
.okr li:last-child::before{border-right:1.5px solid var(--ln);}
.okr ul ul::before{content:""; position:absolute; top:0; left:50%; border-left:1.5px solid var(--ln); width:0; height:9px;}
.okr .nd{display:inline-block; text-align:left; min-width:162px; vertical-align:top;}
.okr .nm{font-weight:600; font-size:12.5px; display:block; margin-bottom:4px; text-align:center; color:var(--ink); line-height:1.3;}
.okr .box{border:1pt solid var(--ink-60); border-radius:6px; padding:2px 9px; margin-top:2px; font-size:10.5px; color:var(--ink); line-height:1.4; font-variant-numeric:lining-nums tabular-nums; background:var(--white); white-space:nowrap;}
.okr .box .lbl{display:inline-block; width:30px; color:var(--ink-60); font-size:9.5px;}
.okr .box b{font-size:12px;}
.okr .box.mk{background:var(--crystal-25); font-weight:600;}
.okr .nd.s .box.mk{background:var(--crystal);}
.okr .nd.lead{background:var(--ink); border-radius:8px; padding:9px 16px; min-width:0; font-size:inherit; line-height:1.3;}
.okr .nd.lead .nm{color:var(--crystal); text-align:left;}
.okr .nd.lead .box{display:block; margin:4px 0 0 0; background:rgba(195,215,238,.12); border-color:rgba(195,215,238,.60); color:var(--crystal);}
.okr .nd.lead .box .lbl{color:rgba(195,215,238,.7);}
.okr .nd.lead .box b{color:var(--crystal);}
.okr-annual-wrap{text-align:center; position:relative;}
.okr-annual{display:inline-block; background:var(--crystal-25); border:1px solid var(--crystal); color:var(--ink); border-radius:8px; padding:5px 24px; font-size:13px; font-weight:600; letter-spacing:.03em;}
.okr-annual b{font-size:16px;}
.okr-sbs{position:relative;}
.okr-total-side{position:absolute; left:0; top:30px; z-index:2; text-align:left;}
.okr-annual-wrap::after{content:""; display:block; width:0; height:4px; margin:0 auto; border-left:1.5px solid var(--ink-60);}
.okr-legend{color:var(--ink-60); font-size:11px; margin:2px 0 3px;}
.okr .nd.lead .box .pending{font-size:9px; font-weight:600; color:var(--crystal); border:1px solid rgba(195,215,238,.5); border-radius:3px; padding:1px 5px; margin-left:6px; letter-spacing:.04em;}
.okr-insight{display:flex; align-items:center; gap:14px; background:var(--crystal-25); border-left:6px solid var(--crystal); border-radius:6px; padding:3px 18px;}
.okr-insight .ins-lbl{flex:none; font-size:11px; font-weight:600; color:var(--ink-60); border:1px solid var(--crystal); border-radius:4px; padding:3px 10px;}
.okr-insight .ins-txt{font-size:15px; font-weight:700; color:var(--ink); line-height:1.5;}
.okr ul ul ul{position:relative;}
.okr ul ul ul > li{padding-top:10px;}
.okr ul ul ul > li::before,.okr ul ul ul > li::after{height:10px;}
.okr .sgrp-row{display:flex; gap:8px; justify-content:center; align-items:flex-end; position:relative; padding-top:9px;}
.okr .sgrp-row::before{content:""; position:absolute; top:0; left:81px; right:81px; border-top:1.5px solid var(--ln);}
.okr li.emg{padding-top:19px;}
.okr .nd .shr{display:block; font-size:8.5px; font-weight:600; color:var(--ink-60); margin-top:1px; line-height:1.2; white-space:nowrap; text-align:center;}
.okr .nd.big{min-width:246px;}
.okr .nd.big .nm{font-size:16px; margin-bottom:6px;}
.okr .nd.big .box{font-size:13px; padding:6px 14px; margin-top:5px; border-color:var(--ink-60);}
.okr .nd.big .box b{font-size:16px;}
.okr .nd.big .box .lbl{width:36px; font-size:11.5px;}
.okr .nd.big .box.mk{background:var(--crystal);}
.okr .nd.mid{min-width:198px;}
.okr .nd.mid .nm{font-size:14px; margin-bottom:4px;}
.okr .nd.mid .box{font-size:11.5px; padding:2px 11px; margin-top:2px;}
.okr .nd.mid .box b{font-size:14px;}
.okr .nd.mid .box .lbl{width:33px; font-size:10.5px;}
.okr .nd.cat{min-width:138px;}
.okr .nd.cat .nm{font-size:11px; margin-bottom:3px;}
.okr .nd.cat .box{font-size:9.5px; padding:2px 7px;}
.okr .nd.cat .box b{font-size:11px;}
.okr .nd.cat .box .lbl{width:27px; font-size:8.5px;}
.okr .nd.cat .shr{font-size:7.5px;}
/* フル再現テーブル(小型＋余白) */
.skyu{margin:4px auto 0; max-width:99%;}
.skyu-h{font-size:11px; color:var(--ink-60); margin:0 0 2px 2px; letter-spacing:.04em;}
.sk-unit{text-align:right; font-size:9px; color:var(--ink-60); margin:0 2px 3px 0; letter-spacing:.02em; line-height:1.4;}
/* 実デッキ準拠：密な数表はゴシック(Hiragino Sans)＋10px。明朝(本文serif)を継承させない */
table.sk{font-size:10px; border-collapse:collapse; width:100%;
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Helvetica Neue",Arial,sans-serif;}
table.sk.wide{font-size:9.5px;}
table.sk.wide th,table.sk.wide td{padding:1px 2px;}
table.sk.dsp3{font-size:9px;} table.sk.dsp3 th,table.sk.dsp3 td{padding:1px 2px;}
table.sk.dense{font-size:9px;} table.sk.dense th,table.sk.dense td{padding:1px 2px;}
/* 罫線ルール：横線のみ(下罫線)・縦線は使わない。font-family/size:inherit で新CI基盤の
   th,td{font-size:1.02rem} 直指定を打ち消す(これが無いと明朝・巨大化で列が切れる) */
table.sk th,table.sk td{border:none; border-bottom:1pt solid var(--ink-60); padding:1px 3px; text-align:right; white-space:nowrap; line-height:1.2; vertical-align:middle; font-size:inherit; font-family:inherit;}
table.sk th{background:var(--crystal-55); text-align:center; font-weight:600;}
table.sk th.g{background:var(--crystal);}
table.sk td.l,table.sk th.l{text-align:left;}
table.sk td.bd{font-weight:700; font-size:10px; background:var(--white);}
table.sk tr.tot td{background:var(--crystal-25); font-weight:600;}
table.sk tr.grand td{background:var(--crystal); font-weight:700; font-size:9px; border-top:2px solid var(--ink-60); border-bottom:1.5px solid var(--ink-60);}
table.sk tr.grand td.l{font-size:10px;}
table.sk td.dim{color:var(--ink-60);}
table.sk tbody tr:nth-child(even){background:transparent;}
table.sk tr.hl td{background:var(--crystal);}
table.sk tr.hl td.l{font-weight:600;}
/* 所見ブロック(構造化) */
.sho{margin:8px auto 0; max-width:99%;}
.sho-h{font-weight:600; font-size:13px; color:var(--ink); display:inline-block; border-left:3px solid var(--crystal); padding-left:9px; margin-bottom:3px;}
ul.clean.sho-l{margin:4px 0 0;}
ul.clean.sho-l li{font-size:11.5px; margin:3px 0; padding-left:18px; line-height:1.5;}
ul.clean.sho-l li::before{top:8px; width:6px; height:6px;}
.sho .hlmk{background:var(--crystal); padding:0 4px; border-radius:3px;}
/* 考察=スライドの主役：クリスタルカード＋結論リード */
.sho-card{margin:11px auto 0; max-width:99%; background:var(--crystal-25); border-radius:8px; padding:14px 24px 16px; border-left:6px solid var(--crystal);}
.sho-card .sho-h{border-left:0; padding-left:0; font-size:13px; color:var(--ink-60); font-weight:600; letter-spacing:.1em;}
.sho-lead{font-size:16px; font-weight:700; color:var(--ink); line-height:1.6; margin:3px 0 10px;}
.sho-card ul.clean.sho-l li{font-size:12.5px; margin:4px 0;}
.note-c{text-align:center; margin-top:10px;}
/* 本文スライドのタイトルは実デッキ準拠27px(新CI基盤の h2=2rem≒38px を上書き。これが無いと約4割大きい) */
h2.title{font-size:27px; line-height:1.5; margin-bottom:2px;}
.sub{font-size:13px; color:var(--ink-85); margin:6px 0 0;}
/* キッカー/リードを実デッキ準拠に(新CI基盤の .kicker=.8rem≒15px / .lead=1.3rem≒25px を上書き) */
.kicker{font-size:13px;}
.lead{font-size:21px; line-height:1.7;}
/* 日進捗・集計期間(フッターCONFIDENTIALの左隣に1行・フッター高に揃える) */
.period{position:absolute; bottom:15px; left:36px; white-space:nowrap; font-family:var(--serif-en);
  font-size:11px; letter-spacing:.04em; color:var(--ink-60); z-index:3;}
.period b{color:var(--ink); font-weight:600;}
.slide::before{left:auto; right:230px;}
.slide.dark .period{color:rgba(195,215,238,.65);} .slide.dark .period b{color:var(--crystal);}
.notemk{font-size:11.5px; color:var(--ink-60); margin-top:6px;}
/* 章扉 divider(dark・左に縦バー) */
.slide.divider{display:flex; align-items:center; padding:0;}
.divider .dv-bar{width:8px; height:58%; background:var(--crystal); margin:0 42px 0 64px;}
.divider .secno{font-family:var(--serif-en); letter-spacing:.3em; font-size:var(--fs-note); color:var(--crystal); opacity:.75; display:block; margin-bottom:16px;}
.divider .dv-title{font-size:var(--fs-lg); line-height:1.2; margin:0; color:var(--crystal);}
.divider .dv-sub{font-size:18px; color:var(--crystal); opacity:.85; margin-top:18px; max-width:62ch;}
</style>
"""
