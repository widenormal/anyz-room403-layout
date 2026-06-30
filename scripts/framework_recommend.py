#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フレームワーク・レコメンダ（CIスライド制作の標準搭載AGENT用の決定論アシスト）。

目的: 制作中のスライドの「言いたいこと/戦略/内容」を渡すと、SLIDE-PATTERN-INDEX.md の
99 パターンから (1)内容に合う図 と (2)未経験かもしれないフレームワーク図(発見枠) を
ショートリスト出力する。最終的な「この戦略に効く理由」の一言はスキル(Claude)が付ける。

設計: 外部LLM不要・INDEXのメタデータ(概要/適したシーン)だけで日本語キーワード重なりスコア。
      framework系カテゴリ/名称にはディスカバリ加点し、全社員が"知らない型"に触れられるようにする。

使い方:
  framework_recommend.py "現状と目指す姿のギャップを2軸で整理したい" [--n 3] [--json]
  framework_recommend.py --list-categories
"""
from __future__ import annotations
import argparse, json, re, sys, pathlib

INDEX = pathlib.Path(__file__).resolve().parent.parent / "docs/SLIDE-PATTERN/SLIDE-PATTERN-INDEX.md"

# 「戦略フレームワーク図」寄りのカテゴリ（発見枠で優先的に拾う＝未経験に触れさせる）
FRAMEWORK_CATEGORIES = {"フロー・ステップ", "図解・ダイアグラム", "グラフ・データ",
                        "テーブル・比較", "KPI・まとめ"}
# 名称に含まれるとフレームワーク性が高い語（2x2・サイクル・ファネル等）
FRAMEWORK_NAME_HINTS = ["matrix", "quadrant", "2x2", "2x3", "2x4", "cycle", "hub", "spoke",
                        "funnel", "roadmap", "pyramid", "venn", "staircase", "timeline",
                        "pdca", "tree", "flow", "step", "dashboard", "kpi", "kgi", "polygon"]


def parse_index(path: pathlib.Path) -> list[dict]:
    """INDEX.md のカテゴリ別テーブルを {name,category,summary,scenes} のリストに。"""
    rows, cat = [], ""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+\S*\s*(.+?)\s*$", line)
        if m:
            cat = m.group(1).strip()
            continue
        if line.startswith("|") and "パターン名" not in line and "---" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.match(r"^[a-z0-9-]+$", cells[0]):
                rows.append({"name": cells[0], "category": cat,
                             "summary": cells[1], "scenes": cells[2]})
    return rows


_STOP_BIGRAM = {"する", "した", "して", "から", "こと", "もの", "など", "ため", "よう",
                "では", "には", "という", "といっ", "やす", "すい", "たい", "れる", "られ"}


def tokens(text: str) -> set[str]:
    """形態素解析器なしで頑健に当てるため、日本語は文字バイグラム＋英単語でトークン化。
    （助詞で区切れず句全体が1語になる問題を回避。「リスク」⊂「リスクの大きさ」も拾える）"""
    text = text.lower()
    out = set()
    for run in re.findall(r"[一-龥ぁ-んァ-ヶ々ー]+", text):
        for i in range(len(run) - 1):
            bg = run[i:i + 2]
            if bg not in _STOP_BIGRAM:
                out.add(bg)
    out |= set(re.findall(r"[a-z]{3,}", text))
    return out


def is_framework(p: dict) -> bool:
    if p["category"] in FRAMEWORK_CATEGORIES:
        return True
    return any(h in p["name"] for h in FRAMEWORK_NAME_HINTS)


def score(query_tok: set[str], p: dict) -> int:
    """適したシーン>概要>カテゴリ の重みでキーワード重なりを採点。"""
    s = 0
    s += 3 * len(query_tok & tokens(p["scenes"]))
    s += 2 * len(query_tok & tokens(p["summary"]))
    s += 1 * len(query_tok & tokens(p["category"]))
    return s


def recommend(query: str, n: int = 3) -> dict:
    pats = parse_index(INDEX)
    qt = tokens(query)
    scored = sorted(((score(qt, p), p) for p in pats), key=lambda x: -x[0])
    best = [p for sc, p in scored if sc > 0][:n]
    best_names = {p["name"] for p in best}
    # 発見枠: 内容にゆるく当たる framework系で、最適に未採用のもの（未経験誘導）
    discovery = [p for sc, p in scored
                 if p["name"] not in best_names and is_framework(p) and sc > 0][:2]
    if not discovery:  # ヒット薄でも framework系を1つは見せる
        discovery = [p for sc, p in scored
                     if p["name"] not in best_names and is_framework(p)][:1]
    return {"query": query, "best": best, "discovery": discovery}


def fmt(p: dict, tag: str) -> str:
    fw = "  〔framework〕" if is_framework(p) else ""
    return (f"[{tag}] {p['name']}  ({p['category']}){fw}\n"
            f"    概要: {p['summary'][:70]}\n"
            f"    適: {p['scenes'][:70]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-categories", action="store_true")
    a = ap.parse_args()
    if a.list_categories:
        pats = parse_index(INDEX)
        from collections import Counter
        for cat, c in Counter(p["category"] for p in pats).most_common():
            mark = "★framework" if cat in FRAMEWORK_CATEGORIES else ""
            print(f"{c:3d}  {cat} {mark}")
        return
    if not a.query:
        sys.exit("ERROR: 提案したいスライドの内容/戦略を渡してください")
    r = recommend(a.query, a.n)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return
    print(f"■ 入力: {r['query']}\n")
    if r["best"]:
        print("● 内容に合う図（最適）")
        for p in r["best"]:
            print(fmt(p, "最適"))
    else:
        print("（直接マッチ無し。発見枠から選ぶか、内容を具体化してください）")
    if r["discovery"]:
        print("\n○ 未経験かも？のフレームワーク（発見枠）")
        for p in r["discovery"]:
            print(fmt(p, "発見"))
    print("\n※ 各候補に「この戦略に効く理由」を一言添えて提示し、最終選択はユーザーに委ねる。")


if __name__ == "__main__":
    main()
