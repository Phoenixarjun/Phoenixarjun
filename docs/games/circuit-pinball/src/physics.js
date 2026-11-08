/* Circuit Pinball — deterministic, dependency-free 2D collision primitives.
   Physics coordinates are logical pixels; +y points downward. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.PinballPhysics = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const EPS = 1e-9;
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const dot = (a, b) => a.x * b.x + a.y * b.y;
  const mag = (a) => Math.hypot(a.x, a.y);
  function normalize(v, fallback = {x: 0, y: -1}) {
    const d = mag(v);
    return d < EPS ? {...fallback} : {x: v.x / d, y: v.y / d};
  }
  function closestPointOnSegment(p, a, b) {
    const dx = b.x - a.x, dy = b.y - a.y;
    const len2 = dx * dx + dy * dy;
    const t = len2 < EPS ? 0 : clamp(((p.x - a.x) * dx + (p.y - a.y) * dy) / len2, 0, 1);
    return {x: a.x + t * dx, y: a.y + t * dy, t};
  }
  function circleSegmentContact(p, r, a, b) {
    const q = closestPointOnSegment(p, a, b);
    const dx = p.x - q.x, dy = p.y - q.y;
    const dist = Math.hypot(dx, dy);
    if (dist >= r) return null;
    let n;
    if (dist > EPS) n = {x: dx / dist, y: dy / dist};
    else {
      const edge = {x: b.x - a.x, y: b.y - a.y};
      n = normalize({x: -edge.y, y: edge.x});
    }
    return {n, penetration: r - dist, point: q};
  }
  function circleCircleContact(p, r, center, otherRadius) {
    const dx = p.x - center.x, dy = p.y - center.y;
    const distance = Math.hypot(dx, dy), combined = r + otherRadius;
    if (distance >= combined) return null;
    return {n: distance > EPS ? {x: dx / distance, y: dy / distance} : {x: 0, y: -1},
      penetration: combined - distance, point: {x: center.x, y: center.y}};
  }
  function circleAABBContact(p, r, box) {
    const q = {x: clamp(p.x, box.x, box.x + box.w), y: clamp(p.y, box.y, box.y + box.h)};
    const dx = p.x - q.x, dy = p.y - q.y;
    const distance = Math.hypot(dx, dy);
    if (distance >= r) return null;
    if (distance > EPS) return {n:{x:dx / distance, y:dy / distance}, penetration:r - distance, point:q};
    const distances = [
      {d:Math.abs(p.x - box.x), n:{x:-1,y:0}},
      {d:Math.abs(box.x + box.w - p.x), n:{x:1,y:0}},
      {d:Math.abs(p.y - box.y), n:{x:0,y:-1}},
      {d:Math.abs(box.y + box.h - p.y), n:{x:0,y:1}}
    ].sort((a,b) => a.d - b.d);
    return {n:distances[0].n, penetration:r + distances[0].d, point:q};
  }
  function resolveContact(ball, contact, restitution = .86, surfaceVelocity = {x:0,y:0}, minimumKick = 0) {
    if (!contact) return false;
    const n = contact.n;
    ball.x += n.x * (contact.penetration + .015);
    ball.y += n.y * (contact.penetration + .015);
    const rvx = ball.vx - surfaceVelocity.x, rvy = ball.vy - surfaceVelocity.y;
    const vn = rvx * n.x + rvy * n.y;
    if (vn < 0) {
      const j = -(1 + restitution) * vn + minimumKick;
      ball.vx += j * n.x;
      ball.vy += j * n.y;
    }
    return true;
  }
  // Continuous collision of a moving circle against a stationary circular bumper.
  // Returns time of impact in [0, dt] or null; handles starting overlap.
  function sweepCircleCircle(p, velocity, r, center, otherR, dt) {
    const sx = p.x - center.x, sy = p.y - center.y, R = r + otherR;
    const c = sx * sx + sy * sy - R * R;
    if (c <= 0) return {t:0,n:normalize({x:sx,y:sy})};
    const a = velocity.x * velocity.x + velocity.y * velocity.y;
    if (a < EPS) return null;
    const b = 2 * (sx * velocity.x + sy * velocity.y);
    if (b >= 0) return null;
    const discr = b * b - 4 * a * c;
    if (discr < 0) return null;
    const t = (-b - Math.sqrt(discr)) / (2 * a);
    if (t < -EPS || t > dt + EPS) return null;
    return {t:clamp(t, 0, dt), n:normalize({x:sx + velocity.x*t, y:sy + velocity.y*t})};
  }
  // Swept circle against a capsule segment: test both flat sides and both end caps.
  function sweepCircleSegment(p, v, r, a, b, dt) {
    const overlap = circleSegmentContact(p, r, a, b);
    if (overlap) return {t:0,n:overlap.n};
    const dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy;
    if (d2<EPS) return sweepCircleCircle(p,v,r,a,0,dt);
    const len=Math.sqrt(d2), nx=-dy/len, ny=dx/len;
    const signed=(p.x-a.x)*nx+(p.y-a.y)*ny, vn=v.x*nx+v.y*ny;
    let best=null;
    if (Math.abs(vn)>EPS) {
      for (const sign of [-1,1]) {
        if (vn*sign>=0) continue;
        const t=(sign*r-signed)/vn;
        if (t < -EPS || t>dt+EPS) continue;
        const hx=p.x+v.x*t, hy=p.y+v.y*t;
        const u=((hx-a.x)*dx+(hy-a.y)*dy)/d2;
        if (u>=0 && u<=1) best={t:clamp(t,0,dt),n:{x:sign*nx,y:sign*ny}};
      }
    }
    for (const end of [a,b]) {
      const hit=sweepCircleCircle(p,v,r,end,0,dt);
      if (hit && (!best || hit.t<best.t)) best=hit;
    }
    return best;
  }
  function limitSpeed(ball,maxSpeed=1780) {
    const speed=Math.hypot(ball.vx,ball.vy);
    if (speed>maxSpeed) { ball.vx*=maxSpeed/speed; ball.vy*=maxSpeed/speed; }
  }
  function flipperTip(pivot, length, angle) {
    return {x:pivot.x+Math.cos(angle)*length,y:pivot.y+Math.sin(angle)*length};
  }
  function angularPointVelocity(pivot,point,angularSpeed) {
    const dx=point.x-pivot.x,dy=point.y-pivot.y;
    return {x:-angularSpeed*dy,y:angularSpeed*dx};
  }
  return {EPS,clamp,dot,mag,normalize,closestPointOnSegment,circleSegmentContact,circleCircleContact,
    circleAABBContact,resolveContact,sweepCircleCircle,sweepCircleSegment,limitSpeed,flipperTip,angularPointVelocity};
});
