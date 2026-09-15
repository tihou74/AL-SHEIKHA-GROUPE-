import { chromium } from 'playwright-core';
import fs from 'node:fs';

const EXE  = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const BASE = 'file:///projects/sandbox/alsheikha-gold-label/index.html';
const OUT  = '/projects/sandbox/alsheikha-gold-label/final';
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
const errors = [];

async function png(file, params, { scale = 3, transparent = false } = {}) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 640 }, deviceScaleFactor: scale });
  page.on('pageerror', e => errors.push(file + ' :: ' + e.message));
  await page.goto(BASE + '?' + params);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/${file}`, omitBackground: transparent });
  await page.close();
  console.log('✔', file);
}

async function pdf(file, params, zoom = 2) {
  const page = await browser.newPage({ viewport: { width: 1600 * zoom, height: 640 * zoom }, deviceScaleFactor: 1 });
  page.on('pageerror', e => errors.push(file + ' :: ' + e.message));
  await page.goto(BASE + '?' + params + '&zoom=' + zoom);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1000);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: `${OUT}/${file}`, width: (1600 * zoom) + 'px', height: (640 * zoom) + 'px',
                   printBackground: true, margin: { top: '0', right: '0', bottom: '0', left: '0' } });
  await page.close();
  console.log('✔', file);
}

// النسخة الموصى بها: كورمورانت مائل + قليتشر خشن
const REC = 'plain=1&gold=f-cormorant&glitter=gl-coarse&metal=g1&ar=a-ruqaa&arsize=80';
await png('01-offwhite-4800.png',    REC, { scale: 3 });
await png('02-black-4800.png',       REC + '&bg=%230C0B0A', { scale: 3 });
await png('03-transparent-4800.png', REC + '&bg=transparent', { scale: 3, transparent: true });

// قليتشر خشن جداً (أقرب للِيبل القديم)
const ROUGH = 'plain=1&gold=f-cormorant&glitter=gl-rough&metal=g1&ar=a-ruqaa&arsize=80';
await png('04-offwhite-rough-glitter-4800.png', ROUGH, { scale: 3 });

// البديل بخط سينزل
const CINZEL = 'plain=1&gold=f-cinzel&glitter=gl-coarse&metal=g1&ar=a-ruqaa&arsize=80';
await png('05-cinzel-offwhite-4800.png', CINZEL, { scale: 3 });
await png('06-cinzel-black-4800.png',    CINZEL + '&bg=%230C0B0A', { scale: 3 });

// ملفات PDF للمطبعة
await pdf('07-offwhite-print.pdf', REC);
await pdf('08-cinzel-offwhite-print.pdf', CINZEL);

await browser.close();
console.log(errors.length ? '\n⚠ ERRORS:\n' + errors.join('\n') : '\nno page errors ✓');
