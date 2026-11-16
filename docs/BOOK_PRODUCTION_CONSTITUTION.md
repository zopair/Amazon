# Mandatory Book Creation Constitution

This constitution is a release gate, not optional creative advice.

## Source-of-truth hierarchy

1. Current official KDP documentation controls platform specifications and policy.
2. \`config/production_policy.json\` controls machine-enforced production constraints.
3. \`config/book_meta.json\` controls the selected book's actual trim, page count, paper, line weight, and output paths.
4. Market observations can guide product packaging but can never override KDP requirements.
5. If any required fact is unknown, conflicting, or unsupported, stop and request human review. Never fill gaps by guessing.

## Copyright and originality

- Generic themes are allowed only when the actual artwork and presentation are original or properly licensed.
- Do not use copyrighted characters, brand names, logos, signature character likenesses, trademarked toy designs, or copied artwork.
- Do not scrape and republish images from search engines.
- Keep a source/license record for every externally sourced asset.

## Visual requirements

- Audience: ages 4–8.
- Pure white background, black contours, no gray, shading, gradients, shadows, halftones, or watermarks.
- Closed bold contours; 2.4 pt target line weight, never below KDP's 0.75 pt minimum.
- Large, open spaces, low clutter, and one clear subject or coherent group.
- 300 DPI minimum for raster art.
- No cropped limbs, cut-off subjects, accidental tangencies, or duplicate/near-duplicate pages.
- Odd pages contain the approved art. Even pages are completely blank.

## Book engineering requirements

- Trim: 8.5 × 11 in.
- Sample: 24 pages / 12 designs. Production target: 100 pages / 50 designs. Never exceed KDP's 590-page maximum for 8.5 × 11 in black-ink / white-paper paperbacks.
- Black ink on white paper.
- No interior bleed for this series profile.
- Inside margin: 0.375 in for the 24–150 page band; outside/top/bottom no less than 0.25 in. This project uses 0.375 in all around.
- Full wrap cover with 0.125 in bleed on top, bottom, and both outer edges; CMYK cover colors; embedded fonts; no document metadata.
- White-paper black-and-white spine formula: page count × 0.002252 in.
- No spine text by default; recalculate and use the official cover template whenever specifications change. Keep a 2 × 1.2 in clear barcode area at least 0.25 in from the spine and trim.
- Embed all cover fonts; flatten all artwork; no encryption, annotations, crop marks, or transparency.

## Metadata and publishing safety

- Cover title/subtitle/author/series must match KDP metadata exactly.
- Keywords and categories must accurately describe the book.
- Do not use another title, author, brand, or trademark as an unauthorized search term.
- Disclose AI-generated content when required by KDP. The publisher must answer based on the actual creation process.
- Do not select public-domain rights unless the material is genuinely public domain and the publisher has evidence.
- Never auto-publish. Owner approval is mandatory.

## Final verification

Every release must have:
- JSON validation report.
- PDF page-count and page-size checks.
- Blank-reverse-page checks.
- Effective image DPI checks.
- Embedded-font checks.
- Cover-size and spine calculation checks.
- Rights/metadata review.
- Visual sample approval.
- Official KDP Print Previewer review.

A passing script is not a promise of Amazon acceptance. Any unknown, ambiguous, or untested condition blocks publication.
