#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIスライドのはみ出し検査
各 .slide の scrollHeight が clientHeight(=720px固定) を超えていないかを
headless Chrome で実測する。編集後は必ず実行すること（ガイドライン§5.6）。

使い方: python3 slide_overflow_check.py <file.html> [<file2.html> ...]
出力:   OK or OVERFLOW slide番号:+超過px
"""
import sys, os, glob, shutil, pathlib, subprocess, tempfile, re, urllib.parse


def find_chrome() -> str:
    """Chrome/Chromium を自動探索（Mac → Playwright 同梱 → PATH）。
    従来は Mac パス決め打ちで、ファイナライザ/CI (Linux) では必ず失敗していた。
    探索順は scripts/html_to_pptx.py / ci-finalize.sh と同一。"""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    pw = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    candidates += sorted(glob.glob(f"{pw}/chromium-*/chrome-linux/chrome"))
    candidates += sorted(glob.glob(f"{pw}/chromium_headless_shell-*/chrome-linux/headless_shell"))
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("ERROR: Chrome/Chromium が見つかりません（Mac は Google Chrome を、"
             "Linux は chromium か PLAYWRIGHT_BROWSERS_PATH を用意してください）。")


CHROME = find_chrome()
PROBE = """
<script>
window.addEventListener('load', () => {
  const out = [];
  const logo = [];
  document.querySelectorAll('.slide').forEach((s, i) => {
    const over = s.scrollHeight - s.clientHeight;
    if (over > 2) out.push((i + 1) + ':+' + over + 'px');
    // 隅ロゴ幅ガード: 正準=102px（CI v2・V3実デッキ準拠）。表紙(cover)の cf-logo は除外。
    const lg = s.querySelector('svg.corner, .corner-logo, .hd, svg.cc-logo, .lockup');
    if (lg && !s.matches('.cover-full, .cover-card')) {
      const w = Math.round(lg.getBoundingClientRect().width);
      if (w > 112) logo.push((i + 1) + ':' + w + 'px');
    }
  });
  document.title = 'OVERFLOW_REPORT[' + out.join(',') + ']!LOGO_REPORT[' + logo.join(',') + ']';
});
</script>
"""

def check(path: pathlib.Path) -> str:
    html = path.read_text()
    probe_html = html.replace('</body>', PROBE + '</body>') if '</body>' in html else html + PROBE
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, dir=str(path.parent)) as tf:
        tf.write(probe_html)
        tmp = pathlib.Path(tf.name)
    try:
        url = 'file://' + urllib.parse.quote(str(tmp))
        # --no-sandbox: CI コンテナ等 root 実行時に必須（Mac では無害）
        r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--dump-dom', '--virtual-time-budget=4000', url],
                           capture_output=True, text=True, timeout=60)
        m = re.search(r'OVERFLOW_REPORT\[([^\]]*)\]', r.stdout)
        if not m:
            return 'ERROR: report not found'
        lm = re.search(r'LOGO_REPORT\[([^\]]*)\]', r.stdout)
        msgs = []
        if m.group(1):
            msgs.append('OVERFLOW ' + m.group(1))
        if lm and lm.group(1):
            msgs.append('LOGO>112px ' + lm.group(1))  # 隅ロゴ過大（正準102px・CI v2/V3準拠）
        # <title> がファイル名の主題と無関係＝head 流用時の更新漏れを検出
        tm = re.search(r'<title>(.*?)</title>', html, re.S)
        if tm:
            title = tm.group(1).strip()
            if '__DOC_TITLE__' in title:
                msgs.append('TITLE? <title> がテンプレ未置換（__DOC_TITLE__ のまま）')
            STOP = {'スライド', 'シート', '資料', 'さん', 'ため', 'こと', '全社', '共有', '版'}
            ftoks = set(re.findall(r'[一-龥ぁ-んァ-ヶ]{2,}', re.sub(r'\d{6,8}', '', path.stem))) - STOP
            ttoks = set(re.findall(r'[一-龥ぁ-んァ-ヶ]{2,}', title)) - STOP
            if title and ftoks and not (ftoks & ttoks):
                msgs.append(f'TITLE? <title>「{title[:24]}」がファイル名と不一致（テンプレ流用の更新漏れ?）')
        return ' / '.join(msgs) if msgs else 'OK'
    finally:
        tmp.unlink(missing_ok=True)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(f'{pathlib.Path(p).name}: {check(pathlib.Path(p))}')
