"""Structural, geometry, resolution, blank-verso, and font checks for KDP PDFs."""
from __future__ import annotations
import math
import hashlib
from pathlib import Path
from typing import Any
from pypdf import PdfReader
from pypdf.generic import ContentStream

PAINT_OPERATORS = {b"S",b"s",b"f",b"F",b"f*",b"B",b"B*",b"b",b"b*",b"Do",b"Tj",b"TJ",b"' ",b'"'}

def _obj(value):
    return value.get_object() if hasattr(value,"get_object") else value

def _page_size(page):
    box=page.mediabox
    return float(box.width)/72.0,float(box.height)/72.0

def _resources(page):
    return _obj(page.get("/Resources",{})) or {}

def _xobjects(page):
    resources=_resources(page)
    xobjects=_obj(resources.get("/XObject",{})) or {}
    return {str(k):_obj(v) for k,v in xobjects.items()}

def _image_placements(page, reader):
    contents=page.get_contents()
    if contents is None:
        return []
    stream=ContentStream(contents,reader)
    xobjects=_xobjects(page)
    matrix=None
    stack=[]
    placements=[]
    for operands,operator in stream.operations:
        if operator==b"q":
            stack.append(matrix)
        elif operator==b"Q":
            matrix=stack.pop() if stack else None
        elif operator==b"cm":
            matrix=[float(v) for v in operands]
        elif operator==b"Do" and operands:
            name=str(operands[0])
            obj=xobjects.get(name)
            if obj is not None and obj.get("/Subtype")=="/Image":
                if matrix and len(matrix)==6:
                    a,b,c,d,_,_=matrix
                    width_pt=math.hypot(a,b)
                    height_pt=math.hypot(c,d)
                else:
                    width_pt=height_pt=0.0
                placements.append({
                    "name":name,
                    "width_px":int(obj.get("/Width",0)),
                    "height_px":int(obj.get("/Height",0)),
                    "width_pt":width_pt,
                    "height_pt":height_pt,
                    "has_soft_mask":bool(obj.get("/SMask") or obj.get("/Mask")),
                    "content_sha256":hashlib.sha256(obj.get_data()).hexdigest(),
                })
    return placements

def _fonts_embedded(page):
    resources=_resources(page)
    fonts=_obj(resources.get("/Font",{})) or {}
    if not fonts:
        return False
    found=False
    for _,font_ref in fonts.items():
        font=_obj(font_ref)
        candidates=[font]
        descendants=_obj(font.get("/DescendantFonts",[])) or []
        candidates.extend(_obj(item) for item in descendants)
        for candidate in candidates:
            descriptor=_obj(candidate.get("/FontDescriptor")) if candidate.get("/FontDescriptor") else None
            if descriptor and any(descriptor.get(key) for key in ("/FontFile","/FontFile2","/FontFile3")):
                found=True
    return found

def _uses_cmyk_only(page, reader):
    contents=page.get_contents()
    if contents is None:
        return False
    stream=ContentStream(contents,reader)
    operators=[operator for _,operator in stream.operations]
    if any(operator in {b"rg",b"RG"} for operator in operators):
        return False
    return any(operator in {b"k",b"K"} for operator in operators)

def _has_transparency(page):
    resources=_resources(page)
    ext=_obj(resources.get("/ExtGState",{})) or {}
    for _,state_ref in ext.items():
        state=_obj(state_ref)
        if float(state.get("/ca",1)) < 1 or float(state.get("/CA",1)) < 1:
            return True
        if state.get("/BM") not in (None,"/Normal","/Compatible"):
            return True
    for obj in _xobjects(page).values():
        if obj.get("/Group") and _obj(obj["/Group"]).get("/S")=="/Transparency":
            return True
        if obj.get("/Subtype")=="/Image" and (obj.get("/SMask") or obj.get("/Mask")):
            return True
    return False

