from pathlib import Path
from playwright.sync_api import sync_playwright
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

BASE=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(BASE)))
Thread(target=server.serve_forever,daemon=True).start()
BASE_URL=f"http://127.0.0.1:{server.server_port}/"
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu-sandbox'])
    page=browser.new_page(viewport={'width':1500,'height':1080},device_scale_factor=1)
    errs=[]
    page.on('pageerror',lambda e:errs.append(str(e)))
    page.set_content((BASE/'standalone.html').read_text(encoding='utf-8'),wait_until='load')
    page.wait_for_timeout(1300)
    assert page.locator('#startBtn').is_visible()
    print('initial title',page.title())
    (BASE/'assets').mkdir(exist_ok=True)
    page.screenshot(path=str(BASE/'assets'/'preview-desktop-menu.png'),full_page=True)
    page.click('#startBtn')
    page.keyboard.down('Space');page.wait_for_timeout(550);page.keyboard.up('Space')
    page.wait_for_timeout(1000)
    print('state',page.evaluate('({state:circuitPinball.state,balls:circuitPinball.balls.map(x=>({x:x.x,y:x.y,shooter:x.shooter})),score:circuitPinball.score})'))
    page.screenshot(path=str(BASE/'assets'/'preview-desktop-playing.png'),full_page=True)
    page.keyboard.down('KeyA');page.wait_for_timeout(250);page.keyboard.up('KeyA')
    page.keyboard.down('KeyD');page.wait_for_timeout(250);page.keyboard.up('KeyD')
    page.keyboard.press('KeyN');page.keyboard.press('KeyP');
    assert page.evaluate('circuitPinball.state')=='paused'
    page.keyboard.press('KeyP');assert page.evaluate('circuitPinball.state')=='playing'
    page.wait_for_timeout(700)
    print('errors',errs[:10])
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,has_touch=True,is_mobile=True)
    me=[];mobile.on('pageerror',lambda e:me.append(str(e)))
    mobile.set_content((BASE/'standalone.html').read_text(encoding='utf-8'),wait_until='load');mobile.wait_for_timeout(1000)
    mobile.screenshot(path=str(BASE/'assets'/'preview-mobile-menu.png'),full_page=True)
    print('mobile overflow',mobile.evaluate('document.documentElement.scrollWidth>innerWidth'))
    print('mobile errors',me[:4])
    browser.close()
    if errs or me:raise RuntimeError('browser errors: '+str(errs+me))
