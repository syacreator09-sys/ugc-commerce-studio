const fs=require('fs');
const path=require('path');
const sharp=require('sharp');

const W=1080,H=1920,FPS=24,START=4.45,END=11.85,N=Math.round((END-START)*FPS);
const out=process.env.CANO_TASKFLOW_OUT || 'storage/render/cano_ugc_v3_overlay_frames';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const eo=x=>1-Math.pow(1-clamp(x),3);
const alpha=(t,s,e)=>clamp((t-s)/(e-s));

fs.rmSync(out,{recursive:true,force:true});
fs.mkdirSync(out,{recursive:true});

function stage(t,s,e,label,num,type){
 const ina=alpha(t,s,s+.25), outa=1-alpha(t,e-.20,e), op=Math.min(ina,outa);
 if(op<=0) return '';
 let extra='';
 if(type==='wave') extra=[0,1,2,3,4,5,6].map((i)=>{const h=12+22*(.5+.5*Math.sin(t*9+i));return `<rect x="${760+i*23}" y="${210-h/2}" width="10" height="${h}" rx="5" fill="#56B7FF" opacity=".8"/>`}).join('');
 if(type==='plan') extra=`<rect x="758" y="183" width="145" height="12" rx="6" fill="#17354B"/><rect x="758" y="183" width="${145*eo(alpha(t,s+.12,e-.18))}" height="12" rx="6" fill="#FFBF3B"/><rect x="758" y="208" width="110" height="9" rx="5" fill="#56B7FF99"/><rect x="758" y="230" width="128" height="9" rx="5" fill="#56B7FF66"/>`;
 if(type==='priority') extra=`<text x="758" y="196" font-family="Inter,Arial" font-size="18" font-weight="800" fill="#FFBF3B">P1</text><rect x="800" y="184" width="115" height="12" rx="6" fill="#FFBF3B"/><text x="758" y="224" font-family="Inter,Arial" font-size="18" font-weight="800" fill="#56B7FF">P2</text><rect x="800" y="212" width="79" height="12" rx="6" fill="#56B7FF"/><text x="758" y="252" font-family="Inter,Arial" font-size="18" font-weight="800" fill="#89A4BA">P3</text><rect x="800" y="240" width="48" height="12" rx="6" fill="#536C80"/>`;
 if(type==='focus') extra=`<circle cx="813" cy="215" r="35" fill="#FFBF3B22" stroke="#FFBF3B" stroke-width="3"/><circle cx="813" cy="215" r="14" fill="#FFBF3B"/><path d="M870 215 L914 215" stroke="#56B7FF" stroke-width="6" stroke-linecap="round"/><circle cx="925" cy="215" r="7" fill="#56B7FF"/>`;
 return `<g opacity="${op}" transform="translate(0 ${24*(1-eo(ina))})"><rect x="126" y="142" width="828" height="142" rx="34" fill="#06101ACC" stroke="#56B7FF55" stroke-width="2"/><text x="164" y="184" font-family="Inter,Arial" font-size="16" letter-spacing="3" fill="#8FAAC0">AI TASK FLOW · ${num}/4</text><text x="164" y="236" font-family="Inter,Arial" font-size="34" font-weight="850" fill="#FFFFFF">${label}</text>${extra}</g>`;
}

function svg(local){
 const t=local+START;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920">
   ${stage(t,4.45,6.15,'CAPTURANDO PENDIENTES','01','wave')}
   ${stage(t,6.05,8.05,'ARMANDO TU DÍA','02','plan')}
   ${stage(t,7.95,10.02,'PRIORIZANDO TAREAS','03','priority')}
   ${stage(t,9.92,11.85,'SOLO LO IMPORTANTE','04','focus')}
 </svg>`;
}

(async()=>{
 for(let i=0;i<N;i++){
   const t=i/FPS;
   await sharp(Buffer.from(svg(t))).png({compressionLevel:4})
     .toFile(path.join(out,`frame_${String(i).padStart(4,'0')}.png`));
 }
 console.log('task-flow frames',N,out);
})();