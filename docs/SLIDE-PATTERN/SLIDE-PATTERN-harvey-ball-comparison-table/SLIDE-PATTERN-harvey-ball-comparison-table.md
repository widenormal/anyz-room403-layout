# SLIDE-PATTERN-harvey-ball-comparison-table

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** harvey-ball-comparison-table
**概要：** 行=評価基準（5行程度）×列=選択肢（3〜4列）の比較表。各セルの充足度をハーベイボール（円の塗り割合: 0/25/50/75/100%）で示す。推奨列はヘッダを濃色で強調し、列全体に薄グレー背景を敷く。表の下に充足度の凡例を置く。
**適したシーン：** ベンダー・製品選定、施策オプション比較、プラン比較、採用ツールの評価まとめ

## Structure（構造）

```yaml
layout: harvey-ball-comparison-table
title_area: true
content_area:
  direction: column
  padding: "16px 48px"
  gap: 10px
  children:
    - id: comparison_table
      type: table
      columns:
        - { header: "評価基準", width: "22%", background: "#F0F0F0" }
        - { header: "ベンダーA", recommended: true,
            header_background: "#333333", header_color: "#FFFFFF",
            cell_background: "#F5F5F5", tag: "推奨" }
        - { header: "ベンダーB" }
        - { header: "ベンダーC" }
      rows:
        # score は 0 / 25 / 50 / 75 / 100 の5段階
        - { criteria: "機能適合度",   sub: "要件カバー率",     scores: [100, 75, 50] }
        - { criteria: "導入コスト",   sub: "初期＋5年運用",   scores: [75, 100, 25] }
        - { criteria: "導入スピード", sub: "契約〜稼働まで",   scores: [75, 50, 100] }
        - { criteria: "サポート体制", sub: "国内・日本語対応", scores: [100, 25, 50] }
        - { criteria: "拡張性",       sub: "API・外部連携",    scores: [50, 75, 25] }
      cell_type: harvey_ball
      harvey_ball:
        render: inline_svg   # 円弧パスで塗り割合を描画
        size: 22px
        fill: "#555555"
        stroke: "#666666"
    - id: legend_row
      type: legend
      align: right
      items:
        - { ball: 0,   label: "0%" }
        - { ball: 25,  label: "25%" }
        - { ball: 50,  label: "50%" }
        - { ball: 75,  label: "75%" }
        - { ball: 100, label: "100%" }
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| 評価基準列（行見出し） | 比較の観点を示す | 5行前後、各4〜8文字＋補足10文字以内 |
| 選択肢列ヘッダ | 比較対象の名称 | 3〜4列、各4〜10文字 |
| 推奨列の強調 | 結論（どれを推すか）を視覚的に即断させる | 「推奨」タグ2〜4文字 |
| ハーベイボール | 各セルの充足度を5段階の円塗りで示す | テキストなし（0/25/50/75/100%） |
| 凡例 | 円の塗り割合と充足度の対応を示す | 5個、各ラベル4文字以内 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-harvey-ball-comparison-table.md を参照して、
以下の評価結果をハーベイボール比較表にしたスライドを作成してください。

【選択肢】ベンダーA（推奨）／ベンダーB／ベンダーC

【評価（0/25/50/75/100%）】
- 機能適合度: A=100, B=75, C=50
- 導入コスト: A=75, B=100, C=25
- 導入スピード: A=75, B=50, C=100
- サポート体制: A=100, B=25, C=50
- 拡張性: A=50, B=75, C=25

【スライドタイトル】
勤怠システム選定 — 総合力でベンダーAを推奨
```

### 注意点
- 評価基準は4〜6行、選択肢は3〜4列が適切（それ以上は判読性が落ちるため表を分割する）
- 充足度は必ず0/25/50/75/100%の5段階に丸める（中間値を作ると円弧の描き分けが判読できない）
- 「コスト」のような小さいほど良い指標は「充足度が高い=良い」に向きを揃えてから点数化する（例: 低コスト=100%）
- 推奨列は必ず1列だけ強調する。推奨が決まっていない段階では強調なしで出し、決定後に更新する
- 各スコアの根拠（元データ・評価方法）を発表者ノートか補足資料に残す。見栄えでスコアを盛らない
- 元資料からの変換時は評価基準の行を欠落・改名・統合しない（項目一致原則）
