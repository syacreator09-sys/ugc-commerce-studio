const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// CANO MOTION UI PACK V1
// Canonical source for the five talking-head / UGC motion families approved after CANO_UGC_SALES_V3_3.
// Source UGC is intentionally external. This script only renders transparent overlay frame sequences.

const W = 1080;
const H = 1920;
const FPS = Number(process.env.CANO_MOTION_FPS || 12);
const DUR = Number(process.env.CANO_MOTION_DURATION || 19.55);
const N = Math.ceil(DUR * FPS);
const ROOT = process.env.CANO_MOTION_OUT || 'storage/render/cano_motion_ui_pack_v1';

const GOLD = '#FFBE37';
const BLUE = '#55B8FF';
const CYAN = '#54F0D1';
const WHITE = '#F7FAFF';
const MUTED = '#A8BAC9';
const FONT = 'Arial,DejaVu Sans,sans-serif';

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);
const inout = (t, s, e, fade = .24) => Math.min(ease((t - s) / fade), ease((e - t) / fade));
const appear = (t, s, d = .35) => ease((t - s) / d);
const pulse = (t, sp = 3) => .5 + .5 * Math.sin(t * sp);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function defs() {
  return `<defs>
    <linearGradient id="gold" x1="0" x2="1"><stop offset="0" stop-color="#FFE39A"/><stop offset=".5" stop-color="${GOLD}"/><stop offset="1" stop-color="#E99C0B"/></linearGradient>
    <linearGradient id="blue" x1="0" x2="1"><stop offset="0" stop-color="#5BE4FF"/><stop offset="1" stop-color="#4088FF"/></linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>`;
}
function text(x, y, txt, size = 32, weight = 700, color = WHITE, anchor = 'start', extra = '') {
  return `<text x="${x}" y="${y}" font-family="${FONT}" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="${anchor}" ${extra}>${esc(txt)}</text>`;
}
function glass(x, y, w, h, r = 26, stroke = '#55B8FF66', fill = '#06101BD9', sw = 2) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
}
function pill(x, y, w, label, color = GOLD, op = 1) {
  return `<g opacity="${op}">${glass(x, y, w, 55, 27, color + '66', '#06101BE6', 2)}<circle cx="${x + 26}" cy="${y + 28}" r="6" fill="${color}"/>${text(x + 44, y + 36, label, 19, 800, WHITE)}</g>`;
}
function phone(x, y, w, h, op = 1, accent = BLUE) {
  return `<g opacity="${op}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${w * .10}" fill="#03070B" stroke="${accent}" stroke-width="3"/><rect x="${x + w * .08}" y="${y + h * .08}" width="${w * .84}" height="${h * .84}" rx="${w * .07}" fill="#0B1620"/><rect x="${x + w * .37}" y="${y + h * .035}" width="${w * .26}" height="${h * .025}" rx="10" fill="#23394B"/></g>`;
}
function floatCard(x, y, w, h, label, value, accent, phase, t) {
  const dx = Math.sin(t * 1.2 + phase) * 10;
  const dy = Math.cos(t * .9 + phase) * 8;
  return `<g transform="translate(${dx} ${dy})">${glass(x, y, w, h, 28, accent + '66', '#06101BDE', 2)}${text(x + 28, y + 42, label, 15, 800, MUTED, 'start', 'letter-spacing="2"')}${text(x + 28, y + 92, value, 31, 900, accent)}</g>`;
}
function footerCTA(theme = 'gold', small = 'Te digo qué anuncio haría para tu marca.') {
  const grad = theme === 'blue' ? 'url(#blue)' : 'url(#gold)';
  return `<g>${glass(66, 1480, 948, 300, 44, theme === 'blue' ? '#55B8FF' : '#FFBE37', '#03080FEF', 3)}
    <rect x="84" y="1500" width="912" height="108" rx="34" fill="${grad}"/>
    ${text(540, 1572, 'MÁNDAME TU PRODUCTO', 48, 900, '#05070B', 'middle')}
    ${text(540, 1658, small, 25, 600, WHITE, 'middle')}
    ${text(540, 1736, 'CANO DIGITAL  ×  AI CREATIVE', 20, 800, theme === 'blue' ? BLUE : GOLD, 'middle', 'letter-spacing="3"')}
  </g>`;
}
function topReveal(t) {
  const o = inout(t, 12.05, 15.82, .3);
  if (o <= 0) return '';
  const p = appear(t, 12.10, .55);
  const scan = (t * 370) % 900;
  return `<g opacity="${o}">
    <rect x="72" y="115" width="936" height="84" rx="30" fill="#020811E8" stroke="#55B8FF66"/>
    ${text(108, 168, 'IDENTITY CHECK', 18, 800, MUTED, 'start', 'letter-spacing="3"')}
    ${text(955, 168, t < 14.05 ? 'SCANNING...' : 'SYNTHETIC PRESENTER', 20, 850, t < 14.05 ? BLUE : GOLD, 'end')}
    <line x1="120" y1="210" x2="${120 + 820 * p}" y2="210" stroke="${t < 14.05 ? BLUE : GOLD}" stroke-width="6" stroke-linecap="round"/>
    <rect x="${100 + scan}" y="95" width="4" height="520" fill="#55B8FF" opacity=".14"/>
  </g>`;
}
function outroShell(t, accent = GOLD, title2 = 'CON TU PRODUCTO.', panel = '1 PRODUCTO → 4 FORMATOS') {
  if (t < 15.78) return '';
  const lt = t - 15.78;
  const o = appear(lt, 0, .25);
  const h1 = appear(lt, .25, .4);
  const chips = appear(lt, .78, .45);
  const cta = appear(lt, 1.45, .4);
  return `<g opacity="${o}"><rect width="1080" height="1920" fill="#02060C" opacity=".79"/>
    ${pill(72, 118, 360, 'AI CREATIVE // LIVE', CYAN, appear(lt, .05, .28))}
    <g opacity="${appear(lt, .10, .38)}">${glass(72, 225, 936, 142, 30, accent + '66', '#06101BEA', 2)}${text(110, 270, 'MULTIFORMAT ENGINE', 17, 800, MUTED, 'start', 'letter-spacing="3"')}${text(110, 330, panel, 42, 900, accent)}</g>
    <g opacity="${h1}">${text(72, 535, 'IMAGINA ESTO', 67, 900, WHITE)}${text(72, 622, title2, 76, 900, accent, 'start', 'filter="url(#glow)"')}</g>
    <g opacity="${chips}">${pill(72, 714, 216, 'AI UGC', GOLD)}${pill(306, 714, 216, 'REELS', BLUE)}${pill(540, 714, 216, 'ADS', GOLD)}${pill(774, 714, 234, 'CREATIVOS', BLUE)}</g>
    <g opacity="${appear(lt, 1.05, .35)}">${text(72, 900, 'TU PRODUCTO. TU MARCA.', 38, 900, WHITE)}${text(72, 954, 'Nosotros creamos el anuncio.', 28, 550, '#DCE6EF')}</g>
    <g opacity="${cta}">${footerCTA(accent === BLUE ? 'blue' : 'gold')}</g>
  </g>`;
}

