#!/bin/bash
SRC="$HOME/Swaytastic/host"

PACKAGES=(
  sway
  foot
  waybar
  pcmanfm-qt
  qt6ct
  thunar
  gvfs
  gvfs-backends
  adwaita-icon-theme
  grim
  brightnessctl
  wlsunset
  wofi
  xdg-user-dirs
  pulseaudio-utils
  oxygencursors
  libqt6svg6
  qt6-wayland
  qt6-qpa-plugins
  qt6-gtk-platformtheme
  lxmenu-data
  xdg-desktop-portal-wlr
  xdg-desktop-portal-gtk
  brightness-udev
  zsh
  zsh-autosuggestions
  zsh-syntax-highlighting
  spice-client-gtk
  copyq
  wf-recorder
  wtype
  zram-tools
  lm-sensors
  curl
  rsync
  unzip
  zip
  tree
  socat
  nmap
  traceroute
  pciutils
  usbutils
  locate
  build-essential
  meson
  ninja-build
  pkgconf
  ccache
  live-build
  simple-cdd
  cdebootstrap
  cryptsetup-initramfs
  xfsprogs
  dosfstools
  layer-shell-qt
)

echo "installing packages"
sudo apt update
sudo apt install -y --no-install-recommends "$PACKAGES"

echo "Install Brave Origin Nightly"
if command -v brave-origin-nightly >/dev/null 2>&1; then
  echo "    already installed"
else
  curl -fsS https://dl.brave.com/install.sh | FLAVOR=origin CHANNEL=nightly sh
fi

cp $SRC/zshrc $HOME/.zshrc
cp $SRC/zprofile $HOME/.zprofile

cp -a $SRC/config/* $HOME/.config/
sudo cp -a $SRC/local/themes/Swaytastic /usr/share/themes/
sudo cp -a $SRC/local/icons/Swaytastic /usr/share/icons/
sudo cp -a $SRC/local/qss/Swaytastic.qss /usr/share/qt6ct/qss/
sudo cp -a $SRC/local/colors/Swaytastic.conf /usr/share/qt6ct/colors/
ln -sfn $HOME/.config/sway/color_schemes/waybar.css $HOME/.config/waybar/style.css

sudo gtk-update-icon-cache -f /usr/share/icons/Swaytastic
xdg-mime default thunar.desktop inode/directory

echo
echo 'done. log in on tty1 (or: set -a; . $HOME/.config/sway/env; set +a; exec sway)'
