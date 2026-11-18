// Sebab Apa? — Duit rokok vs Civic FL5. Masa dikunci pada perkataan VO (events.json).
'use strict';
const { W, H, S, clamp, lerp, inOut, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, label, bigText,
  caption, camAt, applyCam, viewRect, sees, toScreen, grain, vignette, setHostHead, host, hostPeek, person } = PAPER;

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
const lctx = layer.getContext('2d');
let TL, CAPS, BEAT, E, CAM;
const ACC = '#FF6B35', INK = '#2B2024', CREAM = '#FFF4E0', RED = '#E63B2E';
const fmt = v => Math.round(v).toLocaleString('en-US');
const PACK = 18.2;

// ================================================================ objek
function pack(c, x, y, s, o = {}) {   // kotak rokok generik (tiada jenama)
  if (s <= 0.001) return;
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(s, s);
  fillP(c, '#F3EFE6', cc => rr(cc, -60, -90, 120, 180, 10), o.flat ? 0 : 1);
  c.fillStyle = '#7A8794'; c.fillRect(-60, -90, 120, 34);                    // penutup
  c.fillStyle = '#1E1F24'; c.beginPath(); rr(c, -60, 30, 120, 60, 8); c.fill(); // panel amaran
  c.fillStyle = '#FFF'; c.font = "800 22px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('AMARAN', 0, 60);
  c.fillStyle = '#7A8794'; c.font = "800 44px 'Baloo 2'"; c.fillText('20', 0, -10);
  c.restore();
}
function note(c, x, y, s, rot, col) {
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s);
  fillP(c, col, cc => rr(cc, -70, -34, 140, 68, 6), 0.6);
  c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 3; c.strokeRect(-62, -26, 124, 52);
  c.fillStyle = 'rgba(255,255,255,0.85)'; c.font = "800 28px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('RM', -28, 2);
  c.beginPath(); c.arc(34, 0, 16, 0, 7); c.fill();
  c.restore();
}
function puff(c, x, y, r, a) {
  c.save(); c.globalAlpha *= a;
  [[0, 0, 1], [0.7, 0.2, 0.75], [-0.7, 0.25, 0.7], [0.2, -0.55, 0.8]].forEach(([dx, dy, k]) => fillP(c, '#C9C6CF', cc => cc.arc(x + dx * r, y + dy * r, r * k, 0, 7), 0.3));
  c.restore();
}
function fl5(c, x, y, s, o = {}) {   // hot hatch pandangan sisi, Racing Black, sayap belakang
  if (s <= 0.001) return;
  const col = o.color || '#1C1D22';
  c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
  c.fillStyle = 'rgba(20,15,20,0.25)'; c.beginPath(); c.ellipse(0, 4, 330, 16, 0, 0, 7); c.fill();
  // sayap
  c.fillStyle = col; c.fillRect(-300, -210, 14, 46); c.fillRect(-250, -210, 14, 40);
  fillP(c, col, cc => rr(cc, -335, -228, 120, 22, 6), 0.6);
  // badan
  fillP(c, col, cc => {
    cc.moveTo(-310, -50); cc.lineTo(-312, -150); cc.quadraticCurveTo(-300, -175, -250, -190);
    cc.lineTo(-120, -235); cc.quadraticCurveTo(-60, -252, 20, -248); cc.lineTo(90, -240);
    cc.quadraticCurveTo(150, -205, 200, -165); cc.lineTo(300, -140); cc.quadraticCurveTo(330, -130, 330, -90); cc.lineTo(328, -50); cc.closePath();
  }, 1.1);
  // tingkap
  c.fillStyle = '#3A4656'; c.beginPath(); c.moveTo(-235, -178); c.lineTo(-118, -222); c.quadraticCurveTo(-60, -238, 10, -234); c.lineTo(80, -228); c.lineTo(160, -175); c.closePath(); c.fill();
  c.fillStyle = col; c.fillRect(-40, -236, 12, 62);
  c.fillStyle = 'rgba(255,255,255,0.18)'; c.beginPath(); c.moveTo(20, -232); c.lineTo(60, -230); c.lineTo(10, -178); c.lineTo(-25, -178); c.fill();
  // garisan merah bawah, lampu, ekzos
  c.fillStyle = RED; c.fillRect(-300, -62, 620, 7);
  c.fillStyle = '#FFF6C8'; c.beginPath(); rr(c, 270, -142, 52, 14, 7); c.fill();
  c.fillStyle = RED; c.fillRect(-314, -148, 10, 28);
  c.fillStyle = '#8D949F'; [[-318, -70], [-318, -60], [-318, -80]].forEach(([ex, ey]) => { c.beginPath(); c.arc(ex, ey, 5, 0, 7); c.fill(); });
  // roda
  const spin = o.spin || 0;
  [-190, 200].forEach(wx => {
    fillP(c, '#15161A', cc => cc.arc(wx, -50, 64, 0, 7), 0.6);
    c.fillStyle = '#2E3036'; c.beginPath(); c.arc(wx, -50, 42, 0, 7); c.fill();
    c.fillStyle = RED; c.fillRect(wx - 26, -78, 16, 22);
    c.strokeStyle = '#5E646E'; c.lineWidth = 7;
    for (let k = 0; k < 5; k++) { const a = spin + k * 1.2566; c.beginPath(); c.moveTo(wx, -50); c.lineTo(wx + Math.cos(a) * 38, -50 + Math.sin(a) * 38); c.stroke(); }
  });
  c.restore();
}
function tabungAyam(c, x, y, s, shake) {   // tabung tanah liat bentuk ayam jantan
  c.save(); c.translate(x, y); c.rotate(Math.sin(shake * 40) * 0.05 * shake); c.scale(s, s);
  // ekor
  [['#2F6B45', -1.0], ['#E2483A', -0.6], ['#F2A541', -0.2]].forEach(([col, a]) => fillP(c, col, cc => { cc.moveTo(-150, -80); cc.quadraticCurveTo(-260 + a * 30, -260 + a * 40, -150 + a * 80, -300); cc.quadraticCurveTo(-170, -200, -120, -110); }, 0.6));
  // badan
  fillP(c, '#E9A25B', cc => cc.ellipse(0, -110, 190, 140, 0, 0, 7), 1.2);
  c.fillStyle = 'rgba(255,255,255,0.18)'; c.beginPath(); c.ellipse(-50, -170, 80, 40, -0.3, 0, 7); c.fill();
  // corak
  c.strokeStyle = '#C65A2E'; c.lineWidth = 8; c.lineCap = 'round';
  [-60, 0, 60].forEach(dx => { c.beginPath(); c.arc(dx, -90, 28, 0.2, Math.PI - 0.2); c.stroke(); });
  // kepala, balung, paruh
  fillP(c, '#E9A25B', cc => cc.arc(150, -230, 70, 0, 7), 1);
  fillP(c, RED, cc => { cc.arc(130, -300, 22, 0, 7); cc.arc(160, -306, 24, 0, 7); cc.arc(188, -294, 20, 0, 7); }, 0.4);
  fillP(c, '#F2C14E', cc => { cc.moveTo(212, -236); cc.lineTo(262, -222); cc.lineTo(212, -208); }, 0.4);
  c.fillStyle = INK; c.beginPath(); c.arc(170, -244, 9, 0, 7); c.fill();
  // lubang duit
  c.fillStyle = '#5A2E1A'; c.beginPath(); rr(c, -60, -255, 120, 16, 8); c.fill();
  // kaki/tapak
  fillP(c, '#C9814A', cc => cc.ellipse(0, -10, 150, 26, 0, 0, 7), 0.8);
  c.restore();
}

