// Raysha Sofia & kawan kuning — "Apa jadi kalau Pikachu ada di Malaysia?"
// Nota: watak kuning ialah reka bentuk ASLI (bukan Pikachu berhak cipta).
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, grain, vignette, setHostHead, host, hostPeek } = PAPER;

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM, KID = null, KIDM = null, KIDC = null, FLORAL = null;
const ACC = '#FF6B35', INK = '#2B2024', CREAM = '#FFF4E0', RED = '#E63B2E', PINK = '#FF8FB1', YEL = '#FFD447';
const GY = 1450;                       // aras lantai semua set
const SX = i => 540 + i * 1300;        // pusat set ke-i

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
  if (s <= 0.001 || !KID) return;
  const b = S.B, pose = o.pose || 'stand', skin = '#E9B994';
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s); if (o.rot) c.rotate(o.rot);
  const bob = (pose === 'stand' || pose === 'wave' || pose === 'hug') ? -Math.abs(Math.sin(b * Math.PI)) * 8 : 0;
  c.translate(0, bob);
  const sit = pose === 'sit' || pose === 'ride', hipY = sit ? -70 : -120, neckY = hipY - 160;
  // kaki (seluar corak bunga)
  c.save();
  [-1, 1].forEach(sd => {
    const hx = sd * 30;
    if (pose === 'ride') { const ph = b * Math.PI * 2 + (sd > 0 ? Math.PI : 0); seg(c, hx, hipY, 1.35, 60, 0.15 + Math.sin(ph) * 0.4, 55, 46, floral()); c.fillStyle = skin; c.beginPath(); c.arc(hx + 60 + Math.sin(0.15 + Math.sin(ph) * 0.4) * 55, hipY + 10 + Math.cos(0.15 + Math.sin(ph) * 0.4) * 55, 18, 0, 7); c.fill(); }
    else if (sit) { seg(c, hx, hipY, 1.5, 70, 1.5, 30, 48, floral()); c.fillStyle = skin; c.beginPath(); c.ellipse(hx + 105, hipY + 2, 16, 22, 0, 0, 7); c.fill(); }
    else { seg(c, hx, hipY, 0, 75, 0, 30, 50, floral()); c.fillStyle = skin; c.beginPath(); c.ellipse(hx + sd * 4, -6, 24, 13, 0, 0, 7); c.fill(); }
  });
  c.restore();
  // badan
  fillP(c, floral(), cc => { cc.moveTo(-72, neckY + 18); cc.quadraticCurveTo(-84, neckY + 50, -78, hipY + 16); cc.lineTo(78, hipY + 16); cc.quadraticCurveTo(84, neckY + 50, 72, neckY + 18); cc.closePath(); }, 1);
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
  seg(c, -70, neckY + 30, -Lr[0], 58, -Lr[1], 52, 34, floral(), skin);
  seg(c, 70, neckY + 30, Rr[0], 58, Rr[1], 52, 34, floral(), skin);
  c.restore();
  // kepala (muka sebenar)
  const hs = o.headScale || 0.33, tilt = (o.tilt || 0) + Math.sin(b * Math.PI * 0.5) * 0.05;
  c.save(); c.translate(0, neckY + 30); c.rotate(tilt);
  const k = hs / KIDC.sc; c.drawImage(KIDC, -(KIDM.neckX * KIDC.sc + KIDC.pad) * k, -(KIDM.neckY * KIDC.sc + KIDC.pad) * k, KIDC.width * k, KIDC.height * k);
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

