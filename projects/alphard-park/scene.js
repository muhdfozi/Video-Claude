// Sebab Apa? — Park Assist Alphard AGH40. Masa dikunci pada perkataan VO (events.json).
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, grain, vignette, setHostHead, host, hostPeek } = PAPER;

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM;
const ACC = '#FF6B35', INK = '#2B2024', CREAM = '#FFF4E0', RED = '#E63B2E', GREEN = '#2F9E5B';
const M = 150; // piksel per meter (dunia pandangan atas)

// ================================================================ kereta pandangan atas (depan = -y pada rot 0)
function carTop(c, x, y, rot, o = {}) {
  const len = (o.len || 4.995) * M, wid = (o.wid || 1.85) * M, col = o.color || '#F6F3EC';
  c.save(); c.translate(x, y); c.rotate(rot);
  fillP(c, col, cc => rr(cc, -wid / 2, -len / 2, wid, len, wid * 0.28), 1.2);
  if (o.mpv !== false) {
    // cermin sisi
    c.fillStyle = col; [[-1], [1]].forEach(([s]) => { c.beginPath(); rr(c, s * wid / 2 - (s > 0 ? 0 : 22), -len * 0.27, 22, 30, 8); c.fill(); });
    c.fillStyle = '#2C3644';
    c.beginPath(); c.moveTo(-wid * 0.42, -len * 0.30); c.lineTo(wid * 0.42, -len * 0.30); c.lineTo(wid * 0.36, -len * 0.18); c.lineTo(-wid * 0.36, -len * 0.18); c.fill(); // cermin depan
    c.beginPath(); rr(c, -wid * 0.38, len * 0.40, wid * 0.76, len * 0.05, 8); c.fill(); // belakang
    c.fillStyle = mix(col.length === 7 ? col : '#F6F3EC', '#000000', 0.08); c.beginPath(); rr(c, -wid * 0.38, -len * 0.16, wid * 0.76, len * 0.54, 18); c.fill(); // bumbung
    c.fillStyle = '#C9CED6'; c.beginPath(); rr(c, -wid * 0.3, -len / 2 + 6, wid * 0.6, 14, 6); c.fill(); // gril
  } else {
    c.fillStyle = '#2C3644';
    c.beginPath(); c.moveTo(-wid * 0.42, -len * 0.22); c.lineTo(wid * 0.42, -len * 0.22); c.lineTo(wid * 0.36, -len * 0.08); c.lineTo(-wid * 0.36, -len * 0.08); c.fill();
    c.beginPath(); c.moveTo(-wid * 0.38, len * 0.24); c.lineTo(wid * 0.38, len * 0.24); c.lineTo(wid * 0.42, len * 0.34); c.lineTo(-wid * 0.42, len * 0.34); c.fill();
  }
  c.fillStyle = '#FFF6C8'; [-1, 1].forEach(s => { c.beginPath(); rr(c, s * wid * 0.32 - 14, -len / 2 + 2, 28, 10, 4); c.fill(); });
  c.fillStyle = RED; [-1, 1].forEach(s => { c.beginPath(); rr(c, s * wid * 0.34 - 14, len / 2 - 12, 28, 10, 4); c.fill(); });
  c.restore();
}
// kereta pandangan sisi (Alphard)
function mpvSide(c, x, y, s, o = {}) {
  const col = o.color || '#1D1E23', dk = '#0E0F12';
  c.save(); c.translate(x, y); c.scale(s, s);
  c.fillStyle = 'rgba(30,20,30,0.22)'; c.beginPath(); c.ellipse(0, 4, 320, 18, 0, 0, 7); c.fill();
  fillP(c, col, cc => { cc.moveTo(-300, -55); cc.lineTo(-305, -270); cc.quadraticCurveTo(-302, -318, -255, -320); cc.lineTo(140, -322); cc.quadraticCurveTo(170, -320, 185, -295); cc.lineTo(250, -195); cc.quadraticCurveTo(312, -180, 312, -120); cc.lineTo(312, -55); cc.closePath(); }, 1.1);
  c.fillStyle = dk; c.beginPath(); rr(c, -300, -80, 612, 30, 8); c.fill();
  c.fillStyle = '#3A4656'; c.beginPath(); c.moveTo(-282, -200); c.lineTo(-282, -268); c.quadraticCurveTo(-280, -296, -250, -298); c.lineTo(132, -300); c.quadraticCurveTo(155, -298, 166, -280); c.lineTo(222, -200); c.closePath(); c.fill();
  c.fillStyle = 'rgba(255,255,255,0.14)'; c.beginPath(); c.moveTo(60, -298); c.lineTo(110, -298); c.lineTo(40, -202); c.lineTo(-10, -202); c.fill();
  c.fillStyle = col; [-150, -20, 112].forEach(px => c.fillRect(px, -300, 14, 102));
  fillP(c, '#C9CED6', cc => rr(cc, 262, -178, 54, 118, 10), 0.4);
  c.fillStyle = '#8D949F'; for (let k = 0; k < 7; k++) c.fillRect(266, -170 + k * 16, 46, 6);
  c.fillStyle = '#FFF6C8'; c.beginPath(); rr(c, 232, -200, 70, 16, 8); c.fill();
  [-185, 175].forEach(wx => { fillP(c, '#202329', cc => cc.arc(wx, -50, 62, 0, 7), 0.6); c.fillStyle = '#C9CED6'; c.beginPath(); c.arc(wx, -50, 36, 0, 7); c.fill(); c.fillStyle = '#5E646E'; c.beginPath(); c.arc(wx, -50, 10, 0, 7); c.fill(); });
  c.restore();
}

