// Serves scene.html, steps window.renderAt(t) frame by frame, pipes JPEG frames to ffmpeg.
// usage: node render3d.js out.mp4 [fps] [only_t1,t2,... -> writes PNG stills instead]
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const { chromium } = require('playwright');
const root = __dirname;
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f)) return r.writeHead(404).end(); r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); });
(async () => {
  await new Promise(r => srv.listen(0, r)); const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await p.goto(`http://127.0.0.1:${port}/scene.html`); await p.waitForFunction('window.ready === true', { timeout: 120000 });
  const out = process.argv[2], fps = +(process.argv[3] || 30), stills = process.argv[4];
  if (stills) {
    for (const t of stills.split(',').map(Number)) { await p.evaluate(t => window.renderAt(t), t); await p.screenshot({ path: `${out}/s_${t.toFixed(2)}.png` }); }
  } else {
    const dur = await p.evaluate('window.DURATION'); const n = Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => window.renderAt(t), i / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close(); srv.close();
})().catch(e => { console.error('FAILED', e); process.exit(1); });
