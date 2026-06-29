# SLIDE-PATTERN → CI v2 アダプタ寸法仕様

> 99 種の `docs/SLIDE-PATTERN/`（16:9・グレースケール・sans-serif）を **CI v2（A4横・3色・φ）** へ
> 変換するための唯一の寸法正。出典：`5co-CI-kit/SLIDE_DESIGN_GUIDELINES.md §3/§4` ＋
> `docs/SLIDE-md/SLIDE-md-5co/SLIDE.md §Layout` ＋ リポ実装 `5co-CI-kit/ci-theme.css`。

## 0. 換算基準
- **1mm = 96/25.4 = 3.7795 px**（@96dpi）／ 1px = 0.2646mm。φ = 1.618、1−1/φ = 0.382。

## 1. キャンバス
| | パターン側 | CI v2（採用） | px@96dpi |
|---|---|---|---|
| 寸法 | 960×540px | **297×210mm（A4横）** | 1122.5×793.7px |
| アスペクト比 | 1.778（16:9） | **1.414（√2）** | 非相似＝単純スケール不可 |

## 2. グリッド寸法表（§4 px@1280 ↔ SLIDE.md mm ↔ 採用）
| 項目 | §4 (px@1280) | SLIDE.md/repo (mm) | 採用（アダプタ正） | 備考 |
|---|---|---|---|---|
| 外余白 上 | 104px(×φ)=27.5mm | 16mm | **16mm** | ⚠️§4「上だけ広い」は不採用（実装16mm） |
| 外余白 左右 | 64px=16.9mm | 18mm | **18mm** | |
| 外余白 下 | 64px=16.9mm | 14mm | **14mm** | |
| 内容幅 (W−左右) | — | 261mm | **261mm（986.5px）** | =297−18−18 |
| 内容高 (H−上下) | — | 180mm | **180mm（680.3px）** | =210−16−14 |
| ベースライン u | 29px | — | **29px** | 絶対px・行送り/間隔は u の整数/半整数倍 |
| 黄金分割線 (W−W/φ) | 489px@1280 | 全幅×0.382 | **全幅113.4mm / 内容99.7mm** | 左シンボル/右コンテンツ |
| φ note/body/md/lg/xl | 11/18/29/47/76px | 同左 | **11/18/29/47/76px** | line-height 1.618 |

## 3. 配色マッピング（グレー → 3色トークン）
| パターンのグレー | 役割 | CI v2 トークン |
|---|---|---|
| #FFFFFF | 地 | `--white #FFFFFF` |
| 明グレー面（#E8E8E8/#F0F0F0系） | 薄い面・帯 | `--crystal-25 #F0F5FB` / `--crystal-55 #DEE9F6` |
| 中グレー面（#CCC/#E0E0E0） | アクセント面・チップ | `--crystal #C3D7EE` |
| 濃グレー文字（#333/#555） | 本文・見出し | `--ink #101820` |
| 中グレー文字（#666/#999） | 補足・キャプション | `--ink-60` |
| 罫線（#CCC 等） | 罫線 | `--ink-14` |
| 反転（濃地に白） | dark面 | `.slide.dark`（地=ink・字=crystal） |
- データ系列は `5co-CI-kit/ci-charts.css`（`--data-1..4` モノブルー階調・増減のみ `--pos/--neg`）。
- グラデーションを含むパターン（カタログ中1件）は個別に単色 or ティントへ。

## 4. タイポ
- sans-serif → 和文 `Hiragino Mincho ProN`／欧文 `EB Garamond`（`ci-theme.css` の `--serif-ja/--serif-en`）。
- サイズは φ スケールへ丸める（最寄りの note/body/md/lg/xl）。line-height 1.618。
- 数字は lining + tabular（`font-variant-numeric: lining-nums tabular-nums`）。

## 5. アスペクト変換則（幅合わせ＋什器帯）
非等方のため `transform:scale` 一発は不可。幾何的に綺麗に収まる手順：
1. パターンの**内側 `.slide` を抽出**（`body{#E8E8E8}`＋`.slide-label` のプレビュー外装は捨てる）。
2. **内容ボックス 261×180mm** に配置。図本体は**内容幅 261mm に幅合わせ** → 高さ 261×9/16 = **146.8mm**。
3. 余り **180−146.8 = 33.2mm** を**上下の CI 什器帯**へ（numfield ヘッダー／フッター・5co ロックアップ）。
4. 2カラム系は分割線を **黄金分割（内容99.7mm）** に合わせる。
5. グレー→3色・sans→φ を適用 → **`5co-CI-kit/slide_overflow_check.py`**（A4・はみ出し・隅ロゴ64px・3色）。

## 6. 什器（CI 標準装備）
- 隅ロゴ（5co ロックアップ）右上 **64px**（`SLIDE_DESIGN_GUIDELINES §5`）。
- フッター：Garamond 11px・字間.04em（CONFIDENTIAL は.16em）・色 ink-60／dark面は crystal65%・下端14px/左右36px。
- 数字背景（Oracle/numfield）は表紙・章扉に任意。文字・図表には掛けない。

## 7. 実装と検証状況

- **実装**: `scripts/ci_pattern_adapter.py`（配色マッピング＋フォント置換＋A4ページ化＋幅合わせscale＋什器注入）。
- **99種 一括変換＋3色QA合格（pass=99 / fail=0）**: `scripts/adapt_all_patterns.sh` で全件を CI v2 化し、
  3色（白/crystal/ink/tint）以外の hex 残存ゼロを自動確認。emoji 数値文字参照(`&#NNNN;`)は除外判定。
- **目視検証済み（headless Chrome）**: `four-step-flow`/`goal-kgi-kpi-dashboard`/`hub-spoke-diagram`/
  `risk-matrix-2x2`/`six-card-2x3-grid` を実機レンダリングし **A4横・3色・明朝・隅ロゴ・什器帯**で成立。

### 解決済み（本実装）
- **グレー自動畳み込み**: enumerate を廃し、`R≈G≈B`(±20) のグレーを輝度バケットで CI トークンへ変換
  （文字=ink/ink-60、面・罫線=crystal階調/ink）。未知のグレー(#c8c8c8 等)も網羅。
- **タイトル昇格**: 見出し/タイトル要素（h1-3・`[class*=title/heading]`）を **ink !important** に昇格し、
  薄グレーのプレースホルダ見出しが消える問題を解消。

### 残課題
- emoji プレースホルダ・アイコン（📈💻🔒 等）は多色のまま。実運用では**モノクロ SVG アイコンに差し替え**。
- データ系列色は暫定 crystal。最終は `ci-charts.css` の `--data-1..4`（モノブルー階調）へ。
- **生成物は非コミット**（ドリフト防止）。CI版は `adapt_all_patterns.sh` / `ci_pattern_adapter.py` で
  ソース＋アダプタから**オンデマンド再生成**する（ソース+アダプタが唯一の正）。

## 8. 未解決（要確認・別途修正）
1. **上余白**：§4=104px(×φ) と 実装16mm が不一致 → **16mm を採用確定**（§4 文言は要更新）。
2. **基準系**：§4 の px は 1280×720 基準。A4実寸(1122×794)と異なるが φ は絶対px適用で実害なし → §4 に注記。
3. **コメント修正**：`5co-CI-kit/ci-theme.css` の `/* スライド枠 16:9 */` は A4 の誤記 → 文言修正（軽微）。
