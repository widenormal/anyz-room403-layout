# 5co. ブランドデザインガイドライン（2026 版）

> このドキュメントは **CI を破らずに資料を量産する**ための統一ルール。
> 名刺・スライド・社内資料・サイト等すべての制作物が対象。CI_KICKOFF.md / NUMFIELD_HANDOFF.md / LOGO_HANDOFF.md の集約版。

---

## 1. カラー（厳守・3 色のみ）

| ロール | 名前 | HEX | PANTONE | 用途 |
|---|---|---|---|---|
| Base | White | `#FFFFFF` | — | 地・本文背景 |
| Primary | Rich Black | `#101820` | Black 6 C | ロゴ・本文タイポ・強調 |
| Accent | Ice Blue | `#C3D7EE` | 2707 C | 数字パターン・アクセントバー・サブ強調 |

派生トーン（上記からの透明度・白混ぜで作る／単独色追加禁止）：

| 変数 | 値 |
|---|---|
| `--powder-pale` | `#DCEBF1` |
| `--powder-soft` | `#C6DEE9` |
| `--navy-85` | `rgba(14,26,56,.85)` |
| `--navy-60` | `rgba(14,26,56,.60)` |
| `--navy-14` | `rgba(14,26,56,.14)` |

### NG カラー

❌ グレー（`#888`, `#666` 等）／純黒（`#000`）／他色相（緑・赤・橙 等の単独使用）。

---

## 2. タイポグラフィ

| 言語 | フォント | 用途 |
|---|---|---|
| 日本語 | Hiragino Mincho ProN / Yu Mincho（serif） | 本文・見出し |
| 欧文 | EB Garamond / Garamond / Georgia（serif） | 数字・eyebrow・タグライン |
| タグライン専用 | EB Garamond Italic | 「Strategy, refined.」専用 |

サンセリフは原則使用しない（明朝統一でブランドの落ち着きを保つ）。

---

## 3. ロゴ（ロックアップ・固定運用）

### 基本ロックアップ

- マーク（5＋水晶玉）＋ タグライン「Strategy, refined.」を **1 つの組（ロックアップ）として固定**
- 分離・再配置・比率変更は **禁止**
- `slide/5co_logo_tagline.svg` が正データ（`5co-CI-kit/assets/` にも同等品あり）

### サイズ規定

| 媒体 | 推奨サイズ | 最小 | 備考 |
|---|---|---|---|
| 名刺（91×55mm）front 左 | 約 25mm 幅 | 18mm | 名刺天地基準 |
| スライド A4 横 表紙左ゾーン | **54〜64mm 幅** | 40mm | スライド天地 210mm の 25〜30% |
| スライド 各ページ右上 corner-logo | **24〜28mm 幅** | 20mm | 控えめなブランド帰属表示 |
| Web ヘッダー | 100〜140px | 80px | — |

### NG

❌ 表紙に巨大ロゴ（≥ 80mm）／中央巨大配置
❌ マークだけ取り出してタグライン削除
❌ 配色変更（マーク・タグラインは常に Navy）
❌ 影・グロー・グラデーション追加

---

## 4. 数字パターン背景（numfield）

### 用途別 SVG 資産

| ファイル | 用途 | 中心構成 |
|---|---|---|
| `numfield_slide_16x9.svg`（1920×1080） | 表紙・章扉 | 中央クリア・縁に数字 |
| `numfield_slide_allover.svg`（1920×1080） | 本文ページ | 全面うっすら |
| `numfield_cover_left.svg`（1200×2100） | 表紙 **左ゾーン**（縦長） | 左密 → 右ディゾルブ（**名刺 front と同構成**） |
| `numfield_header.svg`（1920×180） | ヘッダー帯（左クリア・右流れ） | 左 1/3 はクリア |
| `numfield_header_even.svg`（1920×180） | ヘッダー帯（均一） | 全幅うっすら |

### CSS 適用パターン（HANDOFF 準拠）

