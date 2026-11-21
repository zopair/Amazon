"""Generate original, bold-outline illustrations for all supported series themes."""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scripts.theme_art import FLOWERS, TOYS, BIRDS, ANIMALS, PROFESSIONS, draw_theme_art

PAGE_W, PAGE_H = 2550, 3300
DESIGNS = [
    "apple", "banana", "orange", "pear", "grapes", "watermelon",
    "strawberry", "pineapple", "lemon", "cherries", "peach", "avocado",
    "mango", "kiwi", "coconut", "blueberries", "raspberry", "melon",
    "papaya", "pomegranate", "plum", "apricot", "fig", "dragonfruit", "starfruit",
    # Vegetables (fruits + veggies production book, bestseller format)
    "carrot", "broccoli", "tomato", "corn", "eggplant", "pumpkin",
    "mushroom", "bell pepper", "cucumber", "peas", "potato", "onion",
    "garlic", "cabbage", "radish", "beet", "cauliflower", "celery",
    "chili pepper", "sweet potato", "zucchini", "spinach", "artichoke", "asparagus", "turnip",
]
THEME_DESIGNS = {
    "flowers": FLOWERS,
    "toys": TOYS,
    "birds": BIRDS,
    "animals": ANIMALS,
    "professions": PROFESSIONS,
}

def _bezier(p0, p1, p2, p3, steps=48):
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        points.append((round(x), round(y)))
    return points

def _line(draw, points, width, fill=0):
    draw.line(points, fill=fill, width=width, joint="curve")

