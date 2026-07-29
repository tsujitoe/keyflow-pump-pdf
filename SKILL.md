---
name: keyflow-pump-pdf
description: Modify EBARA GS-series pump specification PDFs into KEYFLOW AHe-series PDFs. Use when updating brand, headers, model numbers, performance data, ISO 9906 Grade 1U efficiency curves, motor data, materials, dimensions, or pages in this PDF family; compare a source PDF to a supplied target or create a verified modified PDF with true table-cell content replacement and preserved borders.
---

# KEYFLOW pump PDF modification

Use the general `pdf` skill for extraction, editing, rendering, and final visual verification. Treat the original PDF as the layout source; preserve formatting unless this skill specifies a change.

## Removal integrity

When a rule says to remove text, values, axes, or a page, delete it rather than merely paint a white overlay on the original PDF content.

1. Prefer native PDF redaction that removes the selected content from the page stream.
2. If safe structural redaction is unavailable, render the fully edited page at 300 DPI or higher and rebuild a new, static PDF from those rendered pages. Do not retain the source page content stream in the delivered PDF. This fallback is forbidden for a retained vector performance chart until all required curve, marker, operating-line, and native-text edits have first been completed in the original vector content.
3. Reopen the delivered PDF and confirm extracted text does not contain any removed source strings. Treat the static rebuilt PDF as the default when removal integrity matters; report that it is non-editable.
4. For a value inside a table cell, confine every deletion to the cell interior. Never cover, delete, or redraw the cell borders; delete the old value first, then add the replacement value.

## Non-negotiable table editing

Do not use page-overlay patches to change a table value. In particular, do not merge a white rectangle and replacement text over an original page as the delivered edit.

1. Identify the original text object and the exact enclosing cell borders from the source PDF before editing.
2. Prefer genuine content-stream editing or native redaction that deletes only the original glyphs; preserve every original horizontal and vertical border object.
3. Insert the replacement using the source cell's font family, size, weight, color, alignment, and baseline. Do not merely place a visually approximate label over existing text.
4. When native content editing is unsafe, rebuild the entire page as a 300-DPI-or-higher static page. In that rebuilt page, clear only the original glyph pixels inside the cell interior, then typeset the replacement. Do not place a rectangular patch over any table rule.
5. Do not repair a damaged table by drawing new lines. If any original border would be altered, revise the deletion bounds and rebuild the page before delivery.
6. Inspect every changed cell at 200% or higher. Require uninterrupted original borders on all four sides, no visible white patch edge, no duplicate/ghost text, and no shifted neighbouring text.

## Intake and decision

1. Inspect every page as extracted text and rendered images before editing.
2. Identify the original pump model, requested flow/head, performance curve, rated impeller, and whether the document follows the GS-series layout. Report any ambiguous or mismatched data before changing it.
3. Before any curve or material change, explicitly confirm:
   - whether to convert the performance curve to ISO 9906:2012 Grade 1U; and
   - the casing material.
4. Ask only for any remaining non-default data: performance-curve/source data or values needed to update the curve, and the rated-impeller shaft-power value if it cannot be read accurately from the curve.
5. Do not invent performance values. Preserve source dimensions, dimensional drawing, flange table, and total weight unless the user specifically provides replacements.

## Apply standard KEYFLOW conversion

Apply these changes on every applicable page:

- Replace EBARA branding with the supplied KEYFLOW / 士揚國際 logo and company name.
- Remove the customer-information block: Customer, Date, Company, Contact, Item no., Issued by, Phone, Project, Project ID, and E-mail.
- Remove the Construction page, including its drawing and parts table.
- Remove pump manufacturer and `with ISO base, motor` installation wording.
- Change both connection entries to `ANSI 150LB RF SF`.
- Set motor manufacturer to `TECO Standard`. For motor Type, delete the leading segment through the first underscore and preserve the remainder; for example, `280MB_90_3_380` becomes `90_3_380` and `200L_30_3_380` becomes `30_3_380`. Set specific design to `60Hz` and electric voltage to `460 V`. Delete only the values in the Frame size, Weight, and Electric current cells, while preserving every table border.
- Set material fields: Impeller `SCS13`; Shaft `SUS304`; O-ring `FKM`; Mechanical Seal `SiC & Carbon & FKM`. Set Casing only from the user-provided value.
- Keep the Dimensions page drawing, dimensions, flange table, and total weight unchanged, even when the connection standard changes.

