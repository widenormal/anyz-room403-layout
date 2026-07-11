# SLIDE-PATTERN-slope-chart-before-after

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** slope-chart-before-after
**概要：** 左右2本の縦軸（2時点）の間を項目ごとの直線で結び、線の傾きで増減を直感的に見せるスロープチャート。増加項目を濃グレー太線で強調し、各端点に項目名＋値ラベルを付ける。
**適したシーン：** 2時点間の項目別変化（事業別売上の実績vs計画）、順位変動、施策前後の指標比較、ポートフォリオの構造転換の説明

## Structure（構造）

```yaml
layout: slope-chart-before-after
title_area: true
content_area:
  direction: column
  padding: "16px 48px"
  gap: 8px
  children:
    - id: slope_body
      type: svg_slope
      elements:
        - type: time_axis
          count: 2
          headers: ["2024年実績", "2026年計画"]
          stroke: "#999999"
          header_color: "#555555"
        - type: slope_lines
          count: 5   # 5項目程度
          emphasized:      # 増加項目
            stroke: "#333333"
            stroke_width: 3
          normal:          # 減少・横ばい項目
            stroke: "#AAAAAA"
            stroke_width: 1.5
        - type: end_points
          marker: circle
        - type: end_labels
          format: "項目名 値ラベル"   # 例「クラウド事業 38億円」
          left_anchor: end
          right_anchor: start
          font_size: 11px
    - id: legend_row
      direction: row
      elements:
        - type: legend_item
          swatch: "line_bold_dark"
          label: "拡大事業（増加）"
        - type: legend_item
          swatch: "line_thin_light"
          label: "縮小事業（減少）"
        - type: reading_note
          text: "傾きの読み方を1行で補足"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 時点ヘッダー（左右） | 比較する2時点を明示 | 各4〜8文字（「2024年実績」等） |
| 縦軸（左右2本） | 各時点の値の並びを支える基準線 | テキストなし |
| スロープ線 | 項目ごとの増減を傾きで表現 | 5項目程度（最大7） |
| 増加項目の強調線 | 主張したい変化を濃グレー太線で強調 | 1〜3本 |
| 端点ラベル | 項目名＋実数値（両端に必須） | 「クラウド事業 38億円」等 |
| 凡例行 | 線種の意味（拡大／縮小） | 2項目＋注記1行 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-slope-chart-before-after.md を参照して、
以下の事業別売上の構造転換を示すスライドを作成してください。

【2時点】
- 左: 2024年実績 / 右: 2026年計画

【項目（2024年 → 2026年、単位: 億円）】
- 受託開発: 45 → 40（縮小）
- クラウド事業: 12 → 38（拡大・強調）
- SaaS事業: 8 → 21（拡大・強調）
- 保守運用: 22 → 17（縮小）
- ライセンス販売: 18 → 15（縮小）

【スライドタイトル】
売上の柱をどう入れ替えるか — 事業別売上の2年構造転換
```

### 注意点
- 項目は5本程度が適切（8本以上は線が交差しすぎて判読困難。多い場合は上位項目に絞る）
- 強調（濃グレー太線）は「主張したい変化」1〜3本に限定する。全部太いと何も目立たない
- 端点ラベルの縦位置が近い項目（値の差が小さい項目）はラベルが重ならないよう上下にずらすか、値を確認して間隔を確保する（最低12px）
- 値ラベルは両端に必ず付ける（傾きの印象だけで語らせず、実数で裏付ける）
- 2時点は「実績vs計画」に限らず「施策前vs施策後」「前年vs今年」「自社vs業界平均」等に応用可能
- 縦軸のスケールは共通（左右で同一）にする。スケールが違うと傾きが嘘をつく
