# Skill: Qwen でエコ処理（ローカル無料）

> Ollama 上の Qwen3.5 をローカルで動かし、軽処理を Claude のコンテキストに出さずに済ませる。
> **API 代ゼロ・データは外部に出ない**。Drive 共有フォルダのエコ運用の中核。

## トリガー

- 「Qwen で要約」「ローカルで処理」
- ECO_MODE=1 / DRIVE_CONTEXT=1 のとき
- 機密情報（クライアント名・契約金額）を含む文書の処理
- 後段 LLM（Gemini/Codex/Claude）に渡す前の **下ごしらえ**
- プロンプトのドラフトを複数案作成

## 実行コマンド

```bash
# 要約
cat long_doc.txt | bash scripts/qwen-call.sh --task summarize

# 分類
bash scripts/qwen-call.sh --task classify "件名: 月次請求書 ABC社 2026/4 → カテゴリ?"

# プロンプトドラフト（後段 LLM 用）
bash scripts/qwen-call.sh --task draft-prompt "Gemini で画像生成: ロゴ刷新案"

# Markdown 整形
cat raw_meeting_notes.txt | bash scripts/qwen-call.sh --task format
```

## task オプション

| task | 用途 | system プロンプト概要 |
|------|------|---------------------|
| `summarize` | 200 字要約 | 重要数値・固有名詞を保持 |
| `classify` | カテゴリ判定 | カテゴリ名と短い理由のみ |
| `draft-prompt` | 後段 LLM 用プロンプト 3 案 | 各 1〜2 行 |
| `format` | Markdown 構造化 | 内容は変えず構造のみ整形 |
| `generic` | 汎用 | 日本語で簡潔に |

## エコ運用パターン

### Drive ファイル要約 → Claude へ

```
1. Drive MCP で list/search → ファイル一覧取得
2. 各ファイル本文は read_file_content で取得（エコモードフックが警告）
3. ★ scripts/qwen-call.sh --task summarize で各ファイル 200 字に圧縮
4. 圧縮後の要約のみ Claude のコンテキストに渡す
5. 判断・統合だけ Claude が担当
```

これで 1 ファイル 5,000 token → 200 token に圧縮できる（25 倍節約）。

### 後段 LLM に投げる前のドラフト

```
1. 「○○について Gemini に画像生成プロンプトを投げたい」
2. ★ qwen-call.sh --task draft-prompt で 3 案ドラフト
3. 一番良さそうな 1 案だけ Gemini に投げる
```

API 代の節約 + 後段 LLM のレスポンス品質向上の両立。

## 認証・前提

- **認証不要**（ローカル動作）
- Ollama サーバが localhost:11434 で起動している必要がある
- モデル: `qwen3.5:7b-instruct`（既定）または `qwen3.5:14b-instruct`
- セットアップは SessionStart フックが自動化（`.claude/hooks/session-start-multi-llm-setup.sh`）

## 注意

- 7B モデルは複雑な推論には不向き。要約・分類・整形までに用途を絞る
- 推論精度が足りない場合は **haiku** へエスカレート（Claude Code で `model: haiku`）
- 14B モデルは VRAM 16GB 以上推奨
