# テンプレート全体のバージョン管理

> 正データ = リポ直下の `template-manifest.json`。本ドキュメントは運用ルール。
> 設計は Codex sol（gpt-5.6-sol）の独立検証を経て 2026-07-15 に確定（decisions.md 参照）。

## 目的

「このセッションの環境に subagent-orchestration は導入済みか？」等を、ファイル有無を
個別に探さず**1ファイルで即答**できるようにする。git 派生リポ・非 git のローカル展開先
（Drive 等）の両方で機能する。

## 3つの概念を混同しない（設計の核）

| 概念 | 担うもの | 答えられる問い |
|---|---|---|
| リリース版 | `template-manifest.json` の `template_version`（CalVer） | どの版由来か・何が入っている版か |
| 適用元 revision | マーカーの `source_revision`（full SHA） | 正確にどのコミットか |
| 現在の整合性 | マーカーの `files`/`managed_content_digest` ＋ `--verify` | 今も内容が一致しているか |

版マーカーは「過去に何を適用したか」しか示さない。手動改変の検知は digest 照合
（`--verify`）でしかできない。SessionStart 表示も「適用済み」と「整合性確認済み」を
区別する（既定は `integrity: not checked`）。

## 構成要素

1. **`template-manifest.json`**（正本・このリポ直下、派生にも配布される）
   - `template_version`: CalVer 形式 `YYYY.MM.N`（例 `2026.07.1`）
   - `capabilities`: 主要機能の構造化一覧（`introduced_in` / `status` / `entrypoint` / `requires`）
2. **`.claude/.template-state.json`**（展開先マーカー・`apply-template.sh` が自動生成）
   - 版番号・`released_at`・full `source_revision`・`target`・管理対象ファイル別 sha256（`files`）・
     全体 `managed_content_digest`
   - **決定的な値のみ**（適用日時は入れない）。同じ版・同じ digest なら書き換えない
     → 実質差分ゼロの週次 sync で空 PR が立たない・Drive の mtime も動かない
   - **`source_revision` の定義 = 「管理対象の内容が最後に変化した時点の適用元コミット」**。
     内容不変のコミット（active-context 更新等）では書き換えない＝毎コミットで SHA を追従させると
     全派生リポに毎週マーカーだけの sync PR が立つため（sol 検品 P2-1 の裁定）。
     dirty な template から手動適用した場合は `<sha>-dirty` と記録し provenance を偽らない
   - 更新境界は **CLAUDE.md ディレクトリ単位**：そのディレクトリの全コピー成功後にのみ
     atomic rename で更新（`set -e` により途中失敗時は以降のマーカーも書かれない）。
     欠落ファイルが残る状態ではマーカーを書かない（fail-closed）
3. **`apply-template.sh --verify`**（非破壊の整合性検査・fail-closed）
   - マーカーは**信頼しない入力**として扱う：schema・hash 形式（64hex）・パス境界
     （絶対パス・`..`・symlink 拒否）・`managed_content_digest` の再計算照合を通ってから
     `files` と実ファイルを照合 → `verified` / `drifted`（modified・missing を列挙）
   - 空の `files`・形式不正・digest 不一致は「マーカー不正」として fail（verified にしない）。
     検査対象 0 件（CLAUDE.md なし）も fail
   - `target` も検証・表示する: `--target` を明示して verify した場合、マーカーの `target` と
     不一致なら fail（drive 展開＝git 依存品なしが正、を github 展開の verified と誤読させない）。
     未指定時はマーカーの `target` に従い、結果に表示する
   - template 最新版との版差も表示。問題があれば exit 1
   - **残存リスク**: マーカーに署名は無いため、digest まで整合的に再計算した「丸ごと偽造」は
     検出できない（改変防止でなく事故・部分改変・破損の検出が目的。偽造耐性が必要になったら
     署名の導入を別途検討）
4. **SessionStart 注入**（`.claude/scripts/session-context.sh` ⑪ブロック）
   - `テンプレ版: 2026.07.1（source: 0123456789ab・integrity: not checked）` を毎セッション表示
   - `.claude/.sync-disabled`（sync opt-out）があればその旨を明示
   - マーカーが無い展開先は「バージョン管理導入前（legacy）」扱い。**版をファイル有無から推定しない**
5. **CI ガード**（`.github/workflows/template-version-guard.yml`）
   - managed files（配布対象）を変更する PR で `template_version` が bump されていなければ fail
   - managed 一覧は **BASE と HEAD の和集合**で判定（配布対象から外しつつ変更する PR の
     すり抜けを防ぐ）。配布エンジン `apply-template.sh` と本ガード自体も無条件 managed
   - manifest の形式（JSON / CalVer 実在値 / capability 構造 = introduced_in・status・
     entrypoint 実在・requires 型）と版の単調増加も検証
   - `tests/template-versioning.test.sh`（統合テスト: マーカー生成・冪等性・fail-closed verify・
     drive 除外）と `tests/sync-ops.test.sh`（sync 運用: 許可パス検査・local-sync fail-closed）を毎 PR 実行
   - 補足: ガード workflow・managed 定義への変更に管理者レビューを必須化する branch rule /
     CODEOWNERS はリポ設定側の作業（管理者・任意）

## 採番ルール（CalVer）

