# Open-source dependency and security review

Checked: 2026-11-16. Versions are pinned to avoid unreviewed drift. Recheck GitHub advisories before changing pins.

| Package | Pinned version | Upstream source | License | Review result |
|---|---:|---|---|---|
| Pillow | 12.3.0 | https://github.com/python-pillow/Pillow | MIT-CMU | Selected because 12.3.0 includes fixes for multiple 2026 security issues affecting earlier 12.x releases. |
| ReportLab | 5.0.1 | https://github.com/MrBitBucket/reportlab-mirror | BSD | Selected above the 4.4.10 security-fix release; 5.0.1 is the current upstream release observed in the source mirror. |
| pypdf | 7.1.0 | https://github.com/py-pdf/pypdf | BSD-3-Clause | Selected after rejecting 5.9.0: the 6.21.x and 7.0.x releases contain multiple security/resource-exhaustion fixes; 7.1.0 is the latest signed release observed on 2026-11-16. |
| actionlint | 1.7.12 | https://github.com/rhysd/actionlint | MIT | Pinned Docker image used only to statically validate GitHub Actions workflow files. |

## Explicitly rejected versions

- **pypdf 5.9.0** was initially pinned, then rejected before merge because GitHub advisories published in October and November 2026 document resource-exhaustion and parser issues fixed in later 6.21.x and 7.x releases.
- **ReportLab 4.4.9** was initially pinned, then rejected before merge because upstream changelog identifies a security fix in 4.4.10.
- **Pillow below 12.3.0** was rejected because several 2026 advisories identify affected versions below 12.3.0.

## Scope and limits

- The packages are used only for local deterministic image generation, PDF creation, and structural inspection.
- The pipeline does not parse user-supplied PDFs or arbitrary image formats; it creates its own PNGs and reads its own generated PDFs.
- Dependency pins and upstream license sources are recorded, but this is not a full SBOM, malware scan, or continuous vulnerability monitoring service.
- The GitHub Actions test workflow installs only these three pinned runtime packages. No paid API or Telegram dependency is used.
- Before any future dependency upgrade, inspect the upstream GitHub release notes, LICENSE, security advisories, supported Python versions, and transitive dependencies; then run the full test suite.

## Upstream references

- Pillow project and license: https://github.com/python-pillow/Pillow and https://github.com/python-pillow/Pillow/blob/main/docs/about.rst
- ReportLab licensing: https://docs.reportlab.com/developerfaqs/
- ReportLab change history: https://github.com/MrBitBucket/reportlab-mirror/blob/master/CHANGES.md
- pypdf license: https://github.com/py-pdf/pypdf/blob/main/LICENSE
- pypdf releases: https://github.com/py-pdf/pypdf/releases
- pypdf security advisories: https://github.com/py-pdf/pypdf/security/advisories
- actionlint releases and license: https://github.com/rhysd/actionlint/releases and https://github.com/rhysd/actionlint/blob/main/LICENSE.txt

## Fonts

- assets/fonts/DejaVuSans-Bold.ttf - DejaVu Sans Bold (Bitstream Vera license, permissive free license; embedding in produced PDFs/books is allowed). Used for the colorable name labels in generated interior artwork. Source: standard DejaVu distribution (dejavu-fonts.github.io).