// A — SOCIAL CONVERSATION
function styleA(t) {
  let s = '';
  if (t < 3.4) {
    const o = inout(t, .05, 3.35, .3), p = appear(t, .12, .55);
    s += `<g opacity="${o}">${glass(72, 110, 390, 122, 30, '#55B8FF66', '#06101BE8')}<circle cx="132" cy="171" r="34" fill="#0C1E2C" stroke="${BLUE}" stroke-width="3"/><path d="M116 171h32M132 155v32" stroke="${BLUE}" stroke-width="4" stroke-linecap="round"/>${text(190, 152, 'TIEMPO RECUPERADO', 16, 800, MUTED, 'start', 'letter-spacing="2"')}${text(190, 202, `${Math.round(120 * p)} MIN`, 44, 900, GOLD)}</g>`;
  }
  if (t >= 4.25 && t < 6.2) {
    const o = inout(t, 4.25, 6.2, .25), ys = [160, 248, 336], labs = ['Enviar propuesta', 'Llamar a cliente', 'Revisar agenda'];
    labs.forEach((l, i) => {
      const p = appear(t, 4.28 + i * .13, .26), x = i % 2 ? 530 : 72, w = i % 2 ? 430 : 420;
      s += `<g opacity="${o * p}" transform="translate(${(1 - p) * (i % 2 ? 55 : -55)},0)">${glass(x, ys[i], w, 72, 26, i === 0 ? '#FFBE3766' : '#55B8FF66', '#07121EEB')}${text(x + 30, ys[i] + 46, l, 24, 750, WHITE)}<circle cx="${x + w - 30}" cy="${ys[i] + 36}" r="9" fill="${i === 0 ? GOLD : BLUE}"/></g>`;
    });
  }
  if (t >= 6.0 && t < 8.1) {
    const o = inout(t, 6.0, 8.1, .25);
    s += `<g opacity="${o}">${glass(675, 120, 333, 430, 32, '#55B8FF66', '#06101BE9')}${text(710, 166, 'HOY', 22, 850, GOLD)}${text(710, 206, 'AI DAY PLAN', 15, 750, MUTED, 'start', 'letter-spacing="2"')}${['09:00  Propuesta', '12:30  Cliente', '16:00  Revisión'].map((l, i) => `<g opacity="${appear(t, 6.25 + i * .16, .32)}"><circle cx="718" cy="${260 + i * 84}" r="8" fill="${i === 0 ? GOLD : BLUE}"/><line x1="718" y1="${270 + i * 84}" x2="718" y2="${322 + i * 84}" stroke="#456277" stroke-width="3"/>${text(748, 270 + i * 84, l, 23, 700, WHITE)}</g>`).join('')}</g>`;
  }
  if (t >= 7.9 && t < 10.15) {
    const o = inout(t, 7.9, 10.15, .25);
    s += `<g opacity="${o}">${pill(72, 130, 280, 'PRIORIDAD ALTA', GOLD)}${pill(72, 202, 238, 'HOY', BLUE)}${pill(72, 274, 255, 'DESPUÉS', '#7791A7')}<path d="M338 158 C470 160 475 260 615 260" fill="none" stroke="#FFBE37" stroke-width="4" stroke-dasharray="10 10"/></g>`;
  }
  if (t >= 9.85 && t < 11.95) {
    const o = inout(t, 9.85, 11.95, .25), p = pulse(t, 5);
    s += `<g opacity="${o}">${glass(590, 116, 418, 150, 30, '#FFBE3780', '#06101BEC')}<circle cx="650" cy="191" r="31" fill="#FFBE3720" stroke="${GOLD}" stroke-width="3"/><circle cx="650" cy="191" r="${10 + 3 * p}" fill="${GOLD}"/>${text(705, 175, 'FOCO', 17, 800, MUTED, 'start', 'letter-spacing="3"')}${text(705, 220, 'LO IMPORTANTE', 30, 900, WHITE)}</g>`;
  }
  s += topReveal(t);
  if (t >= 15.78) s += outroShell(t, GOLD, 'CON TU PRODUCTO.', '1 PRODUCTO → 4 PIEZAS');
  return s;
}

