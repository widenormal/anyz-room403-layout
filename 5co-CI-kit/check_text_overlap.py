#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CIスライドの文字重なり検査（2026-07-09 新設・NatureLab 週次デッキで確立）。

`slide_overflow_check.py` はスライド外へのあふれ（縦・横・clip）のみを検出するため、
スライド**内**での `position:absolute` 要素同士の衝突（例: OKR凡例テキスト × 洞察カード）が
すり抜ける死角があった。本ゲートはその死角を埋める。

各 .slide 内の「テキストを直接持つ末端要素」同士の矩形交差を headless Chrome で実測し、
祖先子孫関係にないペアが 4px×4px を超えて重なっていたら報告する。

使い方: python3 check_text_overlap.py <file.html> [<file2.html> ...]
出力:   <name>: OK  /  <name>: OVERLAP slide番号:要素A×要素B(重なりpx)
戻り値: 重なりが1件でもあれば 1（ゲートとして ci-finalize.sh から呼ばれる）
"""
import sys, os, glob, shutil, subprocess, tempfile, re, pathlib, urllib.parse

def find_chrome():
    """Chrome/Chromium を自動探索（Mac → Playwright 同梱 → PATH）。
    slide_overflow_check.py と同一の探索順。Mac パス決め打ちだと
    ファイナライザ/CI (Linux/root コンテナ) で必ず失敗するため揃える。"""
    cands=["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    pw=os.environ.get("PLAYWRIGHT_BROWSERS_PATH","/opt/pw-browsers")
    cands+=sorted(glob.glob(f"{pw}/chromium-*/chrome-linux/chrome"))
    cands+=sorted(glob.glob(f"{pw}/chromium_headless_shell-*/chrome-linux/headless_shell"))
    for c in cands:
        if os.path.isfile(c) and os.access(c,os.X_OK): return c
    for n in ("google-chrome","chromium","chromium-browser","chrome"):
        p=shutil.which(n)
        if p: return p
    sys.exit("ERROR: Chrome/Chromium が見つかりません（Mac は Google Chrome を、"
             "Linux は chromium か PLAYWRIGHT_BROWSERS_PATH を用意してください）。")

CHROME=find_chrome()
PROBE="""
<script>
window.addEventListener('load', () => {
  const out=[];
  const lab=el=>{
    const t=(el.textContent||'').trim().replace(/\\s+/g,' ').slice(0,14);
    const c=(el.className&&typeof el.className==='string')?'.'+el.className.split(' ')[0]:'';
    return el.tagName.toLowerCase()+c+'"'+t+'"';
  };
  document.querySelectorAll('.slide').forEach((s,i)=>{
    const leaves=[];
    s.querySelectorAll('*').forEach(el=>{
      if(el.closest('svg')) return;
      let hasText=false;
      for(const n of el.childNodes){ if(n.nodeType===3 && n.textContent.trim()){hasText=true;break;} }
      if(!hasText) return;
      const st=getComputedStyle(el);
      if(st.visibility==='hidden'||st.display==='none'||parseFloat(st.opacity)===0) return;
      const r=el.getBoundingClientRect();
      if(r.width<2||r.height<2) return;
      leaves.push({el,r,inline:st.display==='inline'});
    });
    for(let a=0;a<leaves.length;a++)for(let b=a+1;b<leaves.length;b++){
      const A=leaves[a],B=leaves[b];
      if(A.el.contains(B.el)||B.el.contains(A.el)) continue;
      if(A.inline&&B.inline) continue;  // 行ボックス同士の接触＝通常の組版（誤検出除外）
      const ox=Math.min(A.r.right,B.r.right)-Math.max(A.r.left,B.r.left);
      const oy=Math.min(A.r.bottom,B.r.bottom)-Math.max(A.r.top,B.r.top);
      if(ox>4&&oy>4){
        out.push((i+1)+':'+lab(A.el)+'×'+lab(B.el)+'('+Math.round(ox)+'x'+Math.round(oy)+')');
        if(out.length>40){out.push('...打ち切り');a=b=1e9;}
      }
    }
  });
  document.title='OVERLAP_REPORT['+out.join(' | ')+']';
});
</script>"""

def check(path):
    html=open(path,encoding="utf-8").read()
    html=html.replace("</body>",PROBE+"</body>",1) if "</body>" in html else html+PROBE
    with tempfile.NamedTemporaryFile("w",suffix=".html",delete=False,encoding="utf-8") as f:
        f.write(html); tmp=f.name
    try:
        # --no-sandbox: CI コンテナ等 root 実行時に必須（Mac では無害）
        r=subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
                          "--virtual-time-budget=15000","--dump-dom","file://"+urllib.parse.quote(tmp)],
                         capture_output=True,text=True,timeout=120)
        m=re.search(r"OVERLAP_REPORT\[(.*?)\]</title>",r.stdout,re.S)
        rep=m.group(1).strip() if m else "(probe失敗)"
        name=pathlib.Path(path).name
        if not rep:
            print(f"{name}: OK"); return 0
        print(f"{name}: OVERLAP {rep}"); return 1
    finally:
        os.unlink(tmp)

if __name__=="__main__":
    if len(sys.argv)<2:
        sys.exit("使い方: python3 check_text_overlap.py <file.html> [...]")
    sys.exit(max(check(p) for p in sys.argv[1:]))
