#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ページ参照トークンの解決（2026-07-09 新設・NatureLab 週次デッキで確立）。

資料内の「→P◯」を直書きせず `{{PG:タイトル部分文字列}}` と書いておくと、
ビルド時に**実ページ番号へ自動解決**する。参照先スライドが無ければビルド失敗（参照切れゲート）。
ページの並べ替え・増減に自動追従し、参照ズレを構造的に防ぐ。

想定利用（案件ビルダーの後処理レイヤーから呼ぶ）:
    from ci_pagerefs import resolve_pagerefs
    slides = resolve_pagerefs(slides)   # slides: List[str]（<section class="slide">…</section> の配列）

各スライドの <h2>…</h2> をタイトル索引にする。`{{PG:key}}` は「key を含む最初のスライドの
1始まりページ番号」へ置換する。未解決キーがあれば SystemExit で停止（＝参照切れゲート）。

タイトル以外を索引にしたい場合は title_selector（正規表現）を差し替える。
"""
import re, sys

_TAG=re.compile(r'<[^>]+>')

def _titles(slides, title_pat=r'<h2[^>]*>(.*?)</h2>'):
    rx=re.compile(title_pat, re.S)
    out=[]
    for s in slides:
        m=rx.search(s)
        out.append(_TAG.sub('', m.group(1)).strip() if m else '')
    return out

def resolve_pagerefs(slides, title_pat=r'<h2[^>]*>(.*?)</h2>'):
    """slides 内の {{PG:key}} をページ番号へ置換して返す。参照切れは SystemExit。"""
    titles=_titles(slides, title_pat)
    def find(key):
        for i,t in enumerate(titles):
            if key in t:
                return i+1
        raise SystemExit(f"参照切れ: ページ参照キー『{key}』に一致するスライド見出しがありません")
    return [re.sub(r'\{\{PG:([^}]+)\}\}', lambda m: str(find(m.group(1).strip())), s)
            for s in slides]

if __name__=="__main__":
    # 自己テスト（引数なし）
    demo=['<section class="slide"><h2>OKR 進捗</h2>詳細 →P{{PG:ドリルダウン}}</section>',
          '<section class="slide"><h2>S級ブランド ドリルダウン</h2>本文</section>']
    print('\n'.join(resolve_pagerefs(demo)))
