import sys
from playwright.sync_api import sync_playwright
only=[int(x) for x in sys.argv[1:]] or list(range(1,18))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':720})
    pg.goto('file:///home/claude/gapfuzz/evaluation/presentation/midterm.html#1'); pg.wait_for_timeout(400)
    pg.evaluate("document.getElementById('help').style.display='none'")
    for k in range(1,18):
        pg.keyboard.press('Home')
        for _ in range(k-1): pg.keyboard.press('ArrowRight')
        pg.wait_for_timeout(220)
        if k in only: pg.screenshot(path=f'shots/s{k:02d}.png')
        res=pg.evaluate("""() => {
          const s=document.querySelector('.stage > section.on'); const sr=s.getBoundingClientRect();
          const sc=sr.width/1280; const out=[];
          const src=s.querySelector('.src'); const srcTop = src ? src.getBoundingClientRect().top : null;
          const pn=s.querySelector('.pageno'); const pnTop = pn ? pn.getBoundingClientRect().top : sr.bottom;
          s.querySelectorAll('h1,h2,p,table,pre,svg,.facts,.goals,.plan,.callout,.cov').forEach(el=>{
            if (el.closest('.src')) return;
            const r=el.getBoundingClientRect();
            const bottom=(r.bottom-sr.top)/sc, right=(r.right-sr.left)/sc;
            if (bottom>700 || right>1282) out.push(el.tagName+'.'+el.className+' bottom='+bottom.toFixed(0)+' right='+right.toFixed(0));
            if (srcTop && r.bottom>srcTop+1) out.push('출처와 겹침 '+el.tagName+'.'+el.className+' '+((r.bottom-srcTop)/sc).toFixed(0)+'px');
          });
          s.querySelectorAll('pre').forEach(el=>{ if(el.scrollWidth>el.clientWidth+1) out.push('pre 가로넘침 '+(el.scrollWidth-el.clientWidth)); });
          return out; }""")
        print(k, res if res else 'OK')
    b.close()
