// toon.js — watak kartun keluarga (BABA, IBU, RAYSHA) dengan ekspresi muka.
// Reka bentuk berdasarkan rupa sebenar dalam gambar keluarga, dilukis semula sebagai kartun kertas.
// Guna: TOON.person(c, 'baba'|'ibu'|'raysha', x, y, s, { pose, expr, talk, flip })
//       TOON.setPhoto(who, {...}) — guna muka sebenar (sticker foto) dengan kesan ekspresi
//       TOON.face(c, who, x, y, r, expr)   — muka sahaja (untuk kad/close-up)
// Ekspresi: happy, laugh, wow, wink, love, sleepy, sad, talk, cheeky
'use strict';
const TOON = (() => {
  const { S, fillP, rr, shadow, lerp } = PAPER;
  const INK = '#2B2024';
  const LOOK = {
    baba:   { skin: '#C68A62', skinD: '#A9714D', hair: '#1E1A1C', glasses: true, beard: true, face: [0.86, 1.0] },
    ibu:    { skin: '#F2CDB0', skinD: '#E2B596', hijab: '#EFE6D8', hijabD: '#D9CDBB', lips: '#D9707A', face: [0.94, 0.96], eyeK: 1.25 },
    raysha: { skin: '#F0C7A4', skinD: '#E0AE89', hair: '#2E211C', pigtails: '#FF6FA8', kid: true, face: [1.0, 0.95] },
  };
  const PRESET = {
    happy:  { eyes: 'open', mouth: 'smile', brows: 'neutral' },
    laugh:  { eyes: 'happy', mouth: 'grin', brows: 'up' },
    wow:    { eyes: 'wide', mouth: 'o', brows: 'up' },
    wink:   { eyes: 'wink', mouth: 'smirk', brows: 'neutral' },
    love:   { eyes: 'heart', mouth: 'grin', brows: 'up' },
    sleepy: { eyes: 'closed', mouth: 'small', brows: 'neutral' },
    sad:    { eyes: 'open', mouth: 'frown', brows: 'sad' },
    talk:   { eyes: 'open', mouth: 'talk', brows: 'neutral' },
    cheeky: { eyes: 'happy', mouth: 'tongue', brows: 'up' },
  };

  function eyes(c, L, e, r) {
    const ex = r * 0.34, ey = -r * 0.08, er = r * (L.kid ? 0.17 : 0.13) * (L.eyeK || 1);
    const blink = e.eyes === 'open' && ((S.B * 0.9 + (L.kid ? 0.4 : L.glasses ? 0.2 : 0.7)) % 4 < 0.12);
    [-1, 1].forEach(sd => {
      const x = sd * ex, kind = e.eyes === 'wink' && sd > 0 ? 'happy' : (blink ? 'closed' : e.eyes);
      c.save(); c.translate(x, ey);
      if (kind === 'open' || kind === 'wide' || kind === 'wink') {
        const k = kind === 'wide' ? 1.25 : 1;
        c.fillStyle = '#FFFFFF'; c.beginPath(); c.ellipse(0, 0, er * 1.05 * k, er * 1.2 * k, 0, 0, 7); c.fill();
        c.fillStyle = L.kid ? '#3A2618' : INK; c.beginPath(); c.ellipse(0, er * 0.12, er * 0.72 * k, er * 0.85 * k, 0, 0, 7); c.fill();
        c.fillStyle = '#FFFFFF'; c.beginPath(); c.arc(-er * 0.25, -er * 0.2, er * 0.28, 0, 7); c.fill(); c.beginPath(); c.arc(er * 0.25, er * 0.3, er * 0.12, 0, 7); c.fill();
      } else if (kind === 'happy') {
        c.strokeStyle = INK; c.lineWidth = r * 0.055; c.lineCap = 'round'; c.beginPath(); c.arc(0, er * 0.4, er * 0.9, Math.PI * 1.15, Math.PI * 1.85); c.stroke();
      } else if (kind === 'closed') {
        c.strokeStyle = INK; c.lineWidth = r * 0.05; c.lineCap = 'round'; c.beginPath(); c.arc(0, -er * 0.2, er * 0.85, Math.PI * 0.15, Math.PI * 0.85); c.stroke();
      } else if (kind === 'heart') {
        const h = er * 1.3, pulse = 1 + 0.12 * Math.sin(S.B * Math.PI * 2);
        c.scale(pulse, pulse); c.fillStyle = '#E63B5C'; c.beginPath(); c.moveTo(0, h * 0.6); c.bezierCurveTo(-h * 1.2, -h * 0.1, -h * 0.6, -h * 1.1, 0, -h * 0.35); c.bezierCurveTo(h * 0.6, -h * 1.1, h * 1.2, -h * 0.1, 0, h * 0.6); c.fill();
      }
      c.restore();
    });
    // kening
    c.strokeStyle = L.hair || (L.hijab ? '#5A4032' : INK); c.lineWidth = r * (L.glasses ? 0.07 : 0.05); c.lineCap = 'round';
    [-1, 1].forEach(sd => {
      const bx = sd * ex, by = ey - er * (e.brows === 'up' ? 2.3 : 1.9);
      const tilt = e.brows === 'sad' ? sd * 0.35 : e.brows === 'angry' ? -sd * 0.35 : 0;
      c.save(); c.translate(bx, by); c.rotate(tilt); c.beginPath(); c.arc(0, er * 0.9, er * 1.1, Math.PI * 1.25, Math.PI * 1.75); c.stroke(); c.restore();
    });
  }
  function mouth(c, L, e, r) {
    const my = r * 0.36, w = r * 0.26;
    let kind = e.mouth;
    if (kind === 'talk') kind = (Math.sin(S.B * Math.PI * 3.2) > 0.1) ? 'open' : 'smile';
    c.save(); c.translate(0, my); c.lineCap = 'round'; c.lineJoin = 'round';
    const lip = L.lips || '#B5554F';
    if (kind === 'smile') { c.strokeStyle = INK; c.lineWidth = r * 0.05; c.beginPath(); c.arc(0, -w * 0.5, w, Math.PI * 0.2, Math.PI * 0.8); c.stroke(); if (L.lips) { c.strokeStyle = L.lips; c.lineWidth = r * 0.03; c.stroke(); } }
    if (kind === 'smirk') { c.strokeStyle = INK; c.lineWidth = r * 0.05; c.beginPath(); c.moveTo(-w * 0.7, 0); c.quadraticCurveTo(0, w * 0.4, w * 0.8, -w * 0.3); c.stroke(); }
    if (kind === 'grin' || kind === 'open' || kind === 'tongue') {
      const hgt = kind === 'open' ? w * 0.7 : w * 0.85;
      c.fillStyle = '#5A1F24'; c.beginPath(); c.moveTo(-w, -w * 0.1); c.quadraticCurveTo(0, -w * 0.25, w, -w * 0.1); c.quadraticCurveTo(w * 0.8, hgt, 0, hgt); c.quadraticCurveTo(-w * 0.8, hgt, -w, -w * 0.1); c.fill();
      c.fillStyle = '#FFFFFF'; c.beginPath(); c.moveTo(-w * 0.85, -w * 0.08); c.quadraticCurveTo(0, -w * 0.2, w * 0.85, -w * 0.08); c.lineTo(w * 0.7, w * 0.15); c.quadraticCurveTo(0, w * 0.05, -w * 0.7, w * 0.15); c.fill();
      c.fillStyle = '#E86A7A'; c.beginPath(); c.ellipse(0, hgt * 0.75, w * 0.45, w * (kind === 'tongue' ? 0.45 : 0.22), 0, 0, 7); c.fill();
    }
    if (kind === 'o') { c.fillStyle = '#5A1F24'; c.beginPath(); c.ellipse(0, w * 0.15, w * 0.38, w * 0.48, 0, 0, 7); c.fill(); }
    if (kind === 'small') { c.strokeStyle = INK; c.lineWidth = r * 0.04; c.beginPath(); c.arc(0, -w * 0.15, w * 0.35, Math.PI * 0.25, Math.PI * 0.75); c.stroke(); }
    if (kind === 'frown') { c.strokeStyle = INK; c.lineWidth = r * 0.05; c.beginPath(); c.arc(0, w * 0.6, w * 0.7, Math.PI * 1.2, Math.PI * 1.8); c.stroke(); }
    c.restore();
  }

  // muka (r = jejari kepala)
  function face(c, who, x, y, r, expr = 'happy', o = {}) {
    const L = LOOK[who], e = typeof expr === 'string' ? (PRESET[expr] || PRESET.happy) : expr;
    const [fx, fy] = L.face;
    c.save(); c.translate(x, y); if (o.tilt) c.rotate(o.tilt);
    // belakang: tudung / rambut belakang
    if (L.hijab) fillP(c, L.hijab, cc => { cc.moveTo(-r * 1.25, r * 1.55); cc.quadraticCurveTo(-r * 1.35, -r * 1.25, 0, -r * 1.3); cc.quadraticCurveTo(r * 1.35, -r * 1.25, r * 1.25, r * 1.55); cc.quadraticCurveTo(0, r * 1.8, -r * 1.25, r * 1.55); }, 1);
    if (L.kid) {
      [-1, 1].forEach(sd => { c.save(); c.translate(sd * r * 1.02, -r * 0.35); c.rotate(sd * (0.35 + Math.sin(S.B * Math.PI) * 0.08)); fillP(c, L.hair, cc => cc.ellipse(sd * r * 0.18, r * 0.25, r * 0.24, r * 0.42, 0, 0, 7), 0.5); c.fillStyle = L.pigtails; c.beginPath(); c.arc(0, -r * 0.08, r * 0.11, 0, 7); c.fill(); c.restore(); });
      fillP(c, L.hair, cc => cc.ellipse(0, -r * 0.05, r * 1.04, r * 1.02, 0, 0, 7), 0.8);
    }
    // telinga
    if (!L.hijab) [-1, 1].forEach(sd => fillP(c, L.skin, cc => cc.ellipse(sd * r * fx * 0.98, r * 0.02, r * 0.16, r * 0.22, 0, 0, 7), 0.4));
    // muka
    fillP(c, L.skin, cc => cc.ellipse(0, 0, r * fx, r * fy, 0, 0, 7), L.hijab ? 0.4 : 1);
    if (L.hijab) { c.strokeStyle = L.hijabD; c.lineWidth = r * 0.06; c.beginPath(); c.ellipse(0, 0, r * fx * 1.02, r * fy * 1.02, 0, Math.PI * 1.05, Math.PI * 1.95); c.stroke(); }
    // rambut depan
    if (L.beard) {
      c.fillStyle = L.hair; c.beginPath(); c.moveTo(-r * 0.86, -r * 0.2); c.quadraticCurveTo(-r * 0.95, -r * 1.05, -r * 0.1, -r * 1.12); c.quadraticCurveTo(r * 0.55, -r * 1.35, r * 0.95, -r * 0.95); c.quadraticCurveTo(r * 0.95, -r * 0.55, r * 0.86, -r * 0.25); c.quadraticCurveTo(r * 0.6, -r * 0.72, r * 0.05, -r * 0.7); c.quadraticCurveTo(-r * 0.55, -r * 0.68, -r * 0.78, -r * 0.2); c.fill();
      c.fillStyle = 'rgba(30,26,28,0.22)'; c.beginPath(); c.ellipse(0, r * 0.62, r * 0.5, r * 0.32, 0, 0, Math.PI); c.fill();   // janggut nipis
      c.fillStyle = 'rgba(30,26,28,0.55)'; c.beginPath(); c.ellipse(0, r * 0.27, r * 0.24, r * 0.05, 0, 0, 7); c.fill();       // misai
    }
    if (L.kid) { c.fillStyle = L.hair; c.beginPath(); c.moveTo(-r * 0.95, -r * 0.05); c.quadraticCurveTo(-r * 0.9, -r * 1.02, 0, -r * 1.0); c.quadraticCurveTo(r * 0.9, -r * 1.02, r * 0.95, -r * 0.05); c.quadraticCurveTo(r * 0.6, -r * 0.55, r * 0.25, -r * 0.45); c.lineTo(r * 0.1, -r * 0.3); c.lineTo(-r * 0.05, -r * 0.48); c.quadraticCurveTo(-r * 0.6, -r * 0.55, -r * 0.95, -r * 0.05); c.fill(); }
    // pipi
    c.fillStyle = 'rgba(255,120,130,0.28)'; [-1, 1].forEach(sd => { c.beginPath(); c.ellipse(sd * r * 0.52, r * 0.22, r * 0.15, r * 0.09, 0, 0, 7); c.fill(); });
    eyes(c, L, e, r);
    // hidung
    c.strokeStyle = L.skinD; c.lineWidth = r * 0.045; c.lineCap = 'round'; c.beginPath(); c.arc(0, r * 0.12, r * 0.07, Math.PI * 0.1, Math.PI * 0.9); c.stroke();
    mouth(c, L, e, r);
    // cermin mata baba
    if (L.glasses) {
      c.strokeStyle = '#141214'; c.lineWidth = r * 0.075;
      [-1, 1].forEach(sd => { c.beginPath(); c.ellipse(sd * r * 0.34, -r * 0.06, r * 0.25, r * 0.22, 0, 0, 7); c.stroke(); });
      c.beginPath(); c.moveTo(-r * 0.1, -r * 0.1); c.quadraticCurveTo(0, -r * 0.16, r * 0.1, -r * 0.1); c.stroke();
      c.fillStyle = 'rgba(255,255,255,0.18)'; [-1, 1].forEach(sd => { c.beginPath(); c.ellipse(sd * r * 0.34 - r * 0.08, -r * 0.14, r * 0.07, r * 0.04, -0.6, 0, 7); c.fill(); });
    }
    c.restore();
  }


  // ---------------------------------------------------------------- KEPALA FOTO + EKSPRESI
  // PHOTOS[who] = { c: canvas pra-skala (bayang dibakar), m: {w,h,neckX,neckY}, eyes: [[fx,fy],[fx,fy]], width: lebar sasaran }
  const PHOTOS = {};
  function setPhoto(who, data) { PHOTOS[who] = data; }
  function heartShape(c, x, y, h, col) { c.fillStyle = col; c.beginPath(); c.moveTo(x, y + h * 0.6); c.bezierCurveTo(x - h * 1.2, y - h * 0.1, x - h * 0.6, y - h * 1.1, x, y - h * 0.35); c.bezierCurveTo(x + h * 0.6, y - h * 1.1, x + h * 1.2, y - h * 0.1, x, y + h * 0.6); c.fill(); }
  function photoHead(c, who, x, y, expr, extra = {}) {
    const ph = PHOTOS[who], b = S.B, m = ph.m, hs = ph.width / m.w;
    let sx = 1, sy = 1, rot = Math.sin(b * Math.PI * 0.5) * 0.04 + (extra.tilt || 0), dy = 0;
    if (expr === 'talk') { sy = 1 + 0.035 * Math.max(0, Math.sin(b * Math.PI * 3.2)); }
    if (expr === 'laugh') { dy = -Math.abs(Math.sin(b * Math.PI * 4)) * 14; rot += Math.sin(b * Math.PI * 4) * 0.08; }
    if (expr === 'wow') { const k = 1 + 0.08 * Math.max(0, Math.sin(b * Math.PI * 2)); sx = sy = k; }
    if (expr === 'sleepy') { rot += 0.28; dy = 10; }
    if (expr === 'sad') { rot -= 0.12; dy = 8; }
    c.save(); c.translate(x, y + dy); c.rotate(rot); c.scale(sx, sy);
    const k = hs / ph.c.sc;
    c.drawImage(ph.c, -(m.neckX * ph.c.sc + ph.c.pad) * k, -(m.neckY * ph.c.sc + ph.c.pad) * k, ph.c.width * k, ph.c.height * k);
    const E = ph.eyes.map(([fx, fy]) => [(fx * m.w - m.neckX) * hs, (fy * m.h - m.neckY) * hs]);
    const er = ph.width * 0.085, top = -m.neckY * hs, W = m.w * hs;
    if (expr === 'love') { const pu = 1 + 0.15 * Math.sin(b * Math.PI * 2); E.forEach(([ex, ey]) => heartShape(c, ex, ey, er * 1.6 * pu, '#E63B5C')); }
    if (expr === 'sad') { E.forEach(([ex, ey], i) => { const p = ((b * 0.8 + i * 0.5) % 1); c.fillStyle = `rgba(110,180,255,${0.9 * (1 - p)})`; c.beginPath(); c.ellipse(ex, ey + er * 1.2 + p * er * 3, er * 0.35, er * 0.55, 0, 0, 7); c.fill(); }); }
    if (expr === 'sleepy') { E.forEach(([ex, ey]) => { c.strokeStyle = 'rgba(43,32,36,0.0)'; }); }
    c.restore();
    // kesan di luar kepala (tak berputar)
    const hx = x, hy = y + dy + top * 0.55;
    if (expr === 'laugh') { const s2 = 0.9 + 0.1 * Math.sin(b * Math.PI * 4); PAPER.label(c, 'HAHA!', hx + W * 0.62, hy - W * 0.35, { scale: s2, size: 44, bg: '#FFD447', fg: INK, rot: 0.12 }); }
    if (expr === 'wow') { PAPER.label(c, '!', hx + W * 0.55, hy - W * 0.45, { size: 64, bg: '#E63B2E', fg: '#FFF4E0', rot: 0.1 }); for (let i = 0; i < 6; i++) { const a = i / 6 * 6.283 + b, d = W * (0.75 + 0.06 * Math.sin(b * 6 + i)); star(c, hx + Math.cos(a) * d, hy + Math.sin(a) * d * 0.8, W * 0.06, '#FFD447'); } }
    if (expr === 'love') for (let i = 0; i < 4; i++) { const p = ((b * 0.5 + i / 4) % 1); c.save(); c.globalAlpha = 1 - p; heartShape(c, hx + (i % 2 ? 1 : -1) * W * (0.45 + 0.1 * i), hy - p * W * 0.9, W * 0.07, '#FF6F91'); c.restore(); }
    if (expr === 'sleepy') for (let k = 0; k < 3; k++) { const p = ((b * 0.4 + k / 3) % 1); c.save(); c.globalAlpha = 1 - p; c.font = `800 ${Math.round(W * (0.14 + k * 0.04))}px 'Baloo 2'`; c.fillStyle = '#5B8DB8'; c.fillText('Z', hx + W * 0.4 + p * W * 0.3, hy - W * 0.2 - p * W * 0.6); c.restore(); }
    if (expr === 'cheeky') for (let i = 0; i < 3; i++) star(c, hx + W * (0.5 + 0.08 * i), hy - W * (0.3 + 0.15 * i), W * (0.05 + 0.02 * Math.sin(b * 5 + i)), '#FFD447');
  }
  function star(c, x, y, r, col) { c.fillStyle = col; c.beginPath(); for (let i = 0; i < 10; i++) { const rr2 = i % 2 ? r * 0.45 : r, a = i / 10 * 6.283 - 1.57; c.lineTo(x + Math.cos(a) * rr2, y + Math.sin(a) * rr2); } c.fill(); }

  // badan penuh
  function person(c, who, x, y, s, o = {}) {
    if (s <= 0.001) return;
    const L = LOOK[who], b = S.B, pose = o.pose || 'stand';
    c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
    const jump = pose === 'jump' ? -Math.abs(Math.sin(b * Math.PI)) * 120 : 0;
    const bob = (pose === 'stand' || pose === 'wave' || pose === 'cheer') ? -Math.abs(Math.sin(b * Math.PI)) * 8 : 0;
    c.translate(0, jump + bob);
    const kid = L.kid, H = kid ? 300 : 520, hipY = -H * 0.42, neckY = -H * (kid ? 0.92 : 0.86);
    const run = pose === 'run' ? 1 : 0, ph = b * Math.PI * 2;
    // pakaian
    const top = who === 'baba' ? 'stripes' : who === 'ibu' ? '#2A2A2E' : '#FFF6EE';
    const pants = who === 'baba' ? '#5E7FA8' : who === 'ibu' ? '#2A2A2E' : '#F7B2C8';
    // kaki
    c.save(); c.lineCap = 'round';
    [-1, 1].forEach(sd => {
      const a = run ? Math.sin(ph + (sd > 0 ? Math.PI : 0)) * 0.6 : (pose === 'jump' ? sd * 0.25 : 0);
      c.strokeStyle = pants; c.lineWidth = kid ? 44 : 60;
      c.beginPath(); c.moveTo(sd * (kid ? 26 : 36), hipY); c.lineTo(sd * (kid ? 30 : 42) + Math.sin(a) * (-hipY - 30), -30 * Math.cos(a)); c.stroke();
      c.fillStyle = who === 'raysha' ? '#FF8FB1' : '#2B2024'; c.beginPath(); c.ellipse(sd * (kid ? 32 : 46) + Math.sin(a) * (-hipY - 30) + sd * 6, -12, kid ? 26 : 34, kid ? 14 : 16, 0, 0, 7); c.fill();
    });
    c.restore();
    // badan
    const bw = kid ? 74 : 108;
    if (who === 'ibu') fillP(c, top, cc => { cc.moveTo(-bw * 0.85, neckY + 20); cc.lineTo(bw * 0.85, neckY + 20); cc.lineTo(bw * 1.15, hipY + 130); cc.lineTo(-bw * 1.15, hipY + 130); cc.closePath(); }, 1);
    else fillP(c, top === 'stripes' ? '#1F2A44' : top, cc => rr(cc, -bw, neckY + 16, bw * 2, hipY - neckY + 22, kid ? 30 : 40), 1);
    if (top === 'stripes') { c.save(); c.beginPath(); rr(c, -bw, neckY + 16, bw * 2, hipY - neckY + 22, 40); c.clip(); c.fillStyle = '#F2F2EE'; for (let yy = neckY + 50; yy < hipY + 40; yy += 56) c.fillRect(-bw, yy, bw * 2, 22); c.restore(); fillP(c, '#1F2A44', cc => { cc.moveTo(-34, neckY + 14); cc.lineTo(0, neckY + 50); cc.lineTo(34, neckY + 14); cc.closePath(); }, 0.3); }
    if (who === 'ibu') { c.strokeStyle = 'rgba(255,255,255,0.22)'; c.lineWidth = 3; for (let k = 0; k < 9; k++) { c.beginPath(); c.arc(-bw * 1.1 + k * bw * 0.275, hipY + 118, 12, Math.PI, 0); c.stroke(); } }
    if (who === 'raysha') { c.fillStyle = '#FFC9DA'; for (let k = 0; k < 5; k++) { c.beginPath(); c.arc(-40 + k * 20, neckY + 70 + (k % 2) * 30, 7, 0, 7); c.fill(); } }
    // lengan (sudut: positif ke luar)
    const w = Math.sin(ph);
    let La = [0.2, 0.1], Ra = [0.2, 0.1];
    if (pose === 'wave') Ra = [2.3, 2.6 + 0.4 * w];
    if (pose === 'cheer' || pose === 'jump') { La = [2.5 + 0.15 * w, 2.9]; Ra = [2.5 - 0.15 * w, 2.9]; }
    if (pose === 'point') Ra = [1.45, 1.6];
    if (pose === 'run') { La = [0.5 * w, 0.9]; Ra = [-0.5 * w, 0.9]; }
    if (pose === 'hold') { La = [0.5, -0.9]; Ra = [0.5, -0.9]; }
    const armCol = who === 'baba' ? '#1F2A44' : who === 'ibu' ? '#2A2A2E' : '#FFF6EE', aw = kid ? 30 : 40, al = kid ? 52 : 90;
    [[-1, La], [1, Ra]].forEach(([sd, A]) => {
      const sx = sd * (bw - 6), sy = neckY + 40, a1 = sd * A[0], a2 = sd * A[1];
      const ex = sx + Math.sin(a1) * al, ey = sy + Math.cos(a1) * al, hx = ex + Math.sin(a2) * al, hy = ey + Math.cos(a2) * al;
      c.strokeStyle = armCol; c.lineWidth = aw; c.lineCap = 'round'; c.beginPath(); c.moveTo(sx, sy); c.lineTo(ex, ey); c.stroke();
      c.strokeStyle = who === 'baba' || who === 'raysha' ? L.skin : armCol; c.beginPath(); c.moveTo(ex, ey); c.lineTo(hx, hy); c.stroke();
      c.fillStyle = L.skin; c.beginPath(); c.arc(hx, hy, aw * 0.55, 0, 7); c.fill();
    });
    // kepala
    const hr = kid ? 118 : 108;
    if (PHOTOS[who]) photoHead(c, who, 0, neckY + (who === 'ibu' ? 90 : 26), o.expr || 'happy', { tilt: o.tilt || 0 });
    else face(c, who, 0, neckY - hr * 0.82, hr, o.expr || 'happy', { tilt: (o.tilt || 0) + Math.sin(b * Math.PI * 0.5) * 0.04 });
    c.restore();
  }
  return { face, person, PRESET, LOOK, setPhoto, photoHead, star, heartShape };
})();