// ================================================================ ZON A: KEDAI (0..1080, 0..1920)
function zoneKedai(c) {
  const b = S.B;
  c.fillStyle = '#F2D9B5'; c.fillRect(-900, -400, 2900, 2900);
  // rak belakang
  for (let r = 0; r < 4; r++) {
    fillP(c, '#9C6B3E', cc => cc.rect(-200, 420 + r * 190, 1480, 20), 0.6);
    for (let k = 0; k < 16; k++) {
      const x = -160 + k * 92, cols = ['#E2483A', '#F2C14E', '#5B8DB8', '#7EBF6B', '#E86A5C', '#9B6BD3'];
      fillP(c, cols[(k + r * 3) % 6], cc => rr(cc, x, 300 + r * 190, 70, 120, 10), 0.4);
      c.fillStyle = 'rgba(255,255,255,0.5)'; c.fillRect(x + 12, 330 + r * 190, 46, 18);
    }
  }
  label(c, 'KEDAI RUNCIT', 540, 200, { size: 56, bg: '#2F6B45', fg: CREAM, radius: 14 });
  // almari rokok
  fillP(c, '#4A3B4F', cc => rr(cc, 640, 1100, 360, 230, 16), 0.8);
  for (let r = 0; r < 2; r++) for (let k = 0; k < 5; k++) pack(c, 680 + k * 70, 1160 + r * 110, 0.42, { flat: true });
  // kaunter
  fillP(c, '#8A5A33', cc => cc.rect(-200, 1330, 1480, 40), 1);
  fillP(c, '#A86E45', cc => cc.rect(-200, 1370, 1480, 600), 1);
  c.fillStyle = 'rgba(0,0,0,0.08)'; for (let k = 0; k < 10; k++) c.fillRect(-180 + k * 150, 1390, 8, 560);
  // pelanggan
  const handOut = out3(P(E.buy - 0.5, E.buy + 0.3));
  person(c, 260, 1360, 1.1, { shirt: '#5B8DB8', skin: '#C98B5E', pinch: 0 });
  // kotak di kaunter
  const pk = pop(E.buy, 0.6);
  pack(c, 560, 1250, 0.9 * pk, { rot: -0.08 });
  // duit -> asap
  if (b > E.money - 0.2 && b < E.toPack + 1) {
    for (let i = 0; i < 6; i++) {
      const t0 = E.money - 0.2 + i * 0.35, p = clamp((b - t0) / 4);
      if (p <= 0) continue;
      const x = 400 + rnd(i) * 300 + Math.sin(b * 2 + i) * 30, y = 1200 - p * 900;
      const morph = clamp((b - E.asap + 0.6) / 1.2 + p * 0.3 - 0.3);
      if (morph < 1) { c.save(); c.globalAlpha = 1 - morph; note(c, x, y, 0.9, Math.sin(b * 3 + i) * 0.4, i % 2 ? '#3E8F7A' : '#C9584A'); c.restore(); }
      if (morph > 0) puff(c, x, y, 50 + 30 * morph, morph * (1 - P(E.toPack, E.toPack + 0.8)));
    }
  }
  label(c, `RM${PACK.toFixed(2)}`, 690, 1110, { scale: pop(E.price, 0.6), size: 72, bg: ACC, fg: CREAM, rot: 0.08 });
  label(c, 'sekotak', 690, 1210, { scale: pop(E.price + 0.4, 0.5), size: 40, bg: CREAM, rot: 0.08 });
  hostPeek(c, 960, 1080, 0.6 * life(E.title2, E.toPack - 0.5, 0.7, 0.4), -0.12);
}

