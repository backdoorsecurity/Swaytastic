#!/usr/bin/env python3
"""Build a Swaytastic look from local/packs/<name>.conf.

Installed GTK/icon/qt names stay Swaytastic. Packs only change colors.
"""
from __future__ import annotations

import argparse
import colorsys
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACKS = HERE / "packs"
TEMPLATES = HERE / "templates"
ADWAITA = Path("/usr/share/icons/Adwaita")

HEX_KEYS = (
    "fg",
    "fg_dim",
    "accent",
    "accent_dim",
    "bg",
    "bg_alt",
    "bg_deep",
    "selection",
    "selection_fg",
    "warning",
    "error",
    "success",
    "unfocused",
    "red",
    "blue",
    "yellow",
    "pink",
    "purple",
    "green",
    "folder_fill",
    "folder_stroke",
    "waybar_border",
    "clock",
    "workspace_active_fg",
    "workspace_active_border",
    "workspace_inactive_fg",
    "workspace_inactive_border",
    "term_green",
    "term_green_bright",
    "term_blue",
    "term_blue_bright",
    "term_purple",
    "term_purple_bright",
)

HEX6 = re.compile(r"#([0-9a-fA-F]{6})\b")
HEX3 = re.compile(r"#([0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def parse_hex(value: str) -> tuple[int, int, int]:
    h = value.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"need #rrggbb, got {value!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_of(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def darken(rgb: tuple[int, int, int], factor: float = 0.5) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def lighten(rgb: tuple[int, int, int], t: float = 0.35) -> tuple[int, int, int]:
    return tuple(min(255, int(c + (255 - c) * t)) for c in rgb)  # type: ignore[return-value]


def hue_of(rgb: tuple[int, int, int]) -> float:
    return colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)[0]


def hue_dist(a: float, b: float) -> float:
    d = abs(a - b)
    return min(d, 1.0 - d)


def load_pack(name: str) -> dict[str, str]:
    path = PACKS / f"{name}.conf"
    if not path.is_file():
        known = ", ".join(p.stem for p in sorted(PACKS.glob("*.conf"))) or "(none)"
        raise SystemExit(f"unknown pack {name!r}. have: {known}")
    raw: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        raw[key.strip()] = val.strip()

    def hx(key: str, default: str) -> str:
        v = raw.get(key, default).strip()
        if not v.startswith("#"):
            v = "#" + v
        parse_hex(v)
        return v.lower()

    fg = hx("fg", "#99e01c")
    accent = hx("accent", "#de1062")
    bg = hx("bg", "#000000")
    pack = {
        "name": raw.get("name", name),
        "comment": raw.get("comment", name),
        "icon_mode": raw.get("icon_mode", "dual").strip().lower(),
        "fg": fg,
        "accent": accent,
        "bg": bg,
        "fg_dim": hx("fg_dim", hex_of(darken(parse_hex(fg)))),
        "accent_dim": hx("accent_dim", hex_of(darken(parse_hex(accent)))),
        "bg_alt": hx("bg_alt", "#100909"),
        "bg_deep": hx("bg_deep", "#090909"),
        "selection": hx("selection", accent),
        "selection_fg": hx("selection_fg", fg),
        "warning": hx("warning", accent),
        "error": hx("error", accent),
        "success": hx("success", fg),
        "unfocused": hx("unfocused", hex_of(darken(parse_hex(accent)))),
        "red": hx("red", accent),
        "blue": hx("blue", accent),
        "yellow": hx("yellow", fg),
        "pink": hx("pink", accent),
        "purple": hx("purple", hex_of(darken(parse_hex(accent)))),
        "green": hx("green", fg),
        "folder_fill": hx("folder_fill", accent),
        "folder_stroke": hx("folder_stroke", fg),
        "waybar_border": hx("waybar_border", accent),
        "clock": hx("clock", fg),
        "workspace_active_fg": hx("workspace_active_fg", fg),
        "workspace_active_border": hx("workspace_active_border", fg),
        "workspace_inactive_fg": hx("workspace_inactive_fg", accent),
        "workspace_inactive_border": hx("workspace_inactive_border", fg),
        "term_green": hx("term_green", hx("green", fg)),
        "term_blue": hx("term_blue", hx("blue", accent)),
        "term_purple": hx("term_purple", hx("purple", hex_of(darken(parse_hex(accent))))),
    }
    pack["term_green_bright"] = hx(
        "term_green_bright", hex_of(lighten(parse_hex(pack["term_green"])))
    )
    pack["term_blue_bright"] = hx(
        "term_blue_bright", hex_of(lighten(parse_hex(pack["term_blue"])))
    )
    pack["term_purple_bright"] = hx(
        "term_purple_bright", hex_of(lighten(parse_hex(pack["term_purple"])))
    )
    for key in HEX_KEYS:
        r, g, b = parse_hex(pack[key])
        pack[f"{key}_rgb"] = f"{r},{g},{b}"
        pack[f"{key}_bare"] = pack[key][1:]
        pack[f"{key}_qt"] = f"#ff{pack[key][1:]}"
        pack[f"{key}_qt80"] = f"#80{pack[key][1:]}"
    return pack