// B — COMMAND CENTER
function styleB(t) {
  let s = '';
  if (t < 11.95) {
    const o = inout(t, .05, 11.95, .28);
    s += `<g opacity="${o}">${pill(72, 105, 320, 'COMMAND CENTER', CYAN)}${glass(720, 106, 288, 112, 27, '#55B8FF55', '#06101BE8')}${text(750, 145, 'SYSTEM STATUS', 15, 800, MUTED, 'start', 'letter-spacing="2"')}${text(750, 190, 'ONLINE', 30, 900, CYAN)}</g>`;
  }
  if (t < 3.4) {
    const o = inout(t, .08, 3.35, .3), p = appear(t, .18, .8);
    s += `<g opacity="${o}">${glass(72, 275, 380, 190, 30, '#FFBE3766', '#06101BE6')}${text(110, 320, 'TIME SAVED', 17, 800, MUTED, 'start', 'letter-spacing="2"')}${text(110, 390, '2.0 H', 62, 900, GOLD)}<rect x="110" y="420" width="292" height="14" rx="7" fill="#1A3447"/><rect x="110" y="420" width="${292 * p}" height="14" rx="7" fill="url(#gold)"/></g>`;
  }
  if (t >= 4.25 && t < 8.2) {
    const o = inout(t, 4.25, 8.2, .25);
    s += `<g opacity="${o}">${glass(646, 280, 362, 430, 32, '#55B8FF66', '#06101BE9')}${text(682, 330, 'AGENDA IA', 24, 900, WHITE)}${text(682, 365, 'AUTO-ORGANIZADA', 15, 800, BLUE, 'start', 'letter-spacing="2"')}${[0, 1, 2, 3].map(i => `<g opacity="${appear(t, 4.65 + i * .12, .3)}"><rect x="682" y="${410 + i * 66}" width="${180 + i * 25}" height="42" rx="13" fill="${i === 0 ? '#FFBE3730' : '#55B8FF22'}" stroke="${i === 0 ? '#FFBE3766' : '#55B8FF55'}"/><circle cx="702" cy="${431 + i * 66}" r="6" fill="${i === 0 ? GOLD : BLUE}"/>${text(722, 439 + i * 66, ['Pendientes', 'Bloques', 'Reuniones', 'Seguimiento'][i], 19, 700, WHITE)}</g>`).join('')}</g>`;
  }
  if (t >= 7.95 && t < 10.2) {
    const o = inout(t, 7.95, 10.2, .25);
    s += `<g opacity="${o}">${glass(72, 275, 390, 270, 30, '#FFBE3766', '#06101BEA')}${text(108, 320, 'PRIORITY ENGINE', 18, 800, MUTED, 'start', 'letter-spacing="2"')}${[['P1', .92, GOLD], ['P2', .66, BLUE], ['P3', .38, '#8199AB']].map((r, i) => `<g><text x="108" y="${380 + i * 64}" font-family="${FONT}" font-size="22" font-weight="900" fill="${r[2]}">${r[0]}</text><rect x="160" y="${360 + i * 64}" width="245" height="18" rx="9" fill="#183244"/><rect x="160" y="${360 + i * 64}" width="${245 * r[1]}" height="18" rx="9" fill="${r[2]}"/></g>`).join('')}</g>`;
  }
  if (t >= 9.9 && t < 11.95) {
    const o = inout(t, 9.9, 11.95, .25), p = appear(t, 10, .5);
    s += `<g opacity="${o}">${glass(646, 280, 362, 210, 30, '#55B8FF66', '#06101BEA')}${text(682, 325, 'FOCUS MODE', 18, 800, MUTED, 'start', 'letter-spacing="2"')}<circle cx="826" cy="402" r="68" fill="#55B8FF18" stroke="#55B8FF55" stroke-width="3"/><circle cx="826" cy="402" r="${42 - 24 * p}" fill="none" stroke="${GOLD}" stroke-width="6"/><circle cx="826" cy="402" r="12" fill="${GOLD}"/></g>`;
  }
  s += topReveal(t);
  if (t >= 15.78) s += outroShell(t, BLUE, 'CON TU NEGOCIO.', '1 SISTEMA → MÁS CREATIVOS');
  return s;
}