// ================================================================ ZON B: KALENDAR (pusat 1850, 960)
function zoneKalendar(c) {
  const b = S.B, cx = 1850;
  c.fillStyle = '#CFE3E8'; c.fillRect(1150, -400, 1300, 2900);
  for (let i = 0; i < 20; i++) { c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.arc(1200 + rnd(i + 3) * 1200, rnd(i + 8) * 1900, 30 + rnd(i) * 70, 0, 7); c.fill(); }
  const yr = P(E.year - 0.2, E.year + 0.8);
  // kalendar sebulan
  const mo = 1 - in3(yr) * 0.5;
  c.save(); c.translate(cx, 880); c.scale(mo, mo);
  fillP(c, CREAM, cc => rr(cc, -400, -330, 800, 700, 30), 1.3);
  c.fillStyle = RED; c.beginPath(); rr(c, -400, -330, 800, 120, 30); c.fill(); c.fillRect(-400, -250, 800, 40);
  c.fillStyle = CREAM; c.font = "800 64px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('SEBULAN', 0, -265);
  const filled = clamp((b - (E.month - 2.2)) / 3) * 30;
  for (let d = 0; d < 30; d++) {
    const col = d % 7, row = Math.floor(d / 7), x = -330 + col * 110, y = -150 + row * 110;
    c.fillStyle = '#E9DCC4'; c.beginPath(); rr(c, x - 46, y - 46, 92, 92, 14); c.fill();
    c.fillStyle = '#9A8B78'; c.font = "800 26px 'Baloo 2'"; c.fillText(String(d + 1), x - 26, y - 26);
    if (d < filled) pack(c, x + 8, y + 6, 0.38 * Math.min(1, (filled - d) * 1.5), { flat: true, rot: 0.1 });
  }
  c.restore();
  // pengira
  const vMonth = PACK * 30 * inOut(P(E.month - 2.2, E.m500));
  const vYear = PACK * 365 * inOut(P(E.year, E.y6000));
  const showY = b >= E.year;
  c.save(); c.translate(cx, 1380);
  fillP(c, INK, cc => rr(cc, -330, -95, 660, 190, 40), 1.2);
  c.font = "800 120px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.fillStyle = showY ? ACC : (b >= E.m500 ? '#FFD23F' : CREAM);
  c.fillText('RM' + fmt(showY ? Math.max(vYear, PACK * 30) : vMonth), 0, 8);
  c.restore();
  label(c, showY ? 'RM18.20 × 365 hari' : 'RM18.20 × 30 hari', cx, 1520, { scale: pop(showY ? E.year : E.month - 1, 0.6), size: 38, bg: CREAM });
  // 12 bulan
  if (yr > 0) {
    for (let m = 0; m < 12; m++) {
      const a = m / 12 * 6.283 - 1.57, rad = 520 * out3(yr);
      const x = cx + Math.cos(a) * rad, y = 800 + Math.sin(a) * rad * 0.72;
      c.save(); c.translate(x, y); c.scale(0.9 * pop(E.year + m * 0.06, 0.5), 0.9 * pop(E.year + m * 0.06, 0.5));
      fillP(c, CREAM, cc => rr(cc, -60, -60, 120, 120, 14), 0.8); c.fillStyle = RED; c.fillRect(-60, -60, 120, 30);
      c.fillStyle = INK; c.font = "800 36px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'O', 'S', 'O', 'N', 'D'][m], 0, 18);
      c.restore();
    }
  }
}

