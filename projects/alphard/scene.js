// Sebab Apa? — Alphard. Semua masa dikunci pada perkataan VO (events.json).
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, toScreen, grain, vignette, setHostHead, host, hostPeek } = PAPER;

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM;
const ACC = '#FF6B35', INK = '#2B2024', CREAM = '#FFF4E0';
const fmt = v => Math.round(v).toLocaleString('en-US');

// ================================================================ data (JPJ, dikira daripada data.gov.my)
const YEARS = [[2017, 2267], [2018, 4312], [2019, 4490], [2020, 5269], [2021, 6286], [2022, 13308], [2023, 14322], [2024, 15395], [2025, 17598]];
const RANK = [[11, 'Honda HR-V', 18059], [12, 'Perodua Aruz', 17827], [13, 'Toyota Alphard', 17598], [14, 'Proton S70', 17166], [15, 'Toyota Corolla Cross', 16192], [16, 'Proton Persona', 15046], [17, 'Honda Civic', 12310]];

// ================================================================ kereta MPV (pandangan sisi, menghadap kanan)
function mpv(c, x, y, s, o = {}) {
  const col = o.color || '#F6F3EC', dk = o.dark || mix(col.length === 7 ? col : '#F6F3EC', '#000000', 0.25);
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
  if (o.bounce) c.translate(0, o.bounce);
  // bayang bawah
  c.fillStyle = 'rgba(30,20,30,0.22)'; c.beginPath(); c.ellipse(0, 4, 320, 18, 0, 0, 7); c.fill();
  // badan
  fillP(c, col, cc => {
    cc.moveTo(-300, -55); cc.lineTo(-305, -270); cc.quadraticCurveTo(-302, -318, -255, -320);
    cc.lineTo(140, -322); cc.quadraticCurveTo(170, -320, 185, -295); cc.lineTo(250, -195);
    cc.quadraticCurveTo(312, -180, 312, -120); cc.lineTo(312, -55); cc.closePath();
  }, 1.1);
  // skirt bawah
  c.fillStyle = dk; c.beginPath(); rr(c, -300, -80, 612, 30, 8); c.fill();
  // tingkap
  c.fillStyle = '#26303D';
  c.beginPath(); c.moveTo(-282, -200); c.lineTo(-282, -268); c.quadraticCurveTo(-280, -296, -250, -298); c.lineTo(132, -300); c.quadraticCurveTo(155, -298, 166, -280); c.lineTo(222, -200); c.closePath(); c.fill();
  c.fillStyle = 'rgba(255,255,255,0.16)'; c.beginPath(); c.moveTo(60, -298); c.lineTo(110, -298); c.lineTo(40, -202); c.lineTo(-10, -202); c.fill();
  c.fillStyle = col; [-150, -20, 112].forEach(px => c.fillRect(px, -300, 14, 102));
  // garis pintu gelangsar & pemegang
  c.strokeStyle = dk; c.lineWidth = 3; c.beginPath(); c.moveTo(-20, -195); c.lineTo(-20, -82); c.moveTo(112, -195); c.lineTo(112, -82); c.moveTo(-150, -195); c.lineTo(-150, -82); c.stroke();
  c.fillStyle = dk; c.fillRect(-60, -170, 30, 7); c.fillRect(80, -170, 26, 7);
  // gril besar krom
  fillP(c, '#C9CED6', cc => rr(cc, 262, -178, 54, 118, 10), 0.4);
  c.fillStyle = '#8D949F'; for (let k = 0; k < 7; k++) c.fillRect(266, -170 + k * 16, 46, 6);
  // lampu
  c.fillStyle = '#FFF6C8'; c.beginPath(); rr(c, 232, -200, 70, 16, 8); c.fill();
  c.fillStyle = '#E2483A'; c.fillRect(-306, -250, 10, 60);
  // roda
  const spin = o.spin || 0;
  [-185, 175].forEach(wx => {
    fillP(c, '#202329', cc => cc.arc(wx, -50, 62, 0, 7), 0.6);
    c.fillStyle = '#C9CED6'; c.beginPath(); c.arc(wx, -50, 36, 0, 7); c.fill();
    c.strokeStyle = '#8D949F'; c.lineWidth = 6;
    for (let k = 0; k < 5; k++) { const a = spin + k * 1.2566; c.beginPath(); c.moveTo(wx, -50); c.lineTo(wx + Math.cos(a) * 32, -50 + Math.sin(a) * 32); c.stroke(); }
    c.fillStyle = '#5E646E'; c.beginPath(); c.arc(wx, -50, 9, 0, 7); c.fill();
  });
  c.restore();
}
function miniCar(c, x, y, s, col, a = 1) {  // ikon ringkas untuk grid
  if (s <= 0.001) return;
  c.save(); c.translate(x, y); c.scale(s, s); c.globalAlpha *= a;
  c.fillStyle = col; c.beginPath();
  c.moveTo(-40, -8); c.lineTo(-40, -36); c.quadraticCurveTo(-40, -44, -32, -44); c.lineTo(18, -44); c.lineTo(32, -26); c.quadraticCurveTo(42, -24, 42, -14); c.lineTo(42, -8); c.closePath(); c.fill();
  c.strokeStyle = 'rgba(0,0,0,0.25)'; c.lineWidth = 2; c.stroke();
  c.fillStyle = '#26303D'; c.beginPath(); c.moveTo(-36, -27); c.lineTo(-36, -38); c.lineTo(16, -39); c.lineTo(27, -27); c.fill();
  c.fillStyle = '#1E2126'; [-24, 24].forEach(wx => { c.beginPath(); c.arc(wx, -8, 9, 0, 7); c.fill(); });
  c.restore();
}

