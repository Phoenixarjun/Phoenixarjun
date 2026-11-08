import {W,H,BLOCK_H,BASE_Y,START_W,clamp} from './physics.mjs';
const LIME='#B6FF3B', CYAN='#80D8C7', STEEL='#42535C';
function rr(ctx,x,y,w,h,r=8){ctx.beginPath();ctx.roundRect(x,y,w,h,r);}
function line(ctx,x1,y1,x2,y2,c,width=1,alpha=1){ctx.strokeStyle=c;ctx.lineWidth=width;ctx.globalAlpha=alpha;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.globalAlpha=1;}
function text(ctx,t,x,y,size=14,color='#fff',weight='600',align='left'){ctx.fillStyle=color;ctx.textAlign=align;ctx.font=`${weight} ${size}px ui-monospace, Consolas, monospace`;ctx.fillText(t,x,y);}
export class Scene {
 constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});this.canvas.width=W*2;this.canvas.height=H*2;this.ctx.setTransform(2,0,0,2,0,0);this.fx=[];this.shake=0;this.lastLength=1;this.lastFail=false;this.stars=Array.from({length:145},(_,i)=>({x:(i*71.383)%W,y:(i*39.79)%H,alpha:.07+(i*11%19)/100,r:i%5===0?1.4:.6}));}
 addLand(x,y,perfect){this.shake=perfect?4:9;for(let i=0;i<(perfect?40:23);i++){const a=Math.random()*Math.PI*2,s=60+Math.random()*215;this.fx.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s-40,life:.3+Math.random()*.65,max:.95,color:perfect?LIME:(i%3?CYAN:'#f3c979')});}}
 addFail(x,y){this.shake=20;for(let i=0;i<65;i++){const a=Math.random()*Math.PI*2,s=80+Math.random()*270;this.fx.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:.5+Math.random()*.8,max:1.3,color:i%2?'#ff6577':LIME});}}
 tickFx(dt){this.shake=Math.max(0,this.shake-dt*27);for(const p of this.fx){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=280*dt;p.life-=dt;}this.fx=this.fx.filter(p=>p.life>0);}
 background(ctx,t){const bg=ctx.createLinearGradient(0,0,W,H);bg.addColorStop(0,'#0c1719');bg.addColorStop(.55,'#060b0e');bg.addColorStop(1,'#07120e');ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
 const bloom=ctx.createRadialGradient(520,420,30,520,420,480);bloom.addColorStop(0,'#b6ff3b12');bloom.addColorStop(.65,'#163b2610');bloom.addColorStop(1,'#00000000');ctx.fillStyle=bloom;ctx.fillRect(0,0,W,H);
 // Architectural background rack silhouettes.
 for(let i=0;i<11;i++){const x=18+i*103;ctx.fillStyle=i%2?'#101d1f44':'#18312924';ctx.fillRect(x,30,43,345);for(let j=0;j<17;j++){line(ctx,x+7,49+j*18,x+34,49+j*18,'#4d7163',.6,.14);}}
 for(const s of this.stars){ctx.fillStyle=`rgba(161,255,177,${s.alpha})`;ctx.fillRect(s.x,s.y,s.r,s.r);}
 // Isometric floor lines: fade toward vanishing point; stable across frames.
 const horizon=390;for(let i=-18;i<=18;i++){line(ctx,W/2+i*21,horizon, W/2+i*95,H+80,'#76c890',1,0.11);}
 for(let i=0;i<15;i++){const f=(i/14)**1.8;const y=horizon+f*(H-horizon);line(ctx,0,y,W,y,'#87b8a0',.7,0.06+i/900);}
 const lg=ctx.createLinearGradient(0,0,0,H);lg.addColorStop(0,'#00000004');lg.addColorStop(.77,'#00000000');lg.addColorStop(1,'#000000bb');ctx.fillStyle=lg;ctx.fillRect(0,0,W,H);
 text(ctx,'// TOWER CONSTRUCTION ZONE',34,40,12,'#91bcb3','700');text(ctx,'DEPLOYMENT MATRIX 05',W-34,40,11,'#6f9995','600','right');line(ctx,33,56,1007,56,'#34574d',1,.55);
 // Peripheral scan grids and accents
 for(let i=0;i<4;i++){const y=110+i*56;line(ctx,28,y,140,y,LIME,1,.08);line(ctx,900,y,1011,y,LIME,1,.08);}
 line(ctx,41,74,41,128,LIME,2,.6);line(ctx,41,74,72,74,LIME,2,.6);
 line(ctx,997,74,966,74,LIME,2,.5);line(ctx,997,74,997,128,LIME,2,.5);
 }
 deck(ctx,cy){const px=W/2,base=BASE_Y+cy;const top=base+2;const w=286;ctx.save();ctx.shadowBlur=34;ctx.shadowColor='#b6ff3b23';ctx.fillStyle='#13211f';ctx.beginPath();ctx.moveTo(px-w/2-23,top);ctx.lineTo(px+w/2+23,top);ctx.lineTo(px+w/2+46,top+31);ctx.lineTo(px-w/2-46,top+31);ctx.closePath();ctx.fill();ctx.restore();
 ctx.fillStyle='#0c1217';ctx.fillRect(px-w/2,top,w,39);ctx.strokeStyle='#7eabb0';ctx.lineWidth=1.5;ctx.strokeRect(px-w/2,top,w,39);ctx.fillStyle='#131d24';ctx.beginPath();ctx.moveTo(px-w/2,top);ctx.lineTo(px-w/2+20,top-13);ctx.lineTo(px+w/2+20,top-13);ctx.lineTo(px+w/2,top);ctx.closePath();ctx.fill();
 ctx.strokeStyle=LIME;ctx.lineWidth=2;ctx.strokeRect(px-w/2+8,top+6,w-16,25);
 for(let i=0;i<12;i++){const x=px-w/2+18+i*(w-36)/11;ctx.fillStyle=i%3===0?LIME:'#365857';ctx.fillRect(x,top+17,8,4);}text(ctx,'CORE RACK / BASE 00',px,top+59,11,'#8eb8aa','600','center');}
 cuboid(ctx,b,y,mode='placed',time=0,focus=false){const {x,w,h=BLOCK_H}=b;if(w<=.5)return;const left=x-w/2,top=y,depth=14;
 const bright=mode==='live',ghost=mode==='ghost';const color=bright?LIME:mode==='failure'?'#ff6577':'#659e7d';
 ctx.save();if(ghost){ctx.globalAlpha=.33;ctx.setLineDash([6,6]);ctx.strokeStyle=LIME;ctx.lineWidth=2;ctx.strokeRect(left,top,w,h);ctx.setLineDash([]);ctx.restore();return;}
 if(bright){ctx.shadowColor='#b6ff3b';ctx.shadowBlur=20+Math.sin(time*4)*4;}
 // Front face shaded with three stops
 const front=ctx.createLinearGradient(left,top,left+w,top+h);if(bright){front.addColorStop(0,'#243d2f');front.addColorStop(.55,'#131d19');front.addColorStop(1,'#10181c');}else{front.addColorStop(0,b.tier%5===0?'#395b48':'#253f3b');front.addColorStop(.7,'#102025');front.addColorStop(1,'#091317');}
 ctx.fillStyle=front;ctx.fillRect(left,top,w,h);ctx.shadowBlur=0;
 // right isometric face
 ctx.beginPath();ctx.moveTo(left+w,top);ctx.lineTo(left+w+depth,top-depth*.55);ctx.lineTo(left+w+depth,top+h-depth*.55);ctx.lineTo(left+w,top+h);ctx.closePath();ctx.fillStyle=bright?'#415b30':'#1e3c38';ctx.fill();ctx.strokeStyle=bright?LIME:'#54796b';ctx.lineWidth=1;ctx.stroke();
 // upper metallic bevel
 ctx.beginPath();ctx.moveTo(left,top);ctx.lineTo(left+depth,top-depth*.55);ctx.lineTo(left+w+depth,top-depth*.55);ctx.lineTo(left+w,top);ctx.closePath();const metal=ctx.createLinearGradient(left,top-depth,left+w,top);metal.addColorStop(0,bright?'#9eff3f':'#76b99a');metal.addColorStop(.55,bright?'#365d3d':'#2b5855');metal.addColorStop(1,bright?'#b6ff3b':'#4b8272');ctx.fillStyle=metal;ctx.fill();ctx.strokeStyle=bright?'#d9ffa4':'#6a9d90';ctx.stroke();
 ctx.strokeStyle=bright?'#b6ff3b':'#3e675f';ctx.lineWidth=bright?2:1.25;ctx.strokeRect(left,top,w,h);line(ctx,left+4,top+6,left+w-4,top+6,bright?'#b9ffa5':'#7bdab5',1,.6);
 if(w>=45){let slots=Math.min(13,Math.floor(w/16));for(let i=0;i<slots;i++){const sx=left+10+i*(w-20)/Math.max(1,slots-1);ctx.fillStyle=i%4===0?(bright?LIME:'#7fcca7'):'#3c6464';ctx.fillRect(sx,top+h-10,Math.min(7,w/slots/2),3);}
 if(w>=120){text(ctx,mode==='live'?'INCOMING SERVER // '+String(b.tier).padStart(2,'0'):'SRV / '+String(b.tier).padStart(2,'0'),left+11,top+22,Math.min(11,w/13),bright?'#eaffdf':'#a0c3b8','700');}}
 ctx.restore();}
 draw(g){const ctx=this.ctx;ctx.save();ctx.clearRect(0,0,W,H);this.background(ctx,g.time);const cam=Math.max(0,(g.tower.length-5)*BLOCK_H);ctx.save();if(this.shake>0)ctx.translate((Math.random()-.5)*this.shake,(Math.random()-.5)*this.shake*.48);
 this.deck(ctx,cam);
 for(const block of g.tower){const y=block.y+cam;if(y<-75||y>H+80)continue;this.cuboid(ctx,block,y,'placed',g.time);}
 if(g.moving){const m=g.moving,top=g.tower[g.tower.length-1];const target=top.y-BLOCK_H+cam;let px=g.mode==='falling'?m.x:g.predicted;
 if(px!==null&&Number.isFinite(px)){const prediction={...m,x:px};this.cuboid(ctx,prediction,target,'ghost');line(ctx,px,target-10,px,m.y+cam+BLOCK_H,'#b6ff3b',1,.3);ctx.setLineDash([5,5]);line(ctx,top.x-top.w/2,target+BLOCK_H+2,top.x+top.w/2,target+BLOCK_H+2,'#80D8C7',2,.85);ctx.setLineDash([]);}
 this.cuboid(ctx,m,m.y+cam,'live',g.time);
 if(g.mode==='running'){text(ctx,'SCAN IN PROGRESS',m.x,m.y+cam-30,11,LIME,'800','center');line(ctx,m.x-44,m.y+cam-22,m.x+44,m.y+cam-22,LIME,1,.7);}
 }
 ctx.restore();
 // foreground dust and FX
 for(const p of this.fx){ctx.globalAlpha=clamp(p.life/Math.max(.0001,p.max),0,1);ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,3,3);}ctx.globalAlpha=1;
 // top-right construction status
 text(ctx,g.mode==='falling'?'● DEPLOYING':g.mode==='running'?'● SCANNING':g.mode==='gameover'?'● COLLAPSED':'● STANDBY',1005,80,12,g.mode==='gameover'?'#ff6577':LIME,'800','right');
 // progress elevation marker
 const layers=g.tower.length-1;text(ctx,'ALT '+String(layers*BLOCK_H).padStart(4,'0')+'m',36,H-28,12,'#75a69b','700');text(ctx,'STABILITY // '+Math.round(g.stability*100)+'%',W-35,H-28,12,'#81b9aa','700','right');
 ctx.restore();}
}