def validate_book_config(meta: dict[str,Any]) -> list[str]:
    errors=[]
    try:
        page_count=int(meta["interior"]["page_count"])
        width=float(meta["trim"]["width_in"])
        height=float(meta["trim"]["height_in"])
        line=float(meta["interior"]["line_width_pt"])
        min_line=float(meta["interior"]["min_line_width_pt"])
        dpi=int(meta["interior"]["min_dpi"])
    except (KeyError,TypeError,ValueError) as exc:
        return [f"configuration is missing or has invalid required values: {exc}"]
    if not str(meta.get("title","")).strip():
        errors.append("title must not be empty")
    if page_count<24 or page_count%2:
        errors.append("page_count must be even and at least 24")
    if page_count>590:
        errors.append("page_count exceeds KDP's 590-page maximum for 8.5 x 11 in black-ink white-paper paperbacks")
    if width!=8.5 or height!=11.0:
        errors.append("sample series trim must be exactly 8.5 x 11 inches")
    if meta["interior"].get("single_sided") is not True:
        errors.append("single_sided must be true")
    if meta["interior"].get("blank_reverse_pages") is not True:
        errors.append("blank_reverse_pages must be true")
    if meta["interior"].get("illustration_page_parity")!="odd":
        errors.append("illustration_page_parity must be odd (recto)")
    if dpi<300:
        errors.append("min_dpi must be at least 300")
    if line<min_line or line<0.75:
        errors.append("line_width_pt must be at least the configured and KDP 0.75 pt minimum")
    if min_line<0.75:
        errors.append("min_line_width_pt must not be below KDP's 0.75 pt minimum")
    if meta["interior"].get("paper")!="white" or meta["interior"].get("ink")!="black":
        errors.append("the approved children's coloring-book profile requires black ink on white paper")
    if meta["trim"].get("interior_bleed") is not False:
        errors.append("this production profile uses no-bleed interior pages")
    if float(meta["trim"].get("bleed_in",0))!=0.125:
        errors.append("cover bleed must be 0.125 inches on each outside edge")
    expected=page_count//2
    if int(meta.get("content",{}).get("illustration_count",-1))!=expected:
        errors.append(f"illustration_count must equal page_count / 2 ({expected})")
    required_margin=0.375 if page_count<=150 else 0.5 if page_count<=300 else 0.625 if page_count<=500 else 0.75 if page_count<=700 else 0.875
    if float(meta["interior"].get("inside_margin_in",0))<required_margin:
        errors.append(f"inside_margin_in must be at least {required_margin:.3f} for this page-count band")
    if float(meta["interior"].get("outside_margin_in",0))<0.25:
        errors.append("outside_margin_in must be at least 0.25 for a no-bleed interior")
    if float(meta["interior"].get("top_margin_in",0))<0.25 or float(meta["interior"].get("bottom_margin_in",0))<0.25:
        errors.append("top and bottom margins must each be at least 0.25 for a no-bleed interior")
    return errors

