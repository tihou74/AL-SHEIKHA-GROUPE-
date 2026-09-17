"""
Geometry helpers for building carved-ornament (acanthus / volute) shapes as SVG paths.

Everything is built from "ribbons": a centre-line plus a width profile, converted
into a closed outline. That is how a woodcarver thinks about an acanthus leaf --
a tapering blade following a curve -- so it gives far better results than trying
to guess bezier control points for the outline directly.
"""

import math

# ---------------------------------------------------------------- basic vectors


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def norm(a):
    m = math.hypot(a[0], a[1])
    return (a[0] / m, a[1] / m) if m > 1e-12 else (0.0, 0.0)


def rot(a, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (a[0] * c - a[1] * s, a[0] * s + a[1] * c)


def perp(a):
    """90 deg rotation (screen coords: y grows downward)."""
    return (-a[1], a[0])


# ---------------------------------------------------------------- centre lines


def bezier(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        x = m * m * m * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t * t * t * p3[0]
        y = m * m * m * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t * t * t * p3[1]
        pts.append((x, y))
    return pts


def spiral(center, r0, r1, a0, a1, n=64):
    """Logarithmic spiral -- the 'eye' of a volute."""
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a0 + (a1 - a0) * t
        r = r0 * (r1 / r0) ** t
        pts.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a)))
    return pts


def resample(pts, n):
    """Uniform arc-length resampling, so width profiles read evenly."""
    if len(pts) < 2:
        return pts
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.dist(pts[i], pts[i - 1]))
    total = d[-1]
    if total <= 1e-9:
        return pts
    out, j = [], 0
    for i in range(n + 1):
        target = total * i / n
        while j < len(d) - 2 and d[j + 1] < target:
            j += 1
        span = d[j + 1] - d[j]
        f = 0.0 if span <= 1e-9 else (target - d[j]) / span
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f,
                    pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f))
    return out


def tangents(pts):
    n = len(pts)
    out = []
    for i in range(n):
        if i == 0:
            t = sub(pts[1], pts[0])
        elif i == n - 1:
            t = sub(pts[-1], pts[-2])
        else:
            t = sub(pts[i + 1], pts[i - 1])
        out.append(norm(t))
    return out


def circumradius(a, b, c):
    """Local radius of curvature; used to stop a ribbon folding over itself
    on the tight inside of a spiral."""
    ax, ay = a
    bx, by = b
    cx, cy = c
    area2 = abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
    if area2 < 1e-9:
        return 1e9
    return (math.dist(a, b) * math.dist(b, c) * math.dist(c, a)) / area2


# ---------------------------------------------------------------- path output


def circle(centre, r, n=18):
    return [(centre[0] + r * math.cos(2 * math.pi * i / n),
             centre[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def catmull(pts, closed=True, tension=6.0):
    """Catmull-Rom through the points, emitted as cubic beziers."""
    n = len(pts)
    if n < 3:
        return ""

    def P(i):
        if closed:
            return pts[i % n]
        return pts[max(0, min(n - 1, i))]

    d = ["M%.1f %.1f" % pts[0]]
    last = n if closed else n - 1
    for i in range(last):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        b1 = add(p1, mul(sub(p2, p0), 1.0 / tension))
        b2 = sub(p2, mul(sub(p3, p1), 1.0 / tension))
        d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (b1[0], b1[1], b2[0], b2[1], p2[0], p2[1]))
    if closed:
        d.append("Z")
    return "".join(d)


def ribbon(centre, width_fn, samples=44, clamp=1.55):
    """
    Offset `centre` by +/- width/2 along its normals and close the two sides
    into one outline. `width_fn(t)` takes t in 0..1.
    """
    c = resample(centre, samples)
    tg = tangents(c)
    n = len(c)
    left, right = [], []
    for i, p in enumerate(c):
        t = i / (n - 1)
        w = width_fn(t)
        if 0 < i < n - 1:  # keep the inside edge from crossing the curve centre
            R = circumradius(c[i - 1], p, c[i + 1])
            w = min(w, clamp * R)
        nrm = perp(tg[i])
        left.append(add(p, mul(nrm, w / 2)))
        right.append(add(p, mul(nrm, -w / 2)))

    return list(left) + list(reversed(right))


def offset_line(centre, shift_fn, samples=44):
    """Shift a centre-line sideways (for ribs and edge highlights)."""
    c = resample(centre, samples)
    tg = tangents(c)
    n = len(c)
    out = []
    for i, p in enumerate(c):
        t = i / (n - 1)
        out.append(add(p, mul(perp(tg[i]), shift_fn(t))))
    return out


def trim(pts, t0=0.0, t1=1.0):
    n = len(pts)
    i0 = max(0, int(round(t0 * (n - 1))))
    i1 = min(n - 1, int(round(t1 * (n - 1))))
    if i1 - i0 < 2:
        i1 = min(n - 1, i0 + 2)
    return pts[i0:i1 + 1]


def xform(pts, translate=(0, 0), angle=0.0, scale=1.0, flip=False):
    """Point-level transform. The pattern itself composes copies with SVG
    `transform` on `<use>` instead, which keeps the files small -- this is here
    for one-off geometry work in tools/debug.py."""
    out = []
    for p in pts:
        q = (-p[0], p[1]) if flip else p
        q = mul(q, scale)
        q = rot(q, angle)
        out.append(add(q, translate))
    return out
