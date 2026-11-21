// Muat sticker muka sebenar keluarga (assets/family, tidak dicommit) ke TOON.
async function loadFamily() {
  const conf = {
    ibu:    { width: 300, eyes: [[0.245, 0.395], [0.47, 0.385]] },
    baba:   { width: 225, eyes: [[0.25, 0.46], [0.60, 0.44]] },
    raysha: { width: 255, eyes: [[0.45, 0.52], [0.71, 0.52]] },
  };
  for (const [who, cf] of Object.entries(conf)) {
    const im = new Image(); im.src = `/assets/family/${who}.png`; await im.decode();
    const m = await (await fetch(`/assets/family/${who}.json`)).json();
    const sc = 520 / m.w, pad = 30, cv = document.createElement('canvas'); cv.width = Math.ceil(m.w * sc + pad * 2); cv.height = Math.ceil(m.h * sc + pad * 2);
    const x = cv.getContext('2d'); x.shadowColor = 'rgba(35,18,24,0.32)'; x.shadowBlur = 16; x.shadowOffsetY = 8; x.drawImage(im, pad, pad, m.w * sc, m.h * sc);
    cv.sc = sc; cv.pad = pad;
    TOON.setPhoto(who, { c: cv, m, eyes: cf.eyes, width: cf.width });
  }
}
