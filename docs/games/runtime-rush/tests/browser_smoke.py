#!/usr/bin/env python3
"""Browser smoke test from self-contained HTML.
Works without HTTP/network access. Requires Python Playwright and installed Chromium.
Optional env RUNTIME_RUSH_CHROME points to a locally installed browser binary.
"""
from pathlib import Path
import os,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'standalone.html').read_text(encoding='utf8')
with sync_playwright() as p:
    binary=(os.environ.get('RUNTIME_RUSH_CHROME') or shutil.which('chromium')
            or shutil.which('google-chrome') or p.chromium.executable_path)
    browser=p.chromium.launch(headless=True,executable_path=binary,
             args=['--enable-webgl','--enable-unsafe-swiftshader'])
    desktop=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
    errors=[];desktop.on('pageerror',lambda e:errors.append(str(e)))
    desktop.set_content(source,wait_until='load',timeout=30000)
    desktop.wait_for_timeout(400)
    assert desktop.title()=='Runtime Rush — Titanium Hacker Arcade'
    assert not desktop.locator('#webgl-warning').is_visible(), 'Neither renderer available'
    desktop.screenshot(path=str(ROOT/'previews/desktop-menu.png'),full_page=True)
    desktop.locator('#start-btn').click()
    desktop.wait_for_timeout(1800)
    state=desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState()')
    assert state['state']=='playing' and state['distance']>15,state
    desktop.screenshot(path=str(ROOT/'previews/desktop-playing.png'),full_page=True)
    desktop.keyboard.press('ArrowRight');desktop.wait_for_timeout(320)
    state=desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState()')
    assert state['x'] < -1, f'Right key must move visually right: {state}'
    desktop.keyboard.press('Space');desktop.wait_for_timeout(140)
    state=desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState()')
    assert state['y'] > .68, f'Jump must lift the ball: {state}'
    desktop.keyboard.press('p');desktop.wait_for_timeout(180)
    frozen=desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState()')
    assert frozen['state']=='paused'
    desktop.screenshot(path=str(ROOT/'previews/desktop-paused.png'),full_page=True)
    desktop.wait_for_timeout(200)
    assert desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState().distance')==frozen['distance']
    desktop.keyboard.press('p');desktop.wait_for_timeout(250)
    assert desktop.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState().state')=='playing'
    assert not errors,errors
    print('Desktop: 3D/perspective renderer available, game start, lane right, jump, pause/resume, no JS errors: PASS')

    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,has_touch=True,is_mobile=True)
    merrors=[];mobile.on('pageerror',lambda e:merrors.append(str(e)))
    mobile.set_content(source,wait_until='load',timeout=30000)
    mobile.wait_for_timeout(350)
    assert not mobile.locator('#webgl-warning').is_visible()
    overflow=mobile.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
    assert overflow<=0,f'Mobile horizontal overflow: {overflow}px'
    mobile.screenshot(path=str(ROOT/'previews/mobile-menu.png'),full_page=True)
    mobile.locator('#start-btn').click()
    mobile.locator('#jump-btn').dispatch_event('pointerdown',{'pointerId':1})
    mobile.wait_for_timeout(350)
    mobile.screenshot(path=str(ROOT/'previews/mobile-playing.png'),full_page=True)
    assert mobile.evaluate('window.__RUNTIME_RUSH_DEBUG__.getState().state')=='playing'
    assert not merrors,merrors
    print('Mobile: 390px, touch input, no horizontal overflow, no JS errors: PASS')
    browser.close()