// ================================================================ ikon
function iconSteer(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); c.rotate(Math.sin(S.B * 2) * 0.3); c.strokeStyle = INK; c.lineWidth = 16; c.beginPath(); c.arc(0, 0, 70, 0, 7); c.stroke(); c.lineWidth = 14; c.beginPath(); c.moveTo(-68, 0); c.lineTo(68, 0); c.moveTo(0, 0); c.lineTo(0, 68); c.stroke(); c.fillStyle = INK; c.beginPath(); c.arc(0, 0, 18, 0, 7); c.fill(); c.restore(); }
function iconPedal(c, x, y, s, col) { c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-0.15); fillP(c, col, cc => rr(cc, -38, -70, 76, 140, 16), 0.6); c.strokeStyle = 'rgba(0,0,0,0.25)'; c.lineWidth = 6; for (let k = -2; k <= 2; k++) { c.beginPath(); c.moveTo(-24, k * 22); c.lineTo(24, k * 22); c.stroke(); } c.restore(); }
function iconGear(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#4A4652', cc => rr(cc, -60, 30, 120, 50, 12), 0.6); c.strokeStyle = '#4A4652'; c.lineWidth = 18; c.lineCap = 'round'; const a = Math.sin(S.B * 3) * 0.25; c.beginPath(); c.moveTo(0, 40); c.lineTo(Math.sin(a) * 90, 40 - Math.cos(a) * 90); c.stroke(); fillP(c, INK, cc => cc.arc(Math.sin(a) * 100, 40 - Math.cos(a) * 100, 34, 0, 7), 0.6); c.fillStyle = CREAM; c.font = "800 30px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('D', Math.sin(a) * 100, 42 - Math.cos(a) * 100); c.restore(); }
function iconEye(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#FFFFFF', cc => { cc.moveTo(-100, 0); cc.quadraticCurveTo(0, -80, 100, 0); cc.quadraticCurveTo(0, 80, -100, 0); }, 1); const lk = Math.sin(S.B * 2) * 30; c.fillStyle = '#3E6E9A'; c.beginPath(); c.arc(lk, 0, 34, 0, 7); c.fill(); c.fillStyle = INK; c.beginPath(); c.arc(lk, 0, 16, 0, 7); c.fill(); c.restore(); }
function iconSnail(c, x, y, s) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#C9A27A', cc => { cc.ellipse(-10, 30, 130, 26, 0, 0, 7); cc.moveTo(120, 30); cc.arc(110, 10, 26, 0, 7); }, 0.8); fillP(c, '#E9A25B', cc => cc.arc(-20, -30, 70, 0, 7), 1); c.strokeStyle = '#B5652E'; c.lineWidth = 8; c.beginPath(); for (let a = 0; a < 12; a += 0.2) { const r = 60 - a * 4.5; c.lineTo(-20 + Math.cos(a) * r, -30 + Math.sin(a) * r); } c.stroke(); c.strokeStyle = '#C9A27A'; c.lineWidth = 6; c.beginPath(); c.moveTo(118, -10); c.lineTo(130, -50); c.moveTo(104, -10); c.lineTo(100, -48); c.stroke(); c.fillStyle = INK; [[130, -52], [100, -50]].forEach(([a, b]) => { c.beginPath(); c.arc(a, b, 7, 0, 7); c.fill(); }); c.restore(); }
function apButton(c, x, y, s, pressed) { c.save(); c.translate(x, y); c.scale(s, s); fillP(c, '#3A3F4A', cc => rr(cc, -110, -110, 220, 220, 40), 1.2); fillP(c, pressed ? ACC : '#5A606C', cc => rr(cc, -90, -90 + (pressed ? 8 : 0), 180, 180, 32), pressed ? 0.3 : 0.8); c.fillStyle = CREAM; c.font = "800 120px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('P', -10, 4 + (pressed ? 8 : 0)); c.strokeStyle = CREAM; c.lineWidth = 8; c.beginPath(); c.arc(50, 48 + (pressed ? 8 : 0), 24, 0, 7); c.stroke(); c.restore(); }
function card(c, x, y, w, h, s, col = CREAM, rot = 0) { if (s <= 0.001) return false; c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); fillP(c, col, cc => rr(cc, -w / 2, -h / 2, w, h, 36), 1.4); c.restore(); return true; }
function txt(c, t, x, y, size, col = INK, o = {}) { c.save(); c.translate(x, y); if (o.rot) c.rotate(o.rot); const s = o.scale === undefined ? 1 : o.scale; c.scale(s, s); c.globalAlpha *= o.alpha === undefined ? 1 : o.alpha; c.font = `${o.font || "800"} ${size}px ${o.family || "'Baloo 2'"}`; c.fillStyle = col; c.textAlign = o.align || 'center'; c.textBaseline = 'middle'; c.fillText(t, 0, 0); c.restore(); }
function dimArrow(c, x0, y0, x1, y1, col, w = 6) { c.save(); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = w; c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.stroke(); const a = Math.atan2(y1 - y0, x1 - x0); [[x1, y1, a], [x0, y0, a + Math.PI]].forEach(([x, y, aa]) => { c.beginPath(); c.moveTo(x, y); c.lineTo(x - Math.cos(aa - 0.4) * 24, y - Math.sin(aa - 0.4) * 24); c.lineTo(x - Math.cos(aa + 0.4) * 24, y - Math.sin(aa + 0.4) * 24); c.fill(); }); c.restore(); }

// ================================================================ ZON: TEMPAT LETAK KERETA (pandangan atas)
const BAY_Y0 = 300, BAY_H = 4.8 * M, BAY_W = 2.5 * M, AISLE_Y = 1460;
const bayX = k => 200 + k * BAY_W;               // tepi kiri petak k
const bayCx = k => bayX(k) + BAY_W / 2;
const BAYCY = BAY_Y0 + BAY_H / 2;
const PARKED = { 0: '#5B8DB8', 1: '#C9584A', 3: '#7EBF6B', 4: '#E8C15A', 6: '#9B6BD3', 7: '#E86A5C' };
const PILLAR = { x: bayX(6) + 8, y: BAY_Y0 + BAY_H + 70 };

// keadaan Alphard (x, y, rot) mengikut beat
function bez(p, a, b, c2) { const u = 1 - p; return u * u * a + 2 * u * p * b + p * p * c2; }
function alphardState() {
  const b = S.B;
  const RIGHT = -Math.PI / 2;  // menghadap kiri (bergerak ke -x)
  if (b < E.l8) { // hook: datang & teragak-agak di depan petak 2
    const p = out3(P(0, 4.5)); return { x: lerp(2700, bayCx(2) + 330, p) + Math.sin(b * 6) * 6 * P(4.5, 6) * (1 - P(6, 7)), y: AISLE_Y, r: RIGHT };
  }
  if (b < E.l11) { // demo petak 5
    const tStop = E.berhenti, park0 = E.screen + 1.0, park1 = E.depan + 1.6, out0 = E.keluar, out1 = E.keluar + 3.2;
    const sx = bayCx(5) + 470;
    if (b < tStop) return { x: lerp(3000, sx, out3(P(E.l8, tStop))), y: AISLE_Y, r: RIGHT };
    if (b < park0) return { x: sx, y: AISLE_Y, r: RIGHT };
    if (b < out0) { const p = inOut(P(park0, park1)); return { x: bez(p, sx, bayCx(5), bayCx(5)), y: bez(p, AISLE_Y, AISLE_Y, BAYCY + 15), r: lerp(RIGHT, -Math.PI, inOut(clamp(p * 1.25))) }; }
    const p = inOut(P(out0, out1)); return { x: bez(p, bayCx(5), bayCx(5), bayCx(5) - 600), y: bez(p, BAYCY + 15, AISLE_Y, AISLE_Y), r: lerp(-Math.PI, -Math.PI * 1.5, inOut(clamp(p * 1.3))) };
  }
  if (b < E.l16) return { x: bayCx(2), y: BAY_Y0 + BAY_H - 4.995 * M / 2 + 30, r: 0 };            // dalam petak 2 (ukur)
  if (b < E.l19) return { zone: 'par' };
  if (b < E.l20 + 0.5) { // perlahan + beratur: undur perlahan ke petak 5
    const sx = bayCx(5) + 470, p = inOut(P(E.l19 + 0.5, E.l20 - 0.5));
    return { x: bez(p, sx, bayCx(5), bayCx(5)), y: bez(p, AISLE_Y, AISLE_Y, BAYCY + 15), r: lerp(RIGHT, -Math.PI, inOut(clamp(p * 1.25))) };
  }
  return { x: bayCx(5), y: BAYCY + 15, r: -Math.PI };
}
function zoneLot(c) {
  const b = S.B;
  c.fillStyle = '#5A5763'; c.fillRect(-900, -600, 4900, 2900);
  for (let i = 0; i < 60; i++) { c.fillStyle = 'rgba(255,255,255,0.04)'; c.beginPath(); c.arc(-500 + rnd(i) * 4000, -400 + rnd(i + 9) * 2500, 20 + rnd(i + 3) * 60, 0, 7); c.fill(); }
  // dinding & hiasan atas
  fillP(c, '#B8AFA3', cc => cc.rect(-900, -600, 4900, 860), 0.8);
  for (let k = 0; k < 14; k++) { c.fillStyle = 'rgba(0,0,0,0.06)'; c.fillRect(-850 + k * 360, -600, 14, 860); }
  // petak
  const fade = 1 - 0.85 * P(E.pudar - 0.3, E.pudar + 0.8) * (1 - P(E.l21, E.l21 + 1));
  for (let k = -2; k < 10; k++) {
    c.strokeStyle = `rgba(255,255,255,${k === 2 ? 0.9 * fade : 0.9})`; c.lineWidth = 10;
    c.beginPath(); c.moveTo(bayX(k), BAY_Y0); c.lineTo(bayX(k), BAY_Y0 + BAY_H); c.moveTo(bayX(k), BAY_Y0); c.lineTo(bayX(k + 1), BAY_Y0); c.stroke();
    if (k === 2 && fade < 0.9) { c.strokeStyle = 'rgba(255,255,255,0.9)'; c.lineWidth = 10; c.beginPath(); c.moveTo(bayX(3), BAY_Y0); c.lineTo(bayX(3), BAY_Y0 + BAY_H); c.stroke(); }
  }
  // garisan lorong
  c.fillStyle = 'rgba(255,230,120,0.6)'; for (let x = -800; x < 4000; x += 220) c.fillRect(x, AISLE_Y + 330, 120, 12);
  // kereta lain
  Object.entries(PARKED).forEach(([k, col], i) => carTop(c, bayCx(+k) + (rnd(i) - 0.5) * 18, BAYCY + (rnd(i + 5) - 0.5) * 30, (rnd(i + 2) - 0.5) * 0.04, { len: 4.6, wid: 1.8, color: col, mpv: false }));
  // tiang
  fillP(c, '#9C978F', cc => rr(cc, PILLAR.x - 50, PILLAR.y - 50, 100, 100, 6), 1.2);
  c.fillStyle = '#F2C14E'; for (let k = 0; k < 3; k++) c.fillRect(PILLAR.x - 50, PILLAR.y - 40 + k * 32, 100, 12);
  // Alphard
  const st = alphardState();
  if (!st.zone) {
    // sonar & kamera
    const sv = life(E.kamera - 0.2, E.l6 + 0.5, 0.5, 0.5);
    if (sv > 0) {
      c.save(); c.translate(st.x, st.y); c.rotate(st.r); c.globalAlpha = sv;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sy], i) => { for (let k = 0; k < 3; k++) { const ph = ((b * 0.8 + k / 3 + i * 0.1) % 1); c.strokeStyle = `rgba(120,220,255,${0.8 * (1 - ph)})`; c.lineWidth = 8; c.beginPath(); c.arc(sx * 120, sy * 340, 40 + ph * 200, sy < 0 ? Math.PI + 0.4 : 0.4, sy < 0 ? -0.4 : Math.PI - 0.4); c.stroke(); } });
      const cv2 = pop(E.kamera, 0.5);
      [[0, -375, -Math.PI / 2], [0, 375, Math.PI / 2], [-150, -180, Math.PI], [150, -180, 0]].forEach(([cx, cy, a]) => { c.fillStyle = `rgba(255,214,90,${0.28 * cv2})`; c.beginPath(); c.moveTo(cx, cy); c.arc(cx, cy, 330 * cv2, a - 0.6, a + 0.6); c.fill(); fillP(c, INK, cc => cc.arc(cx, cy, 12, 0, 7), 0.3); });
      c.restore();
    }
    carTop(c, st.x, st.y, st.r, { color: '#F6F3EC' });
    // kawasan sasaran petak (skrin infotainment)
    if (b > E.screen - 0.2 && b < E.depan + 1.6) { const a = 0.5 + 0.3 * Math.sin(b * 6); c.save(); c.strokeStyle = `rgba(80,220,120,${a})`; c.lineWidth = 14; c.setLineDash([30, 18]); c.strokeRect(bayX(5) + 20, BAY_Y0 + 20, BAY_W - 40, BAY_H - 40); c.restore(); }
  }
  // kereta beratur di belakang (ayat 19)
  if (b > E.l19 && b < E.l20 + 1) {
    [0, 1, 2].forEach(i => { const sc = pop(E.l19 + 0.8 + i * 0.6, 0.5); if (sc > 0) carTop(c, bayCx(5) + 1000 + i * 620, AISLE_Y + 40, -Math.PI / 2, { len: 4.6 * sc, wid: 1.8 * sc, color: ['#E86A5C', '#5B8DB8', '#7EBF6B'][i], mpv: false }); });
    const hs = pop(E.hon, 0.45);
    if (hs > 0) label(c, 'HONNN!', bayCx(5) + 1100, AISLE_Y - 260, { scale: hs * (1 + 0.05 * Math.sin(b * 30)), size: 90, bg: RED, fg: CREAM, rot: -0.08 });
    label(c, 'sabar...', bayCx(5), AISLE_Y - 300, { scale: life(E.sabar, E.l20 - 0.4, 0.5, 0.4), size: 70, bg: CREAM, rot: 0.05 });
  }
  // petak pudar & imbasan (ayat 20)
  if (b > E.pudar - 0.5 && b < E.l21 + 0.5) {
    const sx = pop(E.pudar, 0.5);
    if (sx > 0) { c.save(); c.globalAlpha = sx; const ph = (b * 0.7) % 1; c.fillStyle = 'rgba(120,220,255,0.25)'; c.fillRect(bayX(2), BAY_Y0 + ph * BAY_H - 30, BAY_W, 60); c.restore(); }
    const tk = pop(E.takKesan, 0.45);
    if (tk > 0) { c.save(); c.translate(bayCx(2), BAYCY); c.scale(tk, tk); c.strokeStyle = RED; c.lineWidth = 34; c.lineCap = 'round'; c.beginPath(); c.moveTo(-110, -110); c.lineTo(110, 110); c.moveTo(110, -110); c.lineTo(-110, 110); c.stroke(); c.restore(); label(c, 'petak tak dikesan', bayCx(2), BAY_Y0 + BAY_H + 120, { scale: tk, size: 52, bg: RED, fg: CREAM }); }
  }
  // tiang hampir dilanggar (ayat 21)
  const tw = pop(E.terlanggar - 0.2, 0.45) * (1 - P(E.l22 - 0.5, E.l22));
  if (tw > 0) {
    c.save(); c.globalAlpha = 0.5 + 0.5 * Math.sin(b * 12); c.strokeStyle = RED; c.lineWidth = 12; c.beginPath(); c.arc(PILLAR.x, PILLAR.y, 110 * tw, 0, 7); c.stroke(); c.restore();
    label(c, 'TIANG!', PILLAR.x + 90, PILLAR.y - 175, { scale: tw * (1 + 0.04 * Math.sin(b * 20)), size: 80, bg: RED, fg: CREAM, rot: -0.05 });
  }
  // ukuran (ayat 14-15)
  if (b > E.l14 && b < E.l16) {
    const cx = bayCx(2), carTopY = BAY_Y0 + BAY_H - 4.995 * M + 30, carBot = BAY_Y0 + BAY_H + 30;
    const a1 = pop(E.m5, 0.6);
    if (a1 > 0) { c.save(); c.globalAlpha = Math.min(1, a1); dimArrow(c, cx + 260, carTopY, cx + 260, carBot, ACC, 8); c.restore(); label(c, '4,995 mm', cx + 200, carTopY - 75, { scale: a1, size: 52, bg: ACC, fg: CREAM, rot: -0.04 }); }
    const a2 = pop(E.m48, 0.6);
    if (a2 > 0) { c.save(); c.globalAlpha = Math.min(1, a2); dimArrow(c, cx - 260, BAY_Y0, cx - 260, BAY_Y0 + BAY_H, CREAM, 8); c.restore(); label(c, '4,800 mm', cx - 330, BAY_Y0 + 120, { scale: a2, size: 52, bg: CREAM, fg: INK, rot: 0.04 });
      c.save(); c.globalAlpha = 0.5 + 0.4 * Math.sin(b * 8); c.fillStyle = RED; c.fillRect(cx - 140, carTopY - 6, 280, BAY_Y0 - carTopY + 12); c.restore(); }
    const a3 = pop(E.cm32, 0.6);
    if (a3 > 0) { const cw = 1.85 * M; [[bayX(2), cx - cw / 2], [cx + cw / 2, bayX(3)]].forEach(([x0, x1]) => { dimArrow(c, x0 + 4, BAYCY + 120, x1 - 4, BAYCY + 120, '#FFD23F', 6); }); label(c, '32.5 cm', bayX(2) + 70, BAYCY + 200, { scale: a3, size: 40, bg: '#FFD23F', fg: INK }); label(c, '32.5 cm', bayX(3) - 70, BAYCY + 200, { scale: a3, size: 40, bg: '#FFD23F', fg: INK }); }
  }
}

