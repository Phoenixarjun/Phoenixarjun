const test=require('node:test'),assert=require('node:assert/strict');
const P=require('../src/physics.js');
const near=(a,b,e=1e-6)=>assert.ok(Math.abs(a-b)<=e,`${a} !≈ ${b}`);
test('closest point clamps to segment ends',()=>{
  assert.deepEqual(P.closestPointOnSegment({x:-5,y:3},{x:0,y:0},{x:10,y:0}),{x:0,y:0,t:0});
  assert.deepEqual(P.closestPointOnSegment({x:14,y:3},{x:0,y:0},{x:10,y:0}),{x:10,y:0,t:1});
});
test('zero-length segment handled without NaN',()=>{
  const q=P.closestPointOnSegment({x:4,y:6},{x:1,y:2},{x:1,y:2});assert.equal(q.t,0);assert.equal(q.x,1);
});
test('circle/segment contact normal and overlap are correct',()=>{
  let c=P.circleSegmentContact({x:5,y:-2},4,{x:0,y:0},{x:10,y:0});near(c.n.x,0);near(c.n.y,-1);near(c.penetration,2);
  assert.equal(P.circleSegmentContact({x:5,y:-5},4,{x:0,y:0},{x:10,y:0}),null);
});
test('segment end cap collision is circular, not square',()=>{
  let c=P.circleSegmentContact({x:12,y:1},3,{x:0,y:0},{x:10,y:0});assert.ok(c);near(c.point.x,10);
});
test('circle/circle overlap and no-overlap',()=>{
  assert.equal(P.circleCircleContact({x:10,y:0},3,{x:0,y:0},4),null);
  const c=P.circleCircleContact({x:6,y:0},3,{x:0,y:0},4);near(c.n.x,1);near(c.penetration,1);
});
test('circle/AABB contact on horizontal, vertical and inside faces',()=>{
  let c=P.circleAABBContact({x:8,y:-1},3,{x:0,y:0,w:10,h:10});near(c.n.y,-1);near(c.penetration,2);
  c=P.circleAABBContact({x:5,y:5},2,{x:0,y:0,w:10,h:10});assert.ok(Number.isFinite(c.penetration));assert.ok(c.penetration>=2);
  assert.equal(P.circleAABBContact({x:20,y:20},2,{x:0,y:0,w:10,h:10}),null);
});
test('stationary wall reflection preserves normal speed for e=1',()=>{
  let b={x:5,y:-1,vx:20,vy:100};const c=P.circleSegmentContact(b,3,{x:0,y:0},{x:10,y:0});P.resolveContact(b,c,1);near(b.vy,-100);near(b.vx,20);assert.ok(b.y<-2.99);
});
test('inelastic wall collision dissipates energy',()=>{
  let b={x:5,y:-1,vx:0,vy:100};P.resolveContact(b,P.circleSegmentContact(b,3,{x:0,y:0},{x:10,y:0}),.8);near(b.vy,-80);
});
test('relative velocity handles moving flipper surface',()=>{
  let b={x:5,y:-1,vx:0,vy:100};const c=P.circleSegmentContact(b,3,{x:0,y:0},{x:10,y:0});P.resolveContact(b,c,.8,{x:0,y:-200});assert.ok(b.vy<-100);
});
test('swept circle/circle catches fast impact and misses diverging direction',()=>{
  let hit=P.sweepCircleCircle({x:-100,y:0},{x:1000,y:0},4,{x:0,y:0},6,.2);
  near(hit.t,.09);near(hit.n.x,-1);
  assert.equal(P.sweepCircleCircle({x:-100,y:0},{x:-1000,y:0},4,{x:0,y:0},6,.2),null);
});
test('swept circle/segment catches fast wall collision',()=>{
  const h=P.sweepCircleSegment({x:5,y:-100},{x:0,y:1000},5,{x:0,y:0},{x:10,y:0},.2);
  near(h.t,.095);near(h.n.y,-1);
});
test('swept circle/segment catches endpoint grazing',()=>{
  const h=P.sweepCircleSegment({x:12,y:-20},{x:0,y:200},4,{x:0,y:0},{x:10,y:0},.2);
  assert.ok(h);assert.ok(h.t>.06&&h.t<.11);
});
test('swept circle/segment does not hit zero-length absent path',()=>{
  assert.equal(P.sweepCircleSegment({x:100,y:0},{x:1,y:0},5,{x:0,y:0},{x:0,y:0},1),null);
});
test('flipper pivot geometry mirrors its opposite pair',()=>{
  let a=P.flipperTip({x:263,y:892},126,.34),b=P.flipperTip({x:494,y:892},126,Math.PI-.34);
  near(a.y,b.y);near(263+494-a.x,b.x);
});
test('angular contact velocity points upward on both flipping bats',()=>{
  let left=P.angularPointVelocity({x:263,y:892},{x:333,y:892},-10);
  let right=P.angularPointVelocity({x:494,y:892},{x:424,y:892},10);
  assert.ok(left.y<0);assert.ok(right.y<0);
});
test('speed limiting is monotonic and bounded',()=>{
  let b={vx:3000,vy:4000};P.limitSpeed(b,1400);near(Math.hypot(b.vx,b.vy),1400);near(b.vx/b.vy,.75);
  let x={vx:20,vy:30};P.limitSpeed(x,1400);near(x.vx,20);
});
test('10,000 randomized side and end-cap intersections have finite normals',()=>{
  let seed=8142027;
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<10000;i++){
    const a={x:random()*100,y:random()*100};const b={x:a.x+random()*150,y:a.y+random()*150};
    const p={x:random()*250,y:random()*250};const r=5+random()*18;
    const c=P.circleSegmentContact(p,r,a,b);
    if(!c)continue;
    assert.ok(Number.isFinite(c.n.x)&&Number.isFinite(c.n.y));
    near(Math.hypot(c.n.x,c.n.y),1,1e-8);
    assert.ok(c.penetration>=0&&c.penetration<=r);
  }
});
test('10,000 random swept cases never return a time outside [0, dt]',()=>{
  let seed=20384;const rand=()=>{seed=(Math.imul(seed,1103515245)+12345)>>>0;return seed/4294967296};
  for(let i=0;i<10000;i++){
    const p={x:rand()*400-200,y:rand()*400-200};const v={x:rand()*3000-1500,y:rand()*3000-1500};
    const a={x:rand()*100,y:rand()*100},b={x:a.x+100*rand(),y:a.y+100*rand()};
    const hit=P.sweepCircleSegment(p,v,9,a,b,.15);
    if(hit){assert.ok(hit.t>=0&&hit.t<=.15+1e-9);assert.ok(Number.isFinite(hit.n.x)&&Number.isFinite(hit.n.y));}
  }
});