### Current fixed overrides

- These fixed overrides take precedence over any conflicting generic conversion instruction above.
- Use `assets/siyueh-logo.jpg` for EBARA replacement on every retained page. Preserve its aspect ratio; never substitute a cropped sample, text recreation, or another KEYFLOW logo.
- Set the pump Manufacturer value to `SIYUEH`. Preserve the Installation type field and its source value.

## Model-number rule

Convert `GS <size>-<series> /<suffix>` to `AHe <size>-<converted series>`:

1. Replace `GS` with `AHe`.
2. Preserve `<size>`.
3. Round `<series>` to the nearest hundred using conventional half-up rounding, then divide by 10. For example: `200` to `20`, `220` to `20`, `250` to `30`.
4. Remove `/<suffix>` and surrounding extra spaces.

If a model does not match this pattern, ask the user for its target AHe name rather than deriving one.

### Current series override

Override step 3 above: divide the series by 10. Round only a non-zero original ones digit to the nearest ten using conventional half-up rounding before dividing; do not round tens or hundreds. Examples: `160` to `16`, `200` to `20`, `250` to `25`, and `165` to `17`.

## Performance page

### Vector capability gate and evidence

Before making any performance-page change, prove that the current input can be edited safely as a vector PDF. This is a delivery gate, not an optional diagnostic.

1. Decode the current page's content stream and uniquely identify, from that file alone:
   - each P2, hydraulic-efficiency, and NPSH clipping group;
   - the zero line for the P2 and efficiency panels;
   - the rated, maximum, and minimum impeller path/marker groups;
   - the two green operating-line/callout groups; and
   - every Head-panel efficiency text object and its source display precision.
2. Record an evidence manifest before mutation: page number, group identifiers or byte ranges, colours, original text anchors, source values, and intended values. A visual guess, page screenshot, reused coordinate, or raster colour selection is not evidence.
3. Inspect the active font resources and the original chart text operands before replacing any native text. Determine whether the source uses literal strings, UTF-16 strings, CID hex strings, a ToUnicode map, or another encoded glyph sequence. Record the encoding method and a current-file character-to-glyph mapping for every required replacement character.
4. When a text object uses a subset/CID font, never insert a Unicode `TextStringObject` or an unencoded literal string into its `Tj`/`TJ` operand. Replace only the original encoded glyph tokens, preserving the current font resource, glyph widths, kerning operands, fill colour, and anchor. Build the glyph-token mapping from the current PDF's own CMap, ToUnicode map, or existing glyph runs; do not reuse glyph codes from another PDF.
5. For CID chart text, edit the decoded raw page-content bytes directly and write back a new decoded content stream. Do not round-trip the relevant `Tj`/`TJ` operands through a PDF library's generic text-object serializer, because it may silently emit Unicode strings or alter the original glyph encoding.
6. Prefer equal-length native substitutions where the original glyph-run spacing can be preserved. For a different-length label, derive the replacement's native glyph sequence and calculate the required `TJ` spacing from the current font metrics. If the required glyph cannot be mapped from the current source, use a compatible embedded font in a new, isolated native text object only after proving it does not cover or duplicate the source object.
7. Stop and ask for an editable/vector or Adobe-print version only if the chart object cannot be uniquely identified or a valid native encoded replacement cannot be constructed and verified. Do not render the page and paint, erase, move, redraw, or recreate curves/labels as a substitute.
8. A static final PDF is permitted only after all vector mutations pass the verification checks below. It may flatten successful edits; it must never be the mechanism used to perform a curve, marker, green-callout, or chart-label edit.

### Known-compatible EBARA source profile

