# Swaytastic

High-contrast Sway theme kit for those with light-sensitive eyes.
Currently supports debian. will be adding support for more distros soon.

Change hex color values in `config/sway/color_schemes/` and keep the same values in `local/share/themes/Swaytastic`, `config/qt6ct/` (`colors/Swaytastic.conf`, `qss/Swaytastic.qss`), and the icon SVGs. Re-run `install.sh` to push those files into `/usr/share`.

## Install (Debian).

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

Then log in on tty1 (or `set -a; . $HOME/.config/sway/env; set +a; exec sway`).  
  
Session env sets `GTK_THEME=Swaytastic` and `QT_QPA_PLATFORMTHEME=qt6ct` (Fusion + `/usr/share/qt6ct/colors/Swaytastic.conf`). Debian’s default gsettings theme is often HighContrastInverse; `install.sh` and sway startup run `apply-gtk-interface.sh` so menus follow Swaytastic.  
  
No Xwayland/X11.  

## Layout

  
## keymap
[host]  
alt + asdfg == workspace 1,2,3,4,5  
alt + q = brave-origin-nightly  
alt + w,e,r = foot  
alt + t = virt-manager  

[guest]  
alt + asdfg == workspace 1,2,3,4,5  
alt + q = brave-origin-nightly  
alt + w,e,r,t = foot  

[global]  
alt + j,k = switch focus between tiled apps  
alt + i = toggle fullscreen  
alt + c = copy  
alt + v = paste  
alt + x = kill window  
alt + shift + r = reload sway config  
  
- more hotkeys defined in config/sway/config
