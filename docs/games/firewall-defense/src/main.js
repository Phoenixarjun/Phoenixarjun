import {FirewallGame,WAVES,WORLD,PADS,TOWER_TYPES,ENEMY_TYPES,distance} from './engine.mjs';
import {CanvasRenderer} from './renderer.js';

const $=id=>document.getElementById(id);
const game=new FirewallGame();
const renderer=new CanvasRenderer($('gameCanvas'));
const towerIcons={firewall:'⌁',cache:'◷',pulse:'◉',ids:'⌗'};
const towerNames=Object.keys(TOWER_TYPES);
let paused=false,rafId=0,lastFrame=0,acc=0,lastHUD=0,toastTimer=0,lastSound=0,ended=false,keyboardPadIndex=0;
let audioCtx=null;
const bestKey='titanium-firewall-defense-v1-highscore';
function getBest(){try{return Number(localStorage.getItem(bestKey)||0)||0;}catch{return 0;}}
function saveBest(value){if(value>getBest())try{localStorage.setItem(bestKey,String(value));}catch{}}
function beep(freq=330,duration=.08,type='sine',volume=.035){
  if(!game.audio)return;try{
    const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)return;
    if(!audioCtx)audioCtx=new Ctx();if(audioCtx.state==='suspended')audioCtx.resume();
    const osc=audioCtx.createOscillator(),gain=audioCtx.createGain();osc.type=type;osc.frequency.value=freq;
    gain.gain.setValueAtTime(volume,audioCtx.currentTime);gain.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+duration);
    osc.connect(gain);gain.connect(audioCtx.destination);osc.start();osc.stop(audioCtx.currentTime+duration+.02);
  }catch{}
}
function toast(message,kind='info'){
  const el=$('toast');el.textContent=message;el.style.color=kind==='error'?'#FF9DA7':'#B6FF3B';el.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('visible'),2200);
}
function addLog(message){const parent=$('eventLog');const d=document.createElement('div'),time=new Date().toLocaleTimeString('en-GB',{hour12:false});const s=document.createElement('span');s.textContent=time;d.append(s,document.createTextNode(' '+message));parent.prepend(d);while(parent.children.length>12)parent.lastChild.remove();}
function drawPalette(){const palette=$('towerPalette');palette.replaceChildren();for(let i=0;i<towerNames.length;i++){
  const type=towerNames[i],spec=TOWER_TYPES[type];const btn=document.createElement('button');btn.type='button';btn.className='tower-option'+(game.selectedType===type?' selected':'');btn.dataset.type=type;btn.setAttribute('aria-pressed',String(game.selectedType===type));btn.innerHTML=`<div class="tower-glyph" style="color:${spec.color}">${towerIcons[type]}</div><div class="tower-content"><div class="tower-name"><span>${spec.name}</span><span class="tower-cost">${spec.cost} CR</span></div><span class="tower-desc">${spec.desc}</span><span class="tower-stats">[${i+1}] RANGE ${spec.range} / LV. 01</span></div>`;
  btn.addEventListener('click',()=>{game.selectType(type);drawPalette();toast(`${spec.name.toUpperCase()} SELECTED — CHOOSE A NODE`);beep(430,.04,'triangle',.023);});palette.append(btn);
}}
function money(x){return Number(x).toLocaleString('en-US');}
function refreshInspector(){const padId=game.selectedPad,tower=game.getTowerAt(padId),actions=$('inspectorActions'),info=$('selectedInfo');
  if(!tower){info.className='inspector-empty';info.textContent='Select a placed defense to inspect its output, upgrade its capabilities, or reclaim its bandwidth.';actions.hidden=true;return;}
  const s=TOWER_TYPES[tower.type],upgradePrice=Math.round(s.cost*(.7+.3*(tower.level-1))),dps=(s.damage/towerCooldown(tower)).toFixed(1),refund=Math.round(tower.spent*.65);
  info.className='inspector-content';info.innerHTML=`<strong style="color:${s.color}">${s.name.toUpperCase()} <em>LVL ${tower.level}</em></strong>Node ${String(padId+1).padStart(2,'0')} &nbsp;•&nbsp; ${tower.shots} activations<br/>Effective range: ${Math.round(s.range*(1+.08*(tower.level-1)))}m<br/>Approx. base DPS: ${dps}<br/><span style="font-size:10px;color:#75938d">${s.upgrade}</span>`;
  actions.hidden=false;$('upgradeBtn').textContent=tower.level>=3?'MAX LEVEL':`▲ UPGRADE ${upgradePrice}`;$('upgradeBtn').disabled=tower.level>=3||game.credits<upgradePrice;
  $('sellBtn').textContent=`SELL +${refund}`;
}
function towerCooldown(tower){return TOWER_TYPES[tower.type].cooldown/(1+.10*(tower.level-1));}
function refreshHUD(force=false){
  $('coreValue').innerHTML=`${game.integrity} <span>/ 20</span>`;
  $('coreValue').style.color=game.integrity<=7?'#FF7886':'#EEF7EF';
  $('waveValue').innerHTML=`${String(Math.min(game.waveIndex+1,8)).padStart(2,'0')} <span>/ 08</span>`;
  $('creditsValue').innerHTML=`${money(game.credits)} <span>CR</span>`;$('killsValue').textContent=String(game.kills).padStart(3,'0');$('scoreValue').textContent=money(game.score);
  const wave=WAVES[Math.min(game.waveIndex,WAVES.length-1)];$('waveName').textContent=`${String(Math.min(game.waveIndex+1,8)).padStart(2,'0')} // ${wave.name.toUpperCase()}`;$('waveHint').textContent=wave.hint;
  $('threatTitle').textContent=wave.name.toUpperCase();$('threatDesc').textContent=wave.hint;
  $('threatIcon').textContent=game.waveIndex>=7?'⛨':game.waveIndex>=3?'⛯':'▦';
  const remain=game.phase==='wave'?Math.max(0,game.toSpawn-game.spawned)+game.enemies.length:game.phase==='ready'?wave.count:0;
  $('threatRemaining').textContent=`${remain} HOSTILES ${game.phase==='wave'?'ACTIVE':'INBOUND'}`;
  $('threatPhase').textContent=game.phase==='wave'?'LIVE ATTACK':game.phase==='ready'?'PREPARE':game.phase.toUpperCase();
  $('threatProgress').style.width=game.phase==='wave'?`${Math.round(100*game.spawned/Math.max(1,game.toSpawn))}%`:game.phase==='won'?'100%':'0%';
  $('onlineStatus').textContent=game.phase==='lost'?'OFFLINE':game.phase==='won'?'SECURED':'ONLINE';
  $('bestScore').textContent=money(Math.max(getBest(),game.score));
  $('startWaveBtn').disabled=game.phase!=='ready';
  $('startWaveBtn').textContent=game.phase==='ready'?`▶ DEPLOY WAVE ${String(game.waveIndex+1).padStart(2,'0')}`:game.phase==='wave'?'◉ WAVE LIVE':'SESSION CLOSED';
  $('speedBtn').textContent=game.speed+'× SPEED';$('pauseBtn').textContent=paused?'▶ RESUME':'Ⅱ PAUSE';$('pauseBtn').disabled=game.phase!=='wave';
  if(force){drawPalette();refreshInspector();}else if(game.selectedPad!==null)refreshInspector();
}
function processEvents(){const events=game.consumeEvents();if(!events.length)return;renderer.pushEvents(events);
  for(const e of events){switch(e.type){
    case 'build':addLog(`${TOWER_TYPES[e.towerType]?.name||'Defense'} module deployed`);beep(570,.11,'triangle');break;
    case 'upgrade':addLog(`module upgraded to level ${e.level}`);beep(700,.1);break;
    case 'sell':addLog('defense reclaimed / bandwidth returned');break;
    case 'waveStart':addLog(`wave ${String(e.wave).padStart(2,'0')} launched`);toast('HOSTILE TRAFFIC INBOUND');beep(230,.24,'sawtooth',.045);break;
    case 'kill':if(game.kills%5===0)addLog(`${game.kills} threats neutralized`);if(performance.now()-lastSound>65){beep(145,.045,'triangle',.017);lastSound=performance.now();}break;
    case 'leak':addLog(`CORE BREACHED — ${e.damage} integrity lost`);toast('⚠ CORE INTEGRITY LOST','error');beep(155,.18,'sawtooth',.055);break;
    case 'bonus':addLog('streak bonus +20 bandwidth credits');break;
    case 'waveClear':addLog(`wave ${e.wave} cleared // +${e.bonus} credits`);toast(`WAVE CLEARED — +${e.bonus} CR`);beep(720,.21,'sine',.035);saveBest(game.score);break;
    case 'gameWon':finish('won');break;
    case 'gameLost':finish('lost');break;
  }}refreshHUD(true);
}
function finish(reason){if(ended)return;ended=true;saveBest(game.score);
  $('endSymbol').textContent=reason==='won'?'◈':'⚠';$('endSymbol').style.color=reason==='won'?'#B6FF3B':'#FF7886';
  $('endTitle').textContent=reason==='won'?'NETWORK SECURED':'CORE BREACHED';
  $('endCopy').textContent=reason==='won'?'Every hostile wave was contained. The core is still online.':'Hostile packets overwhelmed the core. Rebuild a stronger perimeter and try again.';
  $('endScore').textContent=money(game.score);$('endKills').textContent=money(game.kills);
  if(!$('endDialog').open)$('endDialog').showModal();
  addLog(reason==='won'?'all waves secured':'session terminated');beep(reason==='won'?880:120,.35,'sawtooth',.043);
}
function reset(){if($('endDialog').open)$('endDialog').close();game.reset();paused=false;ended=false;renderer.effects.length=0;renderer.hoverPad=null;acc=0;drawPalette();refreshHUD(true);addLog('network simulator rebooted');toast('DEFENSE SIMULATION REBOOTED');}
function mapCoords(evt){const rect=$('gameCanvas').getBoundingClientRect();return{x:(evt.clientX-rect.left)/rect.width*WORLD.width,y:(evt.clientY-rect.top)/rect.height*WORLD.height};}
function nearPad(pos){let p=null,best=31;for(const item of PADS){const d=distance(item,pos);if(d<best){best=d;p=item;}}return p;}
function selectPad(p){if(!p)return;
  game.selectedPad=p.id;const tower=game.getTowerAt(p.id);
  if(tower){refreshInspector();toast(`${TOWER_TYPES[tower.type].name.toUpperCase()} // LEVEL ${tower.level}`);beep(360,.04,'triangle',.02);}
  else {const outcome=game.placeTower(p.id);if(!outcome.ok){toast(outcome.reason.toUpperCase(),'error');beep(155,.08,'square',.015);}else{toast(`${TOWER_TYPES[game.selectedType].name.toUpperCase()} DEPLOYED`);}}
  processEvents();refreshHUD(true);
}
$('gameCanvas').addEventListener('pointerdown',e=>{selectPad(nearPad(mapCoords(e)));});
$('gameCanvas').addEventListener('keydown',e=>{
  if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Enter','Space'].includes(e.code))e.preventDefault();
  if(e.code==='Enter'||e.code==='Space'){selectPad(PADS[keyboardPadIndex]);return;}
  const direction=e.code==='ArrowRight'?{x:1,y:0}:e.code==='ArrowLeft'?{x:-1,y:0}:e.code==='ArrowUp'?{x:0,y:-1}:e.code==='ArrowDown'?{x:0,y:1}:null;
  if(!direction)return;const current=PADS[keyboardPadIndex];
  const choices=PADS.filter(p=>p.id!==current.id).map(p=>{const dx=p.x-current.x,dy=p.y-current.y;const alignment=dx*direction.x+dy*direction.y;const perp=Math.abs(dx*direction.y-dy*direction.x);return{p,score:alignment+perp*.6,alignment,perp};}).filter(p=>p.alignment>0);
  choices.sort((a,b)=>(a.alignment+a.perp*1.8)-(b.alignment+b.perp*1.8));
  if(choices.length){keyboardPadIndex=choices[0].p.id;renderer.hoverPad=keyboardPadIndex;}
});
$('gameCanvas').addEventListener('pointermove',e=>{const p=nearPad(mapCoords(e));renderer.hoverPad=p?.id??null;$('gameCanvas').style.cursor=p?'pointer':'crosshair';});
$('gameCanvas').addEventListener('pointerleave',()=>renderer.hoverPad=null);
$('startWaveBtn').addEventListener('click',()=>{if(game.startWave()){processEvents();refreshHUD(true);}});
$('pauseBtn').addEventListener('click',()=>{if(game.phase==='wave'){paused=!paused;refreshHUD();toast(paused?'SIMULATION PAUSED':'SIMULATION RESUMED');}});
$('speedBtn').addEventListener('click',()=>{game.speed=game.speed===1?2:1;refreshHUD();toast(`${game.speed}× SIMULATION SPEED`);});
$('upgradeBtn').addEventListener('click',()=>{const outcome=game.upgradeTower(game.selectedPad);if(!outcome.ok){toast(outcome.reason.toUpperCase(),'error');beep(180,.08,'square',.02);}else{toast('MODULE UPGRADED');}processEvents();refreshHUD(true);});
$('sellBtn').addEventListener('click',()=>{const outcome=game.sellTower(game.selectedPad);if(outcome.ok){toast(`+${outcome.refund} BANDWIDTH RECOVERED`);game.selectedPad=null;processEvents();refreshHUD(true);}});
$('soundBtn').addEventListener('click',()=>{game.audio=!game.audio;$('soundBtn').textContent=game.audio?'◖)) SOUND ON':'◖)) SOUND OFF';if(game.audio)beep(530,.09);});
$('helpBtn').addEventListener('click',()=>{$('helpDialog').showModal();});
$('closeHelp').addEventListener('click',()=>{$('helpDialog').close();});
$('helpPlay').addEventListener('click',()=>{$('helpDialog').close();});
$('replayBtn').addEventListener('click',reset);
window.addEventListener('keydown',e=>{
  if($('helpDialog').open||$('endDialog').open||e.target instanceof HTMLInputElement)return;
  if(e.target===$('gameCanvas'))return;
  if(['Space','Digit1','Digit2','Digit3','Digit4'].includes(e.code))e.preventDefault();
  const ix=Number(e.key)-1;if(ix>=0&&ix<4&&Number.isInteger(ix)){game.selectType(towerNames[ix]);drawPalette();toast(`${TOWER_TYPES[towerNames[ix]].name.toUpperCase()} SELECTED`);}
  if(e.code==='Space'){if(game.phase==='ready'){game.startWave();processEvents();refreshHUD(true);}}
  if(e.key.toLowerCase()==='p'&&game.phase==='wave'){paused=!paused;refreshHUD();}
  if(e.code==='Escape'){game.selectedPad=null;refreshInspector();}
});
function frame(now){const dt=lastFrame?Math.min(.05,(now-lastFrame)/1000):0;lastFrame=now;renderer.step(dt);if(!paused&&game.phase==='wave'){
  acc+=dt*game.speed;
  let steps=0;while(acc>=1/120&&steps<15){game.update(1/120);acc-=1/120;steps++;if(game.phase!=='wave'){acc=0;break;}}
  if(steps===15)acc=0;
}
  processEvents();renderer.render(game);if(now-lastHUD>125){lastHUD=now;refreshHUD();}rafId=requestAnimationFrame(frame);
}
window.addEventListener('visibilitychange',()=>{if(document.hidden&&game.phase==='wave'&&!paused){paused=true;refreshHUD();}});
drawPalette();refreshHUD(true);rafId=requestAnimationFrame(frame);
// Explicit debugging harness used by the included browser regression tests.
if(new URLSearchParams(location.search).has('test')||window.__FIREWALL_TEST_MODE__)window.__firewallTest={game,renderer,reset,place:(pad,type)=>game.placeTower(pad,type),step:(seconds)=>{for(let t=0;t<Math.round(seconds*120);t++)game.update(1/120);processEvents();refreshHUD(true);}};
