"""Original, generic, child-safe outline motifs for non-fruit coloring-book themes."""
from __future__ import annotations
import math

FLOWERS=["daisy","tulip","sunflower","rose","lily","poppy","wildflower","bluebell","hibiscus","lotus","dandelion","bouquet"]
TOYS=["ball","teddy bear","building blocks","toy car","kite","toy train","robot","sailboat","drum","spinning top","puzzle piece","crayon"]
BIRDS=["songbird","duck","owl","penguin","parrot","peacock","flamingo","chick","swan","woodpecker","eagle","robin"]
ANIMALS=["cat","dog","rabbit","elephant","lion","turtle","fish","giraffe","bear","fox","horse","frog"]
PROFESSIONS=["doctor","teacher","chef","farmer","builder","pilot","firefighter","artist","scientist","veterinarian","gardener","astronaut"]

def _line(draw, pts, width):
    draw.line(pts,fill=0,width=width,joint="curve")

def _ellipse(draw, box, width):
    draw.ellipse(box,outline=0,width=width)

def _rect(draw, box, width, radius=0):
    if radius:
        draw.rounded_rectangle(box,radius=radius,outline=0,width=width)
    else:
        draw.rectangle(box,outline=0,width=width)

def _poly(draw, pts, width):
    points=list(pts)
    if points and points[0]!=points[-1]:
        points.append(points[0])
    _line(draw,points,width)

def _bezier(p0,p1,p2,p3,steps=36):
    out=[]
    for i in range(steps+1):
        t=i/steps
        u=1-t
        x=u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0]
        y=u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]
        out.append((round(x),round(y)))
    return out

