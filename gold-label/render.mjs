import { chromium } from 'playwright-core';
import fs from 'node:fs';

const EXE  = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const BASE = 'file:///projects/sandbox/alsheikha-gold-label/index.html';
const OUT  = '/projects/sandbox/alsheikha-gold-label/previews';
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });

async function shot(file, params, { scale = 1.5, w = 1600, h = 640, transparent = false, fullPage = false } = {}) {
  const page = await browser.newPage({
    viewport: { width: w, height: h },
    deviceScaleFactor: scale,
  });
  await page.goto(BASE + '?' + params);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${OUT}/${file}`, omitBackground: transparent, fullPage });
  await page.close();
  console.log('✔', file);
}

const golds = ['f-bodoni','f-bodoni-up','f-cormorant','f-playfair','f-cinzel','f-italiana','f-marcellus','f-prata'];

// 1) ورقة مقارنة خطوط GOLD
await shot('00-gold-fonts-sheet.png', 'sheet=1', { scale: 1, w: 1240, h: 4300, fullPage: true });

// 2) كل خط لوحده على أوف وايت
let i = 1;
for (const g of golds) {
  await shot(`${String(i).padStart(2,'0')}-${g.replace('f-','')}.png`, `plain=1&gold=${g}`);
  i++;
}

// 3) أنماط لمعة الذهب على الخط المختار
await shot('20-metal-g1-soft.png',   'plain=1&gold=f-bodoni&metal=g1');
await shot('21-metal-g2-strong.png', 'plain=1&gold=f-bodoni&metal=g2');
await shot('22-metal-g3-antique.png','plain=1&gold=f-bodoni&metal=g3');

// 4) خلفية سوداء + شفافة
await shot('30-black.png', 'plain=1&gold=f-bodoni&bg=%230C0B0A');
await shot('31-transparent.png', 'plain=1&gold=f-bodoni&bg=transparent', { transparent: true });

// 5) ورقة خطوط الاسم العربي
const ars = ['a-ruqaa','a-mirza','a-gulzar','a-amiri','a-messiri','a-reem'];
let j = 40;
for (const a of ars) {
  await shot(`${j}-${a.replace('a-','ar-')}.png`, `plain=1&ar=${a}`);
  j++;
}

await browser.close();