```css
/* 表紙：左ゾーンに数字パターン、地は白のまま */
.slide.cover .cover-left{
  background: url("assets/numfield_cover_left.svg") center/cover no-repeat, var(--white);
}

/* 章扉：中央クリアの 16:9 */
.slide.section-divider{
  background: url("assets/numfield_slide_16x9.svg") center/cover no-repeat, var(--white);
}

/* 本文ページ：うっすら全面 */
.slide.content{
  background: url("assets/numfield_slide_allover.svg") center/cover no-repeat, var(--white);
}
```

### 厳守ルール

- ✅ **地は白のみ**（数字パターンの下に水色ベタを敷かない／パターン自体が地色を作る）
- ✅ **SVG は改変せずそのまま敷く**（手書きで span を散らさない）
- ✅ 不透明度は **0.05〜0.16** 目安（SVG 内で既に調整済）
- ❌ 文字・図表に数字を掛けない（可読性最優先）
- ❌ 「5」だけのパターンを手書きで作らない（公式 SVG は多彩セリフ書体で 0〜9 を散らし生成）

---

## 5. レイアウトの 12 型（5co-slide-template 由来）

| 記号 | 型 | 主クラス | 用途 |
|---|---|---|---|
| A | 表紙 | `slide cover-card` | タイトル・対象者・アジェンダ |
| B | 章扉 | `slide numbg-cover reverse section-divider` | セクション区切り |
| C | リード＋KPI | `slide numbg-content` ＋ `kpi-grid` | 主張＋数値 4 枚 |
| D | 表 | `slide numbg-content` ＋ `table`（`tr.me` で強調） | 一覧・構造 |
| E | 比較 2 カラム | `compare` ＋ `card`/`card navy` | 現在 vs 目指す姿 |
| F | タイムライン | `tl`（3 カラム） | ロードマップ |
| G | キーメッセージ | `keymsg` | 一文を大きく |
| H | 組織図 | `org-compare` | 体制ビフォー/アフター |
| I | 対話・傾聴 | `listen-tag` ＋ `memo` | 問い＋その場メモ |
| J | 数値ハイライト | `keymsg`＋大数字 | 記憶に残す数字 |
| K | 名刺見せ | `meishi`（または `<img>`） | 昇格時の名刺 |
| L | クロージング | `slide reverse center` | 裏表紙・締め |

正データ：`slide/5co_slide_template.html`（A4 横・印刷で PDF）

---

## 6. 表紙レイアウトの黄金比（名刺 front 準拠）

```
┌─────────────────────────┬──────────────────────────────────────┐
│                          │                                       │
│   numfield_cover_left    │   eyebrow (kicker)                    │
│      (左ゾーン)          │   ─                                   │
│                          │                                       │
│       [ Logo ]           │   タイトル（メイン）                  │
│   Strategy, refined.     │                                       │
│                          │   サブタイトル                        │
│   (タグラインは SVG      │                                       │
│    ロックアップ内に内包) │   提案者・日付                        │
│                          │                                       │
│   118mm（40%）          │   約 179mm（60%）                     │
└─────────────────────────┴──────────────────────────────────────┘
                              A4 横 297mm × 210mm
```

### 寸法ルール

| ゾーン | 幅 | 内容 | 背景 |
|---|---|---|---|
| 左ゾーン | 118mm（40%）| ロゴ＋数字パターン | numfield_cover_left.svg + 白 |
| 右ゾーン | 179mm（60%）| タイトル・提案者 | 白のみ |

### CSS（コピペで使える最小実装）

```css
.slide.cover{
  background: var(--white);
  display: grid;
  grid-template-columns: 118mm 1fr;
  padding: 0;
}
.cover-left{
  background: url("numfield_cover_left.svg") center/cover no-repeat, var(--white);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 18mm 10mm;
}
.cover-left .logo-mark{ width: 64mm; color: var(--navy); }
.cover-right{
  padding: 22mm 18mm 18mm; background: var(--white);
  display: flex; flex-direction: column; justify-content: center;
}
```

---

## 7. 文字・図表のサイズ（A4 横スライド向け）

