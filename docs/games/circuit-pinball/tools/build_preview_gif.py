"""Capture real game physics frames into a compact looping preview GIF.
Uses Playwright's in-memory document because this environment blocks local HTTP and file origins.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
html=(BASE/'standalone.html').read_text(encoding='utf-8')
frames=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu-sandbox'])
    page=browser.new_page(viewport={'width':1000,'height':970},device_scale_factor=1)
    page.set_content(html,wait_until='load')
    page.evaluate('''() => {let g=circuitPinball;g.begin();g.launch(.88);}''')
    for index in range(20):
        page.evaluate('''() => {
          const g=circuitPinball;
          for(let i=0;i<19;i++){
            let b=g.balls.find(b=>!b.shooter);
            g.flippers[0].pressed=!!b&&b.y>790&&b.x<385;
            g.flippers[1].pressed=!!b&&b.y>790&&b.x>385;
            if(g.state==='playing')g.step(1/120);
            if(g.balls.some(b=>b.shooter&&!b.launched))g.launch(.8);
          }
          g.renderer.draw(performance.now()/1000);
        }''')
        blob=page.locator('#pinball').screenshot(type='png')
        im=Image.open(BytesIO(blob)).convert('RGB').resize((400,568),Image.Resampling.LANCZOS)
        frames.append(im.quantize(colors=96,method=Image.Quantize.FASTOCTREE))
    browser.close()
out=BASE/'assets'/'circuit-pinball-gameplay.gif'
frames[0].save(out,save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=True,disposal=2)
print('Generated',out,'frames',len(frames),'bytes',out.stat().st_size)
