# -*- mode: python ; coding: utf-8 -*-
# Single-file release build: pyinstaller NITROTOOLS_RELEASE.spec
from PyInstaller.utils.hooks import collect_all

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
]

adb_ret = collect_all('adbutils')
datas += adb_ret[0]
binaries += adb_ret[1]
hiddenimports += adb_ret[2]

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
        'PIL',
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
    name='NITROTOOLS_PUBG_MOBILE_v2.1.0',
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
