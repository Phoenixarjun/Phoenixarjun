/** FIREWALL DEFENSE // procedural vector Canvas HUD and simulated network topology. */
import {WORLD,ROUTES,ROUTE_LENGTHS,PADS,TOWER_TYPES,ENEMY_TYPES,distance} from './engine.mjs';
const C={bg:'#070D0F',surface:'#101B1D',tile:'#0E191A',line:'#29433D',steel:'#42535C',accent:'#B6FF3B',aqua:'#66D9E8',text:'#EEF7EF',muted:'#73928E',amber:'#FFD166',red:'#FF7886'};
const TAU=Math.PI*2;
function rr(ctx,x,y,w,h,r,fill,stroke=null,lw=1){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.lineWidth=lw;ctx.strokeStyle=stroke;ctx.stroke();}}
function line(ctx,pts,color='#B6FF3B',width=1){ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);ctx.lineJoin='round';ctx.lineCap='round';ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function txt(ctx,str,x,y,size=12,color=C.text,align='left',weight=600){ctx.fillStyle=color;ctx.textAlign=align;ctx.textBaseline='middle';ctx.font=`${weight} ${size}px 'Cascadia Code',Consolas,monospace`;ctx.fillText(str,x,y);}
function glow(ctx,x,y,r,color,alpha=.26){const gr=ctx.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,`${color}${Math.floor(alpha*255).toString(16).padStart(2,'0')}`);gr.addColorStop(1,`${color}00`);ctx.fillStyle=gr;ctx.fillRect(x-r,y-r,r*2,r*2);}
function hex(ctx,x,y,r,color,fill=null,width=1.5,rotation=0){ctx.beginPath();for(let i=0;i<6;i++){const a=rotation+(Math.PI/3)*i-Math.PI/6;const px=x+Math.cos(a)*r,py=y+Math.sin(a)*r;if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);}ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill();}ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
export class CanvasRenderer{
  constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});this.hoverPad=null;this.visualTime=0;this.effects=[];this.particles=[];this.size();}
  size(){const dpr=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.round(WORLD.width*dpr);this.canvas.height=Math.round(WORLD.height*dpr);this.ctx.setTransform(dpr,0,0,dpr,0,0);}
  pushEvents(events){for(const e of events){if(['impact','hit','kill','build','upgrade','sell','pulse','beam','slow','leak','bonus','shot'].includes(e.type)){
      const max=['beam','pulse'].includes(e.type)? .24 : e.type==='kill'?.75:.32;
      this.effects.push({...e,life:max,max});if(this.effects.length>95)this.effects.splice(0,this.effects.length-95);
    }} }
  step(dt){this.visualTime+=Math.min(.05,dt);for(const e of this.effects)e.life-=dt;this.effects=this.effects.filter(e=>e.life>0);}
  render(game){const g=this.ctx,t=this.visualTime,w=WORLD.width,h=WORLD.height;g.save();g.clearRect(0,0,w,h);this.drawBackground(g,t);this.drawRoutes(g,t);this.drawPads(g,game,t);this.drawGateways(g,t);this.drawTowers(g,game,t);this.drawEnemies(g,game,t);this.drawProjectiles(g,game,t);this.drawEffects(g,t);this.drawDecorations(g,game,t);g.restore();}
  drawBackground(g,t){const w=WORLD.width,h=WORLD.height;g.fillStyle='#070D0F';g.fillRect(0,0,w,h);const bg=g.createRadialGradient(505,260,40,470,300,600);bg.addColorStop(0,'#14201C');bg.addColorStop(.55,'#0B1415');bg.addColorStop(1,'#060A0D');g.fillStyle=bg;g.fillRect(0,0,w,h);
    // Thin grid plus diagnostic intersections, offset behind the routes.
    g.strokeStyle='#1B2B2B';g.lineWidth=.65;g.globalAlpha=.65;
    for(let x=18;x<w;x+=33){g.beginPath();g.moveTo(x,0);g.lineTo(x,h);g.stroke();}
    for(let y=15;y<h;y+=33){g.beginPath();g.moveTo(0,y);g.lineTo(w,y);g.stroke();}
    g.globalAlpha=1;for(let row=0;row<9;row++)for(let col=0;col<14;col++){
      const x=17+col*66,y=13+row*66;
      g.fillStyle=((col+row)%3===0?'#35504A':'#233D39');g.fillRect(x,y,1.5,1.5);
    }
    // soft washes to make green and cyan lanes visually distinct
    glow(g,290,245,250,'#B6FF3B',.056);glow(g,500,420,230,'#66D9E8',.047);
    // corner brackets
    const corners=[[13,13,1,1],[w-13,13,-1,1],[13,h-13,1,-1],[w-13,h-13,-1,-1]];
    for(const [x,y,sx,sy] of corners){g.strokeStyle='#496454';g.lineWidth=1.6;g.beginPath();g.moveTo(x+sx*24,y);g.lineTo(x,y);g.lineTo(x,y+sy*22);g.stroke();}
  }
  drawRoutes(g,t){ROUTES.forEach((route,idx)=>{
    const color=idx===0?'#B6FF3B':'#66D9E8';
    g.save();g.shadowColor=color;g.shadowBlur=17;line(g,route,color,13);g.restore();
    line(g,route,'#1A3230',16);line(g,route,idx===0?'#537E39':'#3A7280',6);line(g,route,idx===0?'#94BD4E':'#68AFBB',2);
    // Electromagnetic moving lines; not the actual projectiles.
    const dashOffset=-(t*47)%34;
    g.save();g.setLineDash([4,26]);g.lineDashOffset=dashOffset;line(g,route,color,2.5);g.restore();
    // Each corner has visible router-style joint geometry
    for(let i=1;i<route.length-1;i++){
      const p=route[i];g.beginPath();g.arc(p.x,p.y,5,0,TAU);g.fillStyle='#0D1717';g.fill();g.strokeStyle=color;g.globalAlpha=.68;g.lineWidth=1.5;g.stroke();g.globalAlpha=1;
    }
    txt(g,idx===0?'UPLINK A':'UPLINK B',18,idx===0?155:486,10,idx===0?'#ADCA75':'#87B7C3', 'left',800);
  });}
  drawPads(g,game,t){for(const pad of PADS){const tower=game.getTowerAt(pad.id);if(tower)continue;const selected=this.hoverPad===pad.id;const color=selected?C.accent:'#50765E';
      const alpha=selected?.92:.48+.14*Math.sin(t*1.8+pad.id*.7);
      g.save();g.globalAlpha=alpha;
      rr(g,pad.x-20,pad.y-20,40,40,7,'#111E1D',selected?C.accent:'#3F6657',selected?1.8:1);
      g.strokeStyle=color;g.lineWidth=1;g.beginPath();g.moveTo(pad.x-9,pad.y);g.lineTo(pad.x+9,pad.y);g.moveTo(pad.x,pad.y-9);g.lineTo(pad.x,pad.y+9);g.stroke();
      if(selected){g.shadowColor=C.accent;g.shadowBlur=13;g.beginPath();g.arc(pad.x,pad.y,28,0,TAU);g.strokeStyle=C.accent;g.lineWidth=.8;g.stroke();}
      g.restore();
    }}
  drawGateways(g,t){for(let lane=0;lane<2;lane++){
      const start=ROUTES[lane][1],end=ROUTES[lane].at(-1),color=lane===0?C.accent:C.aqua;
      glow(g,start.x,start.y,60,color,.18);
      hex(g,start.x,start.y,22,color,'#142423',1.8);hex(g,start.x,start.y,14,color,'#172F26',1);
      txt(g,'IN',start.x,start.y,11,color,'center',850);
      for(let i=0;i<3;i++){const y=start.y+(i-1)*6;g.fillStyle=color;g.globalAlpha=.5;g.fillRect(4+i*5,y-1,8,2);g.globalAlpha=1;}
      glow(g,end.x+6,end.y,64,C.accent,.13);
    }
    const cx=913,cy=312;
    glow(g,cx,cy,64,'#B6FF3B',.13);
    hex(g,cx,cy,30,C.accent,'#102017',2.2,Math.PI/6);
    hex(g,cx,cy,20,'#89AB62','#13201B',1.3,Math.PI/6);
    txt(g,'CORE',cx,cy,10,C.accent,'center',900);
    txt(g,'◈',cx,cy-51,20,C.accent,'center',800);
  }
  drawTowers(g,game,t){for(const tower of game.towers){const spec=TOWER_TYPES[tower.type],selected=game.selectedPad===tower.padId;
      const range=spec.range*(1+.08*(tower.level-1));
      if(selected||this.hoverPad===tower.padId){g.save();g.globalAlpha=.08;g.fillStyle=spec.color;g.beginPath();g.arc(tower.x,tower.y,range,0,TAU);g.fill();g.globalAlpha=.44;g.setLineDash([5,6]);g.strokeStyle=spec.color;g.lineWidth=1;g.stroke();g.restore();}
      g.save();g.shadowColor=spec.color;g.shadowBlur=selected?17:7;
      hex(g,tower.x,tower.y,29,spec.color,'#14201E',selected?2.6:1.6,Math.PI/6);
      g.restore();hex(g,tower.x,tower.y,23,'#48665D','#172426',1,Math.PI/6);
      // metallic face panel and center icon
      g.fillStyle='#1E2D2E';g.beginPath();g.arc(tower.x,tower.y,15,0,TAU);g.fill();
      if(tower.type==='firewall'){
        g.save();g.translate(tower.x,tower.y);g.rotate(tower.angle);g.strokeStyle=spec.color;g.lineWidth=3;g.beginPath();g.moveTo(-13,0);g.lineTo(10,0);g.moveTo(2,-6);g.lineTo(12,0);g.lineTo(2,6);g.stroke();g.restore();
      } else if(tower.type==='cache'){
        g.strokeStyle=spec.color;g.lineWidth=2.4;g.beginPath();g.arc(tower.x,tower.y,10,0,TAU);g.stroke();g.beginPath();g.moveTo(tower.x,tower.y-8);g.lineTo(tower.x,tower.y+2);g.lineTo(tower.x+7,tower.y+5);g.stroke();
      }else if(tower.type==='pulse'){
        for(let i=0;i<3;i++){const a=i*TAU/3+t*.3;g.beginPath();g.arc(tower.x+Math.cos(a)*9,tower.y+Math.sin(a)*9,3,0,TAU);g.fillStyle=spec.color;g.fill();}
        g.fillStyle='#B7D3BA';g.fillRect(tower.x-2,tower.y-2,4,4);
      }else{
        g.strokeStyle=spec.color;g.lineWidth=2.3;g.beginPath();g.moveTo(tower.x-10,tower.y+7);g.lineTo(tower.x-3,tower.y-6);g.lineTo(tower.x+3,tower.y+4);g.lineTo(tower.x+10,tower.y-10);g.stroke();
      }
      for(let i=0;i<tower.level;i++){g.beginPath();g.arc(tower.x-8+i*8,tower.y+31,2.3,0,TAU);g.fillStyle=spec.color;g.fill();}
      if(selected){hex(g,tower.x,tower.y,35,spec.color,null,1.2,Math.PI/6);}
    }}
  drawEnemies(g,game,t){for(const enemy of game.enemies){const spec=ENEMY_TYPES[enemy.type];const color=enemy.hitFlash>0?'#FFFFFF':spec.color;
      if(game.time<enemy.slowUntil){g.beginPath();g.arc(enemy.x,enemy.y,enemy.radius+8,0,TAU);g.strokeStyle=C.aqua;g.lineWidth=1.8;g.setLineDash([4,3]);g.stroke();g.setLineDash([]);}
      if(enemy.shield>0){g.save();g.shadowColor='#6CADFF';g.shadowBlur=8;g.beginPath();g.arc(enemy.x,enemy.y,enemy.radius+7,0,TAU);g.strokeStyle='#77B8FF';g.lineWidth=2.2;g.stroke();g.restore();}
      g.save();g.shadowColor=color;g.shadowBlur=13;hex(g,enemy.x,enemy.y,enemy.radius,color,'#1A2023',2,enemy.type==='sprint'?t*2:0);g.restore();
      if(enemy.type==='titan'){hex(g,enemy.x,enemy.y,enemy.radius*.62,color,'#381A24',1.5);txt(g,'!',enemy.x,enemy.y,16,color,'center',900);}
      else if(enemy.type==='stealth'){g.save();g.globalAlpha=.66+.18*Math.sin(t*9);txt(g,'?',enemy.x,enemy.y,14,color,'center',900);g.restore();}
      else if(enemy.type==='sprint'){g.fillStyle=color;g.beginPath();g.arc(enemy.x,enemy.y,3,0,TAU);g.fill();}
      else{g.strokeStyle=color;g.lineWidth=1.5;g.beginPath();g.moveTo(enemy.x-4,enemy.y);g.lineTo(enemy.x+4,enemy.y);g.moveTo(enemy.x,enemy.y-4);g.lineTo(enemy.x,enemy.y+4);g.stroke();}
      const bw=enemy.type==='titan'?55:enemy.radius*2.7,bh=3,bx=enemy.x-bw/2,by=enemy.y-enemy.radius-11;
      g.fillStyle='#3D2229';g.fillRect(bx,by,bw,bh);g.fillStyle=enemy.hp/enemy.maxHp>.45?'#A6F46B':'#F8A16B';g.fillRect(bx,by,bw*Math.max(0,enemy.hp/enemy.maxHp),bh);
    }}
  drawProjectiles(g,game,t){for(const p of game.projectiles){const color=TOWER_TYPES[p.type].color;
      g.strokeStyle=color;g.lineWidth=3;g.shadowColor=color;g.shadowBlur=12;g.beginPath();g.moveTo(p.x-p.vx/p.spd*12,p.y-p.vy/p.spd*12);g.lineTo(p.x,p.y);g.stroke();g.shadowBlur=0;g.beginPath();g.arc(p.x,p.y,3,0,TAU);g.fillStyle='#F7FFF6';g.fill();
    }}
  drawEffects(g,t){for(const e of this.effects){const a=e.life/e.max;
      g.save();g.globalAlpha=a;
      if(e.type==='beam'){
        g.shadowColor=e.color;g.shadowBlur=12;g.strokeStyle=e.color;g.lineWidth=2+2*a;
        g.beginPath();g.moveTo(e.x,e.y);g.lineTo((e.x+e.tx)/2+4*Math.sin(t*35), (e.y+e.ty)/2);g.lineTo(e.tx,e.ty);g.stroke();
      }else if(e.type==='pulse'){
        g.strokeStyle=e.color;g.shadowColor=e.color;g.shadowBlur=16;g.lineWidth=2.5;g.beginPath();g.arc(e.x,e.y,e.r*(1-a*.7),0,TAU);g.stroke();
      }else if(e.type==='hit'||e.type==='impact'||e.type==='kill'||e.type==='build'||e.type==='upgrade'||e.type==='slow'||e.type==='bonus'){
        const radius=(1-a)*24+(e.type==='kill'?15:5);g.strokeStyle=e.color||C.accent;g.lineWidth=2*a;g.beginPath();g.arc(e.x,e.y,radius,0,TAU);g.stroke();
        if(e.type==='kill'||e.type==='bonus'){txt(g,e.type==='bonus'?'+20 CR':'NEUTRALIZED',e.x,e.y-15-(1-a)*24,9,C.accent,'center',750);}
      }else if(e.type==='leak'){
        glow(g,e.x,e.y,(1-a)*90+10,C.red,.22*a);
      }
      g.restore();
    }}
  drawDecorations(g,game,t){
    // In-game metric strips are internal canvas HUD elements, not HTML overlays.
    rr(g,18,17,215,30,5,'#0B1516','#283B35',1);
    txt(g,'●',31,32,12,C.accent,'left',700);txt(g,'IDS MATRIX // ACTIVE',49,32,10,'#8DB5A2','left',750);
    rr(g,743,17,197,30,5,'#0B1516','#283B35',1);
    txt(g,'UPLINKS: 02  •  CORE: 01',840,32,9,'#A6C2B7','center',750);
    const active=game.phase==='wave';rr(g,357,570,251,30,7,'#0C1717','#304039',1);
    txt(g,active?'◉   HOSTILE TRAFFIC DETECTED':game.phase==='ready'?'◎   AWAITING WAVE DEPLOYMENT':game.phase==='won'?'◈   NETWORK SECURED':'✕   SYSTEM OFFLINE',482,585,10,active?'#FFD166':C.accent,'center',800);
    // scanning cursor on uplink junctions
    for(let lane=0;lane<2;lane++){
      const x=22+((t*39)%840),y=lane===0?73:557;
      g.fillStyle=lane===0?C.accent:C.aqua;g.globalAlpha=.45;g.fillRect(x,y,11,1.5);g.globalAlpha=1;
    }
  }
}
