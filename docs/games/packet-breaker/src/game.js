import {clamp,length,reflect,sweepCircleAABB,sweepWall,paddleBounce,stabiliseVelocity,testOverlapCircleRect} from './physics.mjs';

// PACKET BREAKER: standalone, local-only canvas arcade. No external assets or analytics.
const W=1000,H=680, STEP=1/120, MAX_FRAME=.05;
const COL={lime:'#B6FF3B',ice:'#d4fff1',mint:'#88dbaa',aqua:'#55e1cb',steel:'#42535C',warning:'#ffc56c',danger:'#ff6e71',paper:'#EEF7EF'};
const $=id=>document.getElementById(id);
const canvas=$('gameCanvas'),ctx=canvas.getContext('2d',{alpha:false});
if(!ctx) throw new Error('Packet Breaker requires a Canvas 2D context');
const arena=$('arenaFrame'),overlay=$('overlay'),toastEl=$('eventToast');
const UI={score:$('score'),best:$('best'),level:$('levelStat'),lives:$('lives'),combo:$('combo'),status:$('status'),remaining:$('remaining'),velocity:$('velocity'),shield:$('shieldState'),message:$('message'),stageDescription:$('stageDescription'),arenaLabel:$('arenaLabel'),pause:$('pauseBtn'),sound:$('soundBtn'),primary:$('primaryAction'),restart:$('restartBtn')};
let audio=null;
const sound={enabled:true,playing:false,beep(freq=440,seconds=.09,type='sine',vol=.025){
  if(!this.enabled)return;try{const C=window.AudioContext||window.webkitAudioContext;if(!C)return;audio??=new C();if(audio.state==='suspended')audio.resume();const t=audio.currentTime,o=audio.createOscillator(),g=audio.createGain();o.type=type;o.frequency.setValueAtTime(freq,t);o.frequency.exponentialRampToValueAtTime(Math.max(70,freq*.65),t+seconds);g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(vol,t+.015);g.gain.exponentialRampToValueAtTime(.0001,t+seconds);o.connect(g);g.connect(audio.destination);o.start(t);o.stop(t+seconds+.01);}catch{/* sound is nonessential */}
}};
const safeBest=()=>{try{return Math.max(0,parseInt(localStorage.getItem('packetbreaker.best.v1')||'0',10)||0);}catch{return 0;}};
const saveBest=(s)=>{try{localStorage.setItem('packetbreaker.best.v1',String(s));}catch{/* private mode is okay */}};
const game={mode:'menu',score:0,best:safeBest(),lives:3,level:1,comboHits:0,clock:0,shake:0,flash:0,statsTimer:0,toastTimer:0,paddle:{x:W/2,y:614,w:152,h:17,target:W/2,vx:0,expandUntil:0},balls:[],bricks:[],drops:[],particles:[],floats:[],shields:0,slowUntil:0,nextId:0,prevInputs:{left:false,right:false},reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches};
const rng=(seed)=>()=>{seed=(Math.imul(seed,1664525)+1013904223)|0;return(seed>>>0)/4294967296;};
const rand=rng(908132);
const randRange=(a,b)=>a+(b-a)*rand();
const stages=[
  {name:'BOOT SEQUENCE',detail:'Clear your first fault domain.',rows:5,cols:9,baseSpeed:425},
  {name:'QUEUE STORM',detail:'Pressure builds across the message bus.',rows:6,cols:9,baseSpeed:460},
  {name:'LOAD BALANCER',detail:'Keep the network responsive.',rows:6,cols:10,baseSpeed:490},
  {name:'FAULT DOMAIN',detail:'Redundant systems. Fragile links.',rows:7,cols:10,baseSpeed:515},
  {name:'KERNEL PANIC',detail:'Recover the core before the network collapses.',rows:7,cols:11,baseSpeed:550}
];
const stage=()=>stages[Math.min(game.level-1,stages.length-1)];
let pointerTarget=null;
let announceTimeout=0;
function announce(msg,color=COL.lime){toastEl.textContent=msg;toastEl.style.color=color;toastEl.classList.add('visible');game.toastTimer=1.35;UI.message.textContent=msg;}
function pointToCanvas(clientX){const rect=canvas.getBoundingClientRect();return clamp((clientX-rect.left)*(W/rect.width),0,W);}
const powder=(x,y,color,count=12,power=170)=>{if(game.reducedMotion)count=Math.min(count,4);for(let i=0;i<count;i++){const a=randRange(0,Math.PI*2),speed=randRange(power*.2,power);game.particles.push({x,y,vx:Math.cos(a)*speed,vy:Math.sin(a)*speed,age:0,life:randRange(.22,.64),r:randRange(1.2,3.4),color});}if(game.particles.length>260)game.particles.splice(0,game.particles.length-260);};
const floatText=(x,y,text,color=COL.lime)=>{game.floats.push({x,y,text,color,age:0,life:.85});if(game.floats.length>36)game.floats.shift();};
function updateBest(){if(game.score>game.best){game.best=game.score;saveBest(game.best);}}
function addScore(amount,x,y){const points=Math.floor(amount*(1+Math.min(3,Math.max(0,game.comboHits-1)*.16)));game.score+=points;updateBest();floatText(x,y,`+${points}`,game.comboHits>=7?COL.lime:COL.mint);}
function buildStage(){
  const d=stage(),n=d.cols,gap=8,avail=W-105,cw=(avail-(n-1)*gap)/n,ch=34,startX=(W-avail)/2,startY=113;game.bricks=[];
  const random=rng(87401+game.level*1907);
  for(let row=0;row<d.rows;row++) for(let col=0;col<n;col++){
    let present=true;
    if(game.level===1) present=(row===0||row===d.rows-1||col%2===0||random()>.15);
    else if(game.level===2)present=(col+row)%5!==0;
    else if(game.level===3)present=(Math.abs(col-(n-1)/2)<3 || row%2===0 || random()>.32);
    else if(game.level===4)present=(row+col)%7!==2;
    else if(game.level===5)present=(row<=1 || Math.abs(col-(n-1)/2)>1 || row%3===0);
    else present=random()>.1;
    if(!present)continue;
    let kind='normal',hp=1;
    if((row<2&&game.level>1&&random()<.5)||(game.level>=4&&random()<.2)){kind='reinforced';hp=Math.min(4,2+Math.floor(game.level/4));}
    if(row>0&&random()<.10){kind='volatile';hp=1;}
    if(game.level>=5&&row===0&&Math.abs(col-(n-1)/2)<1){kind='core';hp=3+Math.floor((game.level-5)/4);}
    const b={id:++game.nextId,x:startX+col*(cw+gap),y:startY+row*42,w:cw,h:ch,hp,maxHp:hp,kind,row,col,flash:0,dead:false};game.bricks.push(b);
  }
  UI.arenaLabel.textContent=`STAGE ${String(game.level).padStart(2,'0')} — ${d.name}`;
  UI.stageDescription.textContent=`STAGE ${String(game.level).padStart(2,'0')} // ${d.name}`;
}
function makeBall(x,y,vx,vy,stuck=false){return{id:++game.nextId,x,y,vx,vy,r:8.4,trail:[],stuck,age:0};}
function resetBalls(stuck=true){const p=game.paddle;game.balls=[makeBall(p.x,p.y-22,180,-stage().baseSpeed,stuck)];}
function launch(){if(game.mode!=='ready')return;game.mode='playing';for(const b of game.balls){if(b.stuck){b.stuck=false;b.vx=stage().baseSpeed*.35;b.vy=-Math.sqrt(stage().baseSpeed**2-b.vx**2);}}announce('PACKET DEPLOYED');sound.beep(570,.11,'triangle',.032);updateUI();}
function startRun(){game.score=0;game.lives=3;game.level=1;game.comboHits=0;game.clock=0;game.shields=0;game.slowUntil=0;game.paddle.w=152;game.paddle.x=W/2;game.paddle.target=W/2;pointerTarget=null;game.drops=[];game.floats=[];game.particles=[];buildStage();resetBalls(true);hideOverlay();game.mode='ready';announce('MOVE PADDLE · TAP OR SPACE TO LAUNCH');updateUI();}
function startLevel(){game.comboHits=0;game.slowUntil=0;game.paddle.w=152;game.paddle.expandUntil=0;game.drops=[];game.particles=[];game.floats=[];buildStage();resetBalls(true);hideOverlay();game.mode='ready';announce(`STAGE ${String(game.level).padStart(2,'0')} READY`);updateUI();}
function showOverlay({icon='⬡',kicker,title,description,button,tip='PRESS ENTER TO CONTINUE',tags=[]}){
  $('overlayIcon').textContent=icon;$('overlayKicker').textContent=kicker;$('overlayTitle').innerHTML=title;$('overlayDescription').textContent=description;
  $('overlayTags').replaceChildren(...tags.map(t=>{const e=document.createElement('span');e.textContent=t;return e;}));
  UI.primary.textContent=button;const arr=document.createElement('span');arr.textContent=' ↗';arr.setAttribute('aria-hidden','true');UI.primary.append(arr);$('overlayKeytip').textContent=tip;overlay.classList.remove('hidden');
}
function hideOverlay(){overlay.classList.add('hidden');}
function setPaused(paused){if(paused){if(game.mode==='playing'||game.mode==='ready'){game.wasReady=game.mode==='ready';game.mode='paused';showOverlay({icon:'Ⅱ',kicker:'PROCESS SUSPENDED',title:'SYSTEM <em>PAUSED</em>',description:'All packets and simulations are safely suspended. Resume whenever you are ready.',button:'RESUME SESSION',tags:['PROGRESS SAVED IN MEMORY']});}}else if(game.mode==='paused'){game.mode=game.wasReady?'ready':'playing';hideOverlay();}updateUI();}
function nextAction(){if(game.mode==='menu'||game.mode==='gameover')startRun();else if(game.mode==='paused')setPaused(false);else if(game.mode==='levelClear'){game.level++;startLevel();}else if(game.mode==='victory'){game.level++;startLevel();}else if(game.mode==='ready')launch();}
function levelClear(){if(game.mode!=='playing')return;game.mode=game.level>=5&&game.level===5?'victory':'levelClear';const bonus=game.lives*500+game.shields*150;game.score+=bonus;updateBest();sound.beep(740,.25,'triangle',.04);sound.beep(1030,.45,'triangle',.028);powder(W/2,H/3,COL.lime,90,350);
  if(game.mode==='victory')showOverlay({icon:'✧',kicker:'NETWORK RESTORED · ALL FIVE STAGES CLEARED',title:'SYSTEM <em>STABLE.</em>',description:`Final score: ${game.score.toLocaleString()}. You survived the network. Endless mode is now available.`,button:'ENTER ENDLESS MODE',tip:'PRESS ENTER FOR ENDLESS MODE',tags:[`SCORE ${game.score.toLocaleString()}`,`SURVIVAL BONUS +${bonus}`]});
  else showOverlay({icon:'◇',kicker:'FAULT DOMAIN CLEARED',title:'STAGE <em>COMPLETE</em>',description:`${stage().name} resolved. Earned +${bonus} survival bonus. Next stage increases packet speed and fault tolerance.`,button:'NEXT STAGE',tags:[`SCORE ${game.score.toLocaleString()}`,`BONUS +${bonus}`,`LIVES ${game.lives}`]});updateUI();}