// ================================================================ alam: pokok kelapa, langit
function palm(c, x, gy, h, sway) {
  c.strokeStyle = '#8A6542'; c.lineWidth = 26; c.lineCap = 'round';
  c.beginPath(); c.moveTo(x, gy); c.quadraticCurveTo(x + 40, gy - h * 0.5, x + 20 + sway, gy - h); c.stroke();
  const tx = x + 20 + sway, ty = gy - h;
  for (let k = 0; k < 7; k++) {
    const a = -Math.PI / 2 + (k - 3) * 0.5 + Math.sin(S.B * 1.5 + k) * 0.04;
    fillP(c, k % 2 ? '#3F8F4E' : '#4FA45C', cc => { cc.moveTo(tx, ty); cc.quadraticCurveTo(tx + Math.cos(a - 0.3) * 150, ty + Math.sin(a - 0.3) * 150, tx + Math.cos(a) * 230, ty + Math.sin(a) * 230 + 70); cc.quadraticCurveTo(tx + Math.cos(a + 0.2) * 130, ty + Math.sin(a + 0.2) * 130, tx, ty); }, 0.6);
  }
  c.fillStyle = '#6B4A2B'; [[-14, 10], [12, 14], [0, 26]].forEach(([dx, dy]) => { c.beginPath(); c.arc(tx + dx, ty + dy, 15, 0, 7); c.fill(); });
}
function sky(c, x0, x1, y0, y1, top, bot) {
  const g = c.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, top); g.addColorStop(1, bot);
  c.fillStyle = g; c.fillRect(x0, y0, x1 - x0, y1 - y0);
}
function clouds(c, x0, x1, y, seed) {
  for (let i = 0; i < 6; i++) {
    const cx = x0 + rnd(i + seed) * (x1 - x0) + ((S.B * 6) % 200), cy = y + rnd(i + seed + 7) * 300, s = 0.6 + rnd(i + seed + 3) * 0.7;
    [[0, 0, 60], [55, 10, 48], [-55, 12, 44], [20, -30, 46]].forEach(([dx, dy, r]) => fillP(c, '#FFFFFF', cc => cc.arc(cx + dx * s, cy + dy * s, r * s, 0, 7), 0.4));
  }
}

