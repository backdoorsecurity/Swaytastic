# Swaytastic

High-contrast Sway kit for light-sensitive eyes. Dark near-black surfaces, green text, pink chrome (same pink as the waybar workspace buttons). The contrast is meant so the backlight can stay low without losing readability. The named toolkit theme is **Swaytastic** (GTK, icons, qt6ct). The repo folder stays `Swaytastic`.

Wayland only. Each machine tree is `config/` → `$HOME/.config` and remaining files at the tree root → `$HOME/.<name>` (`zshrc` → `$HOME/.zshrc`). `local/share/themes/Swaytastic` is GTK source in the repo only. The live **Swaytastic** GTK theme, icon theme, and qt6ct colors/qss are installed under `/usr/share`.

## Palette

| Role | Hex |
| --- | --- |
| background | `#100909` |
| text | `#99e01c` |
| accent / borders | `#de1062` |
| unfocused chrome | `#6f0831` |

Change hex in `config/sway/color_schemes/` and keep the same values in `local/share/themes/Swaytastic`, `config/qt6ct/` (`colors/Swaytastic.conf`, `qss/Swaytastic.qss`), and the icon SVGs. Re-run `install.sh` to push those files into `/usr/share`.

## Install (Debian/Kali)

**Host** (laptop):

```bash
git clone 
cd Swaytastic/host
./install.sh
```

**Guest** (VM):

```bash
git clone 
cd Swaytastic/guest
./install.sh
```

Then log in on **tty1** (or `set -a; . $HOME/.config/sway/env; set +a; exec sway`).

The script installs packages (`--no-install-recommends`), rsyncs `config/` into `$HOME/.config` (skipping `qt6ct/colors` and `qss`), copies root files to `$HOME/.<name>`, and installs the Swaytastic GTK/icon/qt6ct packs into `/usr/share`. `zprofile` starts Sway on tty1.

Session env sets `GTK_THEME=Swaytastic` and `QT_QPA_PLATFORMTHEME=qt6ct` (Fusion + `/usr/share/qt6ct/colors/Swaytastic.conf`). Debian’s default gsettings theme is often HighContrastInverse; `install.sh` and sway startup run `apply-gtk-interface.sh` so menus follow Swaytastic.

Brave Appearance **GTK+** uses the Swaytastic GTK theme. Appearance **QT** talks to Chromium’s Qt shim. On Sway that shim prefers Qt5, and `QT_QPA_PLATFORM=wayland` abort()s if `qtwayland5` is missing. Both trees stay Qt6-only: `sway/scripts/brave` passes `--qt-version=6` so QT uses the session **qt6ct** / Swaytastic pack. Relog on tty1 after install.

pcmanfm-qt is Qt6, so qt6ct is the session default.

Xwayland is not installed; configs do not toggle it.

Debian stable vs Kali: host is sway 1.10 / Qt 6.8 / pcmanfm-qt 2.1; guest is 1.12 / 6.10 / 2.4. Host floats `app_id=pcmanfm-qt` so Qt 6.8 menus are not tiled away.

## Layout

- **Sway** — `sway/config` includes `sway/variables` (`set $mod`, workspaces, cursor) and `sway/color_schemes/sway.conf`. Session toolkit env is `sway/env` (sourced before Sway; Sway cannot parse `KEY=value`).
- **Waybar** — five persistent workspaces. Host: brave, terminal, terminal, terminal, virt-manager. Guest: brave, terminal, terminal, terminal, terminal.
- **Pinned apps** — Brave always on workspace 1. Host also pins virt-manager to workspace 5. Foot is not assigned; open a terminal on whatever workspace you are on.
- **Foot** — matching colors, 2px window border from Sway
- **Desktop folders** — pcmanfm-qt layer-shell; icon theme `Swaytastic`. Desktop text/shadow/background in that GUI are pcmanfm-qt-only (`pcmanfm-qt/sway/settings.conf`); they do not drive Brave or the GTK/qt6ct palettes. Re-running `install.sh` resets those three colors to the pack defaults.
- **Qt6** — `qt6ct`, Fusion, color scheme `Swaytastic` from `/usr/share/qt6ct` (pcmanfm-qt, qt6ct, Brave QT via `--qt-version=6`)
- **GTK** — theme `Swaytastic` from `/usr/share/themes/Swaytastic` (not Adwaita-dark)
- **Icons** — theme `Swaytastic` from `/usr/share/icons/Swaytastic` (source SVGs live in `config/sway/color_schemes/icons`)

`$mod` is **Alt**. Colors are local; keep them in sync when you retint.
