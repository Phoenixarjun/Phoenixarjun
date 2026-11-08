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
    if mono:
        names = ['consolab.ttf', 'consola.ttf', 'DejaVuSansMono-Bold.ttf', 'DejaVuSansMono.ttf', 'LiberationMono-Regular.ttf'] if bold else ['consola.ttf', 'DejaVuSansMono.ttf', 'LiberationMono-Regular.ttf']
    else:
        names = ['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf'] if bold else ['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf']
    candidates = []
    for n in names:
        candidates.extend([n, 'C:/Windows/Fonts/' + n, '/usr/share/fonts/truetype/dejavu/' + n, '/usr/share/fonts/truetype/liberation/' + n, '/System/Library/Fonts/' + n])
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def chamfer(x0,y0,x1,y1,k=22):
    return [(x0+k,y0),(x1-k,y0),(x1,y0+k),(x1,y1-k),(x1-k,y1),(x0+k,y1),(x0,y1-k),(x0,y0+k)]


def draw_base(root,t,scale=2):
    w,h=WIDTH*scale,HEIGHT*scale
    img=Image.new('RGBA',(w,h),(0,0,0,0))
    d=ImageDraw.Draw(img)
    S=lambda z:int(round(z*scale))
    xy=lambda pts:[(S(x),S(y)) for x,y in pts]
    card=chamfer(9,7,931,293,22)
    card_pts=xy(card)

    panelmask=Image.new('L',(w,h),0)
    ImageDraw.Draw(panelmask).polygon(card_pts,fill=255)

    # 1. Base container surface fill
    d.polygon(card_pts,fill=t['base'])

    # 2. Restrained internal corner glow (STRICTLY confined inside panel, never bleeding outside)
    glow=Image.new('RGBA',(w,h),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    accent_rgb=tuple(bytes.fromhex(t['accent'].lstrip('#')))
    for cx,cy in [(35,35),(905,265)]:
        gd.ellipse((S(cx-40),S(cy-40),S(cx+40),S(cy+40)),fill=accent_rgb+(35,))
    glow=glow.filter(ImageFilter.GaussianBlur(S(20)))
    glow.putalpha(ImageChops.multiply(glow.getchannel('A'),panelmask))
    img=Image.alpha_composite(img,glow)
    d=ImageDraw.Draw(img)

    # 3. Clean metallic outline border
    d.line(card_pts+[card_pts[0]],fill=t['stroke'],width=S(1.5))

    # 4. Top-left and bottom-right lime corner accents along chamfers
    tl_accent=[(9,65),(9,29),(31,7),(125,7)]
    br_accent=[(815,293),(909,293),(931,271),(931,235)]
    d.line(xy(tl_accent),fill=t['accent'],width=S(2.5))
    d.line(xy(br_accent),fill=t['accent'],width=S(2.5))

    # 5. Top window dots & interior dividing rules
    for i,color in enumerate([t['accent'],t['secondary'],t['stroke']]):
        cx,cy=38+i*18,28
        d.ellipse((S(cx-4),S(cy-4),S(cx+4),S(cy+4)),fill=color)
    d.line([(S(30),S(47)),(S(910),S(47))],fill=t['stroke'],width=S(1))
    d.line([(S(325),S(62)),(S(325),S(248))],fill=t['stroke'],width=S(1.2))
    d.line([(S(348),S(252)),(S(907),S(252))],fill=t['stroke'],width=S(1))

    # 6. Realistic robot mascot with subtle back-aura inside its bay
    aura=Image.new('RGBA',(w,h),(0,0,0,0))
    ad=ImageDraw.Draw(aura)
    ad.ellipse((S(56),S(59),S(295),S(255)),fill=accent_rgb+(30,))
    aura=aura.filter(ImageFilter.GaussianBlur(S(25)))
    aura.putalpha(ImageChops.multiply(aura.getchannel('A'),panelmask))
    img=Image.alpha_composite(img,aura)

    rp=root/'assets/logout-footer/robot-realistic-transparent.png'
    if not rp.is_file():raise FileNotFoundError('Missing real robot source: '+str(rp))
    robot=Image.open(rp).convert('RGBA')
    bbox=robot.getchannel('A').getbbox()
    robot=robot.crop(bbox)
    maxw,maxh=S(278),S(240)
    sc=min(maxw/robot.width,maxh/robot.height)
    robot=robot.resize((max(1,round(robot.width*sc)),max(1,round(robot.height*sc))),Image.Resampling.LANCZOS)
    xpos=S(35)+(maxw-robot.width)//2
    ypos=S(53)+(maxh-robot.height)//2
    img.alpha_composite(robot,(xpos,ypos))

    # 7. Complete mask: clear ALL channels (RGB and Alpha) outside the card polygon
    clean_img=Image.new('RGBA',(w,h),(0,0,0,0))
    clean_img.paste(img,(0,0),panelmask)
    return clean_img


def render(root,t,c,nchars=None,cursor=False,scale=2):
    img=draw_base(root,t,scale);d=ImageDraw.Draw(img)
    S=lambda a:round(a*scale)
    txt=c['title'] if nchars is None else c['title'][:max(0,nchars)]

    # Bold, prominent headline with dual coloring
    left='Thanks for '; accent_start=len(left)
    titlefont=font(S(36),bold=True)
    x,y=S(351),S(73)
    for idx,ch in enumerate(txt):
        color=t['accent'] if idx>=accent_start else t['text']
        d.text((x,y),ch,font=titlefont,fill=color)
        x+=round(d.textlength(ch,font=titlefont))

    if cursor:
        d.rounded_rectangle((x+S(4),y+S(2),x+S(9),y+S(42)),radius=S(1.5),fill=t['accent'])

    # Principles list
    rowfont=font(S(18),mono=True)
    for i,text in enumerate(c['principles']):
        yy=S(140+i*26)
        d.polygon([(S(355),yy),(S(366),yy+S(7)),(S(355),yy+S(14))],fill=t['accent'])
        d.text((S(380),yy-S(4)),text,font=rowfont,fill=t['text'])

    # Closing label
    closefont=font(S(17),mono=True)
    closing=c['closing'];width=d.textlength(closing,font=closefont)
    d.text((S(627)-width/2,S(259)),closing,font=closefont,fill=t['accent'])
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
        frames = []
        count = 46
        for i in range(count):
            # 0.3 s start; type over ~2.4s; hold for ~2.3s
            visible = 0 if i < 3 else min(len(c['title']), round((i - 3) / 24 * len(c['title'])))
            blink = (i % 7 < 5)
            if i > 29: visible = len(c['title'])
            fr = render(root, t, c, nchars=visible, cursor=blink, scale=1)
            frames.append(fr)
        frames[0].save(out / 'logout-card-animated.gif', save_all=True, append_images=frames[1:], duration=105, loop=0, disposal=2)
        sampleidx = [0, 7, 15, 25, 35, 45]
        sheet = Image.new('RGBA', (940 * 2, 300 * 3), t['base'])
        for j, idx in enumerate(sampleidx):
            f_clamped = frames[min(idx, len(frames) - 1)]
            sheet.alpha_composite(f_clamped, ((j % 2) * 940, (j // 2) * 300))
        sheet.convert('RGB').save(previews / 'typing-frames.png')
        print('Typing animation:', len(frames), 'frames; source robot remains a static realistic pose.')
    print('Generated:',out)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--no-gif',action='store_true')
    args=ap.parse_args();run(args.repo_root,args.no_gif is False)
