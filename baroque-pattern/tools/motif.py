"""
The ornament: a baroque acanthus scroll, reverse-engineered from the carved
gilt mirror frame in the reference photo.

Visual DNA taken from the photo:
  * broad, fleshy C-scrolls that swell in the middle and curl into a tight
    spiral "eye" with a bead in it
  * acanthus blades built as a FAN OF LOBES on a curved spine -- the concave
    notches between the lobes are what makes a leaf read as acanthus rather
    than as a petal or a feather
  * one incised rib per carved surface, plus a rubbed highlight on the upper
    edge only (the reference is worn gilt over gesso, not engraving)
  * pierced negative space between the scrolls

Everything is a "ribbon": a centre-line plus a width profile. Overlapping
ribbons are filled with the nonzero rule, so a fan of lobes merges into one
silhouette with notches.

Output: list of (points, layer); layer in sh / body / rib / hi.
"""

import math

from geom import (add, bezier, catmull, circle, mul, norm, offset_line, perp,
                  resample, ribbon, rot, spiral, sub, tangents, trim)

SH, BODY, RIB, HI = "sh", "body", "rib", "hi"
LAYER_ORDER = [SH, BODY, RIB, HI]


# --------------------------------------------------------------------- leaves


def _scallop(u, sharp=0.80):
    """
    Lobe profile over one lobe cycle, u in 0..1.

    Returns (radial, forward). The radial factor swells from a pinch to full
    width, then drops back quickly -- the drop is the notch between two lobes.
    The forward factor leans the lobe tip along the spine, which is why an
    acanthus lobe looks swept rather than like a round scallop.

    The fall is spread over 20% of the cycle rather than being instantaneous:
    a true discontinuity makes the smoothing overshoot and tie a knot.
    """
    if u < sharp:
        r = u / sharp
        rise = r ** 0.70
        return 0.38 + 0.62 * rise, r ** 1.30
    r = (u - sharp) / (1.0 - sharp)
    fall = (1.0 - r) ** 0.85
    return 0.38 + 0.62 * fall, fall


def _edge(spine, tg, side, w_fn, lobes, phase, fwd=0.55, sharp=0.80):
    """One scalloped side of a blade."""
    n = len(spine) - 1
    pts = []
    for i, p in enumerate(spine):
        t = i / n
        rad, f = _scallop((t * lobes + phase) % 1.0, sharp)
        w = w_fn(t) * rad
        q = add(p, mul(perp(tg[i]), side * w))
        q = add(q, mul(tg[i], w * fwd * f))
        pts.append(q)
    return pts


def acanthus_leaf(base, dirv, length, width, curl, lobes=3, ribs=True):
    """
    A carved acanthus blade: one closed outline whose two sides are scalloped
    into forward-swept lobes with deep notches between them.

    Building the outline directly -- instead of unioning a bundle of separate
    lobe shapes -- is what keeps the blade readable: separate lobes inevitably
    cross one another and the leaf turns into a scribble.
    """
    shapes = []
    d = norm(dirv)
    pp = perp(d)

    # The control points are weighted so the last third hooks over hard: a
    # carved acanthus tip turns back on itself, it does not run out straight.
    p1 = add(base, mul(d, 0.30 * length))
    p2 = add(add(base, mul(d, 0.66 * length)), mul(pp, 0.14 * length * curl))
    p3 = add(add(base, mul(d, 0.80 * length)), mul(pp, 0.70 * length * curl))
    spine = resample(bezier(base, p1, p2, p3, 60), 96)
    tg = tangents(spine)

    def half_w(t):
        # thin where it springs from the scroll, full by 16%, point at the tip
        return 0.5 * width * (0.40 + 0.60 * min(1.0, t / 0.16)) * (1 - t ** 1.5) ** 0.55

    left = _edge(spine, tg, -1.0, half_w, lobes, 0.06, fwd=0.72)
    right = _edge(spine, tg, 1.0, lambda t: half_w(t) * 0.74, max(2, lobes - 1),
                  0.42, fwd=0.55)
    shapes.append((left + list(reversed(right)), BODY))

    if ribs:
        rib = trim(spine, 0.06, 0.80)
        shapes.append((ribbon(rib, lambda t: max(0.8, width * 0.085 * (1 - 0.45 * t)), 22), RIB))
        hi = offset_line(trim(spine, 0.10, 0.72),
                         lambda t: -half_w(0.10 + 0.62 * t) * 0.42, 26)
        shapes.append((ribbon(hi, lambda t: max(0.6, width * 0.065), 22), HI))

    return shapes


# --------------------------------------------------------------------- scrolls


def _scroll_line(stem_pts, eye, sweep, r_end_frac, turns_n=70):
    """Continue a stem into a spiral volute, tangent-matched at the join."""
    v = sub(stem_pts[-1], eye)
    r0 = math.hypot(*v)
    a0 = math.atan2(v[1], v[0])
    sp = spiral(eye, r0, r0 * r_end_frac, a0, a0 + sweep, turns_n)
    return stem_pts + sp[1:], sp[-1]


