/* Synthesized effects; no MP3 files, external services, or autoplay. */
export class SoundEngine{
 constructor(){this.enabled=false;this.ctx=null;}
 unlock(){if(!this.ctx){const A=window.AudioContext||window.webkitAudioContext;if(!A)return;this.ctx=new A();}if(this.ctx.state==='suspended')this.ctx.resume().catch(()=>{});}
 toggle(){this.enabled=!this.enabled;if(this.enabled)this.unlock();return this.enabled;}
 tone(f=440,d=.11,type='sine',vol=.06,end=null){if(!this.enabled)return;this.unlock();const c=this.ctx;if(!c)return;const t=c.currentTime,osc=c.createOscillator(),gain=c.createGain();osc.type=type;osc.frequency.setValueAtTime(f,t);if(end)osc.frequency.exponentialRampToValueAtTime(Math.max(30,end),t+d);gain.gain.setValueAtTime(Math.max(.0001,vol),t);gain.gain.exponentialRampToValueAtTime(.0001,t+d);osc.connect(gain);gain.connect(c.destination);osc.start(t);osc.stop(t+d+.01);}
 play(event){if(!this.enabled)return;switch(event.type){case 'jump':this.tone(220,.19,'triangle',.075,480);break;case 'slide':this.tone(185,.12,'sawtooth',.025,120);break;case 'lane':this.tone(360,.058,'triangle',.026);break;case 'pickup':this.tone(570,.09,'sine',.09,950);this.tone(780,.13,'triangle',.045,1180);break;case 'damage':this.tone(160,.33,'sawtooth',.1,75);break;case 'shieldbreak':this.tone(420,.28,'sawtooth',.055,190);break;case 'sector':this.tone(310,.22,'sine',.065,620);break;case 'gameover':this.tone(300,.55,'sawtooth',.08,60);break;case 'nearmiss':this.tone(640,.07,'triangle',.035,850);break;}}
}
