/* No samples, CDN or downloaded audio. All sounds synthesized locally. */
(function(root){
  'use strict';
  class CircuitAudio {
    constructor(){this.enabled=true;this.ctx=null;this.master=null;this.last={};}
    unlock(){
      if(!this.enabled) return;
      try {if(!this.ctx){
        const C=root.AudioContext||root.webkitAudioContext;if(!C)return;
        this.ctx=new C(); this.master=this.ctx.createGain();this.master.gain.value=.12;
        this.master.connect(this.ctx.destination);
      } if(this.ctx.state==='suspended')this.ctx.resume().catch(()=>{});
      }catch(_){/* Audio is strictly optional. */}
    }
    play(kind){
      if(!this.enabled)return;this.unlock();if(!this.ctx)return;
      const now=this.ctx.currentTime;
      const gap={flip:.06,wall:.06,bumper:.07,score:.055,nudge:.15,lose:.3,launch:.13}[kind]??.035;
      if((this.last[kind]||-100)+gap>now)return;this.last[kind]=now;
      const specs={
        flip:[155,95,.055,'square',.14],wall:[190,112,.045,'triangle',.14],
        bumper:[540,250,.16,'sine',.22],score:[670,910,.09,'triangle',.17],
        target:[480,720,.12,'square',.12],launch:[130,410,.21,'sawtooth',.14],
        nudge:[86,48,.14,'sawtooth',.20],lose:[260,72,.32,'triangle',.18],
        bonus:[380,790,.35,'sine',.18], tilt:[115,70,.40,'square',.16]
      };
      const [f1,f2,dur,type,volume]=specs[kind]||specs.score;
      try{
        const osc=this.ctx.createOscillator(),g=this.ctx.createGain();osc.type=type;
        osc.frequency.setValueAtTime(f1,now);osc.frequency.exponentialRampToValueAtTime(Math.max(f2,30),now+dur);
        g.gain.setValueAtTime(.0001,now);g.gain.exponentialRampToValueAtTime(volume,now+.012);
        g.gain.exponentialRampToValueAtTime(.0001,now+dur);
        osc.connect(g);g.connect(this.master);osc.start(now);osc.stop(now+dur+.02);
      }catch(_){}
    }
    setEnabled(v){this.enabled=!!v;if(this.enabled)this.unlock();}
  }
  root.CircuitAudio=CircuitAudio;
})(typeof globalThis!=='undefined'?globalThis:this);