// ================================================================ set
function ground(c, i, wall, floor) { const x0 = SX(i) - 650; c.fillStyle = wall; c.fillRect(x0, -400, 1300, GY + 400); fillP(c, floor, cc => cc.rect(x0, GY, 1300, 1200), 0.8); }
function set0(c) { // Malaysia
  const i = 0, cx = SX(i), b = S.B;
  const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, '#8FCBE6'); g.addColorStop(1, '#FBEBCB'); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400);
  fillP(c, '#FFE9A8', cc => cc.arc(cx + 300, 260, 70, 0, 7), 0.4);
  [[cx - 170, 0], [cx - 60, 1]].forEach(([tx]) => fillP(c, '#9DB2C8', cc => { cc.moveTo(tx - 46, GY); cc.lineTo(tx - 46, 760); cc.lineTo(tx - 30, 710); cc.lineTo(tx - 14, 670); cc.lineTo(tx - 4, 520); cc.lineTo(tx + 4, 520); cc.lineTo(tx + 14, 670); cc.lineTo(tx + 30, 710); cc.lineTo(tx + 46, 760); cc.lineTo(tx + 46, GY); }, 0.5));
  c.fillStyle = '#9DB2C8'; c.fillRect(cx - 170, 1000, 110, 16);
  for (let k = 0; k < 8; k++) { const bx = cx - 640 + k * 165, h = 220 + rnd(k + 4) * 260; fillP(c, '#B8C9DA', cc => cc.rect(bx, GY - h, 150, h), 0.5); }
  // Jalur Gemilang ringkas
  const fx = cx + 240, fy = 820;
  fillP(c, '#8D949F', cc => cc.rect(fx - 6, fy - 20, 12, GY - fy + 20), 0.5);
  c.save(); c.translate(fx + 6, fy); c.transform(1, Math.sin(b * 3) * 0.04, 0, 1, 0, 0);
  for (let k = 0; k < 14; k++) { c.fillStyle = k % 2 ? '#FFFFFF' : '#CC0001'; c.fillRect(0, k * 14, 280, 14); }
  c.fillStyle = '#010066'; c.fillRect(0, 0, 140, 98);
  c.fillStyle = '#FFCC00'; c.beginPath(); c.arc(52, 49, 30, 0, 7); c.fill(); c.fillStyle = '#010066'; c.beginPath(); c.arc(62, 49, 26, 0, 7); c.fill();
  c.fillStyle = '#FFCC00'; c.beginPath(); for (let k = 0; k < 28; k++) { const r = k % 2 ? 9 : 22, a = k / 28 * 6.283 - 1.57; c.lineTo(100 + Math.cos(a) * r, 49 + Math.sin(a) * r); } c.fill();
  c.restore();
  fillP(c, '#86BA72', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  // kawan kuning jatuh dari langit dengan kilat
  const land = E.title2 + 0.6, f = P(E.title2 - 0.3, land);
  if (b > E.title2 - 0.3) {
    if (b < land + 0.4) { c.save(); c.globalAlpha = 1 - P(land, land + 0.4); c.strokeStyle = '#FFE14D'; c.lineWidth = 22; c.lineJoin = 'round'; c.beginPath(); c.moveTo(cx + 40, -300); c.lineTo(cx - 40, 400); c.lineTo(cx + 30, 420); c.lineTo(cx - 20, GY - 200); c.stroke(); c.restore(); }
    buddy(c, cx, lerp(-200, GY, in3(f)), 1.25, { wave: b > land + 0.5 });
  }
}
function set1(c) { // ruang tamu
  const i = 1, cx = SX(i), b = S.B;
  ground(c, i, '#F3E9DC', '#D9C8B4');
  fillP(c, '#E3D5C0', cc => rr(cc, cx - 520, 1050, 1040, 300, 60), 1.1);
  fillP(c, '#D8C9B2', cc => rr(cc, cx - 560, 1250, 1120, 200, 50), 1.1);
  c.save(); c.translate(cx + 300, 1080); c.rotate(0.1); fillP(c, floral(), cc => rr(cc, -110, -90, 220, 180, 30), 0.8); c.restore();
  floatHearts(c, cx + 120, 1000, E.berkawan, 8, 500);
  kid(c, cx - 170, GY + 20, 1.3, { pose: b > E.berkawan ? 'hug' : 'wave' });
  const bx = lerp(cx + 800, cx + 170, out3(P(E.berkawan - 1.5, E.berkawan)));
  buddy(c, bx, GY + 20, 1.05, { wave: b < E.berkawan });
  host(c, cx - 460, GY + 40, 0.55 * life(E.anakAku - 0.3, E.l3 + 0.5, 0.6, 0.4), { pose: 'point' });
}
function set2(c) { // bilik tidur
  const i = 2, cx = SX(i), b = S.B;
  ground(c, i, '#2E3A66', '#4A3F6B');
  fillP(c, '#1E2850', cc => rr(cc, cx + 120, 420, 360, 360, 30), 0.8);
  fillP(c, '#FFF0C8', cc => cc.arc(cx + 300, 560, 70, 0, 7), 0.3); c.fillStyle = '#1E2850'; c.beginPath(); c.arc(cx + 330, 545, 62, 0, 7); c.fill();
  for (let k = 0; k < 7; k++) { c.fillStyle = `rgba(255,240,200,${0.5 + 0.5 * Math.sin(b * 2 + k)})`; c.beginPath(); c.arc(cx + 150 + rnd(k) * 300, 450 + rnd(k + 9) * 300, 5, 0, 7); c.fill(); }
  // katil
  fillP(c, '#C9A27A', cc => rr(cc, cx - 520, 1150, 1040, 300, 30), 1);
  fillP(c, '#FFFFFF', cc => rr(cc, cx - 500, 1090, 260, 110, 50), 0.8);
  c.save(); c.translate(cx + 40, 1150); c.rotate(-Math.PI / 2); kid(c, 0, 0, 1.0, { pose: 'stand', tilt: 0.2 }); c.restore();
  fillP(c, '#7EC8E3', cc => rr(cc, cx - 220, 1110, 690, 220, 40), 1);
  c.fillStyle = 'rgba(255,255,255,0.3)'; for (let k = 0; k < 7; k++) c.fillRect(cx - 200 + k * 92, 1120, 40, 200);
  buddy(c, cx + 20, 1150, 0.75, { sleep: true, rot: -0.15 });
  for (let k = 0; k < 3; k++) { const ph = ((b * 0.4 + k / 3) % 1); c.save(); c.globalAlpha = 1 - ph; c.font = `800 ${60 + k * 20}px 'Baloo 2'`; c.fillStyle = CREAM; c.fillText('Z', cx - 120 + ph * 160 + k * 40, 980 - ph * 360); c.restore(); }
}
function set3(c) { // makan
  const i = 3, cx = SX(i), b = S.B;
  ground(c, i, '#E7F2E1', '#C9A27A');
  for (let k = 0; k < 6; k++) { c.fillStyle = 'rgba(126,191,107,0.25)'; c.fillRect(cx - 650 + k * 220, 300, 110, 700); }
  kid(c, cx - 200, GY + 20, 1.2, { pose: 'eat' });
  fillP(c, '#A86E45', cc => rr(cc, cx - 460, 1140, 920, 46, 12), 1);
  fillP(c, '#8A5A33', cc => { cc.rect(cx - 420, 1186, 30, 264); cc.rect(cx + 390, 1186, 30, 264); }, 0.6);
  buddy(c, cx + 180, 1150, 0.9, {});
  [[cx - 40, '#FFFFFF'], [cx + 330, '#FFFFFF']].forEach(([bx]) => { fillP(c, '#FFFFFF', cc => { cc.moveTo(bx - 70, 1120); cc.quadraticCurveTo(bx, 1190, bx + 70, 1120); cc.closePath(); }, 0.6); c.fillStyle = '#FFF8EC'; c.beginPath(); c.ellipse(bx, 1118, 64, 16, 0, 0, 7); c.fill(); });
  label(c, 'nyam nyam!', cx + 60, 760, { scale: life(E.makan, E.l7 - 0.3, 0.5, 0.3), size: 64, bg: CREAM, rot: -0.05 });
}
function set4(c) { // bermain
  const i = 4, cx = SX(i), b = S.B;
  const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, '#8FCBE6'); g.addColorStop(1, '#FBEBCB'); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400);
  fillP(c, '#86BA72', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  // gelongsor
  c.strokeStyle = '#E2483A'; c.lineWidth = 22; c.beginPath(); c.moveTo(cx + 260, GY); c.lineTo(cx + 260, 900); c.moveTo(cx + 380, GY); c.lineTo(cx + 380, 900); c.stroke();
  fillP(c, '#F2C14E', cc => { cc.moveTo(cx + 250, 900); cc.lineTo(cx + 390, 900); cc.lineTo(cx + 620, GY); cc.lineTo(cx + 540, GY); cc.closePath(); }, 1);
  kid(c, cx - 300, GY + 20, 1.2, { pose: 'cheer' });
  buddy(c, cx + 60, GY + 20, 1.0, { wave: true });
  const p = (b * 0.5) % 1, bx = lerp(cx - 230, cx, Math.abs(p * 2 - 1)), by = GY - 120 - Math.sin(p * Math.PI * 2) ** 2 * 260;
  fillP(c, '#5B8DB8', cc => cc.arc(bx, by, 46, 0, 7), 0.8); c.strokeStyle = '#FFF'; c.lineWidth = 6; c.beginPath(); c.arc(bx, by, 46, 0.6, 2.4); c.stroke();
}
function set5(c) { // sekolah
  const i = 5, cx = SX(i), b = S.B;
  const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, '#A8D8E8'); g.addColorStop(1, '#FBEFD6'); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400);
  fillP(c, '#F6D6A8', cc => cc.rect(cx - 450, 760, 900, GY - 760), 1.1);
  fillP(c, '#E2483A', cc => { cc.moveTo(cx - 500, 780); cc.lineTo(cx, 520); cc.lineTo(cx + 500, 780); cc.closePath(); }, 1);
  label(c, 'TADIKA', cx, 860, { size: 72, bg: '#2F6B45', fg: CREAM, radius: 14 });
  for (let k = 0; k < 3; k++) { fillP(c, '#7EC8E3', cc => rr(cc, cx - 360 + k * 280, 980, 150, 130, 14), 0.5); }
  fillP(c, '#8A5A33', cc => rr(cc, cx - 70, 1180, 140, 270, 20), 0.6);
  fillP(c, '#C9BBA8', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  const walk = out3(P(E.l8, E.sekolah + 1));
  kid(c, lerp(cx - 560, cx - 220, walk), GY + 30, 1.15, { pose: 'wave', bag: true });
  buddy(c, lerp(cx - 330, cx + 30, walk), GY + 30, 0.9, { bag: true });
  label(c, 'nanti...', cx + 300, 620, { scale: life(E.datang, E.sekolah - 0.2, 0.5, 0.3), size: 60, bg: CREAM, rot: 0.05 });
}
function set6(c) { // basikal
  const i = 6, cx = SX(i), b = S.B, scroll = (b * 60) % 400;
  const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, '#8FCBE6'); g.addColorStop(1, '#FBEBCB'); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400);
  for (let k = -1; k < 5; k++) { const tx = cx - 650 + k * 400 - scroll; fillP(c, '#6B4A2F', cc => cc.rect(tx + 180, 1020, 30, 300), 0.5); [[195, 980, 110], [130, 1040, 80], [260, 1040, 85]].forEach(([dx, dy, r]) => fillP(c, '#4F9A5E', cc => cc.arc(tx + dx, dy, r, 0, 7), 0.6)); }
  fillP(c, '#86BA72', cc => cc.rect(cx - 650, 1320, 1300, 130), 0.4);
  c.fillStyle = '#4A4652'; c.fillRect(cx - 650, GY - 130, 1300, 1330);
  c.fillStyle = 'rgba(255,244,224,0.8)'; for (let k = -1; k < 6; k++) c.fillRect(cx - 650 + k * 260 - (b * 120) % 260, GY + 120, 140, 14);
  // basikal roda tiga
  const bx = cx - 40, by = GY + 40, sp = b * 6;
  [[bx - 170, 60], [bx + 150, 80]].forEach(([wx, r]) => { c.strokeStyle = INK; c.lineWidth = 14; c.beginPath(); c.arc(wx, by - r, r, 0, 7); c.stroke(); c.lineWidth = 4; for (let k = 0; k < 4; k++) { const a = sp + k * 0.785; c.beginPath(); c.moveTo(wx, by - r); c.lineTo(wx + Math.cos(a) * r, by - r + Math.sin(a) * r); c.stroke(); } });
  c.strokeStyle = PINK; c.lineWidth = 16; c.lineCap = 'round'; c.beginPath(); c.moveTo(bx - 170, by - 60); c.lineTo(bx - 20, by - 150); c.lineTo(bx + 150, by - 80); c.moveTo(bx + 110, by - 230); c.lineTo(bx + 150, by - 80); c.stroke();
  c.strokeStyle = INK; c.lineWidth = 12; c.beginPath(); c.moveTo(bx + 80, by - 240); c.lineTo(bx + 140, by - 240); c.stroke();
  fillP(c, '#C9A27A', cc => rr(cc, bx + 120, by - 300, 130, 90, 16), 0.8);
  buddy(c, bx + 185, by - 285, 0.62, { wave: true });
  kid(c, bx - 40, by - 140, 1.0, { pose: 'ride' });
  // romantik
  floatHearts(c, cx, 1000, E.romantik - 0.4, 10, 600);
  if (b > E.l10 - 0.3) hostPeek(c, cx + 420, 640, 0.75 * life(E.romantik - 0.4, E.l11 - 0.4, 0.6, 0.4), -0.12);
  label(c, 'romantik?', cx + 240, 470, { scale: life(E.romantik, E.l11 - 0.4, 0.5, 0.3), size: 54, bg: CREAM, rot: 0.05 });
}
function set7(c) { // suka & sayang
  const i = 7, cx = SX(i), b = S.B;
  ground(c, i, '#FFE3EC', '#F7C6D6');
  for (let k = 0; k < 14; k++) heart(c, cx - 600 + rnd(k + 30) * 1200, 200 + rnd(k + 31) * 1000, 0.5 + rnd(k) * 0.6, 'rgba(255,143,177,0.35)');
  const hs = pop(E.suka, 0.6) + 0.35 * pop(E.sayang, 0.6);
  heart(c, cx, 800 + Math.sin(b * 4) * 10, 5.2 * hs * (1 + 0.04 * Math.sin(b * Math.PI * 2)), PINK);
  kid(c, cx - 140, GY + 20, 1.3, { pose: 'hug' });
  buddy(c, cx + 150, GY + 20, 1.05, {});
  label(c, 'SUKA', cx - 260, 560, { scale: pop(E.suka, 0.5), size: 70, bg: RED, fg: CREAM, rot: -0.08 });
  label(c, 'SAYANG', cx + 250, 520, { scale: pop(E.sayang, 0.5), size: 70, bg: RED, fg: CREAM, rot: 0.08 });
}
function set8(c) { // hari jadi
  const i = 8, cx = SX(i), b = S.B;
  ground(c, i, '#FFF0D9', '#E9C79B');
  // belon
  [[cx - 480, 600, PINK], [cx - 380, 520, '#7EC8E3'], [cx + 420, 560, YEL], [cx + 520, 640, '#7EBF6B']].forEach(([x, y, col], k) => { const dy = Math.sin(b * 2 + k) * 14; c.strokeStyle = '#9A8B78'; c.lineWidth = 3; c.beginPath(); c.moveTo(x, y + 90 + dy); c.lineTo(x + 10, y + 380); c.stroke(); fillP(c, col, cc => cc.ellipse(x, y + dy, 70, 90, 0, 0, 7), 0.8); });
  // panji
  c.strokeStyle = '#9A8B78'; c.lineWidth = 4; c.beginPath(); c.moveTo(cx - 600, 330); c.quadraticCurveTo(cx, 430, cx + 600, 330); c.stroke();
  for (let k = 0; k < 11; k++) { const t = k / 10, x = cx - 560 + t * 1120, y = 340 + Math.sin(t * Math.PI) * 82; c.fillStyle = [PINK, YEL, '#7EC8E3', '#7EBF6B'][k % 4]; c.beginPath(); c.moveTo(x - 40, y); c.lineTo(x + 40, y); c.lineTo(x, y + 80); c.fill(); }
  // meja & kek
  fillP(c, '#FFFFFF', cc => rr(cc, cx - 300, 1200, 600, 60, 16), 1);
  fillP(c, '#F7C6D6', cc => rr(cc, cx - 150, 1060, 300, 140, 20), 1);
  fillP(c, '#FFF8EC', cc => rr(cc, cx - 150, 1040, 300, 40, 18), 0.4);
  for (let k = 0; k < 3; k++) { const x = cx - 60 + k * 60; c.fillStyle = ['#7EC8E3', YEL, PINK][k]; c.fillRect(x - 7, 980, 14, 62); const fl = 1 + 0.15 * Math.sin(b * 12 + k); c.fillStyle = '#FFB13B'; c.beginPath(); c.ellipse(x, 965, 9 * fl, 16 * fl, 0, 0, 7); c.fill(); }
  kid(c, cx - 330, GY + 20, 1.15, { pose: 'cheer', hat: true });
  buddy(c, cx + 330, GY + 20, 0.95, { wave: true, hat: true });
  host(c, cx + 560, GY + 40, 0.5 * pop(E.sambut, 0.6), { pose: 'cheer' });
  label(c, 'SELAMAT HARI JADI!', cx, 640, { scale: pop(E.hariJadi, 0.6), size: 74, bg: ACC, fg: CREAM, rot: -0.03 });
  if (b > E.sambut) for (let k = 0; k < 40; k++) { const ph = ((b - E.sambut) * 0.35 + rnd(k)) % 1; c.fillStyle = [PINK, YEL, '#7EC8E3', '#7EBF6B', RED][k % 5]; c.save(); c.translate(cx - 600 + rnd(k + 5) * 1200, 200 + ph * 1300); c.rotate(ph * 10 + k); c.fillRect(-10, -5, 20, 10); c.restore(); }
}

