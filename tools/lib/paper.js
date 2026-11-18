// paper.js — perpustakaan lukisan gaya "potongan kertas" untuk siri Sebab Apa?
// Semua masa dalam unit BEAT (bukan saat). Set PAPER.B sebelum melukis setiap frame.
'use strict';
const PAPER = (() => {
  const W = 1080, H = 1920;
  const S = { B: 0, ZK: 1 }; // B = beat semasa, ZK = zum kamera semasa (untuk skala bayang)

  // ---------------------------------------------------------------- math
  const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
  const lerp = (a, b, t) => a + (b - a) * t;
  const inOut = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const inOut5 = t => (t < 0.5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2);
  const out3 = t => 1 - Math.pow(1 - t, 3);
  const in3 = t => t * t * t;
  const back = t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
  const P = (b0, b1) => clamp((S.B - b0) / (b1 - b0));
  const pop = (b0, d = 0.7) => { const p = P(b0, b0 + d); return p <= 0 ? 0 : back(p); };
  const life = (b0, b1, din = 0.7, dout = 0.5) => { // skala pop masuk & keluar
    if (S.B < b0 || S.B > b1 + dout) return 0;
    const pin = pop(b0, din);
    const po = 1 - in3(P(b1, b1 + dout));
    return pin * po;
  };
  const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const hex = c => { c = c.replace('#', ''); return [0, 2, 4].map(i => parseInt(c.slice(i, i + 2), 16)); };
  const mix = (a, b, t) => { const A = hex(a), Bc = hex(b); t = clamp(t); return `rgb(${A.map((v, i) => Math.round(lerp(v, Bc[i], t))).join(',')})`; };

  // ---------------------------------------------------------------- kertas
  function shadow(c, on = true, k = 1) {
    if (on) { c.shadowColor = 'rgba(35,18,24,0.32)'; c.shadowBlur = 16 * k * S.ZK; c.shadowOffsetX = 0; c.shadowOffsetY = 7 * k * S.ZK; }
    else { c.shadowColor = 'transparent'; c.shadowBlur = 0; c.shadowOffsetY = 0; }
  }
  function fillP(c, color, pathFn, k = 1) {
    c.save(); shadow(c, k > 0, k); c.fillStyle = color; c.beginPath(); pathFn(c); c.fill(); c.restore();
  }
  function rr(c, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath();
  }
  let grainPat = null;
  function grain(c, alpha = 0.07) {
    if (!grainPat) {
      const g = document.createElement('canvas'); g.width = g.height = 384;
      const gx = g.getContext('2d'); const id = gx.createImageData(384, 384);
      for (let i = 0; i < id.data.length; i += 4) {
        const v = 128 + (Math.random() - 0.5) * 255 * 0.9;
        id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255;
      }
      gx.putImageData(id, 0, 0);
      // gentian kertas
      gx.globalAlpha = 0.08; gx.strokeStyle = '#fff';
      for (let i = 0; i < 260; i++) { gx.lineWidth = Math.random() * 1.5; gx.beginPath(); const x = Math.random() * 384, y = Math.random() * 384, a = Math.random() * 6.28, l = 6 + Math.random() * 22; gx.moveTo(x, y); gx.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); gx.stroke(); }
      grainPat = c.createPattern(g, 'repeat');
    }
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
    c.globalCompositeOperation = 'overlay'; c.globalAlpha = alpha; c.fillStyle = grainPat; c.fillRect(0, 0, W, H);
    c.restore();
  }
  function vignette(c, k = 0.38) {
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
    const g = c.createRadialGradient(W / 2, H / 2, H * 0.32, W / 2, H / 2, H * 0.75);
    g.addColorStop(0, 'rgba(20,10,20,0)'); g.addColorStop(1, `rgba(20,10,20,${k})`);
    c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
  }

  // ---------------------------------------------------------------- teks
  const FT = "800 {s}px 'Baloo 2'", FC = "900 {s}px Nunito";
  const font = (f, s) => f.replace('{s}', Math.round(s));
  function label(c, text, x, y, o = {}) {
    const sc = o.scale === undefined ? 1 : o.scale; if (sc <= 0.001) return;
    const size = o.size || 44;
    c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(sc, sc);
    c.font = font(o.font || FT, size);
    const w = c.measureText(text).width, padX = size * 0.5, padY = size * 0.22;
    const bw = w + padX * 2, bh = size * 1.15 + padY;
    if (o.arrow) fillP(c, o.bg || '#FFF4E0', cc => { cc.moveTo(-18, bh / 2 - 2); cc.lineTo(18, bh / 2 - 2); cc.lineTo(0, bh / 2 + 26); }, 0.6);
    fillP(c, o.bg || '#FFF4E0', cc => rr(cc, -bw / 2, -bh / 2, bw, bh, o.radius === undefined ? bh / 2 : o.radius), o.sh === undefined ? 1 : o.sh);
    c.fillStyle = o.fg || '#2B2024'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(text, 0, size * 0.08);
    c.restore();
  }
  function bigText(c, text, x, y, size, o = {}) {
    c.save(); c.translate(x, y); c.rotate(o.rot || 0); const sc = o.scale === undefined ? 1 : o.scale; c.scale(sc, sc);
    c.font = font(o.font || FT, size); c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
    c.lineJoin = 'round';
    if (o.shadow !== false) { shadow(c, true, 1.2); }
    c.lineWidth = o.strokeW || size * 0.16; c.strokeStyle = o.stroke || '#2B2024'; c.strokeText(text, 0, 0);
    shadow(c, false); c.fillStyle = o.fill || '#FFF4E0'; c.fillText(text, 0, 0);
    c.restore();
  }
  // kapsyen: segs = [{t, hl}]
  function caption(c, segs, cx, cy, o = {}) {
    const size = o.size || 58, maxW = o.maxW || 900, hlc = o.hl || '#FF7A3D';
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
    c.font = font(FC, size);
    // pecah kepada perkataan sambil kekalkan warna
    const words = [];
    segs.forEach(s => s.t.split(/(\s+)/).forEach(w => { if (w.trim()) words.push({ w, hl: s.hl }); }));
    const space = c.measureText(' ').width;
    const lines = [[]]; let lw = 0;
    words.forEach(wd => {
      const ww = c.measureText(wd.w).width;
      if (lw > 0 && lw + space + ww > maxW) { lines.push([]); lw = 0; }
      lines[lines.length - 1].push({ ...wd, ww }); lw += (lw > 0 ? space : 0) + ww;
    });
    const lh = size * 1.22;
    const widths = lines.map(l => l.reduce((a, w, i) => a + w.ww + (i ? space : 0), 0));
    const bw = Math.max(...widths) + size * 0.9, bh = lines.length * lh + size * 0.45;
    const sc = o.scale === undefined ? 1 : o.scale;
    c.translate(cx, cy); c.scale(sc, sc); c.globalAlpha = o.alpha === undefined ? 1 : o.alpha;
    c.save(); shadow(c, true, 1); c.fillStyle = 'rgba(30,20,30,0.84)'; c.beginPath(); rr(c, -bw / 2, -bh / 2, bw, bh, 26); c.fill(); c.restore();
    c.textBaseline = 'middle'; c.textAlign = 'left';
    lines.forEach((l, li) => {
      let x = -widths[li] / 2; const y = -bh / 2 + size * 0.225 + lh * (li + 0.5) + size * 0.04;
      l.forEach(wd => { c.fillStyle = wd.hl ? hlc : '#FFF8EC'; c.fillText(wd.w, x, y); x += wd.ww + space; });
    });
    c.restore();
  }

  // ---------------------------------------------------------------- kamera
  // keys: [{b0,b1,x,y,z,whip}] — peralihan dari keadaan sebelumnya ke sasaran dalam [b0,b1]
  function camAt(keys, b) {
    let st = { x: keys[0].x, y: keys[0].y, z: keys[0].z }; let whip = 0;
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i]; if (b <= k.b0) break;
      const p = clamp((b - k.b0) / (k.b1 - k.b0));
      const e = k.whip ? inOut5(p) : (k.ease === 'lin' ? p : inOut(p));
      st = { x: lerp(st.x, k.x, e), y: lerp(st.y, k.y, e), z: lerp(st.z, k.z, e) };
      if (k.whip && p > 0 && p < 1) whip = 1;
    }
    return { ...st, whip };
  }
  function applyCam(c, cam) { c.setTransform(cam.z, 0, 0, cam.z, W / 2 - cam.x * cam.z, H / 2 - cam.y * cam.z); S.ZK = cam.z; }
  function viewRect(cam) { const hw = W / 2 / cam.z, hh = H / 2 / cam.z; return { x0: cam.x - hw, x1: cam.x + hw, y0: cam.y - hh, y1: cam.y + hh }; }
  const sees = (v, x0, y0, x1, y1) => !(x1 < v.x0 || x0 > v.x1 || y1 < v.y0 || y0 > v.y1);
  function toScreen(cam, x, y) { return [W / 2 + (x - cam.x) * cam.z, H / 2 + (y - cam.y) * cam.z]; }

  // ---------------------------------------------------------------- watak: cicak (maskot siri)
  function cicak(c, x, y, s, rot = 0, o = {}) {
    const b = S.B;
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s);
    const body = '#D9C291', dark = '#B79C66';
    c.lineCap = 'round'; c.lineJoin = 'round';
    // ekor
    c.save(); shadow(c, true, 0.6);
    const tw = Math.sin(b * Math.PI * 0.5) * 14;
    c.strokeStyle = body;
    for (let i = 0; i < 3; i++) { c.lineWidth = 18 - i * 5; c.beginPath(); c.moveTo(0, 40); c.quadraticCurveTo(34 + tw, 105, -6 - tw * 0.5, 150 + i * 6); c.stroke(); }
    // kaki
    c.lineWidth = 10; c.strokeStyle = body;
    const legs = [[-16, -26, -50, -48], [16, -26, 50, -48], [-15, 26, -48, 48], [15, 26, 48, 48]];
    legs.forEach(([a, bb, cx, cy]) => { c.beginPath(); c.moveTo(a, bb); c.lineTo(cx, cy); c.stroke(); });
    c.restore();
    c.fillStyle = body;
    legs.forEach(([, , cx, cy]) => { for (let k = -1; k <= 1; k++) { c.beginPath(); c.arc(cx + k * 7 * Math.sign(cx), cy + k * 6 * Math.sign(cy) * -1, 5.5, 0, 7); c.fill(); } });
    // badan & kepala
    fillP(c, body, cc => cc.ellipse(0, 4, 27, 52, 0, 0, 7), 0.8);
    fillP(c, body, cc => cc.ellipse(0, -60, 31, 29, 0, 0, 7), 0.8);
    c.fillStyle = dark; [[-8, -8, 5], [9, 6, 4], [-6, 22, 4], [7, 34, 3]].forEach(([a, bb, r]) => { c.beginPath(); c.arc(a, bb, r, 0, 7); c.fill(); });
    // mata
    const blink = (o.blink !== false) && ((b + 1.3) % 6 < 0.18);
    const wink = o.wink || 0;
    [[-17, -70], [17, -70]].forEach(([ex, ey], i) => {
      const closed = blink || (i === 1 && wink > 0.5);
      if (closed) { c.strokeStyle = '#2B2024'; c.lineWidth = 5; c.beginPath(); c.arc(ex, ey + 2, 10, Math.PI * 0.15, Math.PI * 0.85); c.stroke(); }
      else {
        c.fillStyle = '#2B2024'; c.beginPath(); c.arc(ex, ey, 12, 0, 7); c.fill();
        c.fillStyle = '#fff'; c.beginPath(); c.arc(ex - 4, ey - 4, 4.5, 0, 7); c.fill();
      }
    });
    // senyum
    c.strokeStyle = '#2B2024'; c.lineWidth = 4; c.beginPath(); c.arc(0, -52, 11, Math.PI * 0.15, Math.PI * 0.85); c.stroke();
    c.restore();
  }

  // ---------------------------------------------------------------- watak: orang
  function person(c, x, y, s, o = {}) {
    const skin = o.skin || '#C98B5E', shirt = o.shirt || '#2E86AB', pants = o.pants || '#3A3048', hair = o.hair || '#2B2024';
    const run = o.run || 0, ph = o.phase || 0, pinch = o.pinch || 0;
    c.save(); c.translate(x, y + (run ? -Math.abs(Math.sin(ph)) * 10 : 0)); c.scale(s * (o.flip ? -1 : 1), s);
    if (o.lean) c.rotate(o.lean);
    c.lineCap = 'round';
    // kaki
    c.save(); shadow(c, true, 0.6); c.strokeStyle = pants; c.lineWidth = 24;
    const la = Math.sin(ph) * 0.7 * run;
    [la, -la].forEach(a => { c.save(); c.translate(0, -92); c.rotate(a); c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 86); c.stroke(); c.restore(); });
    c.restore();
    // badan
    fillP(c, shirt, cc => rr(cc, -40, -215, 80, 130, 32), 1);
    // lengan
    c.strokeStyle = skin; c.lineWidth = 17;
    const sw = Math.sin(ph) * 0.8 * run;
    // lengan belakang
    c.beginPath(); c.moveTo(-26, -190); c.lineTo(-30 - sw * 30, -120); c.stroke();
    // lengan hadapan (picit hidung)
    if (pinch > 0) {
      const hx = lerp(30 + sw * 30, 30, pinch), hy = lerp(-120, -248, pinch);
      c.beginPath(); c.moveTo(26, -190); c.quadraticCurveTo(lerp(34, 58, pinch), lerp(-160, -200, pinch), hx, hy); c.stroke();
      c.fillStyle = skin; c.beginPath(); c.arc(hx, hy, 11, 0, 7); c.fill();
    } else { c.beginPath(); c.moveTo(26, -190); c.lineTo(30 + sw * 30, -120); c.stroke(); }
    // kepala
    fillP(c, skin, cc => cc.arc(0, -255, 46, 0, 7), 1);
    c.fillStyle = hair;
    if (o.cap) { c.fillStyle = o.cap; c.beginPath(); c.arc(0, -262, 47, Math.PI, 0); c.fill(); c.fillRect(0, -268, 64, 12); }
    else if (o.longHair) { c.beginPath(); c.arc(0, -262, 49, Math.PI * 0.95, Math.PI * 2.05); c.fill(); c.fillRect(-49, -262, 22, 60); }
    else if (o.tudung) { c.fillStyle = o.tudung; c.beginPath(); c.arc(0, -258, 54, Math.PI * 0.85, Math.PI * 2.15); c.lineTo(42, -195); c.lineTo(-42, -195); c.closePath(); c.fill(); }
    else { c.beginPath(); c.arc(0, -264, 46, Math.PI * 1.02, Math.PI * 1.98); c.fill(); }
    if (o.tudung) { c.fillStyle = skin; c.beginPath(); c.ellipse(10, -250, 33, 38, 0, 0, 7); c.fill(); }
    // muka (pandang ke +x)
    c.fillStyle = '#2B2024'; c.strokeStyle = '#2B2024'; c.lineWidth = 4.5;
    if (o.disgust) {
      [[2, -262], [26, -262]].forEach(([ex, ey]) => { c.beginPath(); c.moveTo(ex - 7, ey - 6); c.lineTo(ex + 3, ey); c.lineTo(ex - 7, ey + 6); c.stroke(); });
      c.beginPath(); c.moveTo(2, -230); for (let i = 0; i < 4; i++) c.lineTo(8 + i * 6, -230 + (i % 2 ? -5 : 4)); c.stroke();
    } else {
      [[4, -262], [28, -262]].forEach(([ex, ey]) => { c.beginPath(); c.arc(ex, ey, 5.5, 0, 7); c.fill(); });
      c.beginPath(); c.arc(17, -240, 11, Math.PI * 0.15, Math.PI * 0.85); c.stroke();
    }
    c.fillStyle = 'rgba(255,120,120,0.35)'; c.beginPath(); c.arc(36, -244, 7, 0, 7); c.fill();
    c.restore();
  }


  // ---------------------------------------------------------------- watak: HOS (muka sebenar + badan kartun)
  let HEAD = null, HEADM = null;
  function setHostHead(img, meta) { HEAD = img; HEADM = meta; }
  function headSticker(c, x, y, hs, rot = 0) { // (x,y) = titik leher
    if (!HEAD) return;
    c.save(); c.translate(x, y); c.rotate(rot);
    shadow(c, true, 0.8);
    c.drawImage(HEAD, -HEADM.neckX * hs, -HEADM.neckY * hs, HEADM.w * hs, HEADM.h * hs);
    c.restore();
  }
  function limb(c, x, y, a1, l1, a2, l2, w, col, sleeve, sleeveCol, hand) {
    const ex = x + Math.sin(a1) * l1, ey = y + Math.cos(a1) * l1;
    const hx = ex + Math.sin(a2) * l2, hy = ey + Math.cos(a2) * l2;
    c.strokeStyle = col; c.lineWidth = w;
    c.beginPath(); c.moveTo(x, y); c.lineTo(ex, ey); c.lineTo(hx, hy); c.stroke();
    if (sleeve) { c.strokeStyle = sleeveCol; c.lineWidth = w + 18; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.sin(a1) * sleeve, y + Math.cos(a1) * sleeve); c.stroke(); }
    if (hand) { c.fillStyle = hand; c.beginPath(); c.arc(hx, hy, w * 0.72, 0, 7); c.fill(); }
    return [ex, ey, hx, hy];
  }
  function host(c, x, y, s, o = {}) {
    if (s <= 0.001) return;
    const b = S.B, pose = o.pose || 'stand';
    const skin = '#B47C55', shirt = '#F8F4EA', shirtD = '#DCD5C6', pants = '#D9D0C0', pantsD = '#BDB2A0', ink = '#2B2024';
    c.save(); c.translate(x, y); c.scale(s * (o.flip ? -1 : 1), s);
    c.lineCap = 'round'; c.lineJoin = 'round';
    const bob = pose === 'sit' ? 0 : -Math.abs(Math.sin(b * Math.PI)) * 10;
    c.translate(0, bob);
    const sit = pose === 'sit';
    const hipY = sit ? -230 : -270, neckY = hipY - 245;
    // ---- kaki
    c.save(); shadow(c, true, 0.7);
    [-1, 1].forEach(sd => {
      const sw = sit ? Math.sin(b * Math.PI + sd) * 0.25 : 0;
      const hx = sd * 40, fx = sit ? sd * 60 : sd * 46;
      const fy = sit ? hipY + 210 : 0;
      c.strokeStyle = pants; c.lineWidth = 66;
      if (sit) { c.beginPath(); c.moveTo(hx, hipY); c.lineTo(sd * 55, hipY + 20); c.lineTo(fx + Math.sin(sw) * 60, fy); c.stroke(); }
      else { c.beginPath(); c.moveTo(hx, hipY); c.lineTo(fx, fy - 70); c.stroke(); }
      // stokin corak
      const sx = sit ? fx + Math.sin(sw) * 60 : fx, sy = sit ? fy : fy - 70;
      c.save(); c.translate(sx, sy); if (sit) c.rotate(-Math.sin(sw) * 0.6);
      c.fillStyle = '#1F1F24'; c.beginPath(); rr(c, -27, -6, 54, 74, 14); c.fill();
      c.strokeStyle = '#F2EEE6'; c.lineWidth = 5;
      for (let k = 0; k < 3; k++) { c.beginPath(); for (let i = 0; i <= 4; i++) c.lineTo(-22 + i * 11, 6 + k * 18 + (i % 2 ? 8 : 0)); c.stroke(); }
      c.fillStyle = '#1F1F24'; c.beginPath(); c.ellipse(sd * 10, 70, 40, 18, 0, 0, 7); c.fill();
      c.restore();
    });
    c.restore();
    // ---- badan (kemeja)
    fillP(c, shirt, cc => { cc.moveTo(-104, neckY + 26); cc.quadraticCurveTo(-118, neckY + 40, -110, neckY + 90); cc.lineTo(-96, hipY + 22); cc.lineTo(96, hipY + 22); cc.lineTo(110, neckY + 90); cc.quadraticCurveTo(118, neckY + 40, 104, neckY + 26); cc.closePath(); }, 1);
    c.strokeStyle = shirtD; c.lineWidth = 4; c.beginPath(); c.moveTo(0, neckY + 30); c.lineTo(0, hipY + 20); c.stroke();
    c.fillStyle = shirtD; for (let k = 0; k < 4; k++) { c.beginPath(); c.arc(7, neckY + 70 + k * 46, 4.5, 0, 7); c.fill(); }
    c.strokeStyle = shirtD; c.lineWidth = 3.5; c.beginPath(); rr(c, 30, neckY + 80, 50, 54, 6); c.stroke();
    // leher + kolar
    c.fillStyle = skin; c.beginPath(); c.moveTo(-30, neckY - 8); c.lineTo(30, neckY - 8); c.lineTo(22, neckY + 40); c.lineTo(-22, neckY + 40); c.fill();
    fillP(c, '#FFFFFF', cc => { cc.moveTo(-6, neckY + 44); cc.lineTo(-52, neckY + 6); cc.lineTo(-30, neckY - 6); cc.closePath(); cc.moveTo(6, neckY + 44); cc.lineTo(52, neckY + 6); cc.lineTo(30, neckY - 6); cc.closePath(); }, 0.4);
    // ---- lengan
    const beatW = Math.sin(b * Math.PI * 2);
    // sudut: 0 = ke bawah, positif = ke luar badan (kedua-dua belah)
    let L = [0.2 + 0.03 * beatW, 0.1], R = [0.2 - 0.03 * beatW, 0.1];
    if (pose === 'wave') R = [2.25, 2.55 + 0.4 * beatW];
    if (pose === 'point') R = [1.45, 1.6];
    if (pose === 'pointUp') R = [2.2, 2.7];
    if (pose === 'sit') { L = [0.35, -0.6]; R = [0.35, -0.6]; }
    if (pose === 'cheer') { L = [2.5 + 0.15 * beatW, 3.0]; R = [2.5 - 0.15 * beatW, 3.0]; }
    c.save(); shadow(c, true, 0.6);
    const sl = limb(c, -100, neckY + 34, -L[0], 108, -L[1], 100, 34, skin, 62, shirt, skin);
    // jam tangan kiri
    c.fillStyle = '#1F1F24'; const wx = lerp(sl[0], sl[2], 0.78), wy = lerp(sl[1], sl[3], 0.78); c.beginPath(); c.arc(wx, wy, 14, 0, 7); c.fill(); c.fillStyle = '#C9CED6'; c.beginPath(); c.arc(wx, wy, 8, 0, 7); c.fill();
    limb(c, 100, neckY + 34, R[0], 108, R[1], 100, 34, skin, 62, shirt, skin);
    c.restore();
    // ---- kepala (muka sebenar)
    const tilt = (o.tilt || 0) + Math.sin(b * Math.PI * 0.5) * 0.05;
    const hs = o.headScale || 0.95;
    headSticker(c, 0, neckY + 22, hs, tilt);
    c.restore();
  }
  // kepala mengintai dari tepi objek + satu tangan
  function hostPeek(c, x, y, s, rot = 0) {
    if (s <= 0.001 || !HEAD) return;
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s);
    const t = Math.sin(S.B * Math.PI * 0.5) * 0.06;
    headSticker(c, 0, 0, 0.82, t);
    c.fillStyle = '#B47C55'; shadow(c, true, 0.5);
    c.beginPath(); c.ellipse(120, 10, 30, 26, 0, 0, 7); c.fill();
    c.restore();
  }

  // gelombang bau (garisan beralun yang mengalir)
  function wavyPath(c, x0, y0, x1, y1, amp, freq, phase, reveal) {
    const n = 48, dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy), nx = -dy / len, ny = dx / len;
    c.beginPath();
    for (let i = 0; i <= n * reveal; i++) {
      const t = i / n, w = Math.sin(t * freq * Math.PI * 2 + phase) * amp * Math.sin(Math.min(1, t * 3) * Math.PI / 2);
      const px = x0 + dx * t + nx * w, py = y0 + dy * t + ny * w;
      i ? c.lineTo(px, py) : c.moveTo(px, py);
    }
  }
  function smell(c, x0, y0, x1, y1, o = {}) {
    const reveal = o.reveal === undefined ? 1 : o.reveal; if (reveal <= 0) return;
    const k = o.k || 1, n = o.n || 3;
    c.save(); c.lineCap = 'round'; c.globalAlpha = o.alpha === undefined ? 0.9 : o.alpha;
    for (let j = 0; j < n; j++) {
      const off = (j - (n - 1) / 2) * 34 * k;
      c.strokeStyle = j % 2 ? '#C9E26B' : '#A9CF4A'; c.lineWidth = 11 * k;
      c.setLineDash([46 * k, 24 * k]); c.lineDashOffset = -S.B * 46 * k * (o.speed || 1) + j * 20;
      wavyPath(c, x0, y0 + off * 0.4, x1, y1 + off, 16 * k, 2.2 + j * 0.4, S.B * 2.6 + j * 1.7, reveal);
      c.stroke();
    }
    c.restore();
  }

  return { W, H, S, clamp, lerp, inOut, inOut5, out3, in3, back, P, pop, life, rnd, mix, shadow, fillP, rr, grain, vignette,
    FT, FC, font, label, bigText, caption, camAt, applyCam, viewRect, sees, toScreen, cicak, person, smell, wavyPath, setHostHead, host, hostPeek, headSticker };
})();
