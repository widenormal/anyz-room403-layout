---
name: slide-pattern-creator
description: スライドの画像・ファイルからレイアウトパターンを抽出し、SLIDE-PATTERN-{name}.mdとスケルトンHTMLを生成する。「スライドパターンを抽出して」「スライドパターンを作って」「SLIDE-PATTERNを生成して」「slide-pattern-creator」と言われたときに使用する。※レイアウトパターン抽出の任意ツール。5co公式CIスライドの制作自体は Claude Code＋5co-CI-kit の決定論パス（docs/SLIDE-md/SLIDE-md-5co/SLIDE.md）で行う。
---

# slide-pattern-creator

スライドの画像・PowerPointファイル・テキスト説明からレイアウト構造を解析し、AIが再現できるようパターンを言語化した `SLIDE-PATTERN-{name}.md` と、グレースケールのスケルトンHTMLサンプルを生成する。

`slide-md-creator` が生成するSLIDE.md（デザイン定義）と組み合わせて使うことで、AIツールにデザイン＋パターンの両方を渡してスライドを生成できる。

## STEP 1：入力の受け取り

スキル起動時、ユーザーが以下のいずれかを提供しているか確認する：

- スライドの画像・スクリーンショット（主な入力）
- PowerPointファイル（.pptx）
- テキストによるレイアウト構造の説明

**何も提供されていない場合**、以下のように尋ねる：

> 「スライドの画像やファイルを渡してください。PowerPointファイル（.pptx）や、テキストでレイアウト構造を説明していただくことも可能です。なお、Google Slidesは直接受け付けできないため、スクリーンショットまたはPowerPoint形式でエクスポートしてください。」

複数の画像・スライドが渡された場合はすべてを受け取り、STEP 2の分析に使用する。

## STEP 2：パターンの検出と分類

受け取った入力を解析し、異なるレイアウト構造を検出する。

### 分析する観点

- **カラム構成**：1カラム・2カラム・3カラム・グリッド等
- **主要エリアの配置**：画像・テキスト・アイコン・チャートがどこにあるか
- **コンテンツの種類**：見出し・箇条書き・引用・データ・図解 等
- **強調の仕方**：フルスクリーン要素・中央配置・左右分割 等

### 分析対象外（SLIDE.mdで定義）

以下の要素はSLIDE.mdの `Slide Frame` セクションで一括管理されるため、パターン分析には含めない：

- タイトルエリア（スライドタイトルの位置・フォント・装飾）
- ページ番号（位置・スタイル）
- スライド全体の背景色・共通装飾（アクセントバー・装飾図形等）

**パターンとして定義するのは、タイトル行より下のコンテンツエリアの構造のみとする。**

### 検出結果の提示

**1パターンの場合：**

> 「1種類のレイアウトパターンを検出しました。
> 構造：[構造の簡単な説明]
> パターン名の候補：`[proposed-name]`
> このパターン名でよいですか？別の名前にしたい場合はお知らせください。」

→ ユーザーが承認すればSTEP 4へ、別名を希望すればSTEP 3へ

**複数パターンの場合：**

> 「X種類のレイアウトパターンを検出しました：
>
> 1. [構造の説明] → 候補名：`[name-1]`
> 2. [構造の説明] → 候補名：`[name-2]`
> 3. [構造の説明] → 候補名：`[name-3]`
>
> すべてのパターンのファイルを生成しますか？
> 生成するパターンを選びたい場合は番号で教えてください。」

→ ユーザーの回答に応じて対象パターンを確定し、STEP 3へ

## STEP 3：パターン名の確認

STEP 2で提示した命名候補をユーザーが承認していない場合、このSTEPで確定する。

### 命名ルール

- 英小文字・ハイフン区切りのみ使用する
- 構造が一目でわかる名前にする
- 命名例：
  - `title-center` — 中央にタイトルのみ
  - `image-left-text-right` — 左に画像・右にテキスト
  - `three-column-icons` — 3カラムにアイコンと説明
  - `full-image-overlay` — 全面画像にテキストオーバーレイ
  - `bullet-list` — 見出し＋箇条書き
  - `data-chart` — 見出し＋グラフ・表
  - `quote-statement` — 引用・インパクト文字
  - `summary-grid` — まとめのカードグリッド

### 確認の進め方

複数パターンが対象の場合、1パターンずつ確認する：

> 「パターン1の名前：`image-left-text-right` でよいですか？」

ユーザーが承認したら次のパターンの確認へ、または変更を希望する場合は指定の名前を受け取る。

全パターンの名前が確定したらSTEP 4へ進む。

## STEP 4：SLIDE-PATTERN-{name}.mdの生成

確定したパターン名でフォルダとファイルを生成する。

### 出力先

