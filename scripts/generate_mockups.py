from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def save_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]]) -> None:
    raw = b"".join(b"\x00" + bytes([c for pixel in pixels[y * width:(y + 1) * width] for c in pixel]) for y in range(height))
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += png_chunk(b"IDAT", zlib.compress(raw, 9))
    data += png_chunk(b"IEND", b"")
    path.write_bytes(data)


def rect(pixels, width, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(len(pixels) // width, y1)):
        for x in range(max(0, x0), min(width, x1)):
            pixels[y * width + x] = color


def make_mockup(path: Path, accent: tuple[int, int, int]) -> None:
    width, height = 1280, 720
    pixels = [(248, 250, 252)] * (width * height)
    rect(pixels, width, 0, 0, width, 64, (18, 32, 43))
    rect(pixels, width, 24, 96, 270, 188, accent)
    rect(pixels, width, 300, 96, 546, 188, (43, 124, 114))
    rect(pixels, width, 576, 96, 822, 188, (237, 176, 31))
    rect(pixels, width, 852, 96, 1098, 188, (126, 87, 194))
    rect(pixels, width, 24, 224, 610, 520, (255, 255, 255))
    rect(pixels, width, 650, 224, 1256, 520, (255, 255, 255))
    for idx, h in enumerate([180, 245, 120, 280, 210, 155]):
        x = 64 + idx * 80
        rect(pixels, width, x, 500 - h, x + 44, 500, accent)
    rect(pixels, width, 690, 264, 1210, 482, (225, 232, 238))
    rect(pixels, width, 24, 560, 1256, 680, (255, 255, 255))
    save_png(path, width, height, pixels)


def main() -> None:
    names = [
        "01_overview", "02_generation", "03_load", "04_renewables", "05_mmgd",
        "06_geography", "07_expansion", "08_market", "09_state_detail", "10_source_detail",
    ]
    colors = [(22, 119, 190), (36, 131, 78), (205, 92, 52), (49, 150, 129), (247, 166, 37)]
    out = ROOT / "assets/mockups"
    out.mkdir(parents=True, exist_ok=True)
    for idx, name in enumerate(names):
        make_mockup(out / f"{name}.png", colors[idx % len(colors)])
    screenshots = ROOT / "assets/screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    for name in ["overview", "generation", "load", "renewables", "mmgd", "geography", "expansion", "market"]:
        make_mockup(screenshots / f"{name}.png", colors[len(name) % len(colors)])
    print("[OK] mockups")


if __name__ == "__main__":
    main()
