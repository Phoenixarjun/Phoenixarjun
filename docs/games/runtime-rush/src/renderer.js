/* Native WebGL 3D corridor renderer. No Three.js CDN or external assets needed.
 * Every visible world object is a real 3D mesh under a perspective camera. */
const COLORS={lime:[.715,1,.231],aqua:[.35,.77,.75],steel:[.22,.34,.37],floor:[.038,.086,.087],rail:[.085,.22,.20],red:[1,.26,.27],white:[.89,.98,.95],gold:[.93,.67,.21],black:[.026,.055,.068]};
function rgb(hex){return COLORS[hex]||hex;}
function norm(a){let k=Math.hypot(...a)||1;return a.map(v=>v/k)}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function dot(a,b){return a.reduce((s,v,i)=>s+v*b[i],0)}
function perspective(fov,aspect,near,far){const f=1/Math.tan(fov/2),nf=1/(near-far);return [f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]}
function lookAt(eye,target){const f=norm(target.map((x,i)=>x-eye[i])),r=norm(cross(f,[0,1,0])),u=cross(r,f);return [r[0],u[0],-f[0],0,r[1],u[1],-f[1],0,r[2],u[2],-f[2],0,-dot(r,eye),-dot(u,eye),dot(f,eye),1]}
function mul(a,b){let o=new Array(16).fill(0);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o}
function transform(pos,scale=[1,1,1],rotY=0,rotZ=0,rotX=0){const cy=Math.cos(rotY),sy=Math.sin(rotY),cz=Math.cos(rotZ),sz=Math.sin(rotZ),cx=Math.cos(rotX),sx=Math.sin(rotX);const ry=[cy,0,-sy,0,0,1,0,0,sy,0,cy,0,0,0,0,1];const rz=[cz,sz,0,0,-sz,cz,0,0,0,0,1,0,0,0,0,1];const rx=[1,0,0,0,0,cx,sx,0,0,-sx,cx,0,0,0,0,1];const sc=[scale[0],0,0,0,0,scale[1],0,0,0,0,scale[2],0,0,0,0,1];const m=mul(mul(mul(ry,rz),rx),sc);m[12]=pos[0];m[13]=pos[1];m[14]=pos[2];return m}
function makeCube(){const v=[];const faces=[[[1,0,0],[[.5,-.5,-.5],[.5,-.5,.5],[.5,.5,.5],[.5,.5,-.5]]],[[-1,0,0],[[-.5,-.5,.5],[-.5,-.5,-.5],[-.5,.5,-.5],[-.5,.5,.5]]],[[0,1,0],[[-.5,.5,-.5],[.5,.5,-.5],[.5,.5,.5],[-.5,.5,.5]]],[[0,-1,0],[[-.5,-.5,.5],[.5,-.5,.5],[.5,-.5,-.5],[-.5,-.5,-.5]]],[[0,0,1],[[.5,-.5,.5],[-.5,-.5,.5],[-.5,.5,.5],[.5,.5,.5]]],[[0,0,-1],[[-.5,-.5,-.5],[.5,-.5,-.5],[.5,.5,-.5],[-.5,.5,-.5]]]];for(const [n,p] of faces)for(const i of [0,2,1,0,3,2])v.push(...p[i],...n);return new Float32Array(v)}
function makeSphere(lat=18,lon=24){const out=[];function p(a,b){const s=Math.sin(a);return [s*Math.cos(b),Math.cos(a),s*Math.sin(b)]}for(let i=0;i<lat;i++)for(let j=0;j<lon;j++){const a=i*Math.PI/lat,b=j*2*Math.PI/lon,aa=(i+1)*Math.PI/lat,bb=(j+1)*2*Math.PI/lon;for(const pt of [p(a,b),p(aa,bb),p(aa,b),p(a,b),p(a,bb),p(aa,bb)])out.push(...pt,...norm(pt))}return new Float32Array(out)}
function makeTorus(R=1,r=.06,n=48,m=8){const out=[];function p(a,b){const ca=Math.cos(a),sa=Math.sin(a),cb=Math.cos(b),sb=Math.sin(b);const pt=[(R+r*cb)*ca,r*sb,(R+r*cb)*sa];return [pt,[ca*cb,sb,sa*cb]]}for(let i=0;i<n;i++)for(let j=0;j<m;j++){const a=i*2*Math.PI/n,aa=(i+1)*2*Math.PI/n,b=j*2*Math.PI/m,bb=(j+1)*2*Math.PI/m;for(const [pt,no] of [p(a,b),p(aa,bb),p(aa,b),p(a,b),p(a,bb),p(aa,bb)])out.push(...pt,...no)}return new Float32Array(out)}
const VS=`attribute vec3 aPos;attribute vec3 aNorm;uniform mat4 uModel;uniform mat4 uVP;uniform vec3 uCamera;varying vec3 vNormal;varying float vDistance;varying vec3 vWorld;void main(){vec4 wp=uModel*vec4(aPos,1.);vWorld=wp.xyz;vNormal=normalize(mat3(uModel)*aNorm);vDistance=length(wp.xyz-uCamera);gl_Position=uVP*wp;}`;
const FS=`precision mediump float;uniform vec3 uColor;uniform float uEmit;uniform float uAlpha;uniform vec3 uFog;varying vec3 vNormal;varying float vDistance;varying vec3 vWorld;void main(){vec3 n=normalize(vNormal);vec3 ld=normalize(vec3(-.46,.86,-.31));float diffuse=max(dot(n,ld),0.);float ambient=.34+diffuse*.58;vec3 col=uColor*(ambient+uEmit*1.1);col+=vec3(.045,.085,.069)*pow(max(dot(n,normalize(vec3(.2,.8,-.2))),0.),7.);float fog=clamp((vDistance-22.)/127.,0.,1.);col=mix(col,uFog,fog*.94);gl_FragColor=vec4(col,uAlpha);}`;
function shader(gl,type,src){const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(sh));return sh}
function program(gl){const p=gl.createProgram();gl.attachShader(p,shader(gl,gl.VERTEX_SHADER,VS));gl.attachShader(p,shader(gl,gl.FRAGMENT_SHADER,FS));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p}
export class RunnerRenderer{
 constructor(canvas){this.canvas=canvas;this.gl=canvas.getContext('webgl2',{alpha:false,antialias:true,powerPreference:'high-performance'})||canvas.getContext('webgl',{alpha:false,antialias:true});if(!this.gl)throw Error('WebGL is not available');const gl=this.gl;this.prog=program(gl);this.attrs={pos:gl.getAttribLocation(this.prog,'aPos'),norm:gl.getAttribLocation(this.prog,'aNorm')};this.uni=Object.fromEntries(['uModel','uVP','uCamera','uColor','uEmit','uAlpha','uFog'].map(k=>[k,gl.getUniformLocation(this.prog,k)]));this.meshes={};for(const [name,data] of Object.entries({box:makeCube(),sphere:makeSphere(),torus:makeTorus()})){const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);this.meshes[name]={buf,count:data.length/6};}gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);this.vp=null;this.camera=[0,6.4,-13.0];this.w=0;this.h=0;this.draws=0;this.mode='full';this.lastFrame=0;this.resize();}
 resize(){let dpr=Math.min(window.devicePixelRatio||1,1.5),w=Math.max(1,Math.floor(this.canvas.clientWidth*dpr)),h=Math.max(1,Math.floor(this.canvas.clientHeight*dpr));if(this.canvas.width!==w||this.canvas.height!==h){this.canvas.width=w;this.canvas.height=h;}this.w=w;this.h=h;this.gl.viewport(0,0,w,h);}
 draw(mesh,pos,sz,color,emit=0,ry=0,rz=0,rx=0,alpha=1){const gl=this.gl,me=this.meshes[mesh];if(!me)return;gl.bindBuffer(gl.ARRAY_BUFFER,me.buf);gl.enableVertexAttribArray(this.attrs.pos);gl.enableVertexAttribArray(this.attrs.norm);gl.vertexAttribPointer(this.attrs.pos,3,gl.FLOAT,false,24,0);gl.vertexAttribPointer(this.attrs.norm,3,gl.FLOAT,false,24,12);gl.uniformMatrix4fv(this.uni.uModel,false,new Float32Array(transform(pos,sz,ry,rz,rx)));gl.uniform3fv(this.uni.uColor,rgb(color));gl.uniform1f(this.uni.uEmit,emit);gl.uniform1f(this.uni.uAlpha,alpha);gl.drawArrays(gl.TRIANGLES,0,me.count);this.draws++;}
 box(x,y,z,sx,sy,sz,c,em=0,ry=0,rz=0,rx=0,alpha=1){this.draw('box',[x,y,z],[sx,sy,sz],c,em,ry,rz,rx,alpha)}
 sphere(x,y,z,r,c,em=0){this.draw('sphere',[x,y,z],[r,r,r],c,em)}
 render(g,seconds){this.resize();const gl=this.gl;gl.clearColor(.007,.020,.025,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.prog);this.draws=0;
 const floating=g.state==='menu'?Math.sin(seconds*.64)*.18:0,xc=g.x||0;
 this.camera=[xc*.14,5.4+Math.min(2,g.speed/45)*.30,-11.8];const view=lookAt(this.camera,[xc*.13,2.0,23]);const proj=perspective(64*Math.PI/180,this.w/this.h,.1,175);this.vp=mul(proj,view);
 gl.uniformMatrix4fv(this.uni.uVP,false,new Float32Array(this.vp));gl.uniform3fv(this.uni.uCamera,this.camera);gl.uniform3fv(this.uni.uFog,[.008,.026,.032]);
 this.drawWorld(g,seconds);
 this.drawObjects(g,seconds);
 this.drawPlayer(g,seconds,floating);
 this.lastFrame=performance.now();
 }
 drawWorld(g,t){const dist=g.distance||t*5;const track=[-3.05,0,3.05];
 // Concrete highway beneath all three lanes.
 this.box(0,-.32,55,10.9,.44,148,'floor',.02);
 for(const x of track){this.box(x,-.075,55,2.86,.12,148,'rail',.04);this.box(x,0.005,55,2.5,.016,148,'floor',.05)}
 // Endless cross strips on the ground and lane dividers.
 for(let z=-11;z<130;z+=8){let zz=z-(dist%8);this.box(0,.015,zz,9.5,.016,.095,'steel',.08);for(const x of [-4.56,-1.52,1.52,4.56])this.box(x,.033,zz+2.5,.057,.028,3.0,'aqua',.24)}
 for(const x of [-5.45,5.45]){this.box(x,-.02,55,.21,.18,148,'lime',.23);this.box(x,1.2,55,.46,2.6,148,'black',.02);this.box(x,2.62,55,.14,.08,148,'aqua',.18)}
 // An architectural tunnel with animated geometric ribbing.
 for(let z=-14;z<130;z+=13){const zz=z-(dist%13);for(const x of [-5.65,5.65]){
 this.box(x,3.48,zz,.18,6.9,.23,'steel',.1);
 this.box(x,5.8,zz,.33,.23,.3,'aqua',.35);
 this.box(x,1.4,zz,.21,2.1,.3,'rail',.10);
 }
 this.box(0,7.0,zz,11.35,.18,.22,'steel',.09);
 this.box(0,6.87,zz,4.2,.054,.2,'lime',.16);
 this.box(0,-.12,zz,11,.13,.28,'aqua',.25);
 }
 // Suspended ceiling lane guides and chase lights.
 for(let z=0;z<128;z+=7){const zz=z-(dist%7);for(let x of [-3.05,0,3.05])this.box(x,7.08,zz,.14,.06,1.4,zz<40?'lime':'aqua',zz<40?.25:.06)}
 // Moving high speed particles embedded into the track.
 for(let i=0;i<36;i++){const z=((i*11.8+2)-(dist*1.6)%125+125)%125-7;const lane=i%3;this.box(track[lane]+(i%2?-.8:.8),.042,z,.045,.01,1.1,'lime',.22)}
 }
 drawObjects(g,t){for(const o of g.items){const z=o.s-g.distance;if(z>125||z<-9)continue;const x=LANE_X[o.lane];if(o.type==='block'){
 this.box(x,.94,z,2.23,1.9,1.6,'steel',.10);this.box(x,1.93,z,2.3,.10,1.66,'red',.32);this.box(x,1.0,z-0.825,1.62,.15,.052,'red',.65);this.box(x,.60,z-.825,1.62,.14,.052,'red',.65);
 for(const d of [-.85,.85])this.box(x+d,.92,z-.83,.085,1.7,.07,'red',.3);
 }else if(o.type==='barrier'){
 this.box(x,.42,z,2.22,.84,1.06,'steel',.13);this.box(x,.87,z,2.24,.1,1.10,'gold',.28);
 for(let i=0;i<4;i++)this.box(x-1+i*.62,.48,z-.54,.16,.33,.06,i%2?'gold':'black',.22,0,.55);
 }else if(o.type==='beam'){
 for(let d of [-1.03,1.03])this.box(x+d,1.5,z,.11,3.0,.14,'steel',.25);
 this.box(x,1.58,z,2.20,.23,.24,'red',1.15);
 this.box(x,2.7,z,2.16,.1,.18,'steel',.3);
 }else{
 const lift=1.15+Math.sin(t*5+o.id)*.2, size=o.type==='energy'?.5:.62;const c=o.type==='shield'?'aqua':o.type==='overclock'?'gold':'lime';this.sphere(x,lift,z,size,c,.65);
 this.draw('torus',[x,lift,z],[size*1.55,size*1.55,size*1.55],c,.85,t*1.6,0,Math.PI/2,.87);
 }
 }}
 drawPlayer(g,t,bob=0){let x=g.x,y=g.y+bob,z=-.15,slide=g.sliding>0,sc=slide?.57:1;
 // Moving shadow and collision ring below player.
 this.draw('torus',[x,.045,z],[1.05,.055,1.05],'aqua',.04,0,0,0,.36);
 this.sphere(x,y*.85,z,.88*sc,'black',.06);
 this.sphere(x,y,z,.73*sc,'steel',.38);
 this.sphere(x-.11,y+.20*sc,z-.55,.28*sc,'aqua',.47);
 this.draw('torus',[x,y,z],[.90*sc,.90*sc,.90*sc],'lime',.75,t*1.3,0,Math.PI/3);
 this.draw('torus',[x,y,z],[.88*sc,.88*sc,.88*sc],'aqua',.45,-t*.8,0,Math.PI/2);
 if(g.shield>0){this.draw('torus',[x,y,z],[1.23,1.23,1.23],'aqua',1.0,0,0,Math.PI/2,.65);}
 if(g.invulnerable>0)this.draw('torus',[x,y,z],[1.3,1.3,1.3],'red',.55,t*4,0,0,.4);
 }
 project(pos){if(!this.vp)return null;const a=this.vp,x=pos[0],y=pos[1],z=pos[2],w=a[3]*x+a[7]*y+a[11]*z+a[15];if(w<=0)return null;const px=(a[0]*x+a[4]*y+a[8]*z+a[12])/w,py=(a[1]*x+a[5]*y+a[9]*z+a[13])/w;return {x:(px*.5+.5)*this.w,y:(1-(py*.5+.5))*this.h,w};}
}
