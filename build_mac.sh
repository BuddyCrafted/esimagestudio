#!/usr/bin/env bash
# ================================================================
#  ES Image Studio — Mac Build Script
#  Produces: dist/ES Image Studios.app
#            ES_Image_Studio.dmg  (drag-to-Applications installer)
#
#  Run this ON A MAC:
#    chmod +x build_mac.sh && ./build_mac.sh
# ================================================================
set -e

CYN='\033[0;36m'; GRN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info() { echo -e "${CYN}  $*${NC}"; }
ok()   { echo -e "${GRN}  ✓ $*${NC}"; }
fail() { echo -e "${RED}  ✗ $*${NC}"; exit 1; }

echo ""
echo "  ======================================================"
echo "   Eastern Studios  |  ES Image Studio  |  Mac Build"
echo "  ======================================================"
echo ""

command -v python3 &>/dev/null || fail "Python 3 not found. Install from python.org"
info "Python: $(python3 --version)"

info "[1/4] Installing dependencies..."
pip3 install -r desktop_requirements.txt -q || fail "pip install failed"
ok "Dependencies ready"

info "[2/4] Downloading AI model (~500 MB, first time only)..."
python3 -c "from rembg import new_session; new_session('birefnet-general'); print('  cached.')"

info "[3/4] Bundling with PyInstaller..."
pyinstaller es_image_studio.spec --noconfirm
ok "App bundle: dist/ES Image Studios.app"

info "[4/4] Creating DMG installer..."
DMG="ES_Image_Studio_Mac.dmg"
rm -f "$DMG"

# Use hdiutil (built into macOS — no extra install needed)
TMP_DMG="tmp_dmg_folder"
rm -rf "$TMP_DMG" && mkdir "$TMP_DMG"
cp -r "dist/ES Image Studios.app" "$TMP_DMG/"
ln -s /Applications "$TMP_DMG/Applications"   # drag-to-install shortcut

hdiutil create \
    -volname "ES Image Studio" \
    -srcfolder "$TMP_DMG" \
    -ov -format UDZO \
    "$DMG"

rm -rf "$TMP_DMG"
ok "DMG created: $DMG"

echo ""
echo "  +--------------------------------------------------+"
echo "  |  Installer :  ES_Image_Studio_Mac.dmg            |"
echo "  |  App bundle:  dist/ES Image Studios.app          |"
echo "  +--------------------------------------------------+"
echo ""
echo "  NOTE: Mac Gatekeeper will warn about unverified apps."
echo "  Testers: right-click the app → Open → Open anyway."
echo ""
