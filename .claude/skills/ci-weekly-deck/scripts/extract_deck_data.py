#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_deck_data.py — 集計用シートの[資料用]タブ群を OAuth直読みで抽出 → deck_data.json

設定は config.json から読む(spreadsheet_id / ranges / oauth_token / extract_out)。
スプレッドシートIDや顧客名はソースに直書きせず config.json に置く(=共有リポに実IDを残さない)。

前提:
  - google-api-python-client / google-auth がインストール済(例: ~/venv-gapi/bin/python3)
  - oauth_token.json = Sheets読み取りスコープ付きのOAuthトークン(原本シートへの閲覧権限)
  - コピー不可のシート(外部コネクタ依存)はライブ範囲読みのみ。コピーすると値が壊れる点に注意。

使い方:
  python3 extract_deck_data.py [config.json へのパス(既定: ../config.json)]
"""
import json
import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8"))

    token_path = os.path.expanduser(cfg.get("oauth_token", "~/oauth_token.json"))
    c = json.load(open(token_path))
    creds = Credentials(
        token=c.get("token"), refresh_token=c.get("refresh_token"),
        token_uri=c.get("token_uri"), client_id=c.get("client_id"),
        client_secret=c.get("client_secret"), scopes=c.get("scopes"),
    )
    sv = build("sheets", "v4", credentials=creds)

    sid = cfg["spreadsheet_id"]
    if not sid or sid.startswith("REPLACE_"):
        sys.exit("config.json の spreadsheet_id が未設定です。")

    out = {}
    for name, rng in cfg["ranges"].items():
        try:
            r = sv.spreadsheets().values().get(
                spreadsheetId=sid, range=rng, valueRenderOption="FORMATTED_VALUE"
            ).execute()
            out[name] = r.get("values", [])
            print(f"OK {name}: {len(out[name])}行")
        except Exception as e:  # noqa: BLE001 - 1タブ失敗で全体を止めない
            print(f"NG {name}: {str(e)[:120]}")
            out[name] = []

    dst = os.path.expanduser(cfg.get("extract_out", "/tmp/deck_data.json"))
    json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
    print(f"\n保存: {dst}")


if __name__ == "__main__":
    main()