The original `Datasheet_GS_40-160_2P60Hz.pdf` is a supported vector source, not a reason by itself to request an Adobe Print file. When the input has SHA-256 `C8311DE112F28439879F28F014BE2F018A102F5CB0699753168B3BE36726E2F5`, 4 pages, and its page-2 decoded raw content stream contains each of these clip signatures exactly once:

- `q q 1068 -9711 16118 -3227 re` (P2)
- `q q 1068 -12938 16118 -3253 re` (hydraulic efficiency)
- `q q 1068 -16165 16118 -3253 re` (NPSH)

then proceed with the native-vector workflow. Use the current file's raw content stream to locate all paths, markers, text operands, and green operating groups relative to these unique boundaries. Do not reject this exact profile merely because a high-level PDF parser does not expose individually named curve objects or clipping groups.

For this exact profile, do not reimplement the P2/efficiency/NPSH conversion from scratch. First run the bundled, SHA-gated helper:

```powershell
& <bundled-python> <skill-folder>\scripts\transform_known_gs40_160_chart.py <source.pdf> <same-run-chart-stage.pdf>
```

It performs the known native chart operations: removes the max/min impeller path-and-marker groups, transforms the retained P2 and efficiency ordinates, moves the original green operating groups, and replaces the known source-native efficiency/P2 glyph runs. It deliberately stops before branding, table edits, and Δp-axis removal. Inspect its generated stage at 200% before applying those remaining operations. Treat a helper failure as a specific implementation error to diagnose, not a reason to request a different input PDF.

For the routine request of this exact source with Grade 1U and a supplied casing, use the complete SHA-gated adapter rather than manually combining partial edits:

```powershell
& <bundled-python> <skill-folder>\scripts\convert_known_gs40_160_1u.py <source.pdf> <output.pdf> --casing <FC250-or-confirmed-casing>
```

This adapter performs the native chart stage first, applies the approved three-page KEYFLOW layout, removes the Δp scale while retaining its vertical border, and rebuilds a fresh 300-DPI static PDF. Its final PDF contains no original content stream or hidden removable text. It is intentionally limited to the exact SHA above; use the general native workflow for every other source. Render all three pages and run the release checklist before delivery.

For a byte-different source, do not assume compatibility from the filename. First try the same raw-stream signature discovery with unique current-file matches; only request a different source after that discovery and the CID glyph-mapping procedure both fail.

### Compatibility escalation (avoid unnecessary source-file requests)

Treat the known-compatible profile as an affirmative support decision. Its matching SHA-256 and panel signatures override a provisional failure from a high-level parser: do not say that its P2, efficiency, or NPSH curves are unavailable merely because they are not exposed as named PDF objects.

For that profile, complete these recovery steps before considering a refusal:

1. Extract the decoded page-2 bytes with `page.get_contents().get_data()` and search the three clip signatures.
2. Slice the P2, efficiency, and NPSH groups at those current-file boundaries; inspect the local path, colour, text, and `TJ`/`Td` operands directly.
3. Derive the current CID glyph map from its existing chart glyph runs and mutate encoded operands in the decoded bytes; never use `ord()` as a substitute for a CID glyph map.
4. Render the native-mutated draft and compare it against the source at 200%; correct the local object map or transformation before escalating.

Do not ask for an Adobe Print PDF as a routine fallback. Adobe Print files can consolidate or flatten precisely the native chart groups required here. Request another source only after the four steps above fail, and include the measured diagnostic: source SHA-256, each clip-signature count, failing group/operand, and why the current-file CID mapping cannot encode the required replacement. A generic statement that the curves are “not safely editable” is insufficient for a known-compatible source.

