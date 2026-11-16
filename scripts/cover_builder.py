"""Build one flattened, full-wrap paperback cover PDF with embedded TrueType fonts."""
from __future__ import annotations
import os
from pathlib import Path
import reportlab
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from scripts.cover_calculator import calculate_cover_dimensions

PT = 72.0

def _cmyk(hex_value: str):
    value=hex_value.lstrip("#")
    r,g,b=(int(value[i:i+2],16)/255 for i in (0,2,4))
    k=1-max(r,g,b)
    if k>=1:
        return colors.CMYKColor(0,0,0,1)
    c=(1-r-k)/(1-k)
    m=(1-g-k)/(1-k)
    y=(1-b-k)/(1-k)
    return colors.CMYKColor(c,m,y,k)

def _register_fonts() -> None:
    font_dir = Path(os.path.dirname(reportlab.__file__)) / "fonts"
    regular = font_dir / "Vera.ttf"
    bold = font_dir / "VeraBd.ttf"
    if not regular.is_file() or not bold.is_file():
        raise FileNotFoundError("ReportLab bundled Vera TrueType fonts are required for embedded cover typography")
    if "KdpVera" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KdpVera", str(regular)))
    if "KdpVera-Bold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KdpVera-Bold", str(bold)))

def _fruit_icon(pdf, cx: float, cy: float, radius: float, color, kind: int) -> None:
    pdf.setFillColor(color)
    pdf.setStrokeColor(_cmyk("#202020"))
    pdf.setLineWidth(2.2)
    if kind % 4 == 0:
        pdf.circle(cx, cy, radius, stroke=1, fill=1)
        pdf.setFillColor(_cmyk("#4E8B43"))
        pdf.ellipse(cx-2, cy+radius-5, cx+radius*.42, cy+radius+12, stroke=1, fill=1)
    elif kind % 4 == 1:
        p=pdf.beginPath()
        p.moveTo(cx,cy-radius)
        p.curveTo(cx-radius*1.1,cy-radius*.1,cx-radius*.7,cy+radius,cx,cy+radius*.65)
        p.curveTo(cx+radius*.7,cy+radius,cx+radius*1.1,cy-radius*.1,cx,cy-radius)
        pdf.drawPath(p,stroke=1,fill=1)
        pdf.setStrokeColor(_cmyk("#4E8B43"))
        pdf.line(cx,cy+radius*.55,cx+8,cy+radius+12)
    elif kind % 4 == 2:
        pdf.setFillColor(color)
        pdf.roundRect(cx-radius,cy-radius*.65,radius*2,radius*1.3,radius*.45,stroke=1,fill=1)
        pdf.setStrokeColor(_cmyk("#202020"))
        pdf.line(cx-radius*.85,cy+radius*.2,cx+radius*.85,cy+radius*.2)
    else:
        pdf.ellipse(cx-radius*.8,cy-radius,cx+radius*.8,cy+radius,stroke=1,fill=1)
        pdf.setFillColor(_cmyk("#4E8B43"))
        pdf.wedge(cx-8,cy+radius*.65,cx+radius*.9,cy+radius*1.5,0,90,stroke=1,fill=1)

def build_cover(meta: dict, output_path: str | Path) -> Path:
    _register_fonts()
    trim = meta["trim"]
    page_count = int(meta["interior"]["page_count"])
    dimensions = calculate_cover_dimensions(
        page_count, float(trim["width_in"]), float(trim["height_in"]),
        meta["interior"]["paper"], float(trim["bleed_in"])
    )
    width = dimensions["cover_width_in"] * PT
    height = dimensions["cover_height_in"] * PT
    bleed = dimensions["bleed_in"] * PT
    trim_w = float(trim["width_in"]) * PT
    trim_h = float(trim["height_in"]) * PT
    spine_w = dimensions["spine_width_in"] * PT
    back_x = bleed
    spine_x = bleed + trim_w
    front_x = spine_x + spine_w
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(width,height), pageCompression=1, invariant=1)
    # Opaque CMYK backgrounds extend through the bleed to the outer PDF edge.
    pdf.setFillColor(_cmyk("#E6F0FF"))
    pdf.rect(0,0,spine_x,height,stroke=0,fill=1)
    pdf.setFillColor(_cmyk("#FFF4D6"))
    pdf.rect(front_x,0,width-front_x,height,stroke=0,fill=1)
    pdf.setFillColor(_cmyk("#F3E6C8"))
    pdf.rect(spine_x,0,spine_w,height,stroke=0,fill=1)
    # Back cover copy is intentionally modest and remains within the safe area.
    pdf.setFillColor(_cmyk("#202020"))
    pdf.setFont("KdpVera-Bold",20)
    pdf.drawString(back_x+36,height-92,"A fruity first coloring adventure!")
    pdf.setFont("KdpVera",11)
    back_lines = [
        "Meet a cheerful collection of familiar fruits.",
        "Big, clear pictures give young artists room",
        "to color, explore shapes, and have fun.",
        "",
        "• Large 8.5 × 11 inch pages",
        "• Bold, easy-to-follow outlines",
        "• One illustration per sheet",
        "• Blank reverse sides",
        "",
        "Made for young creators ages 4–8."
    ]
    y = height - 125
    for line in back_lines:
        if line:
            pdf.drawString(back_x+36,y,line)
        y -= 21
    # Leave a clear, unprinted barcode placement area on the lower back cover.
    if meta.get("cover",{}).get("reserve_barcode_area",True):
        bw=float(meta.get("cover",{}).get("barcode_area_width_in",2.0))*PT
        bh=float(meta.get("cover",{}).get("barcode_area_height_in",1.2))*PT
        pdf.setFillColor(_cmyk("#FFFFFF"))
        pdf.rect(back_x+trim_w-bw-24,bleed+20,bw,bh,stroke=0,fill=1)
    # Front cover composition.
    front_center = front_x + trim_w/2
    pdf.setFillColor(_cmyk("#263238"))
    pdf.setFont("KdpVera-Bold",34)
    pdf.drawCentredString(front_center,height-112,str(meta["title"]).upper())
    pdf.setFont("KdpVera",14)
    pdf.drawCentredString(front_center,height-143,str(meta.get("subtitle","")))
    palette = ["#F16B5B","#F4B942","#79B96A","#E78AA7","#F3D46B","#E58B48"]
    positions = [
        (front_center-110,height*.54,48),(front_center,height*.49,58),
        (front_center+110,height*.54,48),(front_center-65,height*.36,42),
        (front_center+65,height*.36,42)
    ]
    for i,(cx,cy,radius) in enumerate(positions):
        _fruit_icon(pdf,cx,cy,radius,_cmyk(palette[i%len(palette)]),i)
    pdf.setFillColor(_cmyk("#263238"))
    pdf.setFont("KdpVera-Bold",12)
    pdf.drawCentredString(front_center,bleed+45,"BIG & EASY PICTURES  •  AGES 4–8")
    # No spine lettering: sample has a narrow spine and KDP's fold tolerance must be respected.
    pdf.showPage()
    pdf.save()
    return output
