# SLIDE-PATTERN-waterfall-bridge-chart

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** waterfall-bridge-chart
**概要：** 期首値の柱から期末値の柱まで、増加要因（薄グレーの浮き棒）と減少要因（濃グレーの浮き棒）を階段状に並べ、点線コネクタでつなぐウォーターフォール（ブリッジ）チャート。各棒に増減値ラベルを付け、「何がいくら効いて期首から期末に変わったのか」を1枚で示す。
**適したシーン：** 予実差異の要因分解、前期比の利益ブリッジ、予算・コストの増減内訳説明、KPI変動の要因説明

## Structure（構造）

```yaml
layout: waterfall-bridge-chart
title_area: true
content_area:
  direction: column
  padding: "14px 48px 10px"
  gap: 6px
  children:
    - id: chart_header
      elements:
        - type: unit_label
          text: "単位: 百万円"
          font_size: 11px
          color: "#999999"
        - type: legend
          items:
            - { label: "期首・期末実績", swatch: "#333333" }
            - { label: "増加要因", swatch: "#D8D8D8" }
            - { label: "減少要因", swatch: "#666666" }
    - id: chart_body
      elements:
        - type: y_axis
          ticks: [0, 100, 200, 300, 400, 500]
          font_size: 10px
          color: "#AAAAAA"
        - type: waterfall_plot
          height: 300px
          scale: "0.58px / 単位値"
          bars:
            - { kind: anchor,   label: "前期営業利益", value: 320,  color: "#333333" }
            - { kind: increase, label: "売上増加",     value: +120, color: "#D8D8D8" }
            - { kind: increase, label: "原価率改善",   value: +45,  color: "#D8D8D8" }
            - { kind: decrease, label: "人件費増加",   value: -80,  color: "#666666" }
            - { kind: decrease, label: "販促費増加",   value: -55,  color: "#666666" }
            - { kind: anchor,   label: "当期営業利益", value: 350,  color: "#333333" }
          connectors:
            style: "1px dashed #999999"
            position: "各棒の右端から次の棒まで、累計水準の高さで接続"
    - id: x_labels
      elements:
        - type: category_labels
          font_size: 11px
          color: "#555555"
    - id: reading_note
      elements:
        - type: note
          text: "図の読み方: 左端の前期実績から増減要因を階段状に積み上げ、右端の当期実績に至る内訳を示す"
          font_size: 11px
          color: "#999999"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 期首・期末の柱（#333333） | 比較の起点と終点の実績値 | 値ラベル＋カテゴリ名各2〜6文字 |
| 増加要因の浮き棒（#D8D8D8） | プラスに効いた要因 | 2〜4本、要因名5文字前後 |
| 減少要因の浮き棒（#666666） | マイナスに効いた要因 | 2〜4本、要因名5文字前後 |
| 増減値ラベル | 各要因の寄与額を明示 | 「+120」「−80」等、符号必須 |
| 点線コネクタ | 累計水準を隣の棒へ引き継ぐ視線誘導 | テキストなし |
| Y軸目盛・単位ラベル | 値のスケールを示す | 「単位: 百万円」等 |
| 凡例 | 棒の濃淡の意味（実績/増加/減少） | 3項目固定 |
| 図の読み方 | 初見の読者への読解ガイド | 1文40〜60文字 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-waterfall-bridge-chart.md を参照して、
以下の営業利益ブリッジをウォーターフォールチャートで示すスライドを作成してください。

【期首】前期営業利益: 320百万円
【増加要因】
- 売上増加: +120百万円
- 原価率改善: +45百万円
【減少要因】
- 人件費増加: -80百万円
- 販促費増加: -55百万円
【期末】当期営業利益: 350百万円

【スライドタイトル】
営業利益は前期比+30百万円 — 売上増が人件費増を上回った

【単位】百万円
```

### 注意点
- 期首＋各増減の累計＝期末になるよう、必ず数値の整合を検算してから描画する（合わない場合は「その他」で調整項を立てる）
- 要因の棒は4〜5本が上限（多い場合は小さい要因を「その他」に集約）
- 浮き棒の高さと位置はプロット高さに対するスケール係数（px/単位値）で計算する。目分量で置かない
- 増加＝薄グレー・減少＝濃グレーの濃淡ルールを崩さない（凡例と必ず一致させる）
- 値ラベルには符号（+/−）を必ず付け、期首・期末の柱は符号なしの実績値とする
- 要因の並び順は「増加要因→減少要因」または時系列・重要度順のいずれかに統一する
