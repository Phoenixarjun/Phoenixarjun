/** Runtime Rush — deterministic, fixed-step arcade simulation.
 * Coordinates: x horizontal (lanes -3,0,3), y vertical, distance increases toward +z.
 * All velocities are world units/second; all timers are seconds.
 */
export const FIXED_DT = 1/120;
export const LANE_X = Object.freeze([3.05,0,-3.05]);
export const PLAYER_RADIUS = .68;
export const JUMP_VELOCITY = 9.7;
export const GRAVITY = 21.8;
export const SLIDE_SECONDS = .72;
export const SECTOR_NAMES = Object.freeze(['BOOT SEQUENCE','TRAFFIC SURGE','FAILOVER WINDOW','LATENCY STORM','CORE OVERLOAD']);
export const clamp = (v,a,b) => Math.min(b,Math.max(a,v));
export const lerp = (a,b,t) => a+(b-a)*t;
export const laneX = (lane) => LANE_X[clamp(lane,0,2)];
export const speedAt = distance => clamp(22 + distance/140,22,46);
export const sectorAt = distance => Math.min(5,1+Math.floor(distance/450));
export const xAt = (x,target,dt,rate=11) => target+(x-target)*Math.exp(-rate*dt);
export function mulberry32(seed){let a=seed>>>0;return ()=>{a=(a+0x6D2B79F5)|0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296}}
export const choose = (rng, xs) => xs[Math.floor(rng()*xs.length)];
/** Continuous crossing time so even high-speed steps cannot skip an event plane. */
export function crossingT(oldS,newS,itemS,halfDepth=.55){
  if(newS<=oldS)return null;
  // Trigger on first entry to contact slab, not its center.
  const contact=itemS-halfDepth;
  if(oldS>contact || newS<contact)return null;
  return clamp((contact-oldS)/(newS-oldS),0,1);
}
/** Jump height at time t after leaving ground: h = v*t - 0.5*g*t². */
export function jumpHeight(t){return Math.max(0,JUMP_VELOCITY*t-.5*GRAVITY*t*t)}
export function jumpDuration(){return 2*JUMP_VELOCITY/GRAVITY}
/** Candidate collision against a time-interpolated sphere, slider, and obstacle. */
export function hitsObstacle(ob,playerX,playerY,sliding=false){
  const horizontal=Math.abs(playerX-laneX(ob.lane));
  const radius=sliding?.45:PLAYER_RADIUS;
  const pad=ob.type==='beam'?.96:ob.type==='barrier'?1.0:ob.type==='block'?1.0:.65;
  if(horizontal>pad+radius*.55)return false;
  const bottom=playerY-radius, top=playerY+radius;
  if(ob.type==='barrier')return bottom<.87;
  if(ob.type==='beam')return top>1.23;
  if(ob.type==='block')return bottom<1.67;
  return false;
}
export function scoreFor(type){return type==='energy'?150:type==='shield'?80:type==='overclock'?100:60}
export function safeGeneration(pattern){
  const lanes=new Set(pattern.filter(o=>o.type==='block'||o.type==='barrier'||o.type==='beam').map(o=>o.lane));
  return lanes.size<=2;
}
/** Spawns well-separated challenge rows; each row keeps at least one clear lane.
 * Bonus pickups always go on clear lane, and all decisions can be made in time.
 */
