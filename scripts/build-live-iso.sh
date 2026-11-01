#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Error: this build step must be run as root or with sudo. Example: sudo ./scripts/build-live-iso.sh" >&2
  exit 1
fi

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
WORK_DIR=""
ISO_OUTPUT_NAME="${AETHER_ISO_OUTPUT_NAME:-}"
AETHER_WGETRC_HOST=""

mkdir -p "${BUILD_DIR}/logs"

if [ -n "${ISO_OUTPUT_NAME}" ]; then
  if [[ ! "${ISO_OUTPUT_NAME}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*\.iso$ ]]; then
    echo "Error: AETHER_ISO_OUTPUT_NAME must be a simple .iso filename." >&2
    exit 1
  fi
  if [ -e "${BUILD_DIR}/${ISO_OUTPUT_NAME}" ]; then
    echo "Error: refusing to overwrite existing ISO: ${BUILD_DIR}/${ISO_OUTPUT_NAME}" >&2
    exit 1
  fi
fi

if ! command -v mktemp >/dev/null 2>&1; then
  echo "Error: mktemp is required to create a build path without spaces." >&2
  exit 1
fi

if ! command -v lb >/dev/null 2>&1; then
  echo "Error: live-build (lb) is not installed. Run scripts/bootstrap-wsl-build.sh first." >&2
  exit 1
fi

if [ ! -f "${BUILD_DIR}/auto/config" ]; then
  echo "Error: ${BUILD_DIR}/auto/config is missing. Regenerate the live-build config first." >&2
  exit 1
fi

WORK_DIR="$(mktemp -d /var/tmp/aether-os-build.XXXXXX)"
cleanup() {
  case "${WORK_DIR}" in
    /var/tmp/aether-os-build.*)
      for mount_point in dev/pts proc sys; do
        if mountpoint -q "${WORK_DIR}/chroot/${mount_point}" 2>/dev/null; then
          umount -l -- "${WORK_DIR}/chroot/${mount_point}" || true
        fi
      done
      rm -rf -- "${WORK_DIR}"
      ;;
    "") ;;
    *)
      echo "Error: refusing to remove unexpected build directory: ${WORK_DIR}" >&2
      return 1
      ;;
  esac
  if [ -n "${AETHER_WGETRC_HOST}" ]; then
    rm -f -- "${AETHER_WGETRC_HOST}"
  fi
}
trap cleanup EXIT

for source_dir in auto config hooks local; do
  if [ -d "${BUILD_DIR}/${source_dir}" ]; then
    cp -a "${BUILD_DIR}/${source_dir}" "${WORK_DIR}/"
  fi
done
GRAPHICAL_VT_SERVICE="${WORK_DIR}/config/includes.chroot/etc/systemd/system/aether-activate-graphical-vt.service"
if [ -f "${GRAPHICAL_VT_SERVICE}" ]; then
  chmod 0644 "${GRAPHICAL_VT_SERVICE}"
  # Enable the unit exactly as "systemctl enable" would. The symlink is created
  # here rather than stored in the repository because git cannot represent it
  # on every development platform.
  GRAPHICAL_VT_WANTS="${WORK_DIR}/config/includes.chroot/etc/systemd/system/graphical.target.wants"
  mkdir -p "${GRAPHICAL_VT_WANTS}"
  ln -sfn ../aether-activate-graphical-vt.service \
    "${GRAPHICAL_VT_WANTS}/aether-activate-graphical-vt.service"
fi
AETHER_PANEL_SEED_SCRIPT="${WORK_DIR}/config/includes.chroot/usr/local/sbin/aether-seed-plasma-panel"
if [ -f "${AETHER_PANEL_SEED_SCRIPT}" ]; then
  chmod 0755 "${AETHER_PANEL_SEED_SCRIPT}"
fi
AETHER_WALLPAPER_SCRIPT="${WORK_DIR}/config/includes.chroot/usr/local/bin/aether-set-default-wallpaper"
if [ -f "${AETHER_WALLPAPER_SCRIPT}" ]; then
  chmod 0755 "${AETHER_WALLPAPER_SCRIPT}"
fi
AETHER_WELCOME_APP="${WORK_DIR}/config/includes.chroot/usr/bin/aether-welcome"
if [ -f "${AETHER_WELCOME_APP}" ]; then
  sed -i 's/\r$//' "${AETHER_WELCOME_APP}"
  chmod 0755 "${AETHER_WELCOME_APP}"
