/* Circuit Pinball — layered Canvas 2.5D renderer. No external libraries. */
(function(root){
'use strict';
class PinballRenderer {
  constructor(game){this.g=game;this.ctx=game.ctx;this.W=760;this.H=1080;this.grid=null;}
  resize(){this.grid=null;}
  line(x1,y1,x2,y2,color,width=1,glow=0){const c=this.ctx;c.save();c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.strokeStyle=color;c.lineWidth=width;if(glow){c.shadowBlur=glow;c.shadowColor=color;}c.stroke();c.restore();}
  path(pts,fill,stroke,width=1){const c=this.ctx;c.beginPath();c.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)c.lineTo(pts[i][0],pts[i][1]);c.closePath();if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}}
  rounded(x,y,w,h,r,fill,stroke,width=1){const c=this.ctx;c.beginPath();c.roundRect(x,y,w,h,r);if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}}
  circle(x,y,r,fill,stroke,width=1,glow=0){const c=this.ctx;c.save();c.beginPath();c.arc(x,y,r,0,Math.PI*2);if(glow){c.shadowColor=stroke||fill;c.shadowBlur=glow;}if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}c.restore();}
  label(s,x,y,size=12,color='#a0babc',align='left',weight='600'){const c=this.ctx;c.save();c.font=`${weight} ${size}px Consolas, "Cascadia Code", monospace`;c.fillStyle=color;c.textAlign=align;c.textBaseline='middle';c.fillText(s,x,y);c.restore();}
  draw(now){const c=this.ctx,g=this.g,W=this.W,H=this.H;
    c.save();c.setTransform(c.getTransform().a,0,0,c.getTransform().d,0,0);
    c.clearRect(0,0,W,H);c.save();
    if(g.shake>0)c.translate(Math.sin(now*80)*g.shake*.48,Math.cos(now*64)*g.shake*.31);
    this.background(now);this.traces(now);this.chamber(now);this.launcher(now);
    this.targets(now);this.bumpers(now);this.posts(now);this.spinner(now);
    this.flippers(now);this.balls(now);this.particles(now);this.hud(now);
    if(g.screenFlash>0){c.fillStyle=`rgba(182,255,59,${g.screenFlash*.13})`;c.fillRect(0,0,W,H);}
    c.restore();c.restore();
  }
  background(now){const c=this.ctx;let b=c.createLinearGradient(0,0,760,1080);b.addColorStop(0,'#092023');b.addColorStop(.36,'#071012');b.addColorStop(.72,'#060e10');b.addColorStop(1,'#081b1b');c.fillStyle=b;c.fillRect(0,0,760,1080);
    // micro PCB matrix
    c.save();c.fillStyle='#42675e';c.globalAlpha=.13;
    for(let y=55;y<1040;y+=22)for(let x=65;x<718;x+=22){if((x+y*3)%11!==0)c.fillRect(x,y,1.2,1.2);}c.restore();
    c.save();c.strokeStyle='#173338';c.lineWidth=.75;c.globalAlpha=.65;
    for(let x=45;x<=724;x+=52){c.beginPath();c.moveTo(x,60);c.lineTo(x,1027);c.stroke();}
    for(let y=80;y<=1035;y+=52){c.beginPath();c.moveTo(47,y);c.lineTo(720,y);c.stroke();}
    c.restore();
    // Side neon spine lines, intentionally limited to edges.
    this.line(34,120,34,715,'#6e9a45',2,10);this.line(742,135,742,963,'#3b7771',2,7);
    const vignette=c.createRadialGradient(380,480,160,380,490,670);
    vignette.addColorStop(0,'#00000000');vignette.addColorStop(1,'#000000b6');c.fillStyle=vignette;c.fillRect(0,0,760,1080);
  }
  traces(now){const c=this.ctx;
    c.save();c.lineWidth=1;
    const tracks=[[[140,199],[140,155],[185,118],[226,118]],[[586,186],[605,163],[579,142],[542,142]],[[150,545],[100,545],[100,620],[138,653]],[[536,553],[603,553],[603,618],[584,658]],[[293,571],[293,638],[342,653],[342,723]],[[453,570],[453,625],[405,648],[405,711]]];
    for(let k=0;k<tracks.length;k++){
      c.beginPath();c.moveTo(...tracks[k][0]);for(const p of tracks[k].slice(1))c.lineTo(...p);
      c.strokeStyle=k%2?'#326d6a':'#647a40';c.globalAlpha=.45;c.stroke();c.globalAlpha=1;
      for(let j=1;j<tracks[k].length;j++)this.circle(...tracks[k][j],2.2,'#80c568');
    }
    c.restore();
    // Neon light strips near the mid-field are animated but not collision geometry.
    const alpha=.25+.14*Math.sin(now*3);
    c.save();c.globalAlpha=alpha;
    this.line(107,596,178,596,'#a5fb3e',2,13);
    this.line(539,589,612,589,'#a5fb3e',2,13);
    c.restore();
  }
  chamber(now){const c=this.ctx;
    const outer=[[82,214],[92,160],[118,115],[175,79],[265,61],[492,61],[561,78],[606,120],[638,166],[638,733],[615,778],[540,880],[535,956],[511,1031],[234,1031],[205,954],[196,880],[105,778],[82,746]];
    this.path(outer,'#07141417','#456460',7);
    this.path(outer,null,'#101b1c',3);
    // Inner metal rib + reflective panel highlights
    c.save();c.shadowBlur=13;c.shadowColor='#b6ff3b';this.line(112,137,174,88,'#b6ff3b',2,0);
    this.line(190,82,280,66,'#6f9b70',1.2);this.line(509,67,561,85,'#6b9b8e',1.5);
    this.line(87,262,87,493,'#6c9c80',1.3);
    this.line(634,260,634,488,'#5e928c',1.3);
    c.restore();
    // Arcs in upper chamber
    c.save();c.beginPath();c.arc(370,312,237,Math.PI*1.06,Math.PI*1.94);c.strokeStyle='#42674b';c.lineWidth=1.3;c.setLineDash([5,9]);c.stroke();c.setLineDash([]);c.restore();
    // Voltage and wiring motifs
    this.label('REACTOR-7 / SIGNAL CHAMBER',360,103,13,'#80a8a5','center','800');
    this.label('BUFFER LAYER',370,151,10,'#7ab4a5','center');
    this.line(205,162,535,162,'#305b50',1);
    // Side ramp field
    this.line(93,738,194,861,'#6c9b6d',6,8);
    this.line(642,733,544,862,'#639c91',6,8);
    this.line(93,738,194,861,'#b1d6a1',1.4);
    this.line(642,733,544,862,'#87b3aa',1.4);
    // Lower engineering circuitwork
    this.label('A',186,798,11,'#b6ff3b','center');this.label('B',553,798,11,'#b6ff3b','center');
    this.label('SYSTEM CORE',373,758,16,'#5eaaa0','center','800');
    this.label('KEEP PACKETS IN FLIGHT',374,790,11,'#77918c','center');
    // Bottom danger / drain channel
    this.path([[233,976],[320,1007],[437,1007],[523,976],[507,1044],[248,1044]],'#081013','#2e4140',1.1);
    for(let x=270;x<495;x+=33)this.line(x,1033,x+12,1017,'#536d59',1);
    this.label('DRAIN // LINK LOST',379,1023,11,'#9cae95','center');
  }
  launcher(now){const c=this.ctx;
    // Dedicated plunger lane separated from the main pinball chamber.
    const grad=c.createLinearGradient(656,250,733,250);grad.addColorStop(0,'#132a27');grad.addColorStop(.5,'#071216');grad.addColorStop(1,'#1e3431');
    this.rounded(661,263,73,767,17,grad,'#54736b',2.3);
    this.line(662,302,662,1002,'#86ad78',2,8);
    this.line(728,305,728,1002,'#77ada3',2,7);
    this.label('L',699,342,12,'#a6cf75','center');this.label('A',699,361,12,'#a6cf75','center');this.label('U',699,380,12,'#a6cf75','center');this.label('N',699,399,12,'#a6cf75','center');this.label('C',699,418,12,'#a6cf75','center');this.label('H',699,437,12,'#a6cf75','center');
    for(let y=490;y<955;y+=35)this.line(684,y,714,y,'#375750',1);
    const charge=Pclamp(this.g.charge,0,1);
    this.rounded(688,788,17,210,6,'#111e20','#52645a',1);
    this.rounded(691,993-195*charge,11,195*charge,5,'#b6ff3b',null);
    this.label('PLUNGER',700,1020,10,'#a1cb80','center');
    // Launch lane entrance arc above its physical partition.
    c.save();c.shadowColor='#b6ff3b';c.shadowBlur=11;
    c.beginPath();c.arc(686,270,38,Math.PI*1.03,Math.PI*1.96);c.strokeStyle='#5d987c';c.lineWidth=2;c.stroke();c.restore();
    function Pclamp(v,a,b){return Math.max(a,Math.min(b,v));}
  }
  targets(now){const c=this.ctx,g=this.g;
    this.label('FIREWALL PATCH NODES',358,180,11,'#86b4b3','center','800');
    for(const t of g.targets){
      const x=t.x,y=t.y;
      if(t.alive){
        const gr=c.createLinearGradient(x,y,x,y+26);gr.addColorStop(0,'#5c8c6f');gr.addColorStop(.23,'#264d45');gr.addColorStop(1,'#0d2023');
        c.save();c.shadowColor='#b6ff3b';c.shadowBlur=10;
        this.rounded(x,y,t.w,t.h,4,gr,'#85b78f',1.6);
        c.restore();this.label('0'+(t.id+1),x+t.w/2,y+12,11,'#d5ffc5','center','900');
        this.line(x+5,y+3,x+t.w-5,y+3,'#b6ff3b',1);
      } else {
        this.rounded(x,y,t.w,t.h,4,'#0d181b','#35504c',1);this.label('×',x+t.w/2,y+11,13,'#45675d','center');
      }
    }
    this.line(192,242,534,242,'#294946',1);
  }
  bumpers(now){const c=this.ctx;
    for(let i=0;i<window.CircuitPinballGameBumpers.length;i++){
      const b=window.CircuitPinballGameBumpers[i],phase=now*3.2+i*2.1,pulse=(Math.sin(phase)+1)/2;
      c.save();
      this.circle(b.x,b.y,b.r+17,null,'#365d5a',1);
      this.circle(b.x,b.y,b.r+10,null,'#668e66',2);
      this.circle(b.x,b.y,b.r+4,null,'#b6ff3b',1.5,8+pulse*8);
      const radial=c.createRadialGradient(b.x-11,b.y-15,2,b.x,b.y,b.r);
      radial.addColorStop(0,'#91cbb0');radial.addColorStop(.23,'#2c5751');radial.addColorStop(.64,'#102326');radial.addColorStop(1,'#071316');
      this.circle(b.x,b.y,b.r,radial,'#9fc68a',2,6);
      const metal=c.createRadialGradient(b.x-9,b.y-10,2,b.x,b.y,b.r*.75);
      metal.addColorStop(0,'#c9efb1');metal.addColorStop(.16,'#6b9d92');metal.addColorStop(.65,'#243c3b');metal.addColorStop(1,'#091619');
      this.circle(b.x,b.y,b.r*.71,metal,'#b6ff3b',2.5,8);
      const core=c.createRadialGradient(b.x-7,b.y-6,2,b.x,b.y,b.r*.39);
      core.addColorStop(0,'#f4ffe6');core.addColorStop(.2,'#c0ff69');core.addColorStop(.6,'#81d436');core.addColorStop(1,'#2d6825');
      this.circle(b.x,b.y,b.r*.38,core,null,0,14+pulse*6);
      this.label(b.name,b.x,b.y+b.r+31,10,'#9eb6ab','center','700');
      c.restore();
    }
  }
  posts(){const posts=[[222,868,15],[527,868,15],[134,612,13],[596,607,13]];
    for(const [x,y,r] of posts){this.circle(x,y,r+3,'#1b3333','#60857a',2);
      this.circle(x,y,r*.6,'#b6ff3b','#ecf5e4',1,7);}
    // Slingshot rubber triangles
    this.path([[131,690],[214,763],[164,765]],'#17302b','#6fba6a',2.8);
    this.path([[615,685],[530,761],[583,764]],'#17302b','#6ba89a',2.8);
    this.line(145,702,203,752,'#b6ff3b',2,8);this.line(602,701,541,753,'#7dcbc3',2,7);
  }
  spinner(now){const c=this.ctx,x=576,y=524;
    c.save();c.translate(x,y);c.rotate(now*2.4);this.line(-23,0,23,0,'#d4ffe3',4,5);this.line(0,-23,0,23,'#b6ff3b',3,5);this.circle(0,0,9,'#b6ff3b');c.restore();
    this.label('SPINNER',x,y+42,10,'#8baaaa','center');
  }
  flippers(){const c=this.ctx,g=this.g;
    for(const f of g.flippers){
      const tip=window.PinballPhysics.flipperTip(f.pivot,f.length,f.angle),x=f.pivot.x,y=f.pivot.y;
      c.save();c.lineCap='round';
      this.line(x+1,y+6,tip.x+2,tip.y+7,'#000b0d',43,16);
      this.line(x,y,tip.x,tip.y,'#4d6764',38,9);
      this.line(x,y-1,tip.x,tip.y-1,'#1f4240',32,0);
      this.line(x,y-4,tip.x,tip.y-4,f.pressed?'#b6ff3b':'#8fbeb1',26,f.pressed?18:7);
      this.line(x,y-4,tip.x,tip.y-4,'#d3e9c7',16,4);
      this.line(x,y-5,tip.x,tip.y-5,'#496b5e',7);
      this.circle(x,y,20,'#102424','#9bc4a0',3);this.circle(x,y,10,'#b6ff3b','#e5f6c8',2,12);
      this.circle(tip.x,tip.y,13,'#142d28','#b6ff3b',2);
      c.restore();
    }
  }
  balls(now){const c=this.ctx,g=this.g;
    for(const ball of g.balls){
      if(!ball.shooter){
        for(let i=ball.trail.length-1;i>=0;i--){
          const q=ball.trail[i];c.globalAlpha=(1-i/ball.trail.length)*.25;
          this.circle(q.x,q.y,Math.max(2,ball.r*(1-i/(ball.trail.length+2))),'#b6ff3b');
        }c.globalAlpha=1;
      }
      c.save();c.shadowColor='#d1ff93';c.shadowBlur=25;
      const grad=c.createRadialGradient(ball.x-4,ball.y-5,0,ball.x,ball.y,ball.r+2);
      grad.addColorStop(0,'#ffffff');grad.addColorStop(.28,'#e0fbea');grad.addColorStop(.6,'#9ee1a3');grad.addColorStop(.82,'#4d867e');grad.addColorStop(1,'#1b4145');
      this.circle(ball.x,ball.y,ball.r,grad,'#d5ffd3',1.6);
      this.circle(ball.x-3,ball.y-4,ball.r*.21,'#ffffff');c.restore();
    }
  }
  particles(now){const c=this.ctx,g=this.g;
    for(const p of g.particles){c.save();c.globalAlpha=Math.min(1,p.life/.35);c.shadowBlur=7;c.shadowColor=p.kind==='lime'?'#b6ff3b':'#82e0cf';c.fillStyle=p.kind==='lime'?'#b6ff3b':'#82d6d7';c.fillRect(p.x,p.y,p.r,p.r);c.restore();}
    for(const r of g.rings){c.save();c.globalAlpha=r.life/.4;c.strokeStyle='#b6ff3b';c.lineWidth=3;c.shadowColor='#b6ff3b';c.shadowBlur=14;c.beginPath();c.arc(r.x,r.y,r.r+(1-r.life/.4)*52,0,2*Math.PI);c.stroke();c.restore();}
    for(const f of g.floaters){c.save();c.globalAlpha=Math.max(0,f.life/f.max);c.font='900 17px Consolas,monospace';c.textAlign='center';c.fillStyle='#c9ff77';c.shadowColor='#a2f437';c.shadowBlur=11;c.fillText(f.text,f.x,f.y);c.restore();}
  }
  hud(now){const g=this.g,c=this.ctx;
    // compact floating internal status chips
    this.rounded(285,605,165,37,8,'#081516e8','#3a6958',1.5);
    this.circle(304,623,4,'#b6ff3b',null,0,7);
    this.label(g.tiltTimer>0?'TILT / LOCKOUT':g.balls.some(b=>b.shooter&&!b.launched)?'AWAIT LAUNCH':`SECTOR ${String(g.sector).padStart(2,'0')} // LIVE`,320,625,12,'#b7e0b7','left','800');
    // sector lumens, bottom near outlanes
    for(let i=0;i<5;i++)this.circle(303+i*35,715,5,i<g.sector?'#b6ff3b':'#365351',null,0,i<g.sector?5:0);
    if(g.ballSaver>0){this.label(`BALL SAVER ${Math.ceil(g.ballSaver)}s`,375,677,17,'#b6ff3b','center','900');}
    if(g.tiltTimer>0){c.save();c.globalAlpha=.6+.3*Math.sin(now*12);this.rounded(264,808,244,40,8,'#451816','#ff5b5c',2);this.label('TILT — FLIPPERS LOCKED',385,830,15,'#ffd0c8','center','900');c.restore();}
    if(g.charging){this.rounded(297,959,160,17,6,'#19302c','#7fbe7d',1);
      this.rounded(301,963,152*g.charge,9,4,'#b6ff3b',null);
      this.label('HOLD — RELEASE TO LAUNCH',376,947,10,'#b6ff3b','center');}
    // slim internal lower UI
    this.label('NARESH / CIRCUIT ARCADE',374,1055,10,'#5e8c83','center','700');
  }
}
root.PinballRenderer=PinballRenderer;
})(typeof globalThis!=='undefined'?globalThis:this);
