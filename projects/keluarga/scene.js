// Hari Kanak-Kanak Sedunia — Raysha ke Pusat Sains Negara bersama baba & ibu.
// Muka: sticker dari gambar keluarga (assets/family, tidak dicommit) + kesan ekspresi (TOON.photoHead).
// Watak kuning = reka bentuk ASLI (bukan Pikachu). "Didi & Friends" hanya dalam kapsyen, watak tidak dilukis.
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, grain, vignette } = PAPER;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM, FLORAL = null;
const FACES = {}, LEG = () => '#E9B994', TOP = () => '#FFF', ARM = () => '#FFF';
const ACC = '#FF6B35', INK = '#2B2024', CREAM = '#FFF4E0', RED = '#E63B2E', PINK = '#FF8FB1', YEL = '#FFD447';
const GY = 1450;
const SX = i => 540 + i * 1300;

// ================================================================ corak bunga (baju tidur)
function floral() {
  if (FLORAL) return FLORAL;
  const g = document.createElement('canvas'); g.width = g.height = 120; const x = g.getContext('2d');
  x.fillStyle = '#F8E9EB'; x.fillRect(0, 0, 120, 120);
  for (let i = 0; i < 26; i++) {
    const px = rnd(i + 3) * 120, py = rnd(i + 7) * 120, col = ['#D9708A', '#E8A0B4', '#B84D6B', '#8DB37A', '#E7B5C4'][i % 5];
    x.fillStyle = col; for (let k = 0; k < 5; k++) { const a = k / 5 * 6.283; x.beginPath(); x.arc(px + Math.cos(a) * 3.2, py + Math.sin(a) * 3.2, 2.4, 0, 7); x.fill(); }
    x.fillStyle = '#F3D27A'; x.beginPath(); x.arc(px, py, 1.6, 0, 7); x.fill();
  }
  FLORAL = ctx.createPattern(g, 'repeat'); return FLORAL;
}

// ================================================================ watak: RAYSHA (muka sebenar + badan kartun)
function seg(c, x, y, a1, l1, a2, l2, w, col, hand) {
  const ex = x + Math.sin(a1) * l1, ey = y + Math.cos(a1) * l1, hx = ex + Math.sin(a2) * l2, hy = ey + Math.cos(a2) * l2;
  c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round';
  c.beginPath(); c.moveTo(x, y); c.lineTo(ex, ey); c.lineTo(hx, hy); c.stroke();
  if (hand) { c.fillStyle = hand; c.beginPath(); c.arc(hx, hy, w * 0.55, 0, 7); c.fill(); }
}
function kid(c, x, y, s, o = {}) {
  if (s <= 0.001 || !FACES.smile) return;
  const b = S.B, pose = o.pose || 'stand', skin = '#E9B994';
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s); if (o.rot) c.rotate(o.rot);
  const bob = (pose === 'stand' || pose === 'wave' || pose === 'hug') ? -Math.abs(Math.sin(b * Math.PI)) * 8 : 0;
  c.translate(0, bob);
  const sit = pose === 'sit' || pose === 'ride', hipY = sit ? -70 : -120, neckY = hipY - 160;
  // kaki (seluar corak bunga)
  c.save();
  [-1, 1].forEach(sd => {
    const hx = sd * 30;
    if (pose === 'ride') { const ph = b * Math.PI * 2 + (sd > 0 ? Math.PI : 0); seg(c, hx, hipY, 1.35, 60, 0.15 + Math.sin(ph) * 0.4, 55, 46, LEG(o)); c.fillStyle = skin; c.beginPath(); c.arc(hx + 60 + Math.sin(0.15 + Math.sin(ph) * 0.4) * 55, hipY + 10 + Math.cos(0.15 + Math.sin(ph) * 0.4) * 55, 18, 0, 7); c.fill(); }
    else if (sit) { seg(c, hx, hipY, 1.5, 70, 1.5, 30, 48, LEG(o)); c.fillStyle = skin; c.beginPath(); c.ellipse(hx + 105, hipY + 2, 16, 22, 0, 0, 7); c.fill(); }
    else { seg(c, hx, hipY, 0, 75, 0, 30, 50, LEG(o)); c.fillStyle = skin; c.beginPath(); c.ellipse(hx + sd * 4, -6, 24, 13, 0, 0, 7); c.fill(); }
  });
  c.restore();
  // badan
  fillP(c, TOP(o), cc => { cc.moveTo(-72, neckY + 18); cc.quadraticCurveTo(-84, neckY + 50, -78, hipY + 16); cc.lineTo(78, hipY + 16); cc.quadraticCurveTo(84, neckY + 50, 72, neckY + 18); cc.closePath(); }, 1);
  c.strokeStyle = 'rgba(184,77,107,0.35)'; c.lineWidth = 3; c.beginPath(); c.moveTo(0, neckY + 24); c.lineTo(0, hipY + 14); c.stroke();
  fillP(c, '#FBEFF1', cc => { cc.moveTo(-4, neckY + 34); cc.quadraticCurveTo(-40, neckY + 30, -46, neckY + 6); cc.lineTo(-10, neckY + 4); cc.closePath(); cc.moveTo(4, neckY + 34); cc.quadraticCurveTo(40, neckY + 30, 46, neckY + 6); cc.lineTo(10, neckY + 4); cc.closePath(); }, 0.3);
  // lengan (sudut: positif = ke luar)
  const w = Math.sin(b * Math.PI * 2);
  let Lr = [0.25, 0.15], Rr = [0.25, 0.15];
  if (pose === 'wave') Rr = [2.4, 2.7 + 0.4 * w];
  if (pose === 'hug') { Lr = [1.15 + 0.1 * w, 1.55]; Rr = [1.15 - 0.1 * w, 1.55]; }
  if (pose === 'ride') { Lr = [-1.1, -1.4]; Rr = [-1.1, -1.4]; }
  if (pose === 'eat') Rr = [0.45, 2.75 - 0.2 * Math.abs(w)];
  if (pose === 'cheer') { Lr = [2.5 + 0.15 * w, 2.9]; Rr = [2.5 - 0.15 * w, 2.9]; }
  if (pose === 'sit') { Lr = [0.4, 0.9]; Rr = [0.4, 0.9]; }
  c.save();
  seg(c, -70, neckY + 30, -Lr[0], 58, -Lr[1], 52, 34, ARM(o), skin);
  seg(c, 70, neckY + 30, Rr[0], 58, Rr[1], 52, 34, ARM(o), skin);
  c.restore();
  // kepala (muka sebenar)
  const F = o.face === 'pout' ? FACES.pout : FACES.smile, hs = 265 / F.m.w * ((o.headScale || 0.33) / 0.33), tilt = (o.tilt || 0) + Math.sin(b * Math.PI * 0.5) * 0.05;
  c.save(); c.translate(0, neckY + 30); c.rotate(tilt);
  const k = hs / F.c.sc; c.drawImage(F.c, -(F.m.neckX * F.c.sc + F.c.pad) * k, -(F.m.neckY * F.c.sc + F.c.pad) * k, F.c.width * k, F.c.height * k);
  c.restore();
  if (o.hat) partyHat(c, 10, neckY - 175, 0.9, '#7EC8E3');
  if (o.bag) { fillP(c, '#5B8DB8', cc => rr(cc, -110, neckY + 30, 50, 110, 14), 0.8); }
  c.restore();
}

