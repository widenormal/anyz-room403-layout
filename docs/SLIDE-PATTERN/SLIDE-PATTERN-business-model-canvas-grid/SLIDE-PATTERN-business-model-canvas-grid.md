# SLIDE-PATTERN-business-model-canvas-grid

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** business-model-canvas-grid
**概要：** ビジネスモデルキャンバス（Osterwalder型）の標準9ブロック固定レイアウト。上段5列（KP／KA+KR／VP／CR+CH／CS）＋下段2分割（コスト構造／収益の流れ）をCSS gridで構成し、各ブロックにブロック名（日英併記）と箇条書き2〜3項目を記載する。
**適したシーン：** 事業モデルの1枚構造化、新規事業の検討・壁打ち、既存事業の見直し、投資判断・事業説明の共通言語化

## Structure（構造）

```yaml
layout: business-model-canvas-grid
title_area: true
content_area:
  padding: "12px 40px"
  grid:
    template_areas:
      - "kp kp ka ka vp vp cr cr cs cs"
      - "kp kp kr kr vp vp ch ch cs cs"
      - "cost cost cost cost cost rev rev rev rev rev"
    template_rows: "1fr 1fr 0.62fr"
  blocks:
    - id: kp
      name: "パートナー"
      name_en: "Key Partners"
      items: ["地場運送会社ネットワーク", "会計事務所（紹介元）"]
    - id: ka
      name: "主要活動"
      name_en: "Key Activities"
      items: ["SaaS開発・保守", "導入伴走支援"]
    - id: kr
      name: "リソース"
      name_en: "Key Resources"
      items: ["現場出身エンジニア", "在庫データ基盤"]
    - id: vp
      name: "価値提案"
      name_en: "Value Propositions"
      background: "#EEEEEE"
      items: ["少人数でも回る在庫管理", "導入3週間で稼働", "月額5万円から"]
    - id: cr
      name: "顧客との関係"
      name_en: "Customer Relationships"
      items: ["専任サポート担当", "四半期ごとの活用レビュー"]
    - id: ch
      name: "チャネル"
      name_en: "Channels"
      items: ["士業からの紹介", "業界展示会"]
    - id: cs
      name: "顧客セグメント"
      name_en: "Customer Segments"
      items: ["従業員30〜100名の製造業", "多品種少量生産の工場"]
    - id: cost
      name: "コスト構造"
      name_en: "Cost Structure"
      items: ["開発人件費（約6割）", "クラウド利用料", "展示会出展費"]
    - id: rev
      name: "収益の流れ"
      name_en: "Revenue Streams"
      items: ["月額サブスクリプション", "初期導入支援費", "オプション追加モジュール"]
```

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| ブロック名（日英併記） | 9ブロック各領域の見出し | 日本語3〜8文字＋英語正式名 |
| 箇条書き項目 | 各ブロックの具体内容 | 各ブロック2〜3項目、15文字以内 |
| 価値提案ブロック（中央） | キャンバスの核。薄グレー背景で強調 | 3項目まで |
| 下段2分割（コスト／収益） | お金の出入りの構造 | 各2〜3項目 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-business-model-canvas-grid.md を参照して、
以下の事業をビジネスモデルキャンバスに整理したスライドを作成してください。

【事業概要】
中小製造業向け在庫管理SaaS

【価値提案】少人数でも回る在庫管理／導入3週間で稼働／月額5万円から
【顧客セグメント】従業員30〜100名の製造業／多品種少量生産の工場
【チャネル】士業からの紹介／業界展示会
【顧客との関係】専任サポート担当／四半期ごとの活用レビュー
【主要活動】SaaS開発・保守／導入伴走支援
【リソース】現場出身エンジニア／在庫データ基盤
【パートナー】地場運送会社ネットワーク／会計事務所（紹介元）
【コスト構造】開発人件費（約6割）／クラウド利用料／展示会出展費
【収益の流れ】月額サブスクリプション／初期導入支援費／オプション追加モジュール

【スライドタイトル】
事業モデルの全体像：誰に何をどう届けて稼ぐか
```

### 注意点
- 9ブロックの配置は標準レイアウト固定（KP｜KA/KR｜VP｜CR/CH｜CS＋下段コスト/収益）。順番を入れ替えない
- 各ブロックの項目は2〜3個まで（それ以上は文字サイズが11px未満になり判読不能）
- 中央の価値提案（VP）だけ薄グレー背景で強調する（キャンバスの核であるため）
- 空欄のブロックを作らない（未定なら「検討中：〜」と仮説を書く）
- 詳細な数値検証は別スライドへ（キャンバスは構造の一覧性が目的）
