# SLIDE-PATTERN-nine-box-matrix-3x3

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** nine-box-matrix-3x3
**概要：** 市場魅力度（縦軸・高中低）×競争力（横軸・強中弱）の3×3マトリクス（GE-McKinsey 9box）。対角で「投資・成長／選別／撤退・収穫」の3ゾーンに濃淡を分け、セル内に事業をバブル（大きさ=売上規模）で配置する。
**適したシーン：** 事業ポートフォリオの投資優先度整理、製品ライン評価、人材9box（パフォーマンス×ポテンシャル）、拠点・チャネルの選別

## Structure（構造）

```yaml
layout: nine-box-matrix-3x3
title_area: true
content_area:
  direction: row
  padding: "16px 48px"
  gap: 24px
  children:
    - id: matrix_body
      width: "75%"
      elements:
        - type: y_axis_label
          text: "市場魅力度"
          writing_mode: vertical-rl
          row_labels: ["高", "中", "低"]
        - type: x_axis_label
          text: "競争力"
          col_labels: ["強", "中", "弱"]
        - type: grid_3x3
          # ゾーンは対角で3分割（左上=投資 / 対角=選別 / 右下=撤退・収穫）
          zones:
            - name: "投資・成長"
              cells: [[高,強], [高,中], [中,強]]
              background: "#EEEEEE"
            - name: "選別"
              cells: [[高,弱], [中,中], [低,強]]
              background: "#F5F5F5"
            - name: "撤退・収穫"
              cells: [[中,弱], [低,中], [低,弱]]
              background: "#FAFAFA"
          bubbles:
            # size は売上規模に比例（l/m/s の3段階）
            - { name: "クラウド",  value: "120億円", cell: [高,強], size: l }
            - { name: "新規SaaS",  value: "15億円",  cell: [高,中], size: s }
            - { name: "受託開発",  value: "80億円",  cell: [中,中], size: m }
            - { name: "保守",      value: "60億円",  cell: [低,強], size: m }
            - { name: "印刷",      value: "40億円",  cell: [低,弱], size: s }
          bubble_style:
            fill: "#666666"
            text_color: "#FFFFFF"
    - id: legend_area
      width: "25%"
      elements:
        - type: legend_item
          label: "投資・成長"
          sub: "左上3セル → 積極投資"
          background: "#EEEEEE"
        - type: legend_item
          label: "選別"
          sub: "対角3セル → 案件ごとに判断"
          background: "#F5F5F5"
        - type: legend_item
          label: "撤退・収穫"
          sub: "右下3セル → 投資抑制"
          background: "#FAFAFA"
        - type: size_legend
          text: "円の大きさ＝売上規模"
        - type: reading_note
          text: "図の読み方: 左上に近い事業ほど投資優先度が高い。"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 縦軸ラベル（市場魅力度） | Y軸の評価観点を示す | 3〜6文字＋段階ラベル「高中低」 |
| 横軸ラベル（競争力） | X軸の評価観点を示す | 3〜6文字＋段階ラベル「強中弱」 |
| 9セルグリッド | 評価の組み合わせ位置を示す | セル自体にテキストなし |
| ゾーン濃淡（3段階） | 投資方針の対角3ゾーンを背景色で区別 | ゾーン名4〜8文字 |
| 事業バブル | 評価対象＋規模（大きさで表現） | 3〜7個、名称2〜6文字＋数値 |
| 凡例エリア | ゾーンの意味・バブルサイズの意味を補足 | 3項目＋サイズ凡例＋読み方1文 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-nine-box-matrix-3x3.md を参照して、
以下の事業を市場魅力度×競争力の9boxに配置したスライドを作成してください。

【事業と評価（魅力度 / 競争力 / 売上）】
- クラウド事業: 高 / 強 / 120億円
- 新規SaaS事業: 高 / 中 / 15億円
- 受託開発事業: 中 / 中 / 80億円
- 保守サービス事業: 低 / 強 / 60億円
- 印刷事業: 低 / 弱 / 40億円

【スライドタイトル】
事業ポートフォリオ評価 — クラウドとSaaSに投資を集中
```

### 注意点
- バブルは3〜7個が適切。同一セルに2個までとし、重なる場合はセル内で左右にずらす
- バブルの大きさは必ず売上等の実数値に比例させる（3段階目安：最大値の70%以上=大、30〜70%=中、30%未満=小）
- 空セルはそのまま残してよい（「その位置に事業がない」こと自体が情報になる）
- 軸は用途に応じて差し替え可能（人材9box＝パフォーマンス×ポテンシャル等）。段階ラベル（高中低・強中弱）も合わせて変更する
- ゾーンの切り方（対角3分割）は標準形。自社の投資方針に合わせて変える場合は凡例も必ず更新する
- 2軸×2段階で足りる場合は positioning-matrix-2x2 / risk-matrix-2x2 を使い、9段階の細かさが必要な時だけ本パターンを使う