def volute(centre_pt, r0, sweep, w0, w1, r_end_frac=0.34, bead=True, ribs=True):
    """A stand-alone spiral scroll with a bead in the eye."""
    shapes = []
    a0 = 0.2
    c = spiral(centre_pt, r0, r0 * r_end_frac, a0, a0 + sweep, 64)

    def wf(t):
        return w0 * (1 - t) ** 0.7 + w1

    shapes.append((ribbon(c, wf, 46, clamp=1.3), BODY))
    if ribs:
        ln = offset_line(trim(c, 0.05, 0.80), lambda t: wf(0.05 + 0.75 * t) * -0.18, 34)
        shapes.append((ribbon(ln, lambda t: max(0.7, w0 * 0.07), 26), RIB))
    if bead:
        shapes.append((circle(c[-1], max(2.2, r0 * r_end_frac * 0.52), 16), BODY))
    return shapes


def acanthus_scroll():
    """
    The repeat unit: one broad C-scroll springing from a thin foot, curling
    into a volute, with acanthus blades fanning off its back.

    Local coordinates: foot near (-30, 22), eye of the volute near (60, -62);
    overall span roughly x -46..112, y -104..46.
    """
    shapes = []

    # ---- the main C-scroll -------------------------------------------------
    # A wide-radius volute so the eye stays OPEN: the pierced hole inside the
    # curl is half of what makes the reference carving read as baroque.
    stem = bezier((0, 0), (24, -8), (48, -24), (60, -50), 30)
    eye = (26, -60)
    centre, eye_pt = _scroll_line(stem, eye, -1.42 * math.pi, 0.19, 74)
    n = len(centre) - 1

    def wf(t):
        fade = min(1.0, (t / 0.14) ** 0.6)           # thin foot, no blunt cap
        return (30.0 * (1 - t) ** 0.72 + 3.2) * (0.12 + 0.88 * fade)

    shapes.append((ribbon(centre, wf, 78, clamp=1.22), BODY))
    # one incised groove along the concave side, plus the rubbed bright edge
    ln = offset_line(trim(centre, 0.10, 0.86), lambda t: wf(0.10 + 0.76 * t) * -0.20, 52)
    shapes.append((ribbon(ln, lambda t: max(0.9, 2.3 * (1 - 0.45 * t)), 40), RIB))
    hi = offset_line(trim(centre, 0.14, 0.74), lambda t: wf(0.14 + 0.60 * t) * 0.30, 44)
    shapes.append((ribbon(hi, lambda t: max(0.8, 2.1), 34), HI))
    shapes.append((circle(eye_pt, 5.4, 18), BODY))   # bead in the eye

    # ---- fan of blades off the CONVEX back of the scroll --------------------
    # +perp is the outer side of the C here. Blades laid on the inner side end
    # up inside the curl and choke it, which is exactly what must not happen.
    for at, ang, ln_, w, curl, lb in (
        (0.05, 1.00, 74, 40.0, -1.05, 3),
        (0.19, 0.80, 58, 32.0, -1.10, 3),
        (0.33, 0.62, 42, 23.0, -1.15, 2),
        (0.45, 0.48, 29, 16.0, -1.20, 2),
    ):
        i = int(at * n)
        tg = norm(sub(centre[min(i + 2, n)], centre[max(i - 2, 0)]))
        # anchored well inside the scroll so the blade reads as growing out of
        # it rather than being stuck onto it
        bp = add(centre[i], mul(perp(tg), wf(at) * 0.12))
        shapes += acanthus_leaf(bp, rot(tg, ang), ln_, w, curl, lobes=lb)

    # ---- a bud tucked into the hollow of the C -----------------------------
    shapes += acanthus_leaf((46, -34), (-0.55, -0.84), 30, 15.0, 1.05, lobes=2)

    # ---- foot: a counter-curl that links one unit to the next ---------------
    # No blade here: when the unit is mirrored into a palmette, two foot blades
    # meet head-on at the axis and cross into a knot.
    shapes += volute((-12, 20), 16.0, 1.55 * math.pi, 13.0, 2.0, 0.30)

    return shapes


def boss(r=14.0):
    """A small carved rosette that hides the join at the centre of a spray."""
    shapes = []
    petals = 8
    for k in range(petals):
        a = 2 * math.pi * k / petals
        d = (math.cos(a), math.sin(a))
        spine = [mul(d, r * (0.26 + 0.74 * i / 12)) for i in range(13)]
        # rounded both ends -- a scalloped acanthus edge at this size just
        # reads as a spiky asterisk
        shapes.append((ribbon(spine, lambda t: r * 0.44 * math.sin(
            math.pi * (0.16 + 0.68 * t)) ** 0.8, 14), BODY))
    shapes.append((circle((0, 0), r * 0.34, 22), BODY))
    shapes.append((circle((0, 0), r * 0.15, 16), RIB))
    return shapes


def to_paths(shapes):
    """Sort into carving layers and emit SVG path strings."""
    buckets = {k: [] for k in LAYER_ORDER}
    for pts, layer in shapes:
        buckets[layer].append(catmull(pts, closed=True, tension=7.0))
    return buckets
