"""Generate original, bold-outline illustrations for all supported series themes."""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw
from scripts.theme_art import FLOWERS, TOYS, BIRDS, ANIMALS, PROFESSIONS, draw_theme_art

PAGE_W, PAGE_H = 2550, 3300
DESIGNS = [
    "apple", "banana", "orange", "pear", "grapes", "watermelon",
    "strawberry", "pineapple", "lemon", "cherries", "peach", "avocado",
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

def _fruit(draw, name, cx, cy, s, width, variant=0):
    x, y = cx, cy
    if name == "apple":
        box=(x-s*.48,y-s*.38,x+s*.48,y+s*.48)
        draw.ellipse(box, outline=0, width=width)
        _line(draw, _bezier((x-s*.42,y-s*.02),(x-s*.22,y-s*.34),(x-s*.08,y-s*.2),(x,y-s*.18)), width)
        _line(draw, _bezier((x,y-s*.18),(x+s*.08,y-s*.2),(x+s*.22,y-s*.34),(x+s*.42,y-s*.02)), width)
        _line(draw, [(x,y-s*.18),(x+variant*8,y-s*.48)], width)
        _leaf(draw,x+variant*8,y-s*.43,s*.36,width)
    elif name == "banana":
        outer=_bezier((x-s*.55,y-s*.25),(x-s*.38,y+s*.35),(x+s*.18,y+s*.52),(x+s*.58,y+s*.12))
        inner=_bezier((x-s*.35,y-s*.12),(x-s*.12,y+s*.16),(x+s*.18,y+s*.25),(x+s*.4,y+s*.05))
        _line(draw, outer+[(x+s*.4,y+s*.05)]+inner[::-1]+[(x-s*.55,y-s*.25)],width)
        _line(draw,[(x-s*.55,y-s*.25),(x-s*.64,y-s*.32)],width)
        _line(draw,[(x+s*.58,y+s*.12),(x+s*.66,y+s*.04)],width)
    elif name == "orange":
        draw.ellipse((x-s*.43,y-s*.43,x+s*.43,y+s*.43),outline=0,width=width)
        draw.ellipse((x-s*.07,y-s*.49,x+s*.07,y-s*.35),outline=0,width=max(3,width//2))
        _leaf(draw,x+ s*.02,y-s*.42,s*.34,width)
    elif name == "pear":
        pts=_bezier((x,y-s*.48),(x-s*.12,y-s*.28),(x-s*.43,y-s*.1),(x-s*.43,y+s*.18))
        pts+=_bezier((x-s*.43,y+s*.18),(x-s*.43,y+s*.55),(x-s*.2,y+s*.58),(x,y+s*.55))[1:]
        pts+=_bezier((x,y+s*.55),(x+s*.2,y+s*.58),(x+s*.43,y+s*.55),(x+s*.43,y+s*.18))[1:]
        pts+=_bezier((x+s*.43,y+s*.18),(x+s*.43,y-s*.1),(x+s*.12,y-s*.28),(x,y-s*.48))[1:]
        _line(draw,pts,width)
        _line(draw,[(x,y-s*.48),(x+variant*5,y-s*.67)],width)
        _leaf(draw,x,y-s*.63,s*.32,width)
    elif name == "grapes":
        for row in range(4):
            for col in range(4-row):
                gx=x+(col-(3-row)/2)*s*.22
                gy=y-s*.25+row*s*.2
                draw.ellipse((gx-s*.13,gy-s*.13,gx+s*.13,gy+s*.13),outline=0,width=max(4,width-2))
        _line(draw,[(x,y-s*.35),(x+variant*5,y-s*.62)],width)
        _leaf(draw,x,y-s*.58,s*.42,width)
    elif name == "watermelon":
        draw.pieslice((x-s*.55,y-s*.48,x+s*.55,y+s*.55),0,180,outline=0,width=width)
        _line(draw,[(x-s*.55,y),(x+s*.55,y)],width)
        _line(draw,_bezier((x-s*.43,y+s*.18),(x-s*.18,y+s*.58),(x+s*.18,y+s*.58),(x+s*.43,y+s*.18)),width)
        for dx,dy in [(-.28,.04),(-.08,.12),(.13,.08),(.32,.02)]:
            draw.ellipse((x+s*dx-7,y+s*dy-12,x+s*dx+7,y+s*dy+12),outline=0,width=max(3,width//2))
    elif name == "strawberry":
        pts=_bezier((x,y-s*.45),(x-s*.1,y-s*.3),(x-s*.48,y-s*.12),(x-s*.4,y+s*.18))
        pts+=_bezier((x-s*.4,y+s*.18),(x-s*.32,y+s*.48),(x-s*.08,y+s*.55),(x,y+s*.62))[1:]
        pts+=_bezier((x,y+s*.62),(x+s*.08,y+s*.55),(x+s*.32,y+s*.48),(x+s*.4,y+s*.18))[1:]
        pts+=_bezier((x+s*.4,y+s*.18),(x+s*.48,y-s*.12),(x+s*.1,y-s*.3),(x,y-s*.45))[1:]
        _line(draw,pts,width)
        for dx,dy in [(-.2,-.12),(.0,-.05),(.2,-.12),(-.23,.12),(.0,.18),(.23,.12),(-.1,.37),(.12,.38)]:
            draw.ellipse((x+s*dx-5,y+s*dy-8,x+s*dx+5,y+s*dy+8),outline=0,width=max(3,width//3))
        _leaf(draw,x-s*.16,y-s*.38,s*.28,width)
    elif name == "pineapple":
        draw.ellipse((x-s*.38,y-s*.12,x+s*.38,y+s*.53),outline=0,width=width)
        for i in range(-2,3):
            _line(draw,[(x+i*s*.12,y-s*.12),(x+i*s*.28,y+s*.52)],max(4,width//2))
        for i in range(-2,3):
            _line(draw,[(x-s*.35,y+i*s*.12),(x+s*.35,y+i*s*.12)],max(4,width//2))
        for j in range(5):
            xx=x+(j-2)*s*.13
            _line(draw,_bezier((x,y-s*.15),(xx-s*.12,y-s*.48),(xx+s*.06,y-s*.72),(xx+s*.12,y-s*.88)),width)
    elif name == "lemon":
        pts=_bezier((x-s*.52,y),(x-s*.35,y-s*.4),(x+s*.35,y-s*.4),(x+s*.52,y))
        pts+=_bezier((x+s*.52,y),(x+s*.35,y+s*.4),(x-s*.35,y+s*.4),(x-s*.52,y))[1:]
        _line(draw,pts,width)
        _leaf(draw,x+s*.2,y-s*.22,s*.3,width)
        _line(draw,[(x-s*.52,y),(x-s*.65,y-s*.05)],width)
        _line(draw,[(x+s*.52,y),(x+s*.65,y-s*.05)],width)
    elif name == "cherries":
        _line(draw,_bezier((x-s*.12,y-s*.1),(x-s*.3,y-s*.55),(x+s*.12,y-s*.62),(x+s*.15,y-s*.7)),width)
        _line(draw,_bezier((x+s*.15,y-s*.1),(x+s*.25,y-s*.48),(x+s*.48,y-s*.55),(x+s*.5,y-s*.65)),width)
        draw.ellipse((x-s*.48,y-s*.05,x+s*.04,y+s*.48),outline=0,width=width)
        draw.ellipse((x+s*.1,y-s*.05,x+s*.62,y+s*.48),outline=0,width=width)
        _leaf(draw,x+s*.08,y-s*.62,s*.35,width)
    elif name == "peach":
        draw.ellipse((x-s*.48,y-s*.42,x+s*.48,y+s*.5),outline=0,width=width)
        _line(draw,_bezier((x,y-s*.35),(x-s*.14,y-s*.12),(x-s*.12,y+s*.18),(x,y+s*.36)),max(4,width//2))
        _line(draw,[(x,y-s*.42),(x+variant*5,y-s*.58)],width)
        _leaf(draw,x,y-s*.55,s*.28,width)
    elif name == "avocado":
        pts=_bezier((x,y-s*.55),(x-s*.25,y-s*.48),(x-s*.52,y-s*.05),(x-s*.42,y+s*.32))
        pts+=_bezier((x-s*.42,y+s*.32),(x-s*.3,y+s*.62),(x+s*.3,y+s*.62),(x+s*.42,y+s*.32))[1:]
        pts+=_bezier((x+s*.42,y+s*.32),(x+s*.52,y-s*.05),(x+s*.25,y-s*.48),(x,y-s*.55))[1:]
        _line(draw,pts,width)
        draw.ellipse((x-s*.18,y+s*.05,x+s*.18,y+s*.4),outline=0,width=width)
        _leaf(draw,x+s*.1,y-s*.45,s*.28,width)

def generate_artwork(theme: str, count: int, output_dir: str | Path, dpi: int = 300, line_width_pt: float = 2.4) -> list[Path]:
    if theme != "fruit" and theme not in THEME_DESIGNS:
        raise ValueError(f"Unsupported theme: {theme}. Supported themes: fruit, flowers, toys, birds, animals, professions")
    if count < 1 or count > 50:
        raise ValueError("illustration count must be between 1 and 50")
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
        scale = 1320 if index % 3 else 1240
        cx, cy = PAGE_W // 2, PAGE_H // 2 + (index % 2) * 30
        designs = DESIGNS if theme == "fruit" else THEME_DESIGNS[theme]
        name = designs[index % len(designs)]
        if theme == "fruit":
            _fruit(draw, name, cx, cy, scale, line_px, index)
        else:
            draw_theme_art(draw,theme,name,cx,cy,scale,line_px,index)
        if index >= len(designs):
            # Distinct, low-detail companion motifs keep longer volumes varied.
            accent = designs[(index * 5 + 3) % len(designs)]
            if theme == "fruit":
                _fruit(draw, accent, cx + 540, cy + 620, 360, max(4,line_px-2), index + 1)
                _leaf(draw, cx - 560, cy - 600, 210, max(4,line_px-2))
            else:
                draw_theme_art(draw,theme,accent,cx+520,cy+610,360,max(4,line_px-2),index+1)
        safe_name=name.replace(" ","_")
        path = output / f"{theme}_{index+1:02d}_{safe_name}.png"
        image.save(path, format="PNG", dpi=(dpi,dpi), optimize=True)
        paths.append(path)
    return paths