// ================================================================ ZON: PARKING SELARI (y 2600..3600)
const CURB = 3000, PAR_W = 6.0 * M, PAR_D = 2.5 * M;
function zonePar(c) {
  const b = S.B;
  c.fillStyle = '#5A5763'; c.fillRect(-900, 2300, 4900, 1500);
  fillP(c, '#C9BBA8', cc => cc.rect(-900, CURB, 4900, 260), 0.8);
  c.fillStyle = '#7EBF6B'; c.fillRect(-900, CURB + 260, 4900, 600);
  for (let k = 0; k < 4; k++) { const x0 = 120 + k * PAR_W; c.strokeStyle = 'rgba(255,255,255,0.9)'; c.lineWidth = 10; c.beginPath(); c.moveTo(x0, CURB - PAR_D); c.lineTo(x0, CURB); c.moveTo(x0, CURB - PAR_D); c.lineTo(x0 + PAR_W, CURB - PAR_D); c.stroke(); }
  const yc = CURB - PAR_D / 2;
  carTop(c, 120 + PAR_W * 0.5 - 40, yc, Math.PI / 2, { len: 4.6, wid: 1.8, color: '#5B8DB8', mpv: false });
  carTop(c, 120 + PAR_W * 2.5 + 40, yc, Math.PI / 2, { len: 4.6, wid: 1.8, color: '#E8C15A', mpv: false });
  const ax = 120 + PAR_W * 1.5;
  carTop(c, ax, yc, Math.PI / 2, { color: '#F6F3EC' });
  const a = pop(E.m6, 0.6);
  if (a > 0) { dimArrow(c, 120 + PAR_W, CURB - PAR_D - 70, 120 + PAR_W * 2, CURB - PAR_D - 70, CREAM, 8); label(c, '6.0 m', ax, CURB - PAR_D - 150, { scale: a, size: 60, bg: CREAM }); }
  const s2 = pop(E.semeter, 0.6);
  if (s2 > 0) { const L2 = 4.995 * M / 2; [[120 + PAR_W, ax - L2], [ax + L2, 120 + PAR_W * 2]].forEach(([x0, x1]) => dimArrow(c, x0 + 6, yc, x1 - 6, yc, '#FFD23F', 6)); label(c, '~50 cm', 120 + PAR_W + 80, yc + 150, { scale: s2, size: 52, bg: '#FFD23F' }); label(c, '~50 cm', 120 + PAR_W * 2 - 80, yc + 150, { scale: s2, size: 52, bg: '#FFD23F' }); }
}