// ================================================================ ZON C: TABUNG + FIKIR (pusat 3250, 960)
function zoneTabung(c) {
  const b = S.B, cx = 3250;
  c.fillStyle = '#F6E3C6'; c.fillRect(2550, -400, 1400, 2900);
  for (let i = 0; i < 20; i++) { c.fillStyle = 'rgba(255,255,255,0.35)'; c.beginPath(); c.arc(2600 + rnd(i + 13) * 1300, rnd(i + 18) * 1900, 30 + rnd(i) * 70, 0, 7); c.fill(); }
  fillP(c, '#C9A27A', cc => cc.rect(2550, 1350, 1400, 700), 0.8);
  const sh = clamp(1 - Math.abs(b - E.tabung - 0.6) * 1.5);
  tabungAyam(c, cx, 1350, 1.35, sh);
  label(c, 'TABUNG KERETA', cx - 20, 1215, { scale: pop(E.tabung, 0.6), size: 46, bg: INK, fg: CREAM, rot: -0.03 });
  for (let i = 0; i < 6; i++) {
    const t0 = E.tabung - 1 + i * 0.3, p = P(t0, t0 + 0.8);
    if (p <= 0 || p >= 1) continue;
    note(c, cx + (rnd(i) - 0.5) * 120, lerp(400, 1000, in3(p)), 0.8, rnd(i + 2) * 2, i % 2 ? '#3E8F7A' : '#C9584A');
  }
  // gelembung fikir: berapa kotak -> FL5
  const tb = pop(E.think, 0.7);
  if (tb > 0) {
    [[cx + 170, 900, 22], [cx + 220, 820, 34]].forEach(([x, y, r]) => fillP(c, '#FFFFFF', cc => cc.arc(x, y, r * tb, 0, 7), 0.5));
    c.save(); c.translate(cx, 520); c.scale(tb, tb);
    fillP(c, '#FFFFFF', cc => { [[-250, 0, 170], [0, -60, 200], [250, 0, 170], [-120, 110, 150], [130, 110, 150]].forEach(([x, y, r]) => { cc.moveTo(x + r, y); cc.arc(x, y, r, 0, 7); }); }, 1.1);
    c.restore();
    const cs = pop(E.civic, 0.7);
    fl5(c, cx, 610, 0.85 * cs, { spin: b });
    if (b < E.civic + 0.3) bigText(c, '? kotak', cx, 520, 96, { scale: tb * (1 - P(E.civic - 0.2, E.civic + 0.3)), fill: CREAM });
    label(c, 'Civic FL5', cx, 300, { scale: cs, size: 50, bg: ACC, fg: CREAM });
  }
}

// ================================================================ ZON D: MENARA 15,000 KOTAK (pusat 540, 3300)
const TGROUND = 4200, THMAX = 1500;
function zoneMenara(c) {
  const b = S.B;
  const g = c.createLinearGradient(0, 2200, 0, TGROUND); g.addColorStop(0, '#8FCBE6'); g.addColorStop(1, '#F7E6C4');
  c.fillStyle = g; c.fillRect(-900, 2200, 2900, 2000);
  for (let i = 0; i < 6; i++) fillP(c, '#FFFFFF', cc => cc.arc(-100 + rnd(i + 40) * 1300, 2350 + rnd(i + 41) * 900, 50 + rnd(i) * 40, 0, 7), 0.3);
  fillP(c, '#86BA72', cc => cc.rect(-900, TGROUND, 2900, 800), 0.6);
  const gp = inOut(P(E.k15 - 2.6, E.k15 + 0.2)), h = THMAX * gp;
  if (h > 2) {
    // menara: corak kotak berulang
    c.save(); c.beginPath(); c.rect(300, TGROUND - h, 380, h); c.clip();
    for (let y = TGROUND - 60; y > TGROUND - h - 120; y -= 120) for (let x = 330; x < 680; x += 80) pack(c, x + 10, y, 0.42, { flat: true });
    c.restore();
    c.strokeStyle = INK; c.lineWidth = 6; c.strokeRect(300, TGROUND - h, 380, h);
  }
  fl5(c, 880, TGROUND, 0.42, {});
  // pengira kotak & nilai
  const cnt = 15000 * gp;
  label(c, fmt(cnt) + ' kotak', 490, TGROUND - h - 90, { scale: pop(E.k15 - 2.6, 0.5), size: 64, bg: INK, fg: CREAM });
  const rs = pop(E.rm273, 0.5);
  if (rs > 0) { c.save(); c.translate(490, TGROUND - h - 230); c.rotate(-0.06); c.scale(rs, rs); fillP(c, ACC, cc => rr(cc, -300, -70, 600, 140, 28), 1.2); c.font = "800 96px 'Baloo 2'"; c.fillStyle = CREAM; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('RM273,000', 0, 6); c.restore(); }
  label(c, '15,000 × RM18.20', 490, TGROUND - h - 345, { scale: pop(E.rm273 + 0.6, 0.5), size: 36, bg: CREAM });
}

