"""Generate a real captured GIF of the running game using locally installed Chromium+Playwright.
No AI mockups and no hand-drawn gameplay frames.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'standalone.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page.set_content(html,wait_until='load')
 page.click('#startBtn')
 page.evaluate('''() => {let g=window.__STACK_DEBUG__.game;for(let i=0;i<6;i++){g.moving.x=g.tower.at(-1).x;g.moving.vx=0;g.wind=0;g.release();for(let j=0;j<95;j++)g.update(1/120);}}''')
 page.wait_for_timeout(250)
 frames=[]
 def grab():
  data=page.locator('.canvas-frame').screenshot()
  im=Image.open(BytesIO(data)).convert('RGB')
  im.thumbnail((760,520),Image.Resampling.LANCZOS)
  frames.append(im.copy())
 for _ in range(5):page.wait_for_timeout(90);grab()
 page.evaluate('''() => {let g=window.__STACK_DEBUG__.game;g.moving.x=g.tower.at(-1).x;g.moving.vx=0;g.wind=0;}''')
 page.evaluate('window.__STACK_DEBUG__.drop()')
 for _ in range(16):page.wait_for_timeout(40);grab()
 for _ in range(7):page.wait_for_timeout(100);grab()
 b.close()
 palette=[im.quantize(colors=112,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE) for im in frames]
 palette[0].save(ROOT/'assets/stack-overflow-gameplay.gif',save_all=True,append_images=palette[1:],duration=[95]*5+[55]*16+[180]*7,loop=0,optimize=True,disposal=2)
 print('GIF frames:',len(frames),'bytes:',(ROOT/'assets/stack-overflow-gameplay.gif').stat().st_size)

# The cover uses a screenshot of the actual live ten-layer game, not a synthetic UI depiction.
im=Image.open(ROOT/'previews/desktop-tower-10.png').convert('RGB')
# Center crop with board emphasized
W,H=1400,800
canvas=Image.new('RGB',(W,H),'#081011')
source=im.crop((20,15,min(im.width,1320),min(im.height,1110)))
source=source.resize((W,920),Image.Resampling.LANCZOS)
canvas.paste(source,(0,-55))
# Add subtle edges and small lower label band
from PIL import ImageDraw
D=ImageDraw.Draw(canvas,'RGBA');D.rectangle((0,732,W,800),fill=(4,11,12,219));D.line((0,730,W,730),fill=(182,255,59,180),width=2)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
try:f=ImageFont.truetype(font_path,21)
except: f=ImageFont.load_default()
D.text((35,750),'STACK OVERFLOW  //  SERVER TOWER PROTOCOL',font=f,fill='#B6FF3B')
canvas.save(ROOT/'assets/arcade-cover.png',optimize=True)
print('Cover saved', (ROOT/'assets/arcade-cover.png').stat().st_size)