// ================================================================ rakaman sebenar (jualan)
const FOOT = { a: 102, c: 126, d: 135, b: 132 };
const imgCache = new Map();
function loadImg(url) {
  if (imgCache.has(url)) return imgCache.get(url);
  const p = new Promise(res => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null); im.src = url; });
  imgCache.set(url, p); if (imgCache.size > 40) imgCache.delete(imgCache.keys().next().value);
  return p;
}
function footSched() { const a0 = E.sales - 0.4, c0 = E.apSales - 0.5, d0 = c0 + 126 / 30 / BEAT, b0 = d0 + 135 / 30 / BEAT; return [['a', a0], ['c', c0], ['d', d0], ['b', b0]]; }
async function drawFootage(c) {
  const b = S.B, sch = footSched(); if (b < sch[0][1] - 0.2) return;
  const wipe = out3(P(sch[0][1] - 0.2, sch[0][1] + 0.7));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  const top = lerp(H + 80, -60, wipe);
  c.fillStyle = '#F4DDBE'; c.beginPath(); c.moveTo(0, H); c.lineTo(0, top); for (let x = 0; x <= W; x += 40) c.lineTo(x, top + (rnd(x) - 0.5) * 30); c.lineTo(W, H); c.fill(); c.clip();
  for (let i = 0; i < 14; i++) { c.fillStyle = 'rgba(255,255,255,0.18)'; c.beginPath(); c.arc(rnd(i + 90) * W, rnd(i + 91) * H, 60 + rnd(i) * 120, 0, 7); c.fill(); }
  let cur = sch[0]; sch.forEach(s => { if (b >= s[1]) cur = s; });
  const [k, t0] = cur, ts = (b - t0) * BEAT, n = Math.min(FOOT[k], Math.max(1, Math.floor(ts * 30) + 1));
  const im = await loadImg(`/projects/alphard-park/build/footage/${k}/${String(n).padStart(4, '0')}.jpg`);
  const cardIn = back(P(sch[0][1], sch[0][1] + 0.8)), swap = k === 'a' ? 0 : Math.max(0, 1 - P(t0, t0 + 0.5));
  const rot = ({ a: -0.025, c: 0.02, d: -0.015, b: 0.018 })[k] + swap * 0.15, cw = 820, ch = 1458, kb = 1 + 0.05 * Math.min(1, ts / 4);
  c.save(); c.translate(540, 880); c.rotate(rot); c.scale(cardIn * (1 - swap * 0.08), cardIn * (1 - swap * 0.08));
  fillP(c, '#FFFFFF', cc => rr(cc, -cw / 2 - 22, -ch / 2 - 22, cw + 44, ch + 44, 18), 1.6);
  c.save(); c.beginPath(); rr(c, -cw / 2, -ch / 2, cw, ch, 8); c.clip(); if (im) c.drawImage(im, -cw / 2 * kb, -ch / 2 * kb, cw * kb, ch * kb); c.restore();
  c.restore();
  label(c, 'Alphard Z', 250, 250, { scale: life(E.sales + 1.5, E.rm262 - 0.4, 0.6, 0.3), size: 64, bg: INK, fg: CREAM, rot: -0.06 });
  label(c, 'Advanced Park ✓', 560, 1120, { scale: life(E.apSales, E.rm262 - 0.4, 0.6, 0.3), size: 64, bg: GREEN, fg: CREAM, rot: -0.04 });
  label(c, 'Tahun 2024', 810, 330, { scale: life(E.y2024, E.rm262 - 0.4, 0.6, 0.3), size: 52, bg: CREAM, rot: 0.06 });
  const tg = pop(E.rm262, 0.6) * (1 - P(E.l27 - 0.3, E.l27));
  if (tg > 0) {
    c.save(); c.translate(720, 280); c.rotate(Math.sin(b * 3) * 0.06 + 0.1); c.scale(tg, tg);
    c.strokeStyle = INK; c.lineWidth = 4; c.beginPath(); c.moveTo(-190, -110); c.lineTo(-150, -50); c.stroke();
    fillP(c, '#FFD23F', cc => { cc.moveTo(-170, -60); cc.lineTo(230, -60); cc.lineTo(230, 90); cc.lineTo(-170, 90); cc.lineTo(-230, 15); cc.closePath(); }, 1.3);
    c.fillStyle = INK; c.beginPath(); c.arc(-180, 15, 12, 0, 7); c.fill(); c.font = "800 92px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('RM262k', 30, 22);
    c.restore();
  }
  const kb2 = pop(E.komen, 0.6);
  if (kb2 > 0) { c.save(); c.translate(540, 300); c.scale(kb2, kb2); fillP(c, '#FFFFFF', cc => { rr(cc, -330, -90, 660, 180, 40); cc.moveTo(-220, 85); cc.lineTo(-260, 150); cc.lineTo(-160, 85); }, 1.4); c.font = "800 84px 'Baloo 2'"; c.fillStyle = INK; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('Komen "NAK"', 0, 8); c.restore(); }
  label(c, 'saya DM korang!', 540, 470, { scale: pop(E.dm, 0.6), size: 54, bg: ACC, fg: CREAM, rot: -0.03 });
  c.restore();
}

