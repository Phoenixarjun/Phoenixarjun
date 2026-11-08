/** Geometry-only utilities. No DOM dependencies: tested with Node's built-in test runner. */
export const EPS = 1e-7;
export const clamp = (v,lo,hi) => Math.max(lo,Math.min(hi,v));
export const length = (x,y) => Math.hypot(x,y);
export const normalise = (x,y) => {const l=length(x,y)||1; return {x:x/l,y:y/l};};
export const reflect = (vx,vy,nx,ny) => {const d=vx*nx+vy*ny;return {x:vx-2*d*nx,y:vy-2*d*ny};};

/**
 * Exact continuous collision of a swept circle and an axis-aligned rectangle.
 * Computes contact against the four offset flat faces plus four quarter-circle
 * corners. Unlike an inflated-AABB slab intersection, it does not falsely
 * collide against the square region outside a rounded corner.
 * dx/dy is the full intended displacement this substep; t is normalised [0,1].
 */
export function sweepCircleAABB(x,y,dx,dy,r,rect){
 const rx=rect.x,ry=rect.y,right=rx+rect.w,bottom=ry+rect.h;
 if(Math.abs(dx)+Math.abs(dy)<EPS) return null;
 if(testOverlapCircleRect(x,y,r-.000001,rect))return null;
 if(Math.max(x,x+dx)<rx-r || Math.min(x,x+dx)>right+r ||
    Math.max(y,y+dy)<ry-r || Math.min(y,y+dy)>bottom+r) return null;
 let best=null;
 const offer=(t,nx,ny)=>{
   if(t< -EPS || t>1+EPS || nx*dx+ny*dy>=-EPS) return;
   if(best===null||t<best.t)best={t:clamp(t,0,1),nx,ny};
 };
 if(dx>EPS){const t=(rx-r-x)/dx,yy=y+dy*t;if(yy>=ry-EPS&&yy<=bottom+EPS)offer(t,-1,0);}
 if(dx< -EPS){const t=(right+r-x)/dx,yy=y+dy*t;if(yy>=ry-EPS&&yy<=bottom+EPS)offer(t,1,0);}
 if(dy>EPS){const t=(ry-r-y)/dy,xx=x+dx*t;if(xx>=rx-EPS&&xx<=right+EPS)offer(t,0,-1);}
 if(dy< -EPS){const t=(bottom+r-y)/dy,xx=x+dx*t;if(xx>=rx-EPS&&xx<=right+EPS)offer(t,0,1);}
 const aa=dx*dx+dy*dy;
 for(const [cx,cy,nxSign,nySign] of [[rx,ry,-1,-1],[right,ry,1,-1],[rx,bottom,-1,1],[right,bottom,1,1]]){
   const ox=x-cx,oy=y-cy,bb=2*(ox*dx+oy*dy),cc=ox*ox+oy*oy-r*r;
   const disc=bb*bb-4*aa*cc;
   if(disc<0)continue;
   const t=(-bb-Math.sqrt(Math.max(0,disc)))/(2*aa);
   if(t< -EPS||t>1+EPS)continue;
   const hx=x+dx*t,hy=y+dy*t;
   if((hx-cx)*nxSign< -EPS || (hy-cy)*nySign< -EPS)continue;
   const n=normalise(hx-cx,hy-cy);
   offer(t,n.x,n.y);
 }
 return best;
}

/** Approximate collision with a horizontal/vertical wall at a specific coordinate. */
export function sweepWall(p,d,boundary,normalSign){
  if(Math.abs(d)<EPS || d*normalSign>=0) return null;
  const t=(boundary-p)/d;
  return t>=-EPS&&t<=1?clamp(t,0,1):null;
}

/** Bounce from player paddle with adjustable, bounded reflection angle.
 * contactOffset=-1 at left edge, +1 at right edge, measured at collision time.
 * paddleVelocity adds small English/spin to reward skilled movement.
 */
export function paddleBounce(offset,paddleVelocity,speed,maxAngle=1.08){
  const aim=clamp(offset*maxAngle+clamp(paddleVelocity/1250,-0.12,0.12),-maxAngle,maxAngle);
  let vx=Math.sin(aim)*speed, vy=-Math.cos(aim)*speed;
  // Avoid perfectly vertical stale trajectories, but keep explicit testable math.
  if(Math.abs(vx)<speed*.14) vx=(offset<0?-1:1)*speed*.14;
  vy=-Math.sqrt(Math.max(0,speed*speed-vx*vx));
  return {vx,vy};
}

export function testOverlapCircleRect(x,y,r,rect){
 const cx=clamp(x,rect.x,rect.x+rect.w),cy=clamp(y,rect.y,rect.y+rect.h);
 return (x-cx)**2+(y-cy)**2 <= r*r;
}

/** Clamp speed while ensuring minimum vertical movement to prevent side-to-side loops. */
export function stabiliseVelocity(vx,vy,minSpeed,maxSpeed,minVerticalRatio=.22){
 let speed=clamp(length(vx,vy),minSpeed,maxSpeed);
 let v=normalise(vx,vy);vx=v.x*speed;vy=v.y*speed;
 if(Math.abs(vy)<speed*minVerticalRatio){
   const sign=vy<0?-1:1;
   vy=sign*speed*minVerticalRatio;
   vx=Math.sign(vx||1)*Math.sqrt(speed*speed-vy*vy);
 }
 return {vx,vy};
}