// ================================================================ ZON E: 41 TAHUN + BERHENTI (pusat 1850, 3300)
function zoneTahun(c) {
  const b = S.B, cx = 1850;
  const lit = inOut(P(E.quit - 0.5, E.quit + 0.8));
  c.fillStyle = mix('#1F2433', '#D9E8D4', lit); c.fillRect(1150, 2200, 1400, 2900);
  // kertas kalendar berterbangan
  if (lit < 1) for (let i = 0; i < 30; i++) {
    const ph = ((b * 0.25 + rnd(i)) % 1);
    c.save(); c.globalAlpha = (1 - lit) * 0.7; c.translate(1200 + rnd(i + 3) * 1300, 4300 - ph * 2200); c.rotate(ph * 6 + i);
    c.fillStyle = CREAM; c.fillRect(-30, -30, 60, 60); c.fillStyle = RED; c.fillRect(-30, -30, 60, 16); c.restore();
  }
  // tahun berpusing
  const yp = inOut(P(E.tapi + 1, E.y41 + 0.6)), yr = Math.round(2026 + 41 * yp);
  if (b < E.quit) {
    c.save(); c.globalAlpha = 1 - lit;
    c.font = "800 220px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = CREAM; c.fillText(String(yr), cx, 3200);
    c.font = "900 50px Nunito"; c.fillStyle = '#9AA3B8'; c.fillText('2026  →  ' + (b > E.y41 ? '2067' : '????'), cx, 3380);
    c.restore();
  }
  // berhenti / kurangkan
  if (b > E.quit - 0.3) {
    const sc = pop(E.quit - 0.3, 0.6), shrink = lerp(1, 0.55, inOut(P(E.less, E.less + 0.8)));
    pack(c, cx, 3220, 2.2 * sc * shrink, {});
    const xs = pop(E.quit, 0.45) * (1 - P(E.less - 0.3, E.less));
    if (xs > 0) { c.save(); c.translate(cx, 3220); c.scale(xs, xs); c.strokeStyle = RED; c.lineWidth = 46; c.lineCap = 'round'; c.beginPath(); c.moveTo(-230, -230); c.lineTo(230, 230); c.moveTo(230, -230); c.lineTo(-230, 230); c.stroke(); c.restore(); }
    label(c, 'BERHENTI', cx - 220, 2860, { scale: pop(E.quit, 0.6), size: 64, bg: '#2F6B45', fg: CREAM, rot: -0.06 });
    label(c, 'atau KURANGKAN', cx + 170, 3600, { scale: pop(E.less, 0.6), size: 56, bg: ACC, fg: CREAM, rot: 0.04 });
    const ar = pop(E.less, 0.6);
    if (ar > 0) { c.save(); c.translate(cx + 300, 3220); c.scale(ar, ar); c.fillStyle = ACC; c.fillRect(-18, -120, 36, 160); c.beginPath(); c.moveTo(-60, 40); c.lineTo(60, 40); c.lineTo(0, 120); c.fill(); c.restore(); }
  }
}

