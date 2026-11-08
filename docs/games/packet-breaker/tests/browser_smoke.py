"""Optional browser smoke test: python tests/browser_smoke.py
Requires `pip install playwright` and an installed Chrome/Chromium.
Uses Playwright set_content to avoid any server/network dependency during validation.
"""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def inline_page():
    html=(ROOT/'index.html').read_text('utf-8')
    css=(ROOT/'style.css').read_text('utf-8')
    js=(ROOT/'dist/game.bundle.js').read_text('utf-8')
    return html.replace('<link rel="stylesheet" href="./style.css" />',f'<style>{css}</style>').replace('<script defer src="./dist/game.bundle.js"></script>','').replace('</body>',f'<script>{js}</script></body>')

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=which("chromium") or which("google-chrome") or None, args=["--no-sandbox","--disable-dev-shm-usage"])
        try:
            page=browser.new_page(viewport={'width':1440,'height':900})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(inline_page())
            assert page.evaluate('window.__packetBreakerDebug.snapshot().mode')=='menu'
            page.locator('#primaryAction').click()
            assert page.evaluate('window.__packetBreakerDebug.snapshot().mode')=='ready'
            page.locator('#gameCanvas').click(position={'x':300,'y':240})
            assert page.evaluate('window.__packetBreakerDebug.snapshot().mode')=='playing'
            page.keyboard.press('p')
            assert page.evaluate('window.__packetBreakerDebug.snapshot().mode')=='paused'
            page.keyboard.press('p')
            assert page.evaluate('window.__packetBreakerDebug.snapshot().mode')=='playing'
            page.locator('#soundBtn').click()
            assert 'SOUND OFF' in page.locator('#soundBtn').inner_text()
            mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
            mobile.on('pageerror',lambda e:errors.append(str(e)))
            mobile.set_content(inline_page())
            widths=mobile.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
            assert widths['sw']==widths['cw'],f'mobile horizontal overflow: {widths}'
            mobile.locator('#primaryAction').click()
            mobile.locator('#gameCanvas').tap(position={'x':140,'y':120})
            assert mobile.evaluate('window.__packetBreakerDebug.snapshot().mode')=='playing'
            assert not errors,f'browser JS errors: {errors}'
            print('PASS browser smoke: start, launch, pause/resume, sound, mobile touch, no overflow, no runtime errors')
        finally:
            browser.close()

if __name__=='__main__':main()
