# نقشة باروك — أكانثس ذهبي / Baroque Acanthus Pattern

نقشة متكررة (seamless) مستخرجة من الزخرفة المحفورة في صورة إطار المرآة الذهبي:
لفّات حلزونية عريضة تنتهي بعين حلزونية فيها حبّة، وأوراق أكانثس مسنّنة أطرافها
تنقلب، بذهب مُهترئ فوق أرضية كريمية.

A seamless repeating pattern rebuilt from the carved gilt mirror frame in the
reference photo. Fully vector, generated geometrically — no tracing, so it
scales to any size and can be recoloured or restyled from source.

---

## الملفات / Files

### `patterns/` — SVG (متجهي، الأصل)

| ملف | الاستخدام |
|---|---|
| `tile-gold.svg` | البلاطة الأساسية 400×400 بخلفية كريمية |
| `tile-gold-transparent.svg` | نفسها بخلفية شفافة — فوق أي لون عندك |
| `tile-gold-dark.svg` / `-transparent` | ذهبي على خلفية داكنة |
| `tile-line.svg` / `-transparent` | خطوط فقط (outline) |
| `tile-mono.svg` / `-transparent` | لون واحد يتبع `currentColor` |
| `tile-solid.svg` / `-transparent` | silhouette مسطّح — للتلوين عبر CSS mask، وللقص CNC / التطريز / الاستنسل |
| `field-gold.svg`, `field-gold-dark.svg` | مساحة كبيرة 1600×1200 معبّأة عبر `<pattern>` — جاهزة كبانر |
| `motif-gold.svg`, `motif-line.svg` | الوحدة المفردة (لفّة واحدة) للزوايا والفواصل |
| `palmette-gold.svg`, `palmette-line.svg` | الوحدة معكوسة مرآوياً — تاج متناظر يوضع فوق العناوين |
| `border-gold.svg`, `border-line.svg` | شريط حدود يتكرر أفقياً فقط |

### `png/` — نقطي، لبرامج لا تقبل SVG
`tile-gold-{512,1024,2048}.png`، `tile-gold-dark-*`، `tile-gold-transparent-*`.
كل ملف بلاطة **متكررة**: ضعها في فوتوشوب كـ Pattern أو كـ Texture مباشرة.

### أخرى
- `index.html` — صفحة معاينة تفاعلية (حجم التكرار، اللون، خلفية داكنة).
- `usage/baroque-pattern.css` — أصناف CSS جاهزة.
- `preview/*.png` — صور معاينة، من بينها `seam-check.png` و`raster-seam-check.png`.
- `tools/` — مولّد النقشة بـ Python (`geom.py` هندسة، `motif.py` الزخرفة، `generate.py` التركيب).

---

## الاستخدام / Usage

```css
/* خلفية ويب */
.page{
  background: #f2e8db url("patterns/tile-gold-transparent.svg") repeat;
  background-size: 400px 400px;      /* أي مقاس — يبقى حادّاً */
}

/* بأي لون تريد، عبر mask على الـ silhouette */
.page{
  background-color: #7b1f2b;
  mask: url("patterns/tile-solid-transparent.svg") repeat center / 400px 400px;
}

/* شريط حدود */
.rule{ height:132px; background:url("patterns/border-gold.svg") repeat-x center/auto 132px; }
```

**البلاطة 400×400** والشريط دوره **300×132**. أي مضاعف لهذين الرقمين يتكرر بلا فاصل.

---

## كيف بُنيت / How it is built

كل شكل هو "شريط" = خط مركزي + دالة عرض، ثم يُغلق محيطه. هذا أسلوب النحّات نفسه،
ويعطي نتيجة أنظف بكثير من تخمين نقاط بيزييه للمحيط مباشرةً.

- **اللفّة الحلزونية**: حلزون لوغاريتمي بنصف قطر كبير حتى تبقى العين *مفتوحة* —
  الفراغ داخل اللفّة هو نصف ما يجعل الزخرفة تُقرأ كباروك.