def render_template(name: str, pack: dict[str, str]) -> str:
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    return Template(text).substitute(pack)


def qt_line(pack: dict[str, str], *, disabled: bool) -> str:
    if disabled:
        fg, accent, placeholder = pack["fg_dim_qt"], pack["accent_dim_qt"], pack["fg_dim_qt80"]
    else:
        fg, accent, placeholder = pack["fg_qt"], pack["accent_qt"], pack["fg_qt80"]
    sel = pack["accent_dim_qt"] if disabled else pack["selection_qt"]
    sel_fg = pack["fg_dim_qt"] if disabled else pack["selection_fg_qt"]
    parts = [
        fg,  # WindowText
        pack["bg_qt"],  # Button
        accent,  # Light
        accent,  # Midlight
        accent,  # Dark
        accent,  # Mid
        fg,  # Text
        fg,  # BrightText
        fg,  # ButtonText
        pack["bg_qt"],  # Base
        pack["bg_qt"],  # Window
        accent,  # Shadow
        sel,  # Highlight
        sel_fg,  # HighlightedText
        accent,  # Link
        fg,  # LinkVisited (matches current green_on_pink qt scheme)
        pack["bg_alt_qt"],  # AlternateBase
        fg,  # NoRole
        pack["bg_qt"],  # ToolTipBase
        fg,  # ToolTipText
        placeholder,  # PlaceholderText
        accent,  # Accent
    ]
    return ", ".join(parts)


def qt_conf(pack: dict[str, str]) -> str:
    return (
        "[ColorScheme]\n"
        f"active_colors={qt_line(pack, disabled=False)}\n"
        f"disabled_colors={qt_line(pack, disabled=True)}\n"
        f"inactive_colors={qt_line(pack, disabled=False)}\n"
    )


def kdeglobals(pack: dict[str, str]) -> str:
    return f"""[General]
ColorScheme=Swaytastic
TerminalApplication=foot

[Colors:Window]
BackgroundNormal={pack['bg_alt_rgb']}
BackgroundAlternate={pack['bg_alt_rgb']}
ForegroundNormal={pack['fg_rgb']}
ForegroundInactive={pack['fg_dim_rgb']}
ForegroundLink={pack['accent_rgb']}
ForegroundVisited={pack['accent_dim_rgb']}
ForegroundNegative={pack['error_rgb']}
ForegroundNeutral={pack['fg_rgb']}
ForegroundPositive={pack['success_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[Colors:View]
BackgroundNormal={pack['bg_rgb']}
BackgroundAlternate={pack['bg_alt_rgb']}
ForegroundNormal={pack['fg_rgb']}
ForegroundInactive={pack['fg_dim_rgb']}
ForegroundLink={pack['accent_rgb']}
ForegroundVisited={pack['accent_dim_rgb']}
ForegroundNegative={pack['error_rgb']}
ForegroundNeutral={pack['fg_rgb']}
ForegroundPositive={pack['success_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[Colors:Button]
BackgroundNormal={pack['bg_alt_rgb']}
BackgroundAlternate={pack['bg_alt_rgb']}
ForegroundNormal={pack['fg_rgb']}
ForegroundInactive={pack['fg_dim_rgb']}
ForegroundLink={pack['accent_rgb']}
ForegroundVisited={pack['accent_dim_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[Colors:Selection]
BackgroundNormal={pack['selection_rgb']}
BackgroundAlternate={pack['unfocused_rgb']}
ForegroundNormal={pack['selection_fg_rgb']}
ForegroundInactive={pack['selection_fg_rgb']}
ForegroundLink={pack['selection_fg_rgb']}
ForegroundVisited={pack['selection_fg_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[Colors:Tooltip]
BackgroundNormal={pack['bg_rgb']}
BackgroundAlternate={pack['bg_alt_rgb']}
ForegroundNormal={pack['fg_rgb']}
ForegroundInactive={pack['fg_dim_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[Colors:Header]
BackgroundNormal={pack['bg_alt_rgb']}
BackgroundAlternate={pack['bg_alt_rgb']}
ForegroundNormal={pack['fg_rgb']}
ForegroundInactive={pack['fg_dim_rgb']}
DecorationFocus={pack['accent_rgb']}
DecorationHover={pack['accent_rgb']}

[WM]
activeBackground={pack['bg_alt_rgb']}
activeForeground={pack['fg_rgb']}
inactiveBackground={pack['bg_alt_rgb']}
inactiveForeground={pack['fg_dim_rgb']}
activeBlend={pack['accent_rgb']}
inactiveBlend={pack['unfocused_rgb']}
frame={pack['accent_rgb']}
inactiveFrame={pack['unfocused_rgb']}
"""