// ================================================================ ZON 1: JALAN RAYA + PAPAN IKLAN
const BOARD = { x: 540, y: 905, w: 820, h: 470 };
function carX() { return lerp(-520, 540, out3(P(E.carIn, E.carIn + 2.6))); }
function zoneRoad(c) {
  const b = S.B;
  sky(c, -900, 2000, -200, 1420, '#8FCBE6', '#F7E6C4');
  const sg = c.createRadialGradient(880, 300, 20, 880, 300, 240); sg.addColorStop(0, 'rgba(255,240,190,0.95)'); sg.addColorStop(1, 'rgba(255,240,190,0)');
  c.fillStyle = sg; c.beginPath(); c.arc(880, 300, 240, 0, 7); c.fill();
  fillP(c, '#FFE9A8', cc => cc.arc(880, 300, 70, 0, 7), 0.4);
  clouds(c, -500, 1500, 120, 1);
  // bandar jauh
  for (let i = -4; i < 14; i++) {
    const bx = -700 + i * 170 + rnd(i) * 30, h = 260 + rnd(i + 11) * 300;
    fillP(c, '#B8C9DA', cc => cc.rect(bx, 1360 - h, 150, h), 0.4);
  }
  // menara berkembar (generik)
  [[250, 0], [372, 1]].forEach(([tx]) => {
    fillP(c, '#9DB2C8', cc => { cc.moveTo(tx - 46, 1360); cc.lineTo(tx - 46, 650); cc.lineTo(tx - 30, 600); cc.lineTo(tx - 16, 560); cc.lineTo(tx - 4, 420); cc.lineTo(tx + 4, 420); cc.lineTo(tx + 16, 560); cc.lineTo(tx + 30, 600); cc.lineTo(tx + 46, 650); cc.lineTo(tx + 46, 1360); }, 0.5);
  });
  c.fillStyle = '#9DB2C8'; c.fillRect(250, 900, 122, 18);
  for (let i = -3; i < 12; i++) {
    const bx = -650 + i * 210 + rnd(i + 40) * 40, h = 180 + rnd(i + 51) * 200;
    fillP(c, '#8FA5BC', cc => cc.rect(bx, 1370 - h, 180, h), 0.6);
    c.fillStyle = 'rgba(255,255,255,0.3)'; for (let wy = 1390 - h; wy < 1350; wy += 46) for (let wx = bx + 20; wx < bx + 160; wx += 40) c.fillRect(wx, wy, 18, 24);
  }
  // pokok kelapa
  palm(c, 40, 1390, 520, Math.sin(b * 1.3) * 6);
  palm(c, 1040, 1390, 600, Math.sin(b * 1.3 + 1) * 6);
  // papan iklan
  fillP(c, '#4A4652', cc => { cc.rect(BOARD.x - 260, BOARD.y + 200, 34, 1400 - BOARD.y - 200); cc.rect(BOARD.x + 226, BOARD.y + 200, 34, 1400 - BOARD.y - 200); }, 0.8);
  fillP(c, INK, cc => rr(cc, BOARD.x - BOARD.w / 2 - 16, BOARD.y - BOARD.h / 2 - 16, BOARD.w + 32, BOARD.h + 32, 22), 1.2);
  c.fillStyle = CREAM; c.beginPath(); rr(c, BOARD.x - BOARD.w / 2, BOARD.y - BOARD.h / 2, BOARD.w, BOARD.h, 14); c.fill();
  c.save(); c.beginPath(); rr(c, BOARD.x - BOARD.w / 2, BOARD.y - BOARD.h / 2, BOARD.w, BOARD.h, 14); c.clip();
  boardContent(c);
  c.restore();
  if (b > E.toBoard && b < E.q) hostPeek(c, BOARD.x + BOARD.w / 2 - 120, BOARD.y - BOARD.h / 2 - 4, 0.5 * pop(E.toBoard + 0.6, 0.7), 0.08);
  // jalan
  fillP(c, '#C9BBA8', cc => cc.rect(-900, 1385, 2900, 50), 0.8);
  c.fillStyle = '#4A4652'; c.fillRect(-900, 1435, 2900, 1100);
  c.fillStyle = 'rgba(255,244,224,0.75)';
  for (let x = -880; x < 2000; x += 180) c.fillRect(x - ((b * 0) % 180), 1720, 100, 14);
  // hos di kaki lima
  host(c, 935, 1425, 0.4 * life(1.0, E.toBoard - 0.4, 0.7, 0.4), { pose: 'wave' });
  // kereta
  const cx = carX(), mv = P(E.carIn, E.carIn + 2.6) < 1 ? 1 : 0;
  mpv(c, cx, 1640, 0.95, { spin: cx / 60, bounce: mv ? Math.sin(b * 20) * 2 : 0 });
  if (mv) { c.save(); c.globalAlpha = 0.5 * (1 - P(E.carIn + 1.8, E.carIn + 2.6)); c.strokeStyle = CREAM; c.lineWidth = 8; c.lineCap = 'round'; [0, 1, 2].forEach(k => { c.beginPath(); c.moveTo(cx - 330 - k * 30, 1440 + k * 50); c.lineTo(cx - 470 - k * 50, 1440 + k * 50); c.stroke(); }); c.restore(); }
}
function boardContent(c) {
  const b = S.B, x = BOARD.x, y = BOARD.y;
  c.textAlign = 'center'; c.textBaseline = 'middle';
  if (b < E.toBoard + 0.4) {
    // teaser: angka belum didedahkan
    const wob = Math.sin(b * 6) * 0.03;
    c.save(); c.translate(x, y + 40); c.rotate(wob);
    c.font = "800 210px 'Baloo 2'"; c.fillStyle = '#C9BBA8'; c.fillText('??,???', 0, 0); c.restore();
    c.font = "900 42px Nunito"; c.fillStyle = INK; c.fillText('Alphard setahun', x, y + 170);
    return;
  }
  if (b < E.clock) {
    // kaunter pendaftaran
    const p = inOut(P(E.countStart, E.countEnd)), v = 17598 * p;
    label(c, 'JPJ · 2025', x, y - 165, { scale: pop(E.jpj, 0.6), size: 40, bg: '#1F5E8C', fg: CREAM });
    const s = 1 + 0.12 * Math.max(0, 1 - P(E.countEnd, E.countEnd + 1)) * (b > E.countEnd ? 1 : 0);
    c.save(); c.translate(x, y + 5); c.scale(s, s);
    c.font = "800 190px 'Baloo 2'"; c.fillStyle = b >= E.countEnd ? ACC : INK; c.fillText(fmt(v), 0, 0);
    c.restore();
    c.font = "900 44px Nunito"; c.fillStyle = INK; c.globalAlpha = P(E.countEnd, E.countEnd + 0.5);
    c.fillText('Alphard didaftar', x, y + 145); c.globalAlpha = 1;
    return;
  }
  if (b < E.toChart + 0.6) {
    // jam: 48 sehari, 2 sejam
    const cx = x - 210, cy = y + 10, R = 165, sc = pop(E.clock, 0.6);
    c.save(); c.translate(cx, cy); c.scale(sc, sc);
    fillP(c, '#FFFFFF', cc => cc.arc(0, 0, R, 0, 7), 1); c.strokeStyle = INK; c.lineWidth = 12; c.beginPath(); c.arc(0, 0, R, 0, 7); c.stroke();
    for (let k = 0; k < 12; k++) { const a = k / 12 * 6.283; c.lineWidth = k % 3 ? 5 : 9; c.beginPath(); c.moveTo(Math.cos(a) * R * 0.78, Math.sin(a) * R * 0.78); c.lineTo(Math.cos(a) * R * 0.9, Math.sin(a) * R * 0.9); c.stroke(); }
    const spin = Math.max(0, b - E.clock) * 1.6;
    c.lineCap = 'round'; c.lineWidth = 10; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(spin / 12 - 1.57) * R * 0.45, Math.sin(spin / 12 - 1.57) * R * 0.45); c.stroke();
    c.strokeStyle = ACC; c.lineWidth = 7; c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(spin - 1.57) * R * 0.72, Math.sin(spin - 1.57) * R * 0.72); c.stroke();
    c.fillStyle = INK; c.beginPath(); c.arc(0, 0, 12, 0, 7); c.fill();
    c.restore();
    const s1 = pop(E.d48, 0.6);
    if (s1 > 0) { c.save(); c.translate(x + 175, y - 85); c.scale(s1, s1); c.font = "800 120px 'Baloo 2'"; c.fillStyle = ACC; c.fillText('48', -55, 0); c.font = "900 40px Nunito"; c.fillStyle = INK; c.textAlign = 'left'; c.fillText('/ hari', 15, 12); c.restore(); }
    const s2 = pop(E.perHour, 0.6);
    if (s2 > 0) {
      c.save(); c.translate(x + 175, y + 85); c.scale(s2, s2); c.font = "800 120px 'Baloo 2'"; c.fillStyle = INK; c.fillText('2', -95, 0); c.font = "900 40px Nunito"; c.textAlign = 'left'; c.fillText('/ jam', -40, 12); c.restore();
      miniCar(c, x + 120, y + 190, pop(E.perHour, 0.5) * 1.1, '#F6F3EC'); miniCar(c, x + 240, y + 190, pop(E.perHour + 0.5, 0.5) * 1.1, '#2A2A30');
    }
    return;
  }
  // jawapan (ayat 11)
  label(c, 'Setahun (2025)', x, y - 160, { scale: pop(E.ans - 0.2, 0.6), size: 40, bg: '#1F5E8C', fg: CREAM });
  const sa = pop(E.ans, 0.7);
  c.save(); c.translate(x, y - 10); c.scale(sa, sa); c.font = "800 190px 'Baloo 2'"; c.fillStyle = ACC; c.fillText('17,598', 0, 0); c.restore();
  const sy = pop(E.ytd, 0.6);
  if (sy > 0) { c.save(); c.translate(x, y + 150); c.scale(sy, sy); c.font = "900 46px Nunito"; c.fillStyle = INK; c.fillText('2026 (Jan–Okt): 14,408', 0, 0); c.restore(); }
}

