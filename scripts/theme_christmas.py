"""Original, generic, child-safe outline motifs for the Christmas coloring theme.

Every motif is drawn procedurally with bold outlines, a kawaii smiling face where
the subject allows one, and large simple regions that stay colorable for ages 4-8.
Only generic public-domain Christmas subjects are used; no trademarked characters.
"""
from __future__ import annotations
import math

CHRISTMAS = [
    "santa hat", "christmas tree", "ornament", "snowman", "gift box",
    "candy cane", "stocking", "reindeer", "jingle bell", "snowflake",
    "gingerbread man", "star", "wreath", "candle", "hot cocoa",
    "mitten", "winter penguin", "elf hat", "sleigh", "angel",
    "string lights", "christmas cookie", "holly", "present stack", "nutcracker",
    "dove", "snow globe", "fireplace", "winter sweater", "gift bow",
    "toy drum", "toy train", "christmas pudding", "wrapped candy", "mistletoe",
    "baubles", "ribbon curls", "scarf", "ice skate", "snowball pile",
    "chimney", "north pole sign", "santa mailbox", "cookie plate", "winter beanie",
    "garland", "christmas puppy", "christmas cracker", "lantern", "bell pair",
]

def _line(draw, pts, width):
    draw.line(list(pts), fill=0, width=width, joint="curve")

def _ellipse(draw, box, width):
    draw.ellipse(box, outline=0, width=width)

def _rect(draw, box, width, radius=0):
    if radius:
        draw.rounded_rectangle(box, radius=radius, outline=0, width=width)
    else:
        draw.rectangle(box, outline=0, width=width)

def _poly(draw, pts, width):
    points = list(pts)
    if points and points[0] != points[-1]:
        points.append(points[0])
    _line(draw, points, width)

def _bezier(p0, p1, p2, p3, steps=36):
    out = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        out.append((round(x), round(y)))
    return out

