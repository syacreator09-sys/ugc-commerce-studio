const fs=require('fs');
const path=require('path');
const sharp=require('sharp');

const W=1080,H=1920,FPS=24,DUR=3.85,N=Math.round(FPS*DUR);
const outDir=process.env.CANO_OUTRO_OUT || 'storage/render/cano_ugc_v3_outro_frames';
const base=process.env.CANO_OUTRO_BASE;
if(!base) throw new Error('Set CANO_OUTRO_BASE to the cleaned final UGC frame.');
fs.rmSync(outDir,{recursive:true,force:true}); fs.mkdirSync(outDir,{recursive:true});

const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const eo=x=>1-Math.pow(1-clamp(x),3);
const a=(t,s,e)=>clamp((t-s)/(e-s));
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

function chip(x,y,w,label,idx,t){
 const p=a(t,.92+idx*.08,1.34+idx*.08), yy=y+(1-eo(p))*34;
 return `<g opacity="${p}" transform="translate(0 ${yy-y})"><rect x="${x}" y="${y}" width="${w}" height="86" rx="24" fill="#07101ACD" stroke="#56B7FF77" stroke-width="2"/><circle cx="${x+31}" cy="${y+43}" r="6" fill="#FFBF3B"/><text x="${x+50}" y="${y+53}" font-family="Inter,Arial" font-size="27" font-weight="750" fill="#F8FAFD">${esc(label)}</text></g>`;
}

function svg(t){
 const bg=a(t,0,.45), badge=a(t,.03,.30), panel=a(t,.18,.65), h1=a(t,.48,.92), h2=a(t,.66,1.10), claim=a(t,1.38,1.82), cta=a(t,1.78,2.22), pipe=a(t,2.16,2.68);
 const sweep=100+((t*390)%830), progress=eo(a(t,2.40,3.45)), panelY=226+(1-eo(panel))*28;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
 <defs>
  <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#02060C" stop-opacity=".10"/><stop offset=".42" stop-color="#02060C" stop-opacity=".27"/><stop offset=".56" stop-color="#02060C" stop-opacity=".48"/><stop offset="1" stop-color="#02060C" stop-opacity=".95"/></linearGradient>
  <linearGradient id="gold" x1="0" x2="1"><stop offset="0" stop-color="#FFE6A1"/><stop offset=".46" stop-color="#FFBF3B"/><stop offset="1" stop-color="#E79B0C"/></linearGradient>
  <linearGradient id="cta" x1="0" x2="1"><stop offset="0" stop-color="#EAA20E"/><stop offset=".5" stop-color="#FFD76B"/><stop offset="1" stop-color="#ECA40D"/></linearGradient>
  <filter id="gg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 </defs>
 <rect width="1080" height="1920" fill="url(#shade)" opacity="${bg}"/>
 <rect x="0" y="980" width="1080" height="940" fill="#02060C" opacity="${.78*bg}"/>
 <g opacity="${badge}"><rect x="72" y="118" width="390" height="58" rx="29" fill="#06101BCD" stroke="#FFBF3B66"/><circle cx="108" cy="147" r="7" fill="#5CFFB5"/><text x="130" y="155" font-family="Inter,Arial" font-size="21" font-weight="700" letter-spacing="2" fill="#F7FAFF">AI CREATIVE // LIVE</text></g>
 <g opacity="${panel}" transform="translate(0 ${panelY-226})"><rect x="72" y="226" width="936" height="154" rx="30" fill="#06101AD8" stroke="#56B7FF55" stroke-width="2"/><text x="108" y="270" font-family="Inter,Arial" font-size="18" fill="#9DB3C9" letter-spacing="3">MULTIFORMAT ENGINE</text><text x="108" y="332" font-family="Inter,Arial" font-size="45" font-weight="850" fill="#FFFFFF">1 PRODUCTO</text><text x="404" y="332" font-family="Inter,Arial" font-size="45" font-weight="850" fill="#FFBF3B">→</text><text x="468" y="332" font-family="Inter,Arial" font-size="45" font-weight="850" fill="#FFBF3B">4 FORMATOS</text></g>
 <g opacity="${h1}" transform="translate(${72+(1-eo(h1))*45},0)"><text x="0" y="548" font-family="Inter,Arial" font-size="68" font-weight="850" fill="#FFFFFF">IMAGINA ESTO</text></g>
 <g opacity="${h2}" transform="translate(${72+(1-eo(h2))*55},0)"><text x="0" y="633" font-family="Inter,Arial" font-size="76" font-weight="900" fill="url(#gold)" filter="url(#gg)">CON TU PRODUCTO.</text></g>
 ${chip(72,724,440,'AI UGC',0,t)}${chip(568,724,440,'REELS',1,t)}${chip(72,828,440,'ADS',2,t)}${chip(568,828,440,'CREATIVOS',3,t)}
 <g opacity="${claim}"><text x="72" y="1044" font-family="Inter,Arial" font-size="39" font-weight="850" fill="#FFFFFF">TU PRODUCTO. TU MARCA.</text><text x="72" y="1096" font-family="Inter,Arial" font-size="28" font-weight="520" fill="#DCE6EF">Nosotros creamos el anuncio.</text></g>
 <g opacity="${cta}"><rect x="72" y="1180" width="936" height="184" rx="48" fill="#030910E8" stroke="#FFBF3B" stroke-width="3"/><rect x="86" y="1194" width="908" height="102" rx="38" fill="url(#cta)"/><text x="540" y="1262" text-anchor="middle" font-family="Inter,Arial" font-size="51" font-weight="900" fill="#05070B">MÁNDAME TU PRODUCTO</text><text x="540" y="1335" text-anchor="middle" font-family="Inter,Arial" font-size="26" font-weight="600" fill="#F7FAFF">Te digo qué anuncio haría para tu marca.</text><rect x="${sweep}" y="1197" width="28" height="96" rx="14" fill="#FFFFFF" opacity=".17" transform="skewX(-10)"/></g>
 <g opacity="${pipe}"><text x="72" y="1490" font-family="Inter,Arial" font-size="18" letter-spacing="3" fill="#9FB4C9">CREATIVE PIPELINE</text><line x1="118" y1="1564" x2="948" y2="1564" stroke="#18344B" stroke-width="7" stroke-linecap="round"/><line x1="118" y1="1564" x2="${118+830*progress}" y2="1564" stroke="#56B7FF" stroke-width="7" stroke-linecap="round"/><text x="72" y="1710" font-family="Inter,Arial" font-size="30" font-weight="850" fill="#FFFFFF" letter-spacing="4">CANO DIGITAL</text><text x="1008" y="1710" text-anchor="end" font-family="Inter,Arial" font-size="18" font-weight="700" fill="#FFBF3B" letter-spacing="3">AI CREATIVE</text></g>
 </svg>`;
}

(async()=>{
 const baseBuf=await sharp(base).resize(W,H,{fit:'cover'}).modulate({brightness:.80,saturation:.92}).toBuffer();
 for(let i=0;i<N;i++){
   const t=i/FPS;
   await sharp(baseBuf).composite([{input:Buffer.from(svg(t)),left:0,top:0}]).png({compressionLevel:3})
     .toFile(path.join(outDir,`frame_${String(i).padStart(4,'0')}.png`));
 }
 console.log('outro frames',N,outDir);
})();