# SLIDE-PATTERN-positioning-matrix-2x2

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** positioning-matrix-2x2
**概要：** 2軸の平面上に項目を円マーカーでプロットする汎用2×2ポジショニングマトリクス。risk-matrix-2x2 がセル内バッジで「分類」を示すのに対し、本パターンは平面上の「位置（度合い）」で相対評価を示す。4象限には薄い背景色と象限ラベルを付ける。
**適したシーン：** インパクト×実行容易性の施策優先度整理、SWOT・Ansoffなどの2軸フレームワーク、競合ポジショニング、ステークホルダーマップ（影響力×関心度）

## Structure（構造）

```yaml
layout: positioning-matrix-2x2
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
          text: "インパクト"
          writing_mode: vertical-rl
          font_size: 12px
          color: "#666666"
        - type: plot_plane
          border: "1px solid #CCCCCC"
          quadrants:
            - position: top_left
              label: "大玉"
              background: "#F5F5F5"
            - position: top_right
              label: "Quick Win"
              background: "#EEEEEE"
            - position: bottom_left
              label: "慎重に"
              background: "#FFFFFF"
            - position: bottom_right
              label: "後回し"
              background: "#FAFAFA"
          plot_items:
            # x: 実行容易性（0=左端・低 〜 100=右端・高）
            # y: インパクト（0=上端・高 〜 100=下端・低）
            - { label: "FAQ自動応答の導入",  x: 78, y: 22 }
            - { label: "見積書テンプレ統一", x: 64, y: 38 }
            - { label: "基幹システム刷新",   x: 24, y: 16 }
            - { label: "新規販路の開拓",     x: 34, y: 40 }
            - { label: "社内報の月次化",     x: 70, y: 72 }
            - { label: "オフィス移転",       x: 26, y: 80 }
          marker:
            shape: circle
            size: 14px
            fill: "#555555"
        - type: x_axis_label
          text: "実行容易性"
          font_size: 12px
          color: "#666666"
          align: center
    - id: legend_area
      width: "25%"
      elements:
        - type: legend_item
          label: "Quick Win"
          sub: "高インパクト・容易 → 即着手"
          background: "#EEEEEE"
        - type: legend_item
          label: "大玉"
          sub: "高インパクト・困難 → 計画投資"
          background: "#F5F5F5"
        - type: legend_item
          label: "後回し"
          sub: "低インパクト・容易 → 隙間対応"
          background: "#FAFAFA"
        - type: legend_item
          label: "慎重に"
          sub: "低インパクト・困難 → 原則見送り"
          background: "#FFFFFF"
        - type: reading_note
          text: "図の読み方: 円の位置が2軸上の評価。右上に近いほど優先度が高い。"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 縦軸ラベル（インパクト） | Y軸の意味を示す | 3〜6文字 |
| 横軸ラベル（実行容易性） | X軸の意味を示す | 3〜6文字 |
| 象限ラベル（Quick Win等） | 各象限の解釈名を四隅に薄く表示 | 4〜10文字 |
| プロット項目（円＋ラベル） | 評価対象を平面上の位置で示す | 4〜8個、各10文字以内 |
| 凡例エリア | 象限の意味と取るべきアクションを補足 | 4項目＋読み方1文 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-positioning-matrix-2x2.md を参照して、
以下の施策を「実行容易性（横軸）×インパクト（縦軸）」の平面に
プロットしたスライドを作成してください。

【施策と評価（容易性 / インパクト、各1〜10）】
- FAQ自動応答の導入: 8 / 8
- 見積書テンプレ統一: 7 / 6
- 基幹システム刷新: 2 / 9
- 新規販路の開拓: 3 / 6
- 社内報の月次化: 7 / 3
- オフィス移転: 2 / 2

【スライドタイトル】
来期施策の優先順位マップ — まずQuick Winの2件から着手
```

### 注意点
- プロット項目は4〜8個が適切（多すぎるとラベルが重なり判読不能になる）
- ラベル同士が重なる場合は座標を微調整するか、マーカーの左右どちらにラベルを出すかを切り替える
- 2軸と象限ラベルは内容に合わせて差し替え可能（例：SWOT＝内部×外部、Ansoff＝市場×製品、ステークホルダー＝影響力×関心度）
- 位置（座標）は必ず入力データの評価値から算出する。根拠なく見栄えで配置しない
- 「セルへの分類」で足りる場合は risk-matrix-2x2 を使う。位置の差・相対比較を見せたい時だけ本パターンを使う
