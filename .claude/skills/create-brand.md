# 新規ブランドディレクトリ作成スキル

> 新しいブランドのディレクトリを作成する際の手順。
> ユーザーが「新規ブランド作成」「ブランド追加」等を指示した際に実行する。
> **必ずこのスキルに従って作成すること。手動でディレクトリを作成しない。**

## 実行手順

### 1. ブランド情報の確認

ユーザーに以下を確認する：

- **ブランド名**（ディレクトリ名に使用）
- **配置先の親ディレクトリ**（例: `02_OKR・CFR/`）
- **ブランドの概要**（CLAUDE.md に記載）
- **データソースの優先順位**（該当する場合）

### 2. ディレクトリ構造の作成

以下の構造を一括で作成する：

```
{ブランド名}/
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   ├── hooks/
│   │   ├── protect-files.sh
│   │   └── block-personal-info.sh
│   └── skills/
│       └── session-handoff.md
├── data/
├── docs/
├── learnings/
│   └── insights.md
├── memory/
│   ├── active-context.md
│   ├── decisions.md
│   └── sessions/
├── profile/
│   ├── preferences.md
│   └── resources.md
├── projects/
└── reference/
```

### 3. CLAUDE.md の作成

以下のテンプレートをベースに、ブランド固有の情報を記入する：

```markdown
# CLAUDE.md — {ブランド名}

{ブランドの1行説明}

## セッション開始時（必須）

1. `memory/active-context.md` を読む — 前回の作業状態
2. `profile/preferences.md` を読む — 好み・要件
3. `profile/resources.md` を読む — リソース（**更新日から30日以上経過時は警告**）
4. `learnings/insights.md` を読む — 累積知見

## セッション終了時（必須）

`.claude/skills/session-handoff.md` の手順に従い、コンテキストを永続化する。

## コアルール

- **言語**: 日本語
- **正の情報源**: `projects/*/plan.md` が各案件の唯一の確定プラン
- **即時反映**: 変更を伝えられたら該当ファイルを即座に更新
- 提案には「なぜそれを選んだか」の根拠を必ず添える
- 重要な意思決定は `memory/decisions.md` に記録する

## 禁止事項

- リソース残高を推測で記載しない（`resources.md` 参照）
- 好みの確認なしに1択で断定しない
- 案件終了後の振り返り記録をスキップしない
- 不採用プラン・旧候補をファイルに残置しない

## ブランド固有ルール

- {ブランド固有のルールをここに記載}

## コンテキスト管理（3層構造）

| Layer | 場所 | 役割 | 読み込みタイミング |
|-------|------|------|-------------------|
| 1 | `CLAUDE.md` | コアルール | 毎ターン自動注入 |
| 2 | `memory/` | セッション状態 | セッション開始時 |
| 3 | `.claude/skills/` | 手順スキル | 必要時にオンデマンド |
```

### 4. settings.json の配置

ルートの `.claude/settings.json` をコピーする。
ただし、ブランド固有の PostToolUse フックがある場合は追記する。

### 5. フックスクリプトの配置

ルートの `.claude/hooks/` から以下をコピーする：

- `protect-files.sh`（そのまま使用可）
- `block-personal-info.sh`（`@5inc.jp` が設定済みであること確認）

**必ず実行権限を付与する:**

```bash
chmod +x .claude/hooks/*.sh
```

### 6. session-handoff.md の配置

ルートの `.claude/skills/session-handoff.md` をコピーする。

### 7. Layer 2 ファイルの初期化

以下のファイルをテンプレートから作成する：

- `memory/active-context.md` — 空テンプレート
- `memory/decisions.md` — 空テンプレート
- `learnings/insights.md` — 空テンプレート
- `profile/preferences.md` — 空テンプレート
- `profile/resources.md` — 更新日を本日に設定

### 8. 完了確認

作成後、以下を確認して報告する：

- [ ] CLAUDE.md にセッション開始/終了手順が記載されている
- [ ] `.claude/settings.json` に PreToolUse フックが定義されている
- [ ] `.claude/hooks/` のスクリプトに実行権限がある
- [ ] `memory/`, `learnings/`, `profile/` に初期ファイルがある
- [ ] `.claude/skills/session-handoff.md` が配置されている

## 注意事項

- このスキルを経由せずにブランドディレクトリを作成しない
- 既存ブランドのファイルをそのままコピーしない（固有ルールが混入するため）
- フックスクリプトの内容を変更しない（管理者承認が必要）