// C — KINETIC + PHONE
function styleC(t) {
  let s = '';
  if (t < 3.35) {
    const o = inout(t, .05, 3.35, .25), p = appear(t, .15, .5);
    s += `<g opacity="${o}"><text x="75" y="250" font-family="${FONT}" font-size="${118 + 10 * p}" font-weight="950" fill="${GOLD}">2H</text>${text(78, 315, 'RECUPERADAS', 30, 900, WHITE)}<line x1="78" y1="340" x2="${78 + 330 * p}" y2="340" stroke="${BLUE}" stroke-width="8" stroke-linecap="round"/></g>`;
  }
  if (t >= 4.2 && t < 6.25) {
    const o = inout(t, 4.2, 6.25, .25), p = appear(t, 4.3, .4);
    s += `<g opacity="${o}">${text(72, 180, 'LE DICTO', 55, 900, WHITE)}${text(72, 245, 'MIS PENDIENTES', 60, 950, GOLD)}${phone(715, 120, 290, 520, p, BLUE)}${['PROPOSAL', 'CLIENTE', 'AGENDA'].map((l, i) => `<g opacity="${appear(t, 4.55 + i * .12, .25)}"><rect x="748" y="${225 + i * 74}" width="218" height="48" rx="16" fill="#142838"/><circle cx="768" cy="${249 + i * 74}" r="6" fill="${i === 0 ? GOLD : BLUE}"/>${text(788, 257 + i * 74, l, 17, 800, WHITE)}</g>`).join('')}</g>`;
  }
  if (t >= 6.0 && t < 8.15) {
    const o = inout(t, 6.0, 8.15, .25);
    s += `<g opacity="${o}">${text(72, 190, 'LA IA', 52, 900, WHITE)}${text(72, 260, 'ARMA EL DÍA', 70, 950, BLUE, 'start', 'filter="url(#glow)"')}<path d="M72 292 L520 292" stroke="${GOLD}" stroke-width="8" stroke-linecap="round"/></g>`;
  }
  if (t >= 7.9 && t < 10.1) {
    const o = inout(t, 7.9, 10.1, .25);
    s += `<g opacity="${o}">${text(650, 170, 'PRIORIZA', 44, 900, WHITE)}${text(650, 232, 'TODO', 72, 950, GOLD)}<g transform="translate(720 290)"><path d="M0 0 L210 0" stroke="#213B4E" stroke-width="16" stroke-linecap="round"/><path d="M0 0 L178 0" stroke="${GOLD}" stroke-width="16" stroke-linecap="round"/><path d="M0 60 L210 60" stroke="#213B4E" stroke-width="16" stroke-linecap="round"/><path d="M0 60 L122 60" stroke="${BLUE}" stroke-width="16" stroke-linecap="round"/></g></g>`;
  }
  if (t >= 9.85 && t < 11.95) {
    const o = inout(t, 9.85, 11.95, .25);
    s += `<g opacity="${o}">${text(72, 190, 'YO SOLO HAGO', 46, 900, WHITE)}${text(72, 265, 'LO IMPORTANTE', 64, 950, GOLD)}<circle cx="930" cy="220" r="55" fill="#FFBE371A" stroke="${GOLD}" stroke-width="5"/><circle cx="930" cy="220" r="18" fill="${GOLD}"/></g>`;
  }
  if (t >= 12.05 && t < 14.2) {
    const o = inout(t, 12.05, 14.2, .2);
    s += `<g opacity="${o}">${text(540, 250, 'POR CIERTO…', 42, 800, MUTED, 'middle')}${text(540, 355, 'YO NO EXISTO', 82, 950, WHITE, 'middle')}${text(540, 425, 'SYNTHETIC PRESENTER', 20, 850, BLUE, 'middle', 'letter-spacing="4"')}</g>`;
  }
  if (t >= 14.15 && t < 15.82) {
    const o = inout(t, 14.15, 15.82, .18), p = pulse(t, 7);
    s += `<g opacity="${o}">${glass(170, 210, 740, 180, 38, '#FFBE3788', '#020811E8', 3)}${text(540, 286, 'TODO ESTO ES', 44, 850, WHITE, 'middle')}${text(540, 355, 'IA', 92, 950, GOLD, 'middle', 'filter="url(#glow)"')}<rect x="220" y="408" width="640" height="5" fill="${BLUE}" opacity="${.35 + .35 * p}"/></g>`;
  }
  if (t >= 15.78) s += outroShell(t, GOLD, 'CON TU PRODUCTO.', 'HOOK → DEMO → CTA');
  return s;
}