カレントディレクトリ内の `docs/SLIDE-PATTERN/` フォルダの中に `SLIDE-PATTERN-{name}/` フォルダを作成して保存する：

    docs/SLIDE-PATTERN/SLIDE-PATTERN-{name}/SLIDE-PATTERN-{name}.md

### SLIDE-PATTERN-{name}.mdの出力形式

以下の4セクション構成で出力する。各 `[　]` に解析・確認で得た実際の値を入れる。

---
出力ファイル：docs/SLIDE-PATTERN/SLIDE-PATTERN-{name}/SLIDE-PATTERN-{name}.md

# SLIDE-PATTERN-{name}

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview

**パターン名：** {name}
**概要：** [パターンの一言説明（例：左半分に画像、右半分に見出しと本文を配置する2カラムレイアウト）]
**適したシーン：** [どんな内容のスライドに向いているか（例：製品・事例紹介、ビフォーアフター、具体例の提示）]

## Structure（構造）

[コンテンツエリアの構造を1〜3文で説明する。タイトル行より下のエリアがどう分割されているかを記述する。タイトル・ページ番号・装飾は含めない。]

    structure:
      layout: [two-column / single / grid / full / 等]
      columns: [カラム数（該当する場合）]
      left:
        width: [割合 例: 50%]
        type: [image / text / icon / chart / 等]
        role: [このエリアの役割]
      right:
        width: [割合 例: 50%]
        type: [image / text / icon / chart / 等]
        elements: [含まれる要素のリスト 例: [heading, body, caption]]

（レイアウト構造に応じてYAMLのキーは適宜変更する）

## Elements（各要素の役割）

※ タイトル（H1）はSLIDE.mdの Slide Frame で定義されるため、この表には含めない。コンテンツエリアの要素のみを記述する。

| 要素 | 配置 | 役割 |
|---|---|---|
| [要素名（例：画像）] | [配置場所（例：左カラム全体）] | [この要素が担う意味・機能（例：メッセージを補強するビジュアル）] |
| [要素名（例：見出し H2）] | [配置場所（例：右カラム上部）] | [役割（例：スライドの主張・サブタイトル）] |
| [要素名（例：本文）] | [配置場所（例：右カラム中央）] | [役割（例：見出しを支える説明文（2〜4行））] |

## Usage Guide（AIへの使い方）

このパターンをAIに指示する際のプロンプト例：

> 「SLIDE-PATTERN-{name}のレイアウトで、[各エリアに入れる内容を指定]してください。デザインはSLIDE.mdに従ってください。」

**注意点：**
- [このパターン特有の注意点や代替案（例：画像がない場合は左カラムをカラーブロックで代替できる）]
---

## STEP 5：SLIDE-PATTERN-{name}.htmlの生成

STEP 4と同じフォルダ内にスケルトンHTMLを生成する。

### 出力先

    docs/SLIDE-PATTERN/SLIDE-PATTERN-{name}/SLIDE-PATTERN-{name}.html

### HTMLの実装方針

- **色**：グレースケールのみ（背景：#FFFFFF、ボーダー：#CCCCCC、エリア背景：#F0F0F0、テキスト：#333333）
- **フォント**：システムデフォルト（font-family: sans-serif）
- **サイズ**：960px × 540px固定（16:9）
- **各エリアにラベル表示**：`font-size: 11px; color: #999; text-transform: uppercase;` で何のエリアか明示
- **コンテンツ**：ダミーテキスト（「見出しが入ります」「本文テキストが入ります。2〜4行程度の説明文が配置されます。」「キャプション」等）
- **JavaScriptは使用しない**
- **外部リソース不要**（フォントCDN等は使わない）
- **タイトルエリアのプレースホルダーを必ず上部に配置する**：薄いグレーで "Title Area — SLIDE.md 参照" とラベル表示し、このエリアがSLIDE.mdで定義されることを明示する。タイトルより下がコンテンツエリア（このパターンが定義する領域）となる。
- **スライド全体は `display:flex; flex-direction:column;` で構成する**：タイトルエリアを `flex-shrink:0` で固定し、コンテンツエリアを `flex:1` で残りを埋める。

