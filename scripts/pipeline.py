"""Build, validate, and package a KDP sample with a reproducible manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps
from scripts.artwork_loader import load_artwork
from scripts.interior_builder import build_interior
from scripts.cover_builder import build_cover
from scripts.validator import validate_book
from scripts.pdf_sanitizer import strip_pdf_metadata

def _sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def _make_preview(images: list[Path], output: Path) -> None:
    thumb_w,thumb_h=300,388
    columns=4
    rows=(len(images)+columns-1)//columns
    sheet=Image.new("RGB",(columns*thumb_w,rows*thumb_h),(238,238,238))
    for index,path in enumerate(images):
        with Image.open(path) as source:
            thumb=ImageOps.contain(source.convert("RGB"),(thumb_w-20,thumb_h-20))
        x=(index%columns)*thumb_w+(thumb_w-thumb.width)//2
        y=(index//columns)*thumb_h+(thumb_h-thumb.height)//2
        sheet.paste(thumb,(x,y))
    output.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(output,format="PNG",optimize=True)

def run(config_path: Path, output_dir: Path) -> dict:
    meta=json.loads(config_path.read_text(encoding="utf-8"))
    count=int(meta["interior"]["page_count"])//2
    images=load_artwork(
        meta["content"]["theme"],count,
        meta["content"].get("image_directory","assets/images"),
        meta["content"].get("generated_image_directory","build/images"),
        int(meta["interior"]["min_dpi"]),float(meta["interior"]["line_width_pt"])
    )
    interior=output_dir/"interior.pdf"
    cover=output_dir/"cover.pdf"
    preview=output_dir/"sample-preview.png"
    report_path=output_dir/"validation-report.json"
    manifest_path=output_dir/"manifest.json"
    output_dir.mkdir(parents=True,exist_ok=True)
    build_interior(meta,images,interior)
    build_cover(meta,cover)
    strip_pdf_metadata(interior)
    strip_pdf_metadata(cover)
    report=validate_book(interior,cover,meta)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    _make_preview(images,preview)
    manifest={
        "schema_version":1,
        "created_at":datetime.now(timezone.utc).isoformat(),
        "book_id":meta["book_id"],
        "title":meta["title"],
        "page_count":int(meta["interior"]["page_count"]),
        "illustration_count":count,
        "trim_in":[float(meta["trim"]["width_in"]),float(meta["trim"]["height_in"])],
        "paper":meta["interior"]["paper"],
        "ink":meta["interior"]["ink"],
        "line_width_pt":float(meta["interior"]["line_width_pt"]),
        "artwork_dpi":int(meta["interior"]["min_dpi"]),
        "ai_generated_content_assessment":"Publisher must answer KDP's disclosure question from the actual content creation process; this manifest does not infer the answer.",
        "validation_status":report["status"],
        "files":{
            p.name:{"sha256":_sha256(p),"bytes":p.stat().st_size}
            for p in (interior,cover,preview,report_path)
        },
        "source_artwork":[{"name":p.name,"sha256":_sha256(p)} for p in images]
    }
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"report":report,"manifest":manifest,"output_dir":str(output_dir)}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",default="config/book_meta.json")
    parser.add_argument("--output-dir",default="build/output")
    args=parser.parse_args()
    try:
        result=run(Path(args.config),Path(args.output_dir))
    except Exception as exc:
        print(json.dumps({"status":"ERROR","error_type":type(exc).__name__,"error":str(exc)},indent=2),file=sys.stderr)
        return 1
    report=result["report"]
    print(json.dumps({
        "status":report["status"],
        "output_dir":result["output_dir"],
        "errors":report["errors"],
        "manifest":result["manifest"]
    },indent=2,ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
