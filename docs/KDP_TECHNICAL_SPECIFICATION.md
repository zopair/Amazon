# KDP Technical Specification and Release Constitution

Checked: 2026-11-16. This document separates binding KDP rules from market observations and internal design choices. It is not a promise of KDP acceptance or sales performance.

## 1. Product scope

The first product family contains original, generic coloring subjects for children ages 4–8:
- Fruits
- Flowers
- General toys
- Birds
- Animals
- Children's professions

No licensed characters, franchise names, logos, branded toy silhouettes, copied illustrations, celebrity likenesses, or trademark bait may be used. A subject being generic does not make a particular illustration, character design, photograph, or brand asset free to copy.

## 2. Locked sample and standard production profiles

| Attribute | Review sample | Standard production target |
|---|---:|---:|
| Trim size | 8.5 × 11 in | 8.5 × 11 in |
| Interior | Black ink, white paper | Black ink, white paper |
| Page count | 24 | 100 |
| Unique coloring designs | 12 | 50 |
| Design placement | Odd/recto pages | Odd/recto pages |
| Reverse side | Completely blank | Completely blank |
| Raster target | 300 DPI minimum | 300 DPI minimum |
| Outline target | 2.4 pt | 2.4 pt |
| Interior bleed | No bleed | No bleed |
| Cover bleed | 0.125 in each outside edge | 0.125 in each outside edge |
| Cover finish | Matte design recommendation | Matte design recommendation |
| Spine text | Omitted | Omitted unless the approved template and spine width safely allow it |

The 24-page sample is the KDP minimum and is intended for visual approval, not for sale as a finished series volume. The 100-page / 50-design production target is a market-informed packaging choice, not an Amazon requirement.

## 3. Official KDP print requirements used by the validator

1. **Page-count range:** the 8.5 × 11 in black-ink / white-paper paperback option allows 24–590 pages. KDP calculates the final count from the submitted manuscript and rounds up to an even number where necessary.
2. **Single-page PDF:** upload individual pages, not two-page spreads.
3. **Trim and bleed:** 8.5 × 11 in is the selected trim. This sample uses no interior bleed. If a future interior design reaches the edge, it must be rebuilt using KDP's bleed dimensions rather than reusing this no-bleed template.
4. **Margins:** for 24–150 pages, the minimum inside/gutter margin is 0.375 in. For no-bleed pages, outside margins must be at least 0.25 in. This project deliberately uses 0.375 in on all four sides.
5. **Image resolution:** at least 300 DPI. KDP recommends not exceeding 600 DPI for normal print files because very large files may delay processing.
6. **Line width:** KDP's minimum for lines in graphics is 0.75 pt (0.01 in / 0.3 mm). The project target is 2.4 pt to produce bold outlines suitable for young children; this is an internal design choice, not an Amazon minimum.
7. **Fonts and metadata:** embed all fonts. The cover generator uses embedded TrueType fonts. The interior is image-only and contains no text. Remove PDF document metadata, annotations, comments, invisible objects, crop/trim marks, and placeholder text before upload.
8. **Cover geometry and color:** one continuous PDF containing back cover, spine, and front cover. Add 0.125 in bleed to the top, bottom, and both outer edges. Use CMYK cover artwork, flatten layers/transparency, and keep important text at least 0.125 in inside trim lines (this project uses a more conservative 0.25 in safe zone). Cover text must be at least 7 pt.
9. **White-paper black-and-white spine:** page count × 0.002252 in. Other paper/ink combinations use different coefficients and must not reuse this value.
10. **Spine text:** KDP only prints spine text on books with more than 79 pages. This project defaults to no spine text because the narrow spine and fold tolerance can make it unreadable.
11. **File hygiene:** do not encrypt or lock PDFs. Do not include crop/trim marks, comments, annotations, invisible objects, placeholder text, or document metadata. Embed images and flatten transparency/layers.
12. **Barcode:** KDP can place a barcode automatically if the publisher does not provide one. The suggested barcode area is 2 × 1.2 in (minimum 1.4 × 0.8 in), positioned at least 0.25 in from the spine and trim. The sample reserves a 2 × 1.2 in white region on the lower back cover.

### Cover formulas

For trim width \(W\), trim height \(H\), spine \(S\), and outside bleed \(B=0.125\) in:

- Full cover width = \(2W + S + 2B\)
- Full cover height = \(H + 2B\)
- White-paper black-and-white spine = page count × \(0.002252\) in

For the 24-page sample:
- Spine = 24 × 0.002252 = 0.054048 in
- Full cover = 17.304048 × 11.25 in

For the 100-page standard target:
- Spine = 100 × 0.002252 = 0.2252 in
- Full cover = 17.4752 × 11.25 in

Always re-run the cover calculator after any page-count, paper, trim, or ink change. The KDP cover calculator/template is the final authority for the actual upload dimensions.