def _face(draw, fx, fy, s, width, scale=1.0):
    """Kawaii face: shiny filled eyes, wide smile, colorable cheek ovals."""
    s = s * scale
    eye_dx, eye_rx, eye_ry = s*.16, s*.055, s*.08
    for ex in (fx-eye_dx, fx+eye_dx):
        draw.ellipse((ex-eye_rx, fy-eye_ry, ex+eye_rx, fy+eye_ry), fill=0)
        hl = eye_rx*.42
        draw.ellipse((ex-eye_rx*.4-hl, fy-eye_ry*.45-hl, ex-eye_rx*.4+hl, fy-eye_ry*.45+hl), fill="white")
    mw, mh = s*.13, s*.11
    my = fy + s*.15
    draw.arc((fx-mw, my-mh, fx+mw, my+mh*1.25), start=10, end=170, fill=0, width=max(4, int(width*.55)))
    for cxo in (fx-s*.31, fx+s*.31):
        crx, cry = s*.08, s*.055
        draw.ellipse((cxo-crx, fy+s*.10-cry, cxo+crx, fy+s*.10+cry), outline=0, width=max(4, width//3))

def _star_pts(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def _snowcap(draw, x0, y, x1, width, dips=3):
    """A simple wavy snow line from x0 to x1 at height y."""
    span = (x1 - x0) / dips
    pts = [(x0, y)]
    for i in range(dips):
        pts += _bezier((x0 + i*span, y), (x0 + (i+.3)*span, y + span*.28),
                       (x0 + (i+.7)*span, y + span*.28), (x0 + (i+1)*span, y))[1:]
    _line(draw, pts, width)

def _christmas(draw, name, cx, cy, s, w, index):
    x, y = cx, cy
    if name == "santa hat":
        _rect(draw, (x-s*.4, y+s*.12, x+s*.4, y+s*.34), w, radius=s*.06)
        pts = _bezier((x-s*.38, y+s*.14), (x-s*.3, y-s*.35), (x+s*.05, y-s*.52), (x+s*.3, y-s*.42))
        pts += _bezier((x+s*.3, y-s*.42), (x+s*.5, y-s*.34), (x+s*.42, y-s*.12), (x+s*.38, y+s*.14))[1:]
        _line(draw, pts, w)
        _ellipse(draw, (x+s*.16, y-s*.52, x+s*.44, y-s*.3), w)
        _face(draw, x, y-s*.02, s*.9, w)
    elif name == "christmas tree":
        tiers = ((-.62, -.28, .26), (-.3, .0, .36), (.0, .28, .46))
        for top, base, half in tiers:
            pts = [(x, y+s*top)]
            pts += _bezier((x, y+s*top), (x-s*half*.55, y+s*(top+base)/2), (x-s*half*.95, y+s*base*.85), (x-s*half, y+s*base))[1:]
            pts += _bezier((x-s*half, y+s*base), (x-s*half*.5, y+s*(base-.06)), (x-s*half*.25, y+s*(base+.04)), (x, y+s*(base-.02)))[1:]
            pts += _bezier((x, y+s*(base-.02)), (x+s*half*.25, y+s*(base+.04)), (x+s*half*.5, y+s*(base-.06)), (x+s*half, y+s*base))[1:]
            pts += _bezier((x+s*half, y+s*base), (x+s*half*.95, y+s*base*.85), (x+s*half*.55, y+s*(top+base)/2), (x, y+s*top))[1:]
            _line(draw, pts, w)
        _rect(draw, (x-s*.08, y+s*.28, x+s*.08, y+s*.45), w)
        _poly(draw, _star_pts(x, y-s*.7, s*.13, s*.05), max(4, w//2))
        for bx, by in ((-.13, -.4), (.12, -.12), (-.2, .1), (.18, .12), (0, -.02)):
            _ellipse(draw, (x+s*bx-s*.05, y+s*by-s*.05, x+s*bx+s*.05, y+s*by+s*.05), max(4, w//2))
    elif name == "ornament":
        _rect(draw, (x-s*.09, y-s*.52, x+s*.09, y-s*.38), w, radius=s*.02)
        draw.arc((x-s*.05, y-s*.62, x+s*.05, y-s*.5), start=180, end=360, fill=0, width=w)
        _ellipse(draw, (x-s*.38, y-s*.4, x+s*.38, y+s*.36), w)
        _line(draw, _bezier((x-s*.3, y-s*.1), (x-s*.1, y-s*.22), (x+s*.1, y+.0), (x+s*.3, y-s*.12)), max(4, w//2))
        _line(draw, _bezier((x-s*.3, y+s*.12), (x-s*.1, y+.0), (x+s*.1, y+s*.22), (x+s*.3, y+s*.1)), max(4, w//2))
    elif name == "snowman":
        _ellipse(draw, (x-s*.3, y-s*.55, x+s*.3, y+s*.05), w)
        _ellipse(draw, (x-s*.4, y, x+s*.4, y+s*.55), w)
        _poly(draw, [(x+s*.02, y-s*.32), (x+s*.22, y-s*.27), (x+s*.02, y-s*.22)], max(4, w//2))
        _line(draw, [(x-s*.38, y+s*.12), (x-s*.6, y-s*.05)], w)
        _line(draw, [(x+s*.38, y+s*.12), (x+s*.6, y-s*.05)], w)
        _rect(draw, (x-s*.32, y-s*.02, x+s*.32, y+s*.1), w, radius=s*.04)
        for by in (.2, .32, .44):
            _ellipse(draw, (x-s*.03, y+s*by-s*.03, x+s*.03, y+s*by+s*.03), max(3, w//2))
        _face(draw, x, y-s*.33, s*.8, w)
    elif name == "gift box":
        _rect(draw, (x-s*.35, y-s*.1, x+s*.35, y+s*.5), w)
        _rect(draw, (x-s*.42, y-s*.28, x+s*.42, y-s*.1), w, radius=s*.03)
        _line(draw, [(x, y-s*.28), (x, y+s*.5)], w)
        l1 = _bezier((x, y-s*.28), (x-s*.35, y-s*.55), (x-s*.45, y-s*.2), (x, y-s*.28))
        _line(draw, l1, max(4, w//2))
        l2 = _bezier((x, y-s*.28), (x+s*.35, y-s*.55), (x+s*.45, y-s*.2), (x, y-s*.28))
        _line(draw, l2, max(4, w//2))
    elif name == "candy cane":
        draw.arc((x-s*.28, y-s*.55, x+s*.28, y-s*.05), start=150, end=360, width=w, fill=0)
        _line(draw, [(x-s*.21, y-s*.25), (x-s*.21, y+s*.55)], w)
        _line(draw, [(x-s*.06, y-s*.3), (x-s*.06, y+s*.55)], w)
        _line(draw, [(x-s*.21, y+s*.55), (x-s*.06, y+s*.55)], w)
        for sy in (-.05, .15, .35):
            _line(draw, [(x-s*.21, y+s*sy), (x-s*.06, y+s*(sy-.06))], max(4, w//2))
    elif name == "stocking":
        _rect(draw, (x-s*.3, y-s*.55, x+s*.3, y-s*.35), w, radius=s*.04)
        pts = [(x-s*.22, y-s*.35), (x-s*.22, y-s*.02)]
        pts += _bezier((x-s*.22, y-s*.02), (x-s*.24, y+s*.28), (x-s*.05, y+s*.45), (x+s*.08, y+s*.42))[1:]
        pts += _bezier((x+s*.08, y+s*.42), (x+s*.3, y+s*.38), (x+s*.34, y+s*.2), (x+s*.24, y+s*.08))[1:]
        pts += _bezier((x+s*.24, y+s*.08), (x+s*.18, y-s*.02), (x+s*.14, y-s*.1), (x+s*.14, y-s*.35))[1:]
        _line(draw, pts, w)
        _line(draw, _bezier((x-s*.22, y+s*.18), (x-s*.05, y+s*.26), (x+s*.1, y+s*.24), (x+s*.2, y+s*.14)), max(4, w//2))
        _face(draw, x, y-s*.22, s*.7, w)
    elif name == "reindeer":
        for flip in (-1, 1):
            bx = x + flip*s*.18
            _line(draw, [(bx, y-s*.42), (bx+flip*s*.05, y-s*.62)], w)
            _line(draw, [(bx+flip*s*.02, y-s*.52), (bx+flip*s*.16, y-s*.6)], w)
            _line(draw, [(bx+flip*s*.04, y-s*.6), (bx+flip*s*.14, y-s*.72)], w)
        _ellipse(draw, (x-s*.3, y-s*.45, x+s*.3, y+s*.15), w)
        _ellipse(draw, (x-s*.16, y-s*.05, x+s*.16, y+s*.22), max(4, w//2))
        _ellipse(draw, (x-s*.05, y+s*.03, x+s*.05, y+s*.13), max(4, w//2))
        _face(draw, x, y-s*.22, s*.85, w)
    elif name == "jingle bell":
        draw.arc((x-s*.06, y-s*.6, x+s*.06, y-s*.44), start=180, end=360, fill=0, width=w)
        pts = _bezier((x-s*.12, y-s*.44), (x-s*.42, y-s*.3), (x-s*.42, y+s*.15), (x-s*.4, y+s*.3))
        pts += _bezier((x-s*.4, y+s*.3), (x-s*.2, y+s*.44), (x+s*.2, y+s*.44), (x+s*.4, y+s*.3))[1:]
        pts += _bezier((x+s*.4, y+s*.3), (x+s*.42, y+s*.15), (x+s*.42, y-s*.3), (x+s*.12, y-s*.44))[1:]
        _line(draw, pts, w)
        _ellipse(draw, (x-s*.09, y+s*.3, x+s*.09, y+s*.48), max(4, w//2))
        _line(draw, [(x-s*.36, y+s*.05), (x+s*.36, y+s*.05)], max(4, w//2))
    elif name == "snowflake":
        for i in range(6):
            a = math.radians(i*60)
            dx, dy = math.cos(a), math.sin(a)
            _line(draw, [(x-dx*s*.45, y-dy*s*.45), (x+dx*s*.45, y+dy*s*.45)], w)
            for t in (.25, .45):
                bx, by = x+dx*s*t, y+dy*s*t
                for ba in (a+math.radians(35), a-math.radians(35)):
                    _line(draw, [(bx, by), (bx+math.cos(ba)*s*.12, by+math.sin(ba)*s*.12)], max(4, w//2))
        _ellipse(draw, (x-s*.07, y-s*.07, x+s*.07, y+s*.07), max(4, w//2))
    elif name == "gingerbread man":
        _ellipse(draw, (x-s*.22, y-s*.55, x+s*.22, y-s*.12), w)
        _rect(draw, (x-s*.2, y-s*.12, x+s*.2, y+s*.28), w, radius=s*.1)
        _line(draw, _bezier((x-s*.2, y-s*.05), (x-s*.42, y-s*.02), (x-s*.45, y+s*.1), (x-s*.42, y+s*.15)), w)
        _line(draw, _bezier((x+s*.2, y-s*.05), (x+s*.42, y-s*.02), (x+s*.45, y+s*.1), (x+s*.42, y+s*.15)), w)
        _line(draw, _bezier((x-s*.12, y+s*.28), (x-s*.16, y+s*.45), (x-s*.14, y+s*.55), (x-s*.1, y+s*.56)), w)
        _line(draw, _bezier((x+s*.12, y+s*.28), (x+s*.16, y+s*.45), (x+s*.14, y+s*.55), (x+s*.1, y+s*.56)), w)
        for by in (.0, .12):
            _ellipse(draw, (x-s*.03, y+s*by-s*.03, x+s*.03, y+s*by+s*.03), max(3, w//2))
        _face(draw, x, y-s*.33, s*.75, w)
    elif name == "star":
        _poly(draw, _star_pts(x, y, s*.5, s*.2), w)
        _face(draw, x, y+s*.02, s*.9, w)
    elif name == "wreath":
        _ellipse(draw, (x-s*.45, y-s*.45, x+s*.45, y+s*.45), w)
        _ellipse(draw, (x-s*.24, y-s*.24, x+s*.24, y+s*.24), w)
        for i in range(6):
            a = math.radians(i*60 + 30)
            bx, by = x+math.cos(a)*s*.345, y+math.sin(a)*s*.345
            _ellipse(draw, (bx-s*.045, by-s*.045, bx+s*.045, by+s*.045), max(3, w//2))
        l1 = _bezier((x, y+s*.5), (x-s*.25, y+s*.42), (x-s*.28, y+s*.62), (x, y+s*.52))
        _line(draw, l1, max(4, w//2))
        l2 = _bezier((x, y+s*.5), (x+s*.25, y+s*.42), (x+s*.28, y+s*.62), (x, y+s*.52))
        _line(draw, l2, max(4, w//2))
    elif name == "candle":
        _rect(draw, (x-s*.14, y-s*.2, x+s*.14, y+s*.45), w)
        _line(draw, _bezier((x-s*.14, y-s*.05), (x-s*.05, y-s*.12), (x+s*.05, y+.02), (x+s*.14, y-s*.08)), max(4, w//2))
        pts = _bezier((x, y-s*.58), (x-s*.14, y-s*.38), (x-s*.1, y-s*.26), (x, y-s*.24))
        pts += _bezier((x, y-s*.24), (x+s*.1, y-s*.26), (x+s*.14, y-s*.38), (x, y-s*.58))[1:]
        _line(draw, pts, w)
        draw.arc((x-s*.28, y+s*.38, x+s*.28, y+s*.55), start=0, end=180, fill=0, width=w)
    elif name == "hot cocoa":
        _rect(draw, (x-s*.32, y-s*.25, x+s*.32, y+s*.45), w, radius=s*.08)
        draw.arc((x+s*.28, y-s*.08, x+s*.52, y+s*.28), start=-90, end=90, fill=0, width=w)
        _line(draw, _bezier((x-s*.28, y-s*.25), (x-s*.1, y-s*.34), (x+s*.1, y-s*.18), (x+s*.28, y-s*.25)), max(4, w//2))
        for sx in (-.12, .1):
            _line(draw, _bezier((x+s*sx, y-s*.42), (x+s*(sx-.05), y-s*.5), (x+s*(sx+.05), y-s*.56), (x+s*sx, y-s*.64)), max(4, w//2))
        _rect(draw, (x-s*.1, y-s*.36, x+s*.02, y-s*.26), max(4, w//2), radius=s*.02)
    elif name == "mitten":
        pts = _bezier((x-s*.22, y+s*.3), (x-s*.34, y-.0*s), (x-s*.3, y-s*.3), (x-s*.05, y-s*.42))
        pts += _bezier((x-s*.05, y-s*.42), (x+s*.2, y-s*.5), (x+s*.32, y-s*.3), (x+s*.28, y-s*.05))[1:]
        pts += _bezier((x+s*.28, y-s*.05), (x+s*.42, y+s*.05), (x+s*.38, y+s*.22), (x+s*.2, y+s*.2))[1:]
        _line(draw, pts + [(x+s*.2, y+s*.3)], w)
        _line(draw, [(x-s*.22, y+s*.3), (x+s*.2, y+s*.3)], w)
        for ly in (.36, .44):
            _line(draw, [(x-s*.21, y+s*ly), (x+s*.19, y+s*ly)], max(4, w//2))
    elif name == "winter penguin":
        _ellipse(draw, (x-s*.3, y-s*.5, x+s*.3, y+s*.45), w)
        _ellipse(draw, (x-s*.18, y-s*.2, x+s*.18, y+s*.4), max(4, w//2))
        _line(draw, _bezier((x-s*.3, y-s*.1), (x-s*.48, y+s*.05), (x-s*.44, y+s*.3), (x-s*.34, y+s*.32)), w)
        _line(draw, _bezier((x+s*.3, y-s*.1), (x+s*.48, y+s*.05), (x+s*.44, y+s*.3), (x+s*.34, y+s*.32)), w)
        _rect(draw, (x-s*.3, y-s*.18, x+s*.3, y-s*.06), w, radius=s*.04)
        _poly(draw, [(x-s*.05, y-s*.32), (x+s*.12, y-s*.27), (x-s*.05, y-s*.22)], max(4, w//2))
        for fx in (-.12, .08):
            _line(draw, [(x+s*fx, y+s*.45), (x+s*fx-s*.04, y+s*.52)], max(4, w//2))
        _face(draw, x, y-s*.36, s*.7, w)
    elif name == "elf hat":
        pts = _bezier((x-s*.35, y+s*.15), (x-s*.25, y-s*.3), (x+s*.05, y-s*.55), (x+s*.32, y-s*.45))
        pts += _bezier((x+s*.32, y-s*.45), (x+s*.45, y-s*.4), (x+s*.42, y-s*.25), (x+s*.3, y-s*.3))[1:]
        _line(draw, pts, w)
        _ellipse(draw, (x+s*.38, y-s*.38, x+s*.56, y-s*.22), max(4, w//2))
        _poly(draw, [(x-s*.38, y+s*.15), (x-s*.28, y+s*.02), (x-s*.18, y+s*.15), (x-s*.08, y+s*.02),
                     (x+s*.02, y+s*.15), (x+s*.12, y+s*.02), (x+s*.22, y+s*.15), (x+s*.3, y+s*.05)], w)
        _face(draw, x-s*.05, y-s*.08, s*.8, w)
    elif name == "sleigh":
        _rect(draw, (x-s*.38, y-s*.2, x+s*.3, y+s*.15), w, radius=s*.05)
        _line(draw, _bezier((x+s*.3, y+s*.15), (x+s*.45, y+s*.05), (x+s*.48, y-s*.15), (x+s*.42, y-s*.3)), w)
        _line(draw, [(x-s*.45, y+s*.42), (x+s*.45, y+s*.42)], w)
        _line(draw, _bezier((x+s*.45, y+s*.42), (x+s*.55, y+s*.4), (x+s*.58, y+s*.3), (x+s*.55, y+s*.22)), w)
        _line(draw, [(x-s*.3, y+s*.15), (x-s*.3, y+s*.42)], w)
        _line(draw, [(x+s*.2, y+s*.15), (x+s*.2, y+s*.42)], w)
        _line(draw, [(x-s*.38, y-s*.05), (x+s*.3, y-s*.05)], max(4, w//2))
    elif name == "angel":
        _ellipse(draw, (x-s*.14, y-s*.6, x+s*.14, y-s*.32), w)
        draw.arc((x-s*.12, y-s*.78, x+s*.12, y-s*.62), start=0, end=360, fill=0, width=max(4, w//2))
        _poly(draw, [(x, y-s*.32), (x-s*.32, y+s*.5), (x+s*.32, y+s*.5)], w)
        _line(draw, _bezier((x-s*.05, y-s*.25), (x-s*.42, y-s*.35), (x-s*.5, y+s*.05), (x-s*.3, y+s*.15)), w)
        _line(draw, _bezier((x+s*.05, y-s*.25), (x+s*.42, y-s*.35), (x+s*.5, y+s*.05), (x+s*.3, y+s*.15)), w)
        _face(draw, x, y-s*.46, s*.6, w)
    elif name == "string lights":
        wire = _bezier((x-s*.5, y-s*.3), (x-s*.2, y+s*.15), (x+s*.2, y+s*.15), (x+s*.5, y-s*.3))
        _line(draw, wire, max(4, w//2))
        for t in (.15, .32, .5, .68, .85):
            i = int(t*36)
            bx, by = wire[i]
            _line(draw, [(bx, by), (bx, by+s*.08)], max(4, w//2))
            _ellipse(draw, (bx-s*.06, by+s*.08, bx+s*.06, by+s*.24), w)
    elif name == "christmas cookie":
        _ellipse(draw, (x-s*.4, y-s*.4, x+s*.4, y+s*.4), w)
        draw.arc((x+s*.18, y-s*.42, x+s*.52, y-s*.1), start=270, end=90, fill="white", width=int(w*2.2))
        draw.arc((x+s*.18, y-s*.42, x+s*.52, y-s*.1), start=270, end=90, fill=0, width=max(4, w//2))
        for bx, by in ((-.15, -.1), (.1, .15), (-.2, .2), (.05, -.25)):
            _ellipse(draw, (x+s*bx-s*.045, y+s*by-s*.045, x+s*bx+s*.045, y+s*by+s*.045), max(4, w//2))
        _face(draw, x-s*.05, y, s*.8, w)
    elif name == "holly":
        for flip in (-1, 1):
            pts = [(x, y+s*.05)]
            spikes = 5
            for i in range(spikes):
                t0 = i / spikes
                t1 = (i + .5) / spikes
                t2 = (i + 1) / spikes
                bx0 = x + flip*s*.48*t0
                by0 = y + s*.05 - s*.55*t0
                bx1 = x + flip*s*(.48*t1 + .1)
                by1 = y + s*.05 - s*.55*t1 - s*.04
                bx2 = x + flip*s*.48*t2
                by2 = y + s*.05 - s*.55*t2
                pts += _bezier((bx0, by0), (bx1, by1), (bx1, by1), (bx2, by2))[1:]
            pts += _bezier((x+flip*s*.48, y-s*.5), (x+flip*s*.25, y-s*.2), (x+flip*s*.15, y+s*.05), (x, y+s*.05))[1:]
            _line(draw, pts, w)
        for bx in (-.1, .0, .1):
            _ellipse(draw, (x+s*bx-s*.06, y-s*.02, x+s*bx+s*.06, y+s*.1), max(4, w//2))
    elif name == "present stack":
        _rect(draw, (x-s*.4, y+s*.1, x+s*.4, y+s*.55), w)
        _line(draw, [(x, y+s*.1), (x, y+s*.55)], max(4, w//2))
        _rect(draw, (x-s*.28, y-s*.18, x+s*.28, y+s*.1), w)
        _line(draw, [(x, y-s*.18), (x, y+s*.1)], max(4, w//2))
        _rect(draw, (x-s*.16, y-s*.42, x+s*.16, y-s*.18), w)
        l1 = _bezier((x, y-s*.42), (x-s*.22, y-s*.6), (x-s*.28, y-s*.38), (x, y-s*.42))
        _line(draw, l1, max(4, w//2))
        l2 = _bezier((x, y-s*.42), (x+s*.22, y-s*.6), (x+s*.28, y-s*.38), (x, y-s*.42))
        _line(draw, l2, max(4, w//2))
    elif name == "nutcracker":
        _rect(draw, (x-s*.2, y-s*.6, x+s*.2, y-s*.38), w)
        _line(draw, [(x-s*.2, y-s*.5), (x+s*.2, y-s*.5)], max(4, w//2))
        _rect(draw, (x-s*.24, y-s*.38, x+s*.24, y-s*.05), w, radius=s*.04)
        _rect(draw, (x-s*.26, y-s*.05, x+s*.26, y+s*.5), w)
        _line(draw, [(x-s*.26, y+s*.2), (x+s*.26, y+s*.2)], max(4, w//2))
        _face(draw, x, y-s*.22, s*.6, w)
    elif name == "dove":
        _ellipse(draw, (x-s*.35, y-s*.15, x+s*.15, y+s*.35), w)
        _ellipse(draw, (x+s*.05, y-s*.45, x+s*.4, y-s*.12), w)
        _poly(draw, [(x+s*.38, y-s*.32), (x+s*.55, y-s*.25), (x+s*.38, y-s*.2)], max(4, w//2))
        _line(draw, _bezier((x-s*.1, y-s*.05), (x-s*.02, y-s*.28), (x+s*.12, y-s*.3), (x+s*.1, y-s*.1)), max(4, w//2))
        _poly(draw, [(x-s*.32, y+s*.1), (x-s*.55, y+s*.0), (x-s*.5, y+s*.15), (x-s*.58, y+s*.28), (x-s*.32, y+s*.25)], w)
        _ellipse(draw, (x+s*.26-s*.025, y-s*.3-s*.025, x+s*.26+s*.025, y-s*.3+s*.025), max(3, w//2))
        _line(draw, [(x+s*.52, y-s*.28), (x+s*.62, y-s*.36)], max(4, w//2))
        _line(draw, _bezier((x+s*.62, y-s*.36), (x+s*.68, y-s*.42), (x+s*.7, y-s*.38), (x+s*.72, y-s*.44)), max(3, w//2))
    elif name == "snow globe":
        _ellipse(draw, (x-s*.38, y-s*.55, x+s*.38, y+s*.2), w)
        _rect(draw, (x-s*.32, y+s*.2, x+s*.32, y+s*.5), w, radius=s*.05)
        _poly(draw, [(x, y-s*.25), (x-s*.15, y+s*.05), (x+s*.15, y+s*.05)], max(4, w//2))
        _line(draw, [(x, y+s*.05), (x, y+s*.15)], max(4, w//2))
        for bx, by in ((-.2, -.35), (.18, -.15), (-.1, .0), (.25, -.4)):
            r = s*.02
            draw.ellipse((x+s*bx-r, y+s*by-r, x+s*bx+r, y+s*by+r), fill=0)
    elif name == "fireplace":
        _rect(draw, (x-s*.45, y-s*.4, x+s*.45, y+s*.55), w)
        _rect(draw, (x-s*.25, y-s*.05, x+s*.25, y+s*.55), w)
        pts = _bezier((x, y+s*.45), (x-s*.18, y+s*.3), (x-s*.12, y+s*.1), (x, y+s*.05))
        pts += _bezier((x, y+s*.05), (x+s*.12, y+s*.1), (x+s*.18, y+s*.3), (x, y+s*.45))[1:]
        _line(draw, pts, w)
        _line(draw, [(x-s*.45, y-s*.28), (x+s*.45, y-s*.28)], w)
        _line(draw, _bezier((x-s*.1, y-s*.28), (x-s*.12, y-s*.05), (x-s*.02, y-s*.02), (x-s*.02, y+s*.1)), max(4, w//2))
    elif name == "winter sweater":
        pts = [(x-s*.18, y-s*.5), (x+s*.18, y-s*.5), (x+s*.42, y-s*.35), (x+s*.5, y-s*.05),
               (x+s*.38, y+s*.02), (x+s*.3, y-s*.12), (x+s*.3, y+s*.5), (x-s*.3, y+s*.5),
               (x-s*.3, y-s*.12), (x-s*.38, y+s*.02), (x-s*.5, y-s*.05), (x-s*.42, y-s*.35)]
        _poly(draw, pts, w)
        draw.arc((x-s*.18, y-s*.56, x+s*.18, y-s*.42), start=0, end=180, fill=0, width=w)
        for ly in (-.05, .05):
            _poly(draw, [(x-s*.3, y+s*ly), (x-s*.2, y+s*(ly-.08)), (x-s*.1, y+s*ly), (x, y+s*(ly-.08)),
                         (x+s*.1, y+s*ly), (x+s*.2, y+s*(ly-.08)), (x+s*.3, y+s*ly)], max(4, w//2))
        _line(draw, [(x-s*.3, y+s*.42), (x+s*.3, y+s*.42)], max(4, w//2))
    elif name == "gift bow":
        l1 = _bezier((x, y), (x-s*.45, y-s*.35), (x-s*.55, y+s*.15), (x, y))
        _line(draw, l1, w)
        l2 = _bezier((x, y), (x+s*.45, y-s*.35), (x+s*.55, y+s*.15), (x, y))
        _line(draw, l2, w)
        _ellipse(draw, (x-s*.09, y-s*.09, x+s*.09, y+s*.09), w)
        _line(draw, _bezier((x-s*.05, y+s*.08), (x-s*.2, y+s*.3), (x-s*.15, y+s*.45), (x-s*.25, y+s*.55)), max(4, w//2))
        _line(draw, _bezier((x+s*.05, y+s*.08), (x+s*.2, y+s*.3), (x+s*.15, y+s*.45), (x+s*.25, y+s*.55)), max(4, w//2))
    elif name == "toy drum":
        draw.ellipse((x-s*.32, y-s*.42, x+s*.32, y-s*.2), outline=0, width=w)
        _line(draw, [(x-s*.32, y-s*.31), (x-s*.32, y+s*.35)], w)
        _line(draw, [(x+s*.32, y-s*.31), (x+s*.32, y+s*.35)], w)
        draw.arc((x-s*.32, y+s*.2, x+s*.32, y+s*.42), start=0, end=180, fill=0, width=w)
        for i in range(4):
            t = -.24 + i*.16
            _line(draw, [(x+s*t, y-s*.27), (x+s*(t+.12), y+s*.36)], max(4, w//2))
        _line(draw, [(x-s*.15, y-s*.55), (x-s*.05, y-s*.42)], max(4, w//2))
        _line(draw, [(x+s*.15, y-s*.55), (x+s*.05, y-s*.42)], max(4, w//2))
    elif name == "toy train":
        _rect(draw, (x-s*.45, y-s*.05, x+s*.05, y+s*.3), w, radius=s*.04)
        _rect(draw, (x-s*.05, y-s*.3, x+s*.3, y+s*.3), w, radius=s*.04)
        _rect(draw, (x-s*.42, y-s*.22, x-s*.32, y-s*.05), w)
        for wx in (-.35, -.15, .12):
            _ellipse(draw, (x+s*wx-s*.08, y+s*.3-s*.08, x+s*wx+s*.08, y+s*.3+s*.08), w)
        for i, sx in enumerate((-.45, -.55, -.65)):
            r = s*(.04+.02*i)
            _ellipse(draw, (x+s*sx-r, y-s*(.32+.12*i)-r, x+s*sx+r, y-s*(.32+.12*i)+r), max(3, w//2))
    elif name == "christmas pudding":
        pts = _bezier((x-s*.35, y+s*.4), (x-s*.42, y-.0*s), (x-s*.3, y-s*.35), (x, y-s*.38))
        pts += _bezier((x, y-s*.38), (x+s*.3, y-s*.35), (x+s*.42, y-.0*s), (x+s*.35, y+s*.4))[1:]
        _line(draw, pts + [(x-s*.35, y+s*.4)], w)
        _line(draw, _bezier((x-s*.3, y-s*.28), (x-s*.15, y-s*.12), (x-s*.05, y-s*.25), (x+s*.05, y-s*.05)), max(4, w//2))
        _line(draw, _bezier((x+s*.05, y-s*.05), (x+s*.15, y-s*.22), (x+s*.22, y-s*.1), (x+s*.3, y-s*.28)), max(4, w//2))
        _ellipse(draw, (x-s*.04, y-s*.5, x+s*.04, y-s*.42), max(4, w//2))
    elif name == "wrapped candy":
        _ellipse(draw, (x-s*.22, y-s*.18, x+s*.22, y+s*.18), w)
        _poly(draw, [(x-s*.22, y-s*.12), (x-s*.45, y-s*.25), (x-s*.42, y), (x-s*.45, y+s*.25), (x-s*.22, y+s*.12)], w)
        _poly(draw, [(x+s*.22, y-s*.12), (x+s*.45, y-s*.25), (x+s*.42, y), (x+s*.45, y+s*.25), (x+s*.22, y+s*.12)], w)
        _line(draw, _bezier((x-s*.1, y-s*.18), (x-s*.02, y-.0*s), (x-s*.02, y-.0*s), (x-s*.1, y+s*.18)), max(4, w//2))
        _line(draw, _bezier((x+s*.1, y-s*.18), (x+s*.02, y-.0*s), (x+s*.02, y-.0*s), (x+s*.1, y+s*.18)), max(4, w//2))
    elif name == "mistletoe":
        _line(draw, [(x, y-s*.55), (x, y-s*.35)], w)
        l1 = _bezier((x, y-s*.32), (x-s*.2, y-s*.3), (x-s*.25, y-s*.15), (x, y-s*.3))
        _line(draw, l1, max(4, w//2))
        l2 = _bezier((x, y-s*.32), (x+s*.2, y-s*.3), (x+s*.25, y-s*.15), (x, y-s*.3))
        _line(draw, l2, max(4, w//2))
        for flip in (-1, 1):
            pts = _bezier((x, y-s*.1), (x+flip*s*.2, y-s*.02), (x+flip*s*.38, y+s*.1), (x+flip*s*.4, y+s*.25))
            pts += _bezier((x+flip*s*.4, y+s*.25), (x+flip*s*.25, y+s*.22), (x+flip*s*.12, y+s*.28), (x, y+s*.2))[1:]
            _line(draw, pts, w)
        _ellipse(draw, (x-s*.05, y-s*.02, x+s*.05, y+s*.08), max(4, w//2))
    elif name == "baubles":
        for bx, by, br in ((-.22, -.15, .2), (.18, .05, .16), (-.02, .32, .13)):
            _line(draw, [(x+s*bx, y-s*.55), (x+s*bx, y+s*by-s*br-s*.06)], max(4, w//2))
            _rect(draw, (x+s*bx-s*.05, y+s*by-s*br-s*.06, x+s*bx+s*.05, y+s*by-s*br), max(4, w//2))
            _ellipse(draw, (x+s*bx-s*br, y+s*by-s*br, x+s*bx+s*br, y+s*by+s*br), w)
    elif name == "ribbon curls":
        for i, off in enumerate((-.3, -.1, .1, .3)):
            pts = _bezier((x+s*off, y-s*.5), (x+s*(off-.15), y-s*.2), (x+s*(off+.15), y+.0*s),
                          (x+s*off, y+s*.15))
            pts += _bezier((x+s*off, y+s*.15), (x+s*(off-.12), y+s*.3), (x+s*(off+.1), y+s*.42),
                           (x+s*off, y+s*.5))[1:]
            _line(draw, pts, w)
    elif name == "scarf":
        pts = _bezier((x-s*.5, y-s*.3), (x-s*.1, y-s*.42), (x+s*.3, y-s*.35), (x+s*.42, y-s*.15))
        pts += _bezier((x+s*.42, y-s*.15), (x+s*.45, y+.0*s), (x+s*.3, y+.0*s), (x+s*.32, y-s*.08))[1:]
        pts += _bezier((x+s*.32, y-s*.08), (x+s*.1, y-s*.22), (x-s*.15, y-s*.25), (x-s*.42, y-s*.12))[1:]
        _line(draw, pts + [(x-s*.5, y-s*.3)], w)
        _line(draw, _bezier((x+s*.32, y-s*.05), (x+s*.42, y+s*.2), (x+s*.4, y+s*.4), (x+s*.34, y+s*.5)), w)
        _line(draw, _bezier((x+s*.22, y-s*.02), (x+s*.3, y+s*.2), (x+s*.28, y+s*.4), (x+s*.22, y+s*.48)), w)
        for fx in (.18, .26, .34):
            _line(draw, [(x+s*fx, y+s*.48), (x+s*(fx-.02), y+s*.58)], max(4, w//2))
        _line(draw, [(x-s*.25, y-s*.2), (x-s*.22, y-s*.28)], max(4, w//2))
    elif name == "ice skate":
        pts = [(x-s*.3, y-s*.45), (x-s*.05, y-s*.45), (x-s*.05, y-s*.2), (x+s*.15, y-s*.12),
               (x+s*.35, y+s*.05), (x+s*.38, y+s*.2), (x+s*.3, y+s*.28), (x-s*.3, y+s*.28)]
        _poly(draw, pts, w)
        for i in range(3):
            ly = -.38 + i*.09
            _line(draw, [(x-s*.28, y+s*ly), (x-s*.08, y+s*(ly+.04))], max(4, w//2))
        _line(draw, [(x-s*.35, y+s*.42), (x+s*.45, y+s*.42)], w)
        _line(draw, [(x-s*.25, y+s*.28), (x-s*.25, y+s*.42)], max(4, w//2))
        _line(draw, [(x+s*.32, y+s*.28), (x+s*.32, y+s*.42)], max(4, w//2))
    elif name == "snowball pile":
        _ellipse(draw, (x-s*.42, y-s*.05, x-s*.05, y+s*.32), w)
        _ellipse(draw, (x-s*.05, y-s*.12, x+s*.3, y+s*.25), w)
        _ellipse(draw, (x-s*.2, y-s*.45, x+s*.15, y-s*.08), w)
        _face(draw, x-s*.02, y-s*.27, s*.7, w)
    elif name == "chimney":
        _rect(draw, (x-s*.25, y-s*.35, x+s*.25, y+s*.55), w)
        _snowcap(draw, x-s*.32, y-s*.35, x+s*.32, w)
        for ly in (-.1, .1, .3):
            _line(draw, [(x-s*.25, y+s*ly), (x+s*.25, y+s*ly)], max(4, w//2))
        for i, sx in enumerate((0, .12, .26)):
            r = s*(.05+.02*i)
            _ellipse(draw, (x+s*sx-r, y-s*(.5+.13*i)-r, x+s*sx+r, y-s*(.5+.13*i)+r), max(4, w//2))
    elif name == "north pole sign":
        _line(draw, [(x, y-s*.5), (x, y+s*.55)], w)
        _line(draw, [(x-s*.08, y-s*.5), (x-s*.08, y+s*.55)], max(4, w//2))
        for ly in (-.3, .0, .3):
            _line(draw, [(x-s*.08, y+s*ly), (x, y+s*(ly-.06))], max(4, w//2))
        _poly(draw, [(x-s*.4, y-s*.62), (x+s*.25, y-s*.62), (x+s*.4, y-s*.52), (x+s*.25, y-s*.42), (x-s*.4, y-s*.42)], w)
        _snowcap(draw, x-s*.38, y-s*.62, x+s*.22, max(4, w//2), dips=2)
        _ellipse(draw, (x-s*.12, y-s*.62, x+s*.04, y-s*.5), max(4, w//2))
    elif name == "santa mailbox":
        _rect(draw, (x-s*.3, y-s*.35, x+s*.3, y+s*.15), w, radius=s*.12)
        _line(draw, [(x, y+s*.15), (x, y+s*.55)], w)
        _rect(draw, (x-s*.15, y-s*.08, x+s*.15, y-s*.02), max(4, w//2))
        _poly(draw, [(x+s*.05, y-s*.42), (x+s*.3, y-s*.32), (x+s*.05, y-s*.22)], max(4, w//2))
        _line(draw, [(x-s*.18, y+s*.55), (x+s*.18, y+s*.55)], w)
    elif name == "cookie plate":
        draw.ellipse((x-s*.48, y-s*.02, x+s*.48, y+s*.5), outline=0, width=w)
        draw.ellipse((x-s*.38, y+s*.05, x+s*.38, y+s*.42), outline=0, width=max(4, w//2))
        for bx, by in ((-.2, .12), (.08, .2), (-.02, .02)):
            _ellipse(draw, (x+s*bx-s*.09, y+s*by-s*.09, x+s*bx+s*.09, y+s*by+s*.09), max(4, w//2))
            _ellipse(draw, (x+s*bx-s*.02, y+s*by-s*.02, x+s*bx+s*.02, y+s*by+s*.02), max(3, w//2))
        _line(draw, _bezier((x+s*.3, y-s*.1), (x+s*.35, y-s*.2), (x+s*.25, y-s*.25), (x+s*.3, y-s*.35)), max(4, w//2))
    elif name == "winter beanie":
        pts = _bezier((x-s*.35, y+s*.1), (x-s*.32, y-s*.3), (x-s*.05, y-s*.5), (x, y-s*.5))
        pts += _bezier((x, y-s*.5), (x+s*.32, y-s*.48), (x+s*.35, y-s*.2), (x+s*.35, y+s*.1))[1:]
        _line(draw, pts, w)
        _rect(draw, (x-s*.38, y+s*.1, x+s*.38, y+s*.3), w, radius=s*.05)
        _ellipse(draw, (x-s*.1, y-s*.62, x+s*.1, y-s*.45), w)
        _face(draw, x, y-s*.08, s*.8, w)
    elif name == "garland":
        wire = _bezier((x-s*.5, y-s*.35), (x-s*.2, y+s*.3), (x+s*.2, y+s*.3), (x+s*.5, y-s*.35))
        _line(draw, wire, w)
        for t in (.1, .25, .4, .55, .7, .85):
            i = int(t*36)
            bx, by = wire[i]
            _ellipse(draw, (bx-s*.04, by-s*.04, bx+s*.04, by+s*.04), max(3, w//2))
        for t in (.17, .5, .78):
            i = int(t*36)
            bx, by = wire[i]
            _line(draw, _bezier((bx, by), (bx-s*.08, by+s*.08), (bx-s*.14, by+s*.02), (bx-s*.13, by+s*.12)), max(4, w//2))
    elif name == "christmas puppy":
        _ellipse(draw, (x-s*.3, y-s*.4, x+s*.3, y+s*.2), w)
        _line(draw, _bezier((x-s*.28, y-s*.28), (x-s*.5, y-s*.2), (x-s*.48, y+s*.1), (x-s*.34, y+s*.05)), w)
        _line(draw, _bezier((x+s*.28, y-s*.28), (x+s*.5, y-s*.2), (x+s*.48, y+s*.1), (x+s*.34, y+s*.05)), w)
        _ellipse(draw, (x-s*.06, y-s*.05, x+s*.06, y+s*.07), max(4, w//2))
        pts = _bezier((x-s*.22, y-s*.34), (x-s*.1, y-s*.6), (x+s*.1, y-s*.68), (x+s*.26, y-s*.56))
        _line(draw, pts, w)
        _ellipse(draw, (x+s*.14, y-s*.68, x+s*.36, y-s*.5), max(4, w//2))
        _face(draw, x, y-s*.18, s*.85, w)
    elif name == "christmas cracker":
        _rect(draw, (x-s*.3, y-s*.18, x+s*.3, y+s*.18), w, radius=s*.08)
        _poly(draw, [(x-s*.3, y-s*.12), (x-s*.5, y-s*.22), (x-s*.46, y), (x-s*.5, y+s*.22), (x-s*.3, y+s*.12)], w)
        _poly(draw, [(x+s*.3, y-s*.12), (x+s*.5, y-s*.22), (x+s*.46, y), (x+s*.5, y+s*.22), (x+s*.3, y+s*.12)], w)
        _poly(draw, [(x-s*.15, y-s*.18), (x-s*.05, y+s*.18), (x+s*.05, y-s*.18), (x+s*.15, y+s*.18)], max(4, w//2))
    elif name == "lantern":
        _rect(draw, (x-s*.28, y-s*.35, x+s*.28, y+s*.4), w, radius=s*.04)
        _rect(draw, (x-s*.18, y-s*.48, x+s*.18, y-s*.35), w, radius=s*.03)
        draw.arc((x-s*.08, y-s*.62, x+s*.08, y-s*.46), start=180, end=360, fill=0, width=w)
        _rect(draw, (x-s*.06, y+.02*s, x+s*.06, y+s*.3), max(4, w//2))
        pts = _bezier((x, y-s*.18), (x-s*.08, y-s*.04), (x-s*.05, y+s*.02), (x, y+s*.03))
        pts += _bezier((x, y+s*.03), (x+s*.05, y+s*.02), (x+s*.08, y-s*.04), (x, y-s*.18))[1:]
        _line(draw, pts, max(4, w//2))
        _line(draw, [(x-s*.28, y-s*.12), (x+s*.28, y-s*.12)], max(4, w//2))
    elif name == "bell pair":
        for flip, bx in ((-1, x-s*.18), (1, x+s*.18)):
            pts = _bezier((bx-s*.06*flip*0, y-s*.05), (bx-s*.16, y+.0*s), (bx-s*.17, y+s*.22), (bx-s*.16, y+s*.3))
            pts += _bezier((bx-s*.16, y+s*.3), (bx-s*.08, y+s*.36), (bx+s*.08, y+s*.36), (bx+s*.16, y+s*.3))[1:]
            pts += _bezier((bx+s*.16, y+s*.3), (bx+s*.17, y+s*.22), (bx+s*.16, y+.0*s), (bx, y-s*.05))[1:]
            _line(draw, pts, w)
            _ellipse(draw, (bx-s*.05, y+s*.3, bx+s*.05, y+s*.4), max(4, w//2))
        l1 = _bezier((x, y-s*.15), (x-s*.22, y-s*.4), (x-s*.3, y-s*.15), (x, y-s*.2))
        _line(draw, l1, max(4, w//2))
        l2 = _bezier((x, y-s*.15), (x+s*.22, y-s*.4), (x+s*.3, y-s*.15), (x, y-s*.2))
        _line(draw, l2, max(4, w//2))
    else:
        raise ValueError(f"Unsupported christmas motif: {name}")
