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

## スライド型（12種）
| 記号 | 型 | 主クラス | 用途 |
|---|---|---|---|
| A | 表紙 | `slide cover-card` | タイトル・対象者・アジェンダ |
| B | 章扉 | `slide numbg-cover reverse section-divider` | セクション区切り |
| C | リード＋KPI | `slide numbg-content` ＋ `kpi-grid` | 主張＋数値4枚 |
| D | 表 | `slide numbg-content` ＋ `table`（`tr.me`で強調） | 一覧・構造 |
| E | 比較2カラム | `compare` ＋ `card`/`card navy` | 現在 vs 目指す姿 |
| F | タイムライン | `tl`（3カラム） | ロードマップ |
| G | キーメッセージ | `keymsg` | 一文を大きく |
| H | 組織図 | `org-compare` | 体制ビフォー/アフター |
| I | 対話・傾聴 | `listen-tag` ＋ `memo` | 問い＋その場メモ |
| J | 数値ハイライト | `keymsg`＋大数字 | 記憶に残す数字 |
| K | 名刺見せ | `meishi`（または実物PNGを`<img>`） | 昇格時の名刺 |
| L | クロージング | `slide reverse center` | 裏表紙・締め |

## 配色ルール（厳守・3色のみ）
- 白 `#FFFFFF`／アイスブルー `#C3D7EE`（PANTONE 2707 C）／リッチブラック `#101820`（PANTONE Black 6 C）。
- 文字・ロゴ＝濃紺、地・面・アクセント＝水色/白。**グレー・黒#000・他色相は禁止**。
- 濃淡は不透明度か白混ぜ（`--powder-pale` `--navy-60` 等の用意済み変数）で。
- 強調は `.em`（濃紺カード）・`.navy`（濃紺）・`.me`（薄水色行）・水色の差し色バー。

## よく使う小ワザ
- **濃紺カードで強調**: `<div class="card kpi em">`／`<div class="card navy">`
- **表の注目1行**: `<tr class="me">`
- **問い・傾聴**: `<div class="ask">` ／ `<div class="memo">`（記入欄）
- **長くて入り切らない本文**: `.fit` で自動縮小されるが、まず文を削る（詰め込みより余白）。
- **実物名刺を見せる**: `meishi/cards/<社員名>/<key>_front.png` を `<img>` で K 型に差し込む。

## 機微情報の注意（人事系デッキ）
- 処遇・グレード・生涯賃金などは**サンプル雛形には実数を入れない**。実数版は KR-1A の所定フォルダで作る。
- 「確約ではない／試算・たたき台」「規程・個別契約で確定」を必ず注記（`.note`）。

---
更新: 2026-06-03 / 出典 `~/dev/5co-ci-icon/slide/`
