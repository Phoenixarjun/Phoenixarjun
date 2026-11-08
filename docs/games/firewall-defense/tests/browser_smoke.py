"""Optional Chromium UI regression smoke test. Requires playwright and installed Chromium.

Uses the one-file build and set_content to function in locked-down local test environments.
In a normal computer, you can instead open standalone.html or serve index.html.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'standalone.html').read_text(encoding='utf8')
HTML=HTML.replace('<script type="module">','<script>window.__FIREWALL_TEST_MODE__=true;</script><script type="module">',1)

def run():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1600,'height':1050})
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content(HTML,wait_until='load')
        page.wait_for_timeout(200)
        assert page.locator('.tower-option').count()==4
        assert page.evaluate('window.__firewallTest.game.phase')=='ready'
        bbox=page.locator('#gameCanvas').bounding_box()
        for x,y in [(414,278),(414,344),(216,278)]:
            page.mouse.click(bbox['x']+x*bbox['width']/960,bbox['y']+y*bbox['height']/624)
        assert page.evaluate('window.__firewallTest.game.towers.length')==3
        page.locator('#startWaveBtn').click();page.wait_for_timeout(650)
        assert page.evaluate('window.__firewallTest.game.phase')=='wave'
        page.locator('#pauseBtn').click();assert 'RESUME' in page.locator('#pauseBtn').inner_text()
        page.locator('#pauseBtn').click();assert 'PAUSE' in page.locator('#pauseBtn').inner_text()
        page.locator('#speedBtn').click();assert '2×' in page.locator('#speedBtn').inner_text()
        page.evaluate('window.__firewallTest.step(40)')
        assert page.evaluate('window.__firewallTest.game.waveIndex')==1
        page.mouse.click(bbox['x']+414*bbox['width']/960,bbox['y']+278*bbox['height']/624)
        page.locator('#upgradeBtn').click()
        assert page.evaluate('window.__firewallTest.game.getTowerAt(15)?.level')==2
        page.locator('#helpBtn').click();assert page.locator('#helpDialog').evaluate('(el)=>el.open')
        page.locator('#closeHelp').click();assert not page.locator('#helpDialog').evaluate('(el)=>el.open')
        assert not errors,errors
        mobile=browser.new_page(viewport={'width':390,'height':844},has_touch=True)
        mobile_errors=[];mobile.on('pageerror',lambda error:mobile_errors.append(str(error)))
        mobile.set_content(HTML,wait_until='load');mobile.wait_for_timeout(200)
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        mobile.locator('#gameCanvas').tap(position={'x':160,'y':230})
        assert mobile.evaluate('window.__firewallTest.game.towers.length')==1
        assert not mobile_errors,mobile_errors
        browser.close()
        print('Browser regression checks passed: build, wave, pause, speed, upgrade, help, mobile tap, no page overflow, zero JS exceptions.')
if __name__=='__main__':run()
