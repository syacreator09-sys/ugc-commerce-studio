const fs=require('fs');
const path=require('path');
const sharp=require('sharp');

const W=1080,H=1920,FPS=24,DUR=3.05,N=Math.round(FPS*DUR);
const out=process.env.CANO_CLOCK_OUT || 'storage/render/cano_ugc_v3_clock_frames';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const eo=x=>1-Math.pow(1-clamp(x),3);
const alpha=(t,s,e)=>clamp((t-s)/(e-s));

fs.rmSync(out,{recursive:true,force:true});
fs.mkdirSync(out,{recursive:true});

function svg(t){
  const inn=eo(alpha(t,.05,.32));
  const outa=1-eo(alpha(t,2.56,3.02));
  const op=Math.min(inn,outa);
  const p=eo(alpha(t,.25,1.55));
  const minutes=Math.round(120*p);
  const h=Math.floor(minutes/60), m=minutes%60;
  const digital=`${h}:${String(m).padStart(2,'0')}`;
  const dash=(p*100).toFixed(1);
  const hand=-90+360*p;
  const badge=eo(alpha(t,1.15,1.70));

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
  <defs>
    <linearGradient id="glass" x1="0" x2="1"><stop offset="0" stop-color="#06101A" stop-opacity=".91"/><stop offset="1" stop-color="#0A1722" stop-opacity=".82"/></linearGradient>
    <linearGradient id="gold" x1="0" x2="1"><stop offset="0" stop-color="#FFE39A"/><stop offset=".55" stop-color="#FFBF3B"/><stop offset="1" stop-color="#E79B0C"/></linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <g opacity="${op}" transform="translate(${(1-inn)*-28},0)">
    <rect x="72" y="132" width="420" height="150" rx="34" fill="url(#glass)" stroke="#56B7FF66" stroke-width="2"/>
    <circle cx="145" cy="207" r="43" fill="#07131D" stroke="#23465E" stroke-width="5"/>
    <circle cx="145" cy="207" r="43" fill="none" stroke="#FFBF3B" stroke-width="6" stroke-linecap="round" pathLength="100" stroke-dasharray="${dash} 100" transform="rotate(-90 145 207)" filter="url(#glow)"/>
    <circle cx="145" cy="207" r="5" fill="#FFBF3B"/>
    <line x1="145" y1="207" x2="145" y2="178" stroke="#F7FAFF" stroke-width="5" stroke-linecap="round" transform="rotate(${hand} 145 207)"/>
    <text x="215" y="180" font-family="Inter,Arial" font-size="17" font-weight="700" letter-spacing="2.5" fill="#9DB3C9">AHORRO DE TIEMPO</text>
    <text x="215" y="235" font-family="Inter,Arial" font-size="48" font-weight="900" fill="url(#gold)">${digital}</text>
    <g opacity="${badge}">
      <rect x="360" y="202" width="98" height="38" rx="19" fill="#FFBF3B1F" stroke="#FFBF3B88"/>
      <text x="409" y="228" text-anchor="middle" font-family="Inter,Arial" font-size="15" font-weight="800" letter-spacing="1.3" fill="#FFD572">2 H / DÍA</text>
    </g>
  </g>
</svg>`;
}

(async()=>{
  for(let i=0;i<N;i++){
    const t=i/FPS;
    await sharp(Buffer.from(svg(t))).png({compressionLevel:4})
      .toFile(path.join(out,`frame_${String(i).padStart(4,'0')}.png`));
  }
  console.log('clock frames',N,out);
})();