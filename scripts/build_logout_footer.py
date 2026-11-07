#!/usr/bin/env python3
"""GitHub Profile 2.0 footer v2 — premium realistic mascot + pre-rendered typewriter GIF.

Requirements: Pillow (>=10). No network requests; reads centrally selected theme.
Robot artwork: assets/logout-footer/robot-realistic-transparent.png (RGBA raster).
Usage: python scripts/build_logout_footer.py
      python scripts/build_logout_footer.py --repo-root .
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

THEME={'base':'#070B0C','surface':'#1B2328','stroke':'#42535C','accent':'#B6FF3B','text':'#EEF7EF','muted':'#A6B6B2','secondary':'#8EADB6'}
CONTENT={'title':'Thanks for stopping by.','closing':'// Session Closed //','principles':['Built with curiosity','Driven by systems','Always learning','Always shipping'],'command':'logout'}
WIDTH,HEIGHT=940,300


def load(root):
    t=THEME.copy(); c=CONTENT.copy()
    p=root/'design/themes.json'
    if p.is_file():
        d=json.loads(p.read_text('utf-8'));t.update(d['presets'][d['active']])
    p=root/'content/logout-footer.json'
    if p.is_file():c.update(json.loads(p.read_text('utf-8')))
    assert len(c['principles'])==4
    return t,c


def font(size, bold=False, mono=False):
    names=(['DejaVuSansMono-Bold.ttf','Consolas.ttf','LiberationMono-Bold.ttf'] if bold and mono else
           ['DejaVuSansMono.ttf','Consolas.ttf','LiberationMono-Regular.ttf'] if mono else
           ['DejaVuSans-Bold.ttf','Arial Bold.ttf','LiberationSans-Bold.ttf'] if bold else
           ['DejaVuSans.ttf','Arial.ttf','LiberationSans-Regular.ttf'])
    candidates=[]
    for n in names:
        candidates.extend([n,'/usr/share/fonts/truetype/dejavu/'+n,'/usr/share/fonts/truetype/liberation/'+n,'C:/Windows/Fonts/'+n])
    for p in candidates:
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()


def chamfer(x0,y0,x1,y1,k=18):
    return [(x0+k,y0),(x1-k,y0),(x1,y0+k),(x1,y1-k),(x1-k,y1),(x0+k,y1),(x0,y1-k),(x0,y0+k)]


def draw_base(root,t,scale=2):
    w,h=WIDTH*scale,HEIGHT*scale
    img=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(img)
    S=lambda z:int(round(z*scale))
    xy=lambda pts:[(S(x),S(y)) for x,y in pts]
    card=chamfer(9,7,931,293,22)
    # only the intentionally-contained card surface is opaque; outside remains transparent
    d.polygon(xy(card),fill=t['base'])
    d.line(xy(card+[card[0]]),fill=t['stroke'],width=S(1.5),joint='curve')
    d.line(xy([(10,67),(10,29),(31,8),(122,8)]),fill=t['accent'],width=S(3))
    d.line(xy([(817,292),(909,292),(930,271),(930,235)]),fill=t['accent'],width=S(3))
    # Lime corner glow, clipped naturally by panel and alpha
    glow=Image.new('RGBA',(w,h));g=ImageDraw.Draw(glow)
    accent_rgb=tuple(bytes.fromhex(t['accent'].lstrip('#')))
    for cx,cy in [(26,28),(911,276)]:
        g.ellipse((S(cx-35),S(cy-35),S(cx+35),S(cy+35)),fill=accent_rgb+(65,))
    glow=glow.filter(ImageFilter.GaussianBlur(S(18)))
    img=Image.alpha_composite(glow,img)
    d=ImageDraw.Draw(img)
    d.line(xy(card+[card[0]]),fill=t['stroke'],width=S(1.4))
    d.line(xy([(10,67),(10,29),(31,8),(122,8)]),fill=t['accent'],width=S(2.7))
    d.line(xy([(817,292),(909,292),(930,271),(930,235)]),fill=t['accent'],width=S(2.7))
    for i,color in enumerate([t['accent'],t['secondary'],t['stroke']]):
        cx,cy=38+i*18,28
        d.ellipse((S(cx-4),S(cy-4),S(cx+4),S(cy+4)),fill=color)
    d.line([(S(30),S(47)),(S(910),S(47))],fill=t['stroke'],width=S(1))
    d.line([(S(325),S(62)),(S(325),S(248))],fill=t['stroke'],width=S(1.3))
    d.line([(S(348),S(252)),(S(907),S(252))],fill=t['stroke'],width=S(1))
    # Soft glow behind realistic robot, but do not alter its RGB pixels or proportions.
    aura=Image.new('RGBA',(w,h));ad=ImageDraw.Draw(aura)
    ad.ellipse((S(56),S(59),S(295),S(255)),fill=accent_rgb+(40,))
    aura=aura.filter(ImageFilter.GaussianBlur(S(30)))
    img=Image.alpha_composite(img,aura)
    rp=root/'assets/logout-footer/robot-realistic-transparent.png'
    if not rp.is_file():raise FileNotFoundError('Missing real robot source: '+str(rp))
    robot=Image.open(rp).convert('RGBA')
    # crop alpha bounds, never distort the mascot, keep the original waving pose
    bbox=robot.getchannel('A').getbbox();robot=robot.crop(bbox)
    maxw,maxh=S(278),S(240)
    sc=min(maxw/robot.width,maxh/robot.height)
    robot=robot.resize((max(1,round(robot.width*sc)),max(1,round(robot.height*sc))),Image.Resampling.LANCZOS)
    xpos=S(35)+(maxw-robot.width)//2;ypos=S(53)+(maxh-robot.height)//2
    img.alpha_composite(robot,(xpos,ypos))
    # Keep genuinely transparent outer corners; internal neon glow stays within panel.
    panelmask=Image.new('L',(w,h),0)
    ImageDraw.Draw(panelmask).polygon(xy(card),fill=255)
    img.putalpha(ImageChops.multiply(img.getchannel('A'),panelmask))
    return img


def render(root,t,c,nchars=None,cursor=False,scale=2):
    img=draw_base(root,t,scale);d=ImageDraw.Draw(img)
    S=lambda a:round(a*scale)
    txt=c['title'] if nchars is None else c['title'][:max(0,nchars)]
    # exact typography: different theme colors for 'Thanks for ' and 'stopping by.'
    left='Thanks for '; accent_start=len(left)
    titlefont=font(S(32),bold=True)
    x,y=S(351),S(79)
    for idx,ch in enumerate(txt):
        color=t['accent'] if idx>=accent_start else t['text']
        d.text((x,y),ch,font=titlefont,fill=color,stroke_width=0)
        x+=round(d.textlength(ch,font=titlefont))
    if cursor:
        d.rounded_rectangle((x+S(3),y+S(4),x+S(7),y+S(35)),radius=S(1.5),fill=t['accent'])
    rowfont=font(S(17),mono=True)
    for i,text in enumerate(c['principles']):
        yy=S(144+i*27)
        d.polygon([(S(357),yy),(S(368),yy+S(7)),(S(357),yy+S(14))],fill=t['accent'])
        d.text((S(382),yy-S(5)),text,font=rowfont,fill=t['text'])
    closefont=font(S(17),mono=True)
    closing=c['closing'];width=d.textlength(closing,font=closefont)
    d.text((S(627)-width/2,S(261)),closing,font=closefont,fill=t['accent'])
    return img


def separator_svg(t,command):
    from html import escape
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="940" height="42" viewBox="0 0 940 42" role="img"><title>Terminal footer separator</title><text x="12" y="28" font-family="DejaVu Sans Mono,Consolas,monospace" font-weight="bold" font-size="16" fill="{t['accent']}">naresh@github:~$</text><text x="216" y="28" font-family="DejaVu Sans Mono,Consolas,monospace" font-size="16" fill="{t['text']}">{escape(command)}</text><path d="M335 22H910" stroke="{t['stroke']}" stroke-width="1"/><circle cx="926" cy="22" r="3" fill="{t['accent']}"/></svg>'''


def run(root,build_gif=True):
    t,c=load(root)
    out=root/'assets/logout-footer';out.mkdir(parents=True,exist_ok=True)
    previews=root/'previews';previews.mkdir(parents=True,exist_ok=True)
    static=render(root,t,c,cursor=False,scale=2)
    static.save(out/'logout-card-static.png')
    static.resize((940,300),Image.Resampling.LANCZOS).save(previews/'logout-card-static-preview.png')
    (out/'logout-terminal-separator.svg').write_text(separator_svg(t,c['command']),encoding='utf-8')
    # Combined illustration for QA: on GitHub, always use existing separator once, followed by card.
    canvas=Image.new('RGBA',(980,400),t['base'])
    # render separator in preview with Pillow (no external SVG dependencies)
    pd=ImageDraw.Draw(canvas);pd.text((23,25),'naresh@github:~$',font=font(17,mono=True,bold=True),fill=t['accent'])
    pd.text((226,25),c['command'],font=font(17,mono=True),fill=t['text']);pd.line((335,36,950,36),fill=t['stroke'],width=1)
    card=static.resize((940,300),Image.Resampling.LANCZOS)
    canvas.alpha_composite(card,(20,76));canvas.convert('RGB').save(previews/'readme-footer-preview.png')
    # Robot-only dark preview makes it easy to audit extraction against the approved reference.
    r=Image.open(out/'robot-realistic-transparent.png').convert('RGBA')
    bg=Image.new('RGBA',r.size,t['base']);bg.alpha_composite(r);bg.convert('RGB').save(previews/'robot-on-dark.png')
    if build_gif:
        frames=[];count=46
        for i in range(count):
            # 0.3 s start; type over ~2.4s; hold for ~2.3s
            visible=0 if i<3 else min(len(c['title']),round((i-3)/24*len(c['title'])))
            blink=(i%7<5)
            if i>29:visible=len(c['title'])
            fr=render(root,t,c,nchars=visible,cursor=blink,scale=1).convert('RGB')
            frames.append(fr)
        frames[0].save(out/'logout-card-animated.gif',save_all=True,append_images=frames[1:],duration=105,loop=0,optimize=True,disposal=2)
        sampleidx=[0,7,15,25,35,45]
        sheet=Image.new('RGB',(940*2,300*3),t['base'])
        for j,i in enumerate(sampleidx):sheet.paste(frames[i],((j%2)*940,(j//2)*300))
        sheet.save(previews/'typing-frames.png')
        print('Typing animation:',len(frames),'frames; source robot remains a static realistic pose.')
    print('Generated:',out)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--no-gif',action='store_true')
    args=ap.parse_args();run(args.repo_root,args.no_gif is False)
