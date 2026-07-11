# SLIDE-PATTERN-funnel-conversion-stages

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** funnel-conversion-stages
**概要：** 上から下へ幅が狭まる台形4〜5段のファネル図。各段にステージ名＋実数を表示し、段の右横に段間の転換率（→ 32% 等）を注記する。下段ほど濃いグレーで「最終成果への絞り込み」を視覚化する。
**適したシーン：** 営業パイプライン分析、採用選考の歩留まり、マーケティングのコンバージョン分析、申込〜契約プロセスの離脱箇所特定

## Structure（構造）

```yaml
layout: funnel-conversion-stages
title_area: true
content_area:
  direction: row
  padding: "16px 48px"
  gap: 24px
  justify: center
  children:
    - id: funnel_column
      width: 540px
      type: trapezoid_stack     # clip-path: polygon() で台形を描く
      stages:                   # 4〜5段・下ほど濃色
        - label: "リード獲得"
          value: "4,800件"
          background: "#E8E8E8"
          text_color: "#333333"
        - label: "商談化"
          value: "1,540件"
          background: "#CCCCCC"
          text_color: "#333333"
        - label: "提案"
          value: "620件"
          background: "#AAAAAA"
          text_color: "#FFFFFF"
        - label: "見積提示"
          value: "280件"
          background: "#666666"
          text_color: "#FFFFFF"
        - label: "受注"
          value: "98件"
          background: "#333333"
          text_color: "#FFFFFF"
      stage_height: 66px
      stage_gap: 10px
    - id: rate_column
      width: 220px
      type: conversion_rates    # 段間の境界に揃えて配置
      items:
        - transition: "リード → 商談"
          rate: "→ 32%"
        - transition: "商談 → 提案"
          rate: "→ 40%"
        - transition: "提案 → 見積"
          rate: "→ 45%"
        - transition: "見積 → 受注"
          rate: "→ 35%"
  footer_note:
    text: "図の読み方: 下段ほど濃色＝最終成果に近い。転換率が最も低い段が改善の優先箇所。"
    font_size: 10px
    color: "#999999"
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 台形ステージ | プロセスの各段階と規模 | 4〜5段、ステージ名2〜6文字 |
| ステージ内実数 | 各段の件数・人数（実数必須） | 「4,800件」等3〜7文字 |
| 濃淡グラデーション | 下段ほど濃く＝成果への近さ | テキストなし（5段階グレー） |
| 段間転換率注記 | 隣接段間の歩留まり（→ NN%） | 各「→ 32%」＋遷移名6〜10文字 |
| フッター注記 | 図の読み方・改善ポイントの示唆 | 1行（20〜50文字） |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-funnel-conversion-stages.md を参照して、
以下の営業パイプラインのファネル分析スライドを作成してください。

【ステージ（上から順に・実数）】
- リード獲得: 4,800件
- 商談化: 1,540件
- 提案: 620件
- 見積提示: 280件
- 受注: 98件

【段間転換率】
- リード → 商談: 32%
- 商談 → 提案: 40%
- 提案 → 見積: 45%
- 見積 → 受注: 35%

【スライドタイトル】
どこで案件が消えているか — 営業ファネルの歩留まり分析
```

### 注意点
- 段数は4〜5段が適切（6段以上は各段が薄くなり数値が読めない）
- 実数と転換率は必ず両方表示する（転換率だけでは規模感が、実数だけでは歩留まりが伝わらない）
- 転換率は「上段の実数 × 率 ≒ 下段の実数」が成立するか必ず検算する（数値はデータ由来のみ・つじつまの合わない率を書かない）
- 濃淡は上から薄→濃（#E8E8E8 → #CCCCCC → #AAAAAA → #666666 → #333333）。濃い段（3段目以降）は白文字にする
- 台形の幅は実数に厳密比例させなくてよい（比例させると最下段が細すぎて読めなくなる。段階的に狭める）
- 「転換率が最も低い段＝ボトルネック」を注記やタイトルで指摘すると、単なる現状報告でなく改善提案のスライドになる