// ================================================================ watak: KAWAN KUNING (reka bentuk asli)
function buddy(c, x, y, s, o = {}) {
  if (s <= 0.001) return;
  const b = S.B, sq = o.sleep ? 0 : Math.abs(Math.sin(b * Math.PI)) * 0.06;
  c.save(); c.translate(x, y); c.scale(s * (1 + sq * 0.5), s * (1 - sq)); if (o.rot) c.rotate(o.rot);
  // kaki
  fillP(c, '#F2B33D', cc => { cc.ellipse(-38, -10, 30, 16, 0, 0, 7); cc.moveTo(68, -10); cc.ellipse(38, -10, 30, 16, 0, 0, 7); }, 0.6);
  // jambul kilat
  fillP(c, '#FF9F1C', cc => { cc.moveTo(-6, -168); cc.lineTo(26, -232); cc.lineTo(8, -222); cc.lineTo(30, -268); cc.lineTo(-18, -206); cc.lineTo(2, -212); cc.closePath(); }, 0.6);
  // badan bulat
  fillP(c, YEL, cc => cc.ellipse(0, -95, 92, 88, 0, 0, 7), 1.1);
  c.fillStyle = '#FFE89A'; c.beginPath(); c.ellipse(0, -62, 52, 42, 0, 0, 7); c.fill();
  c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.ellipse(-40, -140, 22, 12, -0.6, 0, 7); c.fill();
  // tangan kecil
  const wv = o.wave ? Math.sin(b * Math.PI * 2) * 0.5 : 0;
  c.save(); c.fillStyle = YEL; shadow(c, true, 0.4);
  c.save(); c.translate(-88, -92); c.rotate(0.5); c.beginPath(); c.ellipse(0, 0, 14, 26, 0, 0, 7); c.fill(); c.restore();
  c.save(); c.translate(88, -92); c.rotate(-0.5 - (o.wave ? 1.6 + wv : 0)); c.beginPath(); c.ellipse(0, 0, 14, 26, 0, 0, 7); c.fill(); c.restore();
  c.restore();
  // muka
  const blink = o.sleep || ((b + 0.7) % 5 < 0.15);
  c.fillStyle = INK; c.strokeStyle = INK; c.lineWidth = 6; c.lineCap = 'round';
  [-30, 30].forEach(ex => { if (blink) { c.beginPath(); c.arc(ex, -112, 11, 0.2, Math.PI - 0.2); c.stroke(); } else { c.beginPath(); c.ellipse(ex, -112, 10, 14, 0, 0, 7); c.fill(); c.fillStyle = '#FFF'; c.beginPath(); c.arc(ex - 3, -117, 4, 0, 7); c.fill(); c.fillStyle = INK; } });
  c.beginPath(); c.arc(0, -92, 13, 0.15 * Math.PI, 0.85 * Math.PI); c.stroke();
  if (o.hat) partyHat(c, 0, -178, 0.8, '#FF8FB1');
  if (o.bag) fillP(c, PINK, cc => rr(cc, -118, -140, 36, 70, 10), 0.6);
  c.restore();
}
function partyHat(c, x, y, s, col) {
  c.save(); c.translate(x, y); c.scale(s, s);
  fillP(c, col, cc => { cc.moveTo(-40, 0); cc.lineTo(0, -95); cc.lineTo(40, 0); cc.closePath(); }, 0.6);
  c.fillStyle = 'rgba(255,255,255,0.7)'; [[-12, -30], [10, -55], [6, -18]].forEach(([a, bb]) => { c.beginPath(); c.arc(a, bb, 6, 0, 7); c.fill(); });
  c.fillStyle = '#FFD447'; c.beginPath(); c.arc(0, -98, 13, 0, 7); c.fill();
  c.restore();
}
function heart(c, x, y, s, col = PINK) { if (s <= 0.001) return; c.save(); c.translate(x, y); c.scale(s, s); fillP(c, col, cc => { cc.moveTo(0, 30); cc.bezierCurveTo(-60, -10, -40, -60, 0, -30); cc.bezierCurveTo(40, -60, 60, -10, 0, 30); }, 0.6); c.restore(); }
function floatHearts(c, cx, cy, b0, n = 8, spread = 300) {
  for (let i = 0; i < n; i++) { const t0 = b0 + i * 0.35, p = clamp((S.B - t0) / 4); if (p <= 0 || p >= 1) continue; heart(c, cx + (rnd(i) - 0.5) * spread + Math.sin(S.B * 2 + i) * 20, cy - p * 500, 0.6 + rnd(i + 3) * 0.6, i % 3 ? PINK : RED); }
}

