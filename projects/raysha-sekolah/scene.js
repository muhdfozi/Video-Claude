// Raysha pergi sekolah — "Video ini adalah video khas untuk Raysha Sofia"
// Nota: watak kuning ialah reka bentuk ASLI (bukan Pikachu berhak cipta). Muka Raysha: sticker dari gambar keluarga.
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, grain, vignette, setHostHead, host, hostPeek, person } = PAPER;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM, FLORAL = null;
const FACES = { smile: null, pout: null };
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
  const F = o.face === 'pout' ? FACES.pout : FACES.smile, hs = (o.face === 'pout' ? 230 : 265) / F.m.w * ((o.headScale || 0.33) / 0.33), tilt = (o.tilt || 0) + Math.sin(b * Math.PI * 0.5) * 0.05;
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

// ================================================================ pakaian
const SCHOOL = o => o.outfit === 'school';
const TOP = o => SCHOOL(o) ? '#3E6FB0' : floral();      // pinafore biru
const ARM = o => SCHOOL(o) ? '#F7F7F2' : floral();      // lengan baju putih
const LEG = o => SCHOOL(o) ? '#E9B994' : floral();      // kaki (stokin dilukis berasingan)

// ================================================================ ikon
function iconX(c, x, y, s) { if (s <= 0.001) return; c.save(); c.translate(x, y); c.scale(s, s); c.strokeStyle = RED; c.lineWidth = 26; c.lineCap = 'round'; c.beginPath(); c.moveTo(-80, -80); c.lineTo(80, 80); c.moveTo(80, -80); c.lineTo(-80, 80); c.stroke(); c.restore(); }
function iconPuting(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#7EC8E3', cc => cc.ellipse(0, 0, 80, 54, 0, 0, 7), 0.8); c.fillStyle = '#F2C14E'; c.beginPath(); c.ellipse(0, -40, 26, 40, 0, 0, 7); c.fill(); c.strokeStyle = '#E86A5C'; c.lineWidth = 14; c.beginPath(); c.arc(0, 50, 34, 0.2, Math.PI - 0.2); c.stroke(); c.restore(); }
function iconPampers(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#FFFFFF', cc => { cc.moveTo(-100, -60); cc.lineTo(100, -60); cc.lineTo(70, 40); cc.quadraticCurveTo(0, 90, -70, 40); cc.closePath(); }, 1); c.fillStyle = '#7EC8E3'; c.fillRect(-100, -60, 200, 24); c.fillStyle = '#FFD447'; c.fillRect(-110, -50, 26, 30); c.fillRect(84, -50, 26, 30); c.restore(); }
function iconBotol(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#FFFFFF', cc => rr(cc, -45, -60, 90, 150, 24), 1); c.fillStyle = '#FFF4C8'; c.fillRect(-40, 0, 80, 85); c.fillStyle = '#FF8FB1'; c.fillRect(-50, -80, 100, 26); c.fillStyle = '#F2C14E'; c.beginPath(); c.ellipse(0, -100, 20, 26, 0, 0, 7); c.fill(); c.restore(); }
function food(c, kind, x, y, s) {
  if (s <= 0.001) return; c.save(); c.translate(x, y); c.scale(s, s);
  if (kind === 'nasi') { fillP(c, '#FFFFFF', cc => cc.ellipse(0, 0, 80, 56, 0, 0, 7), 0.8); c.fillStyle = 'rgba(0,0,0,0.05)'; for (let i = 0; i < 14; i++) { c.beginPath(); c.ellipse((rnd(i) - 0.5) * 110, (rnd(i + 4) - 0.5) * 70, 8, 4, rnd(i) * 3, 0, 7); c.fill(); } }
  if (kind === 'mi') { c.strokeStyle = '#F2C14E'; c.lineWidth = 9; c.lineCap = 'round'; for (let i = 0; i < 6; i++) { c.beginPath(); for (let t = 0; t <= 1; t += 0.1) c.lineTo(-80 + t * 160, -30 + i * 12 + Math.sin(t * 12 + i) * 10); c.stroke(); } }
  if (kind === 'sayur') { fillP(c, '#5DAA3A', cc => { cc.arc(-30, -20, 40, 0, 7); cc.moveTo(70, -20); cc.arc(30, -26, 42, 0, 7); cc.moveTo(40, 10); cc.arc(0, -50, 38, 0, 7); }, 0.6); c.fillStyle = '#8DC86A'; c.fillRect(-14, 0, 28, 60); }
  if (kind === 'ayam') { fillP(c, '#C9813A', cc => cc.ellipse(-10, -10, 70, 50, -0.4, 0, 7), 0.8); c.fillStyle = '#FFF4E0'; c.fillRect(40, 10, 50, 18); c.beginPath(); c.arc(95, 12, 14, 0, 7); c.arc(95, 30, 14, 0, 7); c.fill(); }
  if (kind === 'buah') { fillP(c, '#E2483A', cc => cc.arc(0, 0, 62, 0, 7), 0.8); c.fillStyle = '#5DAA3A'; c.beginPath(); c.ellipse(16, -66, 22, 10, -0.5, 0, 7); c.fill(); c.strokeStyle = '#6B4A2F'; c.lineWidth = 7; c.beginPath(); c.moveTo(0, -58); c.lineTo(4, -80); c.stroke(); c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.ellipse(-22, -18, 14, 22, -0.5, 0, 7); c.fill(); }
  c.restore();
}
function sock(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = '#FFFFFF'; [-30, 30].forEach(sx => { c.beginPath(); rr(c, sx - 22, -40, 44, 40, 10); c.fill(); }); c.fillStyle = '#1F1F24'; [-30, 30].forEach(sx => { c.beginPath(); c.ellipse(sx + 4, -4, 28, 14, 0, 0, 7); c.fill(); }); c.restore(); }
function kidS(c, x, y, s, o = {}) { kid(c, x, y, s, { outfit: 'school', ...o }); if (!o.pose || o.pose === 'stand' || o.pose === 'wave' || o.pose === 'cheer' || o.pose === 'hug') sock(c, x, y - 2, s); }
function sky(c, cx, top, bot) { const g = c.createLinearGradient(0, -400, 0, GY); g.addColorStop(0, top); g.addColorStop(1, bot); c.fillStyle = g; c.fillRect(cx - 650, -400, 1300, GY + 400); }

// ================================================================ set
function set0(c) { // tajuk
  const cx = SX(0), b = S.B;
  c.fillStyle = '#FFE3EC'; c.fillRect(cx - 650, -400, 1300, 3000);
  for (let k = 0; k < 16; k++) heart(c, cx - 600 + rnd(k + 30) * 1200, 100 + rnd(k + 31) * 1300, 0.5 + rnd(k) * 0.7, 'rgba(255,143,177,0.35)');
  fillP(c, '#F7C6D6', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.6);
  kid(c, cx - 140, GY + 20, 1.35, { pose: 'wave' });
  buddy(c, cx + 200, GY + 20, 1.05, { wave: true });
  floatHearts(c, cx, 1100, E.raysha, 10, 600);
}
function set1(c) { // sekolah
  const cx = SX(1), b = S.B;
  sky(c, cx, '#A8D8E8', '#FBEFD6');
  fillP(c, '#F6D6A8', cc => cc.rect(cx - 450, 760, 900, GY - 760), 1.1);
  fillP(c, '#E2483A', cc => { cc.moveTo(cx - 500, 780); cc.lineTo(cx, 520); cc.lineTo(cx + 500, 780); cc.closePath(); }, 1);
  label(c, 'TADIKA', cx, 860, { size: 72, bg: '#2F6B45', fg: CREAM, radius: 14 });
  for (let k = 0; k < 3; k++) fillP(c, '#7EC8E3', cc => rr(cc, cx - 360 + k * 280, 980, 150, 130, 14), 0.5);
  fillP(c, '#8A5A33', cc => rr(cc, cx - 70, 1180, 140, 270, 20), 0.6);
  fillP(c, '#C9BBA8', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  const w = out3(P(E.l2, E.sekolah + 0.5));
  kidS(c, lerp(cx - 600, cx - 200, w), GY + 30, 1.2, { pose: 'wave', bag: true });
  buddy(c, lerp(cx - 380, cx + 120, w), GY + 30, 0.9, { bag: true });
}
function trike(c, bx, by, b) {
  [[bx - 170, 60], [bx + 150, 80]].forEach(([wx, r]) => { c.strokeStyle = INK; c.lineWidth = 14; c.beginPath(); c.arc(wx, by - r, r, 0, 7); c.stroke(); c.lineWidth = 4; for (let k = 0; k < 4; k++) { const a = b * 6 + k * 0.785; c.beginPath(); c.moveTo(wx, by - r); c.lineTo(wx + Math.cos(a) * r, by - r + Math.sin(a) * r); c.stroke(); } });
  c.strokeStyle = PINK; c.lineWidth = 16; c.lineCap = 'round'; c.beginPath(); c.moveTo(bx - 170, by - 60); c.lineTo(bx - 20, by - 150); c.lineTo(bx + 150, by - 80); c.moveTo(bx + 110, by - 230); c.lineTo(bx + 150, by - 80); c.stroke();
  c.strokeStyle = INK; c.lineWidth = 12; c.beginPath(); c.moveTo(bx + 80, by - 240); c.lineTo(bx + 140, by - 240); c.stroke();
}
function road(c, cx, b) {
  sky(c, cx, '#8FCBE6', '#FBEBCB'); const scroll = (b * 60) % 400;
  for (let k = -1; k < 5; k++) { const tx = cx - 650 + k * 400 - scroll; fillP(c, '#6B4A2F', cc => cc.rect(tx + 180, 1020, 30, 300), 0.5); [[195, 980, 110], [130, 1040, 80], [260, 1040, 85]].forEach(([dx, dy, r]) => fillP(c, '#4F9A5E', cc => cc.arc(tx + dx, dy, r, 0, 7), 0.6)); }
  fillP(c, '#86BA72', cc => cc.rect(cx - 650, 1320, 1300, 130), 0.4);
  c.fillStyle = '#4A4652'; c.fillRect(cx - 650, GY - 130, 1300, 1330);
  c.fillStyle = 'rgba(255,244,224,0.8)'; for (let k = -1; k < 6; k++) c.fillRect(cx - 650 + k * 260 - (b * 120) % 260, GY + 120, 140, 14);
}
function set2(c) { // dengan kawan, naik basikal
  const cx = SX(2), b = S.B; road(c, cx, b);
  const bx = cx - 20, by = GY + 40; trike(c, bx, by, b);
  c.save(); c.translate(0, 0); kid(c, bx - 40, by - 140, 1.0, { pose: 'ride', outfit: 'school' }); c.restore();
  const ks = pop(E.kawan, 0.6);
  [[cx - 440, '#E86A5C', { tudung: '#9B6BD3' }], [cx + 420, '#7EBF6B', { cap: '#2E86AB' }]].forEach(([x, sh, ex], i) => { c.save(); c.translate(x, GY + 40); c.scale(ks, ks); person(c, 0, 0, 1.25, { shirt: sh, skin: i ? '#C98B5E' : '#E0AC7E', ...ex, run: 1, phase: b * 6 + i, flip: i === 1 }); c.restore(); });
  label(c, 'KAWAN!', cx - 420, 920, { scale: ks, size: 50, bg: CREAM, rot: -0.06 });
}
function set3(c) { // basikal dengan kawan kuning
  const cx = SX(3), b = S.B; road(c, cx, b);
  const bx = cx - 40, by = GY + 40; trike(c, bx, by, b);
  fillP(c, '#C9A27A', cc => rr(cc, bx + 120, by - 300, 130, 90, 16), 0.8);
  buddy(c, bx + 185, by - 285, 0.62, { wave: true });
  kid(c, bx - 40, by - 140, 1.0, { pose: 'ride', outfit: 'school' });
  floatHearts(c, cx, 1000, E.pikachu, 6, 500);
}
function set4(c) { // peraturan sekolah (muka muncung)
  const cx = SX(4), b = S.B;
  c.fillStyle = '#F3E9DC'; c.fillRect(cx - 650, -400, 1300, 3000);
  fillP(c, '#2F5D46', cc => rr(cc, cx - 470, 260, 940, 560, 24), 1.2);
  c.strokeStyle = '#B8875A'; c.lineWidth = 22; c.strokeRect(cx - 470, 260, 940, 560);
  c.font = "800 56px 'Baloo 2'"; c.fillStyle = 'rgba(255,255,255,0.9)'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('PERATURAN SEKOLAH', cx, 340);
  fillP(c, '#D9C8B4', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  [[E.puting, cx - 300, iconPuting], [E.pampers, cx, iconPampers], [E.susu, cx + 300, iconBotol]].forEach(([bt, x, fn]) => { const s = pop(bt - 0.3, 0.5); if (s > 0) { fillP(c, CREAM, cc => rr(cc, x - 120 * s, 600 - 120 * s, 240 * s, 240 * s, 30 * s), 0.6); fn(c, x, 600, 0.95 * s); iconX(c, x, 600, pop(bt, 0.45) * 0.95); } });
  kidS(c, cx - 30, GY + 30, 1.3, { face: 'pout', pose: 'stand' });
  label(c, 'TAK BOLEH!', cx + 300, 1000, { scale: life(E.puting, E.l8 - 0.5, 0.5, 0.3), size: 58, bg: RED, fg: CREAM, rot: 0.06 });
}
function teacher(c, x, y, s) {   // cikgu berbaju kurung & bertudung
  const b = S.B, sk = '#E0AC7E';
  c.save(); c.translate(x, y - Math.abs(Math.sin(b * Math.PI)) * 4); c.scale(s / 2, s / 2);
  fillP(c, '#5A4A6B', cc => { cc.ellipse(-30, -6, 34, 14, 0, 0, 7); cc.moveTo(64, -6); cc.ellipse(30, -6, 34, 14, 0, 0, 7); }, 0.4);
  fillP(c, '#9B6BD3', cc => { cc.moveTo(-80, -300); cc.lineTo(80, -300); cc.lineTo(120, -12); cc.lineTo(-120, -12); cc.closePath(); }, 1);       // kain
  fillP(c, '#B48BE0', cc => { cc.moveTo(-90, -470); cc.lineTo(90, -470); cc.lineTo(110, -250); cc.lineTo(-110, -250); cc.closePath(); }, 1);    // baju
  c.strokeStyle = sk; c.lineWidth = 26; c.lineCap = 'round';
  c.beginPath(); c.moveTo(-88, -440); c.quadraticCurveTo(-130, -360, -100, -300); c.stroke();
  const wv = Math.sin(b * Math.PI * 2) * 0.25;
  c.beginPath(); c.moveTo(88, -440); c.lineTo(88 + Math.cos(-1.1 + wv) * 120, -440 + Math.sin(-1.1 + wv) * 120); c.stroke();
  c.strokeStyle = '#B48BE0'; c.lineWidth = 46; c.beginPath(); c.moveTo(-86, -450); c.lineTo(-108, -390); c.moveTo(86, -450); c.lineTo(86 + Math.cos(-1.1 + wv) * 60, -450 + Math.sin(-1.1 + wv) * 60); c.stroke();
  fillP(c, '#F2C14E', cc => { cc.moveTo(-95, -460); cc.quadraticCurveTo(-100, -640, 0, -650); cc.quadraticCurveTo(100, -640, 95, -460); cc.quadraticCurveTo(0, -420, -95, -460); }, 1);   // tudung
  fillP(c, sk, cc => cc.ellipse(0, -560, 52, 60, 0, 0, 7), 0.4);
  c.fillStyle = INK; [[-20, -568], [20, -568]].forEach(([ex, ey]) => { c.beginPath(); c.arc(ex, ey, 6.5, 0, 7); c.fill(); });
  c.strokeStyle = INK; c.lineWidth = 5; c.beginPath(); c.arc(0, -545, 16, 0.2 * Math.PI, 0.8 * Math.PI); c.stroke();
  c.fillStyle = 'rgba(255,120,120,0.35)'; [[-34, -540], [34, -540]].forEach(([a, bb]) => { c.beginPath(); c.arc(a, bb, 9, 0, 7); c.fill(); });
  fillP(c, '#E2483A', cc => rr(cc, -150, -370, 70, 90, 8), 0.5);   // buku
  c.restore();
}
function set5(c) { // kelas: dengar cakap teacher
  const cx = SX(5), b = S.B;
  c.fillStyle = '#E7F2E1'; c.fillRect(cx - 650, -400, 1300, 3000);
  fillP(c, '#2F5D46', cc => rr(cc, cx - 500, 300, 640, 420, 20), 1.1);
  c.font = "800 70px 'Baloo 2'"; c.fillStyle = 'rgba(255,255,255,0.85)'; c.textAlign = 'center'; c.fillText('A B C', cx - 180, 470); c.fillText('1 2 3', cx - 180, 590);
  fillP(c, '#C9A27A', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  teacher(c, cx + 320, GY + 30, 2.0);
  label(c, 'TEACHER', cx + 320, 760, { size: 46, bg: '#9B6BD3', fg: CREAM });
  kidS(c, cx - 250, GY + 30, 1.15, { pose: 'stand', tilt: 0.12 });
  fillP(c, '#A86E45', cc => rr(cc, cx - 420, 1300, 340, 34, 10), 0.8); fillP(c, '#8A5A33', cc => { cc.rect(cx - 400, 1334, 22, 120); cc.rect(cx - 122, 1334, 22, 120); }, 0.4);
  const ds = life(b < E.l9 ? E.teacher1 : E.teacher2, b < E.l9 ? E.l9 - 0.4 : E.l13 - 0.4, 0.6, 0.4);
  if (ds > 0) { c.save(); c.translate(cx - 250, 880); c.scale(ds, ds); fillP(c, '#FFFFFF', cc => cc.ellipse(0, 0, 110, 80, 0, 0, 7), 0.6); c.fillStyle = INK; c.font = "800 90px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('!', 0, 6); c.restore(); }
}
function set6(c) { // makan
  const cx = SX(6), b = S.B;
  c.fillStyle = '#FFF0D9'; c.fillRect(cx - 650, -400, 1300, 3000);
  for (let k = 0; k < 6; k++) { c.fillStyle = 'rgba(255,143,177,0.18)'; c.fillRect(cx - 650 + k * 220, 200, 110, 900); }
  fillP(c, '#E9C79B', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  kidS(c, cx - 290, GY + 20, 1.2, { pose: 'eat' });
  fillP(c, '#A86E45', cc => rr(cc, cx - 520, 1180, 1040, 46, 12), 1);
  fillP(c, '#8A5A33', cc => { cc.rect(cx - 480, 1226, 30, 230); cc.rect(cx + 450, 1226, 30, 230); }, 0.6);
  fillP(c, '#FFFFFF', cc => cc.ellipse(cx + 130, 1150, 330, 70, 0, 0, 7), 1);
  [[E.nasi, 'nasi', cx - 60, 1120], [E.mi, 'mi', cx + 80, 1100], [E.sayur, 'sayur', cx + 210, 1090], [E.ayam, 'ayam', cx + 330, 1110], [E.buah, 'buah', cx + 170, 980]].forEach(([bt, k, x, y]) => food(c, k, x, y, pop(bt, 0.5) * 0.75));
  [[E.nasi, 'NASI'], [E.mi, 'MI'], [E.sayur, 'SAYUR'], [E.ayam, 'AYAM'], [E.buah, 'BUAH']].forEach(([bt, t], i) => label(c, t, cx - 450 + i * 225, 700, { scale: pop(bt, 0.5), size: 50, bg: [CREAM, YEL, '#8DC86A', '#F2A541', '#FF8FB1'][i], fg: INK, rot: (i % 2 ? 0.05 : -0.05) }));
  buddy(c, cx + 470, 1180, 0.7, {});
  label(c, 'nyam nyam!', cx - 230, 860, { scale: life(E.makan, E.l10 - 0.3, 0.5, 0.3), size: 58, bg: CREAM, rot: -0.05 });
}
function set7(c) { // main di sekolah dengan kawan kuning & teacher
  const cx = SX(7), b = S.B;
  sky(c, cx, '#8FCBE6', '#FBEBCB');
  fillP(c, '#86BA72', cc => cc.rect(cx - 650, GY, 1300, 1200), 0.8);
  c.strokeStyle = '#E2483A'; c.lineWidth = 22; c.beginPath(); c.moveTo(cx + 280, GY); c.lineTo(cx + 280, 900); c.moveTo(cx + 400, GY); c.lineTo(cx + 400, 900); c.stroke();
  fillP(c, '#F2C14E', cc => { cc.moveTo(cx + 270, 900); cc.lineTo(cx + 410, 900); cc.lineTo(cx + 640, GY); cc.lineTo(cx + 560, GY); cc.closePath(); }, 1);
  teacher(c, cx - 440, GY + 30, 1.7);
  kidS(c, cx - 140, GY + 30, 1.2, { pose: 'cheer' });
  buddy(c, cx + 140, GY + 30, 1.0, { wave: true });
  const p = (b * 0.5) % 1, bx = lerp(cx - 60, cx + 120, Math.abs(p * 2 - 1)), by = GY - 470 - Math.sin(p * Math.PI * 2) ** 2 * 200;
  fillP(c, '#5B8DB8', cc => cc.arc(bx, by, 40, 0, 7), 0.8);
  floatHearts(c, cx, 1000, E.teacher3, 8, 700);
}

// ================================================================ kamera
function buildCam() {
  const k = [{ x: SX(0), y: 1060, z: 1 }];
  const go = (b0, i, z = 1, y = 1060) => k.push({ b0: b0 - 0.5, b1: b0 + 0.7, x: SX(i), y, z, whip: true });
  go(E.l2, 1); go(E.l3, 2); go(E.l4, 3); go(E.l5, 4);
  k.push({ b0: E.l6 - 0.3, b1: E.l6 + 0.8, x: SX(4), y: 1000, z: 1.05 });
  go(E.l8, 5); go(E.l9, 6); go(E.l12, 5); go(E.l13, 7);
  return k;
}

// ================================================================ overlay
function overlay(c) {
  const b = S.B; c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  if (b < E.l2 + 0.6) {
    const o = 1 - in3(P(E.l2 - 0.4, E.l2 + 0.4)), yo = -P(E.l2 - 0.4, E.l2 + 0.4) * 300;
    c.save(); c.globalAlpha = o;
    bigText(c, 'Video khas untuk', 540, 260 + yo, 88, { scale: pop(0, 0.7) });
    const ns = pop(E.raysha, 0.7);
    if (ns > 0) { c.save(); c.translate(540, 400 + yo); c.rotate(-0.03); c.scale(ns, ns); fillP(c, PINK, cc => rr(cc, -380, -80, 760, 160, 40), 1.3); c.restore(); bigText(c, 'Raysha Sofia', 540, 406 + yo, 104, { scale: ns, rot: -0.03, stroke: '#9C2F55' }); }
    c.restore();
  }
  [[E.sekolah, E.l3, 'PERGI SEKOLAH'], [E.basikal, E.l4, 'NAIK BASIKAL'], [E.pikachu, E.l5, 'dengan PIKACHU'], [E.teacher1, E.l9, 'DENGAR CAKAP TEACHER'], [E.makan, E.l10 + 0.3, 'KENA MAKAN'], [E.teacher2, E.l13, 'DENGAR CAKAP TEACHER'], [E.main, E.outro - 0.5, 'MAIN DI SEKOLAH']].forEach(([b0, b1, t]) => {
    const s = life(b0, b1 - 0.5, 0.5, 0.3); if (s > 0) bigText(c, t, 540, 230, t.length > 14 ? 76 : 96, { scale: s });
  });
}
function outro(c) {
  const b = S.B; if (b < E.outro - 0.3) return;
  const p = out3(P(E.outro - 0.2, E.outro + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = '#7EC8E3'; c.fillRect(0, 0, W, H); c.globalAlpha = 0.18;
  for (let i = 0; i < 18; i++) heart(c, rnd(i) * W, rnd(i + 30) * H, 0.6 + rnd(i + 3), '#FFFFFF');
  c.globalAlpha = 1; S.ZK = 1;
  host(c, 270, 1080, 0.6 * pop(E.outro + 0.2, 0.8), { pose: 'wave' });
  kidS(c, 560, 1080, 1.3 * pop(E.outro + 0.4, 0.8), { pose: 'wave', bag: true });
  buddy(c, 830, 1080, 1.0 * pop(E.outro + 0.6, 0.8), { wave: true, bag: true });
  bigText(c, 'Raysha ke sekolah!', 540, 1240, 92, { scale: pop(E.outro + 0.8, 0.7), stroke: '#1F5E8C' });
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
const SETS = [set0, set1, set2, set3, set4, set5, set6, set7];
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
async function loadFace(src, json, target = 460) {
  const im = new Image(); im.src = src; await im.decode(); const m = await (await fetch(json)).json();
  const sc = target / m.w, pad = 30, cv2 = document.createElement('canvas'); cv2.width = Math.ceil(m.w * sc + pad * 2); cv2.height = Math.ceil(m.h * sc + pad * 2);
  const kx = cv2.getContext('2d'); kx.shadowColor = 'rgba(35,18,24,0.32)'; kx.shadowBlur = 16; kx.shadowOffsetY = 8; kx.drawImage(im, pad, pad, m.w * sc, m.h * sc);
  cv2.sc = sc; cv2.pad = pad; return { c: cv2, m };
}
window.ready = (async () => {
  TL = await (await fetch('timeline.json')).json();
  CAPS = await (await fetch('captions.json')).json();
  E = await (await fetch('events.json')).json();
  BEAT = 60 / TL.bpm; CAM = buildCam();
  const hi = new Image(); hi.src = '/assets/host/head.png'; await hi.decode(); setHostHead(hi, await (await fetch('/assets/host/head.json')).json());
  FACES.smile = await loadFace('/assets/kid/head.png', '/assets/kid/head.json');
  FACES.pout = await loadFace('/assets/kid/head_pout.png', '/assets/kid/head_pout.json');
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito'); await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  await renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