// D — FLOATING APP WORLD (face-safe corrected version)
function styleD(t) {
  let s = '';
  const o = inout(t, .05, 11.95, .3);
  if (t < 11.95) {
    s += `<g opacity="${o}">${floatCard(70, 110, 310, 130, 'TIME', '2 H / DÍA', GOLD, 0, t)}${floatCard(700, 110, 310, 130, 'CALENDAR', 'DAY PLAN', BLUE, 1.4, t)}${floatCard(72, 330, 280, 120, 'TASKS', '03 CAPTURED', CYAN, 2.8, t)}${floatCard(735, 350, 273, 120, 'PRIORITY', 'P1 ACTIVE', GOLD, 4.1, t)}</g>`;
  }
  if (t >= 4.25 && t < 6.2) {
    const oo = inout(t, 4.25, 6.2, .25);
    const items = [
      ['PROPUESTA', 748, 555, 242, GOLD],
      ['CLIENTE', 770, 640, 220, BLUE],
      ['AGENDA', 788, 725, 202, CYAN]
    ];
    s += `<g opacity="${oo}">${items.map((c, i) => { const p = appear(t, 4.28 + i * .13, .26); return `<g opacity="${p}" transform="translate(${(1 - p) * 70} 0)">${glass(c[1], c[2], c[3], 62, 21, c[4] + '66', '#07121EE9')}${text(c[1] + 22, c[2] + 40, c[0], 18, 850, WHITE)}<circle cx="${c[1] + c[3] - 25}" cy="${c[2] + 31}" r="7" fill="${c[4]}"/></g>`; }).join('')}</g>`;
  }
  if (t >= 6.0 && t < 10.2) {
    const oo = inout(t, 6.0, 10.2, .25), p = appear(t, 6.2, .7);
    s += `<g opacity="${oo}"><path d="M890 515 C960 ${560 - 35 * p} 970 ${660 - 15 * p} 900 770" fill="none" stroke="${BLUE}" stroke-width="4" stroke-dasharray="12 12" opacity=".85"/><circle cx="890" cy="515" r="9" fill="${GOLD}"/>${pill(812, 760, 196, 'AI ORGANIZA', CYAN)}</g>`;
  }
  if (t >= 9.85 && t < 11.95) {
    const oo = inout(t, 9.85, 11.95, .25);
    s += `<g opacity="${oo}">${glass(350, 230, 380, 104, 30, '#FFBE3777', '#06101BEC')}${text(540, 272, 'FOCUS WINDOW', 16, 800, MUTED, 'middle', 'letter-spacing="3"')}${text(540, 314, 'SOLO LO IMPORTANTE', 27, 900, WHITE, 'middle')}</g>`;
  }
  s += topReveal(t);
  if (t >= 15.78) {
    const lt = t - 15.78, oo = appear(lt, 0, .25);
    s += `<g opacity="${oo}"><rect width="1080" height="1920" fill="#02060C" opacity=".72"/>${floatCard(72, 138, 320, 126, 'AI UGC', 'READY', GOLD, 0, t)}${floatCard(688, 140, 320, 126, 'ADS', 'READY', BLUE, 1, t)}${floatCard(72, 322, 320, 126, 'REELS', 'READY', CYAN, 2, t)}${floatCard(688, 324, 320, 126, 'CREATIVOS', 'READY', GOLD, 3, t)}<g opacity="${appear(lt, .35, .4)}">${text(540, 650, 'TU PRODUCTO', 76, 950, WHITE, 'middle')}${text(540, 740, 'EN OTRO NIVEL.', 78, 950, GOLD, 'middle', 'filter="url(#glow)"')}</g><g opacity="${appear(lt, 1.25, .4)}">${footerCTA('gold', 'Te preparo una idea específica para tu marca.')}</g></g>`;
  }
  return s;
}

