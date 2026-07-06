---
name: slide-md-creator
description: 既存のスライド・画像・WebサイトからデザインシステムSLIDE.mdと6ページのHTMLサンプルスライドを生成する。「このスライドのデザインシステムを作って」「SLIDE.mdを生成して」「SLIDE.mdを作りたい」「このサイトのデザインでSLIDE.mdを生成して」「slide-md-creator」と言われたときに使用する。※5co の正データ仕様は既に docs/SLIDE-md/SLIDE-md-5co/SLIDE.md にある。本スキルは新規ブランド/汎用のデザインシステムを作る任意経路で、5co公式CIの再作成には使わない。
---

# slide-md-creator

既存のスライド・画像・Webサイト・テキストからデザイン情報を解析し、AIツール（Claude Design、NotebookLM、Google Slides等）向けのスライドデザインシステム定義ファイル（SLIDE.md）と6ページのHTMLサンプルスライドを生成する。

## STEP 1：入力の受け取り

スキル起動時、ユーザーが以下のいずれかを提供しているか確認する：

- 画像ファイル（スライドのスクリーンショット、ロゴ、ブランドガイド等）
- WebサイトのURL
- 既存スライドのファイル（PowerPoint / Google Slides）
- テキストによるデザインの説明

**何も提供されていない場合**、以下のように尋ねる：

> 「参考にしたいスライド・画像・WebサイトのURLはありますか？テキストでデザインのイメージを説明していただくことも可能です。」

複数の入力が提供された場合はすべてを受け取り、STEP 2の分析に使用する。

## STEP 2：デザイン要素の分析

受け取った入力を解析し、以下の要素を読み取る。読み取れた内容をユーザーに箇条書きで提示する。

### 分析する要素

**Colors（カラー）**
- Primary（メインカラー）：最も多く使われている色。HEXコードで記録する。
- Secondary（サブカラー）：2番目に使われている色。HEXコードで記録する。
- Background（背景色）：スライドの背景色。HEXコードで記録する。
- Accent（強調色）：ボタン・下線・強調に使われている色。HEXコードで記録する。
- Text（テキスト色）：本文テキストの色。HEXコードで記録する。

**Typography（タイポグラフィ）**
- 見出しフォント：フォント名・サイズ（px）・ウェイト（bold / regular等）
- 本文フォント：フォント名・サイズ（px）・ウェイト
- キャプションフォント：フォント名・サイズ（px）・ウェイト
- フォント名が不明な場合は「不明」と記録し、STEP 3で確認する

**Layout（レイアウト）**
- スライドサイズ：16:9 / 4:3 / その他
- 余白：上下左右のおおよその余白サイズ（px）
- 整列の基準：左寄せ / 中央寄せ / 右寄せ

**Slide Frame（枠要素）**
- タイトルエリア：上部左寄せ / 上部中央揃え、装飾の有無（アクセントバー・下線 等）
- ページ番号：右下 / 左下 / なし、表示フォーマット（01 / 1 / 1/5 等）
- 装飾：アクセントバー・装飾図形・ロゴ等の有無と配置

**Tone（雰囲気）**
- フォーマル / カジュアル / ミニマル / ボールド / 等
- どんなシーンに合うか（ビジネス発表・社内共有・カンファレンス 等）

### 分析結果の提示例

> 「以下のデザイン要素を読み取りました：
>
> **カラー**
> - Primary：#1A237E（ダークネイビー）
> - Secondary：#E3F2FD（ライトブルー）
> - Background：#FFFFFF（白）
> - Accent：#FF6F00（オレンジ）
> - Text：#212121（ほぼ黒）
>
> **タイポグラフィ**
> - 見出し：Noto Sans JP / 36px / Bold
> - 本文：Noto Sans JP / 18px / Regular
> - キャプション：不明
>
> **レイアウト**
> - スライドサイズ：16:9
> - 余白：上下48px・左右64px
> - 整列：左寄せ
>
> **雰囲気**：フォーマル、ビジネス発表・提案資料向け」

## STEP 3：確認の対話

STEP 2の分析結果を提示した後、不明・不確かな点についてユーザーに確認する。

### 確認のルール

- 質問は**合計3〜5問以内**に抑える
- 1つのメッセージにつき**1問だけ**聞く
- 読み取れた情報については聞かない（不明な情報だけを確認する）
- ユーザーが「わからない」と答えた場合は、一般的な値（Webセーフフォント、標準余白等）を使用して進める

