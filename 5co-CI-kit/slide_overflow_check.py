#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIスライドのはみ出し検査
各 .slide の scrollHeight が clientHeight(=720px固定) を超えていないかを
headless Chrome で実測する。編集後は必ず実行すること（ガイドライン§5.6）。

使い方: python3 slide_overflow_check.py <file.html> [<file2.html> ...]
出力:   OK or OVERFLOW slide番号:+超過px
"""
import sys, pathlib, subprocess, tempfile, re, urllib.parse

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROBE = """
<script>
window.addEventListener('load', () => {
  const out = [];
  document.querySelectorAll('.slide').forEach((s, i) => {
    const over = s.scrollHeight - s.clientHeight;
    if (over > 2) out.push((i + 1) + ':+' + over + 'px');
  });
  document.title = 'OVERFLOW_REPORT[' + out.join(',') + ']';
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
        r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--dump-dom',
                            '--virtual-time-budget=4000', url],
                           capture_output=True, text=True, timeout=60)
        m = re.search(r'OVERFLOW_REPORT\[([^\]]*)\]', r.stdout)
        if not m:
            return 'ERROR: report not found'
        return 'OVERFLOW ' + m.group(1) if m.group(1) else 'OK'
    finally:
        tmp.unlink(missing_ok=True)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(f'{pathlib.Path(p).name}: {check(pathlib.Path(p))}')
