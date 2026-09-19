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
  brightnessctl
  wlsunset
  wofi
  xdg-user-dirs
  pulseaudio-utils
  oxygencursors
  libqt6svg6
  qt6-svg-plugins
  librsvg2-common
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
  python3
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
sudo apt install -y --no-install-recommends "${PACKAGES[@]}"

echo "Install Brave Origin Nightly"
if command -v brave-origin-nightly >/dev/null 2>&1; then
  echo "    already installed"
else
  curl -fsS https://dl.brave.com/install.sh | FLAVOR=origin CHANNEL=nightly sh
fi

bash "$SRC/local/install-meslo.sh"

cp $SRC/zshrc $HOME/.zshrc
cp $SRC/p10k.zsh $HOME/.p10k.zsh
cp $SRC/zprofile $HOME/.zprofile

cp -a $SRC/config/* $HOME/.config/
cp -a $SRC/host/sway $HOME/.config/
cp -a $SRC/host/waybar $HOME/.config/
mkdir -p "$HOME/.local/bin"
install -m 755 "$SRC/local/switch_theme" "$HOME/.local/bin/switch_theme"

PACKS=("$SRC"/local/packs/*.conf)
DEFAULT_PACK=Pink_Techno_Syrup
if [[ -f $SRC/local/active-pack ]]; then
  DEFAULT_PACK=$(tr -d '[:space:]' < "$SRC/local/active-pack")
fi
PACK="$DEFAULT_PACK"
if [[ -t 0 ]]; then
  echo "Theme packs:"
  i=1
  DEFAULT_I=1
  for p in "${PACKS[@]}"; do
    n=$(basename "$p" .conf)
    echo "  $i) $n"
    if [[ $n == "$DEFAULT_PACK" ]]; then
      DEFAULT_I=$i
    fi
    i=$((i + 1))
  done
  read -r -p "Select pack [$DEFAULT_I=$DEFAULT_PACK]: " choice
  choice=${choice:-$DEFAULT_I}
  PACK=$(basename "${PACKS[choice-1]}" .conf)
fi
echo "applying pack $PACK"
python3 "$SRC/local/apply-pack.py" "$PACK" --live --repo --root "$SRC"

xdg-mime default thunar.desktop inode/directory
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >> ~/.zshrc

echo
echo 'done. log back in on tty1'
echo 'change look later with: switch_theme'
