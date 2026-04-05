# -*- mode: python ; coding: utf-8 -*-
# Single-file release build: pyinstaller NITROTOOLS_RELEASE.spec
# Optional: set PYINSTALLER_EXE_NAME (e.g. NITROTOOLS_PUBG_MOBILE_v2.1.3) for CI/local builds
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

_exe_basename = os.environ.get("PYINSTALLER_EXE_NAME", "NITROTOOLS_PUBG_MOBILE_v2.1.3")

datas = [('assets', 'assets')]
binaries = []
hiddenimports = [
    'pythoncom',
    'pywintypes',
    'win32api',
    'win32com',
    'win32com.client',
    'wmi',
    'GPUtil',
    'ping3',
    'adbutils',
    'psutil',
    'requests',
    'winshell',
    'src.ui_images.resources_rc',
    'PIL',
    'PIL.Image',
    'pkg_resources',
    'setuptools',
]

datas += copy_metadata('setuptools')

adb_ret = collect_all('adbutils')
datas += adb_ret[0]
binaries += adb_ret[1]
hiddenimports += adb_ret[2]

# adbutils._utils uses pkg_resources.resource_filename (setuptools)
st_ret = collect_all('setuptools')
datas += st_ret[0]
binaries += st_ret[1]
hiddenimports += st_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=_exe_basename,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\logo.ico'],
)
