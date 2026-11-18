// Sebab Apa? — Durian. Animasi dilukis ikut beat (110 BPM).
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, toScreen, cicak, person, smell, wavyPath, grain, vignette, FT } = PAPER;

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT;
const ACC = '#FF6B35';

// ================================================================ kamera
const CAM = [
  { x: 540, y: 1080, z: 1 },
  { b0: 0, b1: 7, x: 540, y: 1100, z: 1.06, ease: 'lin' },
  { b0: 7.1, b1: 9, x: 540, y: 1140, z: 2.15 },
  { b0: 9, b1: 31, x: 540, y: 1120, z: 2.3, ease: 'lin' },
  { b0: 31.2, b1: 32.6, x: 540, y: -1660, z: 1, whip: true },
  { b0: 32.6, b1: 41, x: 560, y: -1640, z: 1.04, ease: 'lin' },
  { b0: 42, b1: 46.6, x: 1560, y: -1620, z: 1.0 },
  { b0: 47, b1: 54, x: 1660, y: -1580, z: 1.14 },
  { b0: 55.2, b1: 56.6, x: 540, y: 4000, z: 1, whip: true },
  { b0: 56.6, b1: 64, x: 540, y: 4030, z: 1.07, ease: 'lin' },
  { b0: 66.4, b1: 68.6, x: 1600, y: 4000, z: 1.0 },
  { b0: 71.2, b1: 72.6, x: 540, y: 1080, z: 1.0, whip: true },
  { b0: 79, b1: 82, x: 540, y: 1100, z: 1.06 },
  { b0: 88, b1: 96, x: 540, y: 1090, z: 1.02 },
];

// ================================================================ objek: durian
function durianPath(c, r) {
  const N = 26; c.beginPath();
  for (let i = 0; i < N * 2; i++) {
    const a = (i / (N * 2)) * Math.PI * 2 - Math.PI / 2, q = i % 2 ? r : r * 1.13;
    c.lineTo(Math.cos(a) * q * 0.95, Math.sin(a) * q * 1.08);
  }
  c.closePath();
}
function durianBody(c, r, ripe) {
  const husk = mix('#86AE3C', '#C9A83E', ripe), dark = mix('#577D24', '#93731F', ripe);
  c.save(); shadow(c, true, 1); c.fillStyle = husk; durianPath(c, r); c.fill(); c.restore();
  c.save(); durianPath(c, r * 0.97); c.clip(); c.fillStyle = dark;
  const s = r * 0.17;
  for (let row = 0, yy = -r * 1.15; yy < r * 1.15; yy += s * 1.2, row++) {
    for (let xx = -r * 1.1; xx < r * 1.1; xx += s * 1.25) {
      const px = xx + (row % 2) * s * 0.62, py = yy;
      c.beginPath(); c.moveTo(px, py - s * 0.55); c.lineTo(px + s * 0.45, py + s * 0.35); c.lineTo(px - s * 0.45, py + s * 0.35); c.closePath(); c.fill();
    }
  }
  c.fillStyle = 'rgba(255,255,225,0.2)'; c.beginPath(); c.ellipse(-r * 0.35, -r * 0.4, r * 0.32, r * 0.5, -0.5, 0, 7); c.fill();
  c.fillStyle = 'rgba(40,20,0,0.12)'; c.beginPath(); c.ellipse(r * 0.45, r * 0.4, r * 0.5, r * 0.6, -0.5, 0, 7); c.fill();
  c.restore();
  c.save(); shadow(c, true, 0.5); c.fillStyle = '#6B4A2B'; c.beginPath(); rr(c, -r * 0.08, -r * 1.36, r * 0.16, r * 0.34, r * 0.05); c.fill();
  c.fillStyle = '#7E5A35'; c.beginPath(); c.ellipse(0, -r * 1.06, r * 0.22, r * 0.09, 0, 0, 7); c.fill(); c.restore();
}
function durian(c, x, y, r, o = {}) {
  const ripe = o.ripe || 0, open = o.open || 0;
  c.save(); c.translate(x, y); if (o.rot) c.rotate(o.rot); if (o.sx) c.scale(o.sx, o.sy || o.sx);
  if (open <= 0.001) durianBody(c, r, ripe);
  else {
    const fl = mix('#FFE27C', '#FFC531', ripe);
    fillP(c, '#F4E8C6', cc => cc.ellipse(0, r * 0.08, r * 0.8 * open + 1, r * 0.92, 0, 0, 7), 1);
    for (let k = -1; k <= 1; k++) {
      fillP(c, fl, cc => cc.ellipse(k * r * 0.33 * open, r * 0.08 + Math.abs(k) * r * 0.06, r * 0.25, r * 0.44 * (0.6 + 0.4 * open), 0, 0, 7), 0.5);
      c.fillStyle = 'rgba(255,255,255,0.4)'; c.beginPath(); c.ellipse(k * r * 0.33 * open - r * 0.08, -r * 0.1, r * 0.06, r * 0.15, 0, 0, 7); c.fill();
    }
    [-1, 1].forEach(side => {
      c.save(); c.translate(side * open * r * 0.8, r * 0.05 * open); c.rotate(side * open * 0.3);
      c.beginPath(); c.rect(side < 0 ? -r * 1.5 : 0, -r * 1.6, r * 1.5, r * 3.2); c.clip();
      durianBody(c, r, ripe);
      durianPath(c, r * 0.97); c.clip(); c.fillStyle = '#EFE0B6'; c.fillRect(side < 0 ? -r * 0.14 : 0, -r * 1.2, r * 0.14, r * 2.4);
      c.restore();
    });
  }
  if (o.face) {
    const f = o.face; // {sad}
    c.fillStyle = '#FFF'; [[-r * 0.3, -r * 0.1], [r * 0.3, -r * 0.1]].forEach(([ex, ey]) => { c.beginPath(); c.arc(ex, ey, r * 0.2, 0, 7); c.fill(); });
    c.fillStyle = '#2B2024'; [[-r * 0.27, -r * 0.05], [r * 0.33, -r * 0.05]].forEach(([ex, ey]) => { c.beginPath(); c.arc(ex, ey, r * 0.1, 0, 7); c.fill(); });
    c.strokeStyle = '#2B2024'; c.lineWidth = r * 0.06; c.lineCap = 'round';
    if (f.sad) {
      c.beginPath(); c.moveTo(-r * 0.48, -r * 0.42); c.lineTo(-r * 0.15, -r * 0.33); c.moveTo(r * 0.48, -r * 0.42); c.lineTo(r * 0.15, -r * 0.33); c.stroke();
      c.beginPath(); c.arc(0, r * 0.38, r * 0.16, Math.PI * 1.15, Math.PI * 1.85); c.stroke();
    } else { c.beginPath(); c.arc(0, r * 0.18, r * 0.16, Math.PI * 0.15, Math.PI * 0.85); c.stroke(); }
  }
  c.restore();
}

