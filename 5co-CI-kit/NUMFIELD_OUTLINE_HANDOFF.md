# Oracle（numfield）アウトライン化 手順書（表紙が非Mac/PDFで消える件の恒久対策・B案）

## 何が問題か
表紙 `cover-full` の Oracle（数字背景）は `numfield_*.svg` を使うが、これらは数字を
`<text font-family='Didot'…>` 等の**ライブテキスト＋Mac専有フォント**（Didot / Bodoni 72 /
Hoefler Text / Big Caslon / Cochin / Palatino / Baskerville / Times New Roman / Georgia の9種混在）で
描いている。これらのフォントが無い環境（プレビュー sandbox・非Mac・一部 PDF）ではグリフが描画されず
Oracle が消える。テンプレ `5co_slide_template.html` の `.numfield-full` 背景は
`numfield_allover_nuki.svg` を base64 dataURI で2箇所に埋め込んでいる（中身は同一・確認済み）。

## 方針（B案＝完全忠実・作り直し禁止）
**実フォントが入っている Mac 上で `<text>` を同じ書体のまま `<path>` 化**する。位置・サイズ・回転・
数字・塗りは一切変えない＝見た目は不変、かつフォント非依存になりどの環境でも同一描画になる。

アウトライン化の手段は2つ。**推奨は Illustrator**（実フォントで確実）。

---

## 推奨フロー：Illustrator で OL → スクリプトで再埋め込み

### 1. Illustrator でアウトライン化（OL）
各 `5co-CI-kit/assets/numfield_*.svg`（最低 `numfield_allover_nuki.svg`、可能なら6種全部）について:

1. SVG を開く。**「環境にないフォント」警告が出ないこと**を確認（出たら欠落書体を Font Book で有効化）。
   - ⚠️ 欠落フォントがあると OL が代替字形を焼き込む＝作り直しになる。**書式 → フォントの検索と置換**で欠落ゼロを確認。
2. `Cmd + A`（全選択）→ **書式 → アウトラインを作成**（`Cmd + Shift + O`）。
3. **SVG で上書き保存**。書き出し時の注意:
   - 文字（`<text>`）が消え `<path>` になっていること。
   - **viewBox `0 0 1920 1080` を維持**。
   - スタイル：プレゼンテーション属性、小数点精度 2〜3。
   - 白抜き（nuki）は白のまま（クリスタル地に白で出る。アートボード白だと画面では見えないがデータは正）。

### 2. テンプレ dataURI を OL 版で再埋め込み
OL ファイルを `_ol` 別名で書き出した場合（例 `numfield_allover_nuki_ol.svg`）は `--src` で直接指定:
```bash
cd <リポ または 5co-CI-kit を含む作業フォルダ>
python3 5co-CI-kit/numfield_outline.py --reembed --src numfield_allover_nuki_ol.svg
```
原本名で上書き保存した場合は `--src` 不要:
```bash
python3 5co-CI-kit/numfield_outline.py --reembed
```
- 指定 SVG（OL済み）を生バイトのまま base64 化し、テンプレの `.numfield-full` dataURI 2箇所を差し替える。
- `<text>` が残っていれば中断する（OL 漏れ検出）。
- 仕上げに原本名へ反映：`numfield_allover_nuki_ol.svg` を canonical 名 `numfield_allover_nuki.svg` に
  リネーム/上書きしてコミットする（テンプレ・スクリプトは原本名を参照するため）。

### 3. 表示確認（実証）
- `5co_slide_template.html` の cover-full を表示、または cover デッキを1枚生成し、**Oracle が出る**ことを確認。
- 非Mac環境（ヘッドレス Chromium 等）でも出れば成功（フォント非依存になった証拠）。

### 4. canonical へ反映
- 正本は `5co-hub/template:5co-CI-kit`。OL済み `numfield_*.svg` ＋ 更新後 `5co_slide_template.html` を
  template リポにコミットしてPR → 33派生リポへ同期。
- ⚠️ Drive 作業フォルダ（AI-Objective-MGMT 等）で作業した場合は、結果を template クローンへコピーしてからコミット。

---

## 代替フロー：スクリプト単体でアウトライン化（Illustrator 無しの Mac）
実フォントが OS に入っていればスクリプトだけでも可（fonttools が実フォントから字形を取得）。
```bash
pip3 install fonttools
python3 5co-CI-kit/numfield_outline.py --report          # 9書体すべて OK か点検
python3 5co-CI-kit/numfield_outline.py --apply --verify  # 6種を path化＋テンプレ再埋め込み＋<text>残存ゼロ検査
```
- `--report` で ❌ が出る書体があれば、その Mac に未インストール。Font Book で入れてから再実行。
- どうしても無い書体のみ代替したい時だけ `--fallback "Times New Roman"`（その path に `data-fallback-from`
  が付き、後から判別できる）。**既定はフォールバックせず中断**（作り直し防止）。

---

## 検証メモ（テンプレ環境で実施済み）
- `--report` ロジック・`convert_svg`（`<text>`→`<path>`、位置/回転/サイズ保持）・`--reembed`（2箇所差し替え）の
  機構を、代替フォント（DejaVu/Liberation）でヘッドレス Chromium 描画まで通して動作確認済み。
- フォント忠実度のみ実フォントのある Mac でしか出ないため、最終の実書体 OL は本手順で Mac 実行が必須。
