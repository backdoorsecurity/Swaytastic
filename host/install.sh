#!/bin/bash
# Install Swaytastic host tree onto this user: packages + $HOME/.config + session hooks.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${XDG_CONFIG_HOME:-$HOME/.config}"

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
  sudo
  git
  curl
  rsync
  unzip
  zip
  tree
  socat
  nmap
  openssh-client
  traceroute
  pciutils
  usbutils
  locate
  wireless-tools
  wpasupplicant
  build-essential
  meson
  ninja-build
  pkgconf
  ccache
  live-build
  simple-cdd
  cdebootstrap
  intel-microcode
  cryptsetup-initramfs
  xfsprogs
  dosfstools
)

need_sudo() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

echo "==> installing packages (no recommends)"
need_sudo apt-get update -qq
if ! need_sudo apt-get install -y --no-install-recommends "${PACKAGES[@]}"; then
  echo "==> batch install missed a package; installing one by one"
  for pkg in "${PACKAGES[@]}"; do
    need_sudo apt-get install -y --no-install-recommends "$pkg" || true
  done
fi

# optional layer-shell helper for pcmanfm-qt desktop menus
need_sudo apt-get install -y --no-install-recommends layer-shell-qt6 2>/dev/null \
  || need_sudo apt-get install -y --no-install-recommends layer-shell-qt 2>/dev/null \
  || true

echo "==> Brave Origin Nightly (not in Debian)"
if command -v brave-origin-nightly >/dev/null 2>&1; then
  echo "    already installed"
else
  curl -fsS https://dl.brave.com/install.sh | FLAVOR=origin CHANNEL=nightly sh
fi

# older host installs pulled qt5ct only for Brave QT; that stack is unused now
echo "==> dropping leftover Qt5 (Brave QT is Qt6 + qt6ct)"
need_sudo apt-get purge -y qt5ct libqt5ct-common1.8 qtwayland5 qt5-gtk-platformtheme 2>/dev/null || true
need_sudo apt-get autoremove -y --purge 2>/dev/null || true

copy_tree() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  if command -v rsync >/dev/null; then
    rsync -a "$src"/ "$dest"/
  else
    cp -a "$src"/. "$dest"/
  fi
}

echo "==> copying config -> $DEST"
mkdir -p "$DEST"
if command -v rsync >/dev/null; then
  rsync -a --exclude 'qt6ct/colors/' --exclude 'qt6ct/qss/' "$SRC/config"/ "$DEST"/
else
  copy_tree "$SRC/config" "$DEST"
fi
echo '==> copying home files (zshrc -> $HOME/.zshrc, …)'
for item in "$SRC"/*; do
  [[ -f "$item" ]] || continue
  base="$(basename "$item")"
  case "$base" in
    install.sh|README.md) continue ;;
  esac
  cp -a "$item" "$HOME/.$base"
done

chmod +x "$DEST/sway/env-exec"
chmod +x "$DEST/sway/scripts/"* 2>/dev/null || true

echo "==> rewriting machine-local paths"
if [[ -f "$DEST/user-dirs.dirs" ]]; then
  sed -i 's|^XDG_DESKTOP_DIR=.*|XDG_DESKTOP_DIR="$HOME"|' "$DEST/user-dirs.dirs"
fi

echo "==> Swaytastic GTK / icon / qt6ct packs -> /usr/share"
ln -sfn "$DEST/sway/color_schemes/waybar.css" "$DEST/waybar/style.css"

install_named_theme() {
  local gtk_src="$SRC/local/share/themes/Swaytastic"
  local icon_src="$DEST/sway/color_schemes/icons"
  local qt_colors="$SRC/config/qt6ct/colors/Swaytastic.conf"
  local qt_qss="$SRC/config/qt6ct/qss/Swaytastic.qss"

  need_sudo mkdir -p /usr/share/themes/Swaytastic /usr/share/icons/Swaytastic \
    /usr/share/qt6ct/colors /usr/share/qt6ct/qss
  if command -v rsync >/dev/null; then
    need_sudo rsync -a "$gtk_src"/ /usr/share/themes/Swaytastic/
    need_sudo rsync -a "$icon_src"/ /usr/share/icons/Swaytastic/
  else
    need_sudo cp -a "$gtk_src"/. /usr/share/themes/Swaytastic/
    need_sudo cp -a "$icon_src"/. /usr/share/icons/Swaytastic/
  fi
  need_sudo cp -a "$qt_colors" /usr/share/qt6ct/colors/Swaytastic.conf
  need_sudo cp -a "$qt_qss" /usr/share/qt6ct/qss/Swaytastic.qss
  if command -v gtk-update-icon-cache >/dev/null; then
    need_sudo gtk-update-icon-cache -f /usr/share/icons/Swaytastic 2>/dev/null || true
  fi
}
install_named_theme

if command -v xdg-mime >/dev/null && [[ -f /usr/share/applications/thunar.desktop ]]; then
  xdg-mime default thunar.desktop inode/directory
fi

hook_login() {
  local file="$1"
  local marker='# Swaytastic: start sway on tty1'
  mkdir -p "$(dirname "$file")"
  if [[ -f "$file" ]] && grep -qF "$marker" "$file"; then
    return
  fi
  if [[ -f "$file" ]] && grep -q 'exec sway' "$file"; then
    return
  fi
  {
    echo
    echo "$marker"
    echo 'if [ "$(tty)" = "/dev/tty1" ]; then'
    echo '	set -a'
    echo '	# shellcheck disable=SC1091'
    echo '	. "$HOME/.config/sway/env"'
    echo '	set +a'
    echo '	exec sway'
    echo 'fi'
  } >> "$file"
}

echo '==> login hook (.profile; zsh uses $HOME/.zprofile from this tree)'
hook_login "$HOME/.profile"

echo "==> GNOME/GTK interface (menus, portals)"
if [[ -x "$DEST/sway/scripts/apply-gtk-interface.sh" ]]; then
  "$DEST/sway/scripts/apply-gtk-interface.sh" || true
fi

echo
echo 'done. log in on tty1 (or: set -a; . $HOME/.config/sway/env; set +a; exec sway)'
echo "GTK/icon/qt6ct live under /usr/share: themes/Swaytastic  icons/Swaytastic  qt6ct/colors+qss"
echo "Qt6: QT_QPA_PLATFORMTHEME=qt6ct, /usr/share/qt6ct colors+qss Swaytastic. Brave QT: --qt-version=6 + qt6ct."
