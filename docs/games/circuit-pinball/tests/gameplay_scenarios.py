"""Browser integration checks use in-memory standalone.html to avoid network requirements."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'standalone.html').read_text(encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':960})
    errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
    page.set_content(HTML,wait_until='load')
    page.click('#startBtn')
    assert page.evaluate('circuitPinball.state')=='playing'
    page.keyboard.down('Space');page.wait_for_timeout(200);page.keyboard.up('Space')
    assert page.evaluate('circuitPinball.balls.some(b=>b.launched)')
    page.wait_for_timeout(900)
    assert page.evaluate('circuitPinball.balls.some(b=>!b.shooter)')
    page.keyboard.down('KeyA');page.wait_for_timeout(125)
    assert page.evaluate('circuitPinball.flippers[0].pressed')
    page.keyboard.up('KeyA')
    assert not page.evaluate('circuitPinball.flippers[0].pressed')
    page.keyboard.press('KeyP');assert page.evaluate('circuitPinball.state')=='paused'
    page.keyboard.press('KeyP');assert page.evaluate('circuitPinball.state')=='playing'
    page.keyboard.press('KeyM');assert not page.evaluate('circuitPinball.audio.enabled')
    page.keyboard.press('KeyM');assert page.evaluate('circuitPinball.audio.enabled')
    target=page.evaluate('''() => {
        const g=circuitPinball;
        // An isolated synthetic trial: move the live ball to a real target.
        const b=g.balls[0];b.x=225;b.y=188;b.vx=0;b.vy=650;
        for(let i=0;i<20;i++)g.step(1/120);
        return {score:g.score,count:g.targets.filter(t=>!t.alive).length};
    }''')
    assert target['count']>=1 and target['score']>0,target
    effects=page.evaluate('''() => {
      const g=circuitPinball;
      // ten separate bumper impacts, a completed target bank and a multiball event
      g.balls=[{x:264,y:389,vx:0,vy:-180,r:11,shooter:false,launched:true,trail:[],lastFlipper:{left:-999,right:-999},lastHit:-999,stuck:0}];
      for(let i=0;i<10;i++){g.time+=.12;g.balls[0].x=264;g.balls[0].y=389;g.balls[0].vx=0;g.balls[0].vy=-250;g.hitBumper(g.balls[0],CircuitPinballGameBumpers[0]);}
      const mul=g.multiplier;
      g.onBankCleared();g.onBankCleared();
      const multi=g.balls.length;
      return {mul,multi,sector:g.sector,cooldown:g.bankRespawnTimer,score:g.score};
    }''')
    assert effects['mul']>=2,effects
    assert effects['multi']>=3,effects
    assert effects['cooldown']>0,effects
    print('target collision',target,'powerups',effects)
    # Reset, then simulate a longer game session in fixed steps to test stability / draining.
    result=page.evaluate('''() => {
      const g=circuitPinball;g.begin();g.launch(.67);
      let max=0, nonFinite=false, drains=0, lastLives=g.ballsRemaining;
      for(let i=0;i<15000;i++){
        // Simulate alternating skilled flipper presses near the impact zone.
        const b=g.balls.find(x=>!x.shooter);
        g.flippers[0].pressed=!!b&&b.y>795&&b.x<385;
        g.flippers[1].pressed=!!b&&b.y>795&&b.x>385;
        if(g.state==='playing')g.step(1/120);
        if(g.ballsRemaining<lastLives){drains++;lastLives=g.ballsRemaining;}
        for(const q of g.balls){if(!Number.isFinite(q.x)||!Number.isFinite(q.y)||!Number.isFinite(q.vx)||!Number.isFinite(q.vy))nonFinite=true;max=Math.max(max,Math.hypot(q.vx,q.vy));}
        if(g.state==='gameover')break;
        if(g.balls.some(x=>x.shooter&&!x.launched))g.launch(.65);
      }
      return {state:g.state,score:g.score,high:g.best,drains,balls:g.ballsRemaining,maxSpeed:max,nonFinite,sector:g.sector};
    }''')
    assert not result['nonFinite'],result
    assert result['maxSpeed']<=1861,result
    assert result['score']>0,result
    # Skilled automated flipper control can keep the ball alive; drains are tested separately.
    print('long run',result)
    forced=page.evaluate('''() => {
      const g=circuitPinball;g.begin();g.ballSaver=0;g.saverUsed=true;
      g.balls=[{x:380,y:1116,vx:0,vy:750,r:11,shooter:false,launched:true,trail:[],lastFlipper:{left:-999,right:-999},lastHit:-999,stuck:0}];
      g.step(1/120);return {balls:g.ballsRemaining,waiting:g.balls.some(b=>b.shooter)};
    }''')
    assert forced['balls']==2 and forced['waiting'],forced
    print('genuine drain/life decrement',forced)
    page.evaluate('''() => {let g=circuitPinball;g.begin();g.nudge();g.nudge();g.nudge();}''')
    assert page.evaluate('circuitPinball.tiltTimer')>0
    print('tilt protection verified')
    # Frame render must survive even after time skips and complex multi-target animations.
    page.evaluate('circuitPinball.renderer.draw(performance.now()/1000)')
    assert errors==[],errors
    mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobileErrors=[];mobile.on('pageerror',lambda e: mobileErrors.append(str(e)))
    mobile.set_content(HTML,wait_until='load')
    mobile.click('#startBtn')
    mobile.dispatch_event('#launchBtn','pointerdown',{'pointerId':17,'pointerType':'touch','isPrimary':True})
    mobile.wait_for_timeout(250)
    mobile.dispatch_event('#launchBtn','pointerup',{'pointerId':17,'pointerType':'touch','isPrimary':True})
    mobile.wait_for_timeout(220)
    assert mobile.evaluate('circuitPinball.balls.some(b=>b.launched)'), 'mobile launch failed'
    mobile.dispatch_event('#leftBtn','pointerdown',{'pointerId':18,'pointerType':'touch','isPrimary':True})
    assert mobile.evaluate('circuitPinball.flippers[0].pressed')
    mobile.dispatch_event('#leftBtn','pointerup',{'pointerId':18,'pointerType':'touch','isPrimary':True})
    assert not mobile.evaluate('circuitPinball.flippers[0].pressed')
    assert not mobile.evaluate('document.documentElement.scrollWidth>innerWidth')
    assert mobileErrors==[],mobileErrors
    print('mobile launch + flippers verified')
    browser.close()
print('All gameplay scenarios passed')
