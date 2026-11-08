import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sweepCircleAABB,paddleBounce,reflect,stabiliseVelocity,sweepWall,testOverlapCircleRect} from '../src/physics.mjs';
const R={x:100,y:100,w:100,h:30};
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-6,`${a} != ${b}`);
test('horizontal high-speed sweep hits brick without tunneling',()=>{const h=sweepCircleAABB(0,115,500,0,8,R); near(h.t,92/500);assert.equal(h.nx,-1);assert.equal(h.ny,0);});
test('vertical high-speed sweep hits brick without tunneling',()=>{const h=sweepCircleAABB(150,0,0,300,6,R);near(h.t,94/300);assert.equal(h.ny,-1);});
test('missed brick does not collide',()=>assert.equal(sweepCircleAABB(0,0,300,0,6,R),null));
test('moving away does not collide',()=>assert.equal(sweepCircleAABB(90,115,-100,0,8,R),null));
test('initial interior is treated separately',()=>assert.equal(sweepCircleAABB(150,110,20,0,8,R),null));
test('wall sweep reaches boundary',()=>near(sweepWall(50,-100,10,1),.4));
test('wall sweep travelling away ignored',()=>assert.equal(sweepWall(50,100,10,1),null));
test('paddle centre keeps ball going up and has adequate horizontal motion',()=>{const b=paddleBounce(0,0,500);assert.ok(b.vy<0); assert.ok(Math.abs(b.vx)>50);near(Math.hypot(b.vx,b.vy),500);});
test('paddle right edge aims right',()=>assert.ok(paddleBounce(.9,0,500).vx>0));
test('paddle left edge aims left',()=>assert.ok(paddleBounce(-.9,0,500).vx<0));
test('velocity stabilization retains max cap',()=>{const v=stabiliseVelocity(10000,1,250,800);near(Math.hypot(v.vx,v.vy),800);assert.ok(Math.abs(v.vy)>=800*.22-1e-6);});
test('reflection mirrors angle',()=>{const b=reflect(200,300,0,-1);assert.equal(b.y,-300);assert.equal(b.x,200);});
test('circle overlap with edge',()=>assert.ok(testOverlapCircleRect(90,112,11,R)));
test('glancing trajectory outside rounded corner does NOT collide',()=>{
 assert.equal(sweepCircleAABB(0,91,300,0,8,R),null);
});
test('diagonal hit against rounded corner has diagonal normal',()=>{
 const h=sweepCircleAABB(80,80,40,40,8,R);
 assert.ok(h);near(h.t,(20-8/Math.SQRT2)/40);near(h.nx,-Math.SQRT1_2);near(h.ny,-Math.SQRT1_2);
});
test('paddle side collision is detected with normal facing outward',()=>{
 const h=sweepCircleAABB(0,610,300,0,8,{x:120,y:600,w:100,h:18});assert.ok(h);near(h.nx,-1);
});
test('10,000 random sweeps return finite, normalized contact times and unit normals',()=>{
 let seed=1337;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)|0;return (seed>>>0)/4294967296;};
 for(let i=0;i<10000;i++){
  const x=rnd()*350-40,y=rnd()*260-40,dx=(rnd()-.5)*600,dy=(rnd()-.5)*600,r=2+rnd()*12;
  const h=sweepCircleAABB(x,y,dx,dy,r,R);if(h){assert.ok(Number.isFinite(h.t)&&h.t>=0&&h.t<=1);near(Math.hypot(h.nx,h.ny),1);assert.ok(h.nx*dx+h.ny*dy<0);}
 }
});
