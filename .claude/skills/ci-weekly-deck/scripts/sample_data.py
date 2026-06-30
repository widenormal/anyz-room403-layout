#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sample_data.py — worked sample 用のダミー構造データ。

元の集計用シートと **同じ列レイアウト** を、架空ブランド(ブランドA/B/C…)・架空カテゴリ・
ダミー数値で再現する。実顧客名・実ブランド名・実数値は一切含まない。
build_deck.py は config に実データJSONが無い場合これを使い、14枚を生成する。

実運用では extract_deck_data.py が出力する deck_data.json 等(同じ列構造)に差し替える。
"""


def _row(maxc, cells=None):
    """列インデックス→値 の辞書から、長さ maxc+1 の行(list)を作る。"""
    r = [""] * (maxc + 1)
    for k, v in (cells or {}).items():
        r[int(k)] = v
    return r


# ----- S級フル表(skyu_full 相当) ----- 列: 5=brand,6=cat,7目標,8目標YoY,9実績,10比率,11達成,
#       12着地,13YoY見込,21日販万,22MoM,23YoY,33広告売上,34比率,35ROAS,36計画費,37実績費
def _skyu_brand(brand, cats, base):
    """総合行(全体（発送）)＋カテゴリ行を返す。cats=[(cat名, 倍率), ...]"""
    rows = []
    # 全体（発送）= カテゴリ合算のダミー
    tgt = base * 1_000_000
    act = int(tgt * 0.82)
    fc = int(tgt * 0.99)
    rows.append(_row(37, {5: brand, 6: "全体（発送）", 7: tgt, 8: "118.0%", 9: act, 10: "",
                            11: "82.0%", 12: fc, 13: "115.0%", 21: int(base * 33), 22: "103%",
                            23: "118%", 33: int(tgt * 0.12), 34: "", 35: "480%", 36: "15.0%", 37: "12.0%"}))
    for i, (c, mul) in enumerate(cats):
        t = int(base * mul * 1_000_000)
        rows.append(_row(37, {6: c, 7: t, 8: f"{110 + i * 6}.0%", 9: int(t * (0.8 + 0.05 * i)),
                                10: "", 11: f"{80 + i * 7}.0%", 12: int(t * 0.98), 13: f"{112 + i * 8}.0%",
                                21: int(base * mul * 33), 22: "101%", 23: f"{115 + i * 5}%",
                                33: int(t * 0.1), 34: "", 35: f"{400 + i * 60}%", 36: "15.0%", 37: f"{10 + i}.0%"}))
    return rows


def skyu_full():
    data = [_row(37), _row(37)]  # header 2行(builderは rows[2:] を使う)
    data += _skyu_brand("ブランドA", [("カテゴリ1", 0.55), ("カテゴリ2", 0.20)], base=283)
    data += _skyu_brand("ブランドB", [("カテゴリ1", 0.30)], base=120)
    data += _skyu_brand("ブランドC", [("カテゴリ1", 0.40)], base=96)
    return data


# ----- DSP(列: 2brand,3予算,4投下,5進捗,6DPV,7DPVR,8eCPDPV,9購入,10CVR,11売上万,12客単価,
#       13ROAS,14前週,16NtB,17新規CPP,18目標CPP,19前週CPP,21SnSS,22S単価)
def _dsp_row(brand, k):
    return _row(22, {2: brand, 3: 70 + k * 5, 4: 65 + k * 5, 5: "95%", 6: 120000 + k * 9000,
                       7: "0.45%", 8: 12 + k, 9: 900 + k * 80, 10: "0.7%", 11: 60 + k * 8,
                       12: 6800, 13: f"{540 + k * 30}%", 14: f"{520 + k * 20}%", 16: 700 + k * 50,
                       17: 962, 18: 1200, 19: 1100, 21: 600 + k * 40, 22: 1100})


def _deck_data():
    # DSP: 6,7,8=S級, 9=S級小計, 11-15=EM, 16=EM小計, 18=総合計。実デッキは3表(合算/P+のみ/Bonus)
    def _dsp_set(off):
        d = [_row(22) for _ in range(19)]
        for idx, (b, k) in zip((6, 7, 8), [("ブランドA", 0), ("ブランドB", 1), ("ブランドC", 2)]):
            d[idx] = _dsp_row(b, k + off)
        d[9] = _dsp_row("S級 小計", 3 + off)
        for idx, (b, k) in zip((11, 12, 13, 14, 15),
                               [("EM-1", 0), ("EM-2", 1), ("EM-3", 2), ("EM-4", 3), ("EM-5", 4)]):
            d[idx] = _dsp_row(b, k + off)
        d[16] = _dsp_row("EM 小計", 5 + off)
        d[18] = _dsp_row("総合計", 6 + off)
        return d
    dsp, dsp_p, dsp_b = _dsp_set(0), _dsp_set(1), _dsp_set(2)

    # SA: 5,6,7=S級,8=小計,10-18=EM,19=小計,21=全体, 29-35=ファネル
    def sa_row(brand, k):
        return _row(17, {2: brand, 3: 50 + k * 4, 4: 47 + k * 4, 5: "94%", 6: "89.6%",
                           7: 200000 + k * 12000, 8: 3000 + k * 200, 9: "1.5%", 10: 35, 11: 120 + k * 9,
                           12: "4.0%", 13: 700, 14: 45 + k * 6, 15: 3700, 16: f"{300 + k * 25}%", 17: f"{290 + k * 20}%"})
    sa = [_row(17) for _ in range(36)]
    for idx, (b, k) in zip((5, 6, 7), [("ブランドA", 0), ("ブランドB", 1), ("ブランドC", 2)]):
        sa[idx] = sa_row(b, k)
    sa[8] = sa_row("S級 小計", 3)
    for i, idx in enumerate(range(10, 15)):  # EM 5ブランド(10-14)
        sa[idx] = sa_row(f"EM-{i + 1}", i)
    sa[15] = sa_row("EM 小計", 9)
    sa[17] = sa_row("全体", 10)
    # ファネル: (一般, 指名)×3ブランド + S級合計
    for j, (g, b) in enumerate([(29, 30), (31, 32), (33, 34)]):
        sa[g] = sa_row(f"ブランド{'ABC'[j]} 一般", j)
        sa[b] = sa_row(f"ブランド{'ABC'[j]} 指名", j + 5)
    sa[35] = sa_row("S級 合計", 7)

    # エマージング drill-down(ブランド単位＋PV列): 4=brand,5='grand',6目標,7目標YoY,8実績,
    #   10達成,11着地見込,12YoY見込,13PV目標,14PV実績,15PV達成,16計画(万),17実績(万),18ROAS,19TACoS
    def emd(brand, base, yoy="133%", fyoy="140%", ad=True, grand=False):
        t = base * 1_000_000
        c = {4: brand, 6: t, 7: yoy, 8: int(t * 0.75), 10: "75.0%", 11: int(t * 1.05), 12: fyoy,
             13: base * 5000, 14: int(base * 4200), 15: "84.0%"}
        if grand:
            c[5] = "grand"
        if ad:
            c.update({16: base * 120000, 17: base * 110000, 18: "380%", 19: "9.0%"})
        return _row(19, c)
    emdrill = [emd("EM合算（主要計）", 126, grand=True),
               emd("EM-1（旗艦）", 50), emd("EM-2", 30, ad=False),
               emd("EM-3", 20), emd("EM-4", 12, fyoy="166%"), emd("EM-5", 8, fyoy="60%")]

    # エマージング(ブランドレベル一覧): 4brand,6目標,7目標YoY,8実績,9達成,10着地,11着地YoY,15PV達成
    def em_brand(brand, base):
        return _row(15, {4: brand, 6: f"¥{base * 1_000_000:,}", 7: "130%", 8: f"¥{int(base * 0.7 * 1e6):,}",
                           9: "70.0%", 10: f"¥{int(base * 1.05 * 1e6):,}", 11: "140%", 15: "82.0%"})
    em = [em_brand(f"EM-{i}", b) for i, b in enumerate([50, 30, 20, 12, 8, 5, 3, 2, 1, 1], start=1)]
    em.append(_row(15, {4: "EM合計", 6: f"¥{126_000_000:,}", 7: "133%", 8: f"¥{94_000_000:,}",
                          9: "75.2%", 10: f"¥{132_000_000:,}", 11: "140%", 15: "82.2%"}))

    return {"DSP": dsp, "DSP_P": dsp_p, "DSP_B": dsp_b, "SA": sa,
            "エマージング_drill": emdrill, "エマージング": em}


# ----- 香調別 月別(lavon 相当): v[3]=hdr(月ラベル), 行は col1=ラベル
def lavon_data():
    months = [f"2025-{m}" for m in range(1, 13)] + [f"2026-{m}" for m in range(1, 8)]  # 19ヶ月
    hdr = _row(1 + len(months))
    hdr[1] = "年"
    for j, m in enumerate(months):
        hdr[2 + j] = m
    v = [_row(1), _row(1), _row(1), hdr]
    labels = ["本体_香調1", "詰替_香調1", "本体_香調2", "詰替_香調2", "本体_香調3", "詰替_香調3",
              "洗剤本体_香調1", "洗剤詰替_香調1", "洗剤本体_香調2", "洗剤詰替_香調2"]
    for li, lbl in enumerate(labels):
        r = _row(1 + len(months), {1: lbl})
        for j in range(len(months)):
            r[2 + j] = (300000 + li * 40000) + j * 9000  # 右肩上がりのダミー
        v.append(r)
    return v


# ----- PD目標表 行(name, cls, 合計円, アーリー円, 本セール円, YoY, eYoY, mYoY, 本ｾﾙ割合, 昨対成長円, 備考)
def pd_rows():
    return [
        ("全体(ベンダーのみ)", "tot", 484_000_000, 151_000_000, 333_000_000, "116%", "120%", "112%", "68%", 67_000_000, "—"),
        ("主要担当", "bold", 362_000_000, 114_000_000, 248_000_000, "136%", "140%", "131%", "67%", 96_000_000, "昨対+0.96億（必達）"),
        ("ブランドA", "", 107_000_000, 35_000_000, 72_000_000, "126%", "134%", "122%", "67%", 22_000_000, "現実的"),
        ("ブランドB", "", 65_000_000, 21_000_000, 44_000_000, "120%", "128%", "116%", "67%", 11_000_000, "ちょいチャレ"),
        ("ブランドC", "", 96_000_000, 29_000_000, 67_000_000, "109%", "115%", "107%", "70%", 8_000_000, "現実的"),
        ("EM-1", "", 11_000_000, 4_000_000, 7_000_000, "229%", "195%", "253%", "65%", 6_000_000, "高伸長"),
        ("EM-2", "", 4_000_000, 1_600_000, 2_900_000, "122%", "102%", "137%", "65%", 800_000, ""),
    ]


# ----- 顧客固有の設定(本来は config / 差し替え領域)。sample は架空値 -----
MARKET = {"カテゴリ1": 2424, "カテゴリ2": 619, "カテゴリ3": 1753, "カテゴリ4": 2388}  # 推計市場月商(百万円)
SKYU_HL = {("ブランドA", "カテゴリ2")}
EMRG_HL = {"EM-3"}
FUNNEL_GROUPS = [("ブランドA", 29, 30), ("ブランドB", 31, 32), ("ブランドC", 33, 34)]
FUNNEL_TOTAL = 35
LAVON_SECTIONS = [
    {"head": "柔軟剤入り洗濯洗剤 月別売上（香調別・本体＋詰め替え）", "title": "柔軟剤入り洗剤",
     "rows": [("香調1", "洗剤本体_香調1", "洗剤詰替_香調1"), ("香調2", "洗剤本体_香調2", "洗剤詰替_香調2")]},
    {"head": "香りシリーズ 月別売上（香調別・本体＋詰め替え）", "title": "香りシリーズ",
     "rows": [("香調1", "本体_香調1", "詰替_香調1"), ("香調2", "本体_香調2", "詰替_香調2"),
              ("香調3", "本体_香調3", "詰替_香調3")]},
]
EMRG_ANNOTATE = {"EM-1": "（旗艦）"}


def all_data():
    d = _deck_data()
    return {
        "skyu_full": skyu_full(),
        "deck_data": d,
        "lavon": lavon_data(),
        "pd_rows": pd_rows(),
        "market": MARKET, "skyu_hl": SKYU_HL, "emrg_hl": EMRG_HL,
        "funnel_groups": FUNNEL_GROUPS, "funnel_total": FUNNEL_TOTAL,
        "lavon_sections": LAVON_SECTIONS, "emrg_annotate": EMRG_ANNOTATE,
    }