- 形式: `YYYY.MM.N`（N = その月の通し番号、1 始まり）
- **PR 単位で 1 回** bump する（コミットごとではない）。managed files を変更する PR は bump 必須（CI が強制）
- semver にしない理由: テンプレは API と違い互換性境界が曖昧で、「いつ頃の運用標準か」の方が重要
- ロールバックも**新しい版として旧内容を再リリース**する（版番号を過去に戻さない）
- 破壊的変更は版番号でなく PR/リリースノートで `BREAKING` を明示する

## capability に載せる基準

**載せる**: 利用者が「この環境で使えるか」を判断する必要があり、複数ファイルにまたがって
ファイル有無だけでは判定しづらく、安定した一意 ID（kebab-case）を付けられる機能。

**載せない**: 誤字修正・内部リファクタ・個別ドキュメント追加・実装詳細・一時的な試験ファイル。

`entrypoint` は**配布されるファイル**を指すこと（派生側で存在確認できるように）。
認証情報等の前提は `requires` に明示する（「配布されている」≠「利用可能」）。
廃止時は削除せず `status: deprecated` → 次版で `removed_in` を記録。

## 使い方

```bash
# 整合性検査（非破壊）: マーカーと実ファイルの照合＋最新版との版差表示
bash scripts/apply-template.sh <対象ルート> --verify

# 通常の適用・修復（マーカーは自動更新される）
bash scripts/apply-template.sh <対象ルート> --repair
```

セッション内で「◯◯は導入済みか？」→ SessionStart 注入の `Template Version` ブロック
（版番号）と `template-manifest.json` の capabilities（版ごとの内容）を突き合わせる。

## エッジケースの扱い

- **sync PR が放置された派生リポ**: default branch のマーカーは旧版のまま＝正しい動作。
  「PR 起票済み」を「適用済み」と数えない
- **opt-out リポ（`.claude/.sync-disabled`）**: 最終適用版マーカーは残る。SessionStart が
  `sync: disabled` を明示し、最新版とは限らないことを伝える
- **マーカーの無い古い展開先**: `unknown / legacy` と扱い、ファイル有無から版を逆算しない。
  `--repair` 1回でマーカーが導入される
- **--target=drive**: git 依存ファイルと `.claude/settings.json`（死んだフック掃除で内容が
  変わる）は digest 対象外
- **ROOT_FILES**（`docs/subagent-orchestration.md` 等、対象ルート直下に置く共通ドキュメント）:
  マーカーは CLAUDE.md ディレクトリ単位のため digest 対象外（配布はされる）

## sync 配布との連動（2026-07-16・sol 提案採用）

- **配布トリガー = `template-manifest.json` の変更**（`sync-template.yml` の push paths）。
  managed 変更は bump 必須＝manifest が配布イベントとして機能する。取りこぼしは週次 cron が回収
- **一括マージ（`ci-merge-sync-prs.sh`）の安全条件**: branch 名だけを信頼せず、
  ①非 draft の open PR ②base=default branch ③CI 非失敗 ④変更パスが `--print-synced`
  （managed＋scaffold＋版マーカー）の範囲内 ⑤検査時点の head SHA 指定マージ、を全て要求。
  **保護ルール迂回（--admin）は廃止**
- **local-sync（非 git 展開先）**: dirty / main 以外の template からは配布しない（fail-closed）。
  検証目的の明示実行は `ALLOW_DIRTY_TEMPLATE=1`。同時実行はロックでスキップ
- **保全保証（sync はコピー型・ミラー型ではない）**: apply/sync が書く・消すのは
  `--print-synced` に列挙されたパスのみ。**派生リポの CLAUDE.md はどの配布リストにも
  含まれず、sync は一切触れない**（検出マーカーとして参照するだけ）。`.claude/skills/` も
  ディレクトリ丸ごとではなく個別ファイル列挙＝独自スキル（例 `jp-*`）は managed と同名で
  ない限り削除・上書きされない（drive の strip も固定3ファイルのみ）。この保証は
  `tests/sync-ops.test.sh` §5 で CI 固定。注意: `.claude/settings.json` は managed＝上書き
  されるため、派生側のローカル差分は `settings.local.json` へ

## 派生リポ側セッションの心得（このファイルは全派生リポに自動配布される）

テンプレ配布の挙動（「sync で消える？上書きされる？」等）に疑問が出たら：

1. **まず本ドキュメントを読む**（あなたのリポ内に配布済み＝これが正）。特に上の
   「保全保証」節——CLAUDE.md と独自スキルは sync に触られない。`.claude/settings.json`
   のローカル差分だけ `settings.local.json` へ
2. **書いていない仕様疑問は推測で埋めない**。子リポ側でのガード実装・CLAUDE.local.md
   分割・独自ディレクトリ移設などの防衛策を先に作らない（＝ドリフト。CLAUDE.md の
   フォーマット改変禁止と同じ理由）。正本 `5co-hub/template` に issue を立てるか、
   管理者経由で正本側セッションに照会する
3. 独自スキルを作るときは managed と同名を避ける（一覧 = 正本の
   `apply-template.sh --print-synced`。同名にすると sync が上書きする）

## 見送り（将来の拡張候補・2026-07-15 裁定）

- 配布を main push 単位 → release/tag 単位に変更（sol 提案。運用影響が大きく別 PR で判断）
- 中央インベントリ（全派生リポの current/pending/latest 一覧レポート）
- opt-out リポでの `latest` 表示（ネットワーク参照が必要なため、ローカル情報のみに留めた）