def waybar_css(pack: dict[str, str]) -> str:
    rainbow = pack["icon_mode"] == "rainbow"
    bat = pack["green"] if rainbow else pack["fg"]
    bat_warn = pack["yellow"] if rainbow else pack["accent"]
    bat_crit = pack["red"] if rainbow else pack["accent"]
    urgent = pack["error"] if rainbow else pack["accent"]
    return f"""/* Generated from pack {pack['name']} */

* {{
    font-family: monospace;
    font-size: 20px;
    min-height: 0;
}}

window#waybar {{
    background: {pack['bg_alt']};
    color: {pack['fg']};
    border: 2px solid {pack['waybar_border']};
    min-height: 40px;
}}

#workspaces {{
    margin: 0;
    padding: 0 2px;
}}

#workspaces button {{
    background: {pack['bg_deep']};
    color: {pack['workspace_inactive_fg']};
    border: 1px solid {pack['workspace_inactive_border']};
    border-radius: 0;
    padding: 2px 4px;
    margin: 4px 2px;
}}

#workspaces button.focused,
#workspaces button.active {{
    background: {pack['bg_deep']};
    color: {pack['workspace_active_fg']};
    border-color: {pack['workspace_active_border']};
}}

#workspaces button.urgent {{
    background: {pack['bg']};
    color: {urgent};
    border-color: {urgent};
}}

#battery {{
    color: {bat};
    padding: 0 12px;
}}

#battery.charging,
#battery.plugged {{
    color: {bat};
}}

#battery.warning {{
    color: {bat_warn};
}}

#battery.critical {{
    color: {bat_crit};
}}

#clock {{
    color: {pack['clock']};
    padding: 0 12px;
}}
"""


def foot_colors(pack: dict[str, str]) -> str:
    r, b, y, g, p, pk = (
        pack["red_bare"],
        pack["term_blue_bare"],
        pack["yellow_bare"],
        pack["term_green_bare"],
        pack["term_purple_bare"],
        pack["pink_bare"],
    )
    br = hex_of(lighten(parse_hex(pack["red"])))[1:]
    bb = pack["term_blue_bright_bare"]
    by = hex_of(lighten(parse_hex(pack["yellow"])))[1:]
    bg_ = pack["term_green_bright_bare"]
    bp = pack["term_purple_bright_bare"]
    bpk = hex_of(lighten(parse_hex(pack["pink"])))[1:]
    return f"""[colors]
 alpha=1.0
 background={pack['bg_deep_bare']}
 foreground={pack['fg_bare']}
 flash=009cff
 flash-alpha=0.5

 regular0={pack['bg_bare']}
 regular1={r}
 regular2={g}
 regular3={y}
 regular4={b}
 regular5={p}
 regular6={pk}
 regular7={pack['fg_bare']}

 bright0={pack['bg_alt_bare']}
 bright1={br}
 bright2={bg_}
 bright3={by}
 bright4={bb}
 bright5={bp}
 bright6={bpk}
 bright7={pack['fg_bare']}
"""