def _leaf(draw, cx, cy, scale, width):
    pts = _bezier((cx,cy), (cx+scale*.55,cy-scale*.65), (cx+scale*1.05,cy-scale*.55), (cx+scale*1.2,cy-scale*.05))
    pts += _bezier((cx+scale*1.2,cy-scale*.05), (cx+scale*.75,cy+scale*.35), (cx+scale*.25,cy+scale*.25), (cx,cy))[1:]
    _line(draw, pts, width)
    _line(draw, [(cx,cy),(cx+scale*1.1,cy-scale*.08)], max(3,width//3))

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

def _sparkle(draw, sx, sy, r, width):
    q = r*.28
    pts = [(sx,sy-r),(sx+q,sy-q),(sx+r,sy),(sx+q,sy+q),(sx,sy+r),(sx-q,sy+q),(sx-r,sy),(sx-q,sy-q),(sx,sy-r)]
    _line(draw, pts, max(4, width//2))

def _heart(draw, hx, hy, r, width):
    pts = _bezier((hx,hy+r*.9),(hx-r*1.25,hy+r*.05),(hx-r*.62,hy-r*.95),(hx,hy-r*.3))
    pts += _bezier((hx,hy-r*.3),(hx+r*.62,hy-r*.95),(hx+r*1.25,hy+r*.05),(hx,hy+r*.9))[1:]
    _line(draw, pts, max(4, width//2))

def _accents(draw, x, y, s, width):
    """Small colorable companions around the subject, as in bold-and-easy bestsellers."""
    _sparkle(draw, x-s*.58, y-s*.5, s*.06, width)
    _heart(draw, x+s*.56, y-s*.4, s*.06, width)
    r = s*.035
    draw.ellipse((x+s*.52-r, y+s*.5-r, x+s*.52+r, y+s*.5+r), outline=0, width=max(4, width//3))

def _fruit(draw, name, cx, cy, s, width, variant=0):
    x, y = cx, cy
    if name == "apple":
        box=(x-s*.48,y-s*.38,x+s*.48,y+s*.48)
        draw.ellipse(box, outline=0, width=width)
        _line(draw, _bezier((x-s*.42,y-s*.02),(x-s*.22,y-s*.34),(x-s*.08,y-s*.2),(x,y-s*.18)), width)
        _line(draw, _bezier((x,y-s*.18),(x+s*.08,y-s*.2),(x+s*.22,y-s*.34),(x+s*.42,y-s*.02)), width)
        _line(draw, [(x,y-s*.18),(x+variant*8,y-s*.48)], width)
        _leaf(draw,x+variant*8,y-s*.43,s*.36,width)
        _face(draw, x, y-s*.02, s, width)
    elif name == "banana":
        outer=_bezier((x-s*.55,y-s*.25),(x-s*.38,y+s*.35),(x+s*.18,y+s*.52),(x+s*.58,y+s*.12))
        inner=_bezier((x-s*.35,y-s*.12),(x-s*.12,y+s*.16),(x+s*.18,y+s*.25),(x+s*.4,y+s*.05))
        _line(draw, outer+[(x+s*.4,y+s*.05)]+inner[::-1]+[(x-s*.55,y-s*.25)],width)
        _line(draw,[(x-s*.55,y-s*.25),(x-s*.64,y-s*.32)],width)
        _line(draw,[(x+s*.58,y+s*.12),(x+s*.66,y+s*.04)],width)
        _face(draw, x-s*.02, y+s*.05, s, width, scale=.75)
    elif name == "orange":
        draw.ellipse((x-s*.43,y-s*.43,x+s*.43,y+s*.43),outline=0,width=width)
        draw.ellipse((x-s*.07,y-s*.49,x+s*.07,y-s*.35),outline=0,width=max(3,width//2))
        _leaf(draw,x+ s*.02,y-s*.42,s*.34,width)
        _face(draw, x, y+s*.02, s, width)
    elif name == "pear":
        pts=_bezier((x,y-s*.48),(x-s*.12,y-s*.28),(x-s*.43,y-s*.1),(x-s*.43,y+s*.18))
        pts+=_bezier((x-s*.43,y+s*.18),(x-s*.43,y+s*.55),(x-s*.2,y+s*.58),(x,y+s*.55))[1:]
        pts+=_bezier((x,y+s*.55),(x+s*.2,y+s*.58),(x+s*.43,y+s*.55),(x+s*.43,y+s*.18))[1:]
        pts+=_bezier((x+s*.43,y+s*.18),(x+s*.43,y-s*.1),(x+s*.12,y-s*.28),(x,y-s*.48))[1:]
        _line(draw,pts,width)
        _line(draw,[(x,y-s*.48),(x+variant*5,y-s*.67)],width)
        _leaf(draw,x,y-s*.63,s*.32,width)
        _face(draw, x, y+s*.22, s, width, scale=.9)
    elif name == "grapes":
        # Four compact rows with visible gaps so every grape remains individually colorable.
        for row in range(4):
            for col in range(4-row):
                gx=x+(col-(3-row)/2)*s*.27
                gy=y-s*.31+row*s*.23
                radius=s*.105
                draw.ellipse((gx-radius,gy-radius,gx+radius,gy+radius),outline=0,width=max(4,width-2))
        _line(draw,[(x,y-s*.35),(x+variant*5,y-s*.62)],width)
        _leaf(draw,x,y-s*.58,s*.42,width)
        _face(draw, x, y+s*.385, s, width, scale=.30)
    elif name == "watermelon":
        # Upright wedge: a taller silhouette reads clearly and uses the page area better.
        top=(x,y-s*.52)
        left=(x-s*.52,y+s*.38)
        right=(x+s*.52,y+s*.38)
        lower=_bezier(left,(x-s*.3,y+s*.55),(x+s*.3,y+s*.55),right)
        _line(draw,[top,left]+lower[1:]+[top],width)
        inner=_bezier((x-s*.43,y+s*.30),(x-s*.2,y+s*.44),(x+s*.2,y+s*.44),(x+s*.43,y+s*.30))
        _line(draw,inner,width)
        for dx,dy in [(-.22,.04),(0,-.12),(.22,.04),(-.1,.20),(.12,.20)]:
            draw.ellipse((x+s*dx-s*.018,y+s*dy-s*.03,x+s*dx+s*.018,y+s*dy+s*.03),outline=0,width=max(4,width//3))
        _face(draw, x, y-s*.06, s, width, scale=.9)
    elif name == "strawberry":
        pts=_bezier((x,y-s*.45),(x-s*.1,y-s*.3),(x-s*.48,y-s*.12),(x-s*.4,y+s*.18))
        pts+=_bezier((x-s*.4,y+s*.18),(x-s*.32,y+s*.48),(x-s*.08,y+s*.55),(x,y+s*.62))[1:]
        pts+=_bezier((x,y+s*.62),(x+s*.08,y+s*.55),(x+s*.32,y+s*.48),(x+s*.4,y+s*.18))[1:]
        pts+=_bezier((x+s*.4,y+s*.18),(x+s*.48,y-s*.12),(x+s*.1,y-s*.3),(x,y-s*.45))[1:]
        _line(draw,pts,width)
        for dx,dy in [(-.2,-.12),(.0,-.05),(.2,-.12),(-.23,.12),(.0,.18),(.23,.12),(-.1,.37),(.12,.38)]:
            draw.ellipse((x+s*dx-s*.013,y+s*dy-s*.02,x+s*dx+s*.013,y+s*dy+s*.02),outline=0,width=max(4,width//4))
        _leaf(draw,x-s*.16,y-s*.38,s*.28,width)
        _face(draw, x, y+s*.1, s, width, scale=.8)
    elif name == "pineapple":
        rx, ry = s*.38, s*.325
        body_cy = y+s*.205
        draw.ellipse((x-rx,body_cy-ry,x+rx,body_cy+ry),outline=0,width=width)
        # Sparse chunky texture diamonds, kept clear of the face area.
        for dx,dy in [(-.19,-.12),(.19,-.12),(-.19,.42),(.19,.42),(0,.5)]:
            px,py=x+s*dx,body_cy+s*dy
            r=s*.032
            _line(draw,[(px,py-r),(px+r*.8,py),(px,py+r),(px-r*.8,py),(px,py-r)],max(4,width//3))
        for j,spread in [(-1,-.42),(0,0),(1,.42)]:
            tipx = x+spread*s
            left=_bezier((x,y-s*.1),(x+spread*s*.3,y-s*.5),(tipx-s*.1,y-s*.72),(tipx,y-s*.86))
            right=_bezier((tipx,y-s*.86),(tipx+s*.1,y-s*.72),(x+spread*s*.3+s*.08,y-s*.45),(x+s*.06,y-s*.12))
            _line(draw,left+right[1:],width)
        _face(draw, x, body_cy-s*.02, s, width, scale=.85)
    elif name == "lemon":
        pts=_bezier((x-s*.52,y),(x-s*.35,y-s*.4),(x+s*.35,y-s*.4),(x+s*.52,y))
        pts+=_bezier((x+s*.52,y),(x+s*.35,y+s*.4),(x-s*.35,y+s*.4),(x-s*.52,y))[1:]
        _line(draw,pts,width)
        _leaf(draw,x+s*.2,y-s*.22,s*.3,width)
        _line(draw,[(x-s*.52,y),(x-s*.65,y-s*.05)],width)
        _line(draw,[(x+s*.52,y),(x+s*.65,y-s*.05)],width)
        _face(draw, x, y, s, width, scale=.9)
    elif name == "cherries":
        _line(draw,_bezier((x-s*.12,y-s*.1),(x-s*.3,y-s*.55),(x+s*.12,y-s*.62),(x+s*.15,y-s*.7)),width)
        _line(draw,_bezier((x+s*.15,y-s*.1),(x+s*.25,y-s*.48),(x+s*.48,y-s*.55),(x+s*.5,y-s*.65)),width)
        draw.ellipse((x-s*.48,y-s*.05,x+s*.04,y+s*.48),outline=0,width=width)
        draw.ellipse((x+s*.1,y-s*.05,x+s*.62,y+s*.48),outline=0,width=width)
        _leaf(draw,x+s*.08,y-s*.62,s*.35,width)
        _face(draw, x-s*.22, y+s*.18, s, width, scale=.42)
        _face(draw, x+s*.36, y+s*.18, s, width, scale=.42)
    elif name == "peach":
        draw.ellipse((x-s*.48,y-s*.42,x+s*.48,y+s*.5),outline=0,width=width)
        _line(draw,_bezier((x-s*.08,y-s*.35),(x-s*.24,y-s*.12),(x-s*.22,y+s*.18),(x-s*.08,y+s*.38)),max(4,width//2))
        _line(draw,[(x,y-s*.42),(x+variant*5,y-s*.58)],width)
        _leaf(draw,x,y-s*.55,s*.28,width)
        _face(draw, x+s*.1, y, s, width, scale=.9)
    elif name == "avocado":
        pts=_bezier((x,y-s*.55),(x-s*.25,y-s*.48),(x-s*.52,y-s*.05),(x-s*.42,y+s*.32))
        pts+=_bezier((x-s*.42,y+s*.32),(x-s*.3,y+s*.62),(x+s*.3,y+s*.62),(x+s*.42,y+s*.32))[1:]
        pts+=_bezier((x+s*.42,y+s*.32),(x+s*.52,y-s*.05),(x+s*.25,y-s*.48),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        draw.ellipse((x-s*.18,y+s*.05,x+s*.18,y+s*.4),outline=0,width=width)
        _leaf(draw,x+s*.1,y-s*.45,s*.28,width)
        _face(draw, x, y-s*.2, s, width, scale=.75)
    elif name == "mango":
        pts=_bezier((x,y-s*.42),(x-s*.4,y-s*.42),(x-s*.52,y-s*.05),(x-s*.38,y+s*.28))
        pts+=_bezier((x-s*.38,y+s*.28),(x-s*.2,y+s*.55),(x+s*.12,y+s*.52),(x+s*.3,y+s*.3))[1:]
        pts+=_bezier((x+s*.3,y+s*.3),(x+s*.5,y+s*.02),(x+s*.42,y-s*.28),(x,y-s*.42))[1:]
        _line(draw,pts,width)
        _line(draw,[(x,y-s*.42),(x+variant*5,y-s*.56)],width)
        _leaf(draw,x+variant*5,y-s*.52,s*.3,width)
        _face(draw, x, y-s*.02, s, width, scale=.95)
    elif name == "kiwi":
        draw.ellipse((x-s*.42,y-s*.46,x+s*.42,y+s*.46),outline=0,width=width)
        for ang in range(0,360,45):
            a=math.radians(ang+22)
            _line(draw,[(x+math.cos(a)*s*.42,y+math.sin(a)*s*.46),(x+math.cos(a)*s*.5,y+math.sin(a)*s*.54)],max(4,width//2))
        _face(draw, x, y, s, width, scale=.9)
    elif name == "coconut":
        draw.ellipse((x-s*.46,y-s*.44,x+s*.46,y+s*.48),outline=0,width=width)
        for dx in (-.14,0,.14):
            draw.ellipse((x+s*dx-s*.035,y-s*.28-s*.04,x+s*dx+s*.035,y-s*.28+s*.04),outline=0,width=max(4,width//2))
        _face(draw, x, y+s*.08, s, width, scale=.9)
    elif name == "blueberries":
        for bx,by in [(-.3,.12),(.3,.12),(0,-.26)]:
            draw.ellipse((x+s*bx-s*.26,y+s*by-s*.26,x+s*bx+s*.26,y+s*by+s*.26),outline=0,width=width)
            _sparkle(draw, x+s*bx, y+s*by-s*.26, s*.05, max(4,width//2))
            _face(draw, x+s*bx, y+s*by, s, width, scale=.4)
    elif name == "raspberry":
        for dx,dy in [(0,-.3),(-.22,-.1),(.22,-.1),(-.22,.14),(.22,.14),(0,.34)]:
            draw.ellipse((x+s*dx-s*.17,y+s*dy-s*.17,x+s*dx+s*.17,y+s*dy+s*.17),outline=0,width=max(4,width-2))
        _leaf(draw,x,y-s*.46,s*.3,width)
        _face(draw, x, y-s*.3, s, width, scale=.34)
    elif name == "melon":
        left=(x-s*.55,y-s*.15); right=(x+s*.55,y-s*.15)
        arc=_bezier(left,(x-s*.42,y+s*.5),(x+s*.42,y+s*.5),right)
        _line(draw,[left]+arc[1:]+[right,left],width)
        # Rind band: a parallel curve just above the bottom outer edge.
        inner=_bezier((x-s*.47,y-s*.06),(x-s*.34,y+s*.34),(x+s*.34,y+s*.34),(x+s*.47,y-s*.06))
        _line(draw,inner,max(4,width//2))
        for dx in (-.18,.18):
            draw.ellipse((x+s*dx-s*.02,y+s*.24-s*.028,x+s*dx+s*.02,y+s*.24+s*.028),outline=0,width=max(4,width//3))
        _face(draw, x, y+s*.02, s, width, scale=.8)
    elif name == "papaya":
        pts=_bezier((x,y-s*.5),(x-s*.3,y-s*.45),(x-s*.42,y-s*.05),(x-s*.34,y+s*.3))
        pts+=_bezier((x-s*.34,y+s*.3),(x-s*.2,y+s*.55),(x+s*.2,y+s*.55),(x+s*.34,y+s*.3))[1:]
        pts+=_bezier((x+s*.34,y+s*.3),(x+s*.42,y-s*.05),(x+s*.3,y-s*.45),(x,y-s*.5))[1:]
        _line(draw,pts,width)
        _line(draw,[(x,y-s*.5),(x+variant*5,y-s*.62)],width)
        _face(draw, x, y, s, width, scale=.9)
    elif name == "pomegranate":
        draw.ellipse((x-s*.44,y-s*.36,x+s*.44,y+s*.5),outline=0,width=width)
        crown=[(x-s*.15,y-s*.3),(x-s*.18,y-s*.52),(x-s*.07,y-s*.44),(x,y-s*.58),(x+s*.07,y-s*.44),(x+s*.18,y-s*.52),(x+s*.15,y-s*.3)]
        _line(draw,crown,width)
        _face(draw, x, y+s*.06, s, width, scale=.9)
    elif name == "plum":
        draw.ellipse((x-s*.4,y-s*.46,x+s*.4,y+s*.46),outline=0,width=width)
        _line(draw,_bezier((x-s*.06,y-s*.44),(x-s*.14,y-s*.1),(x-s*.14,y+s*.1),(x-s*.06,y+s*.44)),max(4,width//2))
        _line(draw,[(x,y-s*.46),(x+variant*5,y-s*.6)],width)
        _leaf(draw,x+variant*5,y-s*.56,s*.3,width)
        _face(draw, x+s*.06, y, s, width, scale=.85)
    elif name == "apricot":
        draw.ellipse((x-s*.42,y-s*.42,x+s*.42,y+s*.42),outline=0,width=width)
        _line(draw,_bezier((x-s*.12,y-s*.4),(x-s*.22,y-s*.1),(x-s*.22,y+s*.1),(x-s*.12,y+s*.4)),max(4,width//2))
        _line(draw,[(x-s*.05,y-s*.42),(x+variant*5-s*.05,y-s*.56)],width)
        _face(draw, x+s*.08, y, s, width, scale=.85)
    elif name == "fig":
        pts=_bezier((x,y-s*.55),(x-s*.3,y-s*.45),(x-s*.5,y-s*.05),(x-s*.38,y+s*.28))
        pts+=_bezier((x-s*.38,y+s*.28),(x-s*.22,y+s*.55),(x+s*.22,y+s*.55),(x+s*.38,y+s*.28))[1:]
        pts+=_bezier((x+s*.38,y+s*.28),(x+s*.5,y-s*.05),(x+s*.3,y-s*.45),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        _line(draw,[(x,y-s*.55),(x+variant*5,y-s*.68)],width)
        _face(draw, x, y, s, width, scale=.9)
    elif name == "dragonfruit":
        draw.ellipse((x-s*.36,y-s*.46,x+s*.36,y+s*.46),outline=0,width=width)
        for sy in (-.25,.05,.35):
            for sgn in (-1,1):
                bx=x+sgn*s*.34; by=y+sy*s
                _line(draw,_bezier((bx,by-s*.1),(bx+sgn*s*.22,by-s*.12),(bx+sgn*s*.26,by+s*.02),(bx,by+s*.12)),width)
        _face(draw, x, y, s, width, scale=.9)
    elif name == "starfruit":
        pts=[]
        for i in range(5):
            a=math.radians(-90+i*72); a2=math.radians(-90+i*72+36)
            pts.append((x+math.cos(a)*s*.5, y+math.sin(a)*s*.5))
            pts.append((x+math.cos(a2)*s*.24, y+math.sin(a2)*s*.24))
        pts.append(pts[0])
        _line(draw,pts,width)
        _face(draw, x, y, s, width, scale=.8)
    elif name == "carrot":
        pts=_bezier((x-s*.25,y-s*.3),(x-s*.32,y),(x-s*.18,y+s*.35),(x,y+s*.55))
        pts+=_bezier((x,y+s*.55),(x+s*.18,y+s*.35),(x+s*.32,y),(x+s*.25,y-s*.3))[1:]
        _line(draw,pts,width)
        for j in (-1,0,1):
            _line(draw,_bezier((x+j*s*.08,y-s*.28),(x+j*s*.16,y-s*.48),(x+j*s*.2,y-s*.6),(x+j*s*.28,y-s*.68)),width)
        for ry in (.18,.34):
            _line(draw,[(x-s*.13,y+s*ry),(x+s*.13,y+s*ry)],max(4,width//3))
        _face(draw, x, y-s*.1, s, width, scale=.85)
    elif name == "broccoli":
        _line(draw,_bezier((x-s*.16,y+s*.55),(x-s*.19,y+s*.3),(x-s*.14,y+s*.08),(x-s*.3,y)),width)
        _line(draw,_bezier((x+s*.16,y+s*.55),(x+s*.19,y+s*.3),(x+s*.14,y+s*.08),(x+s*.3,y)),width)
        _line(draw,[(x-s*.16,y+s*.55),(x+s*.16,y+s*.55)],width)
        pts=_bezier((x-s*.3,y),(x-s*.52,y),(x-s*.5,y-s*.3),(x-s*.3,y-s*.34))
        pts+=_bezier((x-s*.3,y-s*.34),(x-s*.22,y-s*.55),(x+s*.22,y-s*.55),(x+s*.3,y-s*.34))[1:]
        pts+=_bezier((x+s*.3,y-s*.34),(x+s*.5,y-s*.3),(x+s*.52,y),(x+s*.3,y))[1:]
        _line(draw,pts,width)
        _face(draw, x, y-s*.12, s, width, scale=.8)
    elif name == "tomato":
        draw.ellipse((x-s*.46,y-s*.4,x+s*.46,y+s*.48),outline=0,width=width)
        _line(draw,[(x,y-s*.52),(x,y-s*.4)],width)
        pts=[(x,y-s*.38),(x-s*.14,y-s*.3),(x-s*.3,y-s*.4),(x-s*.16,y-s*.42),(x-s*.1,y-s*.52),(x,y-s*.44),(x+s*.1,y-s*.52),(x+s*.16,y-s*.42),(x+s*.3,y-s*.4),(x+s*.14,y-s*.3),(x,y-s*.38)]
        _line(draw,pts,width)
        _face(draw, x, y+s*.04, s, width, scale=.9)
    elif name == "corn":
        pts=_bezier((x,y-s*.55),(x-s*.28,y-s*.45),(x-s*.3,y),(x-s*.26,y+s*.4))
        pts+=_bezier((x-s*.26,y+s*.4),(x-s*.2,y+s*.55),(x+s*.2,y+s*.55),(x+s*.26,y+s*.4))[1:]
        pts+=_bezier((x+s*.26,y+s*.4),(x+s*.3,y),(x+s*.28,y-s*.45),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        for sx in (-.15,.15):
            _line(draw,_bezier((x+s*sx,y-s*.4),(x+s*sx-s*.02,y),(x+s*sx+s*.02,y+s*.2),(x+s*sx,y+s*.45)),max(4,width//3))
        # husk leaves at the base
        _line(draw,_bezier((x-s*.26,y+s*.2),(x-s*.5,y+s*.1),(x-s*.55,y+s*.3),(x-s*.3,y+s*.55)),width)
        _line(draw,_bezier((x+s*.26,y+s*.2),(x+s*.5,y+s*.1),(x+s*.55,y+s*.3),(x+s*.3,y+s*.55)),width)
        _face(draw, x, y-s*.05, s, width, scale=.85)
    elif name == "eggplant":
        draw.ellipse((x-s*.4,y-s*.4,x+s*.4,y+s*.5),outline=0,width=width)
        pts=[(x,y-s*.58),(x-s*.12,y-s*.52),(x-s*.28,y-s*.42),(x-s*.14,y-s*.38),(x-s*.2,y-s*.48),(x,y-s*.42),(x+s*.2,y-s*.48),(x+s*.14,y-s*.38),(x+s*.28,y-s*.42),(x+s*.12,y-s*.52),(x,y-s*.58)]
        _line(draw,pts,width)
        _face(draw, x, y+s*.06, s, width, scale=.9)
    elif name == "pumpkin":
        draw.ellipse((x-s*.5,y-s*.4,x+s*.5,y+s*.48),outline=0,width=width)
        _line(draw,_bezier((x-s*.2,y-s*.38),(x-s*.28,y),(x-s*.28,y+s*.1),(x-s*.2,y+s*.44)),max(4,width//2))
        _line(draw,_bezier((x+s*.2,y-s*.38),(x+s*.28,y),(x+s*.28,y+s*.1),(x+s*.2,y+s*.44)),max(4,width//2))
        _line(draw,_bezier((x,y-s*.4),(x-s*.06,y-s*.55),(x+s*.04,y-s*.62),(x+s*.1,y-s*.56)),width)
        _face(draw, x, y+s*.02, s, width, scale=.9)
    elif name == "mushroom":
        pts=_bezier((x-s*.5,y-s*.02),(x-s*.42,y-s*.42),(x+s*.42,y-s*.42),(x+s*.5,y-s*.02))
        pts+=_bezier((x+s*.5,y-s*.02),(x+s*.3,y+s*.06),(x-s*.3,y+s*.06),(x-s*.5,y-s*.02))[1:]
        _line(draw,pts,width)
        _line(draw,_bezier((x-s*.16,y+s*.06),(x-s*.2,y+s*.3),(x-s*.2,y+s*.42),(x-s*.16,y+s*.55)),width)
        _line(draw,_bezier((x+s*.16,y+s*.06),(x+s*.2,y+s*.3),(x+s*.2,y+s*.42),(x+s*.16,y+s*.55)),width)
        _line(draw,[(x-s*.16,y+s*.55),(x+s*.16,y+s*.55)],width)
        for dx,dy,r in [(-.25,-.2,.05),(0,-.28,.06),(.25,-.2,.05)]:
            draw.ellipse((x+s*dx-s*r,y+s*dy-s*r,x+s*dx+s*r,y+s*dy+s*r),outline=0,width=max(4,width//3))
        _face(draw, x, y-s*.12, s, width, scale=.7)
    elif name == "bell pepper":
        draw.ellipse((x-s*.42,y-s*.38,x+s*.42,y+s*.48),outline=0,width=width)
        _line(draw,_bezier((x-s*.14,y-s*.36),(x-s*.2,y),(x-s*.2,y+s*.2),(x-s*.14,y+s*.44)),max(4,width//2))
        _line(draw,_bezier((x+s*.14,y-s*.36),(x+s*.2,y),(x+s*.2,y+s*.2),(x+s*.14,y+s*.44)),max(4,width//2))
        _line(draw,_bezier((x,y-s*.38),(x-s*.04,y-s*.52),(x+s*.08,y-s*.6),(x+s*.16,y-s*.54)),width)
        _face(draw, x, y+s*.02, s, width, scale=.9)
    elif name == "cucumber":
        pts=_bezier((x-s*.5,y-s*.15),(x-s*.4,y-s*.35),(x+s*.4,y-s*.35),(x+s*.5,y-s*.15))
        pts+=_bezier((x+s*.5,y-s*.15),(x+s*.55,y),(x+s*.5,y+s*.15),(x+s*.4,y+s*.3))[1:]
        pts+=_bezier((x+s*.4,y+s*.3),(x-s*.4,y+s*.3),(x-s*.5,y+s*.15),(x-s*.5,y-s*.15))[1:]
        _line(draw,pts,width)
        _line(draw,_bezier((x-s*.35,y-s*.28),(x-s*.1,y-s*.34),(x+s*.1,y-s*.34),(x+s*.35,y-s*.28)),max(4,width//3))
        _line(draw,_bezier((x-s*.35,y+s*.22),(x-s*.1,y+s*.28),(x+s*.1,y+s*.28),(x+s*.35,y+s*.22)),max(4,width//3))
        _face(draw, x, y, s, width, scale=.8)
    elif name == "peas":
        pts=_bezier((x-s*.5,y+s*.2),(x-s*.3,y-s*.25),(x+s*.3,y-s*.3),(x+s*.55,y-s*.05))
        pts+=_bezier((x+s*.55,y-s*.05),(x+s*.4,y+s*.25),(x-s*.2,y+s*.45),(x-s*.5,y+s*.2))[1:]
        _line(draw,pts,width)
        for px in (-.22,0,.22):
            draw.ellipse((x+s*px-s*.13,y+s*.04-s*.13,x+s*px+s*.13,y+s*.04+s*.13),outline=0,width=max(4,width//2))
        _line(draw,_bezier((x+s*.5,y-s*.08),(x+s*.62,y-s*.2),(x+s*.68,y-s*.1),(x+s*.62,y)),max(4,width//2))
        _face(draw, x, y-s*.12, s, width, scale=.6)
    elif name == "potato":
        pts=_bezier((x-s*.45,y-s*.2),(x-s*.35,y-s*.45),(x+s*.1,y-s*.48),(x+s*.38,y-s*.3))
        pts+=_bezier((x+s*.38,y-s*.3),(x+s*.52,y-s*.1),(x+s*.45,y+s*.25),(x+s*.2,y+s*.42))[1:]
        pts+=_bezier((x+s*.2,y+s*.42),(x-s*.1,y+s*.5),(x-s*.42,y+s*.3),(x-s*.45,y-s*.2))[1:]
        _line(draw,pts,width)
        for dx,dy in [(-.2,-.1),(.15,-.2),(-.05,.25)]:
            draw.ellipse((x+s*dx-s*.025,y+s*dy-s*.018,x+s*dx+s*.025,y+s*dy+s*.018),outline=0,width=max(4,width//3))
        _face(draw, x, y, s, width, scale=.9)
    elif name == "onion":
        pts=_bezier((x,y-s*.5),(x-s*.42,y-s*.3),(x-s*.48,y+s*.1),(x-s*.3,y+s*.4))
        pts+=_bezier((x-s*.3,y+s*.4),(x-s*.1,y+s*.55),(x+s*.1,y+s*.55),(x+s*.3,y+s*.4))[1:]
        pts+=_bezier((x+s*.3,y+s*.4),(x+s*.48,y+s*.1),(x+s*.42,y-s*.3),(x,y-s*.5))[1:]
        _line(draw,pts,width)
        _line(draw,_bezier((x-s*.2,y-s*.28),(x-s*.26,y),(x-s*.22,y+s*.2),(x-s*.12,y+s*.4)),max(4,width//3))
        _line(draw,_bezier((x+s*.2,y-s*.28),(x+s*.26,y),(x+s*.22,y+s*.2),(x+s*.12,y+s*.4)),max(4,width//3))
        _line(draw,[(x,y-s*.5),(x-s*.05,y-s*.62)],width)
        _line(draw,[(x,y-s*.5),(x+s*.05,y-s*.62)],width)
        _face(draw, x, y+s*.05, s, width, scale=.85)
    elif name == "garlic":
        pts=_bezier((x,y-s*.55),(x-s*.3,y-s*.3),(x-s*.48,y),(x-s*.42,y+s*.3))
        pts+=_bezier((x-s*.42,y+s*.3),(x-s*.3,y+s*.55),(x-s*.08,y+s*.5),(x,y+s*.38))[1:]
        pts+=_bezier((x,y+s*.38),(x+s*.08,y+s*.5),(x+s*.3,y+s*.55),(x+s*.42,y+s*.3))[1:]
        pts+=_bezier((x+s*.42,y+s*.3),(x+s*.48,y),(x+s*.3,y-s*.3),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        _line(draw,_bezier((x-s*.18,y-s*.2),(x-s*.24,y+s*.1),(x-s*.2,y+s*.3),(x-s*.1,y+s*.44)),max(4,width//3))
        _line(draw,_bezier((x+s*.18,y-s*.2),(x+s*.24,y+s*.1),(x+s*.2,y+s*.3),(x+s*.1,y+s*.44)),max(4,width//3))
        _face(draw, x, y, s, width, scale=.85)
    elif name == "cabbage":
        draw.ellipse((x-s*.48,y-s*.44,x+s*.48,y+s*.48),outline=0,width=width)
        _line(draw,_bezier((x-s*.4,y+s*.1),(x-s*.2,y-s*.3),(x+s*.1,y-s*.35),(x+s*.35,y-s*.2)),max(4,width//2))
        _line(draw,_bezier((x-s*.35,y+s*.3),(x-s*.1,y+s*.05),(x+s*.2,y),(x+s*.4,y+s*.1)),max(4,width//2))
        _face(draw, x, y, s, width, scale=.9)
    elif name == "radish":
        draw.ellipse((x-s*.4,y-s*.28,x+s*.4,y+s*.4),outline=0,width=width)
        _line(draw,_bezier((x,y+s*.4),(x-s*.06,y+s*.52),(x+s*.04,y+s*.6),(x+s*.1,y+s*.66)),width)
        for j in (-1,0,1):
            _line(draw,_bezier((x+j*s*.06,y-s*.26),(x+j*s*.16,y-s*.48),(x+j*s*.22,y-s*.58),(x+j*s*.3,y-s*.66)),width)
        _face(draw, x, y+s*.05, s, width, scale=.8)
    elif name == "beet":
        pts=_bezier((x,y+s*.6),(x-s*.45,y+s*.3),(x-s*.5,y-s*.05),(x-s*.4,y-s*.2))
        pts+=_bezier((x-s*.4,y-s*.2),(x-s*.2,y-s*.35),(x+s*.2,y-s*.35),(x+s*.4,y-s*.2))[1:]
        pts+=_bezier((x+s*.4,y-s*.2),(x+s*.5,y-s*.05),(x+s*.45,y+s*.3),(x,y+s*.6))[1:]
        _line(draw,pts,width)
        for j in (-1,0,1):
            _line(draw,_bezier((x+j*s*.08,y-s*.3),(x+j*s*.14,y-s*.52),(x+j*s*.2,y-s*.62),(x+j*s*.26,y-s*.7)),width)
        _face(draw, x, y+s*.08, s, width, scale=.85)
    elif name == "cauliflower":
        pts=_bezier((x-s*.3,y-s*.02),(x-s*.5,y-s*.05),(x-s*.48,y-s*.3),(x-s*.28,y-s*.34))
        pts+=_bezier((x-s*.28,y-s*.34),(x-s*.2,y-s*.52),(x+s*.2,y-s*.52),(x+s*.28,y-s*.34))[1:]
        pts+=_bezier((x+s*.28,y-s*.34),(x+s*.48,y-s*.3),(x+s*.5,y-s*.05),(x+s*.3,y-s*.02))[1:]
        _line(draw,pts,width)
        # leaf skirt
        _line(draw,_bezier((x-s*.3,y-s*.02),(x-s*.42,y+s*.3),(x-s*.2,y+s*.45),(x-s*.05,y+s*.5)),width)
        _line(draw,_bezier((x+s*.3,y-s*.02),(x+s*.42,y+s*.3),(x+s*.2,y+s*.45),(x+s*.05,y+s*.5)),width)
        _line(draw,[(x-s*.05,y+s*.5),(x+s*.05,y+s*.5)],width)
        _face(draw, x, y-s*.12, s, width, scale=.8)
    elif name == "celery":
        _line(draw,_bezier((x-s*.3,y+s*.55),(x-s*.34,y+s*.2),(x-s*.3,y-s*.15),(x-s*.24,y-s*.32)),width)
        _line(draw,_bezier((x+s*.3,y+s*.55),(x+s*.34,y+s*.2),(x+s*.3,y-s*.15),(x+s*.24,y-s*.32)),width)
        _line(draw,[(x-s*.3,y+s*.55),(x+s*.3,y+s*.55)],width)
        for j in (-1,0,1):
            sx=x+j*s*.16
            _line(draw,_bezier((sx-s*.02,y+s*.5),(sx-s*.03,y+s*.1),(sx-s*.02,y-s*.1),(sx,y-s*.28)),max(4,width//3))
        for j in (-1,0,1):
            sx=x+j*s*.16
            _line(draw,_bezier((sx,y-s*.28),(sx-s*.06,y-s*.5),(sx+s*.04,y-s*.58),(sx+s*.1,y-s*.5)),width)
        _face(draw, x, y+s*.05, s, width, scale=.85)
    elif name == "chili pepper":
        outer=_bezier((x-s*.5,y-s*.3),(x-s*.45,y+s*.3),(x+s*.1,y+s*.55),(x+s*.45,y+s*.3))
        inner=_bezier((x-s*.32,y-s*.18),(x-s*.22,y+s*.15),(x+s*.1,y+s*.32),(x+s*.35,y+s*.15))
        _line(draw,outer+[(x+s*.35,y+s*.15)]+inner[::-1]+[(x-s*.5,y-s*.3)],width)
        _line(draw,_bezier((x-s*.5,y-s*.3),(x-s*.52,y-s*.5),(x-s*.42,y-s*.6),(x-s*.34,y-s*.55)),width)
        _face(draw, x-s*.05, y+s*.1, s, width, scale=.75)
    elif name == "sweet potato":
        pts=_bezier((x-s*.5,y-s*.05),(x-s*.35,y-s*.32),(x+s*.05,y-s*.38),(x+s*.35,y-s*.25))
        pts+=_bezier((x+s*.35,y-s*.25),(x+s*.52,y-s*.12),(x+s*.5,y+s*.1),(x+s*.3,y+s*.22))[1:]
        pts+=_bezier((x+s*.3,y+s*.22),(x-s*.05,y+s*.38),(x-s*.4,y+s*.25),(x-s*.5,y-s*.05))[1:]
        _line(draw,pts,width)
        _face(draw, x, y, s, width, scale=.85)
    elif name == "zucchini":
        pts=_bezier((x-s*.48,y-s*.12),(x-s*.35,y-s*.28),(x+s*.35,y-s*.28),(x+s*.48,y-s*.12))
        pts+=_bezier((x+s*.48,y-s*.12),(x+s*.52,y),(x+s*.48,y+s*.12),(x+s*.35,y+s*.28))[1:]
        pts+=_bezier((x+s*.35,y+s*.28),(x-s*.35,y+s*.28),(x-s*.48,y+s*.12),(x-s*.48,y-s*.12))[1:]
        _line(draw,pts,width)
        _line(draw,[(x+s*.48,y),(x+s*.6,y-s*.04)],width)
        _face(draw, x-s*.05, y, s, width, scale=.8)
    elif name == "spinach":
        for j,(dx,rot) in enumerate([(-.22,-15),(0,0),(.22,15)]):
            cx0=x+s*dx
            pts=_bezier((cx0,y+s*.45),(cx0-s*.28,y+s*.15),(cx0-s*.24,y-s*.3),(cx0,y-s*.45))
            pts+=_bezier((cx0,y-s*.45),(cx0+s*.24,y-s*.3),(cx0+s*.28,y+s*.15),(cx0,y+s*.45))[1:]
            _line(draw,pts,width)
            _line(draw,[(cx0,y+s*.45),(cx0,y+s*.6)],width)
        _face(draw, x, y-s*.02, s, width, scale=.75)
    elif name == "artichoke":
        pts=_bezier((x,y-s*.55),(x-s*.35,y-s*.3),(x-s*.48,y+s*.05),(x-s*.3,y+s*.4))
        pts+=_bezier((x-s*.3,y+s*.4),(x-s*.1,y+s*.55),(x+s*.1,y+s*.55),(x+s*.3,y+s*.4))[1:]
        pts+=_bezier((x+s*.3,y+s*.4),(x+s*.48,y+s*.05),(x+s*.35,y-s*.3),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        _line(draw,_bezier((x-s*.36,y-s*.05),(x-s*.18,y-s*.2),(x+s*.18,y-s*.2),(x+s*.36,y-s*.05)),max(4,width//2))
        _line(draw,_bezier((x-s*.28,y-s*.25),(x-s*.12,y-s*.38),(x+s*.12,y-s*.38),(x+s*.28,y-s*.25)),max(4,width//2))
        _face(draw, x, y+s*.15, s, width, scale=.8)
    elif name == "asparagus":
        for j in (-1,0,1):
            sx=x+j*s*.24
            _line(draw,_bezier((sx-s*.06,y+s*.55),(sx-s*.07,y+s*.1),(sx-s*.06,y-s*.2),(sx,y-s*.3)),width)
            _line(draw,_bezier((sx+s*.06,y+s*.55),(sx+s*.07,y+s*.1),(sx+s*.06,y-s*.2),(sx,y-s*.3)),width)
            pts=[(sx,y-s*.55),(sx-s*.1,y-s*.28),(sx+s*.1,y-s*.28),(sx,y-s*.55)]
            _line(draw,pts,width)
        _line(draw,[(x-s*.34,y+s*.55),(x+s*.34,y+s*.55)],width)
        _face(draw, x, y+s*.1, s, width, scale=.42)
    elif name == "turnip":
        draw.ellipse((x-s*.42,y-s*.3,x+s*.42,y+s*.42),outline=0,width=width)
        _line(draw,_bezier((x,y+s*.42),(x-s*.05,y+s*.55),(x+s*.03,y+s*.62),(x+s*.08,y+s*.68)),width)
        for j in (-1,0,1):
            _line(draw,_bezier((x+j*s*.07,y-s*.28),(x+j*s*.15,y-s*.5),(x+j*s*.2,y-s*.6),(x+j*s*.28,y-s*.68)),width)
        _face(draw, x, y+s*.06, s, width, scale=.85)
    _accents(draw, x, y, s, width)


FONT_PATH = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "DejaVuSans-Bold.ttf"


def _label(draw, text, cx, top_y, max_width, stroke_px):
    """Large colorable name label: bold caps, white fill, thick black outline."""
    size = 300
    font = ImageFont.truetype(str(FONT_PATH), size)
    while size > 60 and draw.textlength(text, font=font) > max_width:
        size -= 12
        font = ImageFont.truetype(str(FONT_PATH), size)
    draw.text((cx, top_y), text, font=font, anchor="ma",
              fill="white", stroke_width=stroke_px, stroke_fill="black")


def generate_artwork(theme: str, count: int, output_dir: str | Path, dpi: int = 300, line_width_pt: float = 2.4) -> list[Path]:
    if theme != "fruit" and theme not in THEME_DESIGNS:
        raise ValueError(f"Unsupported theme: {theme}. Supported themes: fruit, flowers, toys, birds, animals, professions")
    max_count = len(DESIGNS) if theme == "fruit" else len(THEME_DESIGNS.get(theme, []))
    if count < 1 or count > max_count:
        raise ValueError(f"the built-in generator provides {max_count} distinct motifs for theme '{theme}'; larger books require an exact set of approved original artwork files")
    if dpi < 300:
        raise ValueError("artwork resolution must be at least 300 DPI")
    if line_width_pt < 0.75:
        raise ValueError("line width must meet KDP's 0.75 pt minimum")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    line_px = max(4, math.ceil(line_width_pt * dpi / 72))
    paths = []
    for index in range(count):
        image = Image.new("RGB", (PAGE_W, PAGE_H), "white")
        draw = ImageDraw.Draw(image)
        # Large central subject with generous safe margins and simple secondary accents.
        designs = DESIGNS if theme == "fruit" else THEME_DESIGNS[theme]
        name = designs[index % len(designs)]
        if theme == "fruit":
            fruit_scales = {"pear": 1400, "plum": 1450, "carrot": 1400, "radish": 1350, "beet": 1400, "turnip": 1350, "watermelon": 1400, "strawberry": 1400, "avocado": 1400, "pineapple": 1180, "lemon": 1400, "grapes": 1350, "cherries": 1350}
            scale = fruit_scales.get(name, 1500)
        else:
            scale = 1320 if index % 3 else 1240
        cx, cy = PAGE_W // 2, PAGE_H // 2 - 230 + (index % 2) * 30
        if theme == "fruit":
            _fruit(draw, name, cx, cy, scale, line_px, index)
        else:
            draw_theme_art(draw,theme,name,cx,cy,scale,line_px,index)
        ink = ImageOps.invert(image.convert("L")).getbbox()
        if ink:
            _label(draw, name.replace('_', ' ').upper(), cx, ink[3] + 100, 1800, max(6, line_px // 4))
        # Flatten any antialiased text edges to pure black/white for the binary-palette gate.
        image = image.convert("L").point(lambda v: 0 if v < 128 else 255).convert("RGB")
        safe_name=name.replace(" ","_")
        path = output / f"{theme}_{index+1:02d}_{safe_name}.png"
        image.save(path, format="PNG", dpi=(dpi,dpi), optimize=True)
        paths.append(path)
    return paths
