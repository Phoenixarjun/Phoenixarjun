import {FIXED_DT,PLAYER_RADIUS,SECTOR_NAMES,createGame,startGame,update,setLane,jump,slide} from './physics.mjs';
import {RunnerRenderer} from './renderer.js';
import {CanvasFallback} from './fallback.js';
import {SoundEngine} from './audio.js';

const $=s=>document.querySelector(s);
const canvas=$('#game-canvas');let renderer;let bootError=null;
try{renderer=new RunnerRenderer(canvas)}catch(e){console.info('WebGL unavailable; activating perspective Canvas fallback:',e.message);try{renderer=new CanvasFallback(canvas);document.querySelector('.mission-chip small').textContent='PERSPECTIVE CANVAS / REAL-TIME PHYSICS';}catch(err){bootError=err;$('#webgl-warning').hidden=false;$('#start-btn').disabled=true;}}
const sound=new SoundEngine();let game=createGame(0xC1A0);const storageKey='runtime-rush:titanium:v1:highscore';
try{game.highScore=Math.max(0,Number(localStorage.getItem(storageKey)||0)||0)}catch{}
let accumulator=0,lastFrame=performance.now(),feedbackUntil=0,lastHud=0,seconds=0,toastCount=0,lastSaved=0;
const format=n=>Math.max(0,Math.floor(n)).toString().padStart(6,'0');
function ui(){
 $('#score').textContent=format(game.score);$('#side-score').textContent=format(game.score);$('#distance').textContent=Math.floor(game.distance).toString().padStart(4,'0');
 $('#speed-readout').textContent=String(Math.round(game.speed));$('#integrity').textContent=Array.from({length:3},(_,i)=>i<game.integrity?'◈':'◇').join(' ');
 $('#lane-label').textContent='LANE 0'+(game.targetLane+1);$('#shield-state').textContent=game.shield>0?'◈ SHIELD '+Math.ceil(game.shield)+'S':game.slow>0?'◈ OVERCLOCK '+Math.ceil(game.slow)+'S':'◈ SHIELD OFF';
 $('#combo-state').textContent='COMBO ×'+game.combo;$('#side-combo').textContent='× '+String(game.combo).padStart(2,'0');$('#near-misses').textContent=String(game.nearMiss).padStart(2,'0');$('#side-dodged').textContent=String(game.dodged).padStart(2,'0');
 $('#sector-label').textContent=SECTOR_NAMES[game.stage-1];$('#side-sector').textContent=String(game.stage).padStart(2,'0')+' / 05';$('#progress-mini').textContent='SECTOR '+String(game.stage).padStart(2,'0')+' / 05';
 const p=(game.distance%450)/450;$('#progress-fill').style.width=(p*100).toFixed(2)+'%';$('#progress-num').textContent=Math.floor(p*100)+'%';
 $('#best-readout').textContent=format(Math.max(game.highScore,lastSaved));
 $('#status-text').textContent=game.state==='playing'?'PACKET IN TRANSIT':game.state==='menu'?'AWAITING INITIALIZATION':game.state==='paused'?'SIMULATION PAUSED':'PACKET DROPPED';
 $('#pause-btn').textContent=game.state==='paused'?'▶ RESUME':'Ⅱ PAUSE';
}
function feedback(t,duration=1.3){const e=$('#feedback');e.textContent=t;e.classList.add('show');feedbackUntil=seconds+duration;}
function persist(){if(game.highScore>lastSaved){lastSaved=game.highScore;try{localStorage.setItem(storageKey,String(lastSaved))}catch{}}}
function menu(type){const el=$('#screen');el.classList.remove('hidden');if(type==='pause'){$('#overlay-kicker').textContent='SYSTEM SUSPENDED';$('#overlay-title').innerHTML='RUN <em>PAUSED.</em>';$('#overlay-description').textContent='Request state preserved. Resume when ready.';$('#start-btn').innerHTML='RESUME REQUEST <span>↗</span>';}else if(type==='over'){$('#overlay-kicker').textContent='TRANSPORT CONNECTION TERMINATED';$('#overlay-title').innerHTML='PACKET <em>LOST.</em>';$('#overlay-description').textContent=`You travelled ${Math.floor(game.distance)} metres, scored ${format(game.score)}, and reached sector ${String(game.stage).padStart(2,'0')}. Another run?`;$('#start-btn').innerHTML='REINITIALIZE <span>↗</span>';}else{$('#overlay-kicker').textContent='READY TO INITIALIZE';$('#overlay-title').innerHTML='KEEP THE <em>REQUEST</em> ALIVE.';$('#overlay-description').textContent='Dodge corrupted nodes, leap over failed services, slide under security gates, and collect signal energy. How far can your packet travel?';$('#start-btn').innerHTML='INITIATE RUN <span>↗</span>';}}
function startOrResume(){if(bootError)return;if(game.state==='paused'){game.state='playing'}else{const best=game.highScore;startGame(game);game.highScore=Math.max(best,lastSaved);accumulator=0;}$('#screen').classList.add('hidden');canvas.parentElement.focus({preventScroll:true});feedback('CONNECTION ESTABLISHED',1.5);}
function pauseOrResume(){if(game.state==='playing'){game.state='paused';menu('pause')}else if(game.state==='paused')startOrResume();}
$('#start-btn').addEventListener('click',()=>{sound.unlock();startOrResume()});$('#pause-btn').addEventListener('click',pauseOrResume);
$('#mute-btn').addEventListener('click',()=>{$('#mute-btn').textContent='SOUND: '+(sound.toggle()?'ON':'OFF');$('#mute-btn').setAttribute('aria-label',sound.enabled?'Mute sound':'Enable sound')});
const acts={left:()=>setLane(game,-1),right:()=>setLane(game,1),jump:()=>jump(game),slide:()=>slide(game)};
for(const [name,fun] of Object.entries(acts)){$('#'+name+'-btn').addEventListener('pointerdown',e=>{e.preventDefault();fun();const button=e.currentTarget;button.classList.add('is-pressed');setTimeout(()=>button.classList.remove('is-pressed'),120)});}
window.addEventListener('keydown',e=>{const k=e.key.toLowerCase(),focus=e.target;if(focus&&(/input|textarea|select/i.test(focus.tagName)||focus.isContentEditable))return;
 if(['arrowleft','arrowright','arrowup','arrowdown',' ','w','a','s','d','p','escape','enter','m','r'].includes(k))e.preventDefault();
 if(k==='arrowleft'||k==='a')acts.left();if(k==='arrowright'||k==='d')acts.right();if(k==='arrowup'||k==='w'||k===' ')acts.jump();if(k==='arrowdown'||k==='s')acts.slide();
 if(k==='p'||k==='escape')pauseOrResume();if(k==='enter'&&game.state!=='playing')startOrResume();if(k==='m')$('#mute-btn').click();if(k==='r'&&game.state==='over')startOrResume();});
