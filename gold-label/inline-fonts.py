#!/usr/bin/env python3
"""يحدّث كتلة <style id="embedded-fonts"> داخل index.html من ملف fonts-embedded.css"""
import re
from pathlib import Path

W = Path('/projects/sandbox/alsheikha-gold-label')
css = (W / 'fonts-embedded.css').read_text(encoding='utf-8')
p = W / 'index.html'
s = p.read_text(encoding='utf-8')

pat = re.compile(r'(<style id="embedded-fonts">)(.*?)(</style>)', re.S)
assert pat.search(s), 'كتلة الخطوط المضمّنة غير موجودة'
s = pat.sub(lambda m: m.group(1) + '\n' + css + '\n' + m.group(3), s, count=1)
p.write_text(s, encoding='utf-8')
print(f'تم تضمين {len(css)/1024:.0f} KB من الخطوط  |  حجم index.html: {len(s.encode())/1024:.0f} KB')
