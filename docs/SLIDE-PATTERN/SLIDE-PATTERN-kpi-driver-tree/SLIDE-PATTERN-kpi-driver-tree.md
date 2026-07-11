# SLIDE-PATTERN-kpi-driver-tree

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** kpi-driver-tree
**概要：** 左端の最上位KPI（例: 営業利益）を、演算子（× − ＋ ÷）付きの横型ツリーで2〜3階層に分解するスライド。各ノードに指標名＋数値を表示し、打ち手で動かせる末端の「効くレバー」を濃グレーで強調する。
**適したシーン：** KPI分解、打ち手レバーの特定、予算・目標の構造説明、業績ドライバー分析、経営会議での増減要因整理

## Structure（構造）

```yaml
layout: kpi-driver-tree
title_area: true
content_area:
  direction: column
  padding: "16px 48px 12px"
  children:
    - id: col_headers
      type: header_row
      labels: ["最上位KPI", "第1階層", "第2階層（ドライバー）"]
      font_size: 10px
      color: "#999999"
    - id: tree_body
      direction: row
      connector: "L字罫線（#AAAAAA・1px）＋演算子バッジ（円形・#999999枠）"
      children:
        - type: root_kpi_node
          width: 180px
          background: "#EEEEEE"
          border: "#999999"
          metric: "営業利益（今期実績）"
          value: "1.2億円"
        - type: level1_nodes
          operator_between: "−"
          nodes:
            - metric: "売上高"
              value: "8.0億円"
              operator_children: "×"
              children:
                - { metric: "年間購入客数", value: "24.0万人" }
                - { metric: "客単価", value: "3,330円", lever: true }
            - metric: "総コスト"
              value: "6.8億円"
              operator_children: "＋"
              children:
                - { metric: "固定費", value: "4.2億円" }
                - { metric: "変動費", value: "2.6億円", lever: true }
        - type: lever_node_style
          background: "#555555"
          color: "#FFFFFF"
          tag: "効くレバー"
    - id: footer_row
      type: legend_note
      font_size: 10px
      color: "#999999"
      text: "濃色＝打ち手で動かせる「効くレバー」。分解式を1行で併記"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 最上位KPIノード（左端・大） | 分解の起点となる指標と実績値 | 指標名10文字以内＋数値 |
| 中間ノード（第1階層） | KPIを構成する中間指標 | 2〜3個、指標名6文字以内＋数値 |
| 末端ノード（第2階層） | 打ち手が直接効くドライバー指標 | 4〜6個、指標名8文字以内＋数値 |
| 演算子バッジ（× − ＋ ÷） | 兄弟ノード間の計算関係を示す | 記号1文字（縦連結線の中点に配置） |
| 効くレバーノード（濃グレー） | 打ち手で動かせる指標の強調 | 1〜2個に絞る |
| 凡例・脚注 | 濃色の意味と分解式を補足 | 1〜2文 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-kpi-driver-tree.md を参照して、
以下のKPI分解をドライバーツリーで示すスライドを作成してください。

【最上位KPI】
月間経常収益（MRR） 4,800万円

【第1階層】（＋で分解）
- 新規MRR 900万円
- 既存MRR 3,900万円

【第2階層】
- 新規MRR ＝ 新規契約数 60件 × 平均単価 15万円（新規契約数が効くレバー）
- 既存MRR ＝ 既存顧客数 300社 × 継続単価 13万円（継続単価が効くレバー）

【スライドタイトル】
MRRを動かす2つのレバー
```

### 注意点
- ノードの数値は必ず計算が合うようにする（親 ＝ 子1 演算子 子2 を検算してから記載）
- 数値はデータ由来のみ。推測値を入れない（不明なら「—」とし脚注で明示）
- 「効くレバー」の濃グレー強調は1〜2個に絞る（全部強調すると何も伝わらない）
- 演算子バッジは兄弟ノードをつなぐ縦連結線の中点に置く（親子線上には置かない）
- 3階層を超える分解は2枚に分けるか、注目する枝だけを展開する
- 指標名には日常語を併記してよい（例:「MRR（月間経常収益）」）