def validate_book(interior_pdf: str|Path, cover_pdf: str|Path, meta: dict[str,Any]) -> dict[str,Any]:
    errors=validate_book_config(meta)
    result={
        "schema_version":1,"status":"FAIL","errors":errors,
        "interior":{},"cover":{},
        "policy_note":"Automated preflight only; KDP Print Previewer and owner visual approval remain mandatory."
    }
    interior_path,cover_path=Path(interior_pdf),Path(cover_pdf)
    if not interior_path.is_file():
        errors.append(f"interior PDF missing: {interior_path}")
    if not cover_path.is_file():
        errors.append(f"cover PDF missing: {cover_path}")
    if errors:
        result["errors"]=errors
        return result
    try:
        interior=PdfReader(str(interior_path),strict=True)
        cover=PdfReader(str(cover_path),strict=True)
        if interior.is_encrypted or cover.is_encrypted:
            errors.append("PDF files must not be encrypted or password protected")
        interior_metadata_absent=interior.metadata is None and interior.xmp_metadata is None
        cover_metadata_absent=cover.metadata is None and cover.xmp_metadata is None
        if not interior_metadata_absent:
            errors.append("interior PDF contains document metadata; KDP submission files must not contain metadata")
        if not cover_metadata_absent:
            errors.append("cover PDF contains document metadata; KDP submission files must not contain metadata")
        for path in (interior_path,cover_path):
            if path.stat().st_size>650*1024*1024:
                errors.append(f"PDF exceeds KDP's 650 MB file-size limit: {path.name}")
        expected_pages=int(meta["interior"]["page_count"])
        if len(interior.pages)!=expected_pages:
            errors.append(f"interior page count mismatch: expected {expected_pages}, found {len(interior.pages)}")
        expected_size=(float(meta["trim"]["width_in"]),float(meta["trim"]["height_in"]))
        art_count=0
        blank_count=0
        min_dpi=10_000.0
        seen_art_hashes=set()
        page_results=[]
        for page_index,page in enumerate(interior.pages):
            page_number=page_index+1
            actual=_page_size(page)
            if abs(actual[0]-expected_size[0])>0.001 or abs(actual[1]-expected_size[1])>0.001:
                errors.append(f"interior page {page_number} size is {actual[0]:.4f} x {actual[1]:.4f} in; expected {expected_size}")
            placements=_image_placements(page,interior)
            has_text=bool((page.extract_text() or "").strip())
            if page_number%2==1:
                art_count+=1
                if len(placements)!=1:
                    errors.append(f"art page {page_number} must contain exactly one raster illustration; found {len(placements)}")
                for image in placements:
                    if image["content_sha256"] in seen_art_hashes:
                        errors.append(f"art page {page_number} reuses an identical illustration already used earlier in this volume")
                    seen_art_hashes.add(image["content_sha256"])
                    if image["has_soft_mask"]:
                        errors.append(f"art page {page_number} contains transparency or a soft mask")
                    if image["width_pt"]<=0 or image["height_pt"]<=0:
                        errors.append(f"art page {page_number} image placement could not be measured")
                    else:
                        dpi_x=image["width_px"]/(image["width_pt"]/72)
                        dpi_y=image["height_px"]/(image["height_pt"]/72)
                        actual_dpi=min(dpi_x,dpi_y)
                        min_dpi=min(min_dpi,actual_dpi)
                        if actual_dpi<float(meta["interior"]["min_dpi"]):
                            errors.append(f"art page {page_number} effective resolution {actual_dpi:.1f} DPI is below {meta['interior']['min_dpi']}")
                if has_text:
                    errors.append(f"art page {page_number} contains text; coloring artwork pages must not contain unintended text")
            else:
                blank_count+=1
                if placements or has_text or page.get("/Annots"):
                    errors.append(f"reverse page {page_number} is not completely blank")
                contents=page.get_contents()
                if contents is not None:
                    stream=ContentStream(contents,interior)
                    if any(op in PAINT_OPERATORS for _,op in stream.operations):
                        errors.append(f"reverse page {page_number} contains drawing or paint operators")
            if _has_transparency(page):
                errors.append(f"interior page {page_number} contains transparency")
            page_results.append({"page":page_number,"type":"art" if page_number%2 else "blank","images":len(placements),"text":has_text})
        if len(cover.pages)!=1:
            errors.append(f"cover PDF must contain exactly one full-wrap page; found {len(cover.pages)}")
        cover_page=cover.pages[0] if cover.pages else None
        cover_dims={}
        cover_fonts=False
        cover_cmyk=False
        if cover_page:
            from scripts.cover_calculator import calculate_cover_dimensions
            d=calculate_cover_dimensions(
                int(meta["interior"]["page_count"]),
                float(meta["trim"]["width_in"]),float(meta["trim"]["height_in"]),
                meta["interior"]["paper"],float(meta["trim"]["bleed_in"])
            )
            actual_cover=_page_size(cover_page)
            cover_dims={"width_in":actual_cover[0],"height_in":actual_cover[1],"spine_width_in":d["spine_width_in"]}
            if abs(actual_cover[0]-d["cover_width_in"])>0.001 or abs(actual_cover[1]-d["cover_height_in"])>0.001:
                errors.append(f"cover dimensions mismatch: found {actual_cover}, expected {(d['cover_width_in'],d['cover_height_in'])}")
            cover_fonts=_fonts_embedded(cover_page)
            cover_cmyk=_uses_cmyk_only(cover_page,cover)
            if not cover_cmyk:
                errors.append("cover must use CMYK color values rather than RGB")
            if not cover_fonts:
                errors.append("cover PDF does not contain an embedded TrueType font")
            if _has_transparency(cover_page):
                errors.append("cover PDF contains transparency")
            if cover_page.get("/Annots"):
                errors.append("cover PDF contains annotations")
        result["interior"]={
            "page_count":len(interior.pages),"illustration_pages":art_count,
            "blank_reverse_pages":blank_count,"minimum_effective_dpi":None if min_dpi==10_000 else round(min_dpi,2),
            "metadata_absent":interior_metadata_absent,
            "pages":page_results
        }
        result["cover"]={**cover_dims,"fonts_embedded":cover_fonts,"metadata_absent":cover_metadata_absent,"cmyk_colors":cover_cmyk}
    except Exception as exc:
        errors.append(f"PDF inspection failed: {type(exc).__name__}: {exc}")
    result["errors"]=errors
    result["status"]="PASS" if not errors else "FAIL"
    return result