// E — PROCESS TRANSFORMATION
function styleE(t) {
  let s = '';
  if (t < 3.35) {
    const o = inout(t, .05, 3.35, .3), p = appear(t, .15, .65);
    s += `<g opacity="${o}">${glass(72, 112, 500, 118, 28, '#FFBE3766', '#06101BE9')}${text(108, 155, 'ANTES', 17, 800, MUTED, 'start', 'letter-spacing="2"')}${text(108, 204, 'SIN TIEMPO', 42, 900, WHITE)}<path d="M610 171 L${610 + 280 * p} 171" stroke="${GOLD}" stroke-width="8" stroke-linecap="round"/><path d="M865 148 l30 23 -30 23" fill="none" stroke="${GOLD}" stroke-width="8" stroke-linejoin="round"/></g>`;
  }
  if (t >= 4.15 && t < 6.2) {
    const o = inout(t, 4.15, 6.2, .25), cards = [['PENDIENTE', 95, 180, -8], ['CLIENTE', 710, 155, 7], ['PROPUESTA', 130, 330, 5], ['AGENDA', 720, 355, -6]];
    s += `<g opacity="${o}">${cards.map((c, i) => `<g transform="translate(${c[1]} ${c[2]}) rotate(${c[3]})">${glass(0, 0, 260, 70, 22, i % 2 ? '#55B8FF66' : '#FFBE3766', '#07121EEB')}${text(26, 45, c[0], 20, 850, WHITE)}</g>`).join('')}</g>`;
  }
  if (t >= 6.0 && t < 8.15) {
    const o = inout(t, 6.0, 8.15, .25), p = appear(t, 6.1, .75);
    s += `<g opacity="${o}">${text(540, 142, 'IA ORDENA', 24, 850, CYAN, 'middle', 'letter-spacing="4"')}<path d="M150 300 C310 ${300 - 110 * p} 375 300 500 300 S690 ${300 + 90 * p} 930 300" fill="none" stroke="${BLUE}" stroke-width="5" stroke-dasharray="12 10"/>${pill(120, 420, 190, 'PENDIENTES', GOLD)}${pill(332, 420, 170, 'PLAN', BLUE)}${pill(524, 420, 210, 'PRIORIDAD', GOLD)}${pill(756, 420, 160, 'FOCO', CYAN)}</g>`;
  }
  if (t >= 7.95 && t < 10.2) {
    const o = inout(t, 7.95, 10.2, .25), p = appear(t, 8.1, .55);
    s += `<g opacity="${o}">${glass(690, 125, 318, 302, 28, '#55B8FF66', '#06101BEA')}${text(724, 170, 'PIPELINE', 17, 800, MUTED, 'start', 'letter-spacing="3"')}${['CAPTURA', 'ORDENA', 'PRIORIZA', 'EJECUTA'].map((l, i) => `<g><circle cx="728" cy="${222 + i * 58}" r="10" fill="${i < Math.ceil(p * 4) ? GOLD : '#314B5D'}"/><line x1="728" y1="${232 + i * 58}" x2="728" y2="${260 + i * 58}" stroke="#38576D" stroke-width="3"/>${text(758, 230 + i * 58, l, 20, 800, WHITE)}</g>`).join('')}</g>`;
  }
  if (t >= 9.85 && t < 11.95) {
    const o = inout(t, 9.85, 11.95, .25);
    s += `<g opacity="${o}">${glass(72, 128, 510, 120, 28, '#FFBE3766', '#06101BEC')}${text(108, 170, 'DESPUÉS', 16, 800, MUTED, 'start', 'letter-spacing="3"')}${text(108, 220, 'SOLO LO IMPORTANTE', 36, 900, GOLD)}</g>`;
  }
  s += topReveal(t);
  if (t >= 15.78) {
    const lt = t - 15.78, o = appear(lt, 0, .25), p = appear(lt, .35, .8);
    s += `<g opacity="${o}"><rect width="1080" height="1920" fill="#02060C" opacity=".82"/>${text(540, 260, 'DE IDEA A ANUNCIO', 54, 950, WHITE, 'middle')}<line x1="120" y1="390" x2="${120 + 840 * p}" y2="390" stroke="${BLUE}" stroke-width="7" stroke-linecap="round"/>${[['IDEA', 120, GOLD], ['UGC', 330, BLUE], ['REEL', 540, GOLD], ['AD', 750, BLUE], ['CTA', 930, GOLD]].map(([l, x, c]) => `<g opacity="${p}"><circle cx="${x}" cy="390" r="16" fill="${c}"/><text x="${x}" y="445" text-anchor="middle" font-family="${FONT}" font-size="19" font-weight="850" fill="#F7FAFF">${l}</text></g>`).join('')}<g opacity="${appear(lt, 1.0, .4)}">${text(540, 680, 'IMAGINA ESTO', 65, 900, WHITE, 'middle')}${text(540, 770, 'CON TU PRODUCTO.', 76, 950, GOLD, 'middle', 'filter="url(#glow)"')}</g><g opacity="${appear(lt, 1.55, .4)}">${footerCTA('gold')}</g></g>`;
  }
  return s;
}

const styles = {
  A_SOCIAL_CONVERSATION: styleA,
  B_COMMAND_CENTER: styleB,
  C_KINETIC_PHONE: styleC,
  D_FLOATING_APP_WORLD: styleD,
  E_PROCESS_TRANSFORMATION: styleE
};

async function renderStyle(name, fn) {
  const dir = path.join(ROOT, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < N; i++) {
    const t = i / FPS;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${defs()}${fn(t)}</svg>`;
    await sharp(Buffer.from(svg)).png({ compressionLevel: 5 }).toFile(path.join(dir, `frame_${String(i).padStart(4, '0')}.png`));
  }
  console.log('rendered', name, N);
}

(async () => {
  const requested = process.argv.slice(2);
  const entries = requested.length
    ? Object.entries(styles).filter(([name]) => requested.includes(name))
    : Object.entries(styles);
  for (const [name, fn] of entries) await renderStyle(name, fn);
})().catch(err => { console.error(err); process.exit(1); });
