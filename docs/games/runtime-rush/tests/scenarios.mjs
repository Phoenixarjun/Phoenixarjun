import assert from 'node:assert/strict';
import {createGame,startGame,update,setLane,LANE_X,FIXED_DT,sectorAt} from '../src/physics.mjs';

// Scenario A: zero input must eventually fail in a fair, playable game.
const idle=startGame(createGame(0xC1A0));let n=0;
while(idle.state==='playing'&&n++<100000)update(idle);
assert.equal(idle.state,'over');
assert.equal(idle.integrity,0);
assert.ok(idle.distance>80);
console.log(`Idle failure verified: ${idle.distance.toFixed(0)}m, ${idle.score} points, ${n} steps`);

// Scenario B: predictive bot may play by selecting any open lane in each pattern row.
const g=startGame(createGame(0xC1A0));
let attempts=0,steps=0;
while(g.distance<2300 && g.state==='playing'&&steps++<200000){
 const obs=g.items.filter(o=>['barrier','block','beam'].includes(o.type));
 const future=obs.filter(o=>o.s>=g.distance-1&&o.s<g.distance+30);
 const closest=Math.min(Infinity,...future.map(o=>o.s));
 if(Number.isFinite(closest)){
   const blocked=new Set(future.filter(o=>Math.abs(o.s-closest)<1.2).map(o=>o.lane));
   const reserved=[0,1,2].filter(l=>!blocked.has(l));
   const desired=reserved.reduce((a,b)=>Math.abs(a-g.targetLane)<Math.abs(b-g.targetLane)?a:b,reserved[0]);
   if(desired!==g.targetLane&&closest-g.distance>2){setLane(g,desired-g.targetLane);attempts++;}
 }
 update(g,FIXED_DT);
}
assert.equal(g.state,'playing');assert.ok(g.distance>=2300);assert.equal(g.stage,5);
console.log(`Predictive safety path verified: ${g.distance.toFixed(0)}m, ${g.score} points, stage ${g.stage}, ${attempts} lane switches`);

// Scenario C: ten independent seeds, deterministic replay, finite state and bounded score.
for(let seed=1;seed<=10;seed++){
 const a=startGame(createGame(seed)),b=startGame(createGame(seed));
 for(let i=0;i<15000;i++){
  update(a,FIXED_DT);update(b,FIXED_DT);
  if(a.state==='over')break;
 }
 assert.equal(a.distance,b.distance);assert.equal(a.score,b.score);assert.equal(a.state,b.state);
 assert.ok(Number.isFinite(a.distance));assert.ok(a.integrity>=0&&a.integrity<=3);
}
console.log('10-seed deterministic replay passed');
