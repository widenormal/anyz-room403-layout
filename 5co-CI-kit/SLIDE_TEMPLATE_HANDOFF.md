# 5 co. スライド・テンプレート一式｜使い方

> デザインはこのテンプレに任せ、**中身（文言・数値）だけ差し替える**のが原則。
> 0からCSSを書かない／3色以外を足さない／数字背景とロゴは触らない。

## ファイル
| ファイル | 役割 |
|---|---|
| `slide/5co_slide_template.html` | **本体**。全12スライド型をサンプル文付きで収録（A4横・印刷でPDF） |
| `slide/5co_slide_template.pdf` | 仕上がり見本（12ページ＝12型） |
| `slide/assets/numfield_slide_allover.svg` | 本文の全面うっすら数字背景（自動参照） |
| `slide/assets/numfield_slide_16x9.svg` | 章扉の中央クリア数字背景（自動参照） |
| `slide/assets/numfield_cover_left.svg` | 表紙 左ゾーンの縦長数字背景（自動参照） |
| `slide/assets/5co_logo_lockup_currentColor.svg` | ロゴ（テンプレ内に symbol 化済み・編集不要） |

## 作り方（最短）
1. `5co_slide_template.html` を複製して名前を付ける（例：`組織展望面談_◯◯_スライド.html`）。
2. 要る**スライド型 `<section class="slide ...">` をコピペ**して並べ、中の文言・数値を差し替える。
3. Chrome で開く → **印刷 → PDFに保存**（用紙=**A4横**・余白=**なし**・**背景のグラフィック=ON**）。
4. 仕上げに「3色以外を使っていないか」を自己チェック。
5. **検査（必須）**: `slide_overflow_check.py`（はみ出し・隅ロゴ・3色）＋
   `slide_visual_regression.py`（正本との計算済みスタイル/構造の乖離検出）。
   テンプレ正本そのものを意図的に変えた場合のみ `--update-baseline` で基準を更新。

## このテンプレの成り立ち（重要）

`5co_slide_template.html` は **CI v2 正本デッキ（週次レポート）をそのまま複製し、ダミー文/
サンプル値に差し替えた**正本テンプレ。CSS・レイアウト・スライド構造は正本とバイト一致で、
**文言・数値は汎用ダミー**（`顧客名`・`X.XX億`・`NN%`・`YYYY年MM月DD日`・`ブランドA`・`EM-1` 等）、
**顧客ロゴは `.logo-slot`（ブランク枠／"CLIENT LOGO"）** に置換済み。ブランド名・実数・個人情報
など機密は完全除去（grep 検証済み）。＝「CSSを再構築しない」ので正本との乖離が原理的に起きない。
隅ロゴ（本文右上）は **64px**、OKR/表ページの罫線は既定値で確定済み。

## 構成（正本 V1 と同じ14スライド）

表紙(`slide cover-full`)／本文(`slide`：KPIツリー・ドリルダウン表 等)／章扉(`slide cover-full pd-divider`)／
サマリ(`slide dark`)／付録扉(`slide dark divider`) 等、**正本の型をそのまま**使う。
利用可能クラス: `.slide`(`.pale`/`.pale-strong`/`.dark`/`.center`)・`.t-xl…t-note`・`.kicker`・
`.accent-bar`・`.lead`・`h2.title`・`table`(`.hl`/`.num`)・`.kpis>.kpi`・`.cols`・`.tag`・`.bars` ほか。

## 埋め方

1. `.logo-slot`（"CLIENT LOGO" ブランク枠）に**顧客ロゴ**を差し込む（`<img>` 等）。5co ロックアップ（隅・64px）は既定で入っている。
2. ダミー文/サンプル値（`顧客名`・`X.XX億`・`NN%`・`ブランドA` 等）を実際の**文言・数値**に置き換える（型・レイアウトは触らない）。
3. 不要なスライド `<section>` は削除、足りなければ既存型を**コピペして複製**。

## 配色ルール（厳守・3色のみ／CI v2）
- 白 `#FFFFFF`／crystal `#C3D7EE`（DIC 576 アミ40%）／ink `#101820`（リッチブラック）。
- 文字・ロゴ＝ink、地・面・アクセント＝crystal/白。**グレー・黒#000・他色相は禁止**。
- 濃淡は不透明度か白混ぜ（`--crystal-25`=#F0F5FB／`--crystal-55`=#DEE9F6／`--ink-60` 等）。
- 強調は `.hl`（薄 crystal 行）・`.dark`（ink 面）・`.tag`（crystal チップ）・`.accent-bar`。

## よく使う小ワザ（CI v2）
- **ink 面で強調**: `<section class="slide dark">`（文字＝crystal）。
- **表の注目行**: その行の各 `<td class="hl">`（`tr` のゼブラより優先）。数値列は `<td class="num">`。
- **メモ欄**: `<div class="memo">`（その場記入）。
- **φタイポ**: `.t-xl/.t-lg/.t-md/.t-body/.t-note`、本文見出しは `h2.title`（22px）。
- **実物名刺を見せる**: K 型の `<svg>` ロゴを実物 PNG の `<img>` に差し替え可。

## 機微情報の注意（人事系デッキ）
- 処遇・グレード・生涯賃金などは**サンプル雛形には実数を入れない**。実数版は KR-1A の所定フォルダで作る。
- 「確約ではない／試算・たたき台」「規程・個別契約で確定」を必ず注記（`.note`）。

---
更新: 2026-06-03 / 出典 `~/dev/5co-ci-icon/slide/`