def _leaf(draw,x,y,s,w,flip=1):
    pts=_bezier((x,y),(x+flip*s*.45,y-s*.55),(x+flip*s,y-s*.45),(x+flip*s*1.1,y))
    pts+=_bezier((x+flip*s*1.1,y),(x+flip*s*.65,y+s*.35),(x+flip*s*.25,y+s*.28),(x,y))[1:]
    _line(draw,pts,w)
    _line(draw,[(x,y),(x+flip*s,y)],max(3,w//3))

def _flower(draw,name,cx,cy,s,w,index):
    if name=="tulip":
        pts=_bezier((cx-s*.35,cy),(cx-s*.5,cy-s*.25),(cx-s*.3,cy-s*.65),(cx,cy-s*.4))
        pts+=_bezier((cx,cy-s*.4),(cx+s*.3,cy-s*.65),(cx+s*.5,cy-s*.25),(cx+s*.35,cy))[1:]
        pts+=_bezier((cx+s*.35,cy),(cx+s*.25,cy+s*.2),(cx-s*.25,cy+s*.2),(cx-s*.35,cy))[1:]
        _line(draw,pts,w)
    else:
        petals=6+(index%4)
        radius=s*.34
        for i in range(petals):
            angle=2*math.pi*i/petals
            px=cx+math.cos(angle)*radius
            py=cy+math.sin(angle)*radius
            rw=s*(.18 if name in {"sunflower","daisy"} else .22)
            _ellipse(draw,(px-rw,py-rw*1.2,px+rw,py+rw*1.2),w)
        _ellipse(draw,(cx-s*.2,cy-s*.2,cx+s*.2,cy+s*.2),w)
        if name in {"sunflower","daisy"}:
            for j in range(8):
                a=2*math.pi*j/8
                _ellipse(draw,(cx+math.cos(a)*s*.12-5,cy+math.sin(a)*s*.12-5,cx+math.cos(a)*s*.12+5,cy+math.sin(a)*s*.12+5),max(3,w//3))
    _line(draw,[(cx,cy+s*.25),(cx+((index%3)-1)*s*.03,cy+s*.92)],w)
    _leaf(draw,cx,cy+s*.58,s*.38,w,1)
    _leaf(draw,cx,cy+s*.78,s*.32,w,-1)
    if index%2:
        _ellipse(draw,(cx-s*.7,cy-s*.9,cx-s*.58,cy-s*.78),max(3,w//2))
        _ellipse(draw,(cx+s*.58,cy-s*.86,cx+s*.7,cy-s*.74),max(3,w//2))

def _toy(draw,name,cx,cy,s,w,index):
    if name=="ball":
        _ellipse(draw,(cx-s*.48,cy-s*.48,cx+s*.48,cy+s*.48),w)
        _line(draw,_bezier((cx-s*.42,cy-s*.15),(cx-s*.05,cy-s*.48),(cx+s*.1,cy+s*.4),(cx+s*.42,cy+s*.15)),w)
        _line(draw,_bezier((cx-s*.12,cy-s*.46),(cx+s*.32,cy-s*.12),(cx-s*.32,cy+s*.12),(cx+s*.12,cy+s*.46)),w)
    elif name=="teddy bear":
        _ellipse(draw,(cx-s*.32,cy-s*.45,cx+s*.32,cy+s*.18),w)
        _ellipse(draw,(cx-s*.5,cy-s*.62,cx-s*.2,cy-s*.32),w)
        _ellipse(draw,(cx+s*.2,cy-s*.62,cx+s*.5,cy-s*.32),w)
        _ellipse(draw,(cx-s*.42,cy+s*.05,cx+s*.42,cy+s*.78),w)
        _ellipse(draw,(cx-s*.58,cy+s*.12,cx-s*.28,cy+s*.55),w)
        _ellipse(draw,(cx+s*.28,cy+s*.12,cx+s*.58,cy+s*.55),w)
        _ellipse(draw,(cx-s*.38,cy+s*.6,cx-s*.05,cy+s*.9),w)
        _ellipse(draw,(cx+s*.05,cy+s*.6,cx+s*.38,cy+s*.9),w)
        _ellipse(draw,(cx-s*.1,cy-s*.05,cx+s*.1,cy+s*.12),max(3,w//2))
    elif name=="building blocks":
        _rect(draw,(cx-s*.48,cy+s*.05,cx-s*.02,cy+s*.5),w)
        _rect(draw,(cx+s*.02,cy-s*.38,cx+s*.48,cy+s*.05),w)
        _rect(draw,(cx-s*.48,cy-s*.42,cx-s*.04,cy-s*.02),w)
        for x,y in [(cx-s*.25,cy+s*.25),(cx+s*.25,cy-s*.15),(cx-s*.25,cy-s*.22)]:
            _ellipse(draw,(x-s*.06,y-s*.06,x+s*.06,y+s*.06),max(3,w//2))
    elif name=="toy car":
        _rect(draw,(cx-s*.58,cy-s*.08,cx+s*.58,cy+s*.38),w,int(s*.08))
        _poly(draw,[(cx-s*.3,cy-s*.08),(cx-s*.12,cy-s*.38),(cx+s*.22,cy-s*.38),(cx+s*.42,cy-s*.08)],w)
        _ellipse(draw,(cx-s*.4,cy+s*.24,cx-s*.18,cy+s*.48),w)
        _ellipse(draw,(cx+s*.18,cy+s*.24,cx+s*.4,cy+s*.48),w)
        _line(draw,[(cx-s*.08,cy-s*.32),(cx-s*.08,cy-s*.08)],max(3,w//2))
    elif name=="kite":
        _poly(draw,[(cx,cy-s*.58),(cx+s*.45,cy),(cx,cy+s*.58),(cx-s*.45,cy)],w)
        _line(draw,[(cx,cy-s*.58),(cx,cy+s*.58)],max(3,w//2))
        _line(draw,[(cx-s*.45,cy),(cx+s*.45,cy)],max(3,w//2))
        _line(draw,_bezier((cx,cy+s*.58),(cx-s*.2,cy+s*.8),(cx+s*.25,cy+s*.85),(cx,cy+s*1.05)),w)
        for i in range(3):
            yy=cy+s*(.68+i*.1)
            _poly(draw,[(cx,yy),(cx-s*.08,yy+s*.06),(cx,yy+s*.12),(cx+s*.08,yy+s*.06)],max(3,w//2))
    elif name=="toy train":
        _rect(draw,(cx-s*.48,cy-s*.2,cx+s*.42,cy+s*.35),w,int(s*.06))
        _rect(draw,(cx-s*.3,cy-s*.48,cx+s*.1,cy-s*.2),w,int(s*.04))
        _rect(draw,(cx+s*.18,cy-s*.38,cx+s*.42,cy-s*.2),w)
        for x in [cx-s*.28,cx+s*.2]:
            _ellipse(draw,(x-s*.12,cy+s*.25,x+s*.12,cy+s*.5),w)
        _line(draw,[(cx-s*.5,cy+s*.48),(cx+s*.5,cy+s*.48)],w)
    elif name=="robot":
        _rect(draw,(cx-s*.28,cy-s*.5,cx+s*.28,cy-s*.08),w,int(s*.06))
        _rect(draw,(cx-s*.38,cy-s*.02,cx+s*.38,cy+s*.5),w,int(s*.06))
        _ellipse(draw,(cx-s*.16,cy-s*.36,cx-s*.04,cy-s*.24),max(3,w//2))
        _ellipse(draw,(cx+s*.04,cy-s*.36,cx+s*.16,cy-s*.24),max(3,w//2))
        _line(draw,[(cx,cy-s*.5),(cx,cy-s*.68)],w)
        _ellipse(draw,(cx-s*.06,cy-s*.74,cx+s*.06,cy-s*.62),w)
        _line(draw,[(cx-s*.38,cy+s*.08),(cx-s*.58,cy+s*.28),(cx-s*.48,cy+s*.42)],w)
        _line(draw,[(cx+s*.38,cy+s*.08),(cx+s*.58,cy+s*.28),(cx+s*.48,cy+s*.42)],w)
        _line(draw,[(cx-s*.18,cy+s*.5),(cx-s*.2,cy+s*.72),(cx-s*.32,cy+s*.72)],w)
        _line(draw,[(cx+s*.18,cy+s*.5),(cx+s*.2,cy+s*.72),(cx+s*.32,cy+s*.72)],w)
    elif name=="sailboat":
        _poly(draw,[(cx-s*.55,cy+s*.22),(cx+s*.55,cy+s*.22),(cx+s*.35,cy+s*.48),(cx-s*.35,cy+s*.48)],w)
        _line(draw,[(cx,cy-s*.58),(cx,cy+s*.2)],w)
        _poly(draw,[(cx-s*.02,cy-s*.5),(cx-s*.02,cy+s*.12),(cx-s*.42,cy+s*.12)],w)
        _poly(draw,[(cx+s*.06,cy-s*.35),(cx+s*.06,cy+s*.12),(cx+s*.4,cy+s*.12)],w)
        _line(draw,[(cx-s*.5,cy+s*.62),(cx-s*.2,cy+s*.62),(cx,cy+s*.62),(cx+s*.25,cy+s*.62),(cx+s*.5,cy+s*.62)],w)
    elif name=="drum":
        _rect(draw,(cx-s*.42,cy-s*.25,cx+s*.42,cy+s*.45),w,int(s*.08))
        _ellipse(draw,(cx-s*.42,cy-s*.38,cx+s*.42,cy-s*.08),w)
        _line(draw,[(cx-s*.18,cy-s*.6),(cx+s*.18,cy-s*.42)],w)
        _line(draw,[(cx+s*.18,cy-s*.6),(cx-s*.18,cy-s*.42)],w)
    elif name=="spinning top":
        _poly(draw,[(cx,cy-s*.55),(cx+s*.42,cy-s*.1),(cx+s*.28,cy+s*.35),(cx-s*.28,cy+s*.35),(cx-s*.42,cy-s*.1)],w)
        _line(draw,[(cx,cy-s*.55),(cx,cy+s*.65)],w)
        _ellipse(draw,(cx-s*.1,cy-s*.1,cx+s*.1,cy+s*.1),max(3,w//2))
    elif name=="puzzle piece":
        _rect(draw,(cx-s*.42,cy-s*.42,cx+s*.42,cy+s*.42),w)
        _ellipse(draw,(cx-s*.12,cy-s*.56,cx+s*.12,cy-s*.32),w)
        _ellipse(draw,(cx+s*.3,cy-s*.12,cx+s*.54,cy+s*.12),w)
        _ellipse(draw,(cx-s*.12,cy+s*.3,cx+s*.12,cy+s*.54),w)
    else:
        _poly(draw,[(cx-s*.18,cy-s*.58),(cx+s*.18,cy-s*.58),(cx+s*.12,cy+s*.32),(cx+s*.3,cy+s*.5),(cx-s*.3,cy+s*.5),(cx-s*.12,cy+s*.32)],w)
        _line(draw,[(cx-s*.1,cy-s*.4),(cx+s*.1,cy+s*.2)],max(3,w//2))

def _bird(draw,name,cx,cy,s,w,index):
    _ellipse(draw,(cx-s*.38,cy-s*.12,cx+s*.32,cy+s*.42),w)
    _ellipse(draw,(cx+s*.08,cy-s*.42,cx+s*.46,cy-s*.02),w)
    _poly(draw,[(cx+s*.43,cy-s*.22),(cx+s*.7,cy-s*.1),(cx+s*.43,cy+s*.02)],w)
    _ellipse(draw,(cx+s*.28,cy-s*.28,cx+s*.34,cy-s*.22),max(3,w//2))
    _ellipse(draw,(cx-s*.22,cy-s*.03,cx+s*.1,cy+s*.27),max(4,w//2))
    _line(draw,[(cx-s*.05,cy+s*.4),(cx-s*.05,cy+s*.58),(cx-s*.18,cy+s*.62)],w)
    _line(draw,[(cx+s*.18,cy+s*.4),(cx+s*.18,cy+s*.58),(cx+s*.3,cy+s*.62)],w)
    _line(draw,[(cx-s*.38,cy+s*.02),(cx-s*.6,cy-s*.18),(cx-s*.55,cy+s*.2)],w)
    if name=="owl":
        _ellipse(draw,(cx+s*.12,cy-s*.3,cx+s*.3,cy-s*.12),w)
        _ellipse(draw,(cx+s*.3,cy-s*.3,cx+s*.48,cy-s*.12),w)
    elif name=="peacock":
        for i in range(5):
            xx=cx-s*.48+i*s*.18
            _line(draw,[(cx-s*.25,cy+s*.1),(xx,cy-s*.58)],w)
            _ellipse(draw,(xx-s*.06,cy-s*.66,xx+s*.06,cy-s*.54),max(3,w//2))
    elif name=="flamingo":
        _line(draw,_bezier((cx+s*.12,cy+s*.05),(cx+s*.6,cy-s*.05),(cx+s*.55,cy-s*.65),(cx+s*.28,cy-s*.5)),w)
    elif name=="penguin":
        _ellipse(draw,(cx-s*.2,cy-s*.02,cx+s*.2,cy+s*.35),max(3,w//2))
    elif name=="duck":
        _poly(draw,[(cx+s*.43,cy-s*.18),(cx+s*.72,cy-s*.1),(cx+s*.43,cy+s*.02)],w)
    else:
        _line(draw,[(cx-s*.1,cy-s*.12),(cx-s*.35,cy-s*.32),(cx-s*.45,cy-s*.42)],w)
    if index%2:
        _line(draw,[(cx-s*.5,cy-s*.58),(cx-s*.62,cy-s*.72)],max(3,w//2))

def _animal(draw,name,cx,cy,s,w,index):
    _ellipse(draw,(cx-s*.42,cy-s*.02,cx+s*.28,cy+s*.45),w)
    _ellipse(draw,(cx+s*.12,cy-s*.38,cx+s*.52,cy+s*.08),w)
    # Legs and tail
    for dx in [-.27,.12]:
        _line(draw,[(cx+s*dx,cy+s*.32),(cx+s*dx,cy+s*.62)],w)
    _line(draw,_bezier((cx-s*.4,cy+s*.1),(cx-s*.65,cy-s*.02),(cx-s*.62,cy-s*.25),(cx-s*.5,cy-s*.25)),w)
    if name=="cat":
        _poly(draw,[(cx+s*.17,cy-s*.27),(cx+s*.18,cy-s*.55),(cx+s*.34,cy-s*.35)],w)
        _poly(draw,[(cx+s*.36,cy-s*.35),(cx+s*.52,cy-s*.55),(cx+s*.5,cy-s*.22)],w)
        for i in range(3):
            _line(draw,[(cx+s*.42,cy-s*.12),(cx+s*.66,cy-s*.16+i*s*.08)],max(3,w//2))
    elif name=="dog":
        _ellipse(draw,(cx+s*.08,cy-s*.28,cx+s*.28,cy+s*.02),w)
        _ellipse(draw,(cx+s*.35,cy-s*.25,cx+s*.6,cy+s*.08),w)
    elif name=="rabbit":
        _ellipse(draw,(cx+s*.18,cy-s*.78,cx+s*.32,cy-s*.22),w)
        _ellipse(draw,(cx+s*.36,cy-s*.76,cx+s*.5,cy-s*.2),w)
    elif name=="elephant":
        _ellipse(draw,(cx+s*.06,cy-s*.38,cx+s*.6,cy+s*.2),w)
        _line(draw,_bezier((cx+s*.47,cy-s*.02),(cx+s*.7,cy+s*.12),(cx+s*.62,cy+s*.35),(cx+s*.48,cy+s*.38)),w)
    elif name=="lion":
        _ellipse(draw,(cx+s*.04,cy-s*.48,cx+s*.64,cy+s*.2),w)
        for i in range(8):
            a=math.pi*2*i/8
            px=cx+s*.34+math.cos(a)*s*.36
            py=cy-s*.14+math.sin(a)*s*.36
            _ellipse(draw,(px-s*.08,py-s*.08,px+s*.08,py+s*.08),max(3,w//2))
    elif name=="turtle":
        _ellipse(draw,(cx-s*.38,cy-s*.18,cx+s*.28,cy+s*.35),w)
        _ellipse(draw,(cx+s*.25,cy-s*.02,cx+s*.52,cy+s*.22),w)
        for dx in [-.22,.12]:
            _line(draw,[(cx+s*dx,cy+s*.25),(cx+s*(dx-.08),cy+s*.48)],w)
    elif name=="fish":
        _ellipse(draw,(cx-s*.48,cy-s*.25,cx+s*.38,cy+s*.25),w)
        _poly(draw,[(cx+s*.36,cy),(cx+s*.65,cy-s*.25),(cx+s*.65,cy+s*.25)],w)
        _ellipse(draw,(cx+s*.18,cy-s*.08,cx+s*.26,cy),max(3,w//2))
    elif name=="giraffe":
        _rect(draw,(cx+s*.05,cy-s*.42,cx+s*.35,cy+s*.25),w,int(s*.1))
        for dx,dy in [(.1,-.2),(.28,.0),(.15,.18)]:
            _ellipse(draw,(cx+s*dx-10,cy+s*dy-10,cx+s*dx+10,cy+s*dy+10),max(3,w//2))
    elif name=="bear":
        _ellipse(draw,(cx+s*.14,cy-s*.48,cx+s*.5,cy-s*.08),w)
        _ellipse(draw,(cx+s*.1,cy-s*.58,cx+s*.24,cy-s*.42),w)
        _ellipse(draw,(cx+s*.4,cy-s*.58,cx+s*.54,cy-s*.42),w)
    elif name=="fox":
        _poly(draw,[(cx+s*.14,cy-s*.15),(cx+s*.12,cy-s*.5),(cx+s*.32,cy-s*.32)],w)
        _poly(draw,[(cx+s*.34,cy-s*.32),(cx+s*.56,cy-s*.5),(cx+s*.5,cy-s*.12)],w)
    elif name=="horse":
        _line(draw,[(cx+s*.15,cy-s*.15),(cx+s*.32,cy-s*.5),(cx+s*.55,cy-s*.35)],w)
        _line(draw,[(cx+s*.25,cy-s*.32),(cx+s*.45,cy-s*.55)],w)
    elif name=="frog":
        _ellipse(draw,(cx+s*.1,cy-s*.4,cx+s*.55,cy+s*.08),w)
        _ellipse(draw,(cx+s*.12,cy-s*.55,cx+s*.28,cy-s*.35),w)
        _ellipse(draw,(cx+s*.38,cy-s*.55,cx+s*.54,cy-s*.35),w)
    else:
        _ellipse(draw,(cx+s*.22,cy-s*.3,cx+s*.3,cy-s*.22),max(3,w//2))

def _profession(draw,name,cx,cy,s,w,index):
    # Generic child figure; no brand insignia, emblems, or trademarked uniforms.
    _ellipse(draw,(cx-s*.2,cy-s*.62,cx+s*.2,cy-s*.22),w)
    _ellipse(draw,(cx-s*.06,cy-s*.44,cx+s*.0,cy-s*.38),max(3,w//2))
    _ellipse(draw,(cx+s*.08,cy-s*.44,cx+s*.14,cy-s*.38),max(3,w//2))
    _line(draw,_bezier((cx-s*.04,cy-s*.29),(cx,cy-s*.22),(cx+s*.05,cy-s*.22),(cx+s*.08,cy-s*.29)),max(3,w//2))
    _rect(draw,(cx-s*.26,cy-s*.18,cx+s*.26,cy+s*.42),w,int(s*.08))
    _line(draw,[(cx-s*.24,cy-s*.05),(cx-s*.48,cy+s*.25),(cx-s*.4,cy+s*.38)],w)
    _line(draw,[(cx+s*.24,cy-s*.05),(cx+s*.48,cy+s*.25),(cx+s*.4,cy+s*.38)],w)
    _line(draw,[(cx-s*.12,cy+s*.42),(cx-s*.18,cy+s*.78)],w)
    _line(draw,[(cx+s*.12,cy+s*.42),(cx+s*.18,cy+s*.78)],w)
    # Profession-specific, generic accessories.
    if name in {"doctor","veterinarian"}:
        _line(draw,_bezier((cx-s*.1,cy-s*.05),(cx-s*.35,cy+s*.05),(cx-s*.28,cy+s*.45),(cx,cy+s*.3)),w)
        _ellipse(draw,(cx-s*.04,cy+s*.23,cx+s*.08,cy+s*.35),max(3,w//2))
    elif name=="teacher":
        _rect(draw,(cx+s*.42,cy+s*.08,cx+s*.75,cy+s*.4),w,int(s*.03))
        _line(draw,[(cx+s*.58,cy+s*.08),(cx+s*.58,cy+s*.4)],max(3,w//2))
    elif name=="chef":
        _ellipse(draw,(cx-s*.24,cy-s*.84,cx+s*.24,cy-s*.48),w)
        _line(draw,[(cx-s*.2,cy-s*.5),(cx+s*.2,cy-s*.5)],w)
    elif name in {"farmer","gardener"}:
        _line(draw,[(cx-s*.28,cy-s*.5),(cx+s*.28,cy-s*.5)],w)
        _line(draw,[(cx-s*.18,cy-s*.68),(cx+s*.18,cy-s*.68)],w)
        if name=="gardener":
            _line(draw,[(cx+s*.5,cy+s*.1),(cx+s*.7,cy-s*.15),(cx+s*.7,cy+s*.35)],w)
    elif name=="builder":
        _line(draw,[(cx-s*.25,cy-s*.5),(cx+s*.25,cy-s*.5)],w)
        _line(draw,[(cx-s*.15,cy-s*.72),(cx+s*.15,cy-s*.72)],w)
    elif name=="pilot":
        _line(draw,[(cx-s*.2,cy-s*.5),(cx+s*.2,cy-s*.5)],w)
        _poly(draw,[(cx-s*.2,cy-s*.5),(cx,cy-s*.75),(cx+s*.2,cy-s*.5)],w)
    elif name=="firefighter":
        _line(draw,_bezier((cx-s*.25,cy-s*.45),(cx-s*.35,cy-s*.75),(cx+s*.35,cy-s*.75),(cx+s*.25,cy-s*.45)),w)
    elif name=="artist":
        _ellipse(draw,(cx+s*.4,cy+s*.05,cx+s*.75,cy+s*.4),w)
        for dx,dy in [(.5,.15),(.65,.2),(.55,.32)]:
            _ellipse(draw,(cx+s*dx-5,cy+s*dy-5,cx+s*dx+5,cy+s*dy+5),max(3,w//2))
    elif name=="scientist":
        _poly(draw,[(cx+s*.42,cy+s*.02),(cx+s*.68,cy+s*.02),(cx+s*.6,cy+s*.42),(cx+s*.5,cy+s*.42)],w)
        _line(draw,[(cx+s*.45,cy+s*.2),(cx+s*.64,cy+s*.2)],max(3,w//2))
    elif name=="astronaut":
        _ellipse(draw,(cx-s*.3,cy-s*.75,cx+s*.3,cy-s*.1),w)
        _ellipse(draw,(cx-s*.18,cy-s*.62,cx+s*.18,cy-s*.25),max(3,w//2))

def draw_theme_art(draw,theme,name,cx,cy,scale,width,index):
    if theme=="flowers":
        _flower(draw,name,cx,cy,scale,width,index)
    elif theme=="toys":
        _toy(draw,name,cx,cy,scale,width,index)
    elif theme=="birds":
        _bird(draw,name,cx,cy,scale,width,index)
    elif theme=="animals":
        _animal(draw,name,cx,cy,scale,width,index)
    elif theme=="professions":
        _profession(draw,name,cx,cy,scale,width,index)
    else:
        raise ValueError(f"Unsupported theme: {theme}")