let startPointer=null;
canvas.addEventListener('pointerdown',e=>{startPointer={x:e.clientX,y:e.clientY,id:e.pointerId};try{canvas.setPointerCapture(e.pointerId)}catch{}});
canvas.addEventListener('pointerup',e=>{if(!startPointer)return;const dx=e.clientX-startPointer.x,dy=e.clientY-startPointer.y;startPointer=null;if(Math.abs(dx)>36&&Math.abs(dx)>Math.abs(dy)*.7){acts[dx>0?'right':'left']();}else if(dy < -36){acts.jump()}else if(dy>36){acts.slide()}else if(game.state==='playing'){acts.jump()}});
window.addEventListener('blur',()=>{if(game.state==='playing'){game.state='paused';menu('pause')}});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&game.state==='playing'){game.state='paused';menu('pause')}});
function processEvents(){for(const ev of game.events){sound.play(ev);switch(ev.type){case 'pickup':feedback(ev.kind==='shield'?'SHIELD ONLINE':ev.kind==='overclock'?'OVERCLOCK ENGAGED':'SIGNAL ENERGY +150',1.1);break;case 'damage':feedback('SYSTEM FAILURE · INTEGRITY '+ev.integrity,1.7);break;case 'shieldbreak':feedback('SHIELD ABSORBED IMPACT',1.3);break;case 'sector':feedback('SECTOR '+String(ev.sector).padStart(2,'0')+' // '+SECTOR_NAMES[ev.sector-1],2);break;case 'nearmiss':feedback('NEAR MISS +45',.8);break;case 'gameover':persist();menu('over');break;}}game.events.length=0;}
function loop(now){const delta=Math.min(.05,Math.max(0,(now-lastFrame)/1000));lastFrame=now;seconds+=delta;
 if(game.state==='playing'){accumulator+=delta;let n=0;while(accumulator>=FIXED_DT&&n++<12){update(game,FIXED_DT);accumulator-=FIXED_DT;processEvents();if(game.state==='over')break;}if(n>=12)accumulator=0;}
 if(renderer){renderer.render(game,seconds);}if(now-lastHud>90){ui();lastHud=now;}
 if(seconds>feedbackUntil)$('#feedback').classList.remove('show');requestAnimationFrame(loop);}
menu('menu');ui();requestAnimationFrame(loop);
window.__RUNTIME_RUSH_DEBUG__={getState:()=>({state:game.state,distance:game.distance,score:game.score,integrity:game.integrity,items:game.items.length,stage:game.stage,x:game.x,y:game.y}),start:()=>startOrResume(),left:acts.left,right:acts.right,jump:acts.jump,slide:acts.slide,forceDamage:()=>{game.integrity=Math.max(0,game.integrity-1);if(game.integrity===0){game.state='over';menu('over')}}};
