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
  ids:{name:'IDS Scanner',code:'IDS',cost:160,range:195,damage:22,cooldown:1.12,projectile:0,color:'#C99BFF',desc:'Reveals stealth, chains to 3 targets',upgrade:'+1 chain target each level'}
});
export const ENEMY_TYPES = Object.freeze({
  probe:{name:'Probe',hp:70,speed:67,reward:12,leak:1,color:'#C6E3DA',radius:11},
  sprint:{name:'Burst',hp:45,speed:118,reward:14,leak:1,color:'#50DDF1',radius:9},
  armored:{name:'Armored',hp:165,speed:48,reward:20,leak:2,color:'#EFAD63',radius:14,armor:5},
  stealth:{name:'Stealth',hp:72,speed:84,reward:19,leak:2,color:'#BF90EA',radius:10,stealth:true},
  shield:{name:'Shielded',hp:125,shield:70,speed:60,reward:23,leak:2,color:'#79B6FF',radius:13},
  titan:{name:'Titan',hp:560,shield:190,speed:35,reward:100,leak:6,color:'#F77E7E',radius:23,armor:6}
});
export const WAVES = [
  {name:'Port Scan',hint:'Probes on both network paths',count:10,pool:['probe']},
  {name:'Burst Traffic',hint:'Fast packets—prioritize rate limiting',count:15,pool:['probe','sprint','sprint']},
  {name:'Heavy Payloads',hint:'Armored threats resist low damage',count:16,pool:['probe','armored','sprint']},
  {name:'Silent Intrusion',hint:'IDS detects stealth at full range',count:20,pool:['stealth','probe','sprint']},
  {name:'Shield Storm',hint:'Shields absorb hits before hull',count:22,pool:['shield','probe','armored']},
  {name:'Coordinated Swarm',hint:'Mixed traffic attacks both paths',count:27,pool:['sprint','probe','stealth','shield']},
  {name:'Zero-Day Flood',hint:'High density and hard targets',count:31,pool:['armored','stealth','shield','sprint']},
  {name:'Core Breach',hint:'A Titan arrives in the final assault',count:32,pool:['armored','sprint','shield','stealth','probe']}
];
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
    this.random=makeRng(this.seed);this.phase='ready';this.waveIndex=0;this.credits=290;this.integrity=20;this.score=0;this.kills=0;this.towers=[];this.enemies=[];this.projectiles=[];this.effects=[];this.time=0;this.enemyId=0;this.towerId=0;this.shotId=0;this.spawned=0;this.toSpawn=0;this.spawnTimer=0;this.selectedPad=null;this.selectedType='firewall';this.speed=1;this.audio=true;this.message='Build defenses on glowing nodes, then launch Wave 01.';this.events=[];this.combo=0;this.pendingWaveReward=0;
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
    if(tower.level>=3)return {ok:false,reason:'Maximum level reached'};
    const cost=Math.round(TOWER_TYPES[tower.type].cost*(.7+.3*(tower.level-1)));
    if(this.credits<cost)return {ok:false,reason:'Not enough bandwidth credits'};
    this.credits-=cost;tower.level++;tower.spent+=cost;tower.cooldown=Math.min(tower.cooldown,.25);
    this.emit('upgrade',{x:tower.x,y:tower.y,level:tower.level});return {ok:true,cost};
  }
  sellTower(padId){const tower=this.getTowerAt(padId);if(!tower)return {ok:false,reason:'No defense selected'};
    const refund=Math.round(tower.spent*.65);this.credits+=refund;this.towers=this.towers.filter(t=>t!==tower);this.emit('sell',{x:tower.x,y:tower.y});return {ok:true,refund};}
  startWave(){
    if(this.phase!=='ready'||this.waveIndex>=WAVES.length)return false;
    this.phase='wave';this.spawned=0;this.toSpawn=WAVES[this.waveIndex].count+(this.waveIndex===7?1:0);this.spawnTimer=0;this.combo=0;
    this.message=`WAVE ${String(this.waveIndex+1).padStart(2,'0')} // ${WAVES[this.waveIndex].name.toUpperCase()}`;
    this.emit('waveStart',{wave:this.waveIndex+1});return true;
  }
  spawnEnemy(type,routeIndex=this.random()<.5?0:1){
    const spec=ENEMY_TYPES[type];if(!spec)throw new Error(`Unknown enemy ${type}`);
    const boost=1+Math.max(0,this.waveIndex)*.13;
    const enemy={id:++this.enemyId,type,routeIndex,distance:0,x:ROUTES[routeIndex][0].x,y:ROUTES[routeIndex][0].y,
      hp:Math.round(spec.hp*boost),maxHp:Math.round(spec.hp*boost),shield:Math.round((spec.shield||0)*boost),maxShield:Math.round((spec.shield||0)*boost),
      speed:spec.speed*(1+this.waveIndex*.025),radius:spec.radius,slowUntil:0,slowFactor:1,alive:true,alpha:1,hitFlash:0};
    this.enemies.push(enemy);this.emit('spawn',{x:enemy.x,y:enemy.y,enemyType:type});return enemy;
  }
  getWaveEnemy(i){
    if(this.waveIndex===7&&i===this.toSpawn-1)return 'titan';
    const wave=WAVES[this.waveIndex];return wave.pool[i%wave.pool.length];
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
    if(enemy.hp<=0){enemy.alive=false;this.score+=spec.reward*10;this.credits+=spec.reward;this.kills++;this.combo++;
      this.emit('kill',{x:enemy.x,y:enemy.y,enemyType:enemy.type,points:spec.reward*10});
      if(this.combo%8===0){this.credits+=20;this.emit('bonus',{x:enemy.x,y:enemy.y,value:20});}}
    else this.emit('hit',{x:enemy.x,y:enemy.y,color:spec.color});
    return dmg;
  }
  towerFire(tower){
    const spec=TOWER_TYPES[tower.type];const target=this.targetFor(tower);if(!target)return false;
    tower.angle=Math.atan2(target.y-tower.y,target.x-tower.x);tower.shots++;
    if(tower.type==='pulse'){
      const r=spec.range*(.6+.08*(tower.level-1));let hits=0;
      for(const e of this.enemies)if(e.alive&&distance(tower,e)<r){this.damageEnemy(e,spec.damage*(1+.4*(tower.level-1)),3);hits++;}
      this.emit('pulse',{x:tower.x,y:tower.y,r,color:spec.color,hits});
    }else if(tower.type==='ids'){
      const visited=new Set();let current=target;
      for(let j=0;j<2+tower.level;j++){
        if(!current)break;visited.add(current.id);this.damageEnemy(current,spec.damage*(1+.32*(tower.level-1)),4);
        this.emit('beam',{x:tower.x,y:tower.y,tx:current.x,ty:current.y,color:spec.color,chain:j});
        const candidates=this.enemies.filter(e=>e.alive&&!visited.has(e.id)&&distance(e,current)<115);
        candidates.sort((a,b)=>distance(a,current)-distance(b,current));
        if(candidates.length){tower={...tower,x:current.x,y:current.y};current=candidates[0];}else current=null;
      }
    }else{
      this.projectiles.push({id:++this.shotId,x:tower.x,y:tower.y,targetId:target.id,vx:Math.cos(tower.angle)*spec.projectile,vy:Math.sin(tower.angle)*spec.projectile,spd:spec.projectile,type:tower.type,damage:spec.damage*(1+.34*(tower.level-1)),age:0,ttl:1.6});
      this.emit('shot',{x:tower.x,y:tower.y,towerType:tower.type});
    }
    return true;
  }
  update(dt){
    if(this.phase!=='wave')return;
    const d=clamp(dt,0,1/20);this.time+=d;
    const wave=WAVES[this.waveIndex];
    if(this.spawned<this.toSpawn){this.spawnTimer-=d;
      if(this.spawnTimer<=0){this.spawnEnemy(this.getWaveEnemy(this.spawned),this.spawned%2);this.spawned++;
        this.spawnTimer=.7*(1-this.waveIndex*.055)+(this.random()*.18);}}
    for(const enemy of this.enemies){if(!enemy.alive)continue;
      enemy.hitFlash=Math.max(0,enemy.hitFlash-d);
      const factor=this.time<enemy.slowUntil?enemy.slowFactor:1;
      enemy.distance+=enemy.speed*factor*d;
      if(enemy.distance>=ROUTE_LENGTHS[enemy.routeIndex]){
        enemy.alive=false;this.integrity-=ENEMY_TYPES[enemy.type].leak;this.combo=0;this.emit('leak',{x:enemy.x,y:enemy.y,damage:ENEMY_TYPES[enemy.type].leak});
        if(this.integrity<=0){this.integrity=0;this.phase='lost';this.message='CORE OFFLINE // BREACH DETECTED';this.emit('gameLost');break;}}
      else Object.assign(enemy,locationAlong(ROUTES[enemy.routeIndex],enemy.distance));
    }
    if(this.phase==='lost'){this.enemies=this.enemies.filter(e=>e.alive);return;}
    for(const tower of this.towers){tower.cooldown-=d;
      if(tower.cooldown<=0&&this.towerFire(tower)){
        const spec=TOWER_TYPES[tower.type];tower.cooldown=spec.cooldown/(1+.10*(tower.level-1));}
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
      const bonus=65+this.waveIndex*22;this.credits+=bonus;this.score+=bonus*3;this.waveIndex++;
      this.emit('waveClear',{bonus,wave:this.waveIndex});
      if(this.waveIndex>=WAVES.length){this.phase='won';this.message='NETWORK SECURED // ALL WAVES CLEARED';this.emit('gameWon');}
      else {this.phase='ready';this.message=`WAVE CLEARED +${bonus} // PREPARE ${WAVES[this.waveIndex].name.toUpperCase()}`;}
    }
  }
  snapshot(){return {phase:this.phase,wave:this.waveIndex+1,credits:this.credits,integrity:this.integrity,score:this.score,kills:this.kills,towers:this.towers.length,enemies:this.enemies.length};}
}