### 確認すべき優先順位

1. フォント名が「不明」の場合 → 「見出しや本文に使われているフォントをご存知ですか？（例：Noto Sans JP、Hiragino Kaku Gothic等）」
2. カラーが読み取れなかった場合 → 「〇〇の色をご存知でしたら教えてください」
3. スライドサイズが不明の場合 → 「スライドのサイズは16:9（横長）と4:3（やや正方形）のどちらですか？」
4. 雰囲気の確認 → 「このデザインはどんな場面での使用を想定していますか？（例：社内会議・顧客向けプレゼン・カンファレンス等）」

### 確認完了の判断

以下のいずれかになったら確認終了とする：
- 5問の確認が終わった
- 未確認の情報がなくなった
- ユーザーが「進めてください」等の意思を示した

確認完了後、「では内容をもとにSLIDE.mdとsample.htmlを生成します」と伝えてSTEP 4に進む。

## STEP 4：SLIDE.mdの生成

STEP 2〜3で確定したデザイン情報を使い、以下のテンプレートに値を埋めて `SLIDE.md` を生成する。

### 出力フォルダの決定

ファイルはカレントディレクトリ内の `docs/SLIDE-md/` フォルダの中に `SLIDE-md-{source}` というフォルダを作成して保存する。`{source}` はソースの種類に応じて以下のルールで決める：

- **URLの場合：** ドメイン名から主要な単語を抽出する（例：`https://www.apple.com` → `apple`、`https://www.google.co.jp` → `google`）
- **ファイルの場合：** ファイル名（拡張子なし）を使う（例：`company-deck.pptx` → `company-deck`）
- **テキスト説明の場合：** 説明文からブランド名や代表的なキーワードを1つ抽出する

フォルダ名はすべて小文字・半角英数字・ハイフンのみを使用する。作成するフォルダの例：`docs/SLIDE-md/SLIDE-md-apple`、`docs/SLIDE-md/SLIDE-md-google`、`docs/SLIDE-md/SLIDE-md-toyota`

### SLIDE.mdの出力形式

以下の形式で出力すること。各項目の `[　]` の中に分析・確認で得た実際の値を入れる。Markdownの各セクションの後にYAML形式でも同じ値を記載し、AIツールが値を正確に読み取れるようにする。

---
出力ファイル名：docs/SLIDE-md/SLIDE-md-{source}/SLIDE.md

# SLIDE.md

このファイルはスライドデザインシステムの定義書です。AIツール（Claude Design、NotebookLM、Google Slides等）にこのファイルを渡すことで、一貫したデザインのスライドを生成できます。

## Overview

**参照ソース：** [参考にしたスライド・サイト・ブランドの名称や説明]
**マッチするシーン：** [このデザインが合う場面・用途・雰囲気]

## Colors

