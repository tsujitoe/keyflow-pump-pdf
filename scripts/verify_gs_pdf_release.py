
#!/usr/bin/env python3
"""Fail closed when a GS-to-KEYFLOW PDF loses page content or corrupts graphics state.

This is a release gate, not an editor.  It deliberately detects the failure mode where
a PDF parser can extract text from a page that Acrobat/PDFium renders as blank.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pypdf import PdfReader

try:
    import pypdfium2 as pdfium
except ImportError as exc:  # pragma: no cover - bundled runtime supplies it
    raise SystemExit("pypdfium2 is required for visual release validation") from exc


OP_RE = re.compile(r"(?<!\S)(q|Q|BT|ET)(?!\S)")


def operator_balance(page) -> dict[str, int]:
    raw = page.get_contents().get_data().decode("latin1", "ignore")
    counts = {op: 0 for op in ("q", "Q", "BT", "ET")}
    for op in OP_RE.findall(raw):
        counts[op] += 1
    return counts


def ink_pixels(pdf_path: Path, page_index: int, scale: float = 1.5) -> tuple[int, int]:
    document = pdfium.PdfDocument(str(pdf_path))
    image = document[page_index].render(scale=scale).to_pil().convert("L")
    histogram = image.histogram()
    # 245 tolerates anti-aliased light grid lines while still detecting actual page content.
    ink = sum(histogram[:246])
    return ink, image.width * image.height


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="Text that must not remain in an extractable output stream; repeat as needed.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    if not args.source.is_file():
        errors.append(f"source does not exist: {args.source}")
    if not args.output.is_file() or args.output.stat().st_size == 0:
        errors.append(f"output does not exist or is empty: {args.output}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    source_reader = PdfReader(str(args.source))
    output_reader = PdfReader(str(args.output))
    if len(source_reader.pages) < 3:
        errors.append(f"source has {len(source_reader.pages)} pages; expected GS layout")
    if len(output_reader.pages) != 3:
        errors.append(f"output has {len(output_reader.pages)} pages; expected exactly 3")

    if len(output_reader.pages) >= 3 and len(source_reader.pages) >= 3:
        for page_index, minimum_ratio in ((0, 0.10), (1, 0.25), (2, 0.10)):
            source_ink, _ = ink_pixels(args.source, page_index)
            output_ink, total_pixels = ink_pixels(args.output, page_index)
            ratio = output_ink / max(source_ink, 1)
            if output_ink < total_pixels * 0.001:
                errors.append(f"page {page_index + 1} renders blank ({output_ink} ink pixels)")
            if ratio < minimum_ratio:
                errors.append(
                    f"page {page_index + 1} lost too much visible content "
                    f"({ratio:.3f} of source ink; minimum {minimum_ratio:.2f})"
                )

        # A whole-stream splice that removes unmatched q/Q graphics-state operators can
        # make every object after the underflow disappear in real renderers.
        p2_balance = operator_balance(output_reader.pages[1])
        if p2_balance["q"] != p2_balance["Q"]:
            errors.append(
                "page 2 graphics-state imbalance: "
                f"q={p2_balance['q']} Q={p2_balance['Q']}"
            )
        if p2_balance["BT"] != p2_balance["ET"]:
            errors.append(
                "page 2 text-object imbalance: "
                f"BT={p2_balance['BT']} ET={p2_balance['ET']}"
            )

    extracted = "\n".join(page.extract_text() or "" for page in output_reader.pages)
    for value in args.forbid:
        if value and value in extracted:
            errors.append(f"forbidden extracted text remains: {value!r}")

    if errors:
        print("RELEASE VALIDATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("Release structural and render validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

