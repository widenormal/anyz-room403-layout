# SLIDE-PATTERN-venn-three-circle-overlap

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** venn-three-circle-overlap
**概要：** 3つの円（3C：顧客・競合・自社など）が中央で重なるベン図で、概念の重なりとスイートスポットを可視化するスライド。中央の交差部に「勝ち筋」等のキーメッセージを置き、右側で各領域の意味を補足する。
**適したシーン：** 3C分析、ポジショニングの言語化、勝ち筋・スイートスポットの特定、2〜3概念の重なり整理、提供価値の定義

## Structure（構造）

```yaml
layout: venn-three-circle-overlap
title_area: true
content_area:
  direction: row
  padding: "16px 48px"
  gap: 24px
  children:
    - id: venn_body
      width: "62%"
      elements:
        - type: svg_venn
          circles:
            - position: top
              label: "顧客"
              sublabel: "Customer"
              stroke: "#999999"
              caption: "省人化ニーズの高まり"
            - position: bottom_left
              label: "競合"
              sublabel: "Competitor"
              stroke: "#AAAAAA"
              caption: "大手は大企業向けに集中"
            - position: bottom_right
              label: "自社"
              sublabel: "Company"
              stroke: "#666666"
              caption: "現場密着のサポート体制"
          center_badge:
            text: "勝ち筋"
            message: "中小製造業特化の伴走支援"
            background: "#555555"
            color: "#FFFFFF"
    - id: legend_area
      width: "38%"
      elements:
        - type: legend_card
          label: "顧客が求めること"
          description: "少人数でも回る在庫・生産管理"
        - type: legend_card
          label: "競合ができていないこと"
          description: "導入後の定着支援が手薄"
        - type: legend_card
          label: "自社ができること"
          description: "元現場出身者による導入伴走"
        - type: key_message_card
          label: "中央の重なり＝勝ち筋"
          description: "3つが重なる領域だけが持続的な差別化になる"
          background: "#EEEEEE"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 円ラベル（顧客・競合・自社） | 各円が表す概念名 | 2〜4文字＋英語併記 |
| 円キャプション | 各円の要点（円の外側近傍に配置） | 各10〜15文字 |
| 中央バッジ（勝ち筋） | 3円の交差部＝キーメッセージ | 見出し2〜4文字＋補足15文字以内 |
| 凡例カード（右側） | 各領域の意味の説明 | 各カード：見出し＋1文（20文字以内） |
| キーメッセージカード | 重なりの解釈・結論の強調 | 1文（25文字以内） |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-venn-three-circle-overlap.md を参照して、
以下の3C分析をベン図に整理したスライドを作成してください。

【顧客（Customer）】
- 少人数でも回る在庫・生産管理を求めている

【競合（Competitor）】
- 大手ベンダーは大企業向けに集中、導入後の定着支援が手薄

【自社（Company）】
- 元現場出身者による導入伴走・現場密着サポート

【中央の勝ち筋】
中小製造業特化の伴走支援

【スライドタイトル】
3C分析：私たちの勝ち筋はどこにあるか
```

### 注意点
- 円は3つが基本（2概念の場合は2円に減らしてもよい）
- 円の中は塗りつぶさず輪郭線＋ラベルで描き、中央の交差部だけ濃いグレーのバッジで強調する（重なりの視認性を優先）
- 円ラベルは3C以外にも変更可能（例：「技術」「市場」「組織」、「Will」「Can」「Must」）
- 中央のキーメッセージは必ず1つに絞る（複数置くと「重なり＝結論」の構図が崩れる）
- 各円のキャプション・凡例は短文で（長文はベン図の外の凡例カード側に寄せる）
