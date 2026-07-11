# SLIDE-PATTERN-radar-chart-comparison

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** radar-chart-comparison
**概要：** 5〜6軸の放射グリッド（同心多角形）上に「現状」（薄グレー塗り多角形）と「目標」（濃グレー線の多角形）を重ね描きするレーダーチャート。軸ごとの強み・弱みとギャップを1枚で示す。
**適したシーン：** ケイパビリティ診断（現状vs目標）、組織・人材のスキル評価、製品・サービスの多軸比較、自社vs競合のベンチマーク

## Structure（構造）

```yaml
layout: radar-chart-comparison
title_area: true
content_area:
  direction: row
  padding: "16px 48px"
  gap: 24px
  children:
    - id: radar_body
      width: "68%"
      type: svg_radar
      elements:
        - type: grid_polygons
          axes: 6            # 5〜6軸
          levels: 5          # 同心多角形5段階
          stroke: "#D8D8D8"
        - type: axis_lines
          from: center
          stroke: "#D8D8D8"
        - type: scale_numbers
          values: [1, 2, 3, 4, 5]
          font_size: 9px
          color: "#AAAAAA"
        - type: axis_labels
          position: "各軸の外側端"
          font_size: 12px
          color: "#555555"
          texts: ["技術力", "営業力", "ブランド力", "価格競争力", "サポート体制", "開発スピード"]
        - type: polygon_current   # 現状
          fill: "#CCCCCC"
          fill_opacity_expression: "薄グレー塗り（透過は使わずグレー濃淡で表現）"
          stroke: "#AAAAAA"
          values: [3, 2, 4, 2, 3, 2]
        - type: polygon_target    # 目標
          fill: none
          stroke: "#333333"
          stroke_width: 2.5
          vertex_marker: circle
          values: [4, 4, 5, 4, 4, 4]
    - id: legend_area
      width: "32%"
      elements:
        - type: legend_item
          swatch: "filled_light"
          label: "現状（2026年上期 自己評価）"
        - type: legend_item
          swatch: "line_dark"
          label: "目標（2027年度末）"
        - type: scale_note
          text: "5段階評価・外側ほど高評価"
        - type: reading_note
          text: "最大ギャップ軸への言及など1〜2行"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 放射グリッド（同心多角形） | 5段階のスケールを示す下地 | テキストなし（5段） |
| 軸ラベル | 評価軸の名称（各軸の外側端） | 5〜6軸、各3〜8文字 |
| スケール数値 | 1〜5の段階を示す目盛 | 「1」〜「5」 |
| 現状ポリゴン | 現在の評価値（薄グレー塗り） | 数値は凡例・注記で補足 |
| 目標ポリゴン | 目指す評価値（濃グレー線＋頂点マーカー） | 同上 |
| 凡例エリア | 2系列の意味・評価時点・スケール定義 | 2項目＋注記2〜3行 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-radar-chart-comparison.md を参照して、
以下のケイパビリティ診断のスライドを作成してください。

【評価軸と値（現状 → 目標、5段階）】
- 技術力: 3 → 4
- 営業力: 2 → 4
- ブランド力: 4 → 5
- 価格競争力: 2 → 4
- サポート体制: 3 → 4
- 開発スピード: 2 → 4

【凡例】
- 現状 = 2026年上期の自己評価
- 目標 = 2027年度末の到達水準

【スライドタイトル】
どの能力を伸ばすべきか — ケイパビリティ診断（現状と目標）
```

### 注意点
- 軸数は5〜6軸が適切（4軸以下は2×2マトリクス、7軸以上は判読困難）
- 描画は SVG の polygon が必須（頂点座標 = 中心 + 半径×値/5 の三角関数で算出する）
- 現状は「薄グレー塗り」、目標は「濃グレー線のみ（塗りなし）」で重ねても両方読めるようにする。透過（rgba）は使わず、塗りは薄グレーの単色 hex で表現する
- 軸ラベルはチャートの外側に配置し、グリッドと重ねない
- 各軸のギャップ（目標−現状）が主張になる。凡例横に「最大ギャップは営業力」等の注記を1行添えると伝わりやすい
- 系列は2本まで（現状・目標）。3本以上重ねると判読不能になるため、比較対象が多い場合はスライドを分ける
