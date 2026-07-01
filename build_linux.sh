#!/usr/bin/env bash
# ================================================================
#  ES Image Studio — Linux Build Script
#  Produces: dist/ES Image Studios (portable folder)
#            ES_Image_Studio.AppImage (single portable file)
#
#  Requirements: Python 3.10–3.13, pip, internet connection
#  Run: chmod +x build_linux.sh && ./build_linux.sh
# ================================================================
set -e
APP_NAME="ES Image Studios"
APP_ID="com.easternstudios.imagestudio"

RED='\033[0;31m'; GRN='\033[0;32m'; CYN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYN}  $*${NC}"; }
ok()    { echo -e "${GRN}  ✓ $*${NC}"; }
fail()  { echo -e "${RED}  ✗ $*${NC}"; exit 1; }

echo ""
echo "  ======================================================="
echo "   Eastern Studios  |  ES Image Studio  |  Linux Build"
echo "  ======================================================="
echo ""

# ── 1. Python check ──────────────────────────────────────────────────────────
command -v python3 &>/dev/null || fail "Python 3 not found. Install python3."
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PY_VER detected"

# ── 2. System libs (needed for Pillow / onnxruntime) ─────────────────────────
info "[1/5] Checking system libraries..."
if command -v apt-get &>/dev/null; then
    sudo apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libgtk-3-dev \
        python3-pip python3-venv \
        libwebkit2gtk-4.1-dev   2>/dev/null || true
fi
ok "System libs ready"

# ── 3. Python dependencies ────────────────────────────────────────────────────
info "[2/5] Installing Python dependencies..."
pip3 install -r desktop_requirements.txt -q || fail "pip install failed."
ok "Dependencies installed"

# ── 4. Download model ─────────────────────────────────────────────────────────
info "[3/5] Downloading BiRefNet AI model (first time only, ~500 MB)..."
python3 -c "
from rembg import new_session
new_session('birefnet-general')
print('  Model cached.')
" || fail "Model download failed. Check your internet connection."

# ── 5. PyInstaller ────────────────────────────────────────────────────────────
info "[4/5] Bundling with PyInstaller..."
pyinstaller es_image_studio.spec --noconfirm
ok "Bundle created: dist/${APP_NAME}/"

# ── 6. AppImage (optional — needs appimagetool) ───────────────────────────────
info "[5/5] Creating AppImage..."

APPDIR="AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy PyInstaller output into AppDir
cp -r "dist/${APP_NAME}/." "$APPDIR/usr/bin/"

# Copy icon
if [ -f "icon.ico" ]; then
    # Convert .ico to .png if ImageMagick is available
    if command -v convert &>/dev/null; then
        convert icon.ico -resize 256x256 "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png" 2>/dev/null || \
        cp icon.ico "$APPDIR/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"
    fi
fi

# .desktop file
cat > "$APPDIR/${APP_ID}.desktop" << DESKTOP
[Desktop Entry]
Name=ES Image Studio
Comment=AI-powered image background removal by Eastern Studios
Exec=ES Image Studios
Icon=${APP_ID}
Type=Application
Categories=Graphics;Photography;
Keywords=background;remove;AI;image;studio;
DESKTOP

# AppRun entry point
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF="$(readlink -f "$0")"
HERE="$(dirname "$SELF")"
exec "$HERE/usr/bin/ES Image Studios" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# Download appimagetool if not present
if ! command -v appimagetool &>/dev/null; then
    info "  Downloading appimagetool..."
    ARCH=$(uname -m)
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage" \
         -O appimagetool.AppImage 2>/dev/null || true
    chmod +x appimagetool.AppImage 2>/dev/null || true
    APPTOOL="./appimagetool.AppImage"
else
    APPTOOL="appimagetool"
fi

if [ -f "$APPTOOL" ] || command -v appimagetool &>/dev/null; then
    ARCH=x86_64 "$APPTOOL" "$APPDIR" "ES_Image_Studio.AppImage" 2>/dev/null && \
    ok "AppImage created: ES_Image_Studio.AppImage" || \
    echo "  (AppImage creation skipped — run manually if needed)"
else
    echo "  (appimagetool unavailable — AppImage not created)"
    echo "  Use the portable folder: dist/${APP_NAME}/"
fi

echo ""
echo "  +---------------------------------------------------------+"
echo "  |  Portable  : dist/${APP_NAME}/${APP_NAME}  |"
echo "  |  AppImage  : ES_Image_Studio.AppImage (if created)      |"
echo "  +---------------------------------------------------------+"
echo ""
echo "  Make portable executable runnable:"
echo "  chmod +x 'dist/${APP_NAME}/${APP_NAME}'"
echo ""
