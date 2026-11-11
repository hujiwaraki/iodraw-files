// Real-browser playback check: loads the MP4 in Chromium <video>, plays at start/middle/end,
// verifies time advances, frames + audio bytes are decoded, and screenshots each point.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const file = path.resolve(process.argv[2]); const out = process.argv[3];
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await p.setContent(`<html><body style="margin:0;background:#000"><video id=v src="file://${file}" style="width:1280px;height:720px" preload=auto></video></body></html>`);
  const info = await p.evaluate(() => new Promise((res, rej) => {
    const v = document.getElementById('v');
    v.onloadedmetadata = () => res({ duration: v.duration, w: v.videoWidth, h: v.videoHeight });
    v.onerror = () => rej('media error ' + (v.error && v.error.code));
    setTimeout(() => rej('timeout'), 20000);
  }));
  console.log('metadata', JSON.stringify(info));
  for (const [label, t] of [['start', 0.3], ['middle', 47.0], ['end', info.duration - 4.5]]) {
    const r = await p.evaluate(async (t) => {
      const v = document.getElementById('v'); v.currentTime = t;
      await new Promise(r => v.onseeked = r);
      const a0 = v.webkitAudioDecodedByteCount, f0 = v.webkitVideoDecodedFrameCount;
      await v.play(); await new Promise(r => setTimeout(r, 2500)); v.pause();
      return { from: t, to: v.currentTime, frames: v.webkitVideoDecodedFrameCount - f0, audioBytes: v.webkitAudioDecodedByteCount - a0, muted: v.muted, err: v.error };
    }, t);
    console.log(label, JSON.stringify(r));
    await p.screenshot({ path: `${out}/play_${label}.png` });
  }
  // play through the last seconds to confirm it reaches the end cleanly
  const endr = await p.evaluate(async () => {
    const v = document.getElementById('v'); v.currentTime = v.duration - 1.5; await new Promise(r => v.onseeked = r);
    await v.play(); await new Promise(r => { v.onended = r; setTimeout(r, 5000); });
    return { ended: v.ended, t: v.currentTime, d: v.duration };
  });
  console.log('end-of-file', JSON.stringify(endr));
  await b.close();
})().catch(e => { console.error('FAILED', e); process.exit(1); });
