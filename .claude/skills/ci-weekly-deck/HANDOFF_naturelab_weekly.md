# NatureLab 週次 CIスライド — 最新状態ブリーフ（templateセッション向け）

このスキル `ci-weekly-deck` の出自＝**NatureLab Amazon 週次定例デッキ**。実納品デッキ(CIv2)に
**忠実一致**するよう作り込んだ、データ駆動の週次デッキ生成器。最新は PR #581
(`feat/ci-weekly-deck-slide-md-base`)。#580 は main にマージ済み。

## 構成（scripts/）

| ファイル | 役割 |
|---|---|
| `ci_v2_lib.py` | CI表現層（基盤ローダ・数値整形・レイアウトヘルパ・EXTRA_CSS・numfield埋込・PDF化）。**顧客非依存** |
| `deck_builders.py` | 全テーブルビルダー（skyu/DSP3表/SA/SAファネル/香調別/エマージング/PD）。列構成は実デッキ準拠 |
| `build_deck.py` | **NatureLab週次型・14枚**（OKR/S級/エマージング…）。「顧客ごとに書き換える領域」を実値に差し替え |
| `build_wella_deck.py` | WELLA月次型・8枚（別構造のクライアント例） |
| `extract_deck_data.py` | `[資料用]`タブを OAuth直読み（config駆動） |
| `sample_data.py` | ダミー構造データ（実デッキと同じ列レイアウト） |
| `assets/ci_base_sample.html` | **同梱CI基盤**（SLIDE.md準拠 sample.html・`--ink`/`--crystal`・numfield内蔵・lockup=`lk`）。スキルが自己完結 |

## NatureLab週次デッキ＝14枚

表紙 / OKR進捗ツリー / S級フル表＋洞察カード / エマージング(ブランド単位＋PV列) /
PD章扉 / PD目標 / DSP(合算/P+/Bonusの3表) / SA / まとめ(dark) / 補助章扉 /
SAファネル別 / 香調別月別 / 競合ベンチ / エマージング全ブランド一覧

## CI（SLIDE.md準拠・厳守）

- 色は **`--ink` #101820 / `--crystal` #C3D7EE / 白** の3色のみ。旧名 `--navy`/`--powder`・
  旧hex #A9CFDF/#0E1A38 は廃止。出力で実色を `grep` 確認すれば #101820/#C3D7EE のみ
- **テーブルは横罫線のみ・縦罫線なし**（列のまとまりはヘッダ網掛け）
- **丸数字①②③禁止**（「打ち手:1 / KR:1」）。考察はSMART（実数＋期限）
- A4横・ヒラギノ明朝＋Garamond・表紙numfield・5coロックアップ・CONFIDENTIALフッター
- 表のフォントは **ゴシック(Hiragino Sans)10px**（本文明朝を継承させない）

## 実デッキ忠実度（検証済み）

- 主要17要素のフォントサイズが実デッキCIv2と一致（不一致0）：表紙h1=46px / 本文h2.title=27px /
  kicker=13px / lead=21px / table.sk=10px / OKR各種 ほか
- 表紙の数字フィールド(numfield)を data URI 埋込で再現
- `slide_overflow_check.py`（`5co-CI-kit/`）で OVERFLOW なし。隅ロゴは**正準64px**（102px は旧 build_html_v3.py の上書きで、正本エンジンでは踏襲しない）

## つまずきポイント（既知の罠）

1. **「廃止色を使っている」誤判定**：スキルの旧版**説明文**に旧hex表記が残っていただけ。CSS/出力は #101820/#C3D7EE。
   → 必ず実出力を `grep -c '#A9CFDF'`（=0）で確認してから判断。0から作り直さない
2. **CI基盤**：`5co-CI-kit/5co_slide_template.html` は **#603 で CI v2（`--crystal/--ink`）に更新済み**。
   本スキルは自己完結のため同梱 `assets/ci_base_sample.html`(`--ink/--crystal`・lockup=`lk`)を正基盤とし、config はこれを指す。
3. **`build_html_v3.py`（Drive ビルドキット）は前身モノリス**＝NatureLab 直書き・narrative/PD表/競合表が
   ソースに literal・隅ロゴ102px。**正本は本スキルの汎用エンジン**（`build_deck.py`＋`deck_builders.py`＋`ci_v2_lib.py`）。
   → **#609 で実extract契約（単一DSP・`エマージング_シリーズ`）に整合済み**＝実データ3本(skyu_full/deck_data/lavon)を
   そのまま正本エンジンで14枚に組める。現場（三宅/吉田/森中）は build_html_v3.py でなく本エンジン＋NatureLab `config.json` を使う。

## 使い方（NatureLab実データ）

```bash
SKILL=.claude/skills/ci-weekly-deck
# config.json: client_name=NatureLab / ci_base_html=$SKILL/assets/ci_base_sample.html / lockup=lk / numfield_svg=""
#   spreadsheet_id=1u0WDC5HKQ_Hi1ViS_3ZF8qLVk3ysv1dnyMFTHy45c4U / ranges=[資料用]各タブ / client_logo=NatureLab実ロゴ
python3 $SKILL/scripts/build_deck.py ./config.json          # まずダミー14枚
python3 5co-CI-kit/slide_overflow_check.py ./output/*.html  # はみ出し検査
python3 $SKILL/scripts/extract_deck_data.py ./config.json   # 実データ抽出→ config.data.* に指定して再ビルド
```

提示前に **Codexで原本PPTとの数値差異チェック**。原本シートの「見込み列」に参照ズレ疑義
（全体実績＞着地見込の逆転）→ 取消線＋「要確認」で表示、確定前に担当へ確認。
POS/IGNITE等の機密生データは外部送信しない（集約値のみ）。

## PR

- #580 MERGED（初版14枚）／ #581 OPEN（SLIDE.md準拠基盤・自己完結・WELLA型追加・ダミー/実データガード）