// ================================================================ kamera
function buildCam() {
  const k = [{ x: SX(0), y: 1060, z: 1 }];
  const go = (b0, i, z = 1, y = 1060) => k.push({ b0: b0 - 0.5, b1: b0 + 0.7, x: SX(i), y, z, whip: true });
  go(E.l2, 1); k.push({ b0: E.l3 - 0.3, b1: E.l3 + 0.8, x: SX(1) - 120, y: 1100, z: 1.15 }); k.push({ b0: E.l4 - 0.3, b1: E.l4 + 0.8, x: SX(1), y: 1080, z: 1.05 });
  go(E.l5, 2); go(E.l6, 3); go(E.l7, 4); go(E.l8, 5); go(E.l9, 6); k.push({ b0: E.l10 - 0.3, b1: E.l10 + 0.8, x: SX(6) + 60, y: 1060, z: 1.1 });
  go(E.l11, 7); go(E.l12, 8);
  return k;
}

// ================================================================ overlay
function overlay(c) {
  const b = S.B; c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  if (b < E.l2 + 0.6) {
    const o = 1 - in3(P(E.l2 - 0.4, E.l2 + 0.4)), yo = -P(E.l2 - 0.4, E.l2 + 0.4) * 300;
    c.save(); c.globalAlpha = o;
    bigText(c, 'Apa jadi kalau', 540, 250 + yo, 90, { scale: pop(0, 0.7) });
    bigText(c, 'Pikachu', 540, 360 + yo, 110, { scale: pop(E.title2, 0.6), fill: YEL, stroke: '#7A4A12' });
    const s3 = pop(E.malaysia, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 490 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -380, -64, 760, 128, 24), 1.2); c.restore(); bigText(c, 'ada di Malaysia?', 540, 490 + yo, 88, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
  }
  // nama & umur
  const ns = life(E.raysha, E.l4 + 2, 0.6, 0.4);
  if (ns > 0) { c.save(); c.translate(540, 330); c.rotate(-0.03); c.scale(ns, ns); fillP(c, PINK, cc => rr(cc, -380, -80, 760, 160, 40), 1.3); c.restore(); bigText(c, 'Raysha Sofia', 540, 336, 104, { scale: ns, rot: -0.03, stroke: '#9C2F55' }); }
  label(c, '2 TAHUN', 300, 520, { scale: life(E.umur2, E.l5 - 0.6, 0.6, 0.4), size: 64, bg: YEL, fg: INK, rot: -0.06 });
  label(c, 'minat sangat!', 790, 540, { scale: life(E.minat, E.l5 - 0.6, 0.6, 0.4), size: 54, bg: CREAM, rot: 0.06 });
  // tajuk setiap aktiviti
  [[E.tidur, E.l6, 'TIDUR'], [E.makan, E.l7, 'MAKAN'], [E.main, E.l8, 'MAIN'], [E.sekolah, E.l9, 'SEKOLAH'], [E.basikal, E.l10, 'NAIK BASIKAL']].forEach(([b0, b1, t]) => {
    const s = life(b0, b1 - 0.5, 0.5, 0.3); if (s > 0) { label(c, 'dengan Pikachu', 540, 330, { scale: s, size: 44, bg: YEL, fg: INK }); bigText(c, t, 540, 230, 110, { scale: s }); }
  });
}
function outro(c) {
  const b = S.B; if (b < E.outro - 0.3) return;
  const p = out3(P(E.outro - 0.2, E.outro + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = PINK; c.fillRect(0, 0, W, H); c.globalAlpha = 0.18;
  for (let i = 0; i < 18; i++) heart(c, rnd(i) * W, rnd(i + 30) * H, 0.6 + rnd(i + 3), '#FFFFFF');
  c.globalAlpha = 1; S.ZK = 1;
  host(c, 270, 1080, 0.6 * pop(E.outro + 0.2, 0.8), { pose: 'wave' });
  kid(c, 560, 1080, 1.3 * pop(E.outro + 0.4, 0.8), { pose: 'wave' });
  buddy(c, 830, 1080, 1.0 * pop(E.outro + 0.6, 0.8), { wave: true });
  bigText(c, 'Raysha & kawan', 540, 1240, 100, { scale: pop(E.outro + 0.8, 0.7), stroke: '#9C2F55' });
  label(c, 'follow untuk cerita seterusnya', 540, 1380, { scale: pop(E.outro + 1.4, 0.6), size: 40, bg: CREAM });
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
  const hi = new Image(); hi.src = '/assets/host/head.png'; await hi.decode(); setHostHead(hi, await (await fetch('/assets/host/head.json')).json());
  KID = new Image(); KID.src = '/assets/kid/head.png'; await KID.decode(); KIDM = await (await fetch('/assets/kid/head.json')).json();
  { // pra-skala + bayang dibakar sekali (render jauh lebih laju)
    const sc = 460 / KIDM.w, pad = 30; KIDC = document.createElement('canvas'); KIDC.width = Math.ceil(KIDM.w * sc + pad * 2); KIDC.height = Math.ceil(KIDM.h * sc + pad * 2);
    const kx = KIDC.getContext('2d'); kx.shadowColor = 'rgba(35,18,24,0.32)'; kx.shadowBlur = 16; kx.shadowOffsetY = 8; kx.drawImage(KID, pad, pad, KIDM.w * sc, KIDM.h * sc); KIDC.sc = sc; KIDC.pad = pad; }
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito'); await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  await renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
