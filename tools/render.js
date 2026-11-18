// Render scene.html -> MP4 (atau still PNG untuk semakan).
//   node tools/render.js projects/durian video            -> build/video.mp4 (tanpa audio)
//   node tools/render.js projects/durian stills 0 9 17 ... -> build/stills/b<beat>.png
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const proj = process.argv[2] || 'projects/durian';
const mode = process.argv[3] || 'video';
const extra = process.argv.slice(4);

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.png': 'image/png' };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/${proj}/scene.html`);
  await page.evaluate(() => window.ready);
  const tl = JSON.parse(fs.readFileSync(path.join(ROOT, proj, 'timeline.json')));
  const beat = 60 / tl.bpm, fps = tl.fps;
  const outDir = path.join(ROOT, proj, 'build');
  fs.mkdirSync(outDir, { recursive: true });

  const grab = (t, q) => page.evaluate(([t, q]) => { window.renderFrame(t); return document.getElementById('c').toDataURL(q ? 'image/jpeg' : 'image/png', q || undefined); }, [t, q]);

  if (mode === 'stills') {
    const sd = path.join(outDir, 'stills'); fs.mkdirSync(sd, { recursive: true });
    for (const b of extra) {
      const url = await grab(parseFloat(b) * beat, 0.9);
      fs.writeFileSync(path.join(sd, `b${String(b).padStart(5, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
    }
    console.log('stills ->', sd);
  } else {
    const dur = await page.evaluate(() => window.DURATION);
    const total = Math.round(dur * fps);
    const out = path.join(outDir, 'video.mp4');
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = 0; f < total; f++) {
      const url = await grab(f / fps, 0.94);
      const buf = Buffer.from(url.split(',')[1], 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 150 === 0) console.log(`frame ${f}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('video ->', out);
  }
  await browser.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
