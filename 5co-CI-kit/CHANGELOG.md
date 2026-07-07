# 5co-CI-kit CHANGELOG（スライド媒体版）

> **これは「スライド媒体」の版ログ**です。スライドの正本は本キット（template `5co-CI-kit`）。
> 全媒体共通の**ブランド版**は Drive `5co-CI/CHANGELOG.md` ＋ `BRAND_GUIDELINE.md` が正。

## バージョン管理ルール（2層・decisions.md 2026-06-29 準拠）

- **全体（ブランド）版** … `5co-CI`（Drive）が正。`tokens/`（色・タイポ・ロゴ・3色規律）に及ぶ＝
  **全媒体に影響する変更**で上げる。色相/トークン値の変更＝破壊的（全媒体を再検証）。
- **スライド媒体版（このファイル）** … スライド内だけの変更（型追加・レイアウト・検査）で上げる。
- **対応ブランド版を明記**：各スライド版は「準拠ブランド版」を併記する。
- **カスケード**：ブランド版が上がったら、本キットを新ブランド版で再検証し、必要なら版を上げる。

形式：`slide vMAJOR.MINOR（準拠 brand vX.Y）`。MAJOR＝既存デッキの作り直しを伴う非互換変更／MINOR＝後方互換の追加・修正。

---

## slide v3.3（準拠 brand v2） — 2026-07-07
- **共通HEAD＝正典CSS連結の標準方式を制定（`ci_head.py`・data-analysis 依頼 2026-07-07）**：
  案件ビルダーが正典CSSをコピー・inline再実装する運用（正典改定が届かないフォーク化＝WELLA 事故の温床）を
  禁止し、`VERSION` の format: 宣言を読んで現行CSSを連結する共有ヘルパを唯一の連結方式として提供。
  出力冒頭に版スタンプを焼き込み（ci_head 経由の機械判定マーカー）。VERSION に `head:` 規定と
  ci-charts.css を format: 宣言へ追加。規定＝`V3.2_FORMAT.md` 1.6／`SLIDE_DESIGN_GUIDELINES.md` §5.7。
  - **同時に、ci_head の E2E ゲート検証が露呈した正典CSS内のパレット外色を是正**：
    `.pdstr .c-lo` の青灰 2色（→crystal-55/ink-60）・`.pdstr .tac` の淡青灰（→crystal-25）。
    琥珀の淡地 #fdeacb は `--insight-bg` として追認（#699 の #f6b44a と同型の実装追認・機能色）。
    これで「ci_head で組んだデッキが parity 検査 OK」が成立（連結＋ゲートの二重防御が閉じる）。
- **ライトバリアント（白地 × 水色 Oracle・全型対応）を正式化**：`ci-cover-light-v3.3.css`＋
  `assets/numfield_allover_crystal55.svg`／`_crystal25.svg`。クラシエ薬品デッキ（2026-07-07）の表現を全社CIへ。
  - 使い方: **表紙**は `class="slide cover-full light"`、**本文（任意の型）**は `class="slide <型> light"` を
    付けるだけ（既存スライドは不変＝後方互換）。表紙=crystal-55（濃）・本文=crystal-25（淡）の2段階。
  - 3色規律内（Oracle tint＝crystal-55 #DEE9F6／crystal-25 #F0F5FB・地=白・文字=ink）。ブランド版変更なし。
  - 元実装（`img.nf-bg`＋opacity .5/.35）の外部 `assets/` 参照を dataURI 埋込＋焼き込みtintへ是正
    （自己完結・opacity非依存＝PDF/PPTX出力でも決定論）。旧マークアップの `img.nf-bg` は自動非表示（互換）。
  - 実機検証: 表紙・本文の描画目視（白地・水色Oracle・ink/カード可読）＋はみ出しゲート OK。
- **はみ出し検査の横方向対応（現場報告 2026-07-07・クラシエ制作中に発見された死角）**：
  `slide_overflow_check.py` に ①`scrollWidth` 検査（`+Npx(横)`） ②`overflow:hidden` で
  「あふれず隠れて切れる」table/svg/img の右端クリップ検査（`clip(TAG)`） ③幾何NG時の
  **exit 1**（gate として機能・TITLE? ヒューリスティックは表示のみ）を追加。
  `ci-finalize.sh` の検査を「警告のみ」→**NG で停止**（V3.2 規定「OK まで配布不可」を強制）。
  - 新検査が正本テンプレ自身の潜在不良（週次テンプレ7枚目 DSP 表・右端列+56px 見切れ）を
    検出 → dsp3 表を 8.5px/padding 1px に修正し解消（描画目視で右端列復元を確認）。

