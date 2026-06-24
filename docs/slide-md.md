# SLIDE.md — AI スライド専用デザインシステム（導入メモ）

[sho-ai-magic/slide.md](https://github.com/sho-ai-magic/slide.md)（MIT License）を本リポジトリに導入したときの構成・使い方・トンマナ運用上の注意をまとめる。

## これは何か / なぜ入れたか

「Claude Design で高品質スライドを爆速生成しつつ、色・フォント・余白・構図を統一する」ための
スライド専用デザインシステム。3 つのスキルと、デザインシステム（SLIDE.md）・
スライドパターン（SLIDE-PATTERN）で構成される。

**導入の動機（チーム再現性）**：これまで 5 co. の CI スライドは、ローカル/Drive 上の
`5co-CI-kit/` を理解できる人しか作れず、**他のメンバーが CI を再現できない**課題があった。
SLIDE.md は CI のデザイントークン（色・フォント・余白・構図）を 1 ファイルに自己完結で
書き出すフォーマットなので、これを **Claude Design / NotebookLM 等に渡すだけで誰でも
同じトンマナのスライドを再現**できる。そのために 5co-CI 準拠の `SLIDE-md-5co/` を同梱した。

## 導入物と配置

アセット（デザインシステム・パターン）は `docs/` 配下に集約し、3 つのスキルの
参照パスを `docs/SLIDE-md/` `docs/SLIDE-PATTERN/` に書き換えてある。
スキルはオリジナルの「カレントディレクトリ直下」前提から、本リポの `docs/` 規約に
合わせて調整済みのため、**リポジトリルートで Claude Code を起動すればそのまま動く**。

| 区分 | 配置 | 内容 |
|---|---|---|
| スキル | `.claude/skills/slide-deck-builder/` | プレゼン内容 → 設計書 `SLIDE-DECK.md` を生成 |
| スキル | `.claude/skills/slide-md-creator/` | 既存スライド/画像/URL → `SLIDE.md` + サンプル HTML を生成 |
| スキル | `.claude/skills/slide-pattern-creator/` | スライド画像 → 新規 `SLIDE-PATTERN` を抽出・追加 |
| デザインシステム | `docs/SLIDE-md/SLIDE-md-5co/` | **5co-CI v2 準拠版**（`SLIDE.md` + 6 枚 `sample.html`）。同梱はこの 1 種のみ |
| パターン | `docs/SLIDE-PATTERN/` | 99 種のレイアウトパターン + `SLIDE-PATTERN-INDEX.md` |

> upstream の汎用サンプル 4 種（anthropic / blue-simple-diagram / digital / green-blue-business）は、
> 5co のトンマナと一致せず混乱の元になるため**削除**した。5co 用は `SLIDE-md-5co/` のみを正とする。

## 基本フロー

### 既定（決定論的・崩れない）— Claude Code

**「CIスライド作って」＝ Claude Code が `SLIDE-md-5co/SLIDE.md`（正）と `5co-CI-kit` の
テンプレ/トークンを読み、A4-HTML を直書きする。** 生成AIに丸投げしないので再現性が高い。

1. `5co-CI-kit/5co_slide_template.html` を複製し、仕様のトークン/コンポーネントで文言だけ差し替え。
2. `python3 5co-CI-kit/slide_overflow_check.py <file.html>` で `OK` を確認。
3. Chrome の「印刷→PDF（背景ON）」で配布 PDF。

### 任意（速い初稿・Claude Code 非利用者向け）— Claude Design 等

`slide-deck-builder` で `SLIDE-DECK-{name}.md` を作り、[claude.ai/design](https://claude.ai/design) /
NotebookLM 等にアップして**生成**する。手軽だが生成方式のため厳密な CI 再現は決定論パスが上。
仕上げ・微調整は Markup / Edit、書き出しは PDF 推奨（PowerPoint は崩れる場合あり）。

> 使い分け：**最終の5co正式CIスライド＝決定論パス**／たたき台・CC非利用者の自助＝Claude Design。
> 両者は同じ `SLIDE.md`／`SLIDE-DECK.md` を食うので二重管理にならない。

## 5co-CI 準拠版（SLIDE-md-5co）について

`docs/SLIDE-md/SLIDE-md-5co/` は **実納品 CIスライドの CSS** を正データとして SLIDE.md
フォーマットに写したもの。トークンは以下のとおり（**2 色＋白のみ**）：

- **配色**：白 `#FFFFFF` ／ クリスタル `--crystal #C3D7EE`（PANTONE 2707 C）／ リッチブラック `--ink #101820`（PANTONE Black 6 C）＋ティント。グレー・純黒 `#000`・他色相は禁止。
- **フォント**：和文 `Hiragino Mincho ProN` ／ 欧文 `EB Garamond`（タグラインは italic）。
- **数字**：`lining-nums tabular-nums` 必須。
- **ロゴ**：ロックアップ v2＋「Strategy, refined.」固定。`fill=currentColor`。corner-logo 64px。
- **レイアウト**：**A4 横 297×210mm**・余白 16/18/14mm・表紙は cover-full＋数字フィールド・1 スライド 1 メッセージ。

`sample.html` は実納品デッキの CSS/数字フィールド/ロゴを再利用した **A4 汎用ダミー**（顧客データなし）。

### 正データの優先順位（重要）

**社内・対外の正式制作物は引き続き `5co-CI-kit/`（`CI_KICKOFF.md` ＋ `5co_slide_template.html`）を正**とする。
`SLIDE-md-5co/` と齟齬が出た場合は `5co-CI-kit/` を優先し、本ファイルを追従させる
（CI v2 のトークンが更新されたら `SLIDE-md-5co/SLIDE.md` と `sample.html` も同期する）。

### チームへの配布（Drive 等・非 git 環境）

Claude Code を使うメンバーは「CIスライド作って」で**決定論パス**（崩れない）。
Claude Code/git を使わないメンバーは、`SLIDE.md`（1 ファイル）を共有ドライブに置き
Claude Design / NotebookLM 等にアップして**生成**（任意・たたき台向け）。
非 git 作業環境への展開は `docs/non-git-deployment.md` も参照。

## ライセンス / 出典

導入物は [sho-ai-magic/slide.md](https://github.com/sho-ai-magic/slide.md) を複製したもの。
MIT License に基づき、以下の著作権表示を保持する。

```
MIT License

Copyright (c) 2026 sho-ai-magic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