// ================================================================ keluarga (muka sebenar + badan kartun)
const P3 = (who, x, s, o) => TOON.person(lctxOr(), who, x, GY + 30, s, o);
let CUR = null; const lctxOr = () => CUR;
const SA = 0.62, SK = 0.95;            // skala dewasa / kanak-kanak
function family(c, cx, o = {}) {
  CUR = c;
  TOON.person(c, 'ibu', cx + (o.ix ?? -300), GY + 30, SA, { pose: o.ip || 'stand', expr: o.ie || 'happy' });
  TOON.person(c, 'baba', cx + (o.bx ?? 300), GY + 30, SA, { pose: o.bp || 'stand', expr: o.be || 'happy' });
  TOON.person(c, 'raysha', cx + (o.rx ?? 0), GY + 30, SK, { pose: o.rp || 'stand', expr: o.re || 'happy' });
}
function sky(c, cx, top, bot) { const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, top); g.addColorStop(1, bot); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400); }
function floor(c, cx, col) { fillP(c, col, cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8); }
function balloons(c, cx, b, list) { list.forEach(([x, y, col], k) => { const dy = Math.sin(b * 2 + k) * 14; c.strokeStyle = '#9A8B78'; c.lineWidth = 3; c.beginPath(); c.moveTo(cx + x, y + 90 + dy); c.lineTo(cx + x + 10, y + 380); c.stroke(); fillP(c, col, cc => cc.ellipse(cx + x, y + dy, 70, 90, 0, 0, 7), 0.8); }); }