function gameOver(){game.mode='gameover';sound.beep(150,.6,'sawtooth',.025);showOverlay({icon:'✕',kicker:'CONNECTION TERMINATED',title:'PACKET <em>LOST.</em>',description:`You scored ${game.score.toLocaleString()} points and reached stage ${game.level}. Retry to restore the network.`,button:'RESTART RUN',tags:[`FINAL SCORE ${game.score.toLocaleString()}`,`BEST ${game.best.toLocaleString()}`]});updateUI();}
function lostBall(ball){if(game.shields>0){game.shields--;ball.y=H-55;ball.vy=-Math.abs(ball.vy);ball.vx*=.88;game.shake=6;powder(ball.x,H-42,COL.lime,25,230);announce('FIREWALL BLOCKED PACKET LOSS');sound.beep(650,.16);return false;}return true;}
const POWER=['CACHE','CLONE','FIREWALL','SLOW'];
function spawnDrop(x,y){const type=POWER[Math.floor(rand()*POWER.length)];game.drops.push({x,y,vy:95+game.level*5,type,r:14,phase:randRange(0,6)});}
function applyPower(type){sound.beep(900,.13,'triangle',.045);if(type==='CACHE'){game.paddle.w=210;game.paddle.expandUntil=game.clock+14;announce('CACHE BOOST // PADDLE EXPANDED');}
 else if(type==='CLONE'){const alive=game.balls.filter(b=>!b.stuck);for(const b of alive.slice(0,2)){if(game.balls.length>=6)break;const speed=length(b.vx,b.vy);const angle=Math.atan2(b.vy,b.vx);for(const rot of [-.35,.35]){if(game.balls.length>=6)break;const a=angle+rot;game.balls.push(makeBall(b.x+randRange(-3,3),b.y,Math.cos(a)*speed,Math.sin(a)*speed));}}announce('PACKET CLONED // MULTI-BALL');}
 else if(type==='FIREWALL'){game.shields=Math.min(3,game.shields+1);announce('FIREWALL CHARGED // +1 SAVE');}
 else if(type==='SLOW'){if(game.clock>=game.slowUntil){for(const b of game.balls){b.vx*=.76;b.vy*=.76;}}game.slowUntil=game.clock+11;announce('TIME DILATION // 11 SECONDS');}powder(game.paddle.x,game.paddle.y,COL.lime,18,190);}