// ================================================================ ikon kecil
function molecule(c, x, y, s, o = {}) {
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(s, s); c.globalAlpha *= o.alpha === undefined ? 1 : o.alpha;
  const atoms = [[0, 0, 17, '#3B3540'], [32, -15, 11, '#F4F1EA'], [-30, -17, 11, '#F4F1EA'], [5, 35, o.S ? 21 : 11, o.S ? '#FFD23F' : '#F4F1EA'], [-8, -38, 10, '#F4F1EA']];
  if (o.S && o.glow) {
    const g = c.createRadialGradient(5, 35, 5, 5, 35, 80); g.addColorStop(0, `rgba(255,220,80,${0.7 * o.glow})`); g.addColorStop(1, 'rgba(255,220,80,0)');
    c.fillStyle = g; c.beginPath(); c.arc(5, 35, 80, 0, 7); c.fill();
  }
  c.strokeStyle = '#3B3540'; c.lineWidth = 6; c.lineCap = 'round';
  for (let i = 1; i < atoms.length; i++) { c.beginPath(); c.moveTo(0, 0); c.lineTo(atoms[i][0], atoms[i][1]); c.stroke(); }
  atoms.forEach(a => {
    fillP(c, a[3], cc => cc.arc(a[0], a[1], a[2], 0, 7), 0.4);
    c.lineWidth = 3.5; c.beginPath(); c.arc(a[0], a[1], a[2], 0, 7); c.stroke();
  });
  if (o.S) { c.fillStyle = '#2B2024'; c.font = "800 26px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('S', 5, 37); }
  c.restore();
}
function onion(c, x, y, s) {
  c.save(); c.translate(x, y); c.scale(s, s);
  fillP(c, '#9B4F96', cc => { cc.moveTo(0, -70); cc.bezierCurveTo(10, -40, 62, -30, 60, 15); cc.bezierCurveTo(58, 55, -58, 55, -60, 15); cc.bezierCurveTo(-62, -30, -10, -40, 0, -70); }, 1);
  c.strokeStyle = 'rgba(255,255,255,0.35)'; c.lineWidth = 4;
  [-28, 0, 28].forEach(dx => { c.beginPath(); c.moveTo(0, -60); c.quadraticCurveTo(dx * 1.6, 0, dx * 0.6, 48); c.stroke(); });
  c.strokeStyle = '#E8D9B8'; c.lineWidth = 3; for (let i = -2; i <= 2; i++) { c.beginPath(); c.moveTo(i * 6, 50); c.lineTo(i * 9, 64); c.stroke(); }
  c.restore();
}
function egg(c, x, y, s) {
  c.save(); c.translate(x, y); c.scale(s, s);
  fillP(c, '#FFF7E8', cc => cc.ellipse(0, 0, 50, 64, 0, 0, 7), 1);
  c.strokeStyle = '#6B5A48'; c.lineWidth = 4; c.lineJoin = 'round';
  c.beginPath(); c.moveTo(-48, -6); c.lineTo(-28, 8); c.lineTo(-12, -8); c.lineTo(6, 10); c.lineTo(22, -6); c.lineTo(48, 4); c.stroke();
  c.strokeStyle = '#8DBB3B'; c.lineWidth = 6; c.lineCap = 'round';
  [-22, 0, 22].forEach((dx, i) => { c.beginPath(); c.moveTo(dx, -78); c.bezierCurveTo(dx + 14, -92, dx - 14, -104, dx + Math.sin(S.B * 3 + i) * 6, -122); c.stroke(); });
  c.restore();
}
function noSign(c, x, y, r, sc) {
  if (sc <= 0.001) return;
  c.save(); c.translate(x, y); c.scale(sc, sc);
  fillP(c, '#FFFFFF', cc => cc.arc(0, 0, r, 0, 7), 1);
  durian(c, 0, r * 0.08, r * 0.45, { ripe: 0.3 });
  c.strokeStyle = '#E63B2E'; c.lineWidth = r * 0.16; c.beginPath(); c.arc(0, 0, r * 0.88, 0, 7); c.stroke();
  c.beginPath(); c.moveTo(-r * 0.62, -r * 0.62); c.lineTo(r * 0.62, r * 0.62); c.stroke();
  c.restore();
}
function stamp(c, text, x, y, size, sc, rot = -0.14, color = '#E63B2E') {
  if (sc <= 0.001) return;
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc);
  c.font = `800 ${size}px 'Baloo 2'`; const w = c.measureText(text).width + size * 0.8, h = size * 1.35;
  c.fillStyle = 'rgba(255,248,236,0.92)'; c.beginPath(); rr(c, -w / 2, -h / 2, w, h, 16); c.fill();
  c.strokeStyle = color; c.lineWidth = size * 0.1; c.beginPath(); rr(c, -w / 2 + 8, -h / 2 + 8, w - 16, h - 16, 12); c.stroke();
  c.fillStyle = color; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, 0, size * 0.08);
  c.restore();
}