- **ورقة الأكانثس**: محيط واحد مغلق، ضلعاه مُسنّنان إلى فصوص مائلة للأمام بينها
  حفر عميقة. تجميع فصوص منفصلة يتقاطع دائماً ويحوّل الورقة إلى خربشة — جُرّب وفشل.
- **الطبقات**: ظل سفلي، ثم السطح المذهّب بتدرّج، ثم حَفر غائر، ثم لمعة الحافة
  (تقليد للفضّي المُهترئ في الصورة).
- **التناظر**: الوحدة تُعكس مرآوياً لتكوين palmette متناظرة — التناظر المرآوي
  يُقرأ كزخرفة محفورة، أما التناظر الدوراني الرباعي فيبدو كدوّامة/شمس.
- **التكرار بلا فاصل**: محتوى البلاطة يُرسم **٩ مرات** بإزاحة (−1، 0، +1) بلاطة
  أفقياً ورأسياً ثم يُقصّ على حدود البلاطة. أي شكل يخرج من حافة يعود من المقابلة
  بالضرورة. الوردات المقلوبة موزّعة بإزاحة نصف بلاطة (half-drop) حتى لا تُقرأ
  النقشة كشبكة نقاط.

### إعادة التوليد
```bash
pip install cairosvg pillow
python3 tools/generate.py     # يكتب patterns/ و png/ و preview/
python3 tools/debug.py        # يرسم كل عنصر منفرداً للفحص
```
لتغيير المقاسات أو الكثافة: `TILE` و`build_defs` في `tools/generate.py`.
لتغيير الألوان: `VARIANTS` و`GRADIENT` في نفس الملف.

---

## ما تم التحقق منه فعلياً / Verified

- ✅ الـ 18 ملف SVG كلها تُحلَّل كـ XML صحيح وتُرسَم بلا أخطاء (`cairosvg`).
- ✅ التكرار بلا فاصل — بصرياً: تركيب 3×3 عبر `<pattern>` (`preview/seam-check.png`)
  و 2×2 من ملف PNG الفعلي (`preview/raster-seam-check.png`). لا خط فاصل ولا زخرفة
  مقطوعة عند أي وصلة.
- ✅ التكرار بلا فاصل — **بالقياس**: متوسط فرق البكسل بين آخر صف/عمود وأول صف/عمود
  يساوي الفرق الطبيعي بين أي صفّين مجاورين داخل البلاطة، أي أن الوصلة غير قابلة
  للتمييز عن أي موضع داخلي:

  | الوصلة | عند الالتفاف | المرجع (جاران داخليان) |
  |---|---|---|
  | رأسية (فوق/تحت) | 2.44 | 2.42 |
  | أفقية (يمين/يسار) | 0.81 | 0.84 |
- ✅ ملف `tile-solid-transparent.svg` لا يحتوي تدرّجاً ولا طبقات حَفر/لمعة، أي أنه
  silhouette صالح فعلاً كـ mask.
- ⚠️ لم أختبرها في متصفح حقيقي — لا يوجد متصفح في بيئة العمل. الرسم تم عبر
  `cairosvg`. الأشكال المستخدمة (`<use>`, `<pattern>`, `clipPath`, `mask`) مدعومة
  في كل المتصفحات الحديثة، لكن `mask` بدون بادئة `-webkit-` قديم قليلاً في Safari
  الأقدم — لهذا وُضعت البادئة في `usage/baroque-pattern.css`.
- ⚠️ نسخة الخطوط (`tile-line.svg`) فيها محيطات متراكبة (حدّ الورقة يعبر حدّ
  اللفّة). هذا طبيعي في رسم outline، لكن إن كان الهدف قصّ ليزر فالأنسب هو
  `tile-solid-*.svg` لأنه شكل مصمت واحد.
- ℹ️ حجم بلاطة SVG ≈ 72KB (≈ 20KB بعد gzip). إن أردت أخف، استخدم PNG أو قلّل
  `samples` في `tools/motif.py`.
