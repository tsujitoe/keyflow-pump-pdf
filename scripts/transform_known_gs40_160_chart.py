"""Transform the Grade 1U chart objects of the known EBARA GS 40-160 source.

This helper deliberately supports one byte-identified source profile. It edits
only page 2's decoded content stream: retained P2/efficiency paths, their
markers/operating groups, and the efficiency text operands. It does not
perform page branding, table edits, or right-Δp-axis removal; those remain
separate native-content-stream operations in the calling conversion.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject


PROFILE_SHA256 = "C8311DE112F28439879F28F014BE2F018A102F5CB0699753168B3BE36726E2F5"
P2_START = "q q 1068 -9711 16118 -3227 re"
EFF_START = "q q 1068 -12938 16118 -3253 re"
NPSH_START = "q q 1068 -16165 16118 -3253 re"


def require_profile(source: Path, page2: str) -> None:
    digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
    if digest != PROFILE_SHA256:
        raise ValueError(f"unsupported source SHA-256: {digest}")
    count = sum(page2.count(signature) for signature in (P2_START, EFF_START, NPSH_START))
    if count != 3:
        raise ValueError("the expected P2/efficiency/NPSH clip groups are not unique")


def replace_efficiency_glyphs(content: str) -> str:
    # Exact source-native glyph runs. Keep the source CID font, fill colour,
    # kerning operands, and surrounding text object untouched.
    replacements = {
        "<0035>63.58<0032>46.54<0025>92.75": "<0034>63.58<0038>46.54<0025>92.75",
        "<0036>59.58<0031>126.54<0025>92.75": "<0035>59.58<0037>126.54<0025>92.75",
        "<0036>59.58<0038>58.54<0025>92.75": "<0036>59.58<0033>58.54<0025>92.75",
        "<0037>69.58<0032>46.54<0025>92.75": "<0036>69.58<0037>46.54<0025>92.75",
        "<0037>69.58<0034>30.54<0025>92.75": "<0036>69.58<0039>30.54<0025>92.75",
        "<0037>69.58<0034>30.54<002E>49.16<0034>34.59<0025>88.7": "<0036>69.58<0039>30.54<002E>49.16<0032>34.59<0025>88.7",
        "<0037>69.58<0035>63.58<0025>88.7": "<0037>69.58<0030>63.58<0025>88.7",
        "<0037>69.58<0033>59.54<0025>92.75": "<0036>69.58<0038>59.54<0025>92.75",
        "<0031>130.58<0031>126.54<002E>49.16<0034>34.59<0032>46.54": "<0031>130.58<0032>126.54<002E>49.16<0032>34.59<0038>46.54",
        "<0037>69.58<0033>59.54<002E>49.16<0037>69.59<0035>59.54": "<0036>69.58<0038>59.54<002E>49.16<0035>69.59<0039>59.54",
    }
    for old, new in replacements.items():
        if old not in content:
            raise ValueError(f"missing efficiency glyph run: {old}")
        content = content.replace(old, new)

    for old, new in (("265 -11156 Td", "265 -11117 Td"), ("251 -13292 Td", "251 -13260 Td")):
        if old not in content:
            raise ValueError(f"missing callout anchor: {old}")
        content = content.replace(old, new)
    return content


def remove_outer_impeller_traces(panel: str) -> str:
    """Remove complete max/min path-marker groups; retain the dark-blue rated group."""
    for colour in ("0 0.4 0.616 RG", "0.616 0.122 0 RG"):
        before = panel
        panel = re.sub(re.escape(colour) + r".*?(?: S| b\\*)", "", panel, flags=re.S)
        if panel == before:
            raise ValueError(f"outer impeller colour group was not found: {colour}")
    return panel


def transform_panel_y(panel: str, zero: int, factor: float) -> str:
    def transform(match: re.Match[str]) -> str:
        value = int(match.group(0))
        return str(round(zero + (value - zero) * factor)) if zero <= value <= zero + 3250 else match.group(0)

    return re.sub(r"(?<![0-9.])-?[0-9]+(?![0-9.])", transform, panel)


def transform_green_group(content: str, anchor: str, zero: int, factor: float) -> str:
    position = content.find(anchor)
    if position < 0:
        raise ValueError(f"green operating group anchor missing: {anchor}")
    begin = content.rfind(" 0 G 35 w", 0, position)
    end = content.find(" 0 G 35 w", begin + 1)
    if begin < 0 or end < 0:
        raise ValueError("could not isolate green operating group")
    return content[:begin] + transform_panel_y(content[begin:end], zero, factor) + content[end:]


def mutate_chart(content: str) -> str:
    content = replace_efficiency_glyphs(content)
    starts = (P2_START, EFF_START, NPSH_START)
    for index in range(len(starts) - 1, -1, -1):
        begin = content.find(starts[index])
        end = content.find(starts[index + 1], begin) if index + 1 < len(starts) else len(content)
        if begin < 0 or end < 0:
            raise ValueError("could not isolate a chart panel")
        content = content[:begin] + remove_outer_impeller_traces(content[begin:end]) + content[end:]

    p2_begin = content.find(P2_START)
    efficiency_begin = content.find(EFF_START)
    content = content[:p2_begin] + transform_panel_y(content[p2_begin:efficiency_begin], -12937, 1 / 0.93) + content[efficiency_begin:]
    efficiency_begin = content.find(EFF_START)
    npsh_begin = content.find(NPSH_START)
    content = content[:efficiency_begin] + transform_panel_y(content[efficiency_begin:npsh_begin], -16171, 0.93) + content[npsh_begin:]
    content = transform_green_group(content, "9151 -11092", -12937, 1 / 0.93)
    return transform_green_group(content, "9151 -13191", -16171, 0.93)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    reader = PdfReader(args.input)
    if len(reader.pages) != 4:
        raise ValueError("the known profile must have exactly four source pages")
    source_page2 = reader.pages[1].get_contents().get_data().decode("latin-1")
    require_profile(args.input, source_page2)
    transformed = mutate_chart(source_page2)

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    stream = DecodedStreamObject()
    stream.set_data(transformed.encode("latin-1"))
    writer.pages[1].replace_contents(stream)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as file:
        writer.write(file)


if __name__ == "__main__":
    main()