// ================================================================ alam: pokok & gajah
function jungleTree(c, x, gy, h, k = 0, sc = 1) {
  const cols = [['#2F6B45', '#3C8452', '#4C9A5E'], ['#3E7E4E', '#4F965F', '#63AC6E']][k];
  c.save(); c.translate(x, gy); c.scale(sc, sc);
  fillP(c, '#6B4A2F', cc => { cc.moveTo(-22, 0); cc.lineTo(-12, -h); cc.lineTo(12, -h); cc.lineTo(22, 0); }, 0.8);
  const blobs = [[0, -h, 110], [-90, -h + 40, 80], [90, -h + 30, 85], [-40, -h - 70, 85], [50, -h - 60, 80]];
  blobs.forEach(([bx, by, br], i) => fillP(c, cols[i % 3], cc => cc.arc(bx, by, br, 0, 7), 0.8));
  c.restore();
}
function durianTree(c, x, gy) {
  const h = 1150;
  fillP(c, '#6A472C', cc => { cc.moveTo(x - 60, gy); cc.lineTo(x - 30, gy - h); cc.lineTo(x + 30, gy - h); cc.lineTo(x + 60, gy); }, 1);
  c.strokeStyle = '#6A472C'; c.lineWidth = 26; c.lineCap = 'round';
  [[-1, -700, -210, -880], [1, -820, 230, -980], [-1, -950, -170, -1120]].forEach(([, y0, dx, y1]) => { c.beginPath(); c.moveTo(x, gy + y0); c.lineTo(x + dx, gy + y1); c.stroke(); });
  const cols = ['#2B6240', '#357A4C', '#43905A', '#2F6B45'];
  const blobs = [[-260, -1120, 170], [250, -1160, 180], [0, -1260, 230], [-150, -1350, 170], [170, -1380, 170], [-330, -980, 120], [330, -1010, 130], [0, -1050, 160]];
  blobs.forEach(([bx, by, br], i) => fillP(c, cols[i % 4], cc => cc.arc(x + bx, gy + by, br, 0, 7), 1));
}
function hangingDurian(c, x, y, r, ripe) {
  c.strokeStyle = '#5A3D25'; c.lineWidth = 6; c.beginPath(); c.moveTo(x, y - r * 2.1); c.lineTo(x, y - r * 1.2); c.stroke();
  durian(c, x, y, r, { ripe });
}
function elephant(c, x, y, s, o = {}) {
  const ph = o.phase || 0, walk = o.walk || 0;
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
  const g = '#9096A8', gd = '#7A8094';
  const lg = (lx, a, col) => { c.save(); c.translate(lx, -110); c.rotate(a); fillP(c, col, cc => rr(cc, -24, 0, 48, 112, 16), 0.6); c.restore(); };
  lg(60, Math.sin(ph + 1.5) * 0.25 * walk, gd); lg(-60, Math.sin(ph) * 0.25 * walk, gd);
  c.strokeStyle = gd; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(150, -190); c.quadraticCurveTo(178, -160, 172, -120); c.stroke();
  fillP(c, g, cc => cc.ellipse(30, -195, 140, 100, 0, 0, 7), 1);
  lg(90, Math.sin(ph) * 0.25 * walk, g); lg(-30, Math.sin(ph + 1.5) * 0.25 * walk, g);
  // kepala
  fillP(c, g, cc => cc.arc(-115, -235, 78, 0, 7), 1);
  // belalai
  const up = o.trunk || 0;
  c.save(); shadow(c, true, 0.6); c.strokeStyle = g; c.lineCap = 'round'; c.lineWidth = 34;
  c.beginPath(); c.moveTo(-170, -215);
  c.bezierCurveTo(lerp(-215, -230, up), lerp(-160, -230, up), lerp(-205, -270, up), lerp(-90, -260, up), lerp(-190, -275, up), lerp(-50, -300, up)); c.stroke(); c.restore();
  // telinga
  fillP(c, '#A2A8BA', cc => cc.ellipse(-80, -235, 52 + Math.sin(S.B * 3) * 3, 72, 0.15, 0, 7), 0.7);
  // gading & mata
  c.strokeStyle = '#FFF8E8'; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath(); c.moveTo(-160, -190); c.quadraticCurveTo(-190, -170, -200, -185); c.stroke();
  c.fillStyle = '#2B2024'; c.beginPath(); c.arc(-140, -255, 8, 0, 7); c.fill();
  c.fillStyle = 'rgba(255,140,140,0.35)'; c.beginPath(); c.arc(-140, -228, 10, 0, 7); c.fill();
  c.restore();
}