// ================================================================ ZON 2: GRAF "BANDAR" (x 1300..3000)
const GX0 = 1450, GSTEP = 165, GROUND = 1500, KH = 1100 / 17598;
function barTimes() { return [E.y2017, E.l5 + 0.5, E.l5 + 1.0, E.l5 + 1.5, E.l5 + 2.0, E.jump, E.y2023, E.y2024, E.y2025]; }
function zoneChart(c) {
  const b = S.B;
  sky(c, 1100, 3300, -300, GROUND + 10, '#A8D8E8', '#FBEFD6');
  clouds(c, 1200, 3000, 150, 9);
  fillP(c, '#86BA72', cc => cc.rect(1100, GROUND, 2200, 1100), 0.6);
  c.fillStyle = '#76A863'; c.fillRect(1100, GROUND + 140, 2200, 900);
  const bt = barTimes(); let last = -1;
  YEARS.forEach(([yr, v], i) => {
    const x = GX0 + i * GSTEP, t0 = bt[i];
    const g = i === 5 ? (b < t0 ? 0 : back(P(t0, t0 + 0.9))) : out3(P(t0, t0 + 0.7));
    const h = v * KH * g;
    c.font = "800 44px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = INK; c.globalAlpha = P(t0 - 0.6, t0); c.fillText(String(yr), x, GROUND + 60); c.globalAlpha = 1;
    if (h <= 1) return;
    last = i;
    const col = i === 8 ? ACC : i === 5 ? '#F2A541' : '#5B8DB8';
    fillP(c, col, cc => rr(cc, x - 62, GROUND - h, 124, h + 4, 14), 1.1);
    // tingkap kecil (bar macam bangunan)
    c.fillStyle = 'rgba(255,255,255,0.28)'; for (let wy = GROUND - h + 22; wy < GROUND - 20; wy += 46) { c.fillRect(x - 40, wy, 26, 24); c.fillRect(x + 14, wy, 26, 24); }
    const vs = pop(i === 0 ? E.v2017 : t0 + 0.2, 0.5);
    label(c, fmt(v), x, GROUND - h - 42, { scale: vs, size: 34, font: "900 {s}px Nunito", bg: CREAM });
  });
  // kereta di atas bar terkini
  if (last >= 0) {
    const i = last, t0 = bt[i], prev = Math.max(0, i - 1);
    const hp = (k) => YEARS[k][1] * KH * (k === 5 ? (b < bt[5] ? 0 : back(P(bt[5], bt[5] + 0.9))) : out3(P(bt[k], bt[k] + 0.7)));
    const hop = P(t0, t0 + 0.6);
    const x = lerp(GX0 + prev * GSTEP, GX0 + i * GSTEP, i === 0 ? 1 : inOut(hop));
    const yv = GROUND - lerp(hp(prev), hp(i), i === 0 ? 1 : hop) - 70 - Math.sin(hop * Math.PI) * 120 * (i === 0 ? 0 : 1);
    mpv(c, x, yv, 0.2, {});
  }
  // ×2
  const sx = pop(E.x2, 0.45);
  if (sx > 0) {
    c.save(); c.translate(GX0 + 5 * GSTEP - 90, GROUND - 13308 * KH + 40); c.rotate(-0.15); c.scale(sx, sx);
    fillP(c, '#E63B2E', cc => cc.arc(0, 0, 80, 0, 7), 1.2);
    c.font = "800 84px 'Baloo 2'"; c.fillStyle = CREAM; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('×2', 0, 6);
    c.restore();
    // anak panah dari 2021 ke 2022
    c.save(); c.globalAlpha = Math.min(1, sx); c.strokeStyle = '#E63B2E'; c.lineWidth = 9; c.lineCap = 'round'; c.setLineDash([22, 16]);
    c.beginPath(); c.moveTo(GX0 + 4 * GSTEP, GROUND - 6286 * KH - 90); c.quadraticCurveTo(GX0 + 4.4 * GSTEP, GROUND - 13308 * KH - 180, GX0 + 5 * GSTEP - 20, GROUND - 13308 * KH - 100); c.stroke(); c.restore();
  }
  // panah naik 2022 -> 2025
  const na = out3(P(E.naik, E.naik + 1));
  if (na > 0) {
    const x0 = GX0 + 5 * GSTEP, y0 = GROUND - 13308 * KH - 190, x1 = GX0 + 8 * GSTEP + 40, y1 = GROUND - 17598 * KH - 200;
    c.save(); c.strokeStyle = ACC; c.lineWidth = 16; c.lineCap = 'round';
    c.beginPath(); c.moveTo(x0, y0); c.lineTo(lerp(x0, x1, na), lerp(y0, y1, na)); c.stroke();
    if (na > 0.95) { c.fillStyle = ACC; c.beginPath(); c.moveTo(x1 + 30, y1 - 20); c.lineTo(x1 - 30, y1 - 40); c.lineTo(x1 - 6, y1 + 30); c.fill(); }
    c.restore();
  }
}

