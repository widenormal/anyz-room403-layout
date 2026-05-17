# Skill: Google Drive 共有フォルダ — エコ運用

> **重要**: Drive 共有フォルダは大勢の社員が使う。
> 知識の浅い利用者がファイル本文を Claude にそのまま渡すと
> 1 セッションで数十万トークン浪費する事故が起きる。
> このスキルは「事故が起きないデフォルト動線」を提供する。

## 自動発火

`.claude/hooks/eco-mode-drive.sh` が PreToolUse で発火し、
Drive MCP ツール（`list_recent_files` / `search_files` / `read_file_content`
/ `download_file_content` / `get_file_metadata` 等）を検知したら自動で警告とガイドを出す。

## トリガー（人間からの指示）

- 「Drive の○○フォルダ要約して」
- 「先週共有された資料まとめて」
- 「このフォルダにある全ファイルから△△を抽出」

## 推奨ワークフロー

### Step 1: メタデータだけ取得

```
1. mcp__*__list_recent_files / search_files でファイル名・ID・更新日のみ取得
2. ★ ファイル本文はまだ読まない
```

### Step 2: 本文取得 → 即 Qwen に渡す

```
3. read_file_content で本文取得
4. ★ 必ず scripts/qwen-call.sh --task summarize で 200 字要約に圧縮
5. 圧縮後だけを Claude のコンテキストに展開
```

### Step 3: 統合判断

```
6. 全ファイルの 200 字要約が揃ったら、Claude が統合・判断
7. ユーザーへの最終回答を作成
```

## 禁止事項

- ❌ `download_file_content` の結果を Claude に丸投げ
- ❌ 1 セッションで 10 ファイル以上の本文展開
- ❌ ECO_MODE=0 のまま大容量 PDF/動画ファイルにアクセス
- ❌ 機密情報を含むファイルを外部 API（Gemini/Codex/Grok）に送る

## トークン節約の概算

| 方式 | 1 ファイル | 10 ファイル |
|------|----------|-----------|
| Claude に丸投げ | 5,000 token | 50,000 token |
| Qwen 経由要約 | 200 token | 2,000 token |
| **節約率** | **96%** | **96%** |

## 例: フォルダ要約の標準フロー

```bash
# 1. ファイル一覧（Claude が MCP 経由）
#    mcp__*__search_files { query: "AI 目標管理 共有フォルダ", maxResults: 20 }

# 2. ループで各ファイルを処理
for FILE_ID in $(echo "$LIST" | jq -r '.[].id'); do
  CONTENT=$(...)  # MCP 経由で取得
  echo "$CONTENT" | bash scripts/qwen-call.sh --task summarize > "summaries/${FILE_ID}.md"
done

# 3. 全要約を結合 → Claude に渡す（既に小さく圧縮済み）
cat summaries/*.md | head -200
```

## 関連

- `.claude/hooks/eco-mode-drive.sh` — 自動発火フック
- `scripts/qwen-call.sh` — ローカル要約器
- `scripts/llm-router.sh` — エコ判定ロジック
- `docs/multi-llm-orchestration.md` — 全体設計