export function createPattern(rng,s,sector){
  const reserved=Math.floor(rng()*3);
  const options=[0,1,2].filter(l=>l!==reserved);
  const items=[];
  const count=sector===1?1:(rng() < .48?1:2);
  for(let i=0;i<count;i++){
    const type=choose(rng,sector===1?['barrier','block']:['barrier','block','beam']);
    items.push({id:0,s,lane:options[i],type,hit:false});
  }
  if(rng()<.73){items.push({id:0,s:s+4.5,lane:reserved,type:rng()<.10?'shield':rng()<.08?'overclock':'energy',hit:false});}
  return items;
}
export function createGame(seed=0xC1A0){
  const rng=mulberry32(seed);
  return {state:'menu',distance:0,score:0,highScore:0,combo:0,integrity:3,stage:1,speed:22,
    targetLane:1,x:0,y:PLAYER_RADIUS,vy:0,sliding:0,shield:0,slow:0,invulnerable:0,
    items:[],nextSpawn:55,nextId:1,rng,hitEvents:[],events:[],elapsed:0,dodged:0,
    lastSector:1,particles:[],nearMiss:0,highestCombo:0,scoreRemainder:0,seed};
}
export function startGame(g){
  const ng=createGame(g.seed);ng.state='playing';ng.highScore=g.highScore;Object.assign(g,ng);
  // Safe first tutorial approach; no blocker for 55m.
  return g;
}
export function setLane(g,dir){if(g.state!=='playing')return false;const next=clamp(g.targetLane+Math.sign(dir),0,2);if(next===g.targetLane)return false;g.targetLane=next;g.events.push({type:'lane'});return true;}
export function jump(g){if(g.state!=='playing'||g.y>PLAYER_RADIUS+.02||g.vy>0||g.sliding>.01)return false;g.vy=JUMP_VELOCITY;g.events.push({type:'jump'});return true;}
export function slide(g){if(g.state!=='playing'||g.y>PLAYER_RADIUS+.03)return false;g.sliding=SLIDE_SECONDS;g.events.push({type:'slide'});return true;}
export function update(g,dt=FIXED_DT){
  if(g.state!=='playing')return g;
  dt=Math.min(dt,1/25);
  const s0=g.distance,x0=g.x,y0=g.y,slide0=g.sliding>0;
  g.elapsed+=dt;
  g.shield=Math.max(0,g.shield-dt);g.slow=Math.max(0,g.slow-dt);g.invulnerable=Math.max(0,g.invulnerable-dt);g.sliding=Math.max(0,g.sliding-dt);
  g.speed=speedAt(g.distance)*(g.slow>0?.72:1);
  const s1=s0+g.speed*dt;
  g.distance=s1;
  g.x=xAt(g.x,laneX(g.targetLane),dt,13.5);
  // Semi-implicit integration and landing resolution.
  if(g.vy!==0||g.y>PLAYER_RADIUS){g.vy-=GRAVITY*dt;g.y+=g.vy*dt;if(g.y<=PLAYER_RADIUS){g.y=PLAYER_RADIUS;g.vy=0;g.events.push({type:'land'});}}
  const currentStage=sectorAt(g.distance);g.stage=currentStage;
  if(currentStage>g.lastSector){g.events.push({type:'sector',sector:currentStage});g.score+=currentStage*300;g.lastSector=currentStage;}
  while(g.nextSpawn<g.distance+145){
    for(const item of createPattern(g.rng,g.nextSpawn,g.stage)){
      item.id=g.nextId++;g.items.push(item);
    }
    // 30..38m gap provides ~0.75..1.6s to choose a lane even at high speed.
    g.nextSpawn+=30+g.rng()*9;
  }
  for(const item of g.items){
    if(item.hit)continue;
    const half=item.type==='energy'||item.type==='shield'||item.type==='overclock'?1.0:.7;
    const cross=crossingT(s0,s1,item.s,half);
    if(cross===null)continue;
    item.hit=true;
    const cx=lerp(x0,g.x,cross),cy=lerp(y0,g.y,cross);
    const sliding=slide0||g.sliding>0;
    if(['energy','shield','overclock'].includes(item.type)){
      if(Math.abs(cx-laneX(item.lane))<1.08 && cy<2.6){
        g.score+=scoreFor(item.type)*(1+Math.floor(g.combo/6));
        if(item.type==='shield')g.shield=11;
        if(item.type==='overclock')g.slow=7;
        g.combo++;g.highestCombo=Math.max(g.combo,g.highestCombo);
        g.events.push({type:'pickup',kind:item.type,lane:item.lane});
      }
    }else if(hitsObstacle(item,cx,cy,sliding)){
      if(g.invulnerable<=0){
        if(g.shield>0){g.shield=0;g.events.push({type:'shieldbreak'});}
        else {g.integrity--;g.combo=0;g.events.push({type:'damage',integrity:g.integrity});}
        g.invulnerable=1.8;
        if(g.integrity<=0){g.state='over';g.events.push({type:'gameover'});}
      }
    }else {
      g.dodged++;g.score+=20;
      if(Math.abs(cx-laneX(item.lane)) < 1.35){g.nearMiss++;g.score+=45;g.events.push({type:'nearmiss'});}
    }
  }
  g.scoreRemainder+=(s1-s0)*1.4;
  const distancePoints=Math.floor(g.scoreRemainder);g.score+=distancePoints;g.scoreRemainder-=distancePoints;
  g.highScore=Math.max(g.highScore,g.score);
  g.items=g.items.filter(o=>!o.hit&&o.s>g.distance-15);
  return g;
}
