#!/usr/bin/env python3
"""
Builds the seamless baroque-acanthus pattern files.

Composition: one carved scroll unit is defined once, then reused with SVG
transforms into a four-fold rosette at the tile centre, a smaller rosette on
the tile corner, and small sprigs at the edge midpoints -- the classic damask
lattice. The whole arrangement is then drawn nine times (offset by -1, 0, +1
tiles in x and y) and clipped to the tile, which is what makes the repeat
seamless: anything that runs off one edge is guaranteed to arrive on the
opposite edge.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motif import BODY, HI, RIB, SH, acanthus_scroll, boss, to_paths  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "patterns")
PREVIEW = os.path.join(ROOT, "preview")

TILE = 400.0

# ------------------------------------------------------------------ palettes

VARIANTS = {
    "gold": {
        "bg": "#f2e8db",
        "layers": {
            SH: {"fill": "#6f5210", "opacity": "0.30"},
            BODY: {"fill": "url(#gwGold)"},
            RIB: {"fill": "#8a6520", "opacity": "0.50"},
            HI: {"fill": "#fdf4d5", "opacity": "0.70"},
        },
    },
    "gold-dark": {
        "bg": "#191410",
        "layers": {
            SH: {"fill": "#000000", "opacity": "0.45"},
            BODY: {"fill": "url(#gwGold)"},
            RIB: {"fill": "#5d430f", "opacity": "0.75"},
            HI: {"fill": "#ffeeb5", "opacity": "0.60"},
        },
    },
    "line": {
        "bg": "#ffffff",
        "layers": {
            SH: {"display": "none"},
            BODY: {"fill": "none", "stroke": "#14120f", "stroke-width": "1.5"},
            RIB: {"fill": "#14120f", "opacity": "0.9"},
            HI: {"display": "none"},
        },
    },
    "mono": {
        "bg": "none",
        "layers": {
            SH: {"display": "none"},
            BODY: {"fill": "currentColor"},
            RIB: {"fill": "#ffffff", "opacity": "0.30"},
            HI: {"display": "none"},
        },
    },
    # flat silhouette, for CSS mask-image tinting and for cutting machines
    "solid": {
        "bg": "none",
        "layers": {
            SH: {"display": "none"},
            BODY: {"fill": "#000000"},
            RIB: {"display": "none"},
            HI: {"display": "none"},
        },
    },
}

GRADIENT = """  <linearGradient id="gwGold" x1="0.05" y1="0" x2="0.9" y2="1">
    <stop offset="0"    stop-color="#a9761a"/>
    <stop offset="0.28" stop-color="#e6c976"/>
    <stop offset="0.55" stop-color="#c69a2d"/>
    <stop offset="0.80" stop-color="#f0dc9c"/>
    <stop offset="1"    stop-color="#8a6414"/>
  </linearGradient>"""


def attrs(d):
    return " ".join('%s="%s"' % (k, v) for k, v in d.items())


# ------------------------------------------------------------------ the tile


FOOT = (6, -14)   # shifts the unit so the foot of its scroll sits on the origin


def build_defs(variant, prefix=""):
    """Motif + lattice definitions. `prefix` keeps ids unique if several
    pattern variants ever live in one document."""
    cfg = VARIANTS[variant]
    p = prefix
    parts = [GRADIENT]

    def shaded(name, shapes, sh_offset="2,2.6"):
        """Emit the carved surfaces once, then a shaded assembly that reuses
        the body group for its own drop shadow."""
        b = to_paths(shapes)
        out = []
        for suffix, layer in (("body", BODY), ("rib", RIB), ("hi", HI)):
            if not b[layer] or cfg["layers"][layer].get("display") == "none":
                b[layer] = []
                continue
            out.append('  <g id="%s%s%s">\n%s\n  </g>' % (
                p, name, suffix,
                "\n".join('    <path d="%s"/>' % d for d in b[layer])))
        asm = ['  <g id="%s%s">' % (p, name)]

        def u(suffix, layer, tf=""):
            if not b[layer]:
                return None
            t = ' transform="translate(%s)"' % tf if tf else ""
            return '    <use href="#%s%s%s" xlink:href="#%s%s%s"%s %s/>' % (
                p, name, suffix, p, name, suffix, t, attrs(cfg["layers"][layer]))

        for row in (u("body", SH, sh_offset) if cfg["layers"][SH].get("display") != "none" else None,
                    u("body", BODY),
                    u("rib", RIB),
                    u("hi", HI) if cfg["layers"][HI].get("display") != "none" else None):
            if row:
                asm.append(row)
        asm.append('  </g>')
        out.append("\n".join(asm))
        return out

    parts += shaded("u", acanthus_scroll())
    parts += shaded("b", boss(19.0))

    def use(name, tf):
        return '    <use href="#%s%s" xlink:href="#%s%s" transform="%s"/>' % (p, name, p, name, tf)

    # ---- the palmette: two units mirrored about a vertical axis, feet meeting
    # on the origin. Mirror symmetry (rather than 4-fold rotation) is what
    # makes a baroque spray read as carved ornament instead of a pinwheel.
    pal = ['  <g id="%spal">' % p,
           use("u", "translate(%g,%g)" % FOOT),
           use("u", "scale(-1,1) translate(%g,%g)" % FOOT),
           use("b", "translate(0,4) scale(1.20)"),
           '  </g>']
    parts.append("\n".join(pal))

    # ---- one tile's worth of ornament (deliberately overflows its bounds).
    # Upright sprays alternate with inverted ones offset by half a tile, which
    # is the half-drop that stops the repeat from reading as a grid of dots.
    # A small floret sits in each remaining gap.
    lat = ['  <g id="%slat">' % p,
           use("pal", "translate(%g,%g) scale(1.22)" % (TILE / 2, TILE * 0.68)),
           use("pal", "translate(0,0) rotate(180) scale(0.92)"),
           use("b", "translate(%g,%g) scale(1.7)" % (TILE / 2, TILE * 0.13)),
           use("b", "translate(0,%g) scale(1.7)" % (TILE * 0.63)),
           '  </g>']
    parts.append("\n".join(lat))

    # nine offset copies -> guarantees the edges line up
    field = ['  <g id="%sfield">' % p]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            field.append('    <use href="#%slat" xlink:href="#%slat" transform="translate(%g,%g)"/>'
                         % (p, p, dx * TILE, dy * TILE))
    field.append('  </g>')
    parts.append("\n".join(field))

    return "\n".join(parts)


HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" ')


def tile_svg(variant, transparent=False):
    cfg = VARIANTS[variant]
    bg = "none" if transparent else cfg["bg"]
    bgrect = "" if bg == "none" else '  <rect width="%g" height="%g" fill="%s"/>\n' % (TILE, TILE, bg)
    return (
        '%swidth="%g" height="%g" viewBox="0 0 %g %g">\n'
        '  <title>Baroque acanthus scroll - seamless tile (%s)</title>\n'
        '  <defs>\n%s\n'
        '    <clipPath id="gwClip"><rect width="%g" height="%g"/></clipPath>\n'
        '  </defs>\n'
        '%s'
        '  <g clip-path="url(#gwClip)">\n'
        '    <use href="#gwfield" xlink:href="#gwfield"/>\n'
        '  </g>\n'
        '</svg>\n'
    ) % (HEAD, TILE, TILE, TILE, TILE, variant,
         build_defs(variant, "gw"), TILE, TILE, bgrect)


def field_svg(variant, w=1600, h=1200, scale=1.0):
    """A large area filled through <pattern> -- drop-in for hero sections."""
    cfg = VARIANTS[variant]
    return (
        '%swidth="%g" height="%g" viewBox="0 0 %g %g">\n'
        '  <title>Baroque acanthus scroll - pattern fill (%s)</title>\n'
        '  <defs>\n%s\n'
        '    <pattern id="gwPat" patternUnits="userSpaceOnUse" '
        'width="%g" height="%g" viewBox="0 0 %g %g" '
        'patternTransform="scale(%g)">\n'
        '      <use href="#gwfield" xlink:href="#gwfield"/>\n'
        '    </pattern>\n'
        '  </defs>\n'
        '  <rect width="%g" height="%g" fill="%s"/>\n'
        '  <rect width="%g" height="%g" fill="url(#gwPat)"/>\n'
        '</svg>\n'
    ) % (HEAD, w, h, w, h, variant, build_defs(variant, "gw"),
         TILE, TILE, TILE, TILE, scale, w, h,
         cfg["bg"] if cfg["bg"] != "none" else "#ffffff", w, h)


def motif_svg(variant="gold"):
    """The single scroll on its own: corner pieces, dividers, logo lockups."""
    return (
        '%swidth="460" height="420" viewBox="-60 -120 230 210">\n'
        '  <title>Baroque acanthus scroll - single motif</title>\n'
        '  <defs>\n%s\n  </defs>\n'
        '  <use href="#gwu" xlink:href="#gwu"/>\n'
        '</svg>\n'
    ) % (HEAD, build_defs(variant, "gw"))


def palmette_svg(variant="gold"):
    """The mirrored pair -- the symmetric spray used at the tile centre."""
    return (
        '%swidth="520" height="420" viewBox="-130 -130 260 210">\n'
        '  <title>Baroque acanthus scroll - mirrored palmette</title>\n'
        '  <defs>\n%s\n  </defs>\n'
        '  <use href="#gwpal" xlink:href="#gwpal"/>\n'
        '</svg>\n'
    ) % (HEAD, build_defs(variant, "gw"))


BORDER_W, BORDER_H = 300.0, 132.0
# The spray is 146 units tall about its foot (110 up, 36 down), so the baseline
# has to leave room on both sides or the foot volute gets clipped.
BORDER_BASE = 101.0


def border_svg(variant="gold", repeats=3):
    """A border strip that repeats seamlessly left-to-right."""
    cfg = VARIANTS[variant]
    lat = ('    <use href="#gwpal" xlink:href="#gwpal" transform="translate(%g,%g) scale(0.72)"/>\n'
           '    <use href="#gwpal" xlink:href="#gwpal" transform="translate(0,%g) scale(0.42)"/>\n'
           ) % (BORDER_W / 2, BORDER_BASE, BORDER_BASE)
    body = []
    for r in range(repeats):
        for dx in (-1, 0, 1):
            body.append('  <g transform="translate(%g,0)">\n%s  </g>'
                        % ((r + dx) * BORDER_W, lat))
    w = BORDER_W * repeats
    return (
        '%swidth="%g" height="%g" viewBox="0 0 %g %g">\n'
        '  <title>Baroque acanthus scroll - seamless border</title>\n'
        '  <defs>\n%s\n'
        '    <clipPath id="gwBClip"><rect width="%g" height="%g"/></clipPath>\n'
        '  </defs>\n'
        '  <rect width="%g" height="%g" fill="%s"/>\n'
        '  <g clip-path="url(#gwBClip)">\n%s\n  </g>\n'
        '</svg>\n'
    ) % (HEAD, w, BORDER_H, w, BORDER_H, build_defs(variant, "gw"),
         w, BORDER_H, w, BORDER_H,
         cfg["bg"] if cfg["bg"] != "none" else "#ffffff", "\n".join(body))


# ------------------------------------------------------------------ output

def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)

    files = {}
    for v in VARIANTS:
        files["tile-%s.svg" % v] = tile_svg(v)
        files["tile-%s-transparent.svg" % v] = tile_svg(v, transparent=True)
    files["field-gold.svg"] = field_svg("gold")
    files["field-gold-dark.svg"] = field_svg("gold-dark")
    files["motif-gold.svg"] = motif_svg("gold")
    files["motif-line.svg"] = motif_svg("line")
    files["palmette-gold.svg"] = palmette_svg("gold")
    files["palmette-line.svg"] = palmette_svg("line")
    files["border-gold.svg"] = border_svg("gold")
    files["border-line.svg"] = border_svg("line")

    for name, data in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(data)
        print("%-34s %7.1f KB" % (name, len(data.encode()) / 1024))

    # ---- rasterised checks
    try:
        import cairosvg
    except ImportError:
        print("cairosvg missing - skipping PNG previews")
        return

    def png(svg, name, w):
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(PREVIEW, name),
                         output_width=w)
        print("preview/%s" % name)

    png(motif_svg("gold"), "motif.png", 700)
    png(motif_svg("line"), "motif-line.png", 700)
    png(palmette_svg("gold"), "palmette.png", 760)
    png(palmette_svg("line"), "palmette-line.png", 760)
    png(border_svg("gold"), "border.png", 1000)
    png(tile_svg("gold"), "tile.png", 500)
    # 3x3 of the tile: any seam shows up immediately as a break in the lattice
    png(field_svg("gold", w=1200, h=1200), "seam-check.png", 900)
    png(field_svg("gold-dark", w=1200, h=1200), "seam-check-dark.png", 900)

    # ---- raster tiles for tools that cannot take SVG (Photoshop, embroidery,
    # CNC previews). These are seamless rasters of exactly one tile.
    raster = os.path.join(ROOT, "png")
    os.makedirs(raster, exist_ok=True)
    for v in ("gold", "gold-dark"):
        for size in (512, 1024, 2048):
            cairosvg.svg2png(bytestring=tile_svg(v).encode(), output_width=size,
                             output_height=size,
                             write_to=os.path.join(raster, "tile-%s-%d.png" % (v, size)))
        print("png/tile-%s-{512,1024,2048}.png" % v)
    for size in (512, 1024, 2048):
        cairosvg.svg2png(bytestring=tile_svg("gold", transparent=True).encode(),
                         output_width=size, output_height=size,
                         write_to=os.path.join(raster, "tile-gold-transparent-%d.png" % size))
    print("png/tile-gold-transparent-{512,1024,2048}.png")

    # ---- prove the raster tile really is seamless: butt four copies together
    # and look at the joins. A wrong tile shows a cross of broken ornament.
    try:
        from PIL import Image
    except ImportError:
        return
    t = Image.open(os.path.join(raster, "tile-gold-1024.png")).convert("RGB")
    n = t.width
    sheet = Image.new("RGB", (n * 2, n * 2))
    for x in (0, n):
        for y in (0, n):
            sheet.paste(t, (x, y))
    # mark where the joins fall so they are easy to inspect
    sheet.resize((900, 900), Image.LANCZOS).save(os.path.join(PREVIEW, "raster-seam-check.png"))
    print("preview/raster-seam-check.png")


if __name__ == "__main__":
    main()
