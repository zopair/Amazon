"""Build and validate the configured KDP sample."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from scripts.art_generator import generate_artwork
from scripts.interior_builder import build_interior
from scripts.cover_builder import build_cover
from scripts.validator import validate_book

def run(config_path: Path, output_dir: Path):
    meta=json.loads(config_path.read_text(encoding="utf-8"))
    images=generate_artwork(meta["content"]["theme"], meta["interior"]["page_count"]//2, output_dir.parent/"images", meta["interior"]["min_dpi"], meta["interior"]["line_width_pt"])
    interior=output_dir/"interior.pdf"
    cover=output_dir/"cover.pdf"
    build_interior(meta,images,interior)
    build_cover(meta,cover)
    report=validate_book(interior,cover,meta)
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/"validation-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="config/book_meta.json")
    parser.add_argument("--output-dir",default="build/output")
    args=parser.parse_args()
    try:
        report=run(Path(args.config),Path(args.output_dir))
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}",file=sys.stderr)
        return 1
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