// ================================================================ set
function set0(c) { // Hari Kanak-Kanak Sedunia
  const cx = SX(0), b = S.B;
  sky(c, cx, '#FFD9E6', '#FFF1D9'); floor(c, cx, '#F7C6D6');
  // glob (sedunia)
  const gs = pop(E.sedunia, 0.7);
  if (gs > 0) { c.save(); c.translate(cx, 640); c.scale(gs, gs); c.rotate(b * 0.3); fillP(c, '#5B8DB8', cc => cc.arc(0, 0, 150, 0, 7), 1.1); c.fillStyle = '#7EBF6B'; [[-50, -40, 60, 40], [60, 20, 50, 70], [-20, 80, 45, 30], [70, -80, 30, 25]].forEach(([x, y, rx, ry]) => { c.beginPath(); c.ellipse(x, y, rx, ry, 0.4, 0, 7); c.fill(); }); c.restore(); }
  balloons(c, cx, b, [[-500, 520, PINK], [-410, 440, '#7EC8E3'], [430, 480, YEL], [520, 560, '#7EBF6B']]);
  family(c, cx, { ie: 'laugh', be: 'laugh', re: 'happy', rp: 'cheer', bp: 'wave' });
  if (b > E.sedunia) for (let k = 0; k < 40; k++) { const ph = ((b - E.sedunia) * 0.35 + rnd(k)) % 1; c.fillStyle = [PINK, YEL, '#7EC8E3', '#7EBF6B', RED][k % 5]; c.save(); c.translate(cx - 600 + rnd(k + 5) * 1200, 200 + ph * 1300); c.rotate(ph * 10 + k); c.fillRect(-10, -5, 20, 10); c.restore(); }
}
function set1(c) { // Pusat Sains Negara
  const cx = SX(1), b = S.B;
  sky(c, cx, '#8FCBE6', '#FBEBCB'); floor(c, cx, '#C9BBA8');
  fillP(c, '#E8E4DC', cc => { cc.moveTo(cx - 520, GY); cc.lineTo(cx - 520, 900); cc.lineTo(cx - 260, 700); cc.lineTo(cx + 260, 700); cc.lineTo(cx + 520, 900); cc.lineTo(cx + 520, GY); }, 1.1);
  fillP(c, '#7EC8E3', cc => cc.arc(cx, 760, 190, Math.PI, 0), 1);
  c.strokeStyle = 'rgba(255,255,255,0.6)'; c.lineWidth = 5; for (let k = 1; k < 5; k++) { c.beginPath(); c.arc(cx, 760, 190, Math.PI + k * 0.63, Math.PI + k * 0.63 + 0.01); c.lineTo(cx, 760); c.stroke(); }
  for (let k = 0; k < 4; k++) fillP(c, '#5B8DB8', cc => rr(cc, cx - 400 + k * 220, 980, 140, 200, 14), 0.5);
  label(c, 'PUSAT SAINS NEGARA', cx, 880, { scale: pop(E.psn, 0.6), size: 50, bg: '#1F5E8C', fg: CREAM, radius: 14 });
  CUR = c;
  TOON.person(c, 'raysha', cx, GY + 30, SK, { pose: b > E.psn ? 'cheer' : 'wave', expr: b > E.psn ? 'wow' : 'happy' });
  const bs = pop(E.bapa, 0.6), is = pop(E.ibu, 0.6);
  if (bs > 0) TOON.person(c, 'baba', cx + 330, GY + 30, SA * bs, { pose: 'wave', expr: 'cheeky' });
  if (is > 0) TOON.person(c, 'ibu', cx - 330, GY + 30, SA * is, { pose: 'wave', expr: 'laugh' });
}
function set2(c) { // naik kereta
  const cx = SX(2), b = S.B, scroll = (b * 70) % 400;
  sky(c, cx, '#8FCBE6', '#FBEBCB');
  for (let k = -1; k < 5; k++) { const tx = cx - 650 + k * 400 - scroll; fillP(c, '#B8C9DA', cc => cc.rect(tx + 60, 800 + rnd(k + 9) * 150, 220, 600), 0.4); }
  c.fillStyle = '#4A4652'; c.fillRect(cx - 650, GY - 130, 1300, 1330);
  c.fillStyle = 'rgba(255,244,224,0.8)'; for (let k = -1; k < 6; k++) c.fillRect(cx - 650 + k * 260 - (b * 160) % 260, GY + 120, 140, 14);
  // kereta (sisi) + kepala dalam tingkap
  const bx = cx, by = GY + 60 + Math.sin(b * 8) * 3;
  CUR = c;
  [['ibu', -210, 'talk'], ['raysha', 10, 'laugh'], ['baba', 200, 'happy']].forEach(([w, dx, e]) => { c.save(); c.translate(bx + dx, by - 300); c.scale(0.55, 0.55); TOON.photoHead(c, w, 0, 120, e); c.restore(); });
  fillP(c, '#E2483A', cc => { cc.moveTo(bx - 420, by - 60); cc.lineTo(bx - 410, by - 220); cc.quadraticCurveTo(bx - 380, by - 260, bx - 300, by - 262); cc.lineTo(bx + 230, by - 262); cc.quadraticCurveTo(bx + 290, by - 250, bx + 330, by - 180); cc.quadraticCurveTo(bx + 420, by - 160, bx + 420, by - 90); cc.lineTo(bx + 420, by - 60); cc.closePath(); }, 1.1);
  c.fillStyle = 'rgba(30,40,60,0.35)'; c.beginPath(); c.moveTo(bx - 380, by - 160); c.lineTo(bx - 370, by - 240); c.lineTo(bx + 230, by - 240); c.lineTo(bx + 300, by - 160); c.fill();
  [-260, 260].forEach(wx => { fillP(c, '#202329', cc => cc.arc(bx + wx, by - 50, 66, 0, 7), 0.6); c.fillStyle = '#C9CED6'; c.beginPath(); c.arc(bx + wx, by - 50, 34, 0, 7); c.fill(); });
  label(c, 'NAIK KERETA', cx, 700, { scale: pop(E.kereta, 0.5), size: 70, bg: CREAM, rot: -0.04 });
}
function set3(c) { // main semua barang di Pusat Sains
  const cx = SX(3), b = S.B;
  c.fillStyle = '#2E3A66'; c.fillRect(cx - 650, -400, 1300, 3000);
  for (let k = 0; k < 30; k++) { c.fillStyle = `rgba(255,240,200,${0.4 + 0.4 * Math.sin(b * 2 + k)})`; c.beginPath(); c.arc(cx - 600 + rnd(k) * 1200, 100 + rnd(k + 9) * 900, 4, 0, 7); c.fill(); }
  floor(c, cx, '#4A3F6B');
  // planet bergelang
  c.save(); c.translate(cx - 300, 560 + Math.sin(b * 1.5) * 15); fillP(c, '#F2A541', cc => cc.arc(0, 0, 110, 0, 7), 1); c.strokeStyle = '#FFD447'; c.lineWidth = 16; c.beginPath(); c.ellipse(0, 0, 190, 50, -0.3, 0, 7); c.stroke(); c.restore();
  // atom
  c.save(); c.translate(cx + 320, 600); [0, 1.05, 2.1].forEach(a => { c.strokeStyle = '#7EC8E3'; c.lineWidth = 8; c.beginPath(); c.ellipse(0, 0, 150, 55, a + b * 0.3, 0, 7); c.stroke(); }); fillP(c, RED, cc => cc.arc(0, 0, 30, 0, 7), 0.5); [0, 2.1, 4.2].forEach((a, i) => { const t = b * 2 + a; c.fillStyle = YEL; c.beginPath(); c.arc(Math.cos(t) * 150 * Math.cos(i * 1.05) , Math.sin(t) * 55 + Math.cos(t) * 150 * Math.sin(i * 1.05) * 0.3, 14, 0, 7); c.fill(); }); c.restore();
  // gear
  [[cx - 60, 900, 70, 1], [cx + 60, 960, 50, -1.4]].forEach(([x, y, r, sp]) => { c.save(); c.translate(x, y); c.rotate(b * sp); c.fillStyle = '#B8C9DA'; c.beginPath(); for (let k = 0; k < 24; k++) { const rr2 = k % 2 ? r : r * 1.25, a = k / 24 * 6.283; c.lineTo(Math.cos(a) * rr2, Math.sin(a) * rr2); } c.fill(); c.fillStyle = '#2E3A66'; c.beginPath(); c.arc(0, 0, r * 0.35, 0, 7); c.fill(); c.restore(); });
  family(c, cx, { re: b > E.mainSemua ? 'love' : 'wow', rp: 'cheer', ie: 'happy', be: 'wow' });
}
function set4(c) { // playground, persembahan, mainan
  const cx = SX(4), b = S.B;
  c.fillStyle = '#F3E9DC'; c.fillRect(cx - 650, -400, 1300, 3000); floor(c, cx, '#C9A27A');
  // pentas persembahan (tiada watak berhak cipta)
  const st = pop(E.didi, 0.6);
  fillP(c, '#B5304A', cc => rr(cc, cx - 520, 300, 1040, 560, 20), 1);
  c.fillStyle = '#8E2238'; for (let k = 0; k < 10; k++) c.fillRect(cx - 520 + k * 104, 300, 50, 560);
  if (st > 0) { c.save(); c.globalAlpha = st; const g = c.createRadialGradient(cx, 760, 20, cx, 760, 380); g.addColorStop(0, 'rgba(255,240,180,0.9)'); g.addColorStop(1, 'rgba(255,240,180,0)'); c.fillStyle = g; c.fillRect(cx - 520, 300, 1040, 560); c.restore(); for (let k = 0; k < 5; k++) { const p = ((b * 0.6 + k / 5) % 1); c.save(); c.globalAlpha = (1 - p) * st; c.font = "800 70px 'Baloo 2'"; c.fillStyle = YEL; c.fillText('♪', cx - 300 + k * 150, 760 - p * 300); c.restore(); } }
  label(c, 'PERSEMBAHAN', cx, 470, { scale: st, size: 50, bg: YEL, fg: INK });
  // gelongsor (playground)
  const ps = pop(E.playground, 0.6);
  c.save(); c.globalAlpha = Math.min(1, ps); c.strokeStyle = '#2E86AB'; c.lineWidth = 20; c.beginPath(); c.moveTo(cx - 560, GY); c.lineTo(cx - 560, 1050); c.moveTo(cx - 460, GY); c.lineTo(cx - 460, 1050); c.stroke();
  fillP(c, '#F2C14E', cc => { cc.moveTo(cx - 470, 1050); cc.lineTo(cx - 360, 1050); cc.lineTo(cx - 220, GY); cc.lineTo(cx - 290, GY); cc.closePath(); }, 1); c.restore();
  // mainan
  const ts = pop(E.toys, 0.6);
  [[cx + 330, '#E2483A'], [cx + 410, '#5B8DB8'], [cx + 370, '#7EBF6B']].forEach(([x, col], k) => { const y = GY - 50 - (k === 2 ? 90 : 0); fillP(c, col, cc => rr(cc, x - 40 * ts, y - 40 * ts, 80 * ts, 80 * ts, 10), 0.6); });
  CUR = c;
  TOON.person(c, 'raysha', cx - 80, GY + 30, SK, { pose: 'cheer', expr: b > E.didi && b < E.toys ? 'love' : 'laugh' });
  TOON.person(c, 'baba', cx + 180, GY + 30, SA * 0.9, { pose: 'point', expr: 'happy' });
}
function set5(c) { // lari-lari & lompat-lompat
  const cx = SX(5), b = S.B;
  sky(c, cx, '#A8D8E8', '#FBEFD6'); floor(c, cx, '#86BA72');
  const jumping = b > E.lompat - 0.3;
  // trampolin
  fillP(c, '#2B2024', cc => cc.ellipse(cx + 120, GY - 10, 260, 46, 0, 0, 7), 0.8);
  c.strokeStyle = '#5B8DB8'; c.lineWidth = 16; c.beginPath(); c.ellipse(cx + 120, GY - 14, 260, 46, 0, 0, 7); c.stroke();
  CUR = c;
  const rx = jumping ? cx + 120 : lerp(cx - 380, cx + 120, inOut(clamp((b - E.l7) / (E.lompat - 0.4 - E.l7))));
  TOON.person(c, 'raysha', rx, GY + (jumping ? -10 : 30), SK, { pose: jumping ? 'jump' : 'run', expr: 'laugh' });
  TOON.person(c, 'ibu', cx + 460, GY + 30, SA * 0.9, { pose: 'cheer', expr: 'laugh' });
  label(c, 'LARI-LARI!', cx - 250, 700, { scale: life(E.lari, E.lompat - 0.4, 0.5, 0.3), size: 66, bg: CREAM, rot: -0.05 });
  label(c, 'LOMPAT-LOMPAT!', cx + 100, 640, { scale: life(E.lompat, E.l8 - 0.4, 0.5, 0.3), size: 62, bg: YEL, fg: INK, rot: 0.05 });
}
function set6(c) { // kedai: beli barang dapur
  const cx = SX(6), b = S.B;
  c.fillStyle = '#EEF5EA'; c.fillRect(cx - 650, -400, 1300, 3000); floor(c, cx, '#D9D0C0');
  for (let r = 0; r < 4; r++) { fillP(c, '#C9A27A', cc => cc.rect(cx - 600, 420 + r * 170, 1200, 18), 0.5); for (let k = 0; k < 12; k++) { const col = ['#E2483A', '#F2C14E', '#5B8DB8', '#7EBF6B', '#E86A5C', '#9B6BD3'][(k + r * 2) % 6]; fillP(c, col, cc => rr(cc, cx - 580 + k * 98, 320 + r * 170, 70, 100, 10), 0.3); } }
  // troli
  const tx = cx + 150 + Math.sin(b) * 10;
  c.strokeStyle = '#8D949F'; c.lineWidth = 12; c.lineJoin = 'round'; c.beginPath(); c.moveTo(tx - 200, 1110); c.lineTo(tx - 170, 1300); c.lineTo(tx + 170, 1300); c.lineTo(tx + 200, 1110); c.closePath(); c.stroke();
  c.beginPath(); c.moveTo(tx + 200, 1110); c.lineTo(tx + 260, 1060); c.stroke();
  [tx - 140, tx + 140].forEach(x => { c.fillStyle = INK; c.beginPath(); c.arc(x, 1340, 22, 0, 7); c.fill(); });
  const items = [[E.dapur, '#F2C14E'], [E.shopping, '#7EBF6B'], [E.makanan, '#E2483A'], [E.pilih, '#5B8DB8']];
  items.forEach(([bt, col], k) => { const s2 = pop(bt, 0.5); if (s2 > 0) fillP(c, col, cc => rr(cc, tx - 150 + k * 75, 1200 - 90 * s2 - (k % 2) * 30, 64, 90 * s2, 10), 0.4); });
  CUR = c;
  TOON.person(c, 'raysha', cx - 120, GY + 30, SK, { pose: b > E.happy ? 'cheer' : 'stand', expr: b > E.makanan ? 'love' : (b > E.happy ? 'laugh' : 'happy') });
  TOON.person(c, 'ibu', cx - 400, GY + 30, SA * 0.9, { pose: 'point', expr: 'talk' });
  TOON.person(c, 'baba', cx + 410, GY + 30, SA * 0.9, { pose: 'hold', expr: 'happy' });
  label(c, 'BARANG DAPUR', cx, 240, { scale: life(E.dapur, E.l10, 0.5, 0.3), size: 58, bg: CREAM });
  label(c, 'SHOPPING!', cx, 240, { scale: life(E.shopping, E.l10, 0.5, 0.3) * (b > E.shopping ? 1 : 0), size: 66, bg: ACC, fg: CREAM });
  label(c, 'RAYSHA HAPPY!', cx, 240, { scale: life(E.happy, E.l11, 0.5, 0.3), size: 62, bg: YEL, fg: INK });
}
function set7(c) { // terjumpa "Pikachu" (kawan kuning asli)
  const cx = SX(7), b = S.B;
  c.fillStyle = '#FFF0D9'; c.fillRect(cx - 650, -400, 1300, 3000); floor(c, cx, '#E9C79B');
  const ps = pop(E.pika - 0.2, 0.7);
  if (ps > 0) { c.save(); c.globalAlpha = 0.5 * ps; const g = c.createRadialGradient(cx + 220, 1150, 20, cx + 220, 1150, 500); g.addColorStop(0, 'rgba(255,230,120,0.9)'); g.addColorStop(1, 'rgba(255,230,120,0)'); c.fillStyle = g; c.fillRect(cx - 650, 400, 1300, 1200); c.restore(); }
  buddy(c, cx + 220, GY + 30, 1.25 * ps, { wave: true });
  CUR = c;
  TOON.person(c, 'raysha', cx - 220, GY + 30, SK, { pose: b > E.pika ? 'cheer' : 'stand', expr: b > E.pika + 0.8 ? 'love' : 'wow' });
}
function set8(c) { // balik ke rumah
  const cx = SX(8), b = S.B;
  sky(c, cx, '#3B2C5C', '#F29E8E'); floor(c, cx, '#86BA72');
  fillP(c, '#F6D6A8', cc => cc.rect(cx - 420, 740, 840, GY - 740), 1.1);
  fillP(c, '#A8432F', cc => { cc.moveTo(cx - 480, 760); cc.lineTo(cx, 460); cc.lineTo(cx + 480, 760); cc.closePath(); }, 1);
  [cx - 280, cx + 180].forEach(x => { fillP(c, '#FFD58A', cc => rr(cc, x, 860, 110, 110, 10), 0.4); });
  fillP(c, '#8A5A33', cc => rr(cc, cx - 60, 1140, 120, 310, 16), 0.6);
  // beg mainan (tanpa jenama)
  const gb = pop(E.didi2, 0.6);
  if (gb > 0) { fillP(c, '#FF8FB1', cc => rr(cc, cx + 300 - 60 * gb, GY - 150 * gb, 120 * gb, 150 * gb, 12), 0.8); c.strokeStyle = '#B5304A'; c.lineWidth = 6; c.beginPath(); c.arc(cx + 300, GY - 150 * gb, 30 * gb, Math.PI, 0); c.stroke(); }
  family(c, cx, { ix: -420, bx: 470, rx: -170, re: b > E.rumah - 0.3 ? 'sleepy' : 'happy', ie: 'happy', be: b > E.rumah ? 'sleepy' : 'happy' });
  buddy(c, cx + 90, GY + 30, 0.8 * pop(E.pika2, 0.6), {});
}