// ================================================================ ZON G: JALAN + FL5 + HOS (pusat 3250, 3300)
function zoneJalan(c) {
  const b = S.B, cx = 3250, gy = 3750;
  const g = c.createLinearGradient(0, 2200, 0, gy); g.addColorStop(0, '#8FCBE6'); g.addColorStop(1, '#FBEBCB');
  c.fillStyle = g; c.fillRect(2550, 2200, 1400, 2900);
  for (let i = 0; i < 6; i++) fillP(c, '#FFFFFF', cc => cc.arc(2600 + rnd(i + 60) * 1300, 2400 + rnd(i + 61) * 600, 50 + rnd(i) * 40, 0, 7), 0.3);
  for (let i = 0; i < 9; i++) { const bx = 2560 + i * 160, hh = 300 + rnd(i + 70) * 400; fillP(c, '#B8C9DA', cc => cc.rect(bx, gy - hh, 140, hh), 0.4); }
  fillP(c, '#C9BBA8', cc => cc.rect(2550, gy, 1400, 50), 0.6);
  c.fillStyle = '#4A4652'; c.fillRect(2550, gy + 50, 1400, 900);
  c.fillStyle = 'rgba(255,244,224,0.75)'; for (let x = 2560; x < 3950; x += 180) c.fillRect(x, gy + 300, 100, 14);
  const cxp = lerp(4300, cx + 120, out3(P(E.noSmoke - 0.4, E.noSmoke + 1.6)));
  fl5(c, cxp, gy + 230, 0.95, { spin: -cxp / 60 });
  host(c, cx - 320, gy + 40, 0.55 * pop(E.back + 0.3, 0.7), { pose: b > E.fl5 ? 'pointUp' : 'cheer' });
  label(c, 'FL5?', cx + 200, gy - 330, { scale: pop(E.fl5, 0.6), size: 110, bg: ACC, fg: CREAM, rot: -0.05 });
  label(c, 'tak merokok + cukup duit', cx + 60, 2560, { scale: pop(E.noSmoke, 0.6), size: 44, bg: INK, fg: CREAM });
}

// ================================================================ rakaman sebenar (bingkai kertas)
const FOOT = { a: { n: 174 }, b: { n: 90 }, c: { n: 78 } };
const imgCache = new Map();
function loadImg(url) {
  if (imgCache.has(url)) return imgCache.get(url);
  const p = new Promise(res => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null); im.src = url; });
  imgCache.set(url, p);
  if (imgCache.size > 40) imgCache.delete(imgCache.keys().next().value);
  return p;
}
function footClip() {
  const b = S.B;
  if (b < E.foot) return null;
  if (b < E.footB) return ['a', (b - E.foot) * BEAT];
  if (b < E.footC) return ['b', (b - E.footB) * BEAT];
  return ['c', (b - E.footC) * BEAT];
}
async function drawFootage(c) {
  const b = S.B; if (b < E.foot - 0.1 || b > E.cta + 1.5) return;
  const wipe = out3(P(E.foot - 0.1, E.foot + 0.8));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  // helaian kertas menyapu dari bawah (tepi koyak)
  const top = lerp(H + 80, -60, wipe);
  c.fillStyle = '#F4DDBE'; c.beginPath(); c.moveTo(0, H); c.lineTo(0, top);
  for (let x = 0; x <= W; x += 40) c.lineTo(x, top + (rnd(x) - 0.5) * 30);
  c.lineTo(W, H); c.fill();
  c.clip();
  for (let i = 0; i < 14; i++) { c.fillStyle = 'rgba(255,255,255,0.18)'; c.beginPath(); c.arc(rnd(i + 90) * W, rnd(i + 91) * H, 60 + rnd(i) * 120, 0, 7); c.fill(); }
  const fc = footClip();
  if (fc) {
    const [k, ts] = fc, n = Math.min(FOOT[k].n, Math.max(1, Math.floor(ts * 30) + 1));
    const im = await loadImg(`/projects/civic/build/footage/${k}/${String(n).padStart(4, '0')}.jpg`);
    const cardIn = back(P(E.foot + 0.2, E.foot + 1.0));
    const swap = k === 'a' ? 0 : Math.max(0, 1 - P(k === 'b' ? E.footB : E.footC, (k === 'b' ? E.footB : E.footC) + 0.5));
    const rot = (k === 'a' ? -0.025 : k === 'b' ? 0.02 : -0.015) + swap * 0.15;
    const cw = 820, ch = 1458, kb = 1 + 0.04 * Math.min(1, ts / 6);
    c.save(); c.translate(540, 880); c.rotate(rot); c.scale(cardIn * (1 - swap * 0.08), cardIn * (1 - swap * 0.08));
    fillP(c, '#FFFFFF', cc => rr(cc, -cw / 2 - 22, -ch / 2 - 22, cw + 44, ch + 44, 18), 1.6);
    c.save(); c.beginPath(); rr(c, -cw / 2, -ch / 2, cw, ch, 8); c.clip();
    if (im) c.drawImage(im, -cw / 2 * kb, -ch / 2 * kb, cw * kb, ch * kb);
    c.restore();
    c.restore();
  }
  // pelekat
  label(c, '2 UNIT', 230, 250, { scale: life(E.unit2, E.footB - 0.3, 0.6, 0.3), size: 70, bg: ACC, fg: CREAM, rot: -0.08 });
  label(c, 'spec Racing Black', 330, 400, { scale: life(E.racing, E.footB - 0.3, 0.6, 0.3), size: 50, bg: '#1C1D22', fg: CREAM, rot: -0.04 });
  label(c, 'TAHUN 2025', 820, 330, { scale: life(E.y2025, E.footB - 0.3, 0.6, 0.3), size: 52, bg: CREAM, rot: 0.06 });
  const rd = pop(E.ready, 0.45) * (1 - P(E.footB - 0.3, E.footB));
  if (rd > 0) { c.save(); c.translate(540, 1120); c.rotate(-0.06); c.scale(rd, rd); c.font = "800 70px 'Baloo 2'"; const w = c.measureText('READY DI SHOWROOM').width + 60; c.fillStyle = 'rgba(255,248,236,0.95)'; c.beginPath(); rr(c, -w / 2, -60, w, 120, 16); c.fill(); c.strokeStyle = '#2F6B45'; c.lineWidth = 8; c.beginPath(); rr(c, -w / 2 + 8, -52, w - 16, 104, 12); c.stroke(); c.fillStyle = '#2F6B45'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('READY DI SHOWROOM', 0, 6); c.restore(); }
  // tag harga berayun
  const tg = pop(E.rm270, 0.6) * (1 - P(E.footC - 0.3, E.footC));
  if (tg > 0) {
    c.save(); c.translate(760, 260); c.rotate(Math.sin(b * 3) * 0.06 + 0.1); c.scale(tg, tg);
    c.strokeStyle = INK; c.lineWidth = 4; c.beginPath(); c.moveTo(-190, -110); c.lineTo(-150, -50); c.stroke();
    fillP(c, '#FFD23F', cc => { cc.moveTo(-170, -60); cc.lineTo(230, -60); cc.lineTo(230, 90); cc.lineTo(-170, 90); cc.lineTo(-230, 15); cc.closePath(); }, 1.3);
    c.fillStyle = INK; c.beginPath(); c.arc(-180, 15, 12, 0, 7); c.fill();
    c.font = "800 92px 'Baloo 2'"; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('RM270k', 30, 22);
    c.restore();
  }
  // CTA komen
  const kb2 = pop(E.komen, 0.6);
  if (kb2 > 0 && b < E.cta + 0.5) {
    c.save(); c.translate(540, 300); c.scale(kb2, kb2);
    fillP(c, '#FFFFFF', cc => { rr(cc, -330, -90, 660, 180, 40); cc.moveTo(-220, 85); cc.lineTo(-260, 150); cc.lineTo(-160, 85); }, 1.4);
    c.font = "800 84px 'Baloo 2'"; c.fillStyle = INK; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('Komen "NAK"', 0, 8);
    c.restore();
  }
  label(c, 'saya DM korang!', 540, 470, { scale: pop(E.dm, 0.6) * (b < E.cta + 0.5 ? 1 : 0), size: 54, bg: ACC, fg: CREAM, rot: -0.03 });
  c.restore();
}

