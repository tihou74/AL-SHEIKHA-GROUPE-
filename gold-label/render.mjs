import { chromium } from 'playwright-core';
import fs from 'node:fs';

const EXE  = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const BASE = 'file:///projects/sandbox/alsheikha-gold-label/index.html';
const OUT  = '/projects/sandbox/alsheikha-gold-label/previews';
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
const errors = [];

async function shot(file, params, { scale = 1.5, w = 1600, h = 640, transparent = false, fullPage = false } = {}) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  page.on('pageerror', e => errors.push(file + ' :: ' + e.message));
  await page.goto(BASE + '?' + params);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${OUT}/${file}`, omitBackground: transparent, fullPage });
  await page.close();
  console.log('✔', file);
}

const golds = ['f-cormorant','f-cinzel','f-italiana','f-playfair','f-marcellus','f-bodoni',
               'f-bodoni-up','f-prata','f-gilda','f-forum','f-antic','f-tenor','f-bellefair',
               'f-ebgaramond','f-pinyon','f-vibes'];
const glitters = ['gl-med','gl-coarse','gl-rough','gl-fine','gl-off'];
const frames   = ['double','simple','corners','rules','filled','none'];
const ars      = ['a-ruqaa','a-nastaliq','a-katibeh','a-rakkas','a-ruqaaink','a-mirza','a-gulzar',
                  'a-amiri','a-messiri','a-reem'];

// ═══ أوراق المقارنة ═══
await shot('00-sheet-gold-fonts.png', 'sheet=gold',    { scale: 1, w: 1240, h: 8600, fullPage: true });
await shot('01-sheet-glitter.png',    'sheet=glitter', { scale: 1, w: 1240, h: 2700, fullPage: true });
await shot('02-sheet-frames.png',     'sheet=frame',   { scale: 1, w: 1240, h: 3300, fullPage: true });
await shot('03-sheet-arabic.png',     'sheet=arabic',  { scale: 1, w: 1240, h: 5400, fullPage: true });

// ═══ القليتشر: كل درجة لوحدها بحجم كبير ═══
let i = 10;
for (const g of glitters) {
  await shot(`${i}-glitter-${g.replace('gl-','')}.png`, `plain=1&glitter=${g}`, { scale: 2 });
  i++;
}

// ═══ كل خط GOLD لوحده (بالقليتشر المتوسط) ═══
i = 20;
for (const g of golds) {
  await shot(`${i}-gold-${g.replace('f-','')}.png`, `plain=1&gold=${g}&glitter=gl-coarse`);
  i++;
}

// ═══ أشكال الإطار ═══
i = 40;
for (const f of frames) {
  await shot(`${i}-frame-${f}.png`, `plain=1&frame=${f}&glitter=gl-coarse`);
  i++;
}

// ═══ خطوط الاسم العربي ═══
i = 50;
for (const a of ars) {
  await shot(`${i}-ar-${a.replace('a-','')}.png`, `plain=1&ar=${a}&glitter=gl-coarse`);
  i++;
}

// ═══ خلفيات ═══
await shot('70-black.png',       'plain=1&glitter=gl-coarse&bg=%230C0B0A', { scale: 2 });
await shot('71-transparent.png', 'plain=1&glitter=gl-coarse&bg=transparent', { scale: 2, transparent: true });
await shot('72-ar-glitter-too.png', 'plain=1&glitter=gl-coarse&arglitter=1', { scale: 2 });

await browser.close();
console.log(errors.length ? '\n⚠ ERRORS:\n' + errors.join('\n') : '\nno page errors ✓');