// ================================================================ kamera
function buildCam() {
  const lot = (x, y, z) => ({ x, y, z });
  return [
    lot(1650, 1150, 0.8),
    { b0: 0, b1: 6, x: 1500, y: 1180, z: 0.9, ease: 'lin' },
    { b0: E.l5 - 0.6, b1: E.l5 + 0.6, x: bayCx(2) + 330, y: AISLE_Y - 150, z: 1.15 },
    { b0: E.l8 - 0.4, b1: E.l8 + 1.0, x: bayCx(5) + 250, y: 1100, z: 0.72 },
    { b0: E.screen + 0.6, b1: E.depan + 1.2, x: bayCx(5) + 100, y: 950, z: 0.85 },
    { b0: E.keluar - 0.5, b1: E.keluar + 2.5, x: bayCx(5) - 200, y: 1150, z: 0.75 },
    { b0: E.l14 - 0.6, b1: E.l14 + 0.6, x: bayCx(2), y: 640, z: 1.05, whip: true },
    { b0: E.cm32 - 0.8, b1: E.cm32 + 0.2, x: bayCx(2), y: 700, z: 1.2 },
    { b0: E.l16 - 0.6, b1: E.l16 + 0.6, x: 120 + PAR_W * 1.5, y: CURB - 260, z: 1.05, whip: true },
    { b0: E.l19 - 0.7, b1: E.l19 + 0.5, x: bayCx(5) + 700, y: 1150, z: 0.58, whip: true },
    { b0: E.l20 - 0.1, b1: E.l20 + 0.9, x: bayCx(2), y: 760, z: 0.95 },
    { b0: E.terlanggar - 1.2, b1: E.terlanggar, x: PILLAR.x - 100, y: 800, z: 0.95 },
    { b0: E.l22 - 0.4, b1: E.l22 + 1.2, x: 1600, y: 900, z: 0.6 },
  ];
}

