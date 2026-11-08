import { StackGame,STAGES,clamp,BLOCK_H,G } from './physics.mjs';
import { Scene } from './renderer.js';
const $=id=>document.getElementById(id);
const game=new StackGame();const scene=new Scene($('gameCanvas'));
const saved=(()=>{try{return JSON.parse(localStorage.getItem('stack-overflow-score-v1')||'{"layers":0,"score":0}')}catch{return {layers:0,score:0}}})();
let best={layers:Number(saved.layers)||0,score:Number(saved.score)||0};
let last=0,acc=0,uiWait=0,toastHandle=0,lastLength=game.tower.length,ended=false;
let muted=false;let audio=null;
function tone(freq=420,duration=.1,type='sine',volume=.045){if(muted)return;try{audio ||= new (window.AudioContext||window.webkitAudioContext)();if(audio.state==='suspended')audio.resume();const o=audio.createOscillator(),g=audio.createGain();o.type=type;o.frequency.value=freq;g.gain.setValueAtTime(volume,audio.currentTime);g.gain.exponentialRampToValueAtTime(.0001,audio.currentTime+duration);o.connect(g);g.connect(audio.destination);o.start();o.stop(audio.currentTime+duration)}catch{}}
function successSound(perfect){tone(perfect?830:450,.09,'triangle',.032);setTimeout(()=>tone(perfect?1180:600,.13,'sine',.028),70)}
function showToast(msg){const el=$('toast');el.textContent=msg;el.classList.add('show');clearTimeout(toastHandle);toastHandle=setTimeout(()=>el.classList.remove('show'),1800)}
function overlay(mode){const el=$('overlay');if(!mode){el.classList.remove('active');return}el.classList.add('active');const configs={
 ready:['// INITIATING DEPLOYMENT','BUILD THE <em>IMPOSSIBLE.</em>','Time your release. Stack server layers and keep the system standing as the platform shrinks.','▶ START DEPLOYMENT'],
 paused:['// PROCESS SUSPENDED','SIMULATION <em>PAUSED.</em>','Your stack is safe for now. Resume when you are ready to continue the deployment.','▶ RESUME SIMULATION'],
 gameover:['// STRUCTURAL FAILURE','STACK <em>OVERFLOW.</em>',`You deployed ${game.tower.length-1} server layers and earned ${game.score.toLocaleString()} points. Reboot to beat your personal best.`, '↻ RETRY DEPLOYMENT']};
 const [k,t,p,b]=configs[mode]||configs.ready;$('overlayKicker').textContent=k;$('overlayTitle').innerHTML=t;$('overlayText').textContent=p;$('startBtn').textContent=b;
}
function start(){if(game.mode==='gameover'){game.reset();lastLength=1;ended=false;}if(game.mode==='paused'){game.pause();}else game.start();overlay(null);tone(540,.12);$('gameCanvas').focus({preventScroll:true});syncUI();}
function drop(){if(game.mode==='paused'||game.mode==='gameover')return;if(game.mode==='ready'){start();return;}if(game.release()){tone(300,.055,'sawtooth',.024);syncUI();}}
function restart(){game.reset();lastLength=1;ended=false;scene.fx=[];scene.shake=0;overlay('ready');syncUI();}
function pause(){if(game.mode==='ready'||game.mode==='gameover')return;game.pause();overlay(game.mode==='paused'?'paused':null);syncUI()}
function stageIndex(){return Math.max(0,STAGES.findIndex((s,i)=>i===STAGES.length-1||game.level<STAGES[i+1].from));}
function syncUI(){let layers=game.tower.length-1,stage=game.stage,idx=stageIndex();$('layersValue').innerHTML=String(layers).padStart(2,'0')+' <i>/ ∞</i>';$('scoreValue').textContent=String(game.score).padStart(6,'0');$('stabilityValue').innerHTML=Math.round(game.stability*100)+'<i>%</i>';$('comboValue').innerHTML=String(game.combo).padStart(2,'0')+' <i>CHAIN</i>';$('bestValue').innerHTML=String(Math.max(layers,best.layers)).padStart(2,'0')+' <i>LAYERS</i>';
 $('stageChip').textContent='SECTOR '+String(idx+1).padStart(2,'0')+' // '+stage.name;$('sectorNumber').textContent=String(idx+1).padStart(2,'0')+' / 05';$('sectorName').textContent=stage.name;
 const descriptions=['Establish a stable foundation and deploy the first server layers.','Higher scan velocity demands controlled timing.','Wind pressure begins to affect the falling server blocks.','Keep your precision chain through faster transport cycles.','The final deployment sector. Build upward into the endless zone.'];$('sectorDesc').textContent=descriptions[idx];
 let next=STAGES[idx+1]?.from||Math.max(30,game.level+7);let current=STAGES[idx].from;$('sectorProgress').style.width=(Math.round(clamp((game.level-current)/Math.max(1,next-current),0,1)*100))+'%';$('nextMilestone').textContent=idx===4?'ENDLESS OPERATION // LIVE':'NEXT SECTOR // '+String(next).padStart(2,'0')+' LAYERS';$('sectorStatus').textContent=idx===4?'MAX SECTOR':game.mode==='falling'?'DEPLOYING':'ACTIVE';
 $('widthValue').textContent=game.tower.at(-1).w.toFixed(1)+' U';$('windValue').textContent=Math.abs(game.wind)<1?'CALM':(game.wind>0?'→ ':'← ')+Math.abs(game.wind).toFixed(0)+' U/S²';$('velocityValue').textContent=Math.round(Math.abs(game.moving?.vx||stage.speed))+' U/S';$('accuracyValue').textContent=layers?Math.round(game.lastQuality*100)+'%':'—';$('focusValue').textContent=Math.round(game.focus)+'%';$('focusProgress').style.width=game.focus+'%';
 $('statusLabel').textContent=game.mode==='running'?'SPACE / TAP TO DEPLOY':game.mode==='falling'?'DEPLOYMENT IN PROGRESS':game.mode==='gameover'?'STRUCTURAL FAILURE':game.mode==='paused'?'SIMULATION PAUSED':'AWAITING COMMAND';$('pauseBtn').textContent=game.mode==='paused'?'▶ RESUME':'Ⅱ PAUSE';$('dropBtn').disabled=game.mode==='falling'||game.mode==='paused'||game.mode==='gameover';$('focusBtn').classList.toggle('focused',game.focusHeld&&game.focus>0);
 let secs=Math.floor(game.time);$('events').innerHTML=[...game.events,{message:'SYSTEM READY // '+stage.name,at:0}].slice(0,5).map(v=>`<div><time>${String(Math.floor(v.at/60)).padStart(2,'0')}:${String(Math.floor(v.at%60)).padStart(2,'0')}</time> ${escapeHTML(v.message)}</div>`).join('');
}
function escapeHTML(str){return String(str).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');}
function frame(now){const dt=last?Math.min(.07,(now-last)/1000):0;last=now;acc+=dt;
 let count=0;while(acc>=1/120&&count++<12){const prev=game.tower.length;const state=game.mode;game.update(1/120);if(game.tower.length>prev){const b=game.tower.at(-1);const perfect=game.combo>0;scene.addLand(b.x,b.y+Math.max(0,(game.tower.length-5)*BLOCK_H),perfect);successSound(perfect);showToast(game.events[0]?.message||'SERVER DEPLOYED');lastLength=game.tower.length;
 if(game.tower.length-1>best.layers||(game.tower.length-1===best.layers&&game.score>best.score)){best={layers:game.tower.length-1,score:game.score};try{localStorage.setItem('stack-overflow-score-v1',JSON.stringify(best))}catch{}}
 }
 if(state!=='gameover'&&game.mode==='gameover'&&!ended){ended=true;scene.addFail(game.tower.at(-1).x,game.tower.at(-1).y+Math.max(0,(game.tower.length-5)*BLOCK_H));tone(135,.25,'sawtooth',.035);setTimeout(()=>overlay('gameover'),520);showToast('STRUCTURAL FAILURE');}
 acc-=1/120;}
 scene.tickFx(dt);scene.draw(game);uiWait+=dt;if(uiWait>=.12){syncUI();uiWait=0;}requestAnimationFrame(frame);}
$('startBtn').addEventListener('click',start);$('dropBtn').addEventListener('click',drop);$('gameCanvas').addEventListener('pointerdown',()=>drop());$('pauseBtn').addEventListener('click',pause);$('restartBtn').addEventListener('click',restart);
$('soundBtn').addEventListener('click',()=>{muted=!muted;$('soundBtn').textContent=muted?'◖× SOUND OFF':'◖)) SOUND ON';if(!muted)tone(620)});
$('helpBtn').addEventListener('click',()=>{if(game.mode==='running')pause();$('helpDialog').showModal();});$('helpClose').addEventListener('click',()=>$('helpDialog').close());$('helpPlay').addEventListener('click',()=>{$('helpDialog').close();if(game.mode==='paused')pause();});$('helpDialog').addEventListener('click',e=>{if(e.target===$('helpDialog'))$('helpDialog').close();});
function focus(v){game.toggleFocus(v);$('focusBtn').setAttribute('aria-pressed',String(Boolean(v)));}
$('focusBtn').addEventListener('pointerdown',e=>{e.preventDefault();try{e.currentTarget.setPointerCapture(e.pointerId)}catch{}focus(true)});for(const s of ['pointerup','pointercancel','lostpointercapture','pointerleave'])$('focusBtn').addEventListener(s,()=>focus(false));
document.addEventListener('keydown',e=>{if(document.activeElement?.closest('dialog'))return;const k=e.key.toLowerCase();if([' ','shift'].includes(k))e.preventDefault();if(e.repeat&&k!=='shift')return;if(k===' ')drop();else if(k==='shift')focus(true);else if(k==='p')pause();else if(k==='r')restart();});document.addEventListener('keyup',e=>{if(e.key==='Shift')focus(false)});window.addEventListener('blur',()=>{focus(false);if(game.mode==='running'||game.mode==='falling'){game.pause();overlay('paused');}});
// Pausing a falling server preserves its exact state rather than discarding a committed drop.
// game.pause() handles both run modes through an explicit pause mode stored below.
syncUI();requestAnimationFrame(frame);window.__STACK_DEBUG__={game,scene,drop,restart,pause,start};
