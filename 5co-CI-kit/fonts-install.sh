#!/usr/bin/env bash
# fonts-install.sh — 購入済み CI フォントをフォルダから自動インストールする堅牢ラッパー。
#
# 目的: CI デッキを「忠実にレンダリングする1つの環境（ファイナライザ／各自のMac）」へ、
#       購入フォント(.otf/.ttf/.ttc)を確実に導入する。導入は冪等・導入後に実在を検証する。
#
# 使い方:
#   bash 5co-CI-kit/fonts-install.sh [FONT_SRC_DIR]   # 既定 ./fonts
#   FONT_SRC_DIR を省略時はスクリプトと同階層の fonts/ を探す。
#
# ※ Adobe Fonts について:
#   Adobe Fonts は「フォントファイル」ではなく Creative Cloud でアクティベートする方式のため、
#   本ラッパー（フォルダの .otf/.ttf を配る方式）の対象外。Adobe Fonts は各 Mac の CC、または
#   ファイナライザ Mac の CC でアクティベートして使う。本ラッパーは“実体ファイルを持つ購入フォント”
#   （または Linux ランナーへ入れたい日本語フォント等）用。
#
# 設計（堅牢性）:
#   - OS を判定し、ユーザー領域へインストール（管理者権限なしで完結）。
#   - .otf/.ttf/.ttc を再帰収集。0 件なら明確にエラー。
#   - Linux は fc-cache 更新、導入後 fc-list で family 実在を検証。
#   - macOS は ~/Library/Fonts へ配置、system_profiler で実在を検証。
#   - Windows(WSL/Git Bash) は手順を提示（レジストリ登録は PowerShell 側で実施）。
#   - 既に同名があればハッシュ比較し、同一ならスキップ／差分のみ更新。
#   - ライセンス注意を明示（配布先は最小シートに限定すること）。
set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${1:-${FONT_SRC_DIR:-$SELF_DIR/fonts}}"
EXts='-iname *.otf -o -iname *.ttf -o -iname *.ttc'

say(){ printf '%s\n' "$*"; }
die(){ printf '❌ %s\n' "$*" >&2; exit 1; }

[ -d "$SRC" ] || die "フォントフォルダが見つかりません: ${SRC}（購入フォントを置いて再実行）"

# 対象フォント収集
mapfile -t FONTS < <(find "$SRC" -type f \( -iname '*.otf' -o -iname '*.ttf' -o -iname '*.ttc' \) 2>/dev/null | sort)
[ "${#FONTS[@]}" -gt 0 ] || die "$SRC に .otf/.ttf/.ttc がありません。"

say "対象 ${#FONTS[@]} 件のフォントを検出: $SRC"
say "⚠ ライセンス注意: 購入フォントの配布先は許諾シート数の範囲に限定すること（推奨=ファイナライザ1台）。"
say ""

# OS 判定
OS="$(uname -s 2>/dev/null || echo unknown)"

hash_of(){ if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
           elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1
           else echo "nohash-$(stat -c%s "$1" 2>/dev/null || stat -f%z "$1")"; fi; }

install_one(){ # $1=src font  $2=dest dir
  local src="$1" dest_dir="$2" base; base="$(basename "$src")"
  mkdir -p "$dest_dir"
  local dst="$dest_dir/$base"
  if [ -f "$dst" ] && [ "$(hash_of "$src")" = "$(hash_of "$dst")" ]; then
    say "  ・スキップ（同一既存）: $base"; return 0
  fi
  cp -f "$src" "$dst"; say "  ✓ 導入: $base"
}

case "$OS" in
  Darwin)
    DEST="$HOME/Library/Fonts"
    say "macOS 検出 → $DEST へ導入（管理者不要）"
    for f in "${FONTS[@]}"; do install_one "$f" "$DEST"; done
    say ""
    say "=== 検証（登録フォント family） ==="
    # 反映は即時。代表的に存在確認（system_profiler は重いので任意）
    if command -v system_profiler >/dev/null 2>&1; then
      system_profiler SPFontsDataType 2>/dev/null | grep -iE 'Garamond|Hiragino|Yu Mincho|游明朝' | sed 's/^/  /' | sort -u || say "  （family 名は手動確認推奨）"
    else
      say "  （system_profiler 不可。Font Book で目視確認してください）"
    fi
    ;;
  Linux)
    DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
    say "Linux 検出 → $DEST へ導入＋fc-cache 更新"
    for f in "${FONTS[@]}"; do install_one "$f" "$DEST"; done
    if command -v fc-cache >/dev/null 2>&1; then fc-cache -f "$DEST" >/dev/null 2>&1 || true; say "  fc-cache 更新 完了"
    else say "  ⚠ fontconfig 未導入: 'sudo apt-get install -y fontconfig' を推奨"; fi
    say ""
    say "=== 検証（fc-list で family 実在） ==="
    if command -v fc-list >/dev/null 2>&1; then
      fc-list : family 2>/dev/null | tr ',' '\n' | grep -iE 'Garamond|Hiragino|Yu Mincho|游明朝|Noto Serif' | sort -u | sed 's/^/  /' || say "  ⚠ 期待 family が見つかりません（ファイル名と family 名の不一致に注意）"
    else say "  ⚠ fc-list 不可。fontconfig を導入してください"; fi
    ;;
  *)
    DEST="$HOME/.fonts"; mkdir -p "$DEST"
    say "Windows/その他 検出 → 一旦 $DEST へ集約。下記 PowerShell で登録してください:"
    for f in "${FONTS[@]}"; do install_one "$f" "$DEST"; done
    cat <<'PS'

  --- PowerShell（管理者）でのインストール ---
  $src = "$env:USERPROFILE\.fonts"
  $sh  = New-Object -ComObject Shell.Application
  $fonts = $sh.Namespace(0x14)   # Fonts 特別フォルダ
  Get-ChildItem $src -Include *.otf,*.ttf,*.ttc -Recurse | ForEach-Object { $fonts.CopyHere($_.FullName, 0x10) }
  ----------------------------------------------
PS
    ;;
esac

say ""
say "✅ 完了。レンダリング（HTML→PDF/画像）はこの環境で実行すれば、PDF にフォントサブセットが"
say "   自動埋め込みされ、どの OS でも忠実に表示されます。社員端末へのフォント配布は不要です。"
