#!/usr/bin/env bash
# ci-canonical-sync.sh — 5co CI 正本テンプレ（5co-CI-kit）を「一箇所の正」から取得し、
# 作業環境のドリフトを検知する。SessionStart で実行する想定。
#
# 設計（docs/ci-canonical-bootstrap.md）:
#   - 正本 = git リポ 5co-hub/template の 5co-CI-kit/（唯一の正）。
#   - 各作業環境はテンプレを自前保持せず、毎セッション正本を固定パスへ取得する
#     （コピーを持たせない＝ドリフトを構造的に防ぐ）。
#   - 認証 = fine-grained read-only PAT（op の専用アイテム）。社員個別の GitHub
#     アカウントは不要。広い `GitHub PAT (Template)` は使わない（最小権限）。
#   - 秘密はリポに置かず op からのみ取得。PAT 欠落時はセッションを止めず警告する。
#
# 出力（stdout）は SessionStart の additionalContext として注入される。
set -uo pipefail

# ---- 設定（env で上書き可） ---------------------------------------------------
VAULT="${CI_CANON_VAULT:-claude-code-secrets}"
PAT_ITEM="${CI_CANON_PAT_ITEM:-GitHub PAT (CI canonical read)}"   # fine-grained read-only PAT
CANON_REPO="${CI_CANON_REPO:-5co-hub/template}"
CANON_SUBDIR="${CI_CANON_SUBDIR:-5co-CI-kit}"
CANON_BRANCH="${CI_CANON_BRANCH:-main}"
CACHE_DIR="${CI_CANON_CACHE:-$HOME/.cache/5co-CI-canonical}"
# 作業環境内のローカル CI-kit（ドリフト照合の対象）。未指定なら CWD 直下を見る。
LOCAL_KIT="${CI_CANON_LOCAL_KIT:-$PWD/$CANON_SUBDIR}"

emit() { printf '%s\n' "$*"; }   # additionalContext へ

emit "=== 5co CI 正本（single source of truth） ==="
emit "正本: ${CANON_REPO} :: ${CANON_SUBDIR}（branch=${CANON_BRANCH}）／ローカルにフォーク・改変しない"

# ---- op / SA トークンの存在確認 ----------------------------------------------
if ! command -v op >/dev/null 2>&1; then
  emit "⚠️ op CLI 不在。正本同期スキップ。setup-op.sh の実行を確認。"
  exit 0
fi
if [ -z "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  emit "⚠️ OP_SERVICE_ACCOUNT_TOKEN 未設定。正本同期スキップ（端末ローカルに SA トークンを設定）。"
  exit 0
fi

# ---- fine-grained read-only PAT を op から取得（リポには置かない） ------------
# 括弧入り title のため op item get を使用（op read の op:// は括弧 NG）。
# TLS クロックスキュー保険で軽リトライ。credential ラベルが複数ある履歴に備え jq 走査。
get_pat() {
  local v=""
  v="$(op item get "$PAT_ITEM" --vault "$VAULT" --format=json --reveal 2>/dev/null \
        | jq -r '.fields[] | select((.label=="credential" or .label=="認証情報") and (.value // "")!="") | .value' 2>/dev/null \
        | head -n1)"
  [ -z "$v" ] && v="$(op item get "$PAT_ITEM" --vault "$VAULT" --fields credential --reveal 2>/dev/null)"
  printf '%s' "$v"
}
PAT=""
for attempt in 1 2 3; do
  PAT="$(get_pat)"
  [ -n "$PAT" ] && break
  sleep "$attempt"
done
if [ -z "$PAT" ]; then
  emit "⚠️ 正本同期スキップ: op に '$PAT_ITEM' が見つからない/空。"
  emit "   → GitHub で fine-grained・read-only（Contents: Read / 対象 ${CANON_REPO}）の PAT を発行し、"
  emit "     1Password vault '$VAULT' の item '$PAT_ITEM'（field credential）に投入してください。"
  exit 0
fi

# ---- 正本を固定パスへ取得/更新（shallow・sparse=5co-CI-kit のみ） -------------
AUTH_URL="https://x-access-token:${PAT}@github.com/${CANON_REPO}.git"
sync_ok=0
if [ -d "$CACHE_DIR/.git" ]; then
  git -C "$CACHE_DIR" remote set-url origin "$AUTH_URL" >/dev/null 2>&1
  if git -C "$CACHE_DIR" fetch --depth=1 origin "$CANON_BRANCH" >/dev/null 2>&1 \
     && git -C "$CACHE_DIR" checkout -q -B "$CANON_BRANCH" FETCH_HEAD >/dev/null 2>&1; then
    sync_ok=1
  fi
else
  rm -rf "$CACHE_DIR"
  if git clone --depth=1 --filter=blob:none --sparse --branch "$CANON_BRANCH" \
       "$AUTH_URL" "$CACHE_DIR" >/dev/null 2>&1 \
     && git -C "$CACHE_DIR" sparse-checkout set "$CANON_SUBDIR" >/dev/null 2>&1; then
    sync_ok=1
  fi
fi
# 認証情報を remote URL に残さない
[ -d "$CACHE_DIR/.git" ] && git -C "$CACHE_DIR" remote set-url origin "https://github.com/${CANON_REPO}.git" >/dev/null 2>&1

CANON_KIT="$CACHE_DIR/$CANON_SUBDIR"
if [ "$sync_ok" != 1 ] || [ ! -d "$CANON_KIT" ]; then
  emit "⚠️ 正本の取得に失敗（ネットワーク/PAT 権限/ブランチを確認）。前回キャッシュがあればそれを使用。"
  [ -d "$CANON_KIT" ] || exit 0
fi
emit "正本テンプレ取得: $CANON_KIT"

# ---- ドリフト照合（正本 vs 作業環境ローカル CI-kit のハッシュ） --------------
dir_hash() { # 再帰ハッシュ（パス＋内容）。.git は除外。
  ( cd "$1" 2>/dev/null && find . -type f -not -path './.git/*' -print0 \
      | sort -z | xargs -0 sha256sum 2>/dev/null | sha256sum | awk '{print $1}' )
}
CANON_HASH="$(dir_hash "$CANON_KIT")"
emit "正本ハッシュ: ${CANON_HASH:0:12}"
if [ -d "$LOCAL_KIT" ] && [ "$LOCAL_KIT" != "$CANON_KIT" ]; then
  LOCAL_HASH="$(dir_hash "$LOCAL_KIT")"
  if [ -n "$LOCAL_HASH" ] && [ "$LOCAL_HASH" != "$CANON_HASH" ]; then
    emit "⚠️ ドリフト検知: ローカル $LOCAL_KIT が正本と不一致（local=${LOCAL_HASH:0:12}）。"
    emit "   → 制作は正本（${CANON_KIT}）を使うこと。ローカルコピーを正本に更新（または削除）推奨。"
  else
    emit "ドリフトなし: ローカル CI-kit は正本と一致。"
  fi
fi

# ---- CI ルールの注入（決定論パスの再掲） --------------------------------------
KICKOFF="$CANON_KIT/CI_KICKOFF.md"
if [ -f "$KICKOFF" ]; then
  emit "CI ルール: $KICKOFF を必読。スライド制作は正本テンプレを複製し文言だけ差替え（0からCSSを書かない）。編集後 slide_overflow_check.py で検査・3色厳守。"
fi
exit 0
