#!/usr/bin/env python3
"""
يبني كتلة @font-face مضمّنة (base64) للخطوط المستخدمة في اللِيبل فقط،
بعد تصغيرها لتحتوي الحروف المطلوبة فقط — حتى تعمل الصفحة بدون إنترنت
وينجح زر تحميل PNG (بدون قيود CORS على خطوط Google).
"""
import base64, io, re, subprocess, sys, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont

WORK = Path('/projects/sandbox/alsheikha-gold-label')
TMP  = WORK / '.fontbuild'
TMP.mkdir(exist_ok=True)

AR_TEXT  = 'الشيخة ستايل'
LAT_GOLD = 'GOLD'
LAT_MADE = 'MADE IN QATAR'

# (family, weight, italic, text)
FACES = [
    ('Bodoni Moda',        700, True,  LAT_GOLD),
    ('Bodoni Moda',        600, False, LAT_GOLD),
    ('Cormorant Garamond', 600, True,  LAT_GOLD),
    ('Playfair Display',   600, True,  LAT_GOLD),
    ('Cinzel',             600, False, LAT_GOLD),
    ('Italiana',           400, False, LAT_GOLD),
    ('Marcellus',          400, False, LAT_GOLD),
    ('Prata',              400, False, LAT_GOLD),
    ('Jost',               300, False, LAT_MADE),
    ('Aref Ruqaa',         700, False, AR_TEXT),
    ('Amiri',              700, False, AR_TEXT),
    ('Gulzar',             400, False, AR_TEXT),
    ('Mirza',              600, False, AR_TEXT),
    ('El Messiri',         600, False, AR_TEXT),
    ('Reem Kufi',          500, False, AR_TEXT),
]

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def css_for(family, weight, italic):
    fam = family.replace(' ', '+')
    spec = f'{fam}:ital,wght@1,{weight}' if italic else f'{fam}:wght@{weight}'
    return fetch(f'https://fonts.googleapis.com/css2?family={spec}').decode('utf-8')


def covers(font_bytes, text):
    """هل يغطي هذا الملف كل حروف النص؟"""
    try:
        f = TTFont(io.BytesIO(font_bytes), fontNumber=0, lazy=True)
        cmap = f.getBestCmap()
        return all(ord(ch) in cmap for ch in text if ch != ' ')
    except Exception:
        return False


blocks, total = [], 0
for family, weight, italic, text in FACES:
    slug = re.sub(r'[^a-z0-9]+', '-', family.lower()) + f'-{weight}' + ('-i' if italic else '')
    raw  = TMP / f'{slug}.src'
    sub  = TMP / f'{slug}.subset.woff2'

    if not raw.exists():
        css  = css_for(family, weight, italic)
        urls = re.findall(r'url\((https://[^)]+)\)', css)
        picked = None
        for u in urls:
            data = fetch(u)
            if covers(data, text):
                picked = data
                break
        if picked is None:
            raise RuntimeError(f'لم أجد ملفاً يغطي «{text}» لـ {family} {weight} italic={italic}'
                               f' (جرّبت {len(urls)} ملف)')
        raw.write_bytes(picked)

    subprocess.run([sys.executable, '-m', 'fontTools.subset', str(raw),
                    f'--text={text}', '--layout-features=*', '--flavor=woff2',
                    '--no-hinting', '--desubroutinize', f'--output-file={sub}'],
                   check=True, capture_output=True)

    b64 = base64.b64encode(sub.read_bytes()).decode('ascii')
    total += sub.stat().st_size
    blocks.append(
        f'@font-face{{font-family:"{family}";font-style:{"italic" if italic else "normal"};'
        f'font-weight:{weight};font-display:block;'
        f'src:url(data:font/woff2;base64,{b64}) format("woff2");}}')
    print(f'  ✔ {family} {weight}{" italic" if italic else ""} → {sub.stat().st_size/1024:.1f} KB')

(WORK / 'fonts-embedded.css').write_text('\n'.join(blocks), encoding='utf-8')
print(f'\nمجموع الخطوط المضغوطة: {total/1024:.0f} KB  |  بعد base64: {len("".join(blocks))/1024:.0f} KB')
