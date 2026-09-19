#!/bin/sh
# Point GNOME/GTK settings at the Swaytastic theme. Portals and many menus
# read this instead of $HOME/.config/gtk-3.0/settings.ini.
set -e
gsettings set org.gnome.desktop.interface gtk-theme Swaytastic 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme Swaytastic 2>/dev/null || true
gsettings set org.gnome.desktop.interface color-scheme prefer-dark 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-theme oxy-red-argentina 2>/dev/null || true
gsettings set org.gnome.desktop.interface gtk-application-prefer-dark-theme true 2>/dev/null || true