// ================================================================ ZON 3: PAPAN KEDUDUKAN (y 2600..4300)
const RY0 = 2820, RSTEP = 160;
function zoneRank(c) {
  const b = S.B;
  sky(c, -900, 1100, 2300, 4700, '#F4DDBE', '#EBC9A0');
  for (let i = 0; i < 26; i++) { c.fillStyle = 'rgba(255,255,255,0.12)'; c.beginPath(); c.arc(-200 + rnd(i) * 1400, 2400 + rnd(i + 5) * 2200, 30 + rnd(i + 9) * 90, 0, 7); c.fill(); }
  label(c, 'Kedudukan 2025 · semua model', 540, RY0 - 120, { scale: pop(E.toRank + 0.6, 0.6), size: 44, bg: INK, fg: CREAM });
  RANK.forEach(([rk, name, v], i) => {
    const y = RY0 + i * RSTEP, t0 = E.toRank + 0.8 + i * 0.35, sl = out3(P(t0, t0 + 0.6));
    if (sl <= 0) return;
    const isA = rk === 13, hiA = isA && b >= E.rankAlph;
    const isC = rk === 17 && b >= E.civic, isS = rk === 14 && b >= E.s70;
    const sc = hiA ? 1 + 0.06 * back(P(E.rankAlph, E.rankAlph + 0.6)) - 0.06 : 1;
    c.save(); c.translate(lerp(1600, 0, sl), 0); c.translate(540, y); c.scale(sc, sc); c.translate(-540, -y);
    const bg = hiA ? ACC : isC ? '#5B8DB8' : isS ? '#2F6B45' : CREAM, fg = hiA || isC || isS ? CREAM : INK;
    fillP(c, bg, cc => rr(cc, 50, y - 64, 980, 128, 30), 1);
    fillP(c, hiA ? CREAM : INK, cc => cc.arc(122, y, 44, 0, 7), 0.4);
    c.font = "800 44px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = hiA ? ACC : CREAM; c.fillText('#' + rk, 122, y + 3);
    c.textAlign = 'left'; c.fillStyle = fg; c.font = "800 46px 'Baloo 2'"; c.fillText(name, 190, y - 18);
    const bw = v / 18059 * 520 * out3(P(t0 + 0.3, t0 + 1.0));
    c.fillStyle = hiA || isC || isS ? 'rgba(255,244,224,0.85)' : '#5B8DB8'; c.beginPath(); rr(c, 190, y + 20, Math.max(bw, 1), 22, 11); c.fill();
    c.textAlign = 'right'; c.font = "900 44px Nunito"; c.fillStyle = fg; c.fillText(fmt(v), 1000, y + 2);
    c.restore();
  });
  const r13 = pop(E.n13, 0.5);
  if (r13 > 0) { c.save(); c.translate(122, RY0 + 2 * RSTEP); c.scale(r13, r13); c.strokeStyle = '#E63B2E'; c.lineWidth = 10; c.beginPath(); c.arc(0, 0, 60, 0, 7); c.stroke(); c.restore();
    label(c, 'nombor 13!', 330, RY0 + 2 * RSTEP - 92, { scale: r13, size: 36, bg: '#E63B2E', fg: CREAM, rot: -0.05 }); }
  label(c, 'Alphard lebih 5,288 buah', 600, RY0 + 6 * RSTEP - 105, { scale: life(E.civic + 0.3, E.s70 - 0.8), size: 38, bg: INK, fg: CREAM, arrow: true });
  label(c, 'beza 432 buah je!', 640, RY0 + 3 * RSTEP + 105, { scale: life(E.s70 + 0.3, E.tapi - 0.3), size: 42, bg: '#E63B2E', fg: CREAM, rot: -0.04 });
}
function stamp(c, text, x, y, size, sc, rot = -0.14, color = '#E63B2E') {
  if (sc <= 0.001) return;
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc);
  c.font = `800 ${size}px 'Baloo 2'`; const w = c.measureText(text).width + size * 0.8, h = size * 1.35;
  c.fillStyle = 'rgba(255,248,236,0.95)'; c.beginPath(); rr(c, -w / 2, -h / 2, w, h, 16); c.fill();
  c.strokeStyle = color; c.lineWidth = size * 0.1; c.beginPath(); rr(c, -w / 2 + 8, -h / 2 + 8, w - 16, h - 16, 12); c.stroke();
  c.fillStyle = color; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, 0, size * 0.08);
  c.restore();
}