// ================================================================ kamera
function buildCam() {
  const k = [{ x: SX(0), y: 1060, z: 1 }];
  const go = (b0, i, z = 1, y = 1060) => k.push({ b0: b0 - 0.5, b1: b0 + 0.7, x: SX(i), y, z, whip: true });
  go(E.l2, 1); go(E.l4, 2); go(E.l5, 3); go(E.l6, 4); go(E.l7, 5); go(E.l8, 6); go(E.l11, 7); go(E.l12, 8);
  k.push({ b0: E.pilih - 1, b1: E.pilih, x: SX(6) - 80, y: 1100, z: 1.1 });
  k.sort((a, b2) => (a.b0 ?? -1) - (b2.b0 ?? -1));
  return k;
}

// ================================================================ overlay
function overlay(c) {
  const b = S.B; c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  if (b < E.l2 + 0.6) {
    const o = 1 - in3(P(E.l2 - 0.4, E.l2 + 0.4)), yo = -P(E.l2 - 0.4, E.l2 + 0.4) * 300;
    c.save(); c.globalAlpha = o;
    bigText(c, 'Hari', 540, 200 + yo, 90, { scale: pop(0, 0.7) });
    bigText(c, 'Kanak-Kanak', 540, 300 + yo, 110, { scale: pop(0.6, 0.7), fill: YEL, stroke: '#7A4A12' });
    const s3 = pop(E.sedunia, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 420 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -260, -64, 520, 128, 24), 1.2); c.restore(); bigText(c, 'SEDUNIA!', 540, 420 + yo, 96, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
  }
  [[E.bapa, E.l4, 'dengan BAPA & IBU'], [E.mainSemua, E.l6, 'MAIN SEMUA!'], [E.playground, E.l7, 'PLAYGROUND'], [E.pika, E.l12, 'JUMPA PIKACHU!'], [E.rumah - 0.6, E.outro - 0.4, 'BALIK RUMAH']].forEach(([b0, b1, t]) => {
    const s = life(b0, b1 - 0.5, 0.5, 0.3); if (s > 0) bigText(c, t, 540, 230, t.length > 14 ? 76 : 96, { scale: s });
  });
}
function outro(c) {
  const b = S.B; if (b < E.outro - 0.3) return;
  const p = out3(P(E.outro - 0.2, E.outro + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = '#FF8FB1'; c.fillRect(0, 0, W, H); c.globalAlpha = 0.18;
  for (let i = 0; i < 18; i++) heart(c, rnd(i) * W, rnd(i + 30) * H, 0.6 + rnd(i + 3), '#FFFFFF');
  c.globalAlpha = 1; S.ZK = 1; CUR = c;
  TOON.person(c, 'ibu', 250, 1100, SA * pop(E.outro + 0.2, 0.8), { pose: 'wave', expr: 'laugh' });
  TOON.person(c, 'raysha', 540, 1100, SK * pop(E.outro + 0.4, 0.8), { pose: 'cheer', expr: 'love' });
  TOON.person(c, 'baba', 830, 1100, SA * pop(E.outro + 0.6, 0.8), { pose: 'wave', expr: 'laugh' });
  bigText(c, 'Selamat Hari', 540, 1250, 90, { scale: pop(E.outro + 0.8, 0.7), stroke: '#9C2F55' });
  bigText(c, 'Kanak-Kanak!', 540, 1355, 96, { scale: pop(E.outro + 1.0, 0.7), fill: YEL, stroke: '#9C2F55' });
  c.restore();
}
function drawCaptions(c) {
  const t = S.B * BEAT; if (S.B > E.outro - 0.3) return;
  const cap = CAPS.find(k => t >= k.start && t < k.end); if (!cap || cap.hidden) return;
  const age = (t - cap.start) / BEAT;
  caption(c, cap.segs, 540, 1560, { scale: 0.9 + 0.1 * back(clamp(age / 0.35)), alpha: clamp(age / 0.15) });
}

// ================================================================ render
const SETS = [set0, set1, set2, set3, set4, set5, set6, set7, set8];
function world(c, cam) {
  applyCam(c, cam); const v = viewRect(cam);
  c.fillStyle = '#2A2238'; c.fillRect(v.x0 - 10, v.y0 - 10, v.x1 - v.x0 + 20, v.y1 - v.y0 + 20);
  SETS.forEach((fn, i) => { if (sees(v, SX(i) - 650, -400, SX(i) + 650, 2700)) fn(c); });
}
async function renderFrame(t) {
  const b = t / BEAT; S.B = b;
  const cam = camAt(CAM, b);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (cam.whip) {
    const N = 16, sh = 0.2; ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < N; i++) { const cs = camAt(CAM, b + (i / (N - 1) - 0.5) * sh); lctx.setTransform(1, 0, 0, 1, 0, 0); world(lctx, cs); ctx.filter = 'blur(6px)'; ctx.globalAlpha = 1 / (i + 1); ctx.drawImage(layer, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none'; }
  } else world(ctx, cam);
  overlay(ctx); drawCaptions(ctx); outro(ctx);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  grain(ctx, 0.08); vignette(ctx, 0.26);
  const endB = TL.totalBeats + TL.tailSeconds / BEAT, fo = P(endB - 1.2, endB);
  if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
}
window.ready = (async () => {
  TL = await (await fetch('timeline.json')).json();
  CAPS = await (await fetch('captions.json')).json();
  E = await (await fetch('events.json')).json();
  BEAT = 60 / TL.bpm; CAM = buildCam();
  await loadFamily();
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito'); await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  await renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