## 4. Market observations — not policy

A third-party snapshot of Amazon.com coloring-book listings dated November 6, 2026 reported that 8.5 × 11 in was common in the children's coloring-book sample and that many independently published children's titles clustered around 100–110 pages. Separate retail listings commonly describe 50 designs across about 100 pages, with single-sided printing and 8.5 × 11 in pages.

These are listing-level observations, not verified unit-sales data, not a controlled bestseller study, and not a guarantee that copying the format will sell. They support testing a 100-page / 50-design standard volume while keeping the first proof at 24 pages.

The 2.4 pt outline target, generous white space, one dominant subject per page, and matte cover are internal art-direction choices. They are not claimed as universal bestseller requirements.

## 5. Mandatory creation constitution

Before creating or accepting any page:
- Identify the exact subject and age suitability.
- Use original artwork or retain proof of commercial rights.
- Exclude copyrighted characters, branded toys, logos, trademarked names, and close imitations.
- Use black outlines on pure white; no gray fill, shading, gradients, halftones, shadows, or watermarks.
- Use closed contours, bold lines, large open coloring regions, and simple age-appropriate shapes.
- Avoid tiny details, confusing overlaps, cropped subjects, and accidental tangencies.
- Keep one coherent dominant subject per page.
- Reject duplicate or near-duplicate pages within a volume and avoid excessively reused/recycled content within or across books; KDP's Content Guidelines treat this as a poor-customer-experience issue. The built-in generator is limited to 12 distinct review motifs per theme. A 100-page / 50-design volume must supply 50 approved, distinct original assets; the pipeline refuses to pad the volume with repeated motifs.
- Keep every even-numbered reverse page completely blank: no art, text, folio, watermark, pattern, logo, or hidden objects.
- Do not invent factual or educational claims. Verify any factual label from a suitable authoritative source.
- Keep title, subtitle, series, author, cover, and KDP metadata consistent.
- Do not add keywords or categories unrelated to the actual book.
- Never claim that a book is a bestseller, officially approved, or guaranteed to pass review.

## 6. Anti-hallucination and evidence gate

The production system must treat this constitution and the JSON configuration as the source of truth:
- Never invent a KDP measurement, policy, rights status, license, page count, or validation result.
- For changing KDP requirements, consult the official KDP source URLs below and record the checked date.
- Label every rule as **Official KDP requirement**, **Observed market pattern**, or **Internal design choice**.
- If official sources conflict or a required value is missing, stop the release and create a human-intervention request.
- A green automated preflight means only that the checks implemented in this repository passed. It is not Amazon approval.
- The owner must inspect the sample visually and run the official KDP Print Previewer before any book is submitted.

## 7. AI content disclosure

KDP requires publishers to disclose AI-generated text, images, or translations when publishing or republishing. AI-assisted editing, refinement, error checking, or brainstorming alone does not require the same disclosure. The publisher is responsible for determining the correct answer from the actual content-creation process. The pipeline deliberately records this as a human decision and does not guess.

## 8. Release gates

A production book cannot be marked ready for publication until:
1. All configuration and automated PDF checks pass.
2. Every image and license/rights record has been reviewed.
3. The sample's artwork and cover have been visually approved by the owner.
4. The full manuscript and cover pass the official KDP Print Previewer.
5. Metadata, age range, categories, keywords, AI disclosure, and publishing rights have been reviewed.
6. The owner explicitly approves publication.

## 9. Official source register

- Paperback Submission Guidelines: https://kdp.amazon.com/en_US/help/topic/G201857950
- Create a Paperback Cover: https://kdp.amazon.com/en_US/help/topic/G201953020
- Set Trim Size, Bleed, and Margins: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
- Save Your Manuscript File: https://kdp.amazon.com/en_US/help/topic/G202145060
- Content Guidelines (including IP, reused-content, and AI-generated disclosure rules): https://kdp.amazon.com/en_US/help/topic/G200635600
- Metadata Guidelines: https://kdp.amazon.com/en_US/help/topic/G201097560
- Publishing Public Domain Content: https://kdp.amazon.com/en_US/help/topic/G200743940
- Keywords: https://kdp.amazon.com/en_US/help/topic/G201743260
- Barcodes: https://kdp.amazon.com/en_US/help/topic/G5HDYGP4BXLX4RUW

## 10. Market evidence register

- Coloring-book bestseller snapshot and sample methodology (third-party): https://crayonforge.com/blog/best-selling-coloring-books-on-amazon
- Listing-level example showing 50 designs, 100 pages, 8.5 × 11 in, and single-sided layout: https://business.walmart.com/ip/OWL-Coloring-Book-Coloring-For-Kids-Ages-4-8-years-100-page-50-designs-size-8-5x11-Paperback-9798700479165/515777692

The market sources are illustrative only. They do not replace Amazon's official print/content rules or a current product-by-product review.
