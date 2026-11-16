"""Remove PDF document-information metadata before KDP preflight."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter

def strip_pdf_metadata(pdf_path: str | Path) -> Path:
    path=Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    reader=PdfReader(str(path),strict=True)
    if reader.is_encrypted:
        raise ValueError("encrypted PDFs are not accepted by this production profile")
    writer=PdfWriter()
    writer.append_pages_from_reader(reader)
    # Remove both standard document-information metadata and XMP metadata streams.
    writer.metadata=None
    writer.xmp_metadata=None
    fd,temp_name=tempfile.mkstemp(prefix=".kdp-sanitized-",suffix=".pdf",dir=str(path.parent))
    os.close(fd)
    try:
        with open(temp_name,"wb") as stream:
            writer.write(stream)
        check=PdfReader(temp_name,strict=True)
        if check.metadata is not None or check.xmp_metadata is not None:
            raise ValueError("PDF metadata values or XMP metadata remain after sanitization")
        os.replace(temp_name,path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return path
