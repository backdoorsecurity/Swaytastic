#!/bin/bash
SRC="$HOME/Swaytastic"

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
  zsh
  zsh-autosuggestions
  zsh-syntax-highlighting
  spice-client-gtk
  copyq
  wf-recorder
  wtype
  zram-tools
  sudo
  git
  curl
  rsync
  unzip
  zip
  tree
  socat
  nmap
  traceroute
  netcat-traditional
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
  slurp
  wl-clipboard
  bubblewrap
  wget
  nvtop
  sshpass
  gawk
  bc
  lz4
  libarchive-tools
  cmake
  python3-pip
  python3-venv
  autoconf
  automake
  libtool
  gettext
  fakeroot
  bison
  flex
  dwarves
  pahole
  wayland-protocols
)

echo "installing packages"
sudo apt update
sudo apt install -y --no-install-recommends "${PACKAGES[@]}"

echo "Install Brave Origin Nightly"
if command -v brave-origin-nightly >/dev/null 2>&1; then
  echo "    already installed"
else
  curl -fsS https://dl.brave.com/install.sh | FLAVOR=origin CHANNEL=nightly sh
fi

cp $SRC/zshrc $HOME/.zshrc
cp $SRC/zprofile $HOME/.zprofile

cp -a $SRC/config/* $HOME/.config/
cp -a $SRC/guest/sway $HOME/.config/
cp -a $SRC/guest/waybar $HOME/.config/

sudo cp -a $SRC/local/themes/Swaytastic /usr/share/themes/
sudo cp -a $SRC/local/icons/Swaytastic /usr/share/icons/
sudo cp -a $SRC/local/qss/Swaytastic.qss /usr/share/qt6ct/qss/
sudo cp -a $SRC/local/colors/Swaytastic.conf /usr/share/qt6ct/colors/

sudo gtk-update-icon-cache -f /usr/share/icons/Swaytastic
xdg-mime default thunar.desktop inode/directory

echo
echo 'done. log back in on tty1'
