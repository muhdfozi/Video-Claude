// Render video/scene.html frame by frame with headless Chromium and pipe to ffmpeg.
//
//   node tools/render.mjs --preview            # 540x960, 15fps, fast draft
//   node tools/render.mjs                      # final 1080x1920 @ 30fps
//   node tools/render.mjs --stills 1.2,5,9.5   # PNG stills at given seconds
//
// Frames are split across workers; each worker encodes its own chunk, then
// the chunks are concatenated losslessly and muxed with build/mix.wav.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn, execFileSync } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };

const preview = flag('--preview');
const timeline = JSON.parse(fs.readFileSync(path.join(ROOT, 'build/timeline.json'), 'utf8'));
const W = preview ? 540 : 1080, H = preview ? 960 : 1920;
const FPS = Number(opt('--fps', preview ? 15 : 30));
const WORKERS = Number(opt('--workers', 3));
const out = opt('--out', path.join(ROOT, 'out', preview ? 'preview.mp4' : 'final.mp4'));

// Minimal static server (ES modules don't load from file://).
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.jpg': 'image/jpeg', '.png': 'image/png', '.wav': 'audio/wav' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/video/scene.html?w=${W}&h=${H}`;

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

async function openPage() {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('console', (m) => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(base);
  await page.waitForFunction(() => window.sceneReady === true, null, { timeout: 60000 });
  return page;
}

async function frame(page, t) {
  await page.evaluate((tt) => window.renderAt(tt), t);
  return page.screenshot({ type: 'jpeg', quality: preview ? 85 : 95 });
}

if (opt('--stills')) {
  const dir = path.join(ROOT, 'out', 'stills');
  fs.mkdirSync(dir, { recursive: true });
  const page = await openPage();
  for (const s of opt('--stills').split(',')) {
    await page.evaluate((tt) => window.renderAt(tt), Number(s));
    await page.screenshot({ path: path.join(dir, `t${Number(s).toFixed(2)}.png`) });
  }
  console.log('stills ->', dir);
  await browser.close(); server.close(); process.exit(0);
}

const t0 = Number(opt('--from', 0));
const t1 = Number(opt('--to', timeline.duration));
const total = Math.ceil((t1 - t0) * FPS);
fs.mkdirSync(path.dirname(out), { recursive: true });
const tmp = path.join(ROOT, 'build', 'chunks');
fs.rmSync(tmp, { recursive: true, force: true });
fs.mkdirSync(tmp, { recursive: true });

const per = Math.ceil(total / WORKERS);
const started = Date.now();
let done = 0;
await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
  const a = w * per, b = Math.min(total, a + per);
  if (a >= b) return;
  const page = await openPage();
  const file = path.join(tmp, `c${w}.mp4`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', preview ? 'veryfast' : 'slow', '-crf', preview ? '24' : '16',
    '-pix_fmt', 'yuv420p', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = a; i < b; i++) {
    const buf = await frame(page, t0 + i / FPS);
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    done++;
    if (done % 50 === 0) {
      const el = (Date.now() - started) / 1000;
      console.log(`${done}/${total} frames  ${el.toFixed(0)}s  eta ${(el / done * (total - done)).toFixed(0)}s`);
    }
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await page.close();
}));
await browser.close();
server.close();

const list = path.join(tmp, 'list.txt');
fs.writeFileSync(list, fs.readdirSync(tmp).filter((f) => f.endsWith('.mp4')).sort().map((f) => `file '${path.join(tmp, f)}'`).join('\n'));
const audio = path.join(ROOT, 'build', 'mix.wav');
const aArgs = fs.existsSync(audio) ? ['-ss', String(t0), '-t', String(t1 - t0), '-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, ...aArgs, '-c:v', 'copy', '-movflags', '+faststart', out]);
console.log(`done -> ${out}  (${((Date.now() - started) / 1000).toFixed(0)}s)`);
