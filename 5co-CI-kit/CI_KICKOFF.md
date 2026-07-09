# 5 co. CI トンマナ｜セッション・キックオフ

あなたはこれから 5 co. のCI（トンマナ）に沿って制作します。まず下記の正データを読み、以後すべてこの基準で作ってください。

## CI用語（呼称統一・正式名）

制作物・ドキュメント・コメントで名前を揺らさない。以下を**正式名**とし、旧称は使わない
（`COPY_GUIDE.md` の用語ルールと同じ「一貫した呼称」の原則）。

| 対象 | 正式名 | CSS/実装 | 使わない旧称 |
|---|---|---|---|
| 水色 | **crystal blue（クリスタルブルー）** #C3D7EE・PANTONE 2707 C | `--crystal`（濃淡 `--crystal-55`/`--crystal-25`） | アイスブルー・シアン・水色・ice |
| 濃紺 | **ink（インク）** #101820・PANTONE Black 6 C | `--ink` | リッチブラック・墨・濃紺（プロースの補足は可） |
| 数字背景 | **Oracle（オラクル背景）**＝数字モチーフの全面背景 | `.numfield-full`・`numfield_*.svg` | numfield・数字フィールド・数字モチーフ（実装名としての numfield は可） |
| ロゴのモチーフ | **水晶玉（crystal ball）**＝市場を透視する「5」のマーク | — | ※色の crystal blue と混同しない（片方は色・片方はマーク） |
| 文言の正 | **crystal text（クリスタルテキスト）**＝「問いへの答え」方式の文言ガイド | `COPY_GUIDE.md` | 文言ガイド・コピーガイド（水晶玉シリーズの言葉レイヤー） |

> **なぜ**：同じものを「アイスブルー」「シアン」「水色」と呼び分けると、社員・外部・
> 派生セッションで指すものがぶれる。色は crystal blue、背景は Oracle の2語で通す。

## スライドは「現行版フォーマットの複製」で作る（最優先）
- **生成前に必ず本ディレクトリの `VERSION` を読む**。現行フォーマット（v3.2 以降＝
  `ci-format-v3.2.css` 系）とその構成ファイルは `VERSION` に書いてある。**そこに書かれた版で作る**。
- **0からCSSを書かない**。現行フォーマットのスタイルに**中身（文言・数値）だけ差し替える**。
  型仕様は `V3.2_FORMAT.md`（8型）、文言は `COPY_GUIDE.md`、検査は `slide_overflow_check.py`。
- **v3.2 系の書体（V3.1 タイポ）**: 本文＝ゴシック（Hiragino Sans）、表紙・章扉・見出し・欧文ラベルのみセリフ。
  `ci-format-v3.2.css` の `v31-typography` ブロックがこれを担う（詳細＝`SLIDE_DESIGN_GUIDELINES.md` §3）。
- `5co_slide_template.html`（週次14枚・v2系雛形＝本文明朝）は**週次ベース資料専用の残置雛形**。
  月次・新規デッキをこれから作らない（2026-07-07 WELLA 世代遅れ事故の原因）。
- A4横・出力は `ci-finalize.sh`。3色以外を使っていないか最後に自己チェック。

## 必読ファイル（本ディレクトリ `5co-CI-kit/`）
- **VERSION … 現行フォーマット宣言（まずこれを読む）**
- V3.2_FORMAT.md … 現行スライド8型の仕様
- COPY_GUIDE.md … **crystal text**＝文言の正（「問いへの答え」方式）
- SLIDE_DESIGN_GUIDELINES.md … タイポ・グリッド・ロゴ・表罫線の規範
- LOGO_HANDOFF.md … ロゴSVG・カラー・フォント・ルール
- ci-theme.css … 3色CSSテーマ（:root変数＋v2基本クラス。単体では本文明朝＝v2系）
- NUMFIELD_HANDOFF.md … 数字背景SVGの使い方
- 5co_slide_template.html … 週次v2雛形（残置。月次・新規には使わない）
- 完成名刺の実例: meishi/cards/<社員名>/（front/back PNG・.ai）

## 要点（これだけで最低限再現できる）
- 配色は**3色のみ**：白 #FFFFFF ／ crystal blue #C3D7EE（PANTONE 2707 C）／ ink #101820（PANTONE Black 6 C）。グレー・黒#000・他色相は禁止。濃淡は3色の不透明度・白混ぜで。
- 文字・ロゴ＝ink、地・面・アクセント＝crystal blue／白。
- フォント：和文 'Hiragino Mincho ProN','Yu Mincho',serif ／ 欧文 "Hoefler Text","Baskerville","Palatino","Hiragino Mincho ProN","Yu Mincho",serif（macOS標準・タグラインはイタリック）。**Georgia をフォールバックに置かない（厳禁・オールドスタイル数字事故の原因）**。字間ゆったり（letter-spacing .04em）。ブランド原典の Garamond は名刺等の別成果物のみ（#642 でスライドは Hoefler へ移行）。
- ロゴ＝マーク（水晶玉＝市場を透視する5）＋タグライン「Strategy, refined.」の**固定ロックアップ**。分離・歪み・比率変更しない。color指定で着色。
- **Oracle（数字背景）**：多彩セリフ数字を粗密でちりばめ密→疎へディゾルブ（crystal blue・うっすら）。**文字・図表には掛けない**（可読性最優先）。表紙・章扉の大判のみ。
- コンセプト：水晶玉（crystal ball）で市場を透視し戦略を磨く＝Strategy, Refined.。静謐・上質・余白多め・装飾過多にしない。表紙には `.cover-ci` でこのコンセプトを必ず明記（→ `V3.2_FORMAT.md`「表紙CIコンセプト」）。

## ルール
- 既存の文言・数値・固有名詞は改変しない（誤字修正のみ・要確認）。
- 3色以外を使っていないか自己チェックして明記。

---
更新: 2026-07-07（VERSION 起点の導線へ改定・WELLA 世代遅れ事故対応）/ 初版出典 `~/dev/5co-ci-icon`