| 役割 | カラー名 | HEXコード |
|---|---|---|
| Primary | [色名] | [#XXXXXX] |
| Secondary | [色名] | [#XXXXXX] |
| Background | [色名] | [#XXXXXX] |
| Accent | [色名] | [#XXXXXX] |
| Text | [色名] | [#XXXXXX] |

    colors:
      primary: "[#XXXXXX]"
      secondary: "[#XXXXXX]"
      background: "[#XXXXXX]"
      accent: "[#XXXXXX]"
      text: "[#XXXXXX]"

## Typography

| 役割 | フォント | サイズ | ウェイト |
|---|---|---|---|
| 見出し（H1） | [フォント名] | [Xpx] | [Bold/Regular] |
| 見出し（H2） | [フォント名] | [Xpx] | [Bold/Regular] |
| 本文 | [フォント名] | [Xpx] | [Regular] |
| キャプション | [フォント名] | [Xpx] | [Regular] |

    typography:
      heading_h1:
        font: "[フォント名]"
        size: "[Xpx]"
        weight: "[700/400]"
      heading_h2:
        font: "[フォント名]"
        size: "[Xpx]"
        weight: "[700/400]"
      body:
        font: "[フォント名]"
        size: "[Xpx]"
        weight: "[400]"
      caption:
        font: "[フォント名]"
        size: "[Xpx]"
        weight: "[400]"

## Layout

- **スライドサイズ：** [16:9 / 4:3]（幅[X]px × 高さ[X]px）
- **余白（上下）：** [Xpx]
- **余白（左右）：** [Xpx]
- **テキスト整列：** [左寄せ / 中央寄せ]

    layout:
      slide_size: "[16:9 / 4:3]"
      width: "[X]px"
      height: "[X]px"
      padding_vertical: "[X]px"
      padding_horizontal: "[X]px"
      text_align: "[left / center]"

## Slide Frame

スライドの全ページに共通して適用される「枠」の要素を定義します。SLIDE-PATTERN-{name}.mdはコンテンツエリアの構造のみを定義するため、タイトルエリア・ページ番号・装飾はすべてここで一括管理します。これにより、どのパターンを使っても枠の見た目が統一されます。

**タイトルエリア：** [配置と装飾の説明（例：上部左寄せ、直下にアクセントカラーのバーを配置）]
**ページ番号：** [配置とフォーマット（例：右下・小文字・テキストカラー / なし）]
**装飾：** [共通装飾の説明（例：幅48px・アクセントカラーのアクセントバー / なし）]

    slide_frame:
      title_area:
        position: "[top-left / top-center]"
        text_align: "[left / center]"
        decoration: "[accent-bar / underline / none]"
      page_number:
        position: "[bottom-right / bottom-left / none]"
        format: "[01 / 1 / 1/5 等]"
      decoration: "[accent-bar / none]"

## Do / Don't

**Do（やること）**
- [このデザインで推奨されること]
- [このデザインで推奨されること]

**Don't（やってはいけないこと）**
- [このデザインで避けるべきこと]
- [このデザインで避けるべきこと]
---

### Do / Don't の生成方針

- **Do** はデザインの特徴から自然に導かれるルールを記述する（例：ミニマルなデザインなら「1スライド1メッセージを徹底する」）
- **Don't** はデザインと相反する要素を記述する（例：モノクロデザインなら「原色や派手なグラデーションを使わない」）
- 各2〜4項目を目安にする

## STEP 5：sample.htmlの生成

SLIDE.mdで定義したデザイントークン（色・フォント・余白）を適用した6ページのHTMLスライドを生成し、STEP 4で作成した `docs/SLIDE-md/SLIDE-md-{source}/` フォルダ内に `sample.html` として保存する。

### ページ構成（固定）

| ページ番号 | スライドの種類 | 主な内容 |
|---|---|---|
| 1 | デザインシステム概要 | Overview・カラーパレット・タイポグラフィの一覧（このデザインシステムの仕様書ページ） |
| 2 | 表紙（タイトルスライド） | タイトル・サブタイトル・会社名や日付のプレースホルダー |
| 3 | セクションタイトル | セクション番号・セクション名 |
| 4 | 箇条書き（本文スライド） | 見出し・3〜5項目の箇条書き |
| 5 | データチャート | 見出し・簡易的な棒グラフまたは表（CSSのみで実装） |
| 6 | まとめ | まとめの見出し・3〜5項目の要点・締めのメッセージ |

### ページ1：デザインシステム概要ページの仕様

ページ1は他のスライドとは異なる「仕様書ページ」として生成する。このページの目的は、SLIDE.mdのOverview・カラーパレット・タイポグラフィを視覚的に一覧できるようにすることで、ユーザーがデザインシステムの内容を一目で把握できるようにすることである。

**レイアウト構造：**

スライドを上下2段に分割する。上段にOverview、下段を左右に分割してLeft=Colors・Right=Typographyを配置する。

    ┌──────────────────────────────────────────────────────────────────┐
    │  DESIGN SYSTEM  —  {ソース名}                          [header] │
    ├──────────────────────────────────────────────────────────────────┤
    │  Overview                                               [上段]  │
    │  参照ソース: 〇〇  ／  マッチするシーン: 〇〇                     │
    ├─────────────────────────────┬────────────────────────────────────┤
    │  Colors                [下段左]│  Typography              [下段右]│
    │                              │                                   │
    │  ████████████████  Primary   │  Heading H1                      │
    │  #XXXXXX                     │  フォント名・36px・Bold            │
    │                              │                                   │
    │  ████████████████  Secondary │  Heading H2                      │
    │  #XXXXXX                     │  フォント名・24px・Bold            │
    │                              │                                   │
    │  ████████████████  Background│  Body Text                       │
    │  #XXXXXX                     │  フォント名・18px・Regular         │
    │                              │                                   │
    │  ████████████████  Accent    │  Caption                         │
    │  #XXXXXX                     │  フォント名・12px・Regular         │
    │                              │                                   │
    │  ████████████████  Text      │                                   │
    │  #XXXXXX                     │                                   │
    └─────────────────────────────┴────────────────────────────────────┘

**実装の詳細：**

- ページ全体の背景はSLIDE.mdのBackgroundカラーを使用する
- ヘッダー行（「DESIGN SYSTEM — {ソース名}」）はPrimaryカラーの背景に白テキストで表示する。フォントサイズは13px・padding 10px 20px
- **上段（Overview）：** 背景色はPrimaryカラーを10〜15%の透明度で重ねた淡い色（またはSecondaryカラー）とし、「参照ソース：〇〇　／　マッチするシーン：〇〇」を1行で横並びに表示する。高さはスライド全体の約25%
- **下段：** 残り75%の高さをflexboxで左右に分割する（左50%・右50%）
- **下段左（Colors）：** 5色（Primary・Secondary・Background・Accent・Text）をカード形式で2列グリッドに並べる。各カードは `border: 1px solid #E5E5E5`・`border-radius: 10px`・`background: #FFF`・`overflow: hidden` で囲み、上部に色のスウォッチ（`height: 72px`・角丸なし）、下部のパディングエリア（`padding: 8px 10px`）に役割名（`font-size: 12px・font-weight: 600`）とHEXコード（`font-size: 11px・font-family: monospace・color: #888`）を縦に並べる。Backgroundカラーのスウォッチには `border-bottom: 1px solid #E5E5E5` を付けて白背景でも視認できるようにする
- **下段右（Typography）：** 各フォント役割（Heading H1・H2・Body・Caption）について、役割ラベルをPrimaryカラーの10px大文字で、その下にサンプルテキストをそのフォント・サイズ・ウェイトで実際に適用して表示する。サンプルテキストは「あいう ABC 123」とする
- 下段の左右の見出し（「Colors」「Typography」）はPrimaryカラーのテキスト・12px・font-weight: 600で各カラムの上部に表示し、細い区切り線（1px）を引く
- スライドの枠（.slide）のpaddingは0にして、ヘッダー行・上段・下段がスライド全体を埋めるようにする
- このページにはSlide Frameのタイトルエリア・ページ番号装飾は適用しない（ヘッダー行が代わりの役割を果たす）

### HTMLの実装方針

- **1つのHTMLファイル**にすべてのスライドを縦に並べて出力する
- 各スライドは `<section class="slide">` で区切る
- CSSのカスタムプロパティ（変数）でSLIDE.mdのデザイントークンを定義する
- 外部フォントはGoogle Fonts CDNを使用する（フォントが利用可能な場合）
- JavaScriptは使用しない

### CSSカスタムプロパティの定義

HTMLの `<style>` タグ内で以下のカスタムプロパティを定義し、各スライドのスタイルに適用する：

    :root {
      --color-primary: [SLIDE.mdのPrimaryカラー];
      --color-secondary: [SLIDE.mdのSecondaryカラー];
      --color-background: [SLIDE.mdのBackgroundカラー];
      --color-accent: [SLIDE.mdのAccentカラー];
      --color-text: [SLIDE.mdのTextカラー];
      --font-heading: [SLIDE.mdの見出しフォント];
      --font-body: [SLIDE.mdの本文フォント];
      --font-size-h1: [SLIDE.mdの見出しH1サイズ];
      --font-size-h2: [SLIDE.mdの見出しH2サイズ];
      --font-size-body: [SLIDE.mdの本文サイズ];
      --slide-padding-v: [SLIDE.mdの上下余白];
      --slide-padding-h: [SLIDE.mdの左右余白];
    }

    .slide {
      width: 960px;
      height: 540px; /* 16:9の場合 */
      background: var(--color-background);
      padding: var(--slide-padding-v) var(--slide-padding-h);
      font-family: var(--font-body);
      color: var(--color-text);
      margin: 32px auto;
      box-shadow: 0 4px 24px rgba(0,0,0,0.12);
    }

### 生成完了の通知

sample.html生成後、以下のようにユーザーに伝える：

> 「`docs/SLIDE-md/SLIDE-md-{source}/` フォルダにSLIDE.mdとsample.htmlを生成しました。
>
> - `SLIDE.md`：デザインシステムの定義書。AIツールに渡す際のメインファイルです。
> - `sample.html`：ブラウザで開くとデザインを確認できます。AIツールへの参考資料としても使えます。
>
> このSLIDE.mdとsample.html、および別途作成したスライドパターンファイルをAIツールに渡すことで、このデザインでスライドを生成できます。」
