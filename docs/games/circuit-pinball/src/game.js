/* Circuit Pinball — a standalone, deterministic time-step arcade game.
   Deliberately separate from Packet Breaker and GitHub profile build pipeline.
   Physics is logical-pixel 2D; rendering is high-DPI 2.5D Canvas.
*/
(function(root){
'use strict';
const P=root.PinballPhysics;
if(!P) throw new Error('Circuit Pinball needs src/physics.js loaded first');
const W=760,H=1080, FIXED=1/120, G=760, R=11, MAX_SPEED=1860;
const $=id=>document.getElementById(id);
const SEGMENTS=[
  // Octagonal, smoothly approximated boundary of the upper reactor chamber.
  [[82,746],[82,214]], [[82,214],[92,160]],[[92,160],[118,115]],
  [[118,115],[175,79]],[[175,79],[265,61]],[[265,61],[492,61]],
  [[492,61],[561,78]],[[561,78],[606,120]],[[606,120],[638,166]],[[638,166],[638,733]],
  // Lower outlanes and funnel rails.
  [[82,746],[105,778]],[[105,778],[196,880]],[[638,733],[615,778]],[[615,778],[540,880]],
  [[188,915],[205,954]], [[549,913],[533,955]],
  // Deflectors over the flippers.
  [[133,691],[226,774]],[[226,774],[237,784]],
  [[612,686],[523,774]],[[523,774],[511,785]],
];
const SHOOTER_RAILS=[[[662,285],[662,1038]],[[731,210],[731,1038]]];
const BUMPERS=[{x:264,y:354,r:43,name:'ALPHA'},{x:469,y:348,r:43,name:'BETA'},{x:368,y:475,r:48,name:'GAMMA'}];
root.CircuitPinballGameBumpers=BUMPERS;
const POSTS=[{x:222,y:868,r:15},{x:527,y:868,r:15},{x:134,y:612,r:13},{x:596,y:607,r:13}];
const SPINNER={x:576,y:524,r:17};
const TARGET_X=[204,271,338,405,472];
const NOW=()=>typeof performance!=='undefined'?performance.now():Date.now();
function storedBest(){try{return Number(localStorage.getItem('circuit-pinball-best-v1'))||0;}catch(_){return 0;}}
function saveBest(n){try{localStorage.setItem('circuit-pinball-best-v1',String(n));}catch(_){}}
const fmt=n=>Math.max(0,Math.floor(n)).toLocaleString('en-US');
function random(min,max){return min+Math.random()*(max-min);}
class PinballGame {
  constructor(){
    this.canvas=$('pinball');this.ctx=this.canvas.getContext('2d',{alpha:false});
    this.audio=new root.CircuitAudio();this.state='menu';this.time=0;
    this.score=0;this.best=storedBest();this.ballsRemaining=3;this.sector=1;
    this.multiplier=1;this.combo=0;this.bumpersHit=0;this.totalBumpers=0;
    this.bankClears=0;this.bankRespawnTimer=0;this.targets=TARGET_X.map((x,i)=>({x,y:202,w:48,h:22,alive:true,id:i}));
    this.balls=[];this.particles=[];this.rings=[];this.floaters=[];
    this.flippers=[
      {side:'left',pivot:{x:260,y:892},length:97,radius:15,rest:.34,active:-.57,angle:.34,prevAngle:.34,omega:0,pressed:false},
      {side:'right',pivot:{x:500,y:892},length:97,radius:15,rest:Math.PI-.34,active:Math.PI+.57,angle:Math.PI-.34,prevAngle:Math.PI-.34,omega:0,pressed:false}
    ];
    this.charging=false;this.charge=0;this.tiltHeat=0;this.tiltTimer=0;
    this.ballSaver=0;this.saverUsed=false;this.extraBallAt=50000;this.lastUI=-1;
    this.pausedFrom='playing';this.shake=0;this.screenFlash=0;this.lastNow=0;this.accumulator=0;
    this.eventHistory=[];this.toastUntil=0;this.toastMessage='';this.lastCollisionAudio=0;
    this.controlPointers=new Map();this.pointerFlippers={left:new Set(),right:new Set()};
    this.renderer=new root.PinballRenderer(this);
    this.setupCanvas();this.bindControls();this.updateUI();
    this.addEvent('Table boot complete');this.addEvent('Awaiting player input');
    root.addEventListener('resize',()=>this.setupCanvas(),{passive:true});
    requestAnimationFrame(t=>this.frame(t));
  }
  setupCanvas(){
    const dpr=Math.min(root.devicePixelRatio||1,2);
    this.canvas.width=Math.round(W*dpr);this.canvas.height=Math.round(H*dpr);
    this.ctx.setTransform(dpr,0,0,dpr,0,0);
    this.renderer.resize();
  }
  addEvent(text){
    const mm=String(Math.floor(this.time/60)).padStart(2,'0'),ss=String(Math.floor(this.time%60)).padStart(2,'0');
    this.eventHistory.unshift({time:`${mm}:${ss}`,text});this.eventHistory=this.eventHistory.slice(0,7);
    $('eventStream').innerHTML=this.eventHistory.map(e=>`<div><span>${e.time}</span> ${this.escape(e.text)}</div>`).join('');
  }
  escape(s){return String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
  toast(text,seconds=1.6){this.toastMessage=text;this.toastUntil=this.time+seconds;const n=$('toast');n.textContent=text;n.classList.add('active');}
  hideToast(){if(this.time>this.toastUntil)$('toast').classList.remove('active');}
  setOverlay(kicker,title,body,button){$('overlayKicker').textContent=kicker;$('overlayTitle').innerHTML=title;$('overlayMessage').textContent=body;$('startBtn').innerHTML=`${button} <span aria-hidden="true">↗</span>`;$('overlay').classList.remove('hidden');}
  hideOverlay(){$('overlay').classList.add('hidden');}
  begin(){
    this.score=0;this.time=0;this.ballsRemaining=3;this.sector=1;this.multiplier=1;
    this.combo=0;this.bumpersHit=0;this.totalBumpers=0;this.bankClears=0;this.bankRespawnTimer=0;this.extraBallAt=50000;
    this.targets=TARGET_X.map((x,i)=>({x,y:202,w:48,h:22,alive:true,id:i}));
    this.balls=[];this.particles=[];this.rings=[];this.floaters=[];
    this.charging=false;this.charge=0;this.tiltTimer=0;this.tiltHeat=0;
    this.saverUsed=false;this.ballSaver=0;this.shake=0;this.screenFlash=0;
    this.flippers.forEach(f=>{f.angle=f.rest;f.prevAngle=f.rest;f.omega=0;f.pressed=false});
    this.state='playing';this.hideOverlay();this.spawnShooter();this.audio.unlock();
    this.eventHistory=[];this.addEvent('Reactor initialized');this.addEvent('Hold SPACE to charge the launch');
    this.toast('HOLD SPACE TO CHARGE',2.3);this.updateUI();
  }
  spawnShooter(){
    this.balls.push({x:698,y:941,vx:0,vy:0,r:R,shooter:true,launched:false,trail:[],lastFlipper:{left:-999,right:-999},lastHit:-999,stuck:0});
    this.charging=false;this.charge=0;
    this.addEvent('Packet loaded into launch rail');
  }
  launch(forceOverride){
    if(this.state!=='playing')return;
    const ball=this.balls.find(b=>b.shooter&&!b.launched);
    if(!ball)return;
    const charge=P.clamp(forceOverride===undefined?Math.max(.28,this.charge):forceOverride,.28,1);
    ball.launched=true;ball.vy=-(1420+430*charge);ball.vx=0;
    this.charging=false;this.charge=0;this.audio.play('launch');this.addEvent(`Packet launched @ ${Math.round(charge*100)}% charge`);
    this.toast('PACKET DEPLOYED');this.spawnParticles(ball.x,ball.y,14,'lime');
  }
  startCharging(){if(this.state==='menu'){this.begin();return;}if(this.state!=='playing')return;
    if(this.balls.some(b=>b.shooter&&!b.launched)) {this.charging=true;this.audio.unlock();}}
  stopCharging(){if(this.charging){this.launch();this.charging=false;}}
  togglePause(){
    if(this.state==='playing'){this.state='paused';this.pausedFrom='playing';this.setOverlay('SIMULATION SUSPENDED','SYSTEM<br/><em>PAUSED</em>','The table is frozen. Resume when you are ready.','RESUME SIMULATION');this.addEvent('Simulation paused');}
    else if(this.state==='paused'){this.state='playing';this.hideOverlay();this.addEvent('Simulation resumed');}
    this.updateUI();
  }
  nudge(){
    if(this.state!=='playing'||this.tiltTimer>0)return;
    this.tiltHeat+=.44;
    if(this.tiltHeat>=1.22){this.tiltTimer=3.6;this.audio.play('tilt');this.toast('TILT — FLIPPERS DISABLED',2);this.addEvent('Tilt protection engaged');this.screenFlash=.5;return;}
    for(const b of this.balls) if(!b.shooter) {b.vx+=random(-150,150);b.vy-=Math.round(140+random(0,60));}
    this.shake=7;this.audio.play('nudge');this.addEvent('Mechanical nudge applied');
  }
  scoreHit(points,label,x,y){
    const gain=Math.round(points*this.multiplier*(1+Math.min(this.combo,15)*.045));
    this.score+=gain;this.combo++;this.floaters.push({x,y,text:`+${fmt(gain)}`,life:1,max:1});
    if(this.score>this.best){this.best=this.score;saveBest(this.best);}
    if(this.score>=this.extraBallAt){this.ballsRemaining=Math.min(5,this.ballsRemaining+1);this.extraBallAt+=95000;this.toast('EXTRA BALL AWARDED',2.3);this.audio.play('bonus');this.addEvent('Extra ball awarded');}
    if(label)this.addEvent(label);this.updateUI();
  }
  hitBumper(ball,bump){
    const c=P.circleCircleContact(ball,ball.r,bump,bump.r);
    if(!c)return false;
    const pre=ball.vx*c.n.x+ball.vy*c.n.y;
    if(!P.resolveContact(ball,c,1.07))return false;
    const speed=Math.hypot(ball.vx,ball.vy);
    if(speed<700){ball.vx+=c.n.x*(700-speed);ball.vy+=c.n.y*(700-speed);}
    if(this.time-(ball.lastBumper?.[bump.name]??-100)>.09){
      ball.lastBumper=ball.lastBumper||{};ball.lastBumper[bump.name]=this.time;
      this.totalBumpers++;this.bumpersHit++;this.scoreHit(175,'Bumper '+bump.name+' activated',bump.x,bump.y);
      this.audio.play('bumper');this.rings.push({x:bump.x,y:bump.y,r:bump.r,life:.33});this.spawnParticles(bump.x,bump.y,14,'lime');
      if(this.bumpersHit>=10){this.multiplier=Math.min(5,this.multiplier+1);this.bumpersHit=0;this.toast(`REACTOR CHARGED // ×${this.multiplier}`,2.1);this.audio.play('bonus');}
    }
    if(pre>600)ball.vy-=110;
    return true;
  }
  onBankCleared(){
    this.bankClears++;this.scoreHit(2200,'Target bank neutralized',375,202);
    this.multiplier=Math.min(5,this.multiplier+1);
    this.toast('TARGET BANK COMPLETE // SECTOR UPGRADE',2.2);this.audio.play('bonus');this.screenFlash=.55;
    this.sector=Math.min(5,this.sector+1);
    this.spawnParticles(364,212,60,'lime');
    if(this.bankClears%2===0){this.activateMultiball();}
    this.bankRespawnTimer=1.45; // Keep disabled targets visible during the completed-bank celebration.
  }
  activateMultiball(){
    const playing=this.balls.find(b=>!b.shooter);
    if(!playing)return;
    if(this.balls.length>=5)return;
    for(let i=0;i<2;i++)this.balls.push({x:playing.x+(i?24:-24),y:playing.y-22,
      vx:(i?1:-1)*Math.max(370,Math.abs(playing.vx)+180),vy:-480-i*120,r:R,shooter:false,launched:true,trail:[],lastFlipper:{left:-999,right:-999},lastHit:-999,stuck:0});
    this.toast('MULTIBALL // PACKET STORM',2.4);this.audio.play('bonus');this.addEvent('Multiball activated');this.spawnParticles(playing.x,playing.y,40,'aqua');
  }
  spawnParticles(x,y,n,kind='lime'){
    for(let i=0;i<n&&this.particles.length<400;i++){
      const a=random(0,Math.PI*2),spd=random(50,310);
      this.particles.push({x,y,vx:Math.cos(a)*spd,vy:Math.sin(a)*spd,life:random(.24,.8),max:.8,r:random(1,3.5),kind});
    }
  }
  drain(ball){
    const idx=this.balls.indexOf(ball);if(idx<0)return;this.balls.splice(idx,1);
    this.audio.play('lose');this.spawnParticles(P.clamp(ball.x,160,590),1008,14,'aqua');
    if(this.balls.length>0)return;
    if(this.ballSaver>0&&!this.saverUsed){this.saverUsed=true;this.ballSaver=0;this.addEvent('Ball saver restored packet');this.toast('BALL SAVED!',2);this.spawnShooter();return;}
    this.ballsRemaining--;this.combo=0;this.multiplier=1;this.bumpersHit=0;this.saverUsed=false;this.ballSaver=0;
    if(this.ballsRemaining>0){this.addEvent('Packet lost // next ball queued');this.toast('DRAINED — NEXT BALL',2);this.spawnShooter();}
    else {this.state='gameover';this.audio.play('lose');this.setOverlay('SESSION COMPLETE', 'GAME<br/><em>OVER</em>', `Final score: ${fmt(this.score)} · Best: ${fmt(this.best)}. The reactor is ready for another run.`, 'PLAY AGAIN');this.addEvent('Session closed');}
    this.updateUI();
  }
  // Integrates ball motion in small displacement steps, with contact correction.
  // Swept circle primitives are also available for static contacts and separately tested.
  integrateBall(ball,dt){
    if(ball.shooter){
      if(!ball.launched)return;
      ball.vy+=G*.82*dt;ball.y+=ball.vy*dt;
      if(ball.y<280){ball.shooter=false;ball.x=593;ball.y=262;ball.vx=-350-random(0,80);ball.vy=Math.min(-590,ball.vy*.52);if(!this.saverUsed){this.ballSaver=9;this.toast('BALL SAVER // 9S',1.2);}else{this.ballSaver=0;}}
      else if(ball.y>1010&&ball.vy>0){ball.y=1010;ball.vy=-ball.vy*.43;}
      return;
    }
    const speed=Math.hypot(ball.vx,ball.vy);
    const substeps=Math.min(9,Math.max(1,Math.ceil(speed*dt/4.6)));
    for(let k=0;k<substeps;k++){
      const h=dt/substeps;
      ball.vy+=G*h;
      // Extremely mild drag to prevent unlimited energy in pinball play.
      const drag=Math.exp(-.021*h);ball.vx*=drag;ball.vy*=drag;
      ball.x+=ball.vx*h;ball.y+=ball.vy*h;
      for(let pass=0;pass<2;pass++){
        for(const [a,b] of SEGMENTS){
          const c=P.circleSegmentContact(ball,ball.r,{x:a[0],y:a[1]},{x:b[0],y:b[1]});
          if(c){const impact=-(ball.vx*c.n.x+ball.vy*c.n.y);P.resolveContact(ball,c,.79);
            if(pass===0&&impact>260&&this.time-ball.lastHit>.105){this.audio.play('wall');ball.lastHit=this.time;this.spawnParticles(c.point.x,c.point.y,2,'aqua');}
          }
        }
        for(const post of POSTS)P.resolveContact(ball,P.circleCircleContact(ball,ball.r,post,post.r),.89);
        for(const bump of BUMPERS)this.hitBumper(ball,bump);
        const spinner=P.circleCircleContact(ball,ball.r,SPINNER,SPINNER.r);
        if(spinner){P.resolveContact(ball,spinner,1.1);if(this.time-(ball.spinnerHit??-10)>.28){ball.spinnerHit=this.time;this.scoreHit(100,'Spinner engaged',SPINNER.x,SPINNER.y);this.audio.play('score');}}
        for(const t of this.targets){
          if(!t.alive || this.bankRespawnTimer>0)continue;
          const contact=P.circleAABBContact(ball,ball.r,t);
          if(contact){P.resolveContact(ball,contact,.91);t.alive=false;this.scoreHit(350,'Target disabled',t.x+t.w/2,t.y);this.audio.play('target');this.spawnParticles(t.x+t.w/2,t.y,14,'lime');this.rings.push({x:t.x+t.w/2,y:t.y+11,r:14,life:.4});if(this.targets.every(t=>!t.alive))this.onBankCleared();}
        }
        this.checkFlipper(ball,this.flippers[0]);this.checkFlipper(ball,this.flippers[1]);
      }
      P.limitSpeed(ball,MAX_SPEED);
      if(ball.y>1120){this.drain(ball);return;}
    }
    // Genuine ball trajectory history for short phosphor-style motion trails.
    ball.trail.unshift({x:ball.x,y:ball.y});if(ball.trail.length>11)ball.trail.pop();
    const current=Math.hypot(ball.vx,ball.vy);
    if(current<85&&ball.y<940)ball.stuck+=dt;else ball.stuck=0;
    if(ball.stuck>2.1){ball.vx+=(ball.x<380?240:-240);ball.vy+=190;ball.stuck=0;this.addEvent('Stalled packet released toward drain');}
  }
  checkFlipper(ball,f){
    // Sample the flipper's angular sweep: a rapidly rotating bat can otherwise
    // jump over a ball between successive fixed timesteps (tunneling).
    let c=null;
    for(const fraction of [1,.75,.5,.25,0]){
      const angle=f.prevAngle+(f.angle-f.prevAngle)*fraction;
      const tip=P.flipperTip(f.pivot,f.length,angle);
      c=P.circleSegmentContact(ball,ball.r+f.radius,f.pivot,tip);
      if(c)break;
    }
    if(!c)return;
    const v=P.angularPointVelocity(f.pivot,c.point,f.omega);
    const normalSpeed=ball.vx*c.n.x+ball.vy*c.n.y;
    P.resolveContact(ball,c,f.pressed?.88:.25,v);
    const last=ball.lastFlipper[f.side]??-100;
    if(this.time-last>.075){
      ball.lastFlipper[f.side]=this.time;
      if(this.tiltTimer<=0){
        if(!f.pressed && c.n.y < -.1){
          // A resting flipper is a gravity-fed ramp, NOT an automatic bumper.
          // Feed the ball inward toward the drain unless the player flips.
          ball.vx += f.side==='left'?35:-35;
          ball.vy += 28;
        }
        // A raised flipper adds kinetic energy proportional to paddle rotation.
        // If the ball hits the upper face, ensure a strong upward return.
        if(f.pressed && c.n.y<-.15){
          const kick=f.pressed?180:25;
          ball.vy=Math.min(ball.vy,-Math.min(1250,520+kick+Math.abs(f.omega)*19));
          ball.vx+=f.side==='left'?random(80,225):-random(80,225);
        }
        this.audio.play('flip');this.spawnParticles(c.point.x,c.point.y,8,'lime');
        if(f.pressed&&normalSpeed>50)this.scoreHit(10,'',c.point.x,c.point.y);
      }
    }
  }
  updateFlippers(dt){
    for(const f of this.flippers){
      const old=f.angle,desired=f.pressed&&this.tiltTimer<=0?f.active:f.rest;
      f.prevAngle=old;
      const maximum=(f.pressed?16:11)*dt;
      f.angle+=(P.clamp(desired-old,-maximum,maximum));
      f.omega=(f.angle-old)/dt;
    }
  }
  step(dt){
    if(this.state!=='playing')return;
    this.time+=dt;
    if(this.charging)this.charge=Math.min(1,this.charge+dt/1.12);
    if(this.ballSaver>0)this.ballSaver=Math.max(0,this.ballSaver-dt);
    if(this.bankRespawnTimer>0){this.bankRespawnTimer=Math.max(0,this.bankRespawnTimer-dt);if(this.bankRespawnTimer===0)this.targets.forEach(t=>t.alive=true);}
    this.tiltHeat=Math.max(0,this.tiltHeat-.18*dt);
    this.tiltTimer=Math.max(0,this.tiltTimer-dt);
    this.updateFlippers(dt);
    this.shake=Math.max(0,this.shake-20*dt);this.screenFlash=Math.max(0,this.screenFlash-.75*dt);
    for(const ball of [...this.balls])if(this.balls.includes(ball))this.integrateBall(ball,dt);
    for(const p of this.particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=280*dt;p.life-=dt;}
    this.particles=this.particles.filter(p=>p.life>0);
    for(const r of this.rings)r.life-=dt;this.rings=this.rings.filter(r=>r.life>0);
    for(const f of this.floaters){f.y-=35*dt;f.life-=dt;}this.floaters=this.floaters.filter(f=>f.life>0);
    this.hideToast();if(this.time-this.lastUI>.11){this.updateUI();this.lastUI=this.time;}
  }
  frame(t){
    if(!this.lastNow)this.lastNow=t;
    const elapsed=Math.min((t-this.lastNow)/1000,.05);this.lastNow=t;
    if(this.state==='playing'){
      this.accumulator+=elapsed;
      let iterations=0;
      while(this.accumulator>=FIXED&&iterations<7){this.step(FIXED);this.accumulator-=FIXED;iterations++;}
      if(iterations>=7)this.accumulator=0; // Avoid runaway spiral after a background-tab pause.
    }
    this.renderer.draw(t/1000);
    requestAnimationFrame(ts=>this.frame(ts));
  }
  updateUI(){
    $('score').textContent=fmt(this.score).padStart(7,'0');$('best').textContent=fmt(this.best).padStart(7,'0');
    $('ballsLeft').textContent=String(this.ballsRemaining).padStart(2,'0');$('multiplier').textContent='×'+this.multiplier;
    $('sector').textContent=String(this.sector).padStart(2,'0');$('combo').textContent=String(this.combo).padStart(2,'0');
    const count=this.targets.filter(t=>!t.alive).length;
    $('missionProgressLabel').textContent=`TARGET BANK ${count} / 5`;
    $('progressPercent').textContent=Math.round(count/5*100)+'%';$('missionProgress').style.width=(count/5*100)+'%';
    $('bumperCount').textContent=this.bumpersHit+' / 10';$('targetsCount').textContent=count+' / 5';
    $('multiState').textContent=this.bankClears>=2?'ONLINE':'LOCKED';
    $('diagState').textContent=this.state==='playing'?'RUNNING':this.state.toUpperCase();
    $('saverState').textContent=this.ballSaver>0?Math.ceil(this.ballSaver)+'S':'OFFLINE';
    $('tiltState').textContent=this.tiltTimer>0?'TILT':this.tiltHeat>.7?'WARNING':'NOMINAL';
    $('tableStatus').textContent=this.state==='playing'?'LIVE // REACTOR ACTIVE':this.state==='paused'?'SYSTEM PAUSED':this.state==='gameover'?'SESSION COMPLETE':'READY TO INITIALIZE';
    $('cabinetMessage').textContent=this.tiltTimer>0?'TILT PROTECTION ENGAGED':this.charging?'CHARGING LAUNCH: '+Math.round(this.charge*100)+'%':this.balls.some(b=>b.shooter&&!b.launched)?'HOLD SPACE / LAUNCH BUTTON':'BALL IN PLAY';
    $('pauseBtn').textContent=this.state==='paused'?'▶ RESUME':'Ⅱ PAUSE';
    $('muteBtn').textContent=this.audio.enabled?'♪ SOUND ON':'♪ MUTED';
  }
  bindControls(){
    $('startBtn').addEventListener('click',()=>{if(this.state==='paused')this.togglePause();else this.begin();});
    $('pauseBtn').addEventListener('click',()=>this.togglePause());
    $('muteBtn').addEventListener('click',()=>{this.audio.setEnabled(!this.audio.enabled);this.updateUI();});
    const keysDown=new Set();
    const handleDown=(e)=>{
      const code=e.code;
      if(['ArrowLeft','ArrowRight','ArrowUp','Space'].includes(code))e.preventDefault();
      if(e.repeat&&['Space','KeyN','ArrowUp','KeyP','KeyM','KeyR'].includes(code))return;
      keysDown.add(code);
      this.audio.unlock();
      if(code==='KeyA'||code==='ArrowLeft')this.flippers[0].pressed=true;
      if(code==='KeyD'||code==='ArrowRight')this.flippers[1].pressed=true;
      if(code==='Space'){if(this.state==='menu'||this.state==='gameover')this.begin();else if(this.state==='playing')this.startCharging();}
      if(code==='Enter'&&(this.state==='menu'||this.state==='gameover'))this.begin();
      if(code==='KeyN'||code==='ArrowUp')this.nudge();
      if(code==='KeyP')this.togglePause();
      if(code==='KeyM'){this.audio.setEnabled(!this.audio.enabled);this.updateUI();}
      if(code==='KeyR')this.begin();
    };
    const handleUp=e=>{
      keysDown.delete(e.code);
      if(e.code==='KeyA'||e.code==='ArrowLeft')this.flippers[0].pressed=false;
      if(e.code==='KeyD'||e.code==='ArrowRight')this.flippers[1].pressed=false;
      if(e.code==='Space')this.stopCharging();
    };
    root.addEventListener('keydown',handleDown);root.addEventListener('keyup',handleUp);
    root.addEventListener('blur',()=>{keysDown.clear();this.flippers.forEach(f=>f.pressed=false);this.stopCharging();if(this.state==='playing')this.togglePause();});
    const bindHold=(id,down,up)=>{
      const el=$(id);
      el.addEventListener('pointerdown',e=>{e.preventDefault();this.audio.unlock();try{el.setPointerCapture(e.pointerId);}catch(_){};el.classList.add('pressed');down(e);});
      for(const type of ['pointerup','pointercancel','lostpointercapture'])el.addEventListener(type,e=>{e.preventDefault();el.classList.remove('pressed');up(e);});
    };
    bindHold('leftBtn',()=>{this.flippers[0].pressed=true;},()=>{this.flippers[0].pressed=false;});
    bindHold('rightBtn',()=>{this.flippers[1].pressed=true;},()=>{this.flippers[1].pressed=false;});
    bindHold('launchBtn',()=>this.startCharging(),()=>this.stopCharging());
    $('nudgeBtn').addEventListener('pointerdown',e=>{e.preventDefault();this.nudge();});
    // On touch screens the table itself may be used as a convenient flipper pad.
    this.canvas.addEventListener('pointerdown',e=>{
      if(e.pointerType==='mouse')return;
      e.preventDefault();
      const rect=this.canvas.getBoundingClientRect(),x=(e.clientX-rect.left)*W/rect.width;
      const key=x<W/2?'left':'right';this.controlPointers.set(e.pointerId,key);
      this.flippers[key==='left'?0:1].pressed=true;this.audio.unlock();
      try{this.canvas.setPointerCapture(e.pointerId);}catch(_){}
    });
    const clearPointer=e=>{
      const key=this.controlPointers.get(e.pointerId);if(!key)return;
      this.controlPointers.delete(e.pointerId);
      this.flippers[key==='left'?0:1].pressed=[...this.controlPointers.values()].includes(key);
    };
    this.canvas.addEventListener('pointerup',clearPointer);this.canvas.addEventListener('pointercancel',clearPointer);
  }
}
root.CircuitPinballGame=PinballGame;
root.addEventListener('DOMContentLoaded',()=>{root.circuitPinball=new PinballGame();});
})(typeof globalThis!=='undefined'?globalThis:this);
