import { chromium } from 'playwright-core';
import fs from 'node:fs';

const EXE  = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const BASE = 'file:///projects/sandbox/alsheikha-gold-label/index.html';
const OUT  = '/projects/sandbox/alsheikha-gold-label/final';
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });

async function open(params, scale) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 640 }, deviceScaleFactor: scale });
  await page.goto(BASE + '?' + params);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1000);
  return page;
}

async function png(file, params, { scale = 3, transparent = false } = {}) {
  const page = await open(params, scale);
  await page.screenshot({ path: `${OUT}/${file}`, omitBackground: transparent });
  await page.close();
  console.log('✔', file);
}

async function pdf(file, params, zoom = 2) {
  // zoom يكبّر التصميم قبل التصدير حتى تكون دقة النص الذهبي داخل الـPDF أعلى
  const page = await browser.newPage({ viewport: { width: 1600 * zoom, height: 640 * zoom }, deviceScaleFactor: 1 });
  await page.goto(BASE + '?' + params + '&zoom=' + zoom);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1000);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: `${OUT}/${file}`, width: (1600 * zoom) + 'px', height: (640 * zoom) + 'px',
                   printBackground: true, margin: { top: '0', right: '0', bottom: '0', left: '0' } });
  await page.close();
  console.log('✔', file);
}

// النسخة الموصى بها: كورمورانت مائل + ذهب معدني ناعم
const REC = 'plain=1&gold=f-cormorant&metal=g1&ar=a-ruqaa&arsize=80';

await png('alsheikha-gold-offwhite-4800.png', REC, { scale: 3 });
await png('alsheikha-gold-black-4800.png',    REC + '&bg=%230C0B0A', { scale: 3 });
await png('alsheikha-gold-transparent-4800.png', REC + '&bg=transparent', { scale: 3, transparent: true });

// البديل الثاني: سينزل
const ALT = 'plain=1&gold=f-cinzel&metal=g1&ar=a-ruqaa&arsize=80';
await png('alsheikha-gold-cinzel-offwhite-4800.png', ALT, { scale: 3 });
await png('alsheikha-gold-cinzel-black-4800.png',    ALT + '&bg=%230C0B0A', { scale: 3 });

// ملفات PDF متجهة (للمطبعة — تتكبر بلا حدود)
await pdf('alsheikha-gold-offwhite-vector.pdf', REC);
await pdf('alsheikha-gold-cinzel-offwhite-vector.pdf', ALT);

await browser.close();
