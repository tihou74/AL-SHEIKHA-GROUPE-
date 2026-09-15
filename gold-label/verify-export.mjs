import { chromium } from 'playwright-core';
import fs from 'node:fs';
const EXE = '/opt/playwright/chromium-1232/chrome-linux64/chrome';

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
page.on('requestfailed', r => errs.push('REQFAIL ' + r.url().slice(0, 80)));

await page.goto('file:///projects/sandbox/alsheikha-gold-label/index.html?glitter=gl-rough&gold=f-cinzel');
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1200);

// نفس ما يفعله زر «تحميل PNG» بالضبط
const dataUrl = await page.evaluate(async () => {
  const label = document.getElementById('label');
  label.classList.remove('shine');
  const fontCss = document.getElementById('embedded-fonts');
  return window.htmlToImage.toPng(label, {
    pixelRatio: 2, width: 1600, height: 640, cacheBust: false,
    fontEmbedCSS: fontCss ? fontCss.textContent : '',
    backgroundColor: getComputedStyle(label).backgroundColor,
  });
});

const out = '/projects/sandbox/alsheikha-gold-label/previews/99-exported-by-button.png';
fs.writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
const { width, height } = await page.evaluate(async (u) => {
  const im = new Image(); im.src = u; await im.decode();
  return { width: im.naturalWidth, height: im.naturalHeight };
}, dataUrl);
console.log('exported PNG :', out);
console.log('dimensions   :', width, 'x', height);
console.log('bytes        :', fs.statSync(out).size);
console.log(errs.length ? 'ERRORS: ' + errs.join(' | ') : 'no errors ✓');
await browser.close();