def patch_foot(path: Path, pack: dict[str, str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    block = foot_colors(pack).rstrip() + "\n"
    new, n = re.subn(
        r"(?ms)^\[colors\].*?(?=^\[|\Z)",
        block + "\n",
        text,
        count=1,
    )
    if n == 0:
        new = text.rstrip() + "\n\n" + block
    path.write_text(new, encoding="utf-8")


def patch_pcmanfm(path: Path, pack: dict[str, str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(FgColor=).*$", r"\g<1>" + pack["fg"], text)
    text = re.sub(r"(?m)^(BgColor=).*$", r"\g<1>" + pack["bg"], text)
    text = re.sub(r"(?m)^(ShadowColor=).*$", r"\g<1>" + pack["bg"], text)
    path.write_text(text, encoding="utf-8")


def make_mapper(pack: dict[str, str]):
    fg = parse_hex(pack["fg"])
    fg_dim = parse_hex(pack["fg_dim"])
    accent = parse_hex(pack["accent"])
    accent_dim = parse_hex(pack["accent_dim"])
    bg = parse_hex(pack["bg"])
    bg_alt = parse_hex(pack["bg_alt"])
    special = {
        (0x2E, 0x34, 0x36): fg,
        (0x24, 0x1F, 0x31): bg,
    }
    swatches = [
        (hue_of(parse_hex(pack[k])), parse_hex(pack[k]))
        for k in ("red", "blue", "yellow", "pink", "purple", "green")
    ]
    rainbow = pack["icon_mode"] == "rainbow"

    def nearest(h: float) -> tuple[int, int, int]:
        return min(swatches, key=lambda item: hue_dist(h, item[0]))[1]

    def map_rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
        key = (r, g, b)
        if key in special:
            return special[key]
        mx, mn = max(r, g, b), min(r, g, b)
        if mx < 10:
            return bg
        if mx - mn < 28:
            if mx > 200:
                return fg
            if mx > 140:
                return fg_dim
            if mx > 80:
                return bg_alt
            return bg
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if v < 0.12:
            return bg
        if rainbow:
            color = nearest(h)
            return color if v >= 0.42 else darken(color)
        if 0.45 <= h < 0.90 or h < 0.08 or h >= 0.90:
            return accent if v >= 0.42 else accent_dim
        return fg if v >= 0.45 else fg_dim

    def sub_hex6(m: re.Match[str]) -> str:
        h = m.group(1)
        return hex_of(map_rgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))

    def sub_hex3(m: re.Match[str]) -> str:
        h = m.group(1)
        return hex_of(map_rgb(int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16)))

    def sub_rgb(m: re.Match[str]) -> str:
        return hex_of(map_rgb(*(int(m.group(i)) for i in (1, 2, 3))))

    def recolor_svg(text: str) -> str:
        text = HEX6.sub(sub_hex6, text)
        text = HEX3.sub(sub_hex3, text)
        text = RGB.sub(sub_rgb, text)
        return text

    return recolor_svg


def ignore_emblems(directory: str, names: list[str]) -> list[str]:
    if Path(directory).name == "symbolic" and "emblems" in names:
        return ["emblems"]
    return []


def write_folder_glyphs(pack: dict[str, str], dest: Path) -> None:
    folder = render_template("folder.svg", pack)
    for ctx in ("places", "mimetypes"):
        d = dest / "scalable" / ctx
        d.mkdir(parents=True, exist_ok=True)
        (d / "folder.svg").write_text(folder, encoding="utf-8")
        (d / "folder-open.svg").write_text(folder, encoding="utf-8")
        (d / "inode-directory.svg").write_text(folder, encoding="utf-8")


def build_icons(pack: dict[str, str], dest: Path) -> None:
    if not ADWAITA.is_dir():
        raise SystemExit(f"Adwaita icons not found at {ADWAITA}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    recolor_svg = make_mapper(pack)
    for tree in ("scalable", "symbolic"):
        src = ADWAITA / tree
        if not src.is_dir():
            continue
        dst = dest / tree
        shutil.copytree(src, dst, symlinks=True, ignore=ignore_emblems)
        for svg in dst.rglob("*.svg"):
            if svg.is_symlink():
                continue
            original = svg.read_text(encoding="utf-8", errors="replace")
            svg.write_text(recolor_svg(original), encoding="utf-8")

    write_folder_glyphs(pack, dest)
    (dest / "index.theme").write_text(
        render_template("icon-index.theme", pack), encoding="utf-8"
    )


def write_theme_tree(pack: dict[str, str], dest: Path) -> None:
    gtk = dest / "themes" / "Swaytastic"
    (gtk / "gtk-3.0").mkdir(parents=True, exist_ok=True)
    (gtk / "gtk-4.0").mkdir(parents=True, exist_ok=True)
    (gtk / "index.theme").write_text(
        render_template("gtk-index.theme", pack), encoding="utf-8"
    )
    (gtk / "gtk-3.0" / "gtk.css").write_text(
        render_template("gtk-3.0.css", pack), encoding="utf-8"
    )
    (gtk / "gtk-4.0" / "gtk.css").write_text(
        render_template("gtk-4.0.css", pack), encoding="utf-8"
    )

    qss_dir = dest / "qss"
    qss_dir.mkdir(parents=True, exist_ok=True)
    (qss_dir / "Swaytastic.qss").write_text(
        render_template("Swaytastic.qss", pack), encoding="utf-8"
    )

    colors_dir = dest / "colors"
    colors_dir.mkdir(parents=True, exist_ok=True)
    (colors_dir / "Swaytastic.conf").write_text(qt_conf(pack), encoding="utf-8")

    (dest / "kdeglobals").write_text(kdeglobals(pack), encoding="utf-8")
    (dest / "waybar.css").write_text(waybar_css(pack), encoding="utf-8")
    (dest / "pack.name").write_text(pack["name"] + "\n", encoding="utf-8")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def sudo_cp(src: Path, dest: Path) -> None:
    run(["sudo", "cp", "-a", str(src), str(dest)])


def install_live(stage: Path, pack: dict[str, str], *, skip_icons: bool) -> None:
    sudo_cp(stage / "themes" / "Swaytastic", Path("/usr/share/themes/"))
    sudo_cp(stage / "qss" / "Swaytastic.qss", Path("/usr/share/qt6ct/qss/Swaytastic.qss"))
    sudo_cp(
        stage / "colors" / "Swaytastic.conf",
        Path("/usr/share/qt6ct/colors/Swaytastic.conf"),
    )
    if not skip_icons and (stage / "icons" / "Swaytastic").is_dir():
        run(["sudo", "rm", "-rf", "/usr/share/icons/Swaytastic"])
        sudo_cp(stage / "icons" / "Swaytastic", Path("/usr/share/icons/"))
        run(["sudo", "gtk-update-icon-cache", "-f", "/usr/share/icons/Swaytastic"])
    else:
        folders = stage / "icons" / "Swaytastic"
        write_folder_glyphs(pack, folders)
        live = Path("/usr/share/icons/Swaytastic")
        for ctx in ("places", "mimetypes"):
            src = folders / "scalable" / ctx
            dst = live / "scalable" / ctx
            for name in ("folder.svg", "folder-open.svg", "inode-directory.svg"):
                sudo_cp(src / name, dst / name)
        run(["sudo", "gtk-update-icon-cache", "-f", str(live)])

    home = Path(os.environ.get("HOME", str(Path.home())))
    cfg = home / ".config"
    cfg.mkdir(parents=True, exist_ok=True)
    shutil.copy2(stage / "kdeglobals", cfg / "kdeglobals")
    waybar = cfg / "waybar" / "style.css"
    if waybar.parent.is_dir() or waybar.exists():
        waybar.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(stage / "waybar.css", waybar)
    patch_foot(cfg / "foot" / "foot.ini", pack)
    patch_pcmanfm(cfg / "pcmanfm-qt" / "sway" / "settings.conf", pack)
    mark = cfg / "swaytastic"
    mark.mkdir(parents=True, exist_ok=True)
    (mark / "pack").write_text(pack["name"] + "\n", encoding="utf-8")


def install_repo(stage: Path, pack: dict[str, str], repo: Path, *, skip_icons: bool) -> None:
    shutil.copytree(
        stage / "themes" / "Swaytastic",
        repo / "local" / "themes" / "Swaytastic",
        dirs_exist_ok=True,
    )
    (repo / "local" / "qss").mkdir(parents=True, exist_ok=True)
    (repo / "local" / "colors").mkdir(parents=True, exist_ok=True)
    shutil.copy2(stage / "qss" / "Swaytastic.qss", repo / "local" / "qss" / "Swaytastic.qss")
    shutil.copy2(
        stage / "colors" / "Swaytastic.conf",
        repo / "local" / "colors" / "Swaytastic.conf",
    )
    shutil.copy2(stage / "kdeglobals", repo / "config" / "kdeglobals")
    shutil.copy2(stage / "waybar.css", repo / "host" / "waybar" / "style.css")
    shutil.copy2(stage / "waybar.css", repo / "guest" / "waybar" / "style.css")
    patch_foot(repo / "config" / "foot" / "foot.ini", pack)
    patch_pcmanfm(repo / "config" / "pcmanfm-qt" / "sway" / "settings.conf", pack)
    (repo / "local" / "active-pack").write_text(pack["name"] + "\n", encoding="utf-8")
    if not skip_icons and (stage / "icons" / "Swaytastic").is_dir():
        dest = repo / "local" / "icons" / "Swaytastic"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(stage / "icons" / "Swaytastic", dest)


def reload_session(pack: dict[str, str] | None = None) -> None:
    # Kill pcmanfm before rewriting its settings: it saves FgColor on exit.
    # sway reload restarts waybar (bar { swaybar_command waybar }).
    subprocess.run(
        ["killall", "pcmanfm-qt"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if pack is not None:
        home = Path(os.environ.get("HOME", str(Path.home())))
        patch_pcmanfm(home / ".config" / "pcmanfm-qt" / "sway" / "settings.conf", pack)
    subprocess.run(
        ["swaymsg", "reload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.Popen(
        ["pcmanfm-qt", "--desktop", "--profile=sway"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def list_packs() -> None:
    names = [p.stem for p in sorted(PACKS.glob("*.conf"))]
    active = ""
    for marker in (HERE / "active-pack", Path.home() / ".config" / "swaytastic" / "pack"):
        if marker.is_file():
            active = marker.read_text(encoding="utf-8").strip()
            break
    for name in names:
        mark = " *" if name == active else ""
        print(f"{name}{mark}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Swaytastic pack")
    parser.add_argument("pack", nargs="?", help="pack name (see local/packs/)")
    parser.add_argument("--list", action="store_true", help="list packs")
    parser.add_argument("--dest", type=Path, help="staging directory")
    parser.add_argument("--live", action="store_true", help="install to /usr/share and ~/.config")
    parser.add_argument("--repo", action="store_true", help="write generated files into the repo")
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root")
    parser.add_argument("--skip-icons", action="store_true")
    parser.add_argument("--reload", action="store_true", help="reload sway/waybar/pcmanfm-qt")
    args = parser.parse_args()

    if args.list or not args.pack:
        list_packs()
        if not args.pack:
            return

    pack = load_pack(args.pack)
    keep_dest = args.dest is not None
    dest = args.dest.resolve() if args.dest else Path(tempfile.mkdtemp(prefix="swaytastic-pack-"))
    dest.mkdir(parents=True, exist_ok=True)
    print(f"building {pack['name']} -> {dest}", file=sys.stderr)
    write_theme_tree(pack, dest)
    if not args.skip_icons:
        print("recoloring icons (Adwaita SVG)", file=sys.stderr)
        build_icons(pack, dest / "icons" / "Swaytastic")
    if args.live:
        install_live(dest, pack, skip_icons=args.skip_icons)
        print("installed live", file=sys.stderr)
    if args.repo:
        install_repo(dest, pack, args.root.resolve(), skip_icons=args.skip_icons)
        print(f"updated repo {args.root}", file=sys.stderr)
    if args.reload:
        reload_session(pack)
        print("reloaded session", file=sys.stderr)
    if not keep_dest and not args.live and not args.repo:
        print(dest)
    elif not keep_dest:
        shutil.rmtree(dest, ignore_errors=True)


if __name__ == "__main__":
    main()