- **正典文書の世代整合（WELLA 世代遅れ調査 2026-07-07・docs/CI調査回答_WELLAスライド劣化_2026-07-07.md）**：
  WELLA 月次が CI_KICKOFF の旧導線（v2 週次雛形の複製）どおりに組まれ V3.1 タイポ・琥珀を取りこぼした事故を受け、
  ①CI_KICKOFF.md／SLIDE.md の入口を「VERSION 確認→現行フォーマット」へ改定 ②SLIDE_DESIGN_GUIDELINES.md に
  V3.1 タイポ（§3）を明文化・旧「明朝統一」記述と隅ロゴ 64px 表記を是正（列グループ縦罫禁止の§3.5は別途本日中に明文化済み・
  本件では table.sk の格子罫未追従を注記） ③SLIDE.md の EB Garamond 残骸を Hoefler へ統一
  ④`check-slide-ci-parity.py` に Garamond 系残存の検査を追加。週次雛形 HTML 冒頭に
  「月次・新規に使わない」警告を焼き込み。フォーマット CSS 自体は不変（文書・検査のみ）。
- **正典準拠の是正2件（NatureLab準拠規定 2026-07-07 起点）**：
  ①standalone テンプレの旧トークン名 `--powder`/`--navy` を正準 `--crystal`/`--ink` 系へ改名
  （hex不変・クラス名は後方互換で不変・parity checker 適合化） ②**洞察強調色＝琥珀 #f6b44a を正式化**
  （`--insight` 系トークンを ci-charts.css に追加。v3.2 実装 `td.chl`/`.pdstr .c-hi` の追認・
  意味にのみ使用可＝装飾禁止）。

## slide v3.2（準拠 brand v2） — 2026-07-06
- **月次 V3 デッキ形式を正本フォーマット化**：`ci-format-v3.2.css`（全24 styleブロック連結・
  表紙/扉 Oracle 埋込）＋ `V3.2_FORMAT.md`（スライド8型仕様）＋ `VERSION`（現行版宣言）を新設。
- **格納場所の一元化を明文化**：フォーマット/エンジンの唯一の格納場所＝本キット
  （`5co-hub/template:5co-CI-kit`）。全セッションは `VERSION` を確認し常に最新版で生成（CLAUDE.md に規定）。
- **欧文セリフを Hoefler Text（macOS標準）へ**（Garamond Premier Pro / Adobe Fonts 依存を解消・#642）。
  社員 Mac はフォント導入・CC アクティベート不要で忠実描画。名刺のみ Garamond 据え置き（別成果物）。
- 出力系を整備：`ci-finalize.sh`（PDF埋込＋画像PPTX＋Slides）／`slide_overflow_check.py` の全OS動作化
  （Chrome自動探索＋--no-sandbox）／`EMPLOYEE_RUNBOOK.md`（社員3ステップ・GitHub不要）。
- ※ MAJOR=3 は V3 系デッキ形式（月次28枚・anxs/blk/sof/pdstr/fnl 型）への移行を示す。v2 テンプレは残置（週次ベース雛形）。

## slide v2.2（準拠 brand v2） — 2026-06-30
- **隅ロゴ（本文右上）を 102px で確定**（V3 実デッキ準拠・実測 102×73px）。#603 の 64px は**撤回**。
  - `5co_slide_template.html` の `.corner`/`svg.corner` を 64px→102px。
  - `slide_overflow_check.py` のロゴ幅ガードを 72px→**112px** 基準へ（正準102px・102pxの誤検知防止）。
  - 視覚回帰基準 `baseline/template_signature.json` の corner を 64→102（本文12枚／表紙は null）。
  - `5co_slide_template_standalone.html` の `.corner-logo` も 102px に統一。
- ※表紙Oracle(numfield)のOL化は #617（slide media は同日反映済み）。

## slide v2.1（準拠 brand v2） — 2026-06-28
- 99種 SLIDE-PATTERN を CI v2 化するアダプタ（`ci_pattern_adapter.py`）＋一括QA（`adapt_all_patterns.sh`）。3色QA全合格。
- フレームワーク・レコメンダ（`framework_recommend.py`）標準搭載。
- 週次デッキエンジン `ci-weekly-deck` のデータ契約整合（単一DSP・エマージング_シリーズ受容）。
- アダプタ寸法仕様 `docs/SLIDE-PATTERN-CI-ADAPTER-SPEC.md`。

## slide v2.0（準拠 brand v2） — 2026-06-28
- CI v2 正本スライドテンプレ：`5co_slide_template.html`（`--crystal/--ink`・A4横297×210mm・隅ロゴ64px【→ v2.2 で 102px に改定】・φスケール）。
- 視覚回帰 `slide_visual_regression.py` ＋ `baseline/`、はみ出し検査 `slide_overflow_check.py`。
- 旧 `--powder/--navy`・16:9（1280×720）世代から A4・新トークン名へ移行。

---

## 版を上げる時の手順
1. 変更が `tokens/`（色・ロゴ・タイポ）に及ぶ → **まず `5co-CI`（Drive）のブランド版を上げ**、本キットを追従させてから slide 版を上げる。
2. スライド内のみ → 本ファイルに `slide vX.Y（準拠 brand vZ）` で1エントリ追記。
3. `slide_overflow_check.py` ＋ `slide_visual_regression.py` を通してからコミット。
