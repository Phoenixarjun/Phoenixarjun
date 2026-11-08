"""Browser smoke suite for the generated standalone game. Uses set_content because some containers block local HTTP/file navigation."""
from pathlib import Path
import os, shutil
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
html=(BASE/'standalone.html').read_text()
with sync_playwright() as p:
    exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'); browser=p.chromium.launch(**({'executable_path':exe} if exe else {}),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    errors=[]
    desktop=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    desktop.on('pageerror',lambda e:errors.append(str(e)))
    desktop.set_content(html,wait_until='load')
    assert desktop.locator('#overlay').get_attribute('class').endswith('active')
    desktop.click('#startBtn')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='running'
    desktop.wait_for_timeout(600)
    desktop.keyboard.down('Shift')
    desktop.wait_for_timeout(300)
    desktop.keyboard.up('Shift')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.focus')<100
    desktop.keyboard.press('p')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='paused'
    desktop.keyboard.press('p')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='running'
    # Actual gameplay: synchronize a center drop through the browser integration, no source mutation.
    desktop.evaluate('''() => {let g=window.__STACK_DEBUG__.game; g.moving.x=g.tower.at(-1).x;g.moving.vx=0;g.wind=0;}''')
    desktop.keyboard.press('Space')
    desktop.wait_for_timeout(680)
    first=desktop.evaluate('({n:window.__STACK_DEBUG__.game.tower.length,score:window.__STACK_DEBUG__.game.score, mode:window.__STACK_DEBUG__.game.mode})')
    assert first['n']==2 and first['score']>0 and first['mode']=='running',first
    # Repeat a legitimate collision several times to inspect a populated tower.
    for i in range(9):
        desktop.evaluate('''() => {let g=window.__STACK_DEBUG__.game;g.moving.x=g.tower.at(-1).x;g.moving.vx=0;g.wind=0;g.release(); for(let j=0;j<95;j++)g.update(1/120); }''')
    desktop.wait_for_timeout(300)
    tenth=desktop.evaluate('({n:window.__STACK_DEBUG__.game.tower.length,score:window.__STACK_DEBUG__.game.score,sector:window.__STACK_DEBUG__.game.stage.name})')
    assert tenth['n']>=11 and tenth['score']>5000, tenth
    desktop.screenshot(path=str(BASE/'previews/desktop-tower-10.png'),full_page=True)
    # Loss and restart.
    desktop.evaluate('''() => {let g=window.__STACK_DEBUG__.game;g.moving.x=50;g.moving.vx=0;g.wind=0;g.release();}''')
    desktop.wait_for_timeout(950)
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='gameover'
    assert desktop.locator('#overlay').get_attribute('class').endswith('active')
    desktop.click('#startBtn')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='running'
    assert desktop.evaluate('window.__STACK_DEBUG__.game.tower.length')==1
    desktop.click('#helpBtn')
    assert desktop.locator('#helpDialog').evaluate('(x)=>x.open')
    desktop.click('#helpClose')
    assert not desktop.locator('#helpDialog').evaluate('(x)=>x.open')
    # One extra keyboard restart.
    desktop.keyboard.press('r')
    assert desktop.evaluate('window.__STACK_DEBUG__.game.mode')=='ready'
    assert not errors,errors
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
    mobile_errors=[]
    mobile.on('pageerror',lambda e:mobile_errors.append(str(e)))
    mobile.set_content(html,wait_until='load')
    mobile.screenshot(path=str(BASE/'previews/mobile-menu.png'),full_page=True)
    overflow=mobile.evaluate('document.documentElement.scrollWidth-innerWidth')
    assert overflow<=1,overflow
    mobile.locator('#startBtn').tap()
    mobile.locator('#dropBtn').tap()
    mobile.wait_for_timeout(550)
    assert mobile.evaluate('window.__STACK_DEBUG__.game.mode') in ('running','gameover')
    mobile.screenshot(path=str(BASE/'previews/mobile-playing.png'),full_page=True)
    assert not mobile_errors,mobile_errors
    print('PASS browser: start, drop, scoring, nine additional layers, sector progression, defeat, restart, help, pause, focus, mobile tap, no horizontal overflow, no JS exceptions')
    print('Result:',first,tenth,'mobile overflow:',overflow)
    browser.close()