1. Use the performance-curve data as the authority for the designed/rated impeller diameter when it conflicts with another table.
2. Edit these curves as native PDF vectors. Decode the performance-page content stream, derive each plot panel's clipping group and zero line from this file, and alter only drawing objects in that group. Do not raster-move curves, erase curve pixels, or cover a chart with a white patch. If the PDF is not a usable vector PDF, ask for a vector/Adobe-print version rather than approximating the curves.
3. First remove the maximum- and minimum-impeller traces and their data markers from the `Shaft power P2`, `Hydraulic efficiency`, and `NPSH-values` panel groups. Select their stroke/fill colour commands and complete path/marker objects; retain only the rated-impeller trace, its data markers, and its operating point. Do not change the Head plot or its legend unless separately requested.
4. If Grade 1U is confirmed, update the retained rated-impeller data before performing the standard KEYFLOW conversion:
   - multiply every displayed hydraulic-efficiency value, contour label, operating efficiency, and retained hydraulic-efficiency curve ordinate by `0.93`;
   - divide every retained P2 curve ordinate and operating P2 value by `0.93`;
   - transform vector Y coordinates about each panel zero line: efficiency `y' = zero + 0.93 * (y - zero)` and P2 `y' = zero + (y - zero) / 0.93`; include retained curve paths, square markers, green operating lines, arrows, and green callout anchors; and
   - leave Head and NPSH values unchanged, apart from the removal of maximum/minimum impeller traces in step 2.
   Keep each label's existing display precision unless the user specifies otherwise. For example, `79.16%` becomes `73.62%`, `78.1%` becomes `72.6%`, and `17.2 kW` becomes `18.5 kW`.
   For the P2 and Hydraulic efficiency left green callouts, edit the original vector text/fill colour and move its native anchor with the green operating line. Preserve the original green frame, arrows, colour, and line weight; never cover it in white and add black replacement text.
5. Preserve all grid, axes, labels outside the target objects, and chart borders byte-for-byte where possible. Never reuse panel coordinates from a different datasheet.
6. Update the curve, labels, operating point, shaft-power plot, efficiency plot, NPSH plot, and related tabular values together. Do not alter only headline values while leaving the visual plots stale.
   Preserve the original upper-right Head-chart legend for maximum, minimum, and rated impeller diameters. Do not cover it, delete it, or add a duplicate rated-impeller label beside it.
5. Rename `Max. Shaft Power at max. impeller` to `Max. Shaft Power`.
   Delete the old value glyphs inside the cell before typesetting the new value; never use a white rectangle that intersects a table rule.
6. Delete the original row value without touching its table borders, then set the value to the power at the requested flow/head operating point on the **rated-impeller** shaft-power curve. If it cannot be identified reliably, ask the user for the value.
7. Remove the `Test standard: ISO 9906:2012 - Grade3B` text after any confirmed Grade 1U conversion.
8. Remove only the `Δp / kPa` label, its scale values, and the tick marks or horizontal lines that extend rightward beyond the retained chart/table boundary. Exclude every vertical line that belongs to the remaining chart or table structure from the deletion selection, including its right-hand border and internal vertical segments. Do not delete, mask, or redraw those original vertical lines. Remove adjacent values only when they belong to the Δp scale; retain normal chart legend and table values. Do not leave rightward line stubs or partial Δp cells.

## Verify and deliver

### Portable, repeatable execution contract

Apply these rules in every computer and every session:

- Resolve all skill files relative to this skill folder. Use only `assets/siyueh-logo.jpg`; never depend on a Desktop, Downloads, workspace `work/` folder, prior conversation image, installed font, cached PDF, or absolute local path.
- Treat the input PDF, confirmed Grade choice, and casing value as the complete job input. Re-extract the source text, page geometry, colour commands, chart clipping groups, font metrics, and native text anchors from that input on every run.
- Never reuse page coordinates, vector-stream markers, label lists, text baselines, or output filenames from an earlier pump model. Derive them from the current source, and stop for user direction if a required object cannot be uniquely identified.
- Keep all modifications native-vector until final flattening. Flatten only after verification, at 300 DPI or above, and create a fresh output filename. The flattened PDF must contain no source-page content stream or editable deleted text.
- Use source display precision for every transformed label. Calculate Grade 1U values from unrounded source numbers first, then round once for display.
- Record a run manifest in the delivery note: source filename, model conversion, Grade choice, casing, rated impeller, source and converted P2/efficiency callout values, output page count, vector-capability result, chart-group evidence, and source-to-output Head-panel label mapping.
- For every native text replacement, record the source font resource, source operand encoding, glyph-token mapping source, and a rendered verification that no replacement character becomes a box, blank, fallback glyph, or changed-colour text.
- Reject delivery if any required removal, brand asset, curve group, label mapping, green callout, table border, or output-text check fails. Do not silently approximate or use an overlay fallback.

