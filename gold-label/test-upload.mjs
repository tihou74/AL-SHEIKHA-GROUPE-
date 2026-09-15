/* يحاكي ما سيفعله المستخدم: يرفع صورة اسمه العربي (بخلفية بيضاء)
   ثم يتحقق أن البرنامج استخرج شكل الحروف وطلاها بالذهب الجديد، وأن التصدير ينجح. */
import { chromium } from 'playwright-core';
import fs from 'node:fs';

const EXE = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const DIR = '/projects/sandbox/alsheikha-gold-label';
const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });

/* ── ١) نصنع صورة اختبار تشبه لِيبل العميل: اسم عربي ذهبي مسطّح على خلفية بيضاء ── */
{
  const page = await browser.newPage({ viewport: { width: 1000, height: 300 } });
  await page.goto('file://' + DIR + '/index.html');           // لتتوفر الخطوط المضمّنة
  await page.evaluate(() => document.fonts.ready);
  // نبني عنصراً بخط مختلف (ركّاز) بلون ذهبي مسطّح داخل نفس الصفحة (الخطوط مضمّنة فيها)
  await page.evaluate(() => {
    document.body.innerHTML = '';
    document.body.style.cssText = 'margin:0;background:#fff;display:flex;align-items:center;justify-content:center;height:300px';
    const d = document.createElement('div');
    d.textContent = 'الشيخة ستايل';
    d.style.cssText = "font-family:'Rakkas',serif;font-size:150px;color:#C9A24C;direction:rtl;line-height:1.2";
    document.body.appendChild(d);
  });
  await page.waitForTimeout(600);
  await page.screenshot({ path: DIR + '/previews/_test-customer-arabic.png' });
  await page.close();
  console.log('✔ صورة اختبار جاهزة: previews/_test-customer-arabic.png');
}

/* ── ٢) نرفعها في الاستوديو ونفحص النتيجة ── */
const page = await browser.newPage({ viewport: { width: 1500, height: 1200 } });
const errs = [];
page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
await page.goto('file://' + DIR + '/index.html?glitter=gl-rough&gold=f-cinzel');
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);

await page.setInputFiles('#fileAr', DIR + '/previews/_test-customer-arabic.png');
await page.waitForTimeout(1200);

const state = await page.evaluate(() => {
  const m = document.getElementById('arMask');
  const t = document.getElementById('arText');
  const cs = getComputedStyle(m);
  return {
    maskVisible: !m.hidden,
    textHidden: t.style.display === 'none',
    aspectRatio: m.style.aspectRatio,
    maskImageStarts: (cs.webkitMaskImage || cs.maskImage || '').slice(0, 30),
    maskSize: cs.webkitMaskSize || cs.maskSize,
    boxW: Math.round(m.getBoundingClientRect().width),
    boxH: Math.round(m.getBoundingClientRect().height),
  };
});
console.log('حالة العنصر:', JSON.stringify(state, null, 1));

/* ── ٣) تصدير PNG والتحقق من النتيجة بصرياً ── */
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
const out = DIR + '/previews/97-uploaded-arabic-gold-plated.png';
fs.writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
console.log('✔ تصدير مع صورة العميل:', out, fs.statSync(out).size, 'bytes');

/* ── ٤) لقطة شاشة للمعاينة الحيّة أيضاً ── */
await page.screenshot({ path: DIR + '/previews/96-upload-studio-view.png' });
console.log(errs.length ? 'ERRORS: ' + errs.join(' | ') : 'no page errors ✓');
await browser.close();
