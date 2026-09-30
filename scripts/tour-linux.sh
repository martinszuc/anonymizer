#!/usr/bin/env bash
# Run the window tour inside a fresh Linux distribution, on a virtual display
# with a window manager and a panel, so the screenshots show a desktop's bars.
#
# Meant to run as root inside a container with the repository mounted as the
# working directory and the frontend already built:
#
#   docker run --rm -v "$PWD:/work" -w /work ubuntu:24.04 \
#       bash scripts/tour-linux.sh /work/tour-screenshots
#
# Packages come from the distribution's own repositories; Qt WebEngine (the
# window's browser engine on Linux here) comes from PyPI wheels.
set -euo pipefail

out_dir="${1:?usage: tour-linux.sh OUT_DIR}"
export CI=true

if command -v apt-get >/dev/null; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  # The ALSA library is named libasound2t64 on newer releases, libasound2 on older ones.
  alsa=libasound2t64
  apt-cache show "$alsa" >/dev/null 2>&1 || alsa=libasound2
  apt-get install -y -qq --no-install-recommends \
    ca-certificates curl xvfb xfwm4 xfce4-panel dbus-x11 fonts-dejavu-core \
    libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 \
    libxcb-xkb1 libnss3 libxcomposite1 libxdamage1 libxrandr2 libxtst6 libdbus-1-3 \
    libfontconfig1 libglib2.0-0 libsnappy1v5 "$alsa"
elif command -v dnf >/dev/null; then
  dnf install -y -q --setopt=install_weak_deps=False \
    ca-certificates curl xorg-x11-server-Xvfb xfwm4 xfce4-panel dbus-x11 dejavu-sans-fonts \
    mesa-libEGL mesa-libGL libxkbcommon-x11 xcb-util-cursor xcb-util-wm xcb-util-image \
    xcb-util-keysyms xcb-util-renderutil nss libXcomposite libXdamage libXrandr libXtst \
    alsa-lib fontconfig snappy
else
  echo "tour-linux.sh: no supported package manager (apt-get, dnf)" >&2
  exit 2
fi

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

export UV_PROJECT_ENVIRONMENT=/tmp/tour-venv
uv sync --locked --all-packages
uv pip install --quiet --python "$UV_PROJECT_ENVIRONMENT/bin/python" "pywebview[qt]"

export DISPLAY=:99
export QT_QPA_PLATFORM=xcb
# Running as root in a container: Chromium's sandbox cannot start, and there is no GPU.
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu"

Xvfb "$DISPLAY" -screen 0 1920x1080x24 -nolisten tcp &
for _ in $(seq 50); do
  [ -e /tmp/.X11-unix/X99 ] && break
  sleep 0.2
done

eval "$(dbus-launch --sh-syntax)"
xfwm4 --compositor=off &
xfce4-panel --disable-wm-check &
sleep 3

mkdir -p "$out_dir"
uv run --no-sync python scripts/ui_tour.py "$out_dir"
