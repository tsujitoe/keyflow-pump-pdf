"""Create the approved static KEYFLOW output for the exact GS 40-160 profile.

This is a deliberately narrow adapter for the SHA-identified EBARA source. It
first performs the native vector chart mutation, then renders the complete
edited result at 300 DPI into a fresh three-page static PDF. The static output
therefore contains no hidden source stream, redaction annotation, or overlay
layer. Do not use this script for a byte-different source.
"""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from transform_known_gs40_160_chart import PROFILE_SHA256, mutate_chart, require_profile


def overlay_page(index: int, width: float, height: float, casing: str, logo: Path):
    buffer = BytesIO()
    drawing = canvas.Canvas(buffer, pagesize=(width, height))
    drawing.setFillColor(white)

    def clear(x: float, top: float, w: float, h: float) -> None:
        drawing.rect(x, height - top - h, w, h, fill=1, stroke=0)

    def put(x: float, top: float, value: str, size: float = 6.2) -> None:
        drawing.setFillColorRGB(0, 0, 0)
        drawing.setFont("Helvetica", size)
        drawing.drawString(x, height - top - size, value)
        drawing.setFillColor(white)

    # The customer block and original footer are removed only in the rebuilt
    # static page; no source content survives the final render.
    clear(54, 95, 529, 49)
    clear(52, 800, 180, 42)
    drawing.drawImage(str(logo), 54, 3, width=130, height=36, mask="auto")

    if index == 0:
        clear(395, 65, 105, 16); put(396, 66, "AHe 40-16", 12.2)
        clear(203, 274, 55, 9); put(204, 276, "AHe 40-16")
        clear(203, 297.8, 35, 7); put(204, 299, "SIYUEH")
        for top in (331, 343):
            clear(203, top + 1, 95, 8); put(204, top + 2, "ANSI 150LB RF SF")
        clear(330, 403, 115, 6.5); put(330, 403, "Max. Shaft Power")
        clear(470.2, 402.9, 15, 6.6); put(470, 403, "12.28")
        clear(470, 414.5, 22, 8); put(470, 415, "68.6")
        for top, value in ((447, casing), (458, "SCS13"), (469, "SUS304"), (480, "FKM"), (491, "SiC & Carbon & FKM")):
            clear(203, top + 1, 105, 8); put(204, top + 2, value)
        clear(203, 534, 72, 8); put(204, 535, "TECO Standard")
        clear(203, 545, 88, 8); put(204, 546, "15_3_380")
        clear(203, 556, 140, 8); put(204, 558, "60Hz")
        clear(470, 556, 28, 8)  # Frame size value
        clear(470, 568, 28, 8)  # Weight value
        clear(470, 579, 28, 8); put(470, 580, "460")
        clear(470, 591, 28, 8)  # Electric current value
    elif index == 1:
        clear(395, 65, 105, 16); put(396, 66, "AHe 40-16", 12.2)
        clear(54, 207, 205, 13)  # Test standard
        # Delete only the right-side Δp scale/ticks/stubs. The left edge starts
        # just right of the original retained vertical chart border.
        clear(538.2, 218, 44.8, 284)
    elif index == 2:
        clear(352, 65, 105, 16); put(354, 66, "AHe 40-16", 12.2)

    drawing.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--casing", required=True)
    args = parser.parse_args()

    if hashlib.sha256(args.input.read_bytes()).hexdigest().upper() != PROFILE_SHA256:
        raise ValueError("this adapter accepts only the exact known GS 40-160 source")
    logo = Path(__file__).resolve().parents[1] / "assets" / "siyueh-logo.jpg"
    if not logo.exists():
        raise FileNotFoundError(logo)

    source = PdfReader(args.input)
    if len(source.pages) != 4:
        raise ValueError("expected a four-page source")
    raw_chart = source.pages[1].get_contents().get_data().decode("latin-1")
    require_profile(args.input, raw_chart)
    transformed_chart = mutate_chart(raw_chart)
    from pypdf.generic import DecodedStreamObject
    intermediate = args.output.with_name(args.output.stem + ".native-stage.pdf")
    writer = PdfWriter()
    for page in source.pages[:3]:
        writer.add_page(page)
    stream = DecodedStreamObject()
    stream.set_data(transformed_chart.encode("latin-1"))
    writer.pages[1].replace_contents(stream)
    page_sizes = []
    for index, page in enumerate(writer.pages):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        page_sizes.append((width, height))
        page.merge_page(overlay_page(index, width, height, args.casing, logo))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with intermediate.open("wb") as file:
        writer.write(file)

    # Build a new static document. Source content streams do not appear in the
    # final artifact, so deleted text and Δp-axis objects cannot leak through.
    rendered = pdfium.PdfDocument(intermediate)
    final = canvas.Canvas(str(args.output), pagesize=page_sizes[0])
    for index, page in enumerate(rendered):
        image = page.render(scale=300 / 72).to_pil().convert("RGB")
        final.setPageSize(page_sizes[index])
        final.drawImage(ImageReader(image), 0, 0, width=page_sizes[index][0], height=page_sizes[index][1])
        final.showPage()
    final.save()


if __name__ == "__main__":
    main()
