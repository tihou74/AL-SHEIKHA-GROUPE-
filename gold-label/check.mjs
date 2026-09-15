import { chromium } from 'playwright-core';
const EXE = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });

async function run(url, tag) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
  page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  page.on('requestfailed', r => errs.push('REQFAIL: ' + r.url().slice(0, 90) + ' :: ' + r.failure()?.errorText));

  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);

  const hasLib = await page.evaluate(() => typeof window.htmlToImage);

  const res = await page.evaluate(async () => {
    const label = document.getElementById('label');
    label.classList.remove('shine');
    try {
      const url = await window.htmlToImage.toPng(label, { pixelRatio: 1, width: 1600, height: 640, backgroundColor: '#FAF6EE' });
      return 'OK len=' + url.length;
    } catch (e) {
      return 'FAIL type=' + Object.prototype.toString.call(e) + ' msg=' + (e && (e.message || e.type || String(e)));
    }
  });

  const controls = await page.evaluate(() => {
    const out = [];
    const set = (id, val, ev) => {
      const el = document.getElementById(id);
      if (!el) return out.push(id + ' MISSING');
      if (el.type === 'checkbox') el.checked = val; else el.value = val;
      el.dispatchEvent(new Event(ev || 'change'));
      out.push(id + '=' + val + ' ok');
    };
    set('selGold', 'f-cinzel'); set('selMetal', 'g2'); set('selFrame', 'simple');
    set('selBg', '#0C0B0A'); set('selAr', 'a-mirza'); set('rngAr', '95', 'input');
    set('chkShine', false); set('chkGrid', true);
    const l = document.getElementById('label');
    out.push('classes=' + l.className);
    out.push('arScale=' + getComputedStyle(l).getPropertyValue('--ar-scale').trim());
    out.push('arVal=' + document.getElementById('arVal').textContent);
    return out;
  });

  console.log('\n===== ' + tag + ' =====');
  console.log('htmlToImage:', hasLib, '| export:', res);
  controls.forEach(c => console.log('  ', c));
  console.log(errs.length ? 'ERRORS:\n' + errs.join('\n') : 'no errors');
  await page.close();
}

await run('file:///projects/sandbox/alsheikha-gold-label/index.html', 'file://');
await run('http://127.0.0.1:8899/index.html', 'http://');
await browser.close();