// ================================================================ overlay (kad kertas)
function dim(c, a) { if (a > 0) { c.fillStyle = `rgba(30,22,34,${0.5 * a})`; c.fillRect(0, 0, W, H); } }
function overlay(c) {
  const b = S.B; c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  // HOOK
  if (b < E.l2 + 0.6) {
    const o = 1 - in3(P(E.l2 - 0.4, E.l2 + 0.4)), yo = -P(E.l2 - 0.4, E.l2 + 0.4) * 300;
    c.save(); c.globalAlpha = o;
    label(c, 'SEBAB APA?', 540, 200 + yo, { scale: pop(0, 0.6), size: 40, bg: ACC, fg: CREAM });
    bigText(c, 'Park Assist Alphard', 540, 330 + yo, 88, { scale: pop(0.2, 0.7) });
    const s3 = pop(E.title2, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 460 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -440, -64, 880, 128, 24), 1.2); c.restore(); bigText(c, 'penting / menyusahkan?', 540, 460 + yo, 80, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
    label(c, '?', bayCx(2) * 0 + 540, 1250, { scale: life(4.2, E.l2 - 0.3, 0.5, 0.3), size: 120, bg: CREAM });
  }
  // kad: butang berhabuk (2), kelebihan/kekurangan (3), Advanced Park (4)
  const d1 = P(E.l2 - 0.3, E.l2 + 0.3) * (1 - P(E.l5 - 0.6, E.l5));
  dim(c, d1);
  if (b > E.l2 - 0.3 && b < E.l3 + 0.5) { const s = life(E.l2, E.l3 - 0.2, 0.6, 0.4); if (card(c, 540, 820, 760, 620, s)) { apButton(c, 540, 780, 1.4 * s, false); c.save(); c.globalAlpha = s * 0.85; c.strokeStyle = '#DDD'; c.lineWidth = 3; for (let k = 0; k < 6; k++) { c.beginPath(); c.moveTo(380, 560); c.lineTo(380 + Math.cos(k * 0.28) * 300, 560 + Math.sin(k * 0.28) * 300); c.stroke(); } for (let r = 60; r < 300; r += 60) { c.beginPath(); c.arc(380, 560, r, 0.05, 1.45); c.stroke(); } c.restore(); txt(c, 'tak pernah sentuh?', 540, 1050, 58, INK, { scale: pop(E.sentuh, 0.5) }); } }
  if (b > E.l3 - 0.3 && b < E.l4 + 0.5) { const o = 1 - P(E.l4 - 0.4, E.l4); [[E.lebihCard, 320, GREEN, '✓', 'KELEBIHAN'], [E.kurangCard, 760, RED, '✗', 'KEKURANGAN']].forEach(([bt, x, col, ic, t]) => { const s = pop(bt, 0.6) * o; if (card(c, x, 860, 400, 460, s, col, x < 540 ? -0.04 : 0.04)) { txt(c, ic, x, 790, 180, CREAM, { scale: s }); txt(c, t, x, 980, 54, CREAM, { scale: s }); } }); }
  if (b > E.l4 - 0.3 && b < E.l5 + 0.3) { const s = life(E.ap - 0.3, E.l5 - 0.3, 0.6, 0.4); if (card(c, 540, 860, 820, 640, s)) { apButton(c, 540, 780, 1.3 * s, b > E.sendiri); txt(c, 'Advanced Park', 540, 1040, 80, INK, { scale: s }); txt(c, 'kereta parking sendiri', 540, 1110, 44, '#7A6A70', { scale: pop(E.sendiri, 0.5), family: 'Nunito', font: '900' }); } }
  // ayat 5: label sensor (atas dunia)
  label(c, 'KAMERA', 300, 380, { scale: life(E.kamera, E.l6 - 0.3, 0.5, 0.3), size: 54, bg: '#FFD23F' });
  label(c, 'SONAR', 780, 380, { scale: life(E.sonar, E.l6 - 0.3, 0.5, 0.3), size: 54, bg: '#78DCFF' });
  // ayat 6-7: kawalan
  const d2 = P(E.l6 - 0.3, E.l6 + 0.3) * (1 - P(E.l8 - 0.5, E.l8));
  dim(c, d2);
  if (b > E.l6 - 0.3 && b < E.l8 + 0.3) {
    const o = 1 - P(E.l7 - 0.3, E.l7 + 0.2);
    [[E.steer, 230, 'STERENG', 0], [E.minyak, 540, 'MINYAK', 1], [E.brake, 850, 'BREK', 2]].forEach(([bt, x, t, i]) => { const s = pop(bt, 0.5) * o; if (card(c, x, 820, 280, 360, s)) { if (i === 0) iconSteer(c, x, 780, s); else iconPedal(c, x, 780, s * 1.1, i === 1 ? '#5B8DB8' : RED); txt(c, t, x, 940, 44, INK, { scale: s }); } });
    label(c, 'kereta yang kawal', 540, 1110, { scale: pop(E.control, 0.5) * o, size: 56, bg: GREEN, fg: CREAM });
    const s7 = life(E.l7 - 0.1, E.l8 - 0.3, 0.6, 0.4);
    if (card(c, 540, 860, 820, 620, s7)) { txt(c, 'Versi PETROL', 540, 640, 64, INK, { scale: s7 }); iconGear(c, 540, 840, 1.3 * s7); label(c, 'gear tukar sendiri', 540, 1080, { scale: pop(E.gear, 0.5) * s7, size: 54, bg: ACC, fg: CREAM }); txt(c, '(bantuan gear: hybrid / PHEV sahaja)', 540, 1150, 32, '#7A6A70', { scale: s7, family: 'Nunito', font: '900' }); }
  }
  // ayat 8-10: label demo
  label(c, 'senang!', 540, 330, { scale: life(E.senang, E.berhenti - 0.4, 0.5, 0.3), size: 70, bg: GREEN, fg: CREAM, rot: -0.05 });
  label(c, 'BERHENTI', 540, 330, { scale: life(E.berhenti, E.tekan - 0.3, 0.5, 0.3), size: 60, bg: CREAM });
  if (b > E.tekan - 0.3 && b < E.screen + 0.3) { const s = life(E.tekan, E.screen - 0.2, 0.5, 0.4); if (card(c, 860, 420, 300, 300, s)) apButton(c, 860, 420, 0.95 * s, b > E.tekan + 0.6); }
  if (b > E.screen - 0.3 && b < E.depan) { const s = life(E.screen - 0.1, E.depan - 0.4, 0.6, 0.4); if (card(c, 540, 360, 680, 400, s, '#1E2430')) { c.save(); c.translate(540, 360); c.scale(s, s); c.fillStyle = '#5A5763'; c.fillRect(-300, -160, 600, 320); c.strokeStyle = '#FFF'; c.lineWidth = 4; for (let k = -2; k <= 2; k++) c.strokeRect(k * 110 - 55, -150, 110, 170); c.strokeStyle = 'rgba(80,220,120,0.95)'; c.lineWidth = 8; c.setLineDash([16, 10]); c.strokeRect(55 + 8, -142, 94, 154); c.setLineDash([]); c.fillStyle = '#F6F3EC'; c.fillRect(170, 60, 90, 44); c.fillStyle = GREEN; c.font = "900 30px Nunito"; c.textAlign = 'center'; c.fillText('MULA', -150, 120); c.restore(); } }
  label(c, 'KE DEPAN', 300, 330, { scale: life(E.depan, E.l11 - 0.6, 0.5, 0.3), size: 52, bg: CREAM });
  label(c, 'MENGUNDUR', 780, 330, { scale: life(E.undur, E.l11 - 0.6, 0.5, 0.3), size: 52, bg: CREAM });
  label(c, 'KELUAR PETAK', 540, 450, { scale: life(E.keluar, E.l11 - 0.6, 0.5, 0.3), size: 56, bg: GREEN, fg: CREAM });
  // ayat 11-13: fakta AGH40
  const d3 = P(E.l11 - 0.4, E.l11 + 0.2) * (1 - P(E.l14 - 0.6, E.l14));
  dim(c, d3);
  if (b > E.l11 - 0.4 && b < E.l14) {
    const s = life(E.l11 - 0.2, E.l13 - 0.4, 0.6, 0.4);
    if (card(c, 540, 860, 900, 820, s)) {
      txt(c, 'Alphard AGH40', 540, 560, 76, INK, { scale: s }); txt(c, 'petrol 2.5 · gred Z', 540, 640, 44, '#7A6A70', { scale: s, family: 'Nunito', font: '900' });
      const r1 = pop(E.pilihan - 0.8, 0.5) * s, r2 = pop(E.pilihan, 0.5) * s;
      if (r1 > 0) { card(c, 540, 820, 780, 140, r1, '#E7F4EA'); txt(c, 'Executive Lounge', 190, 820, 40, INK, { scale: r1, align: 'left' }); txt(c, 'STANDARD ✓', 890, 820, 40, GREEN, { scale: r1, align: 'right' }); }
      if (r2 > 0) { card(c, 540, 990, 780, 140, r2, '#FDEBDD'); txt(c, 'Z (AGH40)', 190, 990, 40, INK, { scale: r2, align: 'left' }); txt(c, 'PILIHAN', 890, 990, 40, ACC, { scale: r2, align: 'right' }); }
      txt(c, '(dipilih masa beli dari kilang)', 540, 1130, 36, '#7A6A70', { scale: pop(E.kilang, 0.5) * s, family: 'Nunito', font: '900' });
    }
    if (b > E.l13 - 0.5) {
      const s2 = life(E.l13 - 0.3, E.l14 - 0.4, 0.6, 0.4);
      if (card(c, 540, 860, 940, 700, s2)) {
        txt(c, 'bukan semua Alphard Z', 540, 600, 60, INK, { scale: pop(E.bukan, 0.5) * s2 });
        [0, 1, 2, 3, 4].forEach(i => { const x = 200 + (i % 3) * 340 + (i >= 3 ? 170 : 0), y = i < 3 ? 830 : 1060, si = pop(E.l13 + 0.2 + i * 0.25, 0.5) * s2; mpvSide(c, x, y, 0.42 * si, { color: '#1D1E23' }); if (b > E.bukan) label(c, i === 1 || i === 4 ? '✓' : '—', x + 90, y - 170, { scale: pop(E.bukan + i * 0.12, 0.4) * s2, size: 50, bg: i === 1 || i === 4 ? GREEN : '#9A8B78', fg: CREAM }); });
      }
    }
  }
  label(c, 'KELEBIHAN', 540, 250, { scale: life(E.l14, E.l16 + 4, 0.6, 0.4), size: 60, bg: GREEN, fg: CREAM });
  label(c, 'parking selari', 540, 380, { scale: life(E.l16 + 0.3, E.tapi - 0.4, 0.6, 0.3), size: 56, bg: CREAM });
  // TAPI ... perlahan
  const d4 = P(E.tapi - 0.3, E.tapi + 0.3) * (1 - P(E.l19 - 0.7, E.l19 - 0.2));
  if (d4 > 0) { c.fillStyle = `rgba(28,32,51,${0.85 * d4})`; c.fillRect(0, 0, W, H); }
  const tp = life(E.tapi, E.l18 - 0.2, 0.5, 0.4);
  if (tp > 0) { bigText(c, 'TAPI...', 540 + Math.sin(b * 40) * 4 * (1 - P(E.tapi, E.tapi + 1.5)), 640, 170, { scale: tp, stroke: '#1C2033' }); label(c, 'KEKURANGAN', 540, 820, { scale: pop(E.kelemahan, 0.5) * tp, size: 64, bg: RED, fg: CREAM }); }
  if (b > E.l18 - 0.3 && b < E.l19) { const s = life(E.l18, E.l19 - 0.5, 0.6, 0.4); const sx = lerp(260, 820, P(E.l18, E.l19)); iconSnail(c, sx, 900, 1.5 * s); label(c, '1. PERLAHAN', 540, 620, { scale: pop(E.perlahan, 0.5) * s, size: 80, bg: CREAM }); }
  label(c, '2. TAK KESAN', 540, 250, { scale: life(E.l20, E.l21 - 0.3, 0.5, 0.3), size: 60, bg: RED, fg: CREAM });
  label(c, '3. TETAP KENA PANTAU', 540, 250, { scale: life(E.l21, E.l22 - 0.4, 0.5, 0.3), size: 56, bg: RED, fg: CREAM });
  if (b > E.sekeliling - 0.3 && b < E.terlanggar) { const s = life(E.sekeliling, E.terlanggar - 0.6, 0.5, 0.4); if (card(c, 300, 470, 380, 260, s)) iconEye(c, 300, 470, 1.2 * s); }
  if (b > E.tekanBrake - 0.3 && b < E.terlanggar) { const s = life(E.tekanBrake, E.terlanggar - 0.6, 0.5, 0.4); if (card(c, 780, 470, 320, 300, s)) { iconPedal(c, 780, 460, 1.2 * s, RED); txt(c, 'BREK', 780, 580, 40, INK, { scale: s }); } }
  // JAWAPAN
  const d5 = P(E.l22 - 0.3, E.l22 + 0.3) * (1 - P(E.sales - 0.6, E.sales));
  dim(c, d5);
  bigText(c, 'Penting ke tidak?', 540, 560, 104, { scale: life(E.l22, E.l23 - 0.2, 0.6, 0.4) });
  if (b > E.l23 - 0.3 && b < E.l24 + 0.3) {
    const o = 1 - P(E.l24 - 0.4, E.l24);
    [[E.sempit, 320, 'parking SEMPIT'], [E.selari2, 760, 'parking SELARI']].forEach(([bt, x, t]) => { const s = pop(bt, 0.5) * o; if (card(c, x, 760, 400, 360, s, '#E7F4EA')) { txt(c, '✓', x, 720, 150, GREEN, { scale: s }); txt(c, t, x, 870, 42, INK, { scale: s }); } });
    label(c, 'SANGAT MEMBANTU', 540, 1060, { scale: pop(E.membantu, 0.5) * o, size: 70, bg: GREEN, fg: CREAM, rot: -0.03 });
  }
  if (b > E.l24 - 0.3 && b < E.l25 + 0.3) {
    const s = life(E.l24, E.l25 - 0.3, 0.6, 0.4);
    host(c, 300, 1350, 0.55 * s, { pose: b > E.confident ? 'cheer' : 'stand' });
    mpvSide(c, 760, 1300, 0.55 * pop(E.mpv, 0.6) * (s > 0 ? 1 : 0), { color: '#F6F3EC' });
    label(c, 'MPV besar?', 760, 980, { scale: pop(E.mpv, 0.5) * s, size: 56, bg: CREAM });
    label(c, 'CONFIDENT!', 540, 560, { scale: pop(E.confident, 0.5) * s, size: 90, bg: ACC, fg: CREAM, rot: -0.04 });
  }
  if (b > E.l25 - 0.3 && b < E.sales) {
    const s = life(E.l25, E.sales - 0.4, 0.6, 0.4);
    host(c, 540, 1380, 0.6 * s, { pose: 'pointUp' });
    label(c, 'dah cekap parking?', 540, 380, { scale: pop(E.cekap, 0.5) * s, size: 64, bg: CREAM });
    const bs = pop(E.bonus, 0.5) * s;
    if (bs > 0) { c.save(); c.translate(540, 610); c.rotate(b * 0.5); c.scale(bs, bs); c.fillStyle = '#FFD23F'; c.beginPath(); for (let i = 0; i < 10; i++) { const r = i % 2 ? 80 : 170, a = i / 10 * 6.283; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); } c.fill(); c.restore(); bigText(c, 'BONUS', 540, 620, 80, { scale: bs, fill: INK, stroke: '#FFD23F' }); }
  }
}
function outro(c) {
  const b = S.B; if (b < E.outro - 0.3) return;
  const p = out3(P(E.outro - 0.2, E.outro + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = ACC; c.fillRect(0, 0, W, H); c.globalAlpha = 0.12; c.fillStyle = CREAM;
  for (let i = 0; i < 18; i++) { c.beginPath(); c.arc(rnd(i) * W, rnd(i + 30) * H, 40 + rnd(i + 3) * 120, 0, 7); c.fill(); }
  c.globalAlpha = 1; S.ZK = 1;
  label(c, 'SEBAB APA?', 540, 200, { scale: pop(E.outro + 0.2, 0.6), size: 40, bg: CREAM, fg: ACC });
  host(c, 540, 1000, 0.74 * pop(E.outro + 0.2, 0.8), { pose: 'wave' });
  bigText(c, 'Komen "NAK"', 540, 1130, 130, { scale: pop(E.outro + 0.5, 0.7), stroke: '#7A2A12' });
  label(c, 'saya DM korang', 540, 1270, { scale: pop(E.outro + 1.0, 0.6), size: 52, bg: CREAM });
  label(c, 'Alphard Z 2024 · Advanced Park · RM262,000', 540, 1390, { scale: pop(E.outro + 1.5, 0.6), size: 36, bg: INK, fg: CREAM });
  c.restore();
}
function drawCaptions(c) {
  const t = S.B * BEAT; if (S.B > E.outro - 0.3) return;
  const cap = CAPS.find(k => t >= k.start && t < k.end); if (!cap || cap.hidden) return;
  const age = (t - cap.start) / BEAT;
  caption(c, cap.segs, 540, 1500, { scale: 0.9 + 0.1 * back(clamp(age / 0.35)), alpha: clamp(age / 0.15) });
}

// ================================================================ render
function world(c, cam) {
  applyCam(c, cam); const v = viewRect(cam);
  c.fillStyle = '#2A2238'; c.fillRect(v.x0 - 10, v.y0 - 10, v.x1 - v.x0 + 20, v.y1 - v.y0 + 20);
  if (sees(v, -900, -600, 4000, 2300)) zoneLot(c);
  if (sees(v, -900, 2300, 4000, 3800)) zonePar(c);
}
async function renderFrame(t) {
  const b = t / BEAT; S.B = b;
  const cam = camAt(CAM, b);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (b < E.sales + 1) {
    if (cam.whip) {
      const N = 16, sh = 0.2; ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < N; i++) { const cs = camAt(CAM, b + (i / (N - 1) - 0.5) * sh); lctx.setTransform(1, 0, 0, 1, 0, 0); world(lctx, cs); ctx.filter = 'blur(6px)'; ctx.globalAlpha = 1 / (i + 1); ctx.drawImage(layer, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none'; }
    } else world(ctx, cam);
    overlay(ctx);
  }
  await drawFootage(ctx);
  drawCaptions(ctx);
  outro(ctx);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  grain(ctx, 0.09); vignette(ctx, 0.3);
  const endB = TL.totalBeats + TL.tailSeconds / BEAT, fo = P(endB - 1.2, endB);
  if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
}
window.ready = (async () => {
  TL = await (await fetch('timeline.json')).json();
  CAPS = await (await fetch('captions.json')).json();
  E = await (await fetch('events.json')).json();
  BEAT = 60 / TL.bpm; CAM = buildCam();
  const hi = new Image(); hi.src = '/assets/host/head.png'; await hi.decode();
  setHostHead(hi, await (await fetch('/assets/host/head.json')).json());
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito'); await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  await renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
