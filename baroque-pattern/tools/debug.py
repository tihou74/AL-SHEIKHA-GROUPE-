#!/usr/bin/env python3
"""Render individual pieces of the ornament so each can be judged on its own."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairosvg  # noqa: E402
from geom import bezier, catmull, circle, ribbon  # noqa: E402
import motif  # noqa: E402

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preview")
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" '
        'viewBox="%s">')


def render(shapes, name, box="-70 -140 260 260"):
    body = [catmull(p, True, 7.0) for p, l in shapes if l == motif.BODY]
    rib = [catmull(p, True, 7.0) for p, l in shapes if l == motif.RIB]
    hi = [catmull(p, True, 7.0) for p, l in shapes if l == motif.HI]
    svg = [HEAD % box, '<rect x="-500" y="-500" width="2000" height="2000" fill="#fff"/>']
    svg.append('<g fill="none" stroke="#111" stroke-width="1.2">')
    svg += ['<path d="%s"/>' % d for d in body]
    svg.append('</g>')
    svg.append('<g fill="#c00" opacity="0.75">')
    svg += ['<path d="%s"/>' % d for d in rib]
    svg.append('</g>')
    svg.append('<g fill="#08f" opacity="0.75">')
    svg += ['<path d="%s"/>' % d for d in hi]
    svg.append('</g>')
    svg.append('</svg>')
    out = "\n".join(svg)
    cairosvg.svg2png(bytestring=out.encode(), write_to=os.path.join(OUTDIR, name),
                     output_width=620)
    print("preview/%s  (%d body, %d rib, %d hi)" % (name, len(body), len(rib), len(hi)))


def main():
    # 1. the bare main scroll, no blades
    stem = bezier((0, 0), (24, -8), (48, -24), (60, -50), 30)
    centre, eye_pt = motif._scroll_line(stem, (26, -60), -1.42 * math.pi, 0.19, 74)

    def wf(t):
        fade = min(1.0, (t / 0.14) ** 0.6)
        return (30.0 * (1 - t) ** 0.72 + 3.2) * (0.12 + 0.88 * fade)

    sc = [(ribbon(centre, wf, 78, clamp=1.22), motif.BODY),
          (circle(eye_pt, 5.4, 18), motif.BODY)]
    render(sc, "dbg-scroll.png")

    # 2. one blade on its own
    render(motif.acanthus_leaf((0, 0), (1, -0.15), 90, 36.0, 1.0), "dbg-leaf.png",
           box="-30 -90 170 170")

    # 3. a stand-alone volute
    render(motif.volute((0, 0), 30.0, 1.6 * math.pi, 20.0, 3.0, 0.22),
           "dbg-volute.png", box="-50 -50 110 110")

    # 4. the full unit
    render(motif.acanthus_scroll(), "dbg-unit.png")


if __name__ == "__main__":
    main()
