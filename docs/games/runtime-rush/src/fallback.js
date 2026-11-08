/** Perspective-projected Canvas2D renderer for browsers with WebGL disabled.
 * Same world coordinates, player physics, and obstacles as the WebGL renderer.
 * All transforms are deterministic and based on a proper perspective camera.
 */
import {LANE_X} from './physics.mjs';
const PAL={lime:[182,255,59],aqua:[108,204,189],steel:[67,90,95],floor:[11,28,31],rail:[23,66,63],red:[249,85,86],white:[222,247,231],gold:[236,180,83],black:[7,22,26]};
const mix=(a,b,k)=>a.map((v,i)=>Math.round(v+(b[i]-v)*k));
const fbNorm=a=>{let k=Math.hypot(...a)||1;return a.map(v=>v/k)};
const fbCross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const fbDot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cc=(c,a=1)=>`rgba(${Math.round(c[0])},${Math.round(c[1])},${Math.round(c[2])},${a})`;
export class CanvasFallback{
 constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});if(!this.ctx)throw Error('Canvas not available');this.mode='fallback';this.w=0;this.h=0;this.boxes=[];this.glows=[];this.cam=[0,6.6,-14];this.resize();}
 resize(){let dpr=Math.min(window.devicePixelRatio||1,1.4),w=Math.max(1,Math.floor(this.canvas.clientWidth*dpr)),h=Math.max(1,Math.floor(this.canvas.clientHeight*dpr));if(w!==this.canvas.width||h!==this.canvas.height){this.canvas.width=w;this.canvas.height=h;}this.w=w;this.h=h;this.focal=h/(2*Math.tan(64*Math.PI/360));}
 camera(g){let x=(g.x||0)*.12;this.cam=[x,5.5,-11.8];let target=[x*.8,2.0,23];this.forward=fbNorm(target.map((v,i)=>v-this.cam[i]));this.right=fbNorm(fbCross(this.forward,[0,1,0]));this.up=fbCross(this.right,this.forward);}
 proj(p){let d=p.map((x,i)=>x-this.cam[i]),z=fbDot(d,this.forward);if(z<.15)return null;return {x:this.w/2+fbDot(d,this.right)*this.focal/z,y:this.h/2-fbDot(d,this.up)*this.focal/z,z,scale:this.focal/z}}
 face(pts,name='steel',emit=0,lit=1){const p=pts.map(v=>this.proj(v));if(p.some(x=>!x))return;const depth=p.reduce((s,v)=>s+v.z,0)/4;if(depth>165)return;this.boxes.push({p,depth,name,emit,lit})}
 box(x,y,z,sx,sy,sz,name,emit=0){const a=sx/2,b=sy/2,c=sz/2;const p=[[x-a,y-b,z-c],[x+a,y-b,z-c],[x+a,y+b,z-c],[x-a,y+b,z-c],[x-a,y-b,z+c],[x+a,y-b,z+c],[x+a,y+b,z+c],[x-a,y+b,z+c]];this.face([p[0],p[1],p[2],p[3]],name,emit,.75);this.face([p[4],p[5],p[6],p[7]],name,emit,.55);this.face([p[0],p[4],p[7],p[3]],name,emit,.48);this.face([p[1],p[5],p[6],p[2]],name,emit,.77);this.face([p[3],p[2],p[6],p[7]],name,emit,1.2);this.face([p[0],p[1],p[5],p[4]],name,emit,.35);}
 circle(x,y,z,r,c,em=0){const p=this.proj([x,y,z]);if(p)this.glows.push({p,r:r*p.scale,c,em})}
 render(g,t){this.resize();this.camera(g);this.boxes=[];this.glows=[];const ctx=this.ctx,w=this.w,h=this.h;
 let grad=ctx.createLinearGradient(0,0,0,h);grad.addColorStop(0,'#071718');grad.addColorStop(.54,'#071215');grad.addColorStop(1,'#02090b');ctx.fillStyle=grad;ctx.fillRect(0,0,w,h);
 ctx.fillStyle='#1a493f';for(let i=0;i<40;i++){let x=((i*191.7+80)%w),y=((i*41.8+12)%(h*.42));ctx.globalAlpha=.25+(i%7)*.045;ctx.fillRect(x,y,1.2,1.2)}ctx.globalAlpha=1;
 this.world(g,t);this.objects(g,t);
 this.boxes.sort((a,b)=>b.depth-a.depth);
 for(const f of this.boxes){let col=PAL[f.name]||PAL.steel,k=Math.min(1.75,f.lit+f.emit*.32),fog=Math.max(0,Math.min(.94,(f.depth-14)/132));col=mix(col.map(v=>Math.min(255,Math.round(v*k))),[6,26,28],fog);ctx.beginPath();ctx.moveTo(f.p[0].x,f.p[0].y);for(let j=1;j<4;j++)ctx.lineTo(f.p[j].x,f.p[j].y);ctx.closePath();ctx.fillStyle=cc(col);ctx.fill();if(f.emit>.3&&f.depth<65){ctx.strokeStyle=cc(mix(PAL[f.name]||PAL.lime,[255,255,255],.3),Math.max(.12,.6-fog));ctx.lineWidth=Math.max(.5,Math.min(2.2,f.p[0].scale*.012));ctx.stroke();}}
 for(const o of this.glows){const p=o.p,r=o.r;if(r<.2||r>500)continue;const c=PAL[o.c]||PAL.lime;ctx.save();ctx.shadowColor=cc(c,.68);ctx.shadowBlur=Math.min(30,r*.5);let grd=ctx.createRadialGradient(p.x-r*.16,p.y-r*.2,Math.max(.1,r*.03),p.x,p.y,r);grd.addColorStop(0,'#f2fff4');grd.addColorStop(.32,cc(c));grd.addColorStop(.75,cc(mix(c,[20,39,43],.4)));grd.addColorStop(1,'#071b1d');ctx.fillStyle=grd;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();ctx.restore();ctx.beginPath();ctx.arc(p.x,p.y,r*1.35,0,Math.PI*2);ctx.strokeStyle=cc(c,.4);ctx.lineWidth=Math.max(.7,Math.min(3,p.scale*.05));ctx.stroke();}
 this.player(g,t);}
 world(g,t){const dist=g.distance||t*5;
 this.box(0,-.22,55,11,.46,149,'floor');for(const lane of LANE_X){this.box(lane,-.03,55,2.9,.1,149,'rail');this.box(lane,.018,55,2.54,.012,149,'floor');}
 for(let z=-8;z<130;z+=7){const zz=z-(dist%7);this.box(0,.025,zz,10,.03,.09,'steel',.15);for(const xx of [-4.6,-1.55,1.55,4.6])this.box(xx,.04,zz+2,.07,.025,2.4,'aqua',.8)}
 for(const xx of [-5.4,5.4]){this.box(xx,.02,54,.2,.2,147,'lime',.7);this.box(xx,1.3,54,.36,2.6,147,'steel');this.box(xx,2.7,54,.12,.07,147,'aqua',.5)}
 for(let z=-11;z<128;z+=12){const zz=z-(dist%12);for(const xx of [-5.6,5.6]){this.box(xx,3.4,zz,.23,6.8,.27,'steel');this.box(xx,5.9,zz,.34,.25,.3,'aqua',.4)}this.box(0,7.1,zz,11.4,.2,.3,'steel');this.box(0,6.98,zz,4.0,.07,.32,'lime',1);this.box(0,-.13,zz,11,.18,.31,'aqua',.5)}
 for(let i=0;i<24;i++){const z=((i*15.7-(dist*1.2)%130+130)%130)-6;this.box(LANE_X[i%3]+(i%2?.81:-.81),.048,z,.065,.018,1.4,'lime',.8)}
 }
 objects(g,t){for(const o of g.items){const z=o.s-g.distance;if(z<-4||z>120)continue;const x=LANE_X[o.lane];if(o.type==='block'){this.box(x,.92,z,2.25,1.83,1.25,'steel');this.box(x,1.91,z,2.31,.13,1.33,'red',.6);for(let d of [-.7,.7])this.box(x+d,.8,z-.64,.1,1.5,.09,'red',.6)}else if(o.type==='barrier'){this.box(x,.43,z,2.21,.86,1.12,'steel');this.box(x,.9,z,2.25,.12,1.15,'gold',.4);for(let a=-.7;a<1;a+=.48)this.box(x+a,.45,z-.58,.16,.4,.04,'gold',.5)}else if(o.type==='beam'){for(const d of [-1.08,1.08])this.box(x+d,1.4,z,.12,2.8,.2,'steel');this.box(x,1.57,z,2.25,.20,.28,'red',1.4);this.box(x,2.8,z,2.2,.1,.2,'aqua')}else this.circle(x,1.1+Math.sin(t*4+o.id)*.2,z,o.type==='energy'?.6:.77,o.type==='shield'?'aqua':o.type==='overclock'?'gold':'lime',1.0);}}
 player(g,t){const ctx=this.ctx,x=g.x,y=g.y+(g.state==='menu'?Math.sin(t)*.15:0),p=this.proj([x,y,-.1]);if(!p)return;let r=.78*p.scale*(g.sliding>0?.65:1),c=g.shield>0?PAL.aqua:PAL.lime;ctx.save();ctx.shadowColor=cc(c,.7);ctx.shadowBlur=Math.min(35,r*.5);const grd=ctx.createRadialGradient(p.x-r*.32,p.y-r*.4,r*.1,p.x,p.y,r);grd.addColorStop(0,'#eaf8fa');grd.addColorStop(.16,'#638f94');grd.addColorStop(.45,'#264d52');grd.addColorStop(.78,'#102c30');grd.addColorStop(1,'#050c11');ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fillStyle=grd;ctx.fill();ctx.strokeStyle=cc(c,.95);ctx.lineWidth=Math.max(1.2,r*.09);ctx.stroke();ctx.restore();ctx.strokeStyle=cc(c,.8);ctx.lineWidth=Math.max(1.2,r*.06);ctx.beginPath();ctx.ellipse(p.x,p.y,r*1.08,r*.36,Math.sin(t*1.7)*.35,0,Math.PI*2);ctx.stroke();if(g.invulnerable>0){ctx.strokeStyle='#ff6161';ctx.beginPath();ctx.arc(p.x,p.y,r*1.45,0,Math.PI*2);ctx.stroke()}}
}
