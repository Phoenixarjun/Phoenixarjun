/* STACK OVERFLOW // deterministic, fixed-step server-stack simulation.
   World units are pixels, time seconds. Rendering never determines collisions. */
export const W=1040, H=680, BLOCK_H=34, BASE_Y=552, START_W=224, G=1450;
export const STAGES=[
  {name:'BOOTSTRAP',from:1,speed:230,wind:0},
  {name:'LOAD BALANCE',from:5,speed:275,wind:35},
  {name:'DISTRIBUTED CORE',from:10,speed:330,wind:63},
  {name:'HIGH AVAILABILITY',from:16,speed:388,wind:85},
  {name:'HYPERSCALE',from:23,speed:445,wind:112}
];
export function stageFor(level){ return [...STAGES].reverse().find(s=>level>=s.from)||STAGES[0]; }
export function clamp(x,a,b){return Math.min(b,Math.max(a,x));}
export function easeOutCubic(t){return 1-Math.pow(1-clamp(t,0,1),3);}
export function overlap(a,b){let l=Math.max(a.x-a.w/2,b.x-b.w/2);let r=Math.min(a.x+a.w/2,b.x+b.w/2);return {left:l,right:r,width:Math.max(0,r-l),center:(l+r)/2};}
export function impactTime(y,vy,targetY,g=G){const dist=Math.max(0,targetY-y);return (-vy+Math.sqrt(vy*vy+2*g*dist))/g;}
export function predictLandingX(moving,targetY,wind=0){const t=impactTime(moving.y,moving.vy||0,targetY);return moving.x+(moving.vx||0)*t+.5*wind*t*t;}
export function solveLanding(block,top,{snap=7,minimum=24,minRatio=.18,maxWidth=START_W}={}){
  const delta=Math.abs(block.x-top.x); const ol=overlap(block,top);
  if(ol.width<minimum || ol.width<block.w*minRatio) return {ok:false,reason:'INSUFFICIENT OVERLAP',overlap:ol};
  if(delta<=snap && Math.abs(block.w-top.w)<=snap){
    return {ok:true,perfect:true,quality:1,trim:0,block:{...block,x:top.x,w:Math.min(maxWidth,Math.max(top.w,block.w)+2)}};
  }
  const quality=clamp(ol.width/Math.min(block.w,top.w),0,1);
  return {ok:true,perfect:false,quality,trim:Math.max(0,block.w-ol.width),block:{...block,x:ol.center,w:ol.width}};
}
export function supportStability(blocks){
  if(blocks.length<2)return 1;
  let min=1;
  // For each joint, mass center of EVERY block above the supporting block must lie on its upper footprint.
  for(let i=0;i<blocks.length-1;i++){
    let sum=0,mass=0;
    for(let j=i+1;j<blocks.length;j++){let m=blocks[j].w;sum+=blocks[j].x*m;mass+=m;}
    const support=blocks[i];const displacement=Math.abs(sum/mass-support.x);
    const ratio=clamp((support.w/2-displacement)/Math.max(1,support.w/2),0,1);
    min=Math.min(min,ratio);
  }
  return min;
}
export function mulberry32(seed){let a=seed>>>0;return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
export class StackGame {
  constructor(seed=0xCB923){this.seed=seed>>>0;this.rng=mulberry32(this.seed);this.reset();}
  reset(){this.rng=mulberry32(this.seed);this.mode='ready';this.time=0;this.tower=[{x:W/2,y:BASE_Y-BLOCK_H,w:START_W,h:BLOCK_H,tier:0,kind:'foundation'}];this.level=1;this.score=0;this.combo=0;this.perfects=0;this.bestCombo=0;this.focus=100;this.focusHeld=false;this.reducedThisFrame=false;this.health=1;this.lastQuality=0;this.events=[];this.drops=[];this.shock=0;this.wind=0;this.windClock=0;this.moving=null;this.spawn();}
  start(){if(this.mode==='ready'||this.mode==='paused')this.mode='running';}
  pause(){if(this.mode==='running'||this.mode==='falling'){this.resumeMode=this.mode;this.mode='paused';}else if(this.mode==='paused'){this.mode=this.resumeMode||'running';}}
  spawn(){const top=this.tower[this.tower.length-1];const stage=stageFor(this.level);const sign=this.level%2?1:-1;const x=sign>0?115:W-115;
    this.wind=(this.level<=4?0:(this.rng()-.5)*2*stage.wind);
    this.moving={x:clamp(x,top.w/2+24,W-top.w/2-24),y:top.y-162,w:top.w,h:BLOCK_H,vx:sign*(stage.speed+Math.min(100,(this.level-1)*2.7)),vy:0,tier:this.level,kind:this.level%7===0?'reinforced':'standard'};
    this.mode=this.mode==='ready'?'ready':'running';this.shock=0;
  }
  release(){if(this.mode==='ready')this.start();if(this.mode!=='running'||!this.moving)return false;
    this.moving.vx*=.13;this.moving.vy=0;this.mode='falling';this.focusHeld=false;this.emit('DROP COMMITTED');return true;}
  toggleFocus(enabled){this.focusHeld=Boolean(enabled);}
  emit(msg){this.events.unshift({message:msg,at:this.time});if(this.events.length>8)this.events.length=8;}
  update(dt){ if(!Number.isFinite(dt)||dt<=0) return; dt=Math.min(dt,1/30); if(this.mode!=='running'&&this.mode!=='falling')return;
    this.time+=dt;this.shock=Math.max(0,this.shock-dt*2.2);this.windClock+=dt;
    if(this.mode==='running'){
      const m=this.moving, stage=stageFor(this.level);
      const focusing=this.focusHeld&&this.focus>0;
      const speedFactor=focusing?.34:1;
      this.focus=clamp(this.focus+(focusing?-31:11)*dt,0,100);
      const bound=Math.max(36,m.w/2+24);m.x+=m.vx*dt*speedFactor;
      if(m.x>W-bound){m.x=2*(W-bound)-m.x;m.vx=-Math.abs(m.vx);}
      if(m.x<bound){m.x=2*bound-m.x;m.vx=Math.abs(m.vx);}
    }else if(this.mode==='falling'){
      const m=this.moving;const top=this.tower[this.tower.length-1];const targetY=top.y-BLOCK_H;
      const oldY=m.y; const newVy=m.vy+G*dt;let newY=m.y+(m.vy+newVy)*.5*dt;
      const newX=m.x+m.vx*dt+.5*this.wind*dt*dt;
      m.vx+=this.wind*dt; m.vy=newVy;m.x=newX;m.y=newY;
      if(oldY<=targetY && newY>=targetY){
        // Solve exact time of contact within this fixed step to avoid high-speed penetration.
        const remaining=targetY-oldY;
        const fraction=clamp((targetY-oldY)/Math.max(0.0001,newY-oldY),0,1);
        const t=dt*fraction;
        m.x=newX-(m.vx-this.wind*dt)*(dt-t)-.5*this.wind*(dt*dt-t*t);m.y=targetY;
        this.land();
      }
    }
  }
  land(){const m=this.moving,top=this.tower[this.tower.length-1];const result=solveLanding(m,top);this.shock=1;
    if(!result.ok){this.mode='gameover';this.moving=null;this.combo=0;this.emit('STACK FAILURE // '+result.reason);return;}
    const landed={...result.block,y:top.y-BLOCK_H,h:BLOCK_H,tier:this.level};
    const next=[...this.tower,landed];const stability=supportStability(next);
    if(stability<=0.002){this.mode='gameover';this.combo=0;this.emit('TOWER COLLAPSE // CENTER OF MASS');this.moving=null;return;}
    this.tower.push(landed);this.lastQuality=result.quality;
    if(result.perfect){this.combo++;this.perfects++;this.focus=clamp(this.focus+21,0,100);}
    else {this.combo=0;this.focus=clamp(this.focus+7,0,100);}
    this.bestCombo=Math.max(this.bestCombo,this.combo);
    const points=Math.round(100+300*Math.pow(result.quality,2)+(result.perfect?180:0)+this.combo*35);
    this.score+=points;
    if(result.trim>0){const left=m.x-m.w/2;const right=m.x+m.w/2;const ol=overlap(m,top);
      if(ol.left>left+0.5)this.drops.push({x:(left+ol.left)/2,y:m.y,w:ol.left-left,vx:-65,vy:-70,rotation:0,spin:-2.4,life:1.5});
      if(ol.right<right-0.5)this.drops.push({x:(right+ol.right)/2,y:m.y,w:right-ol.right,vx:65,vy:-70,rotation:0,spin:2.4,life:1.5});
    }
    this.emit(result.perfect?'PERFECT SYNC // +'+points:'SERVER DOCKED // '+Math.round(result.quality*100)+'% ALIGNMENT');
    this.level++;this.moving=null;this.spawn();
  }
  get stability(){return supportStability(this.tower);}
  get stage(){return stageFor(this.level);}
  get predicted(){if(!this.moving)return null;const top=this.tower[this.tower.length-1];const m=this.moving;const t=impactTime(m.y,0,top.y-BLOCK_H);return m.x+m.vx*.13*t+.5*this.wind*t*t;}
}