// ================================================================ kamera
function buildCam() {
  return [
    { x: 540, y: 960, z: 1 },
    { b0: 0, b1: E.toPack, x: 540, y: 980, z: 1.04, ease: 'lin' },
    { b0: E.toPack, b1: E.toPack + 1.2, x: 600, y: 1170, z: 1.7 },
    { b0: E.toCal, b1: E.toCal + 1.2, x: 1850, y: 960, z: 1.0, whip: true },
    { b0: E.year - 0.2, b1: E.year + 0.8, x: 1850, y: 960, z: 0.92 },
    { b0: E.toBank, b1: E.toBank + 1.2, x: 3250, y: 1000, z: 1.0, whip: true },
    { b0: E.think - 0.5, b1: E.think + 0.6, x: 3250, y: 900, z: 1.0 },
    { b0: E.toTower, b1: E.toTower + 1.2, x: 540, y: 3700, z: 1.0, whip: true },
    { b0: E.k15 - 2.6, b1: E.k15 + 0.2, x: 540, y: 3250, z: 0.95 },
    { b0: E.rm273 - 0.5, b1: E.rm273 + 0.5, x: 540, y: 3330, z: 0.86 },
    { b0: E.tapi - 0.5, b1: E.tapi + 0.7, x: 1850, y: 3300, z: 1.0, whip: true },
    { b0: E.tapi + 0.7, b1: E.back - 0.4, x: 1850, y: 3280, z: 1.05, ease: 'lin' },
    { b0: E.back - 0.4, b1: E.back + 0.8, x: 3250, y: 3300, z: 1.0, whip: true },
    { b0: E.back + 0.8, b1: E.foot, x: 3250, y: 3320, z: 1.04, ease: 'lin' },
  ];
}

