# Swaytastic

High-contrast Sway theme kit for those with light-sensitive eyes.
Currently supports debian. will be adding support for more distros soon.

Color looks live in `local/packs/` (`Pink_Techno_Syrup`, `Dirty_Crayon`). `install.sh` prompts which pack to apply and installs `switch_theme` to `~/.local/bin`. The installed GTK/icon/qt name stays `Swaytastic`. Later, run `switch_theme` (menu) or `switch_theme Dirty_Crayon`. To add a look, copy a pack conf and run `switch_theme`.
  
## Install (Debian).
  
[Host]:

```bash
git clone https://github.com/backdoorsecurity/Swaytastic.git
cd Swaytastic/host
./install.sh
```
  
[Guest vm]:

```bash
git clone https://github.com/backdoorsecurity/Swaytastic.git
cd Swaytastic/guest
./install.sh
```

Then log in on tty1.  
  
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