// ================================================================ ZON 4: GRID 100 KERETA (x 1300..2500, y 2600..4400)
const WX = 1900, WY = 3500;
function zoneWaffle(c) {
  const b = S.B;
  const lit = inOut(P(E.putih - 1, E.putih + 0.3));
  c.fillStyle = mix('#232838', '#8C9AAE', lit); c.fillRect(1150, 2560, 1600, 2200);
  for (let i = 0; i < 30; i++) { c.fillStyle = `rgba(255,255,255,${0.04 + 0.04 * lit})`; c.beginPath(); c.arc(1200 + rnd(i + 70) * 1500, 2400 + rnd(i + 80) * 2200, 20 + rnd(i + 90) * 80, 0, 7); c.fill(); }
  const others = ['#9C6B3E', '#C9A13B', '#B3B8C2'];
  for (let i = 0; i < 100; i++) {
    const col = i % 10, row = Math.floor(i / 10);
    const x = WX - 450 + col * 100, y = WY - 290 + row * 70;
    const sc = pop(E.hampir + (col + row) * 0.05, 0.5);
    let fill = '#6F7686';
    if (i < 62) fill = b >= E.putih + i * 0.012 ? '#F6F3EC' : fill;
    else if (i < 97) fill = b >= E.hitam + (i - 62) * 0.014 ? '#1E1F24' : fill;
    else fill = b >= E.hitam + 0.8 ? others[i - 97] : fill;
    const flip = (i < 62 && Math.abs(b - (E.putih + i * 0.012)) < 0.15) || (i >= 62 && i < 97 && Math.abs(b - (E.hitam + (i - 62) * 0.014)) < 0.15);
    miniCar(c, x, y, sc * 1.05 * (flip ? 1.25 : 1), fill);
  }
  label(c, 'PUTIH 61.5%', WX - 230, WY - 410, { scale: pop(E.putih, 0.6), size: 54, bg: '#F6F3EC', fg: INK });
  label(c, 'HITAM 34.9%', WX + 230, WY - 410, { scale: pop(E.hitam, 0.6), size: 54, bg: '#1E1F24', fg: CREAM });
  label(c, 'lain-lain 3.6%', WX + 300, WY + 470, { scale: pop(E.hitam + 0.9, 0.6), size: 36, bg: '#C9A13B', fg: INK });
  label(c, '100 Alphard (2025)', WX, WY - 410, { scale: life(E.hampir + 1, E.putih - 0.5), size: 40, bg: CREAM, fg: INK });
}

