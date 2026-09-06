# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, copy_metadata

datas = [("klassen_klo_app.py", ".")]
binaries = []
hiddenimports = []

for paket in ("streamlit",):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(paket)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

for paket in ("streamlit", "pandas", "click", "importlib_metadata"):
    try:
        datas += copy_metadata(paket)
    except Exception:
        pass

a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["cryptography"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="KlassenKloTerminal",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