fi
if [ -d "${WORK_DIR}/config/hooks" ]; then
  find "${WORK_DIR}/config/hooks" -name '*.hook.chroot' -exec chmod 0755 {} +
fi
AETHER_DOCK_SOURCE="${BUILD_DIR}/../shell/aether-dock"
if [ ! -d "${AETHER_DOCK_SOURCE}" ]; then
  echo "Error: Aether Dock source is missing: ${AETHER_DOCK_SOURCE}" >&2
  exit 1
fi
AETHER_DOCK_TARGET="${WORK_DIR}/config/includes.chroot/usr/share/plasma/plasmoids/org.aether.shell.dock"
mkdir -p "${AETHER_DOCK_TARGET}"
cp -a "${AETHER_DOCK_SOURCE}/." "${AETHER_DOCK_TARGET}/"
AETHER_WALLPAPER_SOURCE="${BUILD_DIR}/../wallpapers/default_wallpaper.png"
if [ ! -f "${AETHER_WALLPAPER_SOURCE}" ]; then
  echo "Error: Aether wallpaper source is missing: ${AETHER_WALLPAPER_SOURCE}" >&2
  exit 1
fi
AETHER_WALLPAPER_TARGET="${WORK_DIR}/config/includes.chroot/usr/share/wallpapers/Aether/contents/images"
mkdir -p "${AETHER_WALLPAPER_TARGET}"
install -m 0644 "${AETHER_WALLPAPER_SOURCE}" "${AETHER_WALLPAPER_TARGET}/2560x1600.png"
cd "${WORK_DIR}"
lb clean
AETHER_WGETRC_SOURCE="${BUILD_DIR}/aether-build-wgetrc"
AETHER_WGETRC_HOOK="${WORK_DIR}/config/hooks/normal/9990-remove-aether-build-wgetrc.hook.chroot"
if [ -f "${AETHER_WGETRC_SOURCE}" ] && [ -f "${AETHER_WGETRC_HOOK}" ]; then
  AETHER_WGETRC_HOST="$(mktemp /tmp/aether-build-wgetrc.XXXXXX)"
  chmod 0600 "${AETHER_WGETRC_HOST}"
  cat "${AETHER_WGETRC_SOURCE}" > "${AETHER_WGETRC_HOST}"
  AETHER_WGETRC_CHROOT="${WORK_DIR}/config/includes.chroot_before_packages/root/.wgetrc"
  mkdir -p "$(dirname -- "${AETHER_WGETRC_CHROOT}")"
  install -m 0644 "${AETHER_WGETRC_HOST}" "${AETHER_WGETRC_CHROOT}"
  sed -i "s|@AETHER_WGETRC_PATH@|${AETHER_WGETRC_HOST}|g" "${AETHER_WGETRC_HOOK}"
  sed -i 's/\r$//' "${AETHER_WGETRC_HOOK}"
  chmod 0755 "${AETHER_WGETRC_HOOK}"
  WGETRC="${AETHER_WGETRC_HOST}" lb build 2>&1 | tee "${BUILD_DIR}/logs/lb-build.log"
else
  echo "Error: temporary wget configuration or cleanup hook is missing." >&2
  exit 1
fi

shopt -s nullglob
ISO_FILES=("${WORK_DIR}"/*.iso)
shopt -u nullglob
if [ "${#ISO_FILES[@]}" -eq 0 ]; then
  echo "Error: live-build completed without producing an ISO image. See ${BUILD_DIR}/logs/lb-build.log." >&2
  exit 1
fi

if [ -n "${ISO_OUTPUT_NAME}" ] && [ "${#ISO_FILES[@]}" -ne 1 ]; then
  echo "Error: custom ISO naming requires exactly one ISO build output." >&2
  exit 1
fi

for iso in "${ISO_FILES[@]}"; do
  if [ -n "${ISO_OUTPUT_NAME}" ]; then
    OUTPUT_ISO="${BUILD_DIR}/${ISO_OUTPUT_NAME}"
  else
    OUTPUT_ISO="${BUILD_DIR}/$(basename -- "${iso}")"
  fi
  cp -v -- "${iso}" "${OUTPUT_ISO}"
  OUTPUT_ISO_NAME="$(basename -- "${OUTPUT_ISO}")"
  (
    cd "${BUILD_DIR}"
    sha256sum -- "${OUTPUT_ISO_NAME}" > "${OUTPUT_ISO_NAME}.sha256"
  )
done

echo "live-build completed. ISO artifacts are in ${BUILD_DIR}."
