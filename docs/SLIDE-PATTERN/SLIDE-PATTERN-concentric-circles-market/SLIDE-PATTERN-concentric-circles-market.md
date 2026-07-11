# SLIDE-PATTERN-concentric-circles-market

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** concentric-circles-market
**概要：** 中心から TAM→SAM→SOM の3重の入れ子円（下端揃え・外ほど薄いグレー）で市場の階層を示す図。各円に市場名＋金額を置き、引き出し線で右側に詳細説明を並べる。SVGで描画する。
**適したシーン：** 市場規模の階層説明（TAM/SAM/SOM）、ターゲット顧客の絞り込み、コア事業→周辺領域の層構造、対象範囲（スコープ）の段階整理

## Structure（構造）

```yaml
layout: concentric-circles-market
title_area: true
content_area:
  direction: row
  align: center
  padding: "16px 48px"
  children:
    - id: circles_canvas
      type: composite
      elements:
        - type: nested_circles_svg
          size: "480x410"
          align: bottom      # 3円は下端揃えの入れ子
          circles:           # 外→内。外ほど薄いグレー
            - { name: "TAM", value: "5,000億円", r: 195, fill: "#F5F5F5" }
            - { name: "SAM", value: "1,200億円", r: 130, fill: "#E8E8E8" }
            - { name: "SOM", value: "150億円",   r: 68,  fill: "#D8D8D8" }
          stroke: "#AAAAAA"
          labels: "各円の上部空きスペースに市場名＋金額を配置"
          leader_lines:
            from: "各円の右端"
            to: "キャンバス右端"
            style: "1px dashed #AAAAAA"
        - type: circle_descriptions
          position: "引き出し線の高さに揃えて右側に配置"
          items:
            - name: "TAM — 獲得可能な市場全体"
              value: "5,000億円"
              text: "国内バックオフィスSaaS市場の総額。理論上の最大市場規模。"
            - name: "SAM — 自社が狙えるセグメント"
              value: "1,200億円"
              text: "従業員300名以下の中小企業向けセグメント。自社製品の対象範囲。"
            - name: "SOM — 現実的に獲得できる市場"
              value: "150億円"
              text: "3年以内に自社の販路・営業体制で到達可能な範囲。事業計画の根拠。"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 入れ子円（3層） | 全体→絞り込みの包含関係を面積で示す | 2〜4層 |
| 円内ラベル | 各層の名称＋金額 | 名称2〜6文字＋数値 |
| 円の濃淡 | 内側（コア）ほど濃く、焦点を視覚化 | テキストなし |
| 引き出し線 | 円と右側説明の対応を示す | 破線1px |
| 詳細説明 | 各層の定義・算出根拠を補足 | 名称＋金額＋本文30〜50文字 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-concentric-circles-market.md を参照して、
以下の市場規模を同心円で示したスライドを作成してください。

【市場の階層（外→内）】
- TAM: 5,000億円 — 国内バックオフィスSaaS市場の総額
- SAM: 1,200億円 — 従業員300名以下の中小企業セグメント
- SOM: 150億円 — 3年以内に自社販路で到達可能な範囲

【スライドタイトル】
狙う市場は150億円 — 全体の3%だが自社販路で確実に取れる範囲
```

### 注意点
- 円は2〜4層が適切（5層以上はラベルが入らず判読性が落ちる）
- 包含関係（内側は必ず外側の部分集合）が成立する内容にのみ使う。並列な区分にはベン図や横並び図を使う
- 円の面積比を金額比に厳密一致させる必要はないが、大小の順序は必ず数値と一致させる（内側が外側より大きい数値は不可）
- 各金額には算出根拠（出典・推計方法）を持たせ、詳細説明か発表者ノートに残す。推測で数値を置かない
- ラベルの用語（TAM/SAM/SOM）は初出時に日常語の併記を推奨（例:「TAM＝獲得可能な市場全体」）
- 段階的な減少プロセス（応募→面接→採用等）を見せたい場合はファネル図、積み上げ階層は layered-pyramid-hierarchy を使う
