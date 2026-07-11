# SLIDE-PATTERN-scatter-bubble-positioning

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** scatter-bubble-positioning
**概要：** X軸×Y軸の平面上に、規模を円の大きさで表したバブルを6〜8個配置するポジショニングマップ。中央の十字参照線で4象限に分け、自社バブルを濃グレーで強調して相対的な立ち位置を一目で示す。
**適したシーン：** 競合ポジショニング分析、事業ポートフォリオの俯瞰、市場マッピング、M&A候補・パートナー候補の比較

## Structure（構造）

```yaml
layout: scatter-bubble-positioning
title_area: true
content_area:
  direction: row
  padding: "16px 48px"
  gap: 24px
  children:
    - id: chart_body
      width: "78%"
      type: svg_scatter
      elements:
        - type: plot_area
          background: "#FAFAFA"
          border: "#CCCCCC"
        - type: x_axis
          label: "市場成長率"
          end_labels: ["低", "高"]
          color: "#666666"
        - type: y_axis
          label: "収益性"
          end_labels: ["低", "高"]
          writing_mode: rotated
          color: "#666666"
        - type: quadrant_cross_lines
          style: dashed
          color: "#CCCCCC"
        - type: quadrant_corner_labels
          font_size: 10px
          color: "#AAAAAA"
          texts: ["高収益・低成長（安定領域）", "高収益・高成長（注力領域）",
                  "低収益・低成長（撤退検討）", "低収益・高成長（投資判断）"]
        - type: bubbles
          count: 6-8
          size_meaning: "売上規模（円の面積に比例）"
          own_company:
            fill: "#555555"
            label_color: "#FFFFFF"
          competitors:
            fill: ["#CCCCCC", "#D8D8D8"]
            stroke: "#AAAAAA"
          labels: "社名＋売上値（数値ラベル必須）"
    - id: legend_area
      width: "22%"
      elements:
        - type: legend_item
          swatch: "circle_dark"
          label: "自社"
        - type: legend_item
          swatch: "circle_light"
          label: "競合他社"
        - type: legend_item
          swatch: "circle_size_pair"
          label: "円の大きさ＝売上規模"
        - type: reading_note
          text: "図の読み方の1〜2行注記"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| X軸ラベル・端ラベル | 横軸の意味と方向（低→高）を示す | 軸名4〜8文字＋「低」「高」 |
| Y軸ラベル・端ラベル | 縦軸の意味と方向を示す（縦書き回転） | 軸名3〜6文字＋「低」「高」 |
| 十字参照線 | 平面を4象限に分割し解釈を助ける | テキストなし（破線） |
| 象限コーナーラベル | 各象限の戦略的な意味づけ | 各8〜14文字 |
| バブル（円） | 各社・各事業の位置と規模 | 6〜8個、社名2〜8文字 |
| バブル数値ラベル | 規模の実数値（売上等） | 「85億円」など4〜7文字 |
| 自社バブル強調 | 濃グレー塗り＋白文字で自社を識別 | 1個のみ |
| 凡例エリア | 色・大きさの意味を補足説明 | 3〜4項目＋注記1〜2行 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-scatter-bubble-positioning.md を参照して、
以下の競合ポジショニングマップのスライドを作成してください。

【軸の定義】
- X軸: 市場成長率（低→高）
- Y軸: 収益性（低→高）

【バブル（社名 / X位置 / Y位置 / 売上規模）】
- 自社: 中央やや左・高収益 / 85億円（強調）
- A社: 低成長・高収益 / 40億円
- B社: 高成長・高収益 / 120億円
- C社: 低成長・中収益 / 25億円
- D社: 高成長・中収益 / 60億円
- E社: 高成長・低収益 / 15億円
- F社: 低成長・低収益 / 30億円

【スライドタイトル】
当社はどこで戦うべきか — 競合ポジショニングマップ
```

### 注意点
- バブルは6〜8個が適切（多すぎるとラベルが重なり判読不能になる）
- バブル同士・バブルと軸ラベルが重ならないよう座標を調整する（円の中心間距離 > 半径の和）
- 円の大きさは規模の平方根に比例させる（面積が規模を表すため。半径を規模に比例させない）
- 自社は必ず濃グレー（#555555 等）＋白文字で1個だけ強調する
- 軸の意味は内容に合わせて変更可能（例：「価格帯」×「品質評価」「シェア」×「成長率」）
- 数値ラベル（売上等）は全バブルに必ず付ける（規模感の根拠を示すため）