### CSSの基本構造

    body {
      background: #E8E8E8;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
      font-family: sans-serif;
    }

    .slide {
      width: 960px;
      height: 540px;
      background: #FFFFFF;
      border: 1px solid #CCCCCC;
      position: relative;
      overflow: hidden;
      margin-bottom: 8px;
    }

    .area-label {
      font-size: 11px;
      color: #999999;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }

    .placeholder-box {
      background: #F0F0F0;
      border: 1px dashed #CCCCCC;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #AAAAAA;
      font-size: 13px;
    }

### HTMLの構成例（image-left-text-rightの場合）

パターンの構造に応じてHTMLを生成する。以下は2カラム（左画像・右テキスト）の構成例：

    <p class="slide-label">[{name}]</p>
    <div class="slide" style="display:flex; flex-direction:column;">
      <!-- タイトルエリア（SLIDE.mdの Slide Frame で定義） -->
      <div style="padding:14px 40px 12px; border-bottom:1px dashed #CCCCCC; flex-shrink:0; background:#FAFAFA;">
        <div class="area-label">Title Area — SLIDE.md 参照</div>
        <div style="font-size:16px; color:#CCCCCC; margin-top:4px;">スライドタイトルが入ります</div>
      </div>
      <!-- コンテンツエリア（このパターンが定義する領域） -->
      <div style="display:flex; flex:1; overflow:hidden;">
        <div style="width:50%; padding:24px 32px; display:flex; flex-direction:column; justify-content:center; border-right:1px solid #CCCCCC;">
          <div class="area-label">Image Area</div>
          <div class="placeholder-box" style="flex:1;">[IMAGE]</div>
        </div>
        <div style="width:50%; padding:24px 32px; display:flex; flex-direction:column; justify-content:center;">
          <div class="area-label">Heading (H2)</div>
          <div style="font-size:20px; font-weight:bold; color:#333; margin-bottom:12px;">見出しが入ります</div>
          <div class="area-label">Body Text</div>
          <div style="font-size:13px; color:#555; line-height:1.7; margin-bottom:12px;">本文テキストが入ります。2〜4行程度の説明文が配置されます。ここにメッセージの詳細を記述します。</div>
          <div class="area-label">Caption (optional)</div>
          <div style="font-size:11px; color:#999;">補足・注釈テキスト</div>
        </div>
      </div>
    </div>

### 生成時の注意

- パターンの構造（カラム数・配置）に合わせてHTMLを柔軟に組み立てる
- ラベルは必ずすべてのエリアに表示する
- ダミーテキストは日本語で記述する

## STEP 6：繰り返し・完了通知

### 複数パターンの繰り返し

対象パターンが複数ある場合、STEP 3〜5を1パターンずつ繰り返す：

1. パターン名を確認（STEP 3）
2. SLIDE-PATTERN-{name}.md を生成（STEP 4）
3. SLIDE-PATTERN-{name}.html を生成（STEP 5）
4. 次のパターンへ

## STEP 7：SLIDE-PATTERN-INDEX.md の更新

全パターンの生成が完了したら、`docs/SLIDE-PATTERN/SLIDE-PATTERN-INDEX.md` を更新する。

### インデックスファイルが存在する場合

今回生成したパターンの内容（概要・適したシーン）をもとに、`docs/SLIDE-PATTERN/SLIDE-PATTERN-INDEX.md` の**最も近いカテゴリの末尾**に追記する。

カテゴリは以下の12種類（ギャラリーと同じ順番）：
- 🎯 表紙・セクション
- 📋 目次
- ✏️ コンテンツ（本文）
- 📝 テキストリスト
- ➡️ フロー・ステップ
- 🔄 図解・ダイアグラム
- 🃏 カード・グリッド
- 📊 グラフ・データ
- 📑 テーブル・比較
- 🏆 KPI・まとめ
- ❓ Q&A・FAQ
- 👤 プロフィール

追記する形式（該当カテゴリのテーブル末尾に1行追加）：

    | {name} | {概要の内容} | {適したシーンの内容} |

どのカテゴリにも当てはまらない場合は、最も近いカテゴリを選んで追記する。
「パターン数：XX」の行も更新する（現在の件数＋追加件数に書き換える）。

### インデックスファイルが存在しない場合

`docs/SLIDE-PATTERN/` フォルダ内にある既存の `SLIDE-PATTERN-*/SLIDE-PATTERN-*.md` をすべて読み込み、各ファイルの `**概要：**` と `**適したシーン：**` を抽出してインデックスを新規作成する。

作成するファイルの形式：

    # SLIDE-PATTERN-INDEX

    スライドパターンの一覧です。`slide-deck-builder` はこのファイルを参照してパターンを選択します。
    新しいパターンを追加した際は、このファイルの末尾に追記してください。

    パターン数：XX

    | パターン名 | 概要 | 適したシーン |
    |---|---|---|
    | {name} | {概要} | {適したシーン} |
    （既存パターン＋今回生成したパターンをすべて含める）

### 完了通知

インデックス更新後、以下のようにユーザーに伝える：

> 「[X]件のスライドパターンファイルを生成し、SLIDE-PATTERN-INDEX.md を更新しました。
>
> [生成したフォルダ・ファイルの一覧]
> 例：
> - docs/SLIDE-PATTERN/SLIDE-PATTERN-image-left-text-right/
>   - SLIDE-PATTERN-image-left-text-right.md
>   - SLIDE-PATTERN-image-left-text-right.html
>
> SLIDE.mdとこれらのパターンファイルをAIツールに渡すことで、このデザインとレイアウトでスライドを生成できます。」