// ================================================================ overlay
function overlay(c) {
  const b = S.B;
  c.setTransform(1, 0, 0, 1, 0, 0); S.ZK = 1;
  if (b < E.toPack + 0.8) {
    const o = 1 - in3(P(E.toPack - 0.4, E.toPack + 0.4)), yo = -P(E.toPack - 0.4, E.toPack + 0.4) * 300;
    c.save(); c.globalAlpha = o;
    label(c, 'SEBAB APA?', 540, 330 + yo, { scale: pop(0, 0.6), size: 40, bg: ACC, fg: CREAM });
    bigText(c, 'Hari-hari beli rokok,', 540, 450 + yo, 88, { scale: pop(0.2, 0.7) });
    const s3 = pop(E.title2, 0.7);
    if (s3 > 0) { c.save(); c.translate(540, 575 + yo); c.rotate(-0.03); c.scale(s3, s3); fillP(c, ACC, cc => rr(cc, -400, -64, 800, 128, 24), 1.2); c.restore(); bigText(c, 'pernah terfikir tak?', 540, 575 + yo, 88, { scale: s3, rot: -0.03, stroke: '#7A2A12' }); }
    c.restore();
  }
  if (b < E.toPack + 1) bigText(c, 'lesap jadi asap...', 540, 760, 84, { scale: life(E.asap, E.toPack - 0.3, 0.6, 0.4), fill: '#E9E6EE', stroke: '#5A5466' });
  const tp = life(E.tapi, E.tapi + 2.4, 0.5, 0.5);
  if (tp > 0) bigText(c, 'TAPI...', 540 + Math.sin(b * 40) * 4 * (1 - P(E.tapi, E.tapi + 1.5)), 560, 170, { scale: tp, stroke: '#1C2033' });
  const t41 = life(E.y41, E.quit - 0.5, 0.45, 0.4);
  if (t41 > 0) { c.save(); c.translate(540, 1150); c.rotate(-0.08); c.scale(t41, t41); c.font = "800 130px 'Baloo 2'"; const w = c.measureText('41 TAHUN').width + 90; c.fillStyle = 'rgba(255,248,236,0.95)'; c.beginPath(); rr(c, -w / 2, -95, w, 190, 20); c.fill(); c.strokeStyle = RED; c.lineWidth = 12; c.beginPath(); rr(c, -w / 2 + 12, -83, w - 24, 166, 14); c.stroke(); c.fillStyle = RED; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('41 TAHUN', 0, 10); c.restore(); }
}
function ctaOutro(c) {
  const b = S.B; if (b < E.cta - 0.3) return;
  const p = out3(P(E.cta - 0.2, E.cta + 0.9));
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
  c.beginPath(); c.arc(540, 960, p * 1200, 0, 7); c.clip();
  c.fillStyle = ACC; c.fillRect(0, 0, W, H);
  c.globalAlpha = 0.12; c.fillStyle = CREAM;
  for (let i = 0; i < 18; i++) { c.beginPath(); c.arc(rnd(i) * W, rnd(i + 30) * H, 40 + rnd(i + 3) * 120, 0, 7); c.fill(); }
  c.globalAlpha = 1; S.ZK = 1;
  label(c, 'SEBAB APA?', 540, 200, { scale: pop(E.cta + 0.2, 0.6), size: 40, bg: CREAM, fg: ACC });
  host(c, 540, 1000, 0.74 * pop(E.cta + 0.2, 0.8), { pose: 'wave' });
  bigText(c, 'Komen "NAK"', 540, 1130, 130, { scale: pop(E.cta + 0.5, 0.7), stroke: '#7A2A12' });
  label(c, 'saya DM korang', 540, 1270, { scale: pop(E.cta + 1.0, 0.6), size: 52, bg: CREAM });
  label(c, 'Civic FL5 · 2025 · RM270,000', 540, 1390, { scale: pop(E.cta + 1.5, 0.6), size: 38, bg: INK, fg: CREAM });
  c.restore();
}
function drawCaptions(c) {
  const t = S.B * BEAT; if (S.B > E.cta - 0.3) return;
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
  if (sees(v, -900, -400, 1150, 2200)) zoneKedai(c);
  if (sees(v, 1150, -400, 2550, 2200)) zoneKalendar(c);
  if (sees(v, 2550, -400, 3950, 2200)) zoneTabung(c);
  if (sees(v, -900, 2200, 1150, 5000)) zoneMenara(c);
  if (sees(v, 1150, 2200, 2550, 5000)) zoneTahun(c);
  if (sees(v, 2550, 2200, 3950, 5000)) zoneJalan(c);
}
async function renderFrame(t) {
  const b = t / BEAT; S.B = b;
  const cam = camAt(CAM, b);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (b < E.foot + 1) {
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
  }
  await drawFootage(ctx);
  drawCaptions(ctx);
  ctaOutro(ctx);
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
  await renderFrame(0);
  return true;
})();
window.renderFrame = renderFrame;
