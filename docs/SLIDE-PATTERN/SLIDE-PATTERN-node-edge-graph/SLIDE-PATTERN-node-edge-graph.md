# SLIDE-PATTERN-node-edge-graph

このファイルはスライドのコンテンツエリア（タイトル行より下の領域）のレイアウトパターン定義書です。SLIDE.mdと組み合わせてAIツールに渡すことで、このパターンのスライドを生成できます。タイトルエリア・ページ番号・装飾はSLIDE.mdの `Slide Frame` セクションで定義されるため、このファイルには含みません。

## Overview
**パターン名：** node-edge-graph
**概要：** ノード（ボックス）をグリッド座標系（列×行）上の任意の位置に置き、ノード間の関係をエッジ（矢印）として明示的に描くグラフ図。エッジごとに線種・ラベルで意味（自動／人手、月次／随時 等）を持たせられるため、直線的なステップフローでは表現できない「戻り」「合流」「参照」を含む関係構造を1枚で示せる。座標はすべてグリッドの式から算出し、専用の自動検査（ノード重なり・矢印接続）で崩れを防ぐ。
**適したシーン：** 業務プロセスのループ構造（OODA・PDCA の実運用形）、システム間のデータ連携図、組織・ツール間の情報の流れ、依存関係・参照関係のネットワーク表現

## Structure（構造）

```yaml
layout: node-edge-graph
title_area: true
content_area:
  padding: "12px 40px 14px"
  children:
    - id: graph_svg
      type: inline_svg
      class: ne-graph          # 検査対象マーカー（graph_node_edge_check.py）
      viewBox: "0 0 880 430"
      grid:                    # ノード座標はすべてこの式から算出（手置き禁止）
        margin: 8
        cols: 8                # col_x(i) = 8 + i*108
        col_width: 108
        rows: 5                # row_y(j) = 8 + j*82
        row_height: 82
        node_height: 44
        gap: 12                # node.w = colspan*108 - 12
      elements:
        - type: node           # rect（class="ne-node" 必須）
          count: "4〜8個"
          size: { width: "colspan×108−12", height: 44 }
          fill: ["#FFFFFF", "#F5F5F5", "#EEEEEE"]   # 強調ノードは一段濃く
          stroke: "#999999"
        - type: edge           # line / polyline / path（class="ne-edge" 必須）
          endpoint_rule: "始点・終点はノードの接続点の式から算出"
          connection_points:
            top-center:    "(x + w/2, y)"
            bottom-center: "(x + w/2, y + h)"
            left-center:   "(x, y + h/2)"
            right-center:  "(x + w, y + h/2)"
          semantics: "実線＝自動・定常 ／ 破線＝人手・随時（線種に意味を持たせる）"
          marker: "#999999"
        - type: edge_label     # 頻度・条件（月次／随時／承認 等）
          font_size: 10
        - type: legend
          note: "見本線はノードへ繋がないため class=\"ne-skip\" で検査除外"
```

## グリッド座標システム（本パターンの中核ルール）

ノードを絶対座標で手置きせず、**グリッド（列×行）上の位置＋幅（colspan）で定義**する。
エッジは常にノードの縁の式から機械的に算出し、手で微調整しない。

```
col_x(i) = MARGIN + i * COL_W   // 列iの左端x
row_y(j) = MARGIN + j * ROW_H   // 行jの上端y

node = { x: col_x(i), y: row_y(j), w: colspan * COL_W - GAP, h: NODE_H }

// ノードの接続点（エッジの起点・終点は必ずこれらの縁上の点を使う）
top-center    = (x + w/2, y)
bottom-center = (x + w/2, y + h)
left-center   = (x, y + h/2)
right-center  = (x + w, y + h/2)
```

スケルトンは 8列×5行（viewBox 880×430・MARGIN=8・COL_W=108・ROW_H=82・NODE_H=44・GAP=12）。
列数・セルサイズは案件ごとに調整可（式ごと差し替える）。

