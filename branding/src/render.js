const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
(async () => { const b = await chromium.launch(); const [,, input, out, scale] = process.argv;
  const p = await b.newPage({deviceScaleFactor: +(scale||1)});
  const html = input.endsWith('.svg') ? `<html><body style="margin:0;background:${input.includes('white')?'#0A1A33':'#fff'}">${fs.readFileSync(input,'utf8')}</body></html>` : null;
  if (html) await p.setContent(html); else await p.goto('file://'+path.resolve(input));
  await p.waitForTimeout(400);
  const el = await p.$(html ? 'svg' : '#stage'); await el.screenshot({path: out, omitBackground: !!html && !input.includes('white')});
  await b.close(); })();