// ================================================================ ZON 1: LORONG (0..1080, 0..1920)
const DUR = { x: 540, y: 1212, r: 72 };
const SHOPS = ['KOPI SATU', 'JAHIT', 'RUNCIT', 'GUNTING', 'KEDAI EMAS', 'KOPI SATU', 'BASIKAL', 'JAHIT'];
function zoneLorong(c, v) {
  const b = S.B;
  let g = c.createLinearGradient(0, -1040, 0, 1160);
  g.addColorStop(0, '#24203F'); g.addColorStop(0.5, '#3B2C5C'); g.addColorStop(0.75, '#8A4F7A'); g.addColorStop(0.92, '#E58A7B'); g.addColorStop(1, '#F7B98A');
  c.fillStyle = g; c.fillRect(-900, -1040, 3000, 2200);
  for (let i = 0; i < 40; i++) { const x = -600 + rnd(i) * 2400, y = -900 + rnd(i + 50) * 1300, tw = 0.5 + 0.5 * Math.sin(b * 2 + i); c.fillStyle = `rgba(255,240,200,${0.25 + 0.5 * tw})`; c.beginPath(); c.arc(x, y, 2.5 + rnd(i + 9) * 2.5, 0, 7); c.fill(); }
  // bulan
  const mg = c.createRadialGradient(830, 250, 30, 830, 250, 200); mg.addColorStop(0, 'rgba(255,240,200,0.45)'); mg.addColorStop(1, 'rgba(255,240,200,0)');
  c.fillStyle = mg; c.beginPath(); c.arc(830, 250, 200, 0, 7); c.fill();
  fillP(c, '#FFF0CC', cc => cc.arc(830, 250, 56, 0, 7), 0.5);
  // deret belakang
  for (let i = -5; i < 12; i++) {
    const bx = -700 + i * 215 + rnd(i) * 40, h = 380 + rnd(i + 7) * 240, top = 1080 - h, w = 200;
    fillP(c, '#4A3560', cc => cc.rect(bx, top, w, h), 0.8);
    for (let wy = top + 30; wy < 560; wy += 60) for (let wx = bx + 25; wx < bx + w - 30; wx += 50) {
      if (rnd(wx * 3 + wy) > 0.55) { c.fillStyle = 'rgba(255,207,122,0.85)'; c.fillRect(wx, wy, 24, 32); }
    }
  }
  // deret kedai depan
  const walls = ['#E8A33D', '#D9674A', '#6FA89E', '#E8C15A', '#C9584A', '#7EA4C9'];
  for (let u = -2; u < 6; u++) {
    const x0 = -600 + (u + 2) * 300, col = walls[(u + 6) % walls.length];
    fillP(c, col, cc => cc.rect(x0, 570, 300, 740), 1);
    c.fillStyle = 'rgba(0,0,0,0.12)'; c.fillRect(x0, 920, 300, 390);
    // bumbung
    fillP(c, '#A8432F', cc => { cc.rect(x0 - 6, 535, 312, 44); }, 0.8);
    c.fillStyle = '#C45A42'; for (let k = 0; k < 10; k++) { c.beginPath(); c.arc(x0 + 15 + k * 30, 579, 15, 0, Math.PI); c.fill(); }
    // tingkap
    [x0 + 55, x0 + 175].forEach(wx => {
      fillP(c, '#FFF4E0', cc => rr(cc, wx - 8, 640, 86, 196, 40), 0.5);
      c.fillStyle = '#2F7F7A'; c.beginPath(); rr(c, wx, 648, 70, 180, 34); c.fill();
      c.strokeStyle = '#1F5E5A'; c.lineWidth = 4; for (let k = 0; k < 8; k++) { c.beginPath(); c.moveTo(wx + 6, 690 + k * 17); c.lineTo(wx + 64, 690 + k * 17); c.stroke(); }
    });
    // papan tanda
    fillP(c, '#FFF4E0', cc => cc.rect(x0 + 20, 880, 260, 52), 0.6);
    c.fillStyle = '#7A3B2A'; c.font = "800 34px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(SHOPS[u + 2], x0 + 150, 909);
    // gerbang kaki lima
    [x0 + 30, x0 + 160].forEach(ax => {
      fillP(c, '#2C2030', cc => { cc.moveTo(ax, 1310); cc.lineTo(ax, 1030); cc.arc(ax + 55, 1030, 55, Math.PI, 0); cc.lineTo(ax + 110, 1310); }, 0.4);
      const lg = c.createLinearGradient(0, 1000, 0, 1310); lg.addColorStop(0, 'rgba(255,190,100,0.55)'); lg.addColorStop(1, 'rgba(255,190,100,0.05)');
      c.fillStyle = lg; c.beginPath(); c.moveTo(ax + 10, 1310); c.lineTo(ax + 10, 1035); c.arc(ax + 55, 1035, 45, Math.PI, 0); c.lineTo(ax + 100, 1310); c.fill();
    });
    fillP(c, '#F3E3C3', cc => cc.rect(x0 - 8, 940, 18, 370), 0.5);
  }
  // lampu tali
  c.strokeStyle = '#2B2024'; c.lineWidth = 3; c.beginPath();
  for (let x = -600; x <= 1800; x += 20) { const t = ((x + 600) % 400) / 400, y = 990 + Math.sin(t * Math.PI) * 50; x === -600 ? c.moveTo(x, y) : c.lineTo(x, y); } c.stroke();
  for (let x = -580; x <= 1800; x += 40) {
    const t = ((x + 600) % 400) / 400, y = 990 + Math.sin(t * Math.PI) * 50 + 10, on = 0.7 + 0.3 * Math.sin(b * 3 + x);
    const cols = ['255,200,90', '255,120,90', '140,220,200'][Math.abs(Math.round(x / 40)) % 3];
    const gg = c.createRadialGradient(x, y, 2, x, y, 28); gg.addColorStop(0, `rgba(${cols},${on})`); gg.addColorStop(1, `rgba(${cols},0)`);
    c.fillStyle = gg; c.beginPath(); c.arc(x, y, 28, 0, 7); c.fill();
    c.fillStyle = `rgba(${cols},1)`; c.beginPath(); c.arc(x, y, 7, 0, 7); c.fill();
  }
  // cicak (maskot) atas dinding
  const wink = P(84.8, 85.1) * (1 - P(86.2, 86.5));
  cicak(c, 905, 760, 0.95, -0.35, { wink });
  // kaki lima + jalan
  fillP(c, '#BCA794', cc => cc.rect(-900, 1310, 3000, 64), 0.8);
  c.fillStyle = '#3E3349'; c.fillRect(-900, 1374, 3000, 1100);
  c.fillStyle = 'rgba(255,244,224,0.5)'; for (let x = -880; x < 2000; x += 160) c.fillRect(x, 1740, 90, 14);
  // tiang lampu
  fillP(c, '#2B2735', cc => cc.rect(1000, 720, 18, 640), 0.6);
  const lg = c.createRadialGradient(1009, 715, 10, 1009, 715, 170); lg.addColorStop(0, 'rgba(255,220,140,0.7)'); lg.addColorStop(1, 'rgba(255,220,140,0)');
  c.fillStyle = lg; c.beginPath(); c.arc(1009, 715, 170, 0, 7); c.fill();
  fillP(c, '#2B2735', cc => rr(cc, 975, 690, 70, 30, 12), 0.6);

  // ---- gerai durian
  [292, 776].forEach(px => fillP(c, '#5A4636', cc => cc.rect(px, 1080, 14, 260), 0.6));
  for (let k = 0; k < 12; k++) {
    const sx = 260 + k * 47;
    fillP(c, k % 2 ? '#FFF4E0' : ACC, cc => { cc.moveTo(sx, 1010); cc.lineTo(sx + 47, 1010); cc.lineTo(sx + 47, 1078); cc.arc(sx + 23.5, 1078, 23.5, 0, Math.PI); }, k === 0 ? 1 : 0);
  }
  const bulb = c.createRadialGradient(540, 1110, 5, 540, 1110, 260); bulb.addColorStop(0, 'rgba(255,230,160,0.55)'); bulb.addColorStop(1, 'rgba(255,230,160,0)');
  c.fillStyle = bulb; c.beginPath(); c.arc(540, 1110, 260, 0, 7); c.fill();
  // penjual
  person(c, 700, 1330, 0.78, { shirt: '#F2C14E', skin: '#B97A4E', cap: '#2E86AB', disgust: false });
  // longgok
  const ripeAll = P(26, 30);
  [[330, 1255, 40, 0.3], [395, 1250, 44, 0.5], [700, 1256, 42, 0.4], [760, 1253, 38, 0.2], [362, 1206, 36, 0.6], [732, 1210, 36, 0.4]].forEach(([x, y, r, rp], i) => durian(c, x, y, r, { ripe: Math.max(rp, ripeAll * 0.8), rot: (rnd(i) - 0.5) * 0.5 }));
  // meja
  fillP(c, '#8A5A33', cc => cc.rect(262, 1290, 556, 26), 1);
  fillP(c, ACC, cc => { cc.moveTo(280, 1316); cc.lineTo(800, 1316); cc.lineTo(800, 1430); for (let k = 0; k <= 10; k++) cc.lineTo(800 - k * 52, 1430 + (k % 2 ? 14 : 0)); cc.lineTo(280, 1316); }, 1);
  c.fillStyle = '#FFF4E0'; c.font = "800 72px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('DURIAN', 540, 1378);
  // durian hero
  const open = back(P(9, 9.9)) * (b < 9 ? 0 : 1);
  durian(c, DUR.x, DUR.y, DUR.r, { ripe: ripeAll, open: clamp(open, 0, 1.15), rot: b < 9 && b > 8.6 ? Math.sin(b * 60) * 0.06 : 0 });
  // bau mengalir ke hujung lorong
  const r1 = out3(P(2.5, 5.5)) * (1 - P(8, 9)), r2 = out3(P(80.5, 83.5));
  if (r1 > 0) smell(c, 500, 1160, 175, 1080, { reveal: r1 });
  if (r2 > 0) smell(c, 500, 1160, 120, 1080, { reveal: r2 });
  // pak cik hujung lorong (lari di L10)
  const runP = P(73, 76.5);
  if (runP < 1) {
    const px = lerp(130, -260, in3(runP) * 0.4 + runP * 0.6), pinch = clamp(P(5.9, 6.4) + (b > 72 ? 1 : 0));
    const runing = b > 73 ? 1 : 0;
    person(c, px, 1450, 0.92, { shirt: '#2E86AB', skin: '#C98B5E', pinch: b < 8 || b > 72 ? pinch : 0, disgust: b > 6 && (b < 8 || b > 72), flip: runing === 1, run: runing, phase: b * 7, lean: runing ? 0.12 : 0 });
    if (b > 6 && b < 8.5) label(c, '?!', 190, 1130, { scale: life(6, 7.6, 0.5, 0.4), size: 50, bg: '#FFF4E0', fg: '#E63B2E' });
  }
  label(c, 'hujung lorong', 160, 1100 - 40, { scale: life(4, 7.4), size: 40, bg: '#FFF4E0', arrow: true });
  // barisan orang beratur
  const q = [[235, 76, '#7EBF6B', '#8D5A3B', { tudung: '#E05A8C' }], [170, 77, '#F2C14E', '#C98B5E', {}], [105, 78, '#9B6BD3', '#E0AC7E', { longHair: true }], [40, 79, '#E86A5C', '#A86E45', { cap: '#2B2024' }]];
  q.forEach(([x, bt, sh, sk, ex], i) => {
    const sc = pop(bt, 0.6); if (sc <= 0) return;
    c.save(); c.translate(x, 1452); c.scale(1, sc); person(c, 0, 0, 0.86, { shirt: sh, skin: sk, ...ex, phase: 0 }); c.restore();
  });
  foreground(c);
  label(c, 'BERATUR!', 190, 1090, { scale: life(79.5, 87.5), size: 46, bg: ACC, fg: '#FFF4E0', rot: 0.06 });
}


