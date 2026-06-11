# 5 co. ロゴ / ブランド データ（HTMLスライド用ハンドオフ）

> このmdをスライド作成スレッドに貼り付けてください。ロゴは下記SVGをインライン展開し、CSSの `color` で色指定します（`fill="currentColor"`）。

## 1. ロゴ（固定ロックアップ＝マーク＋タグライン）
**マーク（5＋エナジーフレア＝水晶玉）と タグライン「Strategy, refined.」は一体の固定ロックアップ。分離・比率変更・歪み禁止。**

- 推奨（recolor可・currentColor）: `slide/assets/5co_logo_lockup_currentColor.svg`
  - viewBox `0 0 194.13 173.88`、全パス `fill="currentColor"`
  - 使い方: インラインSVGを置き、親要素に `color: <ブランド色>` を指定すれば任意色になる
- 原本（グレー固定）: `slide/5co_logo_tagline.svg`
- マーク＋タグライン別アセット: `slide/5co_mark.svg`

```html
<!-- 例: 紺ロゴ -->
<span style="color:#101820; display:inline-block; width:120px">
  <!-- ここに 5co_logo_lockup_currentColor.svg の中身を貼る -->
</span>
```

## 2. カラー
> 最終仕様＝**2色刷り（紺＋アイスブルー）**。リッツ・カールトン的な上質な配色。

| 役割 | 画面(hex) | 印刷（スポット・推奨） | 用途 |
|---|---|---|---|
| **ロゴ／文字＝リッチブラック** | `#101820`（近似） | PANTONE Black 6 C（CI v2・2026-06-10改定） | ロゴ・全テキスト（版1） |
| **署名色＝アイスブルー** | `#C3D7EE`（近似） | PANTONE 2707 C（CI v2・2026-06-10改定） | 数字背景・面・反転地（版2） |
| ニュートラル（白） | `#FFFFFF` | — | 地・反転ロゴ |

- アイスブルー地ではロゴ＝**ネイビー**。濃い地では**白**反転も可。
- ※色名は推奨。最終は**実Pantoneチップ**で確定。

## 3. フォント
- 欧文/数字（セリフ）: **Garamond Premier Pro** → web代替 `'EB Garamond', Garamond, Georgia, serif`
- 和文: **Hiragino Mincho ProN** → 代替 `'Yu Mincho', serif`
- タグライン「Strategy, refined.」= Garamondイタリック

## 4. コンセプト / モチーフ
- **水晶玉**（市場を透視・予測）に「5」が写り込む。創業の五輪書（地水火風空）＝5つの反射。
- タグライン: **Strategy, Refined.**（曇りを払い、市場の像を澄ませて利益へ）
- **数字モチーフ**: 多彩セリフ数字を粗密（小さい字を多く＋大きい字を疎に）でちりばめ、密→疎へディゾルブ。色はシアン`#C3D7EE`（白地）／白抜き（シアン地）。背景に薄く使用、文字には掛けない。

## 5. 使用ルール（厳守）
- ロゴはロックアップで使用（マーク＋タグライン一体）。
- 余白を確保し、数字や他要素を**ロゴに重ねない**（重ねる場合はロゴ周りをソフトに抜く）。
- 最小サイズで潰れる場合もマーク（水晶玉の球）を identity の最後の砦とする。
- 背景・アクセントにはシアン、ロゴはネイビー、本文は墨、が基本配色。

---
更新: 2026-06-03 / 出典 repo `~/dev/5co-ci-icon`（`CLAUDE.md` / `docs/brand_book_crystalball.md` / `memory/decisions.md`）
