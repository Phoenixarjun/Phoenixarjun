import test from 'node:test';
import assert from 'node:assert/strict';
import {FirewallGame,ROUTES,ROUTE_LENGTHS,PADS,TOWER_TYPES,ENEMY_TYPES,WAVES,makeRng,distance,routeLength,locationAlong,segmentCircleHit} from '../src/engine.mjs';
const step=(g,s)=>{for(let i=0;i<Math.round(s*120);i++)g.update(1/120);};
test('Two routes have ordered, finite, nonzero lengths and end at core gateways',()=>{
 assert.equal(ROUTES.length,2);for(let n=0;n<2;n++){assert.ok(ROUTE_LENGTHS[n]>700);assert.equal(ROUTE_LENGTHS[n],routeLength(ROUTES[n]));assert.ok(ROUTES[n][0].x<ROUTES[n].at(-1).x);}
});
test('Location interpolation handles negative, interior and beyond-end distances',()=>{
 const r=ROUTES[0];assert.deepEqual(locationAlong(r,-20),r[0]);assert.deepEqual(locationAlong(r,1e9),r.at(-1));
 const mid=locationAlong(r,33);assert.equal(mid.y,r[0].y);assert.ok(mid.x>r[0].x);});
test('Pads never occupy actual route tiles and have no duplicates',()=>{
 const cells=new Set();for(const route of ROUTES)for(const p of route)cells.add(`${p.x},${p.y}`);
 const pads=new Set();for(const p of PADS){assert.ok(!cells.has(`${p.x},${p.y}`));const key=`${p.c},${p.r}`;assert.ok(!pads.has(key));pads.add(key);}
});
test('Segment-circle collision handles tunneling, tangencies and zero-length steps',()=>{
 assert.ok(segmentCircleHit(-100,0,100,0,0,0,5));assert.ok(segmentCircleHit(-10,5,10,5,0,0,5));assert.ok(!segmentCircleHit(-10,6,10,6,0,0,5));assert.ok(segmentCircleHit(0,0,0,0,0,0,3));assert.ok(!segmentCircleHit(0,0,0,0,8,0,3));
});
test('Randomized segment collision agrees with point-segment distance for 15000 cases',()=>{
 const rng=makeRng(9812);for(let i=0;i<15000;i++){
   const a={x:rng()*400-200,y:rng()*400-200},b={x:rng()*400-200,y:rng()*400-200},c={x:rng()*400-200,y:rng()*400-200},radius=1+rng()*20;
   const dx=b.x-a.x,dy=b.y-a.y,d=dx*dx+dy*dy,t=d?Math.max(0,Math.min(1,((c.x-a.x)*dx+(c.y-a.y)*dy)/d)):0;
   const dist=Math.hypot(c.x-(a.x+t*dx),c.y-(a.y+t*dy));
   assert.equal(segmentCircleHit(a.x,a.y,b.x,b.y,c.x,c.y,radius),dist<=radius);
 }
});
test('RNG determinism',()=>{const a=makeRng(42),b=makeRng(42);for(let i=0;i<500;i++)assert.equal(a(),b());});
test('Invalid/duplicate placement and missing credit are rejected',()=>{
 const g=new FirewallGame();assert.equal(g.placeTower(-1).ok,false);assert.equal(g.placeTower(0,'broken').ok,false);
 assert.equal(g.placeTower(0,'firewall').ok,true);assert.equal(g.placeTower(0,'firewall').ok,false);
 assert.equal(g.placeTower(1,'ids').ok,true);assert.equal(g.placeTower(2,'ids').ok,false);
});
test('Upgrades have bounded levels, nonnegative credits and selling refunds',()=>{
 const g=new FirewallGame();g.credits=2000;g.placeTower(2,'firewall');assert.equal(g.getTowerAt(2).level,1);
 assert.ok(g.upgradeTower(2).ok);assert.ok(g.upgradeTower(2).ok);assert.equal(g.getTowerAt(2).level,3);assert.equal(g.upgradeTower(2).ok,false);
 const old=g.credits,refund=Math.round(g.getTowerAt(2).spent*.65);assert.ok(g.sellTower(2).ok);assert.equal(g.credits,old+refund);assert.equal(g.sellTower(2).ok,false);
});
test('Cannot start overlapping waves; spawned enemies traverse two lanes',()=>{
 const g=new FirewallGame();assert.equal(g.startWave(),true);assert.equal(g.startWave(),false);
 step(g,2);assert.ok(g.enemies.some(e=>e.routeIndex===0));assert.ok(g.enemies.some(e=>e.routeIndex===1));assert.ok(g.spawned>=2);
});
test('No defenses eventually leak and cause game loss without stuck packets',()=>{
 const g=new FirewallGame();g.startWave();step(g,35);assert.equal(g.phase,'ready');assert.ok(g.integrity<20);
 while(g.phase==='ready'){g.startWave();step(g,70);}assert.equal(g.phase,'lost');assert.equal(g.integrity,0);
});
test('Damage honors shields and armor, kills pay credits exactly once',()=>{
 const g=new FirewallGame();const e=g.spawnEnemy('shield');let before=g.credits;
 g.damageEnemy(e,60);assert.equal(e.hp,e.maxHp);assert.equal(e.shield,10);
 g.damageEnemy(e,30);assert.equal(e.shield,0);assert.equal(e.hp,e.maxHp-20);
 g.damageEnemy(e,1e4);assert.equal(e.alive,false);assert.equal(g.credits,before+ENEMY_TYPES.shield.reward);
 g.damageEnemy(e,1e4);assert.equal(g.credits,before+ENEMY_TYPES.shield.reward);
});
test('No tower can see stealth from full range except IDS',()=>{
 const g=new FirewallGame();g.credits=1000;const a=g.placeTower(2,'firewall').tower,b=g.placeTower(16,'ids').tower;
 const e=g.spawnEnemy('stealth',0);e.x=a.x+130;e.y=a.y;e.distance=300;
 assert.equal(g.targetFor(a),null);e.x=b.x+130;e.y=b.y;assert.equal(g.targetFor(b)?.id,e.id);
});
test('Rate limiter slows a real enemy and restores it after its expiration',()=>{
 const g=new FirewallGame();const e=g.spawnEnemy('probe',0);e.slowFactor=.56;e.slowUntil=2;g.startWave();const initial=e.distance;g.update(1/120);assert.ok(e.distance-initial<e.speed/120);
 step(g,3);assert.ok(g.time>2);assert.ok(e.distance>50);
});
test('Wave sequencing is deterministic, exactly eight waves with Titan last',()=>{
 const g=new FirewallGame();assert.equal(WAVES.length,8);g.waveIndex=7;g.startWave();assert.equal(g.getWaveEnemy(g.toSpawn-1),'titan');
 assert.equal(g.getWaveEnemy(0),WAVES[7].pool[0]);
});
test('Damage and range improve with tower level',()=>{
 const g=new FirewallGame();g.credits=5000;const t=g.placeTower(2,'firewall').tower;
 const e=g.spawnEnemy('probe',0);e.x=t.x+168;e.y=t.y;e.distance=100;
 assert.equal(g.targetFor(t),null);g.upgradeTower(2);assert.equal(g.targetFor(t)?.id,e.id);
});
test('Snapshot and event stream exclude secrets and remain bounded',()=>{
 const g=new FirewallGame();for(let i=0;i<200;i++)g.emit('test',{i});assert.equal(g.events.length,160);
 assert.equal(g.consumeEvents().length,160);assert.equal(g.events.length,0);assert.deepEqual(Object.keys(g.snapshot()),['phase','wave','credits','integrity','score','kills','towers','enemies']);
});
test('A well-planned and adequately funded mixed-defense layout can clear all eight waves',()=>{
 const g=new FirewallGame();
 const buildPlan=[[15,'firewall'],[19,'firewall'],[1,'firewall'],[5,'firewall'],[12,'firewall'],[18,'pulse'],[14,'ids'],[17,'ids'],[3,'cache'],[9,'cache'],[6,'firewall'],[13,'firewall']];
 for(let wave=0;wave<WAVES.length;wave++){
   for(const [pad,type] of buildPlan){if(!g.getTowerAt(pad))g.placeTower(pad,type);}
   for(const pad of [15,19,14])if(g.getTowerAt(pad)&&g.credits>=200)g.upgradeTower(pad);
   assert.ok(g.startWave(),`wave ${wave+1} should start`);
   for(let frame=0;frame<120*115&&g.phase==='wave';frame++)g.update(1/120);
   assert.notEqual(g.phase,'lost',`no unexpected defeat in wave ${wave+1}`);
 }
 assert.equal(g.phase,'won');assert.equal(g.waveIndex,8);assert.ok(g.kills>150);assert.ok(g.integrity>0);
});
test('Underpowered layouts can lose later; resources never go negative and restart resets state',()=>{
 const g=new FirewallGame(21);g.placeTower(15,'firewall');
 for(let w=0;w<8&&g.phase!=='lost'&&g.phase!=='won';w++){
   assert.ok(g.startWave());for(let n=0;n<120*115&&g.phase==='wave';n++)g.update(1/120);
 }
 assert.equal(g.phase,'lost');assert.ok(g.credits>=0);
 g.reset();assert.equal(g.phase,'ready');assert.equal(g.integrity,20);assert.equal(g.towers.length,0);assert.equal(g.credits,290);
});