function plasticSet(c, x, y, s, col) {
  c.save(); c.translate(x, y); c.scale(s, s);
  fillP(c, col, cc => { cc.moveTo(-70, -150); cc.lineTo(70, -150); cc.lineTo(90, 0); cc.lineTo(60, 0); cc.lineTo(45, -110); cc.lineTo(-45, -110); cc.lineTo(-60, 0); cc.lineTo(-90, 0); cc.closePath(); }, 1.2);
  fillP(c, col, cc => cc.ellipse(0, -152, 92, 22, 0, 0, 7), 0.8);
  c.fillStyle = 'rgba(255,255,255,0.18)'; c.beginPath(); c.ellipse(-30, -156, 40, 8, 0, 0, 7); c.fill();
  c.restore();
}
function foreground(c) {
  plasticSet(c, 70, 1905, 1.25, '#D93A2E');
  plasticSet(c, 1010, 1915, 1.35, '#2E86AB');
  fillP(c, '#E9E4DA', cc => cc.ellipse(-40, 1790, 160, 40, 0, 0, 7), 1.2);
}

// ================================================================ ZON 2: HUTAN (pusat 540,-2000)
const GY = -1250; // aras tanah hutan
function elephantX() {
  const b = S.B;
  if (b < 35) return 1300;
  if (b < 38.5) return lerp(1300, 790, out3(P(35, 38.5)));
  if (b < 42) return 790;
  return lerp(790, 2500, (b - 42) / 9);
}
function zoneHutan(c, v) {
  const b = S.B;
  let g = c.createLinearGradient(0, -2960, 0, -1040); g.addColorStop(0, '#BFE3D0'); g.addColorStop(1, '#EEF6DC');
  c.fillStyle = g; c.fillRect(-900, -3300, 3800, 2300);
  const sg = c.createRadialGradient(950, -2700, 20, 950, -2700, 260); sg.addColorStop(0, 'rgba(255,245,200,0.9)'); sg.addColorStop(1, 'rgba(255,245,200,0)');
  c.fillStyle = sg; c.beginPath(); c.arc(950, -2700, 260, 0, 7); c.fill();
  const hill = (col, base, amp, fr, ph, k) => fillP(c, col, cc => { cc.moveTo(-900, -1000); for (let x = -900; x <= 2900; x += 40) cc.lineTo(x, base + Math.sin(x * fr + ph) * amp); cc.lineTo(2900, -1000); }, k);
  hill('#A9D3A2', -1800, 70, 0.004, 1, 0.6);
  for (let i = 0; i < 9; i++) jungleTree(c, -500 + i * 380 + rnd(i) * 80, -1600, 260 + rnd(i + 3) * 120, 1, 0.8);
  hill('#78B47E', -1560, 45, 0.006, 2, 0.8);
  [[900, 1], [1250, 0], [2050, 0], [2400, 1], [-300, 0]].forEach(([x, k], i) => jungleTree(c, x, GY + 10, 380 + rnd(i) * 160, k, 1));
  hill('#5A9A5B', GY - 10, 12, 0.01, 0, 1);
  c.fillStyle = '#4C8A4F'; c.fillRect(-900, GY + 30, 3800, 760);
  for (let i = 0; i < 70; i++) { const x = -800 + i * 55 + rnd(i) * 20; c.fillStyle = i % 2 ? '#3E7A45' : '#6BAA5E'; c.beginPath(); c.moveTo(x, GY + 40); c.lineTo(x + 8, GY + 5 - rnd(i) * 20); c.lineTo(x + 16, GY + 40); c.fill(); }
  // pokok durian besar
  durianTree(c, 430, GY);
  [[300, -2210, 30, 0.3], [470, -2180, 32, 0.5], [210, -2300, 28, 0.2]].forEach(([x, y, r, rp]) => hangingDurian(c, x, y, r, rp));
  // buah hero: tergantung → jatuh (b40) → dimakan (b41)
  const fall = P(40, 40.6);
  if (b < 41) {
    const fx = lerp(600, 700, fall), fy = lerp(-2190, GY - 40, fall * fall);
    if (fall <= 0) hangingDurian(c, 600, -2190, 40, 0.9); else durian(c, fx, fy, 40, { ripe: 0.9, rot: fall * 2 });
    if (fall <= 0 && b > 33) {
      for (let k = 0; k < 4; k++) {
        const ph = ((b - 33 - k * 1.5) % 6) / 6; if (b - 33 - k * 1.5 < 0) continue;
        c.strokeStyle = `rgba(160,205,70,${0.75 * (1 - ph)})`; c.lineWidth = 10 * (1 - ph) + 2; c.setLineDash([30, 18]);
        c.beginPath(); c.arc(600, -2190, 40 + ph * 900, 0, 7); c.stroke(); c.setLineDash([]);
      }
      smell(c, 640, -2190, 1050, -1950, { reveal: out3(P(33.5, 36)), k: 0.9 });
    }
  } else if (b < 42.2) {
    for (let k = 0; k < 6; k++) { const a = rnd(k) * 6.28, d = P(41, 42) * 60; c.fillStyle = '#FFD54A'; c.beginPath(); c.arc(700 + Math.cos(a) * d, GY - 60 + Math.sin(a) * d - P(41, 42) * 30, 7 * (1 - P(41, 42.2)), 0, 7); c.fill(); }
  }
  // gajah
  const ex = elephantX(), walking = (b > 35 && b < 38.5) || b > 42;
  // laluan putus-putus (biji dibawa jauh)
  if (b > 42) {
    c.save(); c.strokeStyle = '#FFF4E0'; c.lineWidth = 8; c.setLineDash([24, 18]); c.lineCap = 'round';
    c.beginPath(); c.moveTo(480, GY + 70); c.lineTo(Math.min(ex - 120, 1700), GY + 70); c.stroke(); c.restore();
  }
  const seeds = [[44.5, 1250], [46, 1650]];
  seeds.forEach(([bt, sx2], i) => {
    if (b < bt) return; const f = P(bt, bt + 0.5);
    if (i === 1 && b > 49) return; // biji kedua jadi anak pokok
    fillP(c, '#7A4A28', cc => cc.ellipse(sx2, lerp(GY - 150, GY + 40, f * f), 16, 11, 0.3, 0, 7), 0.6);
  });
  if (b > 34 && b < 52) elephant(c, ex, GY + 60, 1.0, { flip: b > 41.8, walk: walking ? 1 : 0, phase: b * 5, trunk: b > 40.4 && b < 41.6 ? Math.sin(P(40.4, 41.6) * Math.PI) : 0 });
  label(c, '!', 790 - 110, GY - 340, { scale: life(38, 40.2, 0.5, 0.4), size: 60, bg: ACC, fg: '#FFF4E0' });
  // JAUH: anak panah dari pokok ke biji
  const ja = life(46.5, 50.5, 0.6, 0.5);
  if (ja > 0) {
    c.save(); c.globalAlpha = Math.min(1, ja); c.strokeStyle = '#2B2024'; c.lineWidth = 6; c.beginPath(); c.moveTo(500, GY - 40); c.lineTo(1630, GY - 40); c.stroke();
    [[500, 1], [1630, -1]].forEach(([x, d]) => { c.beginPath(); c.moveTo(x + d * 26, GY - 58); c.lineTo(x, GY - 40); c.lineTo(x + d * 26, GY - 22); c.stroke(); });
    c.restore(); label(c, 'JAUH dari pokok induk', 1400, GY - 40, { scale: ja, size: 38 });
  }
  // anak pokok tumbuh
  if (b > 49) {
    const sp = pop(49, 0.6), gr = inOut(P(50, 53));
    const sx2 = 1650, h = lerp(30, 330, gr);
    c.save(); c.translate(sx2, GY + 40); c.scale(sp, sp);
    fillP(c, '#6A472C', cc => { cc.moveTo(-8 - gr * 14, 0); cc.lineTo(-5, -h); cc.lineTo(5, -h); cc.lineTo(8 + gr * 14, 0); }, 0.7);
    if (gr < 0.5) {
      [-1, 1].forEach(d => fillP(c, '#6BC266', cc => cc.ellipse(d * 26, -h, 28, 13, d * -0.5, 0, 7), 0.5));
    }
    const cr = gr * 150;
    if (cr > 5) [[0, -h - cr * 0.3, cr], [-cr * 0.7, -h + cr * 0.1, cr * 0.7], [cr * 0.7, -h + cr * 0.1, cr * 0.7]].forEach(([bx, by, br], i) => fillP(c, ['#3C8452', '#4C9A5E', '#2F6B45'][i], cc => cc.arc(bx, by, br, 0, 7), 0.8));
    if (gr > 0.7) durian(c, 40, -h + 40, 22, { ripe: 0.2, sx: P(52, 53) });
    c.restore();
  }
}

