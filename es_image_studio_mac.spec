# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — ES Image Studio (Mac)
# Produces a proper .app bundle

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas_rembg,   binaries_rembg,   hiddenimports_rembg   = collect_all("rembg")
datas_onnx,    binaries_onnx,    hiddenimports_onnx    = collect_all("onnxruntime")
datas_webview, binaries_webview, hiddenimports_webview = collect_all("webview")

a = Analysis(
    ["desktop.py"],
    pathex=["."],
    binaries=binaries_rembg + binaries_onnx + binaries_webview,
    datas=datas_rembg + datas_onnx + datas_webview + [
        ("app.py", "."),
    ],
    hiddenimports=(
        hiddenimports_rembg
        + hiddenimports_onnx
        + hiddenimports_webview
        + collect_submodules("uvicorn")
        + collect_submodules("fastapi")
        + collect_submodules("PIL")
        + collect_submodules("starlette")
        + collect_submodules("pyobjc")
        + ["anyio", "anyio._backends._asyncio", "h11",
           "httptools", "python_multipart",
           "Foundation", "AppKit", "WebKit"]
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ES Image Studios",
    debug=False,
    strip=False,
    upx=False,        # UPX breaks Mac binaries
    console=False,
    icon="icon.icns", # converted from icon.ico during build
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="ES Image Studios",
)

# Mac-specific: wrap in a .app bundle
app = BUNDLE(
    coll,
    name="ES Image Studios.app",
    icon="icon.icns",
    bundle_identifier="com.easternstudios.imagestudio",
    info_plist={
        "CFBundleName": "ES Image Studios",
        "CFBundleDisplayName": "ES Image Studios",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "Copyright 2026 Eastern Studios",
        "LSUIElement": False,
    },
)
