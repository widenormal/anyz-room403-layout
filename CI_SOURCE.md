# CI 正本ソース（最初に読む）

> このファイルは「5co CI テンプレの唯一の正（single source of truth）の場所」を宣言する。
> 各作業環境（クライアント別の共有フォルダ等）はこれを最初に読み、**正本を読みに行く**。
> 目的: 全社員がどの環境からでも**完全に同一のテンプレ**で制作し、ドリフトを防ぐ。

## 正本の場所（ここだけが正）

- リポ: **`5co-hub/template`** の **`5co-CI-kit/`**（branch `main`）。
- 取得物: `5co_slide_template.html`・`ci-theme.css`・`CI_KICKOFF.md`・`SLIDE_DESIGN_GUIDELINES.md`・`slide_overflow_check.py`・`assets/` 等。

## 鉄則

- **フォーク・ローカル改変をしない。** テンプレを各フォルダにコピーして持ち回らない（コピーは必ずドリフトする）。
- 制作のたびに **正本を取得して使う**。SessionStart の `scripts/ci-canonical-sync.sh` が
  正本を固定パス（既定 `~/.cache/5co-CI-canonical/5co-CI-kit`）へ取得し、ローカルとの**ドリフトを照合・警告**する。
- スライド制作は **`CI_KICKOFF.md` を必読**。正本テンプレを複製し**文言だけ差替え**（0から CSS を書かない）。
  編集後は `slide_overflow_check.py` ではみ出し検査・**3色厳守**・隅ロゴ 64px。

## 取得の仕組み（社員 GitHub アカウント不要）

- 認証は **fine-grained read-only PAT**（GitHub・Contents: Read・対象 `5co-hub/template`）を
  **1Password に1つ**保管し、`scripts/ci-canonical-sync.sh` が `op` 経由で取得して `git` で正本を pull。
- 社員端末に必要なのは **`OP_SERVICE_ACCOUNT_TOKEN`（sa-common）だけ**。GitHub ログインは不要。
- **PAT・SA トークンは端末ローカルに置く**（共有フォルダには置かない＝「機密の置き場＝誰が触れるか」）。

詳細設計: `docs/ci-canonical-bootstrap.md`