// ================================================================ ZON 3: BANDAR (pusat 540,4000)
const CGY = 4420;
function zoneBandar(c, v) {
  const b = S.B;
  let g = c.createLinearGradient(0, 2400, 0, CGY); g.addColorStop(0, '#1C2033'); g.addColorStop(1, '#3E4562');
  c.fillStyle = g; c.fillRect(-900, 2400, 3800, 2100);
  for (let i = -4; i < 16; i++) {
    const bx = -700 + i * 230, h = 600 + rnd(i + 20) * 700;
    fillP(c, '#2C324A', cc => cc.rect(bx, CGY - h, 200, h), 0.6);
    for (let wy = CGY - h + 40; wy < CGY - 80; wy += 70) for (let wx = bx + 25; wx < bx + 170; wx += 55) if (rnd(wx + wy * 7) > 0.7) { c.fillStyle = 'rgba(160,180,230,0.35)'; c.fillRect(wx, wy, 26, 36); }
  }
  // hotel
  fillP(c, '#4C5677', cc => cc.rect(130, 3240, 820, CGY - 3240), 1);
  for (let r = 0; r < 9; r++) for (let k = 0; k < 6; k++) { const on = rnd(r * 13 + k) > 0.4; c.fillStyle = on ? 'rgba(255,214,140,0.85)' : 'rgba(30,35,55,0.9)'; c.fillRect(185 + k * 125, 3300 + r * 85, 70, 50); }
  fillP(c, '#2C324A', cc => cc.rect(110, 4090, 860, 26), 0.8);
  c.font = "800 92px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.save(); c.shadowColor = 'rgba(255,200,110,0.9)'; c.shadowBlur = 30; c.fillStyle = '#FFD58A'; c.fillText('HOTEL', 540, 4050); c.restore();
  fillP(c, '#1E2333', cc => cc.rect(400, 4140, 280, 280), 0.8);
  c.fillStyle = 'rgba(140,200,230,0.35)'; c.fillRect(415, 4155, 120, 265); c.fillRect(545, 4155, 120, 265);
  // tren
  const tx = 1170;
  fillP(c, '#5A6178', cc => cc.rect(-900, CGY - 40, 3800, 40), 0.6);
  fillP(c, '#DCE1EA', cc => rr(cc, tx, 3990, 1200, 380, 60), 1);
  c.fillStyle = ACC; c.fillRect(tx, 4250, 1200, 34);
  for (let k = 0; k < 4; k++) { c.fillStyle = '#2B3550'; c.beginPath(); rr(c, tx + 60 + k * 270, 4050, 190, 150, 22); c.fill(); }
  fillP(c, '#B9C1D0', cc => cc.rect(tx + 395, 4040, 150, 330), 0.5);
  c.fillStyle = '#2B3550'; c.fillRect(tx + 410, 4060, 55, 150); c.fillRect(tx + 475, 4060, 55, 150);
  // lampu sorot pada durian
  const spot = P(56, 56.6) * (1 - P(64, 66));
  if (spot > 0) {
    c.save(); c.globalAlpha = spot;
    const sg = c.createLinearGradient(0, 3200, 0, CGY); sg.addColorStop(0, 'rgba(255,250,220,0.0)'); sg.addColorStop(1, 'rgba(255,250,220,0.28)');
    c.fillStyle = sg; c.beginPath(); c.moveTo(500, 3150); c.lineTo(580, 3150); c.lineTo(720, CGY); c.lineTo(360, CGY); c.fill();
    c.fillStyle = 'rgba(255,250,220,0.25)'; c.beginPath(); c.ellipse(540, CGY + 4, 190, 30, 0, 0, 7); c.fill(); c.restore();
  }
  // durian berwajah — melompat dari hotel ke tren
  let dx = 540, dy = CGY - 70, sq = 1;
  if (b > 66.4) { const p = P(66.4, 68.6); dx = lerp(540, 1470, inOut(p)); const hop = Math.abs(Math.sin(p * Math.PI * 4)); dy -= hop * 90 * (p < 1 ? 1 : 0); }
  if (b > 72) dx = -9999;
  durian(c, dx, dy, 62, { ripe: 0.4, face: { sad: b > 61.5 }, sx: 1, sy: sq });
  noSign(c, 540, 4250, 70, pop(65, 0.6));
  noSign(c, tx + 470, 4130, 62, pop(69, 0.6));
}

