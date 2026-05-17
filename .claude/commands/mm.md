# /mm — 現ブランチを main に merge して掃除（PR 経由）

引数：`$ARGUMENTS`（オプション。`--keep` を渡すと feature ブランチを削除しない）

## 動作仕様

以下を**順に**実行する。**追加の確認質問は出さない**（`/mm` の発火自体が pre-authorization）。
ただし**実行前に「main に取り込まれるコミット一覧」を表示**してからすぐ実行する。

### 1. 前提チェック（失敗したら止めて報告）

- `git status --porcelain` が空でない場合 → 「未 commit の変更があります」で停止
- 現ブランチが `main` の場合 → 「main 上にいます。merge 不要」で停止
- `git fetch origin --quiet` 実行
- `git remote get-url origin` で remote URL を取得し、以下を判別：
  - **GitHub**（`github.com` を含む）→ **PR 経由パス**（既定・branch protection 対応）
  - **その他**（GitLab・自前 git server 等）→ **直接 push パス**（後述）

### 2. 取り込み内容を表示

```bash
git log origin/main..HEAD --oneline
```

これを実行して「main に取り込まれるコミット一覧」をユーザーに見せる。
0 件なら「現ブランチは既に main に含まれています。merge 不要」で停止。

### 3a. PR 経由パス（GitHub 既定）

#### 3a-1. 未 push のコミットがあれば push

```bash
CURRENT=$(git branch --show-current)
git push -u origin "$CURRENT"
```

リトライ 4 回・指数バックオフ（2/4/8/16 秒）。

#### 3a-2. PR 作成

`mcp__github__create_pull_request` を以下で呼ぶ：

```yaml
owner: <git remote から抽出>
repo: <git remote から抽出>
title: "<commit log の最初の 1 行 or branch 名>"
head: $CURRENT
base: main
body: |
  ## 概要
  
  $CURRENT を main にマージ。
  
  ## 取り込まれるコミット
  
  <git log origin/main..HEAD --oneline の結果を貼る>
  
  ## /mm 経由で自動作成
```

返り値の PR number を `PR_NUMBER` として記憶。

#### 3a-3. PR を merge

`mcp__github__merge_pull_request` を以下で呼ぶ：

```yaml
owner: <同>
repo: <同>
pullNumber: PR_NUMBER
merge_method: merge   # no-ff 相当
commit_title: "Merge PR #<PR_NUMBER>: <PR title>"
```

merge が拒否された場合（CI 失敗・required reviews 未達・conflict 等）：
- エラー内容を表示
- 「PR は作成済（#<PR_NUMBER>）。GitHub UI で対応してください」と報告して停止
- ローカルは触らずに終わる

#### 3a-4. ローカル main を同期

```bash
git checkout main
git pull origin main --ff-only
```

#### 3a-5. ブランチ削除（`--keep` 引数がない場合のみ）

```bash
if [ "$ARGUMENTS" != "--keep" ]; then
  git branch -d "$CURRENT"
  # remote 削除は GitHub 側の "Automatically delete head branches" 設定に委ねる
  # （branch protection で push --delete が 403 になるリポジトリ対策）
  git push origin --delete "$CURRENT" 2>/dev/null || \
    echo "ℹ️ remote branch 削除は権限不足。GitHub Settings > Pull Requests > Automatically delete head branches を ON 推奨"
fi
```

#### 3a-6. 完了報告

```
✅ PR #<PR_NUMBER> merge 完了
- branch: <CURRENT> → main
- N コミット取り込み（<from>..<to>）
- main HEAD: <短ハッシュ>
- feature ブランチ削除：local ✅ / remote <✅ or ⚠️ 設定推奨>
- 現在: main
- PR URL: <url>
```

### 3b. 直接 push パス（GitHub 以外・既存ロジック）

GitHub MCP が使えない・GitHub 以外の remote の場合は従来の直接 push 経路：

#### 3b-1. main を最新化

```bash
CURRENT=$(git branch --show-current)
git checkout main
git pull origin main --ff-only
```

`--ff-only` が失敗したら止めて報告。

#### 3b-2. no-ff merge

```bash
git merge --no-ff "$CURRENT" -m "Merge branch '$CURRENT' into main"
```

conflict が出たら：
- `git merge --abort`
- `git checkout "$CURRENT"` で元に戻る
- 「conflict 発生のため中断」と報告して停止

#### 3b-3. push

```bash
git push origin main
```

403 で reject されたら：
- ローカル main を `git reset --hard origin/main` で巻き戻す
- 元ブランチに `git checkout "$CURRENT"` で戻る
- 「main への直 push が拒否された。PR 経由が必要だが現リポは GitHub MCP 範囲外。手動で PR を作ってください」と報告

#### 3b-4. ブランチ削除（同上）

```bash
if [ "$ARGUMENTS" != "--keep" ]; then
  git branch -d "$CURRENT"
  git push origin --delete "$CURRENT" 2>/dev/null || true
fi
```

### 4. 戻り先

- `--keep` あり：元ブランチに `git checkout "$CURRENT"` で戻る
- `--keep` なし：`main` に留まる

## 想定外への対処

- **ネットワーク失敗**：push/fetch/MCP のリトライは 4 回・指数バックオフ（2/4/8/16 秒）
- **`gh` 不在**：使わない（mcp__github 経由）
- **mcp__github 不在 or scope 外**：直接 push パスにフォールバック（手動 PR 案内）
- **rebase ベースの workflow**：`/mm` は merge_method=merge（no-ff 相当）専用。rebase 派なら別コマンド `/mr` を作る
- **CI 失敗で auto-merge 不可**：PR は残して停止。ユーザーが GitHub UI で対応

## 設計メモ

- **既定で GitHub PR 経由**：branch protection が普及している現代の標準
- **直接 push パスは fallback**：GitHub 以外（GitLab self-hosted / Bitbucket）対策
- **PR 自動 merge と branch 削除を一気通貫**で実行・追加確認なし（pre-authorization）
- **PR が merge できない時はローカル無傷で停止**：destructive op を伴わない安全設計
- **GitHub の "Automatically delete head branches" 設定を ON 推奨**：remote branch delete の 403 を抜本解決