function handleBrickHit(brick,impactX,impactY){brick.flash=1;brick.hp--;game.comboHits++;game.shake=Math.min(8,game.shake+1.8);game.flash=Math.max(game.flash,.1);const color=brick.kind==='volatile'?COL.warning:brick.kind==='core'?COL.aqua:COL.lime;
  if(brick.hp>0){addScore(28,impactX,impactY);powder(impactX,impactY,COL.ice,7,110);sound.beep(215+Math.min(game.comboHits,15)*24,.055,'triangle',.022);return;}
  brick.dead=true;addScore(brick.kind==='core'?300:brick.kind==='reinforced'?160:100,brick.x+brick.w/2,brick.y+brick.h/2);
  powder(brick.x+brick.w/2,brick.y+brick.h/2,color,15,190);sound.beep(340+Math.min(game.comboHits,16)*24,.075,'triangle',.018);
  if(rand()<.15)spawnDrop(brick.x+brick.w/2,brick.y+brick.h/2);
  if(brick.kind==='volatile'){const radius=brick.w*1.45;for(const other of game.bricks){if(other.dead||other.id===brick.id)continue;const dist=length(other.x+other.w/2-(brick.x+brick.w/2),other.y+other.h/2-(brick.y+brick.h/2));if(dist<radius){other.hp=0;other.dead=true;addScore(80,other.x+other.w/2,other.y+other.h/2);powder(other.x+other.w/2,other.y+other.h/2,COL.warning,9,140);}}game.shake=9;announce('CHAIN REACTION');}
  if(game.bricks.every(b=>b.dead))levelClear();
}
function updatePaddle(dt){const p=game.paddle,old=p.x;const key=(game.prevInputs.right?1:0)-(game.prevInputs.left?1:0);
 if(key) {pointerTarget=null;p.target=clamp(p.target+key*730*dt,p.w/2+15,W-p.w/2-15);}
 else if(pointerTarget!=null)p.target=clamp(pointerTarget,p.w/2+15,W-p.w/2-15);
 const maxMove=1450*dt;p.x+=clamp(p.target-p.x,-maxMove,maxMove);
 p.x=clamp(p.x,p.w/2+15,W-p.w/2-15);p.vx=(p.x-old)/dt;
 if(p.expandUntil&&game.clock>p.expandUntil){p.expandUntil=0;p.w=152;p.target=clamp(p.target,p.w/2+15,W-p.w/2-15);announce('CACHE BOOST EXPIRED');}
}
function stepBall(ball,dt){ball.age+=dt;
 if(ball.stuck){ball.x=game.paddle.x;ball.y=game.paddle.y-21;return;}
 let remaining=dt,collisionCount=0;
 while(remaining>1e-6&&collisionCount++<7){
  const dx=ball.vx*remaining,dy=ball.vy*remaining;
  let hit=null;const add=(t,nx,ny,type,other)=>{if(t==null||t<0||t>1)return;if(!hit||t<hit.t)hit={t,nx,ny,type,other};};
  add(sweepWall(ball.x,dx,ball.r,1),1,0,'wall');add(sweepWall(ball.x,dx,W-ball.r,-1),-1,0,'wall');add(sweepWall(ball.y,dy,55+ball.r,1),0,1,'wall');
  if(ball.vy>0&&ball.y<=game.paddle.y+game.paddle.h+ball.r){const p=game.paddle;const h=sweepCircleAABB(ball.x,ball.y,dx,dy,ball.r,{x:p.x-p.w/2,y:p.y,w:p.w,h:p.h});if(h&&h.ny<0)add(h.t,h.nx,h.ny,'paddle',p);}
  for(const b of game.bricks){if(b.dead)continue;const h=sweepCircleAABB(ball.x,ball.y,dx,dy,ball.r,b);if(h)add(h.t,h.nx,h.ny,'brick',b);}
  if(!hit){ball.x+=dx;ball.y+=dy;break;}
  ball.x+=dx*hit.t;ball.y+=dy*hit.t;
  if(hit.type==='paddle'){
    const p=hit.other,relative=clamp((ball.x-p.x)/(p.w/2),-1,1),speed=clamp(length(ball.vx,ball.vy)*1.008,330,790+game.level*15);
    const b=paddleBounce(relative,p.vx,speed);ball.vx=b.vx;ball.vy=b.vy;ball.y=p.y-ball.r-.2;game.comboHits=0;powder(ball.x,p.y,COL.lime,8,130);sound.beep(210,.08,'triangle',.026);
  } else {
    const v=reflect(ball.vx,ball.vy,hit.nx,hit.ny);ball.vx=v.x;ball.vy=v.y;
    ball.x+=hit.nx*.18;ball.y+=hit.ny*.18;
    if(hit.type==='brick')handleBrickHit(hit.other,ball.x,ball.y);
    else sound.beep(135,.04,'sine',.008);
  }
  const cap=790+game.level*15;
  const stable=stabiliseVelocity(ball.vx,ball.vy,330,cap,.21);ball.vx=stable.vx;ball.vy=stable.vy;
  remaining*=1-hit.t;
  if(hit.t<.001)remaining=Math.max(0,remaining-.000015);
  if(game.mode!=='playing')break;
 }
 if(ball.y>H+ball.r+3)ball.lost=true;
 ball.trail.unshift({x:ball.x,y:ball.y});if(ball.trail.length>17)ball.trail.pop();
}
function fixedUpdate(dt){game.clock+=dt;game.flash=Math.max(0,game.flash-dt*2.5);game.shake=Math.max(0,game.shake-dt*35);
 for(const b of game.bricks)b.flash=Math.max(0,b.flash-dt*3);
 for(const p of game.particles){p.age+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vx*=.978;p.vy=p.vy*.978+70*dt;}game.particles=game.particles.filter(p=>p.age<p.life);
 for(const f of game.floats){f.age+=dt;f.y-=32*dt;}game.floats=game.floats.filter(f=>f.age<f.life);
 if(game.toastTimer>0){game.toastTimer-=dt;if(game.toastTimer<=0)toastEl.classList.remove('visible');}
 if(game.mode!=='playing'&&game.mode!=='ready')return;
 updatePaddle(dt);
 if(game.mode==='playing'){
  if(game.slowUntil&&game.clock>game.slowUntil){game.slowUntil=0;for(const b of game.balls){b.vx*=1/.76;b.vy*=1/.76;}announce('TIME DILATION ENDED');}
  for(const b of [...game.balls]){if(game.mode==='playing')stepBall(b,dt);}
  if(game.mode!=='playing')return;
  for(const b of game.balls.filter(b=>b.lost)){if(!lostBall(b)){b.lost=false;}else game.balls.splice(game.balls.indexOf(b),1);}
  if(game.balls.length===0){game.lives--;game.comboHits=0;game.shake=12;game.flash=.3;sound.beep(145,.35,'sawtooth',.024);
    if(game.lives<=0){gameOver();return;}game.mode='ready';resetBalls(true);announce('PACKET LOST // SPACE TO REDEPLOY',COL.warning);
  }
  for(const d of game.drops){d.y+=d.vy*dt;d.phase+=dt*4;
    if(testOverlapCircleRect(d.x,d.y,d.r,{x:game.paddle.x-game.paddle.w/2,y:game.paddle.y,w:game.paddle.w,h:game.paddle.h})){d.dead=true;applyPower(d.type);}}
  game.drops=game.drops.filter(d=>!d.dead&&d.y<H+30);
 }else for(const b of game.balls){b.x=game.paddle.x;b.y=game.paddle.y-21;}
}
function roundRect(x,y,w,h,r,fill,stroke,width=1){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke();}}
function line(x1,y1,x2,y2,color,width=1){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function drawBackground(t){
  const grad=ctx.createLinearGradient(0,0,W,H);grad.addColorStop(0,'#0c1717');grad.addColorStop(.52,'#061012');grad.addColorStop(1,'#071011');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
  const bloom=ctx.createRadialGradient(500,200,15,500,230,660);bloom.addColorStop(0,'#21402a30');bloom.addColorStop(.55,'#12332813');bloom.addColorStop(1,'transparent');ctx.fillStyle=bloom;ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='#24423c4a';ctx.lineWidth=.5;
  for(let x=26;x<W;x+=42){line(x,55,x,H-27,'#27464023',.6);}for(let y=66;y<H-30;y+=42)line(0,y,W,y,'#27464020',.6);
  // Technical corner crosshairs and atmospheric particles.
  for(let i=0;i<90;i++){const x=(i*231.41+33)%W,y=(i*313.8+47)%H;if(y<52||y>H-37)continue;const alpha=.07+.06*Math.sin(t*.42+i);ctx.fillStyle=`rgba(182,255,59,${Math.max(.03,alpha)})`;ctx.fillRect(x,y,1.5,1.5);}
  const glow=ctx.createLinearGradient(0,H-80,0,H);glow.addColorStop(0,'transparent');glow.addColorStop(1,'#b6ff3b0d');ctx.fillStyle=glow;ctx.fillRect(0,H-85,W,85);
  line(14,55,W-14,55,'#45625456',1);
  ctx.font='700 10px monospace';ctx.fillStyle='#6e8e87';ctx.fillText('NODE_GRID // REV 4.2',28,77);
  ctx.textAlign='right';ctx.fillText('LIVE / '+(game.mode==='paused'?'SUSPENDED':'SIMULATED'),W-27,77);ctx.textAlign='left';
  // scan strip at bottom.
  line(20,H-30,W-20,H-30,'#4058507e',1);
  for(let x=35;x<965;x+=45)line(x,H-31,x+11,H-31,'#a1cf4948',1.3);
  ctx.save();ctx.font='900 120px sans-serif';ctx.textAlign='center';ctx.fillStyle='#b6ff3b06';ctx.fillText(String(game.level).padStart(2,'0'),W/2,480);ctx.restore();
}
function brickColor(b){if(b.kind==='volatile')return {t:'#c5e5ad',edge:COL.warning,fill:'#293226',shade:'#131d1c'};if(b.kind==='core')return{t:'#cff9f0',edge:COL.aqua,fill:'#203838',shade:'#0a2025'};if(b.kind==='reinforced')return{t:'#c1dfc9',edge:'#8daea2',fill:'#263137',shade:'#111b20'};return{t:'#b8f5a0',edge:COL.lime,fill:'#203129',shade:'#0f211c'};}
function drawBrick(b,t){if(b.dead)return;const{x,y,w,h}=b,c=brickColor(b);ctx.save();
  if(b.flash>0){ctx.shadowColor=c.edge;ctx.shadowBlur=22*b.flash;}
  const top=ctx.createLinearGradient(x,y,x,y+h);top.addColorStop(0,b.flash>0?'#a9ff77':c.fill);top.addColorStop(1,c.shade);
  roundRect(x,y,w,h,5,top,'#5b7b68'+(b.flash>.1?'ff':'aa'),1);
  // Isometric top/face facets
  ctx.beginPath();ctx.moveTo(x+5,y+2);ctx.lineTo(x+w-8,y+2);ctx.lineTo(x+w-14,y+7);ctx.lineTo(x+11,y+7);ctx.closePath();ctx.fillStyle=c.edge+'30';ctx.fill();
  line(x+8,y+3,x+w-19,y+3,c.edge,1.5);
  line(x+w-3,y+11,x+w-3,y+h-5,c.edge+'55',1.4);
  ctx.shadowBlur=0;ctx.fillStyle=c.edge;ctx.fillRect(x+8,y+h-8,Math.max(10,(w-16)*(b.hp/b.maxHp)),2);
  if(b.kind==='reinforced'||b.kind==='core'){ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#c8ebdb';ctx.font='900 12px monospace';ctx.fillText(b.kind==='core'?'CORE':`x${b.hp}`,x+w/2,y+h/2);}
  if(b.kind==='volatile'){ctx.fillStyle=COL.warning;ctx.beginPath();ctx.arc(x+w-16,y+14,4,0,Math.PI*2);ctx.fill();line(x+w-26,y+14,x+w-21,y+14,COL.warning,1);}
  ctx.restore();}
function drawPaddle(){const p=game.paddle,x=p.x-p.w/2,y=p.y,w=p.w,h=p.h;ctx.save();ctx.shadowColor=COL.lime;ctx.shadowBlur=23;
 const lg=ctx.createLinearGradient(0,y,0,y+h);lg.addColorStop(0,'#e2ffaf');lg.addColorStop(.28,'#b6ff3b');lg.addColorStop(.51,'#38632c');lg.addColorStop(1,'#101f1a');roundRect(x,y,w,h,8,lg,'#d8ff92',1.6);
 ctx.shadowBlur=0;roundRect(x+10,y+4,w-20,3,2,'#f8ffdaaa');ctx.fillStyle='#a2ff54';ctx.fillRect(x+w/2-17,y+12,34,2);
 ctx.strokeStyle='#b6ff3b30';ctx.beginPath();ctx.ellipse(p.x,p.y+18,p.w*.8,11,0,0,Math.PI*2);ctx.stroke();
 if(game.shields>0){line(x-3,y-16,x+w+3,y-16,'#b6ff3b7b',2);for(let i=0;i<game.shields;i++){ctx.beginPath();ctx.arc(p.x+(i-1)*17,y-17,4,0,Math.PI*2);ctx.fillStyle=COL.lime;ctx.fill();}}
 ctx.restore();}
function drawBall(b){ctx.save();for(let i=b.trail.length-1;i>=0;i--){const q=b.trail[i],k=1-i/b.trail.length;ctx.globalAlpha=k*k*.5;ctx.fillStyle=COL.lime;ctx.beginPath();ctx.arc(q.x,q.y,b.r*(.15+.62*k),0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;
 ctx.shadowColor=COL.lime;ctx.shadowBlur=25;const g=ctx.createRadialGradient(b.x-2.5,b.y-3,1,b.x,b.y,b.r*1.7);g.addColorStop(0,'#fff');g.addColorStop(.25,'#e4ffd9');g.addColorStop(.56,'#b6ff3b');g.addColorStop(1,'#7ac13f00');ctx.fillStyle=g;ctx.beginPath();ctx.arc(b.x,b.y,b.r*1.65,0,Math.PI*2);ctx.fill();ctx.fillStyle='#f5ffda';ctx.beginPath();ctx.arc(b.x,b.y,b.r*.47,0,Math.PI*2);ctx.fill();ctx.restore();}
function drawDrop(d,t){ctx.save();ctx.translate(d.x,d.y);const s=1+Math.sin(d.phase)*.08;ctx.scale(s,s);ctx.rotate(Math.PI/4);ctx.shadowBlur=13;ctx.shadowColor=COL.lime;roundRect(-12,-12,24,24,5,'#243527',COL.lime,2);ctx.restore();ctx.textAlign='center';ctx.font='900 12px monospace';ctx.fillStyle='#edffd6';ctx.fillText(({CACHE:'↔',CLONE:'Ⅱ',FIREWALL:'◆',SLOW:'◷'})[d.type],d.x,d.y+5);ctx.textAlign='left';}
function drawParticles(){for(const p of game.particles){const fade=Math.max(0,1-p.age/p.life);ctx.globalAlpha=fade;ctx.fillStyle=p.color;ctx.fillRect(p.x-p.r/2,p.y-p.r/2,p.r,p.r);}ctx.globalAlpha=1;for(const f of game.floats){ctx.globalAlpha=1-f.age/f.life;ctx.font='900 17px monospace';ctx.textAlign='center';ctx.fillStyle=f.color;ctx.fillText(f.text,f.x,f.y);}ctx.globalAlpha=1;ctx.textAlign='left';}
function render(t){const px=window.devicePixelRatio?Math.min(window.devicePixelRatio,2):1;const expectedW=Math.round(W*px),expectedH=Math.round(H*px);if(canvas.width!==expectedW||canvas.height!==expectedH){canvas.width=expectedW;canvas.height=expectedH;}ctx.setTransform(px,0,0,px,0,0);ctx.save();ctx.clearRect(0,0,W,H);
 if(game.shake>0&&!game.reducedMotion)ctx.translate(randRange(-game.shake,game.shake),randRange(-game.shake,game.shake));
 drawBackground(t);for(const b of game.bricks)drawBrick(b,t);for(const d of game.drops)drawDrop(d,t);drawPaddle();for(const b of game.balls)drawBall(b);drawParticles();
 if(game.flash>0){ctx.fillStyle=`rgba(193,255,105,${game.flash*.07})`;ctx.fillRect(0,0,W,H);}ctx.restore();}
function fmt(n){return String(n).padStart(6,'0');}
function updateUI(){UI.score.textContent=fmt(game.score);UI.best.textContent=fmt(game.best);UI.level.innerHTML=`${String(game.level).padStart(2,'0')} <small>/ ${game.level>5?'∞':'05'}</small>`;UI.lives.textContent='◆ '.repeat(Math.max(0,game.lives)).trim()||'✕';UI.lives.setAttribute('aria-label',`${game.lives} lives`);
 UI.combo.textContent=`x${(1+Math.min(3,Math.max(0,game.comboHits-1)*.16)).toFixed(1)}`;
 UI.status.textContent=({menu:'STANDBY',ready:'READY',playing:'ONLINE',paused:'PAUSED',levelClear:'CLEARED',victory:'COMPLETE',gameover:'OFFLINE'})[game.mode]||'STANDBY';
 UI.remaining.textContent=String(game.bricks.filter(b=>!b.dead).length);UI.velocity.textContent=`${Math.round(game.balls.length?length(game.balls[0].vx,game.balls[0].vy):0)} PX/S`;
 UI.shield.textContent=game.shields?`${game.shields} CHARGE${game.shields!==1?'S':''}`:'OFFLINE';
 UI.pause.disabled=['menu','gameover','levelClear','victory'].includes(game.mode);UI.pause.innerHTML=game.mode==='paused'?'▶ <span>RESUME</span>':'Ⅱ <span>PAUSE</span>';
 UI.sound.innerHTML=sound.enabled?'♫ <span>SOUND ON</span>':'♪ <span>SOUND OFF</span>';
}
let last=0,acc=0,lastUI=0;
function frame(ms){if(!last)last=ms;const delta=Math.min(MAX_FRAME,(ms-last)/1000);last=ms;
 if(game.mode!=='paused')acc+=delta;else acc=0;
 let loops=0;while(acc>=STEP&&loops++<9){fixedUpdate(STEP);acc-=STEP;}if(loops>=9)acc=0;
 render(ms/1000);if(ms-lastUI>120){updateUI();lastUI=ms;}requestAnimationFrame(frame);}
function clickArena(e){if(e.pointerType==='mouse'&&e.button!==0)return;pointerTarget=pointToCanvas(e.clientX);game.paddle.target=pointerTarget;if(game.mode==='ready')launch();}
canvas.addEventListener('pointermove',e=>{if(e.pointerType==='touch'&&e.buttons===0)return;pointerTarget=pointToCanvas(e.clientX);});
canvas.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'){e.preventDefault();}clickArena(e);});
canvas.addEventListener('pointerup',e=>{if(e.pointerType==='touch')e.preventDefault();});
window.addEventListener('keydown',e=>{const tag=e.target?.tagName;if(['INPUT','TEXTAREA','SELECT'].includes(tag))return;
 if(['ArrowLeft','ArrowRight','Space'].includes(e.code))e.preventDefault();
 if(e.code==='ArrowLeft'||e.code==='KeyA'){game.prevInputs.left=true;pointerTarget=null;}
 if(e.code==='ArrowRight'||e.code==='KeyD'){game.prevInputs.right=true;pointerTarget=null;}
 if(e.repeat)return;
 if(e.code==='Space'){if(game.mode==='ready')launch();else if(game.mode==='menu'||game.mode==='levelClear'||game.mode==='victory'||game.mode==='gameover')nextAction();}
 if(e.code==='KeyP'||e.code==='Escape'){if(game.mode==='paused')setPaused(false);else setPaused(true);}
 if(e.code==='Enter'&&!overlay.classList.contains('hidden'))nextAction();
});
window.addEventListener('keyup',e=>{if(e.code==='ArrowLeft'||e.code==='KeyA')game.prevInputs.left=false;if(e.code==='ArrowRight'||e.code==='KeyD')game.prevInputs.right=false;});
window.addEventListener('blur',()=>{game.prevInputs.left=false;game.prevInputs.right=false;if(game.mode==='playing')setPaused(true);});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&game.mode==='playing')setPaused(true);});
UI.primary.addEventListener('click',nextAction);
UI.pause.addEventListener('click',()=>{if(game.mode==='paused')setPaused(false);else setPaused(true);});
UI.restart.addEventListener('click',()=>{if(game.mode==='menu')startRun();else {const ok=game.mode==='gameover'||game.mode==='victory'||window.confirm('Restart the run and reset the current score?');if(ok)startRun();}});
UI.sound.addEventListener('click',()=>{sound.enabled=!sound.enabled;updateUI();if(sound.enabled)sound.beep(700,.12);});
// Public, read-only debugging hook for deterministic browser smoke tests. Not an in-game cheat UI.
window.__packetBreakerDebug={snapshot:()=>({mode:game.mode,score:game.score,lives:game.lives,level:game.level,balls:game.balls.length,paddle:{x:Math.round(game.paddle.x),target:Math.round(game.paddle.target),width:game.paddle.w},ballPositions:game.balls.map(b=>({x:Math.round(b.x),y:Math.round(b.y),vx:Math.round(b.vx),vy:Math.round(b.vy)})),bricks:game.bricks.filter(b=>!b.dead).length,ui:{arena:canvas.width+'x'+canvas.height}})};
buildStage();resetBalls(true);updateUI();requestAnimationFrame(frame);