### Mandatory implementation gate

- Do not use PIL/ImageDraw, screenshots, `pdftoppm`, ReportLab overlays, fixed pixel boxes, or hard-coded coordinates to modify a source datasheet. Those tools are allowed only to render the *already edited* PDF for inspection and to rebuild the final static PDF after native edits are complete.
- The only approved exception is `scripts/convert_known_gs40_160_1u.py` for its exact SHA-identified source. It performs the native chart mutations before using a source-specific 300-DPI static rebuild; do not copy its fixed geometry, overlays, or raster-finalization pattern to another source.
- Do not infer a page layout from a previous GS 40-160 file. In particular, do not hard-code page-1 table cells, page-2 callout rectangles, efficiency-label lists, logo rectangles, or any `x/y` coordinates from an earlier run.
- For a compatible vector GS datasheet, modify the current page's content stream: remove source glyph/path objects, update native glyph codes and `Td`/`Tm` anchors, update vector curve paths and markers, then render for inspection. Preserve all unrelated source stream objects.
- Update the original P2 and efficiency callout text objects in-place. Never clear their green boxes, recreate their borders, add a new pointer, or place replacement text on a rendered image.
- Build a per-run object map before editing: every source efficiency label and callout value, its colour, font, stream location, and intended Grade 1U value. Use this map both for mutation and for verification. Do not use a manually typed list from another pump.
- If an implementation cannot complete these native edits, report the source as unsupported and request a compatible vector PDF. Do not produce a “best effort” raster PDF.

### Known-profile toolchain and output-proof gate

For the known-compatible GS 40-160 source profile, use the bundled Python runtime with `pypdf` to edit decoded content streams and to write the output. Do not use PyMuPDF/`fitz` `search_for`, `add_redact_annot`, `apply_redactions`, `insert_text`, or `insert_textbox` as the editing path for this profile. Those APIs operate on search rectangles and replacement fonts, not the required current-file CID operands and chart paths; they are not a substitute for the native-vector workflow.

Treat a failed write, an unchanged output, or an unexpected page count as a local toolchain failure, not as evidence that the EBARA source needs Acrobat or a new design file. Diagnose and correct it with the bundled `pypdf` workflow before considering source escalation.

Before rendering or visually reviewing any candidate, reopen the exact output pathname that was written and record all of the following:

1. File exists, size is non-zero, and its SHA-256 differs from the input.
2. `PdfReader(output)` opens successfully and reports exactly 3 pages.
3. The Construction-page text is absent from the output, and pages 1–3 are the Technical Data, Performance Curve, and Dimensions pages respectively.
4. The decoded output page-2 stream differs from the source page-2 stream in the recorded chart groups; do not accept a file whose curve page is byte-identical to the source.

Do not claim that an output “still has four pages” without this direct readback of the exact emitted file. Do not delete failed diagnostic or candidate files automatically; keep them outside the delivery folder or label them clearly as failed so the cause can be inspected. A local output/write failure must be reported as such and worked around, not converted into a request for a different user PDF.

Never use a previous candidate/output PDF as the input to a second “finalize” or “compatibility” pass unless it has already passed every release check. The sole exception is the same-run, SHA-gated chart-stage file written by `scripts/transform_known_gs40_160_chart.py`; record its input/output hashes and continue only after its chart-specific inspection passes. Always derive every other deliverable from the original user-supplied vector PDF and the current-run object manifest. A partial candidate may already contain stale right-axis objects, wrong curve colours, missing glyphs, or incorrect state transitions; a second pass cannot make it a valid source of truth.

