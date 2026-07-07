# 5 co. CI トンマナ｜セッション・キックオフ

あなたはこれから 5 co. のCI（トンマナ）に沿って制作します。まず下記の正データを読み、以後すべてこの基準で作ってください。

## スライドは「テンプレ複製」で作る（最優先）
- **0からCSSを書かない**。`slide/5co_slide_template.html` を複製し、要る型をコピペして**中身（文言・数値）だけ差し替える**。
- 全12スライド型（表紙/章扉/KPI/表/比較/タイムライン/キーメッセージ/組織図/対話/数値ハイライト/名刺/クロージング）がサンプル文付きで入っている。
- 仕上がり見本: `slide/5co_slide_template.pdf`。使い方: `slide/SLIDE_TEMPLATE_HANDOFF.md`。
- A4横・Chromeの「印刷→PDF保存（背景ON）」で配布用PDF。3色以外を使っていないか最後に自己チェック。

## 必読ファイル（~/dev/5co-ci-icon/）
- **slide/5co_slide_template.html … スライドの本体テンプレ（まずこれを複製）**
- slide/SLIDE_TEMPLATE_HANDOFF.md … テンプレの使い方・型一覧
- slide/assets/LOGO_HANDOFF.md … ロゴSVG・カラー・フォント・ルール
- docs/名刺デザイン_社内共有.md … コンセプト・トンマナの背景
- slide/assets/ci-theme.css … 3色CSSテーマ（:root変数＋クラス）
- slide/assets/NUMFIELD_HANDOFF.md … 数字背景SVGの使い方
- ロゴ本体: slide/assets/5co_logo_lockup_currentColor.svg（fill=currentColor）
- 数字背景: slide/assets/numfield_slide_16x9.svg / numfield_slide_allover.svg / numfield_header.svg ほか
- 完成名刺の実例: meishi/cards/<社員名>/（front/back PNG・.ai）

## 要点（これだけで最低限再現できる）
- 配色は**3色のみ**：白 #FFFFFF ／ アイスブルー #C3D7EE（PANTONE 2707 C）／ リッチブラック #101820（PANTONE Black 6 C）。グレー・黒#000・他色相は禁止。濃淡は3色の不透明度・白混ぜで。
- 文字・ロゴ＝濃紺、地・面・アクセント＝水色／白。
- フォント：和文 'Hiragino Mincho ProN','Yu Mincho',serif ／ 欧文 "Hoefler Text","Baskerville","Palatino","Hiragino Mincho ProN","Yu Mincho",serif（macOS標準・タグラインはイタリック）。**Georgia をフォールバックに置かない（厳禁・オールドスタイル数字事故の原因）**。字間ゆったり（letter-spacing .04em）。ブランド原典の Garamond は名刺等の別成果物のみ（#642 でスライドは Hoefler へ移行）。
- ロゴ＝マーク（水晶玉＝市場を透視する5）＋タグライン「Strategy, refined.」の**固定ロックアップ**。分離・歪み・比率変更しない。color指定で着色。
- **数字モチーフ**：多彩セリフ数字を粗密でちりばめ密→疎へディゾルブ（アイスブルー・うっすら）。**文字・図表には掛けない**（可読性最優先）。
- コンセプト：水晶玉で市場を透視し戦略を磨く＝Strategy, Refined.。静謐・上質・余白多め・装飾過多にしない。

## ルール
- 既存の文言・数値・固有名詞は改変しない（誤字修正のみ・要確認）。
- 3色以外を使っていないか自己チェックして明記。

---
更新: 2026-06-03 / 出典 `~/dev/5co-ci-icon`