// ================================================================ kamera
function buildCam() {
  return [
    { x: 540, y: 1080, z: 1 },
    { b0: 0, b1: E.toBoard, x: 540, y: 1100, z: 1.05, ease: 'lin' },
    { b0: E.toBoard, b1: E.toBoard + 1.2, x: 540, y: 930, z: 1.25 },
    { b0: E.toBoard + 1.2, b1: E.toChart, x: 540, y: 920, z: 1.3, ease: 'lin' },
    { b0: E.toChart, b1: E.toChart + 1.2, x: 1500, y: 1250, z: 1.35, whip: true },
    { b0: E.l5 - 0.4, b1: E.l5 + 2.4, x: 1880, y: 1130, z: 0.95 },
    { b0: E.y2023 - 1.6, b1: E.y2023 + 0.4, x: 2150, y: 1080, z: 0.74 },
    { b0: E.toRank, b1: E.toRank + 1.2, x: 540, y: 3390, z: 0.9, whip: true },
    { b0: E.rankAlph - 0.8, b1: E.rankAlph + 0.2, x: 540, y: 3200, z: 1.12 },
    { b0: E.civic - 0.7, b1: E.civic, x: 540, y: 3700, z: 1.12 },
    { b0: E.s70 - 0.8, b1: E.s70, x: 540, y: 3250, z: 1.12 },
    { b0: E.tapi - 0.5, b1: E.tapi + 0.7, x: WX, y: WY + 20, z: 1.0, whip: true },
    { b0: E.tapi + 0.7, b1: E.toRoad, x: WX, y: WY, z: 1.05, ease: 'lin' },
    { b0: E.toRoad, b1: E.toRoad + 1.2, x: 540, y: 930, z: 1.25, whip: true },
    { b0: E.q - 1.2, b1: E.q + 0.4, x: 540, y: 1090, z: 1.0 },
  ];
}