For any CID font in this profile, a function such as `glyph(ch) = <{ord(ch):04X}>` is forbidden. A Unicode code point is not the PDF font's CID. Use only the source file's proven character-to-CID map and preserve the original `TJ` kerning. Before any flattening, render and visually confirm on every retained page that all occurrences of `AHe 40-16` and `SIYUEH` contain no square, replacement, blank, or fallback glyph.

### Whole-page change-control verification

1. Render both source and edited pages at the same resolution, align them using page geometry, and compare them page-by-page. Inspect every detected difference at 200% or higher.
2. Permit differences only inside the explicitly required text, curve, marker, callout, logo, customer-block, or removed-page regions. Any difference to an untouched table rule, grid, axis, dimension drawing, flange table, footer rule, or source logo-clear area is a rejection until explained and corrected.
3. For every changed table cell, retain proof that its four source borders remain present and continuous. For every logo replacement, retain proof that no EBARA pixels or text remain in its source region and that the replacement has margins to nearby rules.
4. Reject the result if any white patch edge, duplicate/ghost glyph, duplicate diamond, stale chart label, stale max/min trace, raster speckling, or unexplained full-page difference remains. Text extraction passing by itself is never sufficient evidence of a correct visual result.

### Cross-reader compatibility gate

Do not release a vector-mutated PDF solely because it renders correctly in one viewer. Before delivery, open the exact emitted file in Adobe Acrobat (or Acrobat's rendering engine when available) and compare the Performance Curve page against the verification render at 200%. Check clipping, curve paths, markers, callout frames, grid lines, and all text anchors. If Acrobat and the verification render disagree, reject the vector draft as non-portable. Diagnose the graphics-state or content-stream defect; do not describe the draft as complete.

Never flatten a vector draft in order to conceal, bypass, or defer a failed chart, font, text, or colour verification. In particular, a rated P2 or efficiency curve that has turned green, a right-side Δp scale that remains visible, or a missing CID glyph is a source-draft defect that must be repaired before flattening.

When all required native-vector edits have passed the vector and Acrobat checks but reader-to-reader rendering remains inconsistent, rebuild the final deliverable from 300-DPI-or-higher renders of the verified native draft. Reopen the flattened file in Acrobat and confirm every page matches the verification render. State in the delivery note that the released PDF is flattened, non-editable, and cross-reader verified.

### Latest fixed rendering rules

- Size `assets/siyueh-logo.jpg` inside the original footer clear area with a margin to every table and footer rule; reduce it rather than letting it overlap a rule or table.
- In the Max. Shaft Power row, delete only the old numeric glyph bounds. Preserve the existing `kW` unit and all cell rules.
- For P2 and Hydraulic efficiency, preserve the green frame, text, arrow, and horizontal operating line. Align each arrow centre exactly to the corresponding green horizontal line; do not substitute an unframed or black value.
- Match the source callout geometry exactly: a thin green rectangular frame with a compact filled green diamond pointer on its right edge, not a triangular pointer or a resized/rounded replacement.
- When the source diamond pointer remains after value replacement, retain that single original diamond and do not draw another one.
- Limit clearing behind a green callout to the exact original green-frame bounds. Do not leave a white rectangle above, below, or beside the callout.

### Grade 1U completeness and callout integrity

- For Grade 1U, update every visible hydraulic-efficiency label in the Head panel, including black efficiency contours, coloured impeller-curve efficiency labels, the `Eff.` operating annotation, and the left green operating callout. Multiply every value by `0.93` while retaining its source precision, colour, and native anchor. Do not leave a source efficiency percentage visible after the corresponding curve has been transformed.
- Do not create a new green callout, frame, pointer, diamond, or horizontal line. Locate the existing vector text object inside each original P2/efficiency green callout and replace only its glyph content, colour-preserving and at the same anchor. Keep the original frame and its single original diamond untouched.
- Before delivery, compare the source and output Head panels label-by-label. Require each source efficiency label to map to one Grade 1U value, and inspect the two left green callouts at 200% to confirm no duplicate/covered frame, diamond, or text is present.

### Release blockers learned from the compatible GS 40-160 profile

For the known-compatible `Datasheet_GS_40-160_2P60Hz.pdf`, run this visual release checklist after producing the final file. It is a hard blocker; do not describe a PDF as complete while any item is false.

- All three retained pages have an empty customer/header block: no date, ID, or other residual customer value. All three footer regions use `assets/siyueh-logo.jpg`; no EBARA wordmark or logo remains.
- Every visible pump-name occurrence reads `AHe 40-16` with no fallback square, blank glyph, or mixed `GS` text. The Manufacturer reads exactly `SIYUEH`; do not accept `SI□UEH` or any other font-substitution artefact.
- Both Connection values are exactly `ANSI 150LB RF SF`, with no leading `EN` or source residue. Preserve `Installation type` and `with ISO base, motor`. Set `Specific design` to exactly `60Hz`; leave only the values of Frame size, Weight, and Electric current blank.
- The material row reads the requested casing (for this test, `FC250`), `SCS13`, `SUS304`, `FKM`, and `SiC & Carbon & FKM`, including the required spaces. The page-1 Max. Shaft Power row retains its `kW` unit and has the rated-impeller curve value (for this profile/1U, `12.28`); the page-1 efficiency is `68.6`.
- Page 2 has no `Δp / kPa` label, right-side scale numbers, ticks, or protruding horizontal fragments, while its original right vertical boundary remains. It retains only the rated trace and markers in P2, Hydraulic efficiency, and NPSH; no maximum/minimum trace, marker, or recoloured residual line is permitted. Preserve the source rated-trace stroke/fill colours; green is reserved for the original operating lines and callouts, never a replacement curve colour.
- Page 2 P2 and Hydraulic efficiency callouts read `12.28` and `68.59` respectively for this profile/1U. They remain the original single green-frame/single-diamond objects, and the transformed rated curves, markers, and green operating lines meet those values. Head-panel legend and its three impeller diameters remain present and unaltered.

Render the final PDF at 200% and check this list visually, even if the delivered file was flattened and text extraction is unavailable. A failed glyph, leftover header/footer, incomplete motor cell, residual outer trace, or right-side Δp element requires correction, not a delivery note.

For this profile, explicitly inspect the page-2 right edge after rendering: none of the former Δp scale values (`720`, `680`, `640`, `600`, `560`, `520`, `480`, `440`, `400`, `360`, `320`, `280`, `240`, `200`, `160`, `120`, `80`, `40`, `0`) may remain on the right of the retained vertical boundary. Also compare P2 and Hydraulic efficiency strokes with the source rated-trace blue at three separated points; any green stroke outside the original operating line/callout objects is a rejection.

1. Render every output page and compare it visually with the source layout and requested changes.
2. Verify model naming, brand replacement, removal of the customer block and Construction page, material defaults, confirmed casing, connections, motor values, and all performance values.
3. Check that the retained impeller on the performance page agrees with the curve legend. Confirm that the maximum/minimum impeller traces and markers are absent from P2, efficiency, and NPSH plots.
4. When Grade 1U was selected, verify P2 is the pre-conversion value divided by `0.93`, hydraulic efficiency is the pre-conversion value multiplied by `0.93`, and the curves, markers, green operating lines, and green callouts agree at the rated operating point. At 200% inspection, require continuous vector curves with no raster speckling, ghost path, duplicate trace, or white deletion patch.
5. Confirm the Test standard text is absent; the right side has no Δp label, scale values, ticks, or rightward protruding line fragments; original chart/table vertical lines were not altered; the Frame size, Weight, and Electric current values are blank; and every changed cell passes the non-negotiable table-editing inspection. Do not deliver if a patch edge, duplicate text, or broken/rewritten table border is visible.
6. Confirm extracted text from the delivered PDF does not contain removed customer fields, EBARA branding, Construction content, deleted values, the Test standard string, or `Δp / kPa`.
7. Flag, rather than silently correct, source-data conflicts that are not covered by these rules.
8. Deliver the edited PDF and a short list of values applied, including the Grade 1U choice and the casing value supplied by the user.
9. Include the run manifest and state explicitly whether the delivered PDF is a native-vector PDF or a post-verification flattened PDF.