| 要素 | サイズ | 用途 |
|---|---|---|
| h1 表紙メイン | 2.4〜2.8rem | 短い見出し（〜20 文字推奨） |
| h2 章タイトル | 2rem | 章扉・章別表紙 |
| h3 セクション | 1.35rem | 各セクション見出し |
| lead | 1.15〜1.3rem | サブタイトル・リード文 |
| body | 1rem | 本文 |
| kicker | 0.8rem | 章番号・タグ |
| tagline | 1.05rem italic | "Strategy, refined." 等 |

`html { font-size: 19px; }` を基準に投影向けスケール。

---

## 8. NG パターン集（よくある CI 違反）

| NG | 理由 | 対処 |
|---|---|---|
| ❌ 数字パターンを「5」だけの手書き spans で再現 | 公式 SVG は 0〜9 多書体で生成済 | 公式 SVG を `center/cover` で敷く |
| ❌ 数字パターン背景下に水色ベタを敷く | パターン自体が地色 | 地は白のみ |
| ❌ 表紙ロゴを 100mm 超で巨大配置 | ブランドの落ち着き喪失 | 54〜64mm 推奨 |
| ❌ タグラインを SVG 外で別配置 | ロックアップ分離 | SVG ロックアップに内包させる |
| ❌ グレー・黒で文字を書く | 3 色ルール違反 | Navy + 透明度で階層化 |
| ❌ サンセリフで本文を組む | ブランドの統一感破壊 | 明朝で統一 |
| ❌ KPI 数字を緑・赤・橙で色付け | 3 色ルール違反 | Navy 強調 or Navy 反転カードで |
| ❌ 数字を文字や図表に掛ける | 可読性低下 | 数字パターンは余白/カードの隙間にのみ |

---

## 9. 自己検証チェックリスト（出力前に必ず実施）

```bash
# Chrome headless で PNG レンダリング
chrome --headless --disable-gpu --window-size=1400,990 \
  --screenshot=/tmp/check.png "file:///path/to/slide.html"
# 結果を目視確認
```

### 目視チェック項目

- [ ] 3 色以外を使っていないか
- [ ] ロゴが大きすぎないか（A4 横の 30% 以内）
- [ ] タグラインが二重表示されていないか
- [ ] 数字パターンの下に水色ベタを敷いていないか
- [ ] 数字が文字・図表に掛かっていないか
- [ ] 公式 SVG をそのまま敷いているか（手書き spans で代替していないか）
- [ ] 明朝統一されているか（サンセリフ混入なし）

---

## 10. 関連ファイル

- `5co-CI-kit/CI_KICKOFF.md` — CI 立ち上げ時の意思決定経緯
- `5co-CI-kit/NUMFIELD_HANDOFF.md` — 数字パターン詳細
- `5co-CI-kit/LOGO_HANDOFF.md` — ロゴ運用詳細
- `5co-CI-kit/SLIDE_TEMPLATE_HANDOFF.md` — スライド 12 型
- `5co-CI-kit/名刺デザイン_社内共有.md` — 名刺デザイン経緯
- `slide/5co_slide_template.html` — スライド正データ
- `slide/assets/numfield_*.svg` — 数字パターン SVG
- `slide/assets/5co_logo_lockup_currentColor.svg` — ロゴロックアップ
- `meishi/cards/<社員名>/` — 完成名刺サンプル

---

## 11. 更新履歴

- **2026-06-10** 初版作成。名刺リニューアル後の CI 統一ルールを集約。
- 旧ルール「コーポレートカラー Luminous Sky #6CC5DC／ロゴ非彩色」は本 2 色刷り CI で **無効化**。

---

## 12. プラグイン展開

本ガイドラインは **`5co-brand-kit`** プラグインとして配布する。

- `~/dev/5co-brand-kit/` がソース
- 5co-slide-tools マーケットプレイスに追加し、`/plugin install 5co-brand-kit@5co-slide-tools` で導入
- 詳細は `~/dev/5co-brand-kit/README.md` 参照
