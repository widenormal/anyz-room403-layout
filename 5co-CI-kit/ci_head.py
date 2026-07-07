#!/usr/bin/env python3
"""
ci_head.py — 正典CSS連結の唯一の標準方式（共通HEAD）

案件ビルダー（NatureLab build_html_monthly.py / WELLA 等）が、正典フォーマットCSSを
**コピー・inline再実装せずに**デッキHTMLへ注入するための共有ヘルパ。

なぜ存在するか（2026-07-07 WELLA 世代遅れ事故・共通HEAD化依頼）:
  各案件が正典CSSを手元へコピー／自前再実装すると、正典の改定（#642 Hoefler化・
  #709 縦罫撤去 等）が自動では届かず、案件ごとに「連結方式の即興実装」が新たな
  ドリフト源になる。連結方式を正典側で1つに固定し、全案件が同一方式で消費する。

設計原則:
  - **VERSION が唯一の宣言源**。連結対象CSSは本スクリプトにハードコードせず、
    VERSION の `format:` 行から読む（版上げ時は VERSION 更新だけで全案件に追従）。
  - 本スクリプトは kit 内に置かれ、自分の場所（__file__）から kit を特定する
    （git派生リポでも Drive 案件コピーでも、kit ごと配布されるためパス設定不要）。
  - 出力の先頭に版スタンプコメントを焼き込む（「ci_head 経由で組まれたか」を
    parity 検査・監査で機械判定できるマーカー）。

使い方（案件ビルダー側・これ以外の連結方式は禁止）:
  # Python から（推奨）
  import sys; sys.path.insert(0, "<kitへのパス>")   # 例: "5co-CI-kit"
  import ci_head
  html = template.replace("<!--CI_HEAD-->", ci_head.style_block())

  # subprocess / シェルから
  python3 5co-CI-kit/ci_head.py            # <style>…</style> ブロックを stdout へ
  python3 5co-CI-kit/ci_head.py --css      # 生CSSのみ（<style>タグなし）
  python3 5co-CI-kit/ci_head.py --files    # 連結対象ファイル一覧
  python3 5co-CI-kit/ci_head.py --version  # 現行版タグ（例: v3.3）

終了コード: 0=成功 / 1=VERSION不在・宣言CSS欠落（fail-closed: 欠けたまま黙って
組ませない）
"""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent


def _version_text() -> str:
    vf = KIT / "VERSION"
    if not vf.exists():
        raise FileNotFoundError(
            f"VERSION が見つかりません: {vf}（kit コピーが不完全。正典から再取得してください）"
        )
    return vf.read_text(encoding="utf-8")


def version_tag() -> str:
    """VERSION 先頭行の版タグ（例: 'v3.3'）。"""
    return _version_text().splitlines()[0].strip()


def css_files() -> list:
    """VERSION の format: 行に宣言された CSS ファイル群（宣言順・kit相対）。"""
    m = re.search(r"^format:\s*(.+)$", _version_text(), re.MULTILINE)
    if not m:
        raise ValueError("VERSION に format: 行がありません（正典の宣言形式が変わった場合は本ヘルパも追従させること）")
    names = re.findall(r"[\w][\w.-]*\.css", m.group(1))
    if not names:
        raise ValueError("VERSION の format: 行に .css 宣言がありません")
    missing = [n for n in names if not (KIT / n).exists()]
    if missing:
        raise FileNotFoundError(
            f"VERSION 宣言のCSSが kit に見つかりません: {', '.join(missing)}（kit コピーが不完全）"
        )
    return names


def head_css() -> str:
    """現行フォーマットCSS（VERSION宣言・宣言順）を連結して返す（生CSS）。"""
    parts = []
    for name in css_files():
        body = (KIT / name).read_text(encoding="utf-8")
        parts.append(f"/* ==== {name}（正典 5co-CI-kit・編集禁止） ==== */\n{body}")
    return "\n\n".join(parts)


def style_block() -> str:
    """HEADに挿入する <style> ブロック。先頭の版スタンプが ci_head 経由の証跡になる。"""
    tag = version_tag()
    files = " + ".join(css_files())
    stamp = (
        f"/* 5co-CI ci_head {tag} — {files}\n"
        f"   正典連結（5co-CI-kit/ci_head.py 生成・手編集禁止・CSSコピー/inline再実装禁止） */"
    )
    return f"<style>\n{stamp}\n{head_css()}\n</style>"


def main(argv):
    try:
        if "--version" in argv:
            print(version_tag())
        elif "--files" in argv:
            print("\n".join(css_files()))
        elif "--css" in argv:
            print(head_css())
        else:
            print(style_block())
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"NG: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:
        # `ci_head.py | head` 等でパイプ先が先に閉じた場合は正常終了扱い
        sys.exit(0)
