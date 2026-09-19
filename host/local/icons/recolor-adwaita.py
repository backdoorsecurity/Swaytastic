#!/usr/bin/env python3
"""Copy Adwaita SVG trees into a Swaytastic icon theme and remap colors."""
from __future__ import annotations

import colorsys
import re
import shutil
from pathlib import Path

ADWAITA = Path("/usr/share/icons/Adwaita")
DEST = Path("/tmp/Swaytastic-icons")
OURS = Path("/usr/share/icons/Swaytastic")

PINK = (0xDE, 0x10, 0x62)
PINK_DARK = (0x6F, 0x08, 0x31)
GREEN = (0x99, 0xE0, 0x1C)
GREEN_DARK = (0x4A, 0x7A, 0x0E)
BLACK = (0x10, 0x09, 0x09)
BLACKER = (0x00, 0x00, 0x00)

# Adwaita symbolic default foreground must not collapse to black-on-black.
SPECIAL = {
    (0x2E, 0x34, 0x36): GREEN,
    (0x24, 0x1F, 0x31): BLACKER,
}


def hex_of(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def map_rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
    key = (r, g, b)
    if key in SPECIAL:
        return SPECIAL[key]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx < 10:
        return BLACKER
    if mx - mn < 28:
        if mx > 200:
            return GREEN
        if mx > 140:
            return GREEN_DARK
        if mx > 80:
            return BLACK
        return BLACKER
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if v < 0.12:
        return BLACKER
    # blue / cyan / purple → pink chrome
    if 0.45 <= h < 0.90:
        return PINK if v >= 0.42 else PINK_DARK
    # reds → pink
    if h < 0.08 or h >= 0.90:
        return PINK if v >= 0.42 else PINK_DARK
    # yellow / green → lime
    return GREEN if v >= 0.45 else GREEN_DARK


HEX6 = re.compile(r"#([0-9a-fA-F]{6})\b")
HEX3 = re.compile(r"#([0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def _sub_hex6(m: re.Match[str]) -> str:
    h = m.group(1)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return hex_of(map_rgb(r, g, b))


def _sub_hex3(m: re.Match[str]) -> str:
    h = m.group(1)
    r, g, b = int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16)
    return hex_of(map_rgb(r, g, b))


def _sub_rgb(m: re.Match[str]) -> str:
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    return hex_of(map_rgb(r, g, b))


def recolor_svg(text: str) -> str:
    text = HEX6.sub(_sub_hex6, text)
    text = HEX3.sub(_sub_hex3, text)
    text = RGB.sub(_sub_rgb, text)
    return text


INDEX = """[Icon Theme]
Name=Swaytastic
Comment=Swaytastic folders and Adwaita shapes in green/pink
Inherits=hicolor
Directories=scalable/places,scalable/mimetypes,scalable/devices,scalable/status,symbolic/actions,symbolic/apps,symbolic/categories,symbolic/devices,symbolic/emblems,symbolic/emotes,symbolic/mimetypes,symbolic/places,symbolic/status,symbolic/legacy,symbolic/ui

[scalable/places]
Size=48
MinSize=1
MaxSize=512
Context=Places
Type=Scalable

[scalable/mimetypes]
Size=48
MinSize=1
MaxSize=512
Context=MimeTypes
Type=Scalable

[scalable/devices]
Size=48
MinSize=1
MaxSize=512
Context=Devices
Type=Scalable

[scalable/status]
Size=48
MinSize=1
MaxSize=512
Context=Status
Type=Scalable

[symbolic/actions]
Size=16
MinSize=1
MaxSize=512
Context=Actions
Type=Scalable

[symbolic/apps]
Size=16
MinSize=1
MaxSize=512
Context=Applications
Type=Scalable

[symbolic/categories]
Size=16
MinSize=1
MaxSize=512
Context=Categories
Type=Scalable

[symbolic/devices]
Size=16
MinSize=1
MaxSize=512
Context=Devices
Type=Scalable

[symbolic/emblems]
Size=16
MinSize=1
MaxSize=512
Context=Emblems
Type=Scalable

[symbolic/emotes]
Size=16
MinSize=1
MaxSize=512
Context=Emotes
Type=Scalable

[symbolic/mimetypes]
Size=16
MinSize=1
MaxSize=512
Context=MimeTypes
Type=Scalable

[symbolic/places]
Size=16
MinSize=1
MaxSize=512
Context=Places
Type=Scalable

[symbolic/status]
Size=16
MinSize=1
MaxSize=512
Context=Status
Type=Scalable

[symbolic/legacy]
Size=16
MinSize=1
MaxSize=512
Context=Legacy
Type=Scalable

[symbolic/ui]
Size=16
MinSize=1
MaxSize=512
Context=UI
Type=Scalable
"""


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for tree in ("scalable", "symbolic"):
        src = ADWAITA / tree
        if not src.is_dir():
            continue
        dst = DEST / tree
        shutil.copytree(src, dst, symlinks=True)
        for svg in dst.rglob("*.svg"):
            if svg.is_symlink():
                continue
            original = svg.read_text(encoding="utf-8", errors="replace")
            svg.write_text(recolor_svg(original), encoding="utf-8")

    # Keep the hand-drawn Swaytastic folder glyphs.
    ours_folder = (OURS / "scalable/places/folder.svg").read_bytes()
    ours_open = (OURS / "scalable/places/folder-open.svg").read_bytes()
    ours_inode = (OURS / "scalable/mimetypes/inode-directory.svg").read_bytes()
    for ctx in ("places", "mimetypes"):
        d = DEST / "scalable" / ctx
        d.mkdir(parents=True, exist_ok=True)
        (d / "folder.svg").write_bytes(ours_folder)
        (d / "folder-open.svg").write_bytes(ours_open)
        (d / "inode-directory.svg").write_bytes(ours_inode)

    (DEST / "index.theme").write_text(INDEX, encoding="utf-8")
    print("built", DEST)


if __name__ == "__main__":
    main()