// ================================================================ overlay skrin
function screenDurian(cam) { return toScreen(cam, DUR.x, DUR.y); }
function overlay(c, cam) {
  const b = S.B;
  c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  // ---- HOOK: tajuk
  const tOut = 1 - in3(P(7, 7.7));
  if (b < 7.8) {
    const yo = -P(7, 7.7) * 300;
    c.save(); c.globalAlpha = tOut;
    label(c, 'SEBAB APA?', 540, 180 + yo, { scale: pop(0, 0.6), size: 40, bg: ACC, fg: '#FFF4E0' });
    bigText(c, 'Kenapa bau durian', 540, 315 + yo, 92, { scale: pop(0.1, 0.7) });
    bigText(c, 'boleh sampai ke', 540, 420 + yo, 92, { scale: pop(2, 0.7) });
    const s3 = pop(2.4, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 540 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -330, -64, 660, 128, 24), 1.2); c.restore(); bigText(c, 'hujung lorong?', 540, 540 + yo, 96, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
  }
  // ---- L2: molekul keluar dari isi durian
  if (b > 9.5 && b < 25) {
    const [sx, sy] = screenDurian(cam);
    for (let i = 0; i < 10; i++) {
      const b0 = 9.6 + i * 0.55; if (b < b0) continue;
      const p = (b - b0) / 9, a = 1 - P(16.6, 17.4);
      if (a <= 0) continue;
      const x = sx + (rnd(i) - 0.5) * 820 * Math.min(1, p * 2.2) + Math.sin(b * 0.9 + i) * 25;
      const y = sy - 120 - Math.min(1, p) * (560 + rnd(i + 4) * 260);
      molecule(c, x, y, pop(b0, 0.5) * (0.75 + rnd(i + 2) * 0.4), { rot: b * 0.4 + i, alpha: a * 0.95, S: i === 3 });
    }
    label(c, 'PULUHAN SEBATIAN', 540, 330, { scale: life(12, 16.3), size: 50, bg: '#FFF4E0', fg: '#2B2024' });
    // L3: molekul sulfur dibesarkan
    const hs = P(16.6, 17.3);
    if (hs > 0) {
      const x = lerp(sx + (rnd(3) - 0.5) * 820, 540, out3(hs)), y = lerp(sy - 560, 400, out3(hs));
      const out = 1 - in3(P(24, 24.6));
      molecule(c, x, y, lerp(1, 2.3, out3(hs)) * out, { rot: lerp(b * 0.4 + 3, -0.3, hs), S: true, glow: P(17, 17.6) * (0.8 + 0.2 * Math.sin(b * 4)) });
      label(c, 'S = SULFUR', 540, 625, { scale: life(17.3, 24), size: 46, bg: '#FFD23F', fg: '#2B2024' });
      const card = life(18.6, 24, 0.6, 0.5);
      if (card > 0) {
        c.save(); c.translate(540, 900); c.scale(card, card);
        fillP(c, '#FFF4E0', cc => rr(cc, -460, -170, 920, 340, 40), 1.4);
        c.restore();
        onion(c, 540 - 290 * card, 880, pop(19, 0.6) * 1.15);
        egg(c, 540, 895, pop(21, 0.6) * 1.1);
        durian(c, 540 + 290 * card, 890, 62 * pop(22.5, 0.6), { ripe: 0.8 });
        c.save(); c.font = "900 36px Nunito"; c.textAlign = 'center'; c.fillStyle = '#5A4A50';
        [['bawang', 250, 19], ['telur busuk', 540, 21], ['durian', 830, 22.5]].forEach(([t, x, bt]) => { c.globalAlpha = P(bt, bt + 0.5) * card; c.fillText(t, x, 1030); });
        c.restore();
        [[395, 21], [685, 22.5]].forEach(([x, bt]) => { c.save(); c.globalAlpha = P(bt, bt + 0.4) * card; c.fillStyle = '#FFD23F'; c.strokeStyle = '#2B2024'; c.lineWidth = 4; c.beginPath(); c.arc(x, 890, 22, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#2B2024'; c.font = "800 26px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('S', x, 892); c.restore(); });
      }
    }
  }
  // ---- L4: meter bau
  const mt = life(25, 31, 0.6, 0.4);
  if (mt > 0) {
    const fillv = inOut(P(26, 30)) * 0.92 + 0.08;
    c.save(); c.translate(940, 820); c.scale(mt, mt);
    fillP(c, '#FFF4E0', cc => rr(cc, -55, -330, 110, 600, 55), 1.2);
    c.fillStyle = '#E9DCC4'; c.beginPath(); rr(c, -30, -300, 60, 520, 30); c.fill();
    const hh = 520 * fillv; c.fillStyle = mix('#8DC63F', '#FF4B2B', fillv); c.beginPath(); rr(c, -30, 220 - hh, 60, hh, 30); c.fill();
    c.fillStyle = '#2B2024'; c.font = "800 40px 'Baloo 2'"; c.textAlign = 'center'; c.fillText('BAU', 0, 300 - 20 + 30);
    c.restore();
    label(c, 'masak', 760, 1060, { scale: life(26.3, 30.5), size: 40, bg: '#FFF4E0' });
  }
  stamp(c, 'MASAK!', 470, 540, 110, pop(30, 0.45) * (1 - P(31, 31.4)), -0.12, '#E2591F');
  // ---- L5
  label(c, 'HUTAN', 540, 300, { scale: life(33.2, 39.5), size: 52, bg: '#2F6B45', fg: '#FFF4E0' });
  // ---- L7 strategi
  const st = life(53, 55.3, 0.6, 0.4);
  if (st > 0) {
    c.save(); c.translate(540, 520); c.scale(st, st); c.rotate(-0.04);
    fillP(c, ACC, cc => rr(cc, -330, -95, 660, 190, 36), 1.4);
    c.restore();
    bigText(c, 'STRATEGI!', 540, 525, 120, { scale: st, rot: -0.04, stroke: '#7A2A12' });
    for (let k = 0; k < 10; k++) { const a = k / 10 * 6.28, d = 380 + P(53, 54.5) * 90; c.save(); c.globalAlpha = 1 - P(53.5, 55); c.fillStyle = '#FFD23F'; c.translate(540 + Math.cos(a) * d, 520 + Math.sin(a) * d * 0.5); c.rotate(a); c.fillRect(-14, -4, 28, 8); c.restore(); }
  }
  // ---- L8: TAPI...
  const tp = life(56, 60, 0.5, 0.6);
  if (tp > 0) { const sh = Math.sin(b * 40) * 4 * (1 - P(56, 57.5)); bigText(c, 'TAPI...', 540 + sh, 520, 170, { scale: tp, fill: '#FFF4E0', stroke: '#1C2033' }); }
  stamp(c, 'KENA LARANG', 540, 800, 92, pop(61.5, 0.45) * (1 - P(64.4, 64.9)));
  // ---- L11 banner
  const kd = life(86, 88, 0.6, 0.4);
  if (kd > 0) { c.save(); c.translate(540, 470); c.rotate(0.03); c.scale(kd, kd); fillP(c, '#FFF4E0', cc => rr(cc, -400, -80, 800, 160, 32), 1.3); c.restore(); bigText(c, 'buat kerja dia!', 540, 474, 90, { scale: kd, rot: 0.03, fill: ACC, stroke: '#2B2024', shadow: false }); }
  // ---- L12 soalan
  const dim = P(88, 88.6) * (1 - P(96, 96.3));
  if (dim > 0) {
    c.fillStyle = `rgba(20,14,26,${0.55 * dim})`; c.fillRect(0, 0, W, H);
    const qc = pop(88.5, 0.7);
    bigText(c, 'Kau team mana?', 540, 470, 104, { scale: qc });
    const bt1 = pop(90, 0.6), bt2 = pop(92, 0.6);
    c.save(); c.translate(540, 720); c.scale(bt1, bt1); fillP(c, '#5DAA3A', cc => rr(cc, -380, -85, 760, 170, 85), 1.3);
    c.restore(); bigText(c, 'TEAM DURIAN', 540, 724, 80, { scale: bt1, fill: '#FFF4E0', stroke: '#2D5A1C' });
    c.save(); c.translate(540, 940); c.scale(bt2, bt2); fillP(c, '#E2483A', cc => rr(cc, -380, -85, 760, 170, 85), 1.3);
    c.restore(); bigText(c, 'TEAM TUTUP HIDUNG', 540, 944, 70, { scale: bt2, fill: '#FFF4E0', stroke: '#7A1E16' });
    const cm = pop(94, 0.6);
    if (cm > 0) { label(c, 'jawab di komen', 540, 1140, { scale: cm, size: 46, bg: '#FFF4E0' }); c.save(); c.translate(540, 1215 + Math.sin(b * 3) * 10); c.scale(cm, cm); c.fillStyle = '#FFF4E0'; c.beginPath(); c.moveTo(-26, 0); c.lineTo(26, 0); c.lineTo(0, 34); c.fill(); c.restore(); }
  }
}

function outro(c) {
  const b = S.B; if (b < 95.6) return;
  const p = out3(P(95.8, 96.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = ACC; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.12; c.fillStyle = '#FFF4E0';
  for (let i = 0; i < 18; i++) { c.beginPath(); c.arc(rnd(i) * W, rnd(i + 30) * H, 40 + rnd(i + 3) * 120, 0, 7); c.fill(); }
  c.globalAlpha = 1;
  S.ZK = 1;
  cicak(c, 540, 690, 1.9 * pop(96.2, 0.8), 0, { wink: P(97.5, 97.7) * (1 - P(98.4, 98.6)) });
  bigText(c, 'SEBAB APA?', 540, 1040, 150, { scale: pop(96.5, 0.7), stroke: '#7A2A12' });
  label(c, 'Satu soalan. Satu minit.', 540, 1190, { scale: pop(97.2, 0.6), size: 48, bg: '#FFF4E0' });
  label(c, 'follow untuk soalan seterusnya', 540, 1320, { scale: pop(97.8, 0.6), size: 36, bg: '#2B2024', fg: '#FFF4E0' });
  c.restore();
}

// ================================================================ kapsyen
function drawCaptions(c) {
  const t = S.B * BEAT; if (S.B > 95.8) return;
  const cap = CAPS.find(k => t >= k.start && t < k.end);
  if (!cap || cap.hidden) return;
  const age = (t - cap.start) / BEAT;
  const sc = 0.9 + 0.1 * back(clamp(age / 0.35));
  caption(c, cap.segs, 540, 1500, { scale: sc, alpha: clamp(age / 0.15) });
}

// ================================================================ dunia + render
function world(c, cam) {
  applyCam(c, cam);
  const v = viewRect(cam);
  c.fillStyle = '#2A2238'; c.fillRect(v.x0 - 10, v.y0 - 10, v.x1 - v.x0 + 20, v.y1 - v.y0 + 20);
  if (sees(v, -900, -1040, 2100, 2500)) zoneLorong(c, v);
  if (sees(v, -900, -3300, 2900, -480)) zoneHutan(c, v);
  if (sees(v, -900, 2400, 2900, 4500)) zoneBandar(c, v);
}

function renderFrame(t) {
  const b = t / BEAT; S.B = b;
  const cam = camAt(CAM, b);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (cam.whip) {
    // motion blur: purata beberapa sampel kamera
    const N = 16, sh = 0.2;
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < N; i++) {
      const cs = camAt(CAM, b + (i / (N - 1) - 0.5) * sh);
      lctx.setTransform(1, 0, 0, 1, 0, 0); world(lctx, cs);
      ctx.filter = 'blur(6px)'; ctx.globalAlpha = 1 / (i + 1); ctx.drawImage(layer, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
    }
  } else world(ctx, cam);
  overlay(ctx, cam);
  drawCaptions(ctx);
  outro(ctx);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  // fade masuk/keluar hitam
  const fo = P(TL.totalBeats + TL.tailSeconds / BEAT - 1.2, TL.totalBeats + TL.tailSeconds / BEAT);
  grain(ctx, 0.09);
  vignette(ctx, 0.32);
  if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
}

window.ready = (async () => {
  TL = await (await fetch('timeline.json')).json();
  CAPS = await (await fetch('captions.json')).json();
  BEAT = 60 / TL.bpm;
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito');
  await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