// ================================================================ overlay skrin
function overlay(c) {
  const b = S.B;
  c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  // HOOK
  if (b < E.toBoard + 0.8) {
    const o = 1 - in3(P(E.toBoard - 0.3, E.toBoard + 0.5)), yo = -P(E.toBoard - 0.3, E.toBoard + 0.5) * 300;
    c.save(); c.globalAlpha = o;
    label(c, 'SEBAB APA?', 540, 160 + yo, { scale: pop(0, 0.6), size: 40, bg: ACC, fg: CREAM });
    bigText(c, 'Berapa ribu Alphard', 540, 285 + yo, 90, { scale: pop(0.2, 0.7) });
    bigText(c, 'register di Malaysia', 540, 382 + yo, 90, { scale: pop(E.title2, 0.7) });
    const s3 = pop(E.title2 + 0.8, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 495 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -300, -64, 600, 128, 24), 1.2); c.restore(); bigText(c, 'setiap tahun?', 540, 495 + yo, 96, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
  }
  // TAPI
  const tp = life(E.tapi, E.hampir + 0.3, 0.5, 0.5);
  if (tp > 0) bigText(c, 'TAPI...', 540 + Math.sin(b * 40) * 4 * (1 - P(E.tapi, E.tapi + 1.5)), 560, 170, { scale: tp, stroke: '#1C2033' });
  const dw = life(E.duaWarna, E.putih - 0.4, 0.5, 0.4);
  if (dw > 0) bigText(c, '2 warna sahaja!', 540, 520, 104, { scale: dw, fill: CREAM, stroke: '#1C2033' });
  // SOALAN
  const dim = P(E.q, E.q + 0.6) * (1 - P(E.outro, E.outro + 0.3));
  if (dim > 0) {
    c.fillStyle = `rgba(20,14,26,${0.6 * dim})`; c.fillRect(0, 0, W, H);
    bigText(c, 'Kalau kau beli...', 540, 420, 100, { scale: pop(E.q + 0.4, 0.7) });
    [[E.qPutih, '#F6F3EC', 'PUTIH', INK, 300], [E.qHitam, '#1E1F24', 'HITAM', CREAM, 780]].forEach(([bt, col, txt, fg, x]) => {
      const s = pop(bt, 0.6); if (s <= 0) return;
      c.save(); c.translate(x, 800); c.scale(s, s);
      fillP(c, col === '#F6F3EC' ? '#5B8DB8' : '#E8D9C0', cc => rr(cc, -210, -190, 420, 380, 40), 1.3);
      c.restore();
      mpv(c, x, 800 + 40 * s, 0.55 * s, { color: col, dark: col === '#F6F3EC' ? '#C9C5BC' : '#0E0F12' });
      label(c, txt, x, 800 + 140 * s, { scale: s, size: 56, bg: col, fg });
    });
    host(c, 165, 1420, 0.42 * pop(E.q + 0.8, 0.7), { pose: 'pointUp' });
    const cm = pop(E.comment, 0.6);
    if (cm > 0) { label(c, 'jawab di komen', 540, 1110, { scale: cm, size: 46, bg: CREAM }); c.save(); c.translate(540, 1185 + Math.sin(b * 3) * 10); c.scale(cm, cm); c.fillStyle = CREAM; c.beginPath(); c.moveTo(-26, 0); c.lineTo(26, 0); c.lineTo(0, 34); c.fill(); c.restore(); }
  }
}
function outro(c) {
  const b = S.B; if (b < E.outro - 0.4) return;
  const p = out3(P(E.outro - 0.2, E.outro + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = ACC; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.12; c.fillStyle = CREAM;
  for (let i = 0; i < 18; i++) { c.beginPath(); c.arc(rnd(i) * W, rnd(i + 30) * H, 40 + rnd(i + 3) * 120, 0, 7); c.fill(); }
  c.globalAlpha = 1; S.ZK = 1;
  host(c, 540, 990, 0.74 * pop(E.outro + 0.2, 0.8), { pose: 'wave' });
  bigText(c, 'SEBAB APA?', 540, 1120, 150, { scale: pop(E.outro + 0.5, 0.7), stroke: '#7A2A12' });
  label(c, 'Satu soalan. Satu minit.', 540, 1265, { scale: pop(E.outro + 1.2, 0.6), size: 48, bg: CREAM });
  label(c, 'follow untuk soalan seterusnya', 540, 1385, { scale: pop(E.outro + 1.8, 0.6), size: 36, bg: INK, fg: CREAM });
  c.restore();
}
function drawCaptions(c) {
  const t = S.B * BEAT; if (S.B > E.outro - 0.3) return;
  const cap = CAPS.find(k => t >= k.start && t < k.end);
  if (!cap || cap.hidden) return;
  const age = (t - cap.start) / BEAT;
  caption(c, cap.segs, 540, 1500, { scale: 0.9 + 0.1 * back(clamp(age / 0.35)), alpha: clamp(age / 0.15) });
}

// ================================================================ render
function world(c, cam) {
  applyCam(c, cam);
  const v = viewRect(cam);
  c.fillStyle = '#2A2238'; c.fillRect(v.x0 - 10, v.y0 - 10, v.x1 - v.x0 + 20, v.y1 - v.y0 + 20);
  if (sees(v, -900, -300, 1100, 2535)) zoneRoad(c);
  if (sees(v, 1100, -300, 3300, 2500)) zoneChart(c);
  if (sees(v, -900, 2300, 1100, 4700)) zoneRank(c);
  if (sees(v, 1150, 2300, 2750, 4700)) zoneWaffle(c);
}
function renderFrame(t) {
  const b = t / BEAT; S.B = b;
  const cam = camAt(CAM, b);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (cam.whip) {
    const N = 16, sh = 0.2;
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < N; i++) {
      const cs = camAt(CAM, b + (i / (N - 1) - 0.5) * sh);
      lctx.setTransform(1, 0, 0, 1, 0, 0); world(lctx, cs);
      ctx.filter = 'blur(6px)'; ctx.globalAlpha = 1 / (i + 1); ctx.drawImage(layer, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
    }
  } else world(ctx, cam);
  overlay(ctx);
  drawCaptions(ctx);
  outro(ctx);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  grain(ctx, 0.09);
  vignette(ctx, 0.3);
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
  await document.fonts.load("800 50px 'Baloo 2'"); await document.fonts.load('900 50px Nunito');
  await document.fonts.ready;
  window.DURATION = TL.totalBeats * BEAT + TL.tailSeconds;
  renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
