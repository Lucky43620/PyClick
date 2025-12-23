"""
Génère une série d'icônes pixel-art 16x16 (placeholders) sans stocker de binaires dans le repo.

Usage :
    python assets/pixel/generate_icons.py
"""

import struct
import zlib
from pathlib import Path
from typing import Dict, Tuple

WIDTH = HEIGHT = 16
OUTPUT_DIR = Path(__file__).parent


def write_png(path: Path, pixels, width: int, height: int) -> None:
    raw = b"".join(b"\x00" + bytes(p) for p in pixels)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def make_icon(base: Tuple[int, int, int], accent: Tuple[int, int, int], spec: str | None = None):
    pixels = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if spec == "diagonal" and (x == y or x + y == WIDTH - 1):
                color = accent
            elif spec == "border" and (x in (0, WIDTH - 1) or y in (0, HEIGHT - 1)):
                color = accent
            elif (x + y) % 5 == 0:
                color = accent
            elif (x % 4 == 0 and y % 3 == 0):
                color = tuple(max(0, c - 20) for c in base)
            else:
                color = base
            row.extend((*color, 255))
        pixels.append(row)
    return pixels


def main() -> None:
    icons: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
        "wood.png": ((140, 98, 57), (170, 128, 78)),
        "stone.png": ((110, 114, 118), (160, 165, 170)),
        "herb.png": ((60, 130, 70), (90, 170, 100)),
        "coin.png": ((196, 156, 40), (236, 195, 60)),
        "iron_ingot.png": ((150, 156, 170), (190, 196, 210)),
        "leather.png": ((139, 98, 63), (172, 125, 85)),
        "crystal.png": ((80, 140, 200), (140, 200, 255)),
        "potion_red.png": ((180, 50, 60), (230, 110, 120)),
        "potion_blue.png": ((60, 90, 180), (110, 150, 230)),
        "scroll.png": ((210, 200, 160), (240, 220, 180)),
        "pickaxe.png": ((120, 90, 70), (180, 160, 120)),
        "sword.png": ((160, 160, 170), (220, 220, 230)),
        "shield.png": ((120, 140, 170), (190, 200, 215)),
        "ring.png": ((200, 170, 80), (240, 210, 110)),
    }

    specs = {
        "crystal.png": "diagonal",
        "shield.png": "border",
        "ring.png": "border",
    }

    for name, (base, accent) in icons.items():
        pixels = make_icon(base, accent, specs.get(name))
        write_png(OUTPUT_DIR / name, pixels, WIDTH, HEIGHT)
        print(f"Wrote {name}")


if __name__ == "__main__":
    main()
