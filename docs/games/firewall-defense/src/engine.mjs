/** FIREWALL DEFENSE // deterministic strategy simulation, no browser dependencies. */
export const WORLD = Object.freeze({width:960,height:624,cell:66,originX:51,originY:47,columns:12,rows:8});
const P = (c,r) => ({x:WORLD.originX+c*WORLD.cell+WORLD.cell/2,y:WORLD.originY+r*WORLD.cell+WORLD.cell/2});
export const ROUTES = [
  [[-1,2],[0,2],[1,2],[2,2],[3,2],[3,1],[4,1],[5,1],[6,1],[6,2],[7,2],[8,2],[9,2],[9,3],[10,3],[11,3],[12,3]],
  [[-1,5],[0,5],[1,5],[2,5],[3,5],[3,6],[4,6],[5,6],[6,6],[6,5],[7,5],[8,5],[9,5],[9,4],[10,4],[11,4],[12,4]]
].map(route=>route.map(([c,r])=>P(c,r)));
export const PADS = [[1,1],[2,3],[4,2],[5,2],[7,1],[8,3],[10,2],[1,6],[2,4],[4,5],[5,5],[7,6],[8,4],[10,5],[4,3],[5,3],[6,3],[6,4],[7,4],[5,4],[9,1],[9,6]].map(([c,r],id)=>({id,c,r,...P(c,r)}));
export const TOWER_TYPES = Object.freeze({
  firewall:{name:'Firewall',code:'FW',cost:95,range:165,damage:30,cooldown:0.73,projectile:480,color:'#B6FF3B',desc:'Precision packet interceptor',upgrade:'+30% damage, +7% range'},
  cache:{name:'Rate Limiter',code:'RL',cost:110,range:160,damage:12,cooldown:0.82,projectile:380,color:'#66D9E8',desc:'Slow hostile traffic by 44%',upgrade:'Longer slowdown, faster fire'},
  pulse:{name:'Pulse Node',code:'AOE',cost:145,range:105,damage:17,cooldown:1.28,projectile:0,color:'#FFD166',desc:'Radial area-of-effect burst',upgrade:'Wider pulse and stronger damage'},
  ids:{name:'IDS Scanner',code:'IDS',cost:160,range:195,damage:22,cooldown:1.12,projectile:0,color:'#C99BFF',desc:'Reveals stealth, chains to 3 targets',upgrade:'+1 chain target each level'},
  scatter:{name:'Scatter Cannon',code:'SC',cost:180,range:158,damage:16,cooldown:1.14,projectile:430,color:'#FFAA78',desc:'Triple-shot bursts against close-range traffic',upgrade:'More damage and faster volleys'},
  rail:{name:'Rail Lance',code:'RLX',cost:265,range:275,damage:95,cooldown:2.48,projectile:0,color:'#E2FD83',desc:'Piercing beam damages multiple aligned targets',upgrade:'Higher beam energy and penetration'}
});
export const ENEMY_TYPES = Object.freeze({
  probe:{name:'Probe',hp:70,speed:67,reward:12,leak:1,color:'#C6E3DA',radius:11},
  sprint:{name:'Burst',hp:45,speed:118,reward:14,leak:1,color:'#50DDF1',radius:9},
  armored:{name:'Armored',hp:165,speed:48,reward:20,leak:2,color:'#EFAD63',radius:14,armor:5},
  stealth:{name:'Stealth',hp:72,speed:84,reward:19,leak:2,color:'#BF90EA',radius:10,stealth:true},
  shield:{name:'Shielded',hp:125,shield:70,speed:60,reward:23,leak:2,color:'#79B6FF',radius:13},
  titan:{name:'Titan',hp:560,shield:190,speed:35,reward:110,leak:6,color:'#F77E7E',radius:23,armor:6,boss:true},
  swarm:{name:'Swarm',hp:38,speed:142,reward:9,leak:1,color:'#9DDFF4',radius:8},
  splitter:{name:'Splitter',hp:150,speed:61,reward:27,leak:2,color:'#D1E77D',radius:12,armor:2,split:true},
  jammer:{name:'Jammer',hp:185,speed:54,reward:34,leak:3,color:'#FFAD85',radius:14,armor:3,jammer:true},
  regen:{name:'Regenerator',hp:205,speed:49,reward:35,leak:3,color:'#9BE8BA',radius:15,armor:3,regen:true},
  sentinel:{name:'Sentinel',hp:900,shield:360,speed:30,reward:195,leak:8,color:'#FF9D8B',radius:25,armor:8,boss:true,jammer:true},
  overseer:{name:'Overseer',hp:1450,shield:620,speed:26,reward:300,leak:12,color:'#F96A9A',radius:28,armor:10,boss:true,jammer:true,regen:true}
});
// Six acts of five authored missions. The counts exclude any boss appended at the end.
const W=(name,hint,count,pool,boss=null)=>Object.freeze({name,hint,count,pool,boss});
export const WAVES = Object.freeze([
  W('Port Scan','Establish your first defenses on both paths',10,['probe']),
  W('Burst Traffic','Fast probes test your early reaction time',14,['probe','sprint','sprint']),
  W('Heavy Payloads','Armored traffic needs focused fire',16,['probe','armored','sprint']),
  W('Silent Intrusion','IDS scanners reveal stealth threats',18,['stealth','probe','sprint']),
  W('Gateway Titan','BOSS // The first heavy breach attempt',18,['armored','shield','probe'],'titan'),
  W('Shield Storm','Layered shields demand sustained damage',21,['shield','probe','armored']),
  W('Packet Fragmentation','Splitters create additional attackers on defeat',22,['splitter','probe','sprint']),
  W('Saturation Attack','Swarm packets threaten both gateways',26,['swarm','sprint','probe','probe']),
  W('Blackout Probe','Jammers disrupt nearby defenses',26,['jammer','stealth','shield']),
  W('Sentinel Protocol','BOSS // A jammer-protected sentinel approaches',28,['jammer','shield','sprint'],'sentinel'),
  W('Supply Chain Breach','Stealth and armored units cooperate',29,['stealth','armored','splitter']),
  W('Regenerative Payload','Repair-capable enemies need concentrated damage',29,['regen','shield','sprint']),
  W('Twin Lane Siege','Heavy pressure on both ingress routes',32,['armored','splitter','swarm','shield']),
  W('Ghost Traffic','Stealth bursts mix with disrupting jammers',34,['stealth','jammer','sprint']),
  W('Titan Recompiled','BOSS // The Titan returns reinforced',34,['regen','armored','shield'],'titan'),
  W('Cache Poisoning','Fast traffic blends with regenerative threats',36,['swarm','regen','sprint','shield']),
  W('Zero Trust Collapse','Jammers and stealth nodes pressure the core',38,['jammer','stealth','splitter','shield']),
  W('Flood of Forks','Splitters create secondary swarms',40,['splitter','splitter','swarm','armored']),
  W('Deep Packet Assault','Elites lead shielded and armored packets',41,['shield','armored','regen','jammer']),
  W('Sentinel Reboot','BOSS // A second sentinel drives the breach',40,['jammer','regen','shield'],'sentinel'),
  W('Kernel Panic','Full-spectrum threats attack at once',43,['armored','stealth','jammer','sprint']),
  W('Replication Storm','Replicating traffic congests both lanes',45,['splitter','swarm','regen','shield']),
  W('Critical Vulnerability','High-speed waves require careful timing',46,['sprint','swarm','jammer','stealth']),
  W('No Safe Route','All defenses are tested simultaneously',48,['armored','shield','regen','splitter','jammer']),
  W('Titan Uprising','BOSS // Heavy armor at maximum pressure',45,['armored','regen','shield','jammer'],'titan'),
  W('Final Handshake','High-density encrypted attack traffic',49,['shield','stealth','swarm','splitter']),
  W('Quarantine Failure','Jam-resistant timing is essential',50,['jammer','regen','shield','armored']),
  W('System Meltdown','Rapid splitters push both pathways',52,['splitter','swarm','sprint','stealth']),
  W('Absolute Zero-Day','Every enemy capability enters the network',54,['jammer','shield','armored','regen','stealth','splitter']),
  W('The Final Overseer','FINAL BOSS // Protect the core against the Overseer',55,['jammer','regen','shield','armored','splitter','stealth'],'overseer')
]);
export const MAX_LEVEL=5;
export const ABILITIES=Object.freeze({
  emp:{name:'EMP FREEZE',cost:120,cooldown:52,duration:2.7,description:'Freeze every active hostile packet for 2.7s'},
  overclock:{name:'OVERCLOCK',cost:155,cooldown:62,duration:7,description:'Increase all tower firing rates for 7s'},
  shield:{name:'CORE SHIELD',cost:135,cooldown:58,charges:7,description:'Absorb 7 points of incoming core damage'}
});
// Saturating curves avoid zero/negative spawn delays and unbounded threat speed.
export const spawnInterval=(index,noise=0)=>Math.max(.19,.76*Math.exp(-.042*Math.max(0,index)))+Math.max(0,noise)*.11;
export const enemyHealthScale=index=>1+.10*Math.max(0,index)+.0032*Math.max(0,index)**2;
export const enemySpeedScale=index=>1+Math.min(.42,.016*Math.max(0,index));
export function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y);}
export function routeLength(route){let total=0;for(let i=1;i<route.length;i++)total+=distance(route[i-1],route[i]);return total;}
export const ROUTE_LENGTHS=ROUTES.map(routeLength);
export function locationAlong(route,dist){
  if(dist<=0)return {...route[0]};
  let remain=dist;
  for(let i=1;i<route.length;i++){
    const len=distance(route[i-1],route[i]);
    if(remain<=len){const t=remain/len;return {x:route[i-1].x+(route[i].x-route[i-1].x)*t,y:route[i-1].y+(route[i].y-route[i-1].y)*t};}
    remain-=len;
  }
  return {...route[route.length-1]};
}
// Segment and circle test prevents projectile tunneling for high velocities.
export function segmentCircleHit(ax,ay,bx,by,cx,cy,r){
  const dx=bx-ax,dy=by-ay,den=dx*dx+dy*dy;
  const t=den>0?Math.max(0,Math.min(1,((cx-ax)*dx+(cy-ay)*dy)/den)):0;
  const x=ax+t*dx,y=ay+t*dy;
  return (x-cx)**2+(y-cy)**2<=r*r;
}
export function makeRng(seed){let value=seed>>>0||1;return ()=>{value^=value<<13;value^=value>>>17;value^=value<<5;return (value>>>0)/4294967296;};}
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
export class FirewallGame {
  constructor(seed=0xB6FF3B){this.seed=seed;this.reset();}
  reset(){
    this.random=makeRng(this.seed);this.phase='ready';this.waveIndex=0;this.credits=290;this.integrity=20;this.score=0;this.kills=0;this.towers=[];this.enemies=[];this.projectiles=[];this.effects=[];this.time=0;this.enemyId=0;this.towerId=0;this.shotId=0;this.spawned=0;this.toSpawn=0;this.spawnTimer=0;this.selectedPad=null;this.selectedType='firewall';this.speed=1;this.audio=true;this.message='Build defenses on glowing nodes, then launch Wave 01.';this.events=[];this.combo=0;this.pendingWaveReward=0;this.abilityLast={emp:-Infinity,overclock:-Infinity,shield:-Infinity};this.overclockUntil=0;this.coreShield=0;this.endless=false;this.bossKills=0;
  }
  emit(type,data={}){this.events.push({type,...data});if(this.events.length>160)this.events.splice(0,this.events.length-160);}
  consumeEvents(){return this.events.splice(0);}
  selectType(type){if(!TOWER_TYPES[type])return false;this.selectedType=type;return true;}
  getTowerAt(padId){return this.towers.find(t=>t.padId===padId);}
  getTowerCost(type){return TOWER_TYPES[type]?.cost??Infinity;}
  placeTower(padId,type=this.selectedType){
    if(!PADS.some(p=>p.id===padId)||!TOWER_TYPES[type]||this.phase==='lost'||this.phase==='won')return {ok:false,reason:'Invalid build position'};
    if(this.getTowerAt(padId))return {ok:false,reason:'Node is occupied'};
    const spec=TOWER_TYPES[type];if(this.credits<spec.cost)return {ok:false,reason:'Insufficient bandwidth credits'};
    const pad=PADS.find(p=>p.id===padId);this.credits-=spec.cost;
    const tower={id:++this.towerId,type,padId,x:pad.x,y:pad.y,level:1,spent:spec.cost,cooldown:this.random()*.25,angle:-Math.PI/2,shots:0};
    this.towers.push(tower);this.selectedPad=padId;this.emit('build',{x:pad.x,y:pad.y,towerType:type});return {ok:true,tower};
  }
  upgradeTower(padId){
    const tower=this.getTowerAt(padId);if(!tower)return {ok:false,reason:'Select a defense'};
    if(tower.level>=MAX_LEVEL)return {ok:false,reason:'Maximum level reached'};
    const cost=this.upgradeCost(tower);
    if(this.credits<cost)return {ok:false,reason:'Not enough bandwidth credits'};
    this.credits-=cost;tower.level++;tower.spent+=cost;tower.cooldown=Math.min(tower.cooldown,.25);
    this.emit('upgrade',{x:tower.x,y:tower.y,level:tower.level});return {ok:true,cost};
  }
  upgradeCost(tower){return Math.round(TOWER_TYPES[tower.type].cost*(.7+.43*Math.pow(tower.level-1,1.25)));}
  currentWave(){if(this.waveIndex<WAVES.length)return WAVES[this.waveIndex];const i=this.waveIndex-WAVES.length;const pool=['probe','sprint','armored','shield','stealth','splitter','jammer','regen','swarm'];return W(`Endless ${i+1}`, 'SURVIVAL // High-pressure randomized threat mixture', Math.min(85,55+Math.floor(i*1.35)),[pool[i%pool.length],pool[(i+2)%pool.length],pool[(i+5)%pool.length],pool[(i+7)%pool.length]],(i+1)%5===0?(i%2?'sentinel':'overseer'):null);}
  abilityState(type){const spec=ABILITIES[type];if(!spec)return null;return {cooldown:Math.max(0,spec.cooldown-(this.time-this.abilityLast[type])),cost:spec.cost,ready:this.phase==='wave'&&this.credits>=spec.cost&&this.time-this.abilityLast[type]>=spec.cooldown};}
  activateAbility(type){const spec=ABILITIES[type];if(!spec)return {ok:false,reason:'Unknown protocol'};if(this.phase!=='wave')return {ok:false,reason:'Activate during an attack wave'};const state=this.abilityState(type);if(state.cooldown>0)return {ok:false,reason:`Cooldown ${Math.ceil(state.cooldown)}s`};if(this.credits<spec.cost)return {ok:false,reason:'Insufficient bandwidth credits'};
    if(type==='shield'&&this.coreShield>=14)return {ok:false,reason:'Core shield capacity full'};
    if(type==='emp'&&!this.enemies.length)return {ok:false,reason:'No hostile packets to freeze'};
    this.credits-=spec.cost;this.abilityLast[type]=this.time;
    if(type==='emp'){for(const enemy of this.enemies)enemy.frozenUntil=Math.max(enemy.frozenUntil||0,this.time+spec.duration);this.emit('emp',{x:WORLD.width/2,y:WORLD.height/2,color:'#66D9E8'});}
    else if(type==='overclock'){this.overclockUntil=Math.max(this.overclockUntil,this.time+spec.duration);this.emit('overclock',{x:WORLD.width/2,y:WORLD.height/2,color:'#B6FF3B'});}
    else{this.coreShield=Math.min(14,this.coreShield+spec.charges);this.emit('coreShield',{x:913,y:312,color:'#B6FF3B'});}
    this.emit('ability',{ability:type,cost:spec.cost});return {ok:true,cost:spec.cost};
  }
  startEndless(){if(this.phase!=='won'||this.waveIndex<WAVES.length)return false;this.endless=true;this.phase='ready';this.message='ENDLESS PROTOCOL // SURVIVE AS LONG AS POSSIBLE';this.emit('endlessStart');return true;}
  sellTower(padId){const tower=this.getTowerAt(padId);if(!tower)return {ok:false,reason:'No defense selected'};
    const refund=Math.round(tower.spent*.65);this.credits+=refund;this.towers=this.towers.filter(t=>t!==tower);this.emit('sell',{x:tower.x,y:tower.y});return {ok:true,refund};}
  startWave(){
    if(this.phase!=='ready'||(this.waveIndex>=WAVES.length&&!this.endless))return false;
    this.phase='wave';this.spawned=0;this.toSpawn=this.currentWave().count+(this.currentWave().boss?1:0);this.spawnTimer=0;this.combo=0;
    this.message=`WAVE ${String(this.waveIndex+1).padStart(2,'0')} // ${this.currentWave().name.toUpperCase()}`;
    this.emit('waveStart',{wave:this.waveIndex+1});return true;
  }
  spawnEnemy(type,routeIndex=this.random()<.5?0:1){
    const spec=ENEMY_TYPES[type];if(!spec)throw new Error(`Unknown enemy ${type}`);
    const boost=enemyHealthScale(this.waveIndex);
    const enemy={id:++this.enemyId,type,routeIndex,distance:0,x:ROUTES[routeIndex][0].x,y:ROUTES[routeIndex][0].y,
      hp:Math.round(spec.hp*boost),maxHp:Math.round(spec.hp*boost),shield:Math.round((spec.shield||0)*boost),maxShield:Math.round((spec.shield||0)*boost),
      speed:spec.speed*enemySpeedScale(this.waveIndex),radius:spec.radius,slowUntil:0,slowFactor:1,frozenUntil:0,jamTimer:2.8,regenTimer:2.3,alive:true,alpha:1,hitFlash:0};
    this.enemies.push(enemy);this.emit('spawn',{x:enemy.x,y:enemy.y,enemyType:type});return enemy;
  }
  getWaveEnemy(i){
    const wave=this.currentWave();if(wave.boss&&i===this.toSpawn-1)return wave.boss;return wave.pool[i%wave.pool.length];
  }
  targetFor(tower){
    const spec=TOWER_TYPES[tower.type];const radius=spec.range*(1+.08*(tower.level-1));let best=null,bestProgress=-1;
    for(const enemy of this.enemies){
      if(!enemy.alive)continue;
      const maxRange=ENEMY_TYPES[enemy.type].stealth&&tower.type!=='ids'?radius*.43:radius;
      if(distance(tower,enemy)>maxRange)continue;
      const progress=enemy.distance/ROUTE_LENGTHS[enemy.routeIndex];
      if(progress>bestProgress){best=enemy;bestProgress=progress;}
    }
    return best;
  }
  damageEnemy(enemy,damage,pierce=0){
    if(!enemy?.alive)return 0;const spec=ENEMY_TYPES[enemy.type];let dmg=Math.max(1,damage-Math.max(0,(spec.armor||0)-pierce));
    if(enemy.shield>0){const shieldDmg=Math.min(enemy.shield,dmg);enemy.shield-=shieldDmg;dmg-=shieldDmg;}
    enemy.hp-=dmg;enemy.hitFlash=.12;
    if(enemy.hp<=0){enemy.alive=false;if(spec.boss)this.bossKills++;this.score+=spec.reward*10;this.credits+=spec.reward;this.kills++;this.combo++;
      this.emit('kill',{x:enemy.x,y:enemy.y,enemyType:enemy.type,points:spec.reward*10});
      if(spec.split){for(let j=0;j<2;j++){const child=this.spawnEnemy('swarm',enemy.routeIndex);child.distance=Math.max(0,enemy.distance-18+j*20);Object.assign(child,locationAlong(ROUTES[child.routeIndex],child.distance));}this.emit('split',{x:enemy.x,y:enemy.y,color:spec.color});}
      if(this.combo%8===0){this.credits+=20;this.emit('bonus',{x:enemy.x,y:enemy.y,value:20});}}
    else this.emit('hit',{x:enemy.x,y:enemy.y,color:spec.color});
    return dmg;
  }
  towerFire(tower){
    const spec=TOWER_TYPES[tower.type];const target=this.targetFor(tower);if(!target)return false;
    tower.angle=Math.atan2(target.y-tower.y,target.x-tower.x);tower.shots++;
    const boost=1+.34*(tower.level-1);
    if(tower.type==='pulse'){
      const r=spec.range*(.6+.08*(tower.level-1));let hits=0;
      for(const e of this.enemies)if(e.alive&&distance(tower,e)<r){this.damageEnemy(e,spec.damage*(1+.4*(tower.level-1)),3);hits++;}
      this.emit('pulse',{x:tower.x,y:tower.y,r,color:spec.color,hits});
    }else if(tower.type==='ids'){
      const visited=new Set();let current=target,from={x:tower.x,y:tower.y};
      for(let j=0;j<2+tower.level;j++){
        if(!current)break;visited.add(current.id);this.damageEnemy(current,spec.damage*(1+.32*(tower.level-1)),4);
        this.emit('beam',{x:from.x,y:from.y,tx:current.x,ty:current.y,color:spec.color,chain:j});
        const candidates=this.enemies.filter(e=>e.alive&&!visited.has(e.id)&&distance(e,current)<115);
        candidates.sort((a,b)=>distance(a,current)-distance(b,current));
        from={x:current.x,y:current.y};current=candidates[0]||null;
      }
    }else if(tower.type==='rail'){
      const range=spec.range*(1+.08*(tower.level-1)),cos=Math.cos(tower.angle),sin=Math.sin(tower.angle);
      const tx=tower.x+cos*range,ty=tower.y+sin*range;
      const hits=this.enemies.filter(e=>e.alive&&distance(tower,e)<=range+e.radius&&segmentCircleHit(tower.x,tower.y,tx,ty,e.x,e.y,e.radius+9))
        .sort((a,b)=>distance(tower,a)-distance(tower,b)).slice(0,3+Math.floor(tower.level/2));
      hits.forEach((enemy,j)=>this.damageEnemy(enemy,spec.damage*boost*Math.pow(.81,j),8));
      this.emit('rail',{x:tower.x,y:tower.y,tx,ty,color:spec.color,hits:hits.length});
    }else{
      const createShot=(enemy,offset=0)=>{
        const angle=Math.atan2(enemy.y-tower.y,enemy.x-tower.x)+offset;
        this.projectiles.push({id:++this.shotId,x:tower.x+Math.cos(tower.angle+Math.PI/2)*Math.sign(offset)*10,y:tower.y+Math.sin(tower.angle+Math.PI/2)*Math.sign(offset)*10,targetId:enemy.id,vx:Math.cos(angle)*spec.projectile,vy:Math.sin(angle)*spec.projectile,spd:spec.projectile,type:tower.type,damage:spec.damage*boost,age:0,ttl:1.7});
      };
      if(tower.type==='scatter'){
        const others=this.enemies.filter(e=>e.alive&&e.id!==target.id&&distance(tower,e)<spec.range*(1+.08*(tower.level-1)))
          .sort((a,b)=>distance(tower,a)-distance(tower,b));
        const targets=[target,others[0]||target,others[1]||target];
        targets.forEach((enemy,j)=>createShot(enemy,(j-1)*.085));
      }else createShot(target);
      this.emit('shot',{x:tower.x,y:tower.y,towerType:tower.type});
    }
    return true;
  }
  update(dt){
    if(this.phase!=='wave')return;
    const d=clamp(dt,0,1/20);this.time+=d;
    const wave=this.currentWave();
    if(this.spawned<this.toSpawn){this.spawnTimer-=d;
      if(this.spawnTimer<=0){this.spawnEnemy(this.getWaveEnemy(this.spawned),this.spawned%2);this.spawned++;
        this.spawnTimer=spawnInterval(this.waveIndex,this.random());}}
    for(const enemy of this.enemies){if(!enemy.alive)continue;
      enemy.hitFlash=Math.max(0,enemy.hitFlash-d);
      if(ENEMY_TYPES[enemy.type].regen){enemy.regenTimer-=d;if(enemy.regenTimer<=0){enemy.hp=Math.min(enemy.maxHp,enemy.hp+Math.max(4,enemy.maxHp*.027));enemy.regenTimer=2.7;this.emit('regen',{x:enemy.x,y:enemy.y,color:'#9BE8BA'});}}
      if(ENEMY_TYPES[enemy.type].jammer){enemy.jamTimer-=d;if(enemy.jamTimer<=0){for(const tower of this.towers)if(distance(enemy,tower)<118)tower.jammedUntil=Math.max(tower.jammedUntil||0,this.time+1.35);enemy.jamTimer=3.9;this.emit('jam',{x:enemy.x,y:enemy.y,color:'#FFAD85'});}}
      const factor=this.time<(enemy.frozenUntil||0)?0:this.time<enemy.slowUntil?enemy.slowFactor:1;
      enemy.distance+=enemy.speed*factor*d;
      if(enemy.distance>=ROUTE_LENGTHS[enemy.routeIndex]){
        enemy.alive=false;const leak=ENEMY_TYPES[enemy.type].leak;const absorbed=Math.min(this.coreShield,leak);this.coreShield-=absorbed;this.integrity-=leak-absorbed;this.combo=0;this.emit('leak',{x:enemy.x,y:enemy.y,damage:leak-absorbed,absorbed});
        if(this.integrity<=0){this.integrity=0;this.phase='lost';this.message='CORE OFFLINE // BREACH DETECTED';this.emit('gameLost');break;}}
      else Object.assign(enemy,locationAlong(ROUTES[enemy.routeIndex],enemy.distance));
    }
    if(this.phase==='lost'){this.enemies=this.enemies.filter(e=>e.alive);return;}
    for(const tower of this.towers){if(this.time<(tower.jammedUntil||0))continue;tower.cooldown-=d;
      if(tower.cooldown<=0&&this.towerFire(tower)){
        const spec=TOWER_TYPES[tower.type];tower.cooldown=spec.cooldown/(1+.10*(tower.level-1))/(this.time<this.overclockUntil?1.8:1);}
      else if(tower.cooldown<-.08)tower.cooldown=-.08;
    }
    for(const shot of this.projectiles){
      const target=this.enemies.find(e=>e.id===shot.targetId&&e.alive);
      if(!target){shot.ttl=0;continue;}
      shot.age+=d;shot.ttl-=d;
      const ax=shot.x,ay=shot.y;
      const ang=Math.atan2(target.y-shot.y,target.x-shot.x);
      shot.vx=Math.cos(ang)*shot.spd;shot.vy=Math.sin(ang)*shot.spd;
      shot.x+=shot.vx*d;shot.y+=shot.vy*d;
      if(segmentCircleHit(ax,ay,shot.x,shot.y,target.x,target.y,target.radius+7)){
        this.damageEnemy(target,shot.damage,shot.type==='firewall'?4:0);
        if(shot.type==='cache'&&target.alive){target.slowFactor=.56;target.slowUntil=this.time+1.7;this.emit('slow',{x:target.x,y:target.y});}
        this.emit('impact',{x:shot.x,y:shot.y,color:TOWER_TYPES[shot.type].color});shot.ttl=0;
      }
    }
    this.projectiles=this.projectiles.filter(p=>p.ttl>0);
    this.enemies=this.enemies.filter(e=>e.alive);
    if(this.phase==='wave'&&this.spawned>=this.toSpawn&&this.enemies.length===0){
      const bonus=70+this.waveIndex*19;this.credits+=bonus;this.score+=bonus*3;this.waveIndex++;
      this.emit('waveClear',{bonus,wave:this.waveIndex});
      if(this.waveIndex>=WAVES.length&&!this.endless){this.phase='won';this.message='NETWORK SECURED // ALL WAVES CLEARED';this.emit('gameWon');}
      else {this.phase='ready';this.message=`WAVE CLEARED +${bonus} // PREPARE ${this.currentWave().name.toUpperCase()}`;}
    }
  }
  snapshot(){return {phase:this.phase,wave:this.waveIndex+1,credits:this.credits,integrity:this.integrity,score:this.score,kills:this.kills,towers:this.towers.length,enemies:this.enemies.length};}
}
