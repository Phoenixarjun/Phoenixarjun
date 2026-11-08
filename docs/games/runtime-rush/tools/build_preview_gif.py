#!/usr/bin/env python3
"""Capture actual Runtime Rush running in Chromium to produce a gameplay GIF.
Uses an in-memory standalone document; works where localhost is restricted.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageDraw
import os,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'assets';FOLDER.mkdir(exist_ok=True)
with sync_playwright() as p:
    binary=os.environ.get('RUNTIME_RUSH_CHROME') or shutil.which('chromium') or shutil.which('google-chrome') or p.chromium.executable_path
    browser=p.chromium.launch(headless=True,executable_path=binary,args=['--enable-webgl','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content((ROOT/'standalone.html').read_text(encoding='utf8'),wait_until='load')
    page.locator('#start-btn').click()
    page.wait_for_timeout(1300)
    captures=[]
    for i in range(18):
        if i==4:page.keyboard.press('ArrowRight')
        if i==8:page.keyboard.press('Space')
        if i==12:page.keyboard.press('ArrowLeft')
        if i==15:page.keyboard.press('ArrowLeft')
        frame=Image.open(BytesIO(page.locator('#game-wrap').screenshot(type='png'))).convert('RGB')
        frame.thumbnail((760,450),Image.Resampling.LANCZOS)
        captures.append(frame.copy())
        page.wait_for_timeout(135)
    if errors: raise RuntimeError('Browser errors: '+repr(errors))
    browser.close()
    # GIF optimized palette, intentionally loops as a short teaser, unlike the full gameplay.
    pal=[x.quantize(colors=128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for x in captures]
    out=FOLDER/'runtime-rush-gameplay.gif'
    pal[0].save(out,format='GIF',save_all=True,append_images=pal[1:],duration=165,loop=0,optimize=True,disposal=2)
    print(out, out.stat().st_size, 'bytes', len(captures),'frames')