**利点：** ノード数・文言量が変わっても影響範囲は「新しい行・列を1つ足す」だけで済み、
既存ノードの座標を引き直す必要がない（5ノード→12ノードへの拡張で既存座標・エッジ無変更を実証済み）。

## 実装構成の選択（純SVG／ハイブリッド）

| 構成 | 作り方 | 向く場面 |
|------|--------|---------|
| 純SVG構成（スケルトンどおり） | ノードも `rect.ne-node` で SVG 内に描く | パターン変換（ci_pattern_adapter）・図が自己完結する場合・文言が短い場合 |
| **ハイブリッド構成（実運用で最安定）** | ノード＝HTML div（`.ne-node` 付与・既存CSSクラス流用可）、エッジ＝コンテナ内に `position:absolute` で重ねた SVG（`.ne-edge`）、コンテナ（div）に `.ne-graph` | CIスライド本番化。和文の折返し・組版を HTML に任せられ、純SVG＋foreignObject より折返し精度が高い |

どちらの構成でも `graph_node_edge_check.py` は screen 座標系で突き合わせるため同一に検査できる
（ハイブリッドの座標はグリッドの式を CSS px（left/top/width）にそのまま使う）。

## Elements（各要素の役割）

| 要素 | 役割 | 推奨テキスト量 |
|------|------|--------------|
| ノード（rect.ne-node） | 主体・工程・システム・成果物 | 4〜12文字、全体で4〜8個 |
| エッジ（.ne-edge 実線） | 自動・定常の流れ | テキストなし |
| エッジ（.ne-edge 破線） | 人手・随時・差戻しの流れ | テキストなし |
| エッジラベル | 頻度・条件・トリガー（月次／随時／承認 等） | 2〜8文字、主要エッジのみ |
| 強調ノード（濃い背景） | 議論の焦点・最終成果物 | 1〜2個まで |
| 凡例（.ne-skip の見本線） | 線種の意味を補足 | 1行 |

## Usage Guide（AIへの使い方）

### プロンプト例

```
SLIDE.md と SLIDE-PATTERN-node-edge-graph.md を参照して、
以下の月次レポート運用の関係構造をノード・エッジ図のスライドにしてください。

【ノード（グリッド位置）】
- データ収集（col0-2, row0）
- 自動集計・レポート生成（col5-7, row0）
- マスタ情報（col3-4, row2）
- 責任者確認（col5-7, row4・強調）
- 修正指示（col3-4, row4）
- 担当者対応（col0-2, row4）

【エッジ】
- データ収集 → 自動集計（実線・ラベル「夜間バッチ」）
- 自動集計 → 責任者確認（実線・ラベル「月次」）
- マスタ情報 → 自動集計（実線・直交ポリライン）
- 責任者確認 → 修正指示 → 担当者対応（破線＝人手）
- 担当者対応 → データ収集（破線・ラベル「再収集（随時）」）

【スライドタイトル】
月次レポートはどこが自動で、どこに人手が残るか
```

### 注意点
- ノードは4〜8個に絞る（9個超なら2枚に分割するか粒度を上げる）
- **座標を手で微調整しない**。文言が入らない場合は colspan を増やすか列数の式ごと変える
  （1ノードだけ幅を手伸ばしすると隣と重なる＝実際に試作で起きた実害）
- エッジの始点・終点は必ず接続点の式から取る（ズレると「浮いた矢印」になる）
- 線種は2種まで（実線／破線）。3種以上の意味分けは判読性が落ちるため凡例で補っても避ける
- エッジ同士が同一直線上に重ならないよう、接続点（上下左右）を使い分ける
- 凡例の見本線など意図的にノードへ繋がない線は `class="ne-skip"` を付けて検査除外する
- **検査必須**：`python3 5co-CI-kit/graph_node_edge_check.py <file.html>` でノード重なり
  （NODE_OVERLAP）・矢印の浮き（EDGE_DETACHED）が OK になるまで配布しない
  （`ci-finalize.sh` が自動でゲートする。`svg.ne-graph`＋`rect.ne-node`＋`.ne-edge` のタグ付けが前提）
