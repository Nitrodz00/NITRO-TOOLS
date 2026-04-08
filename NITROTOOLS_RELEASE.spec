# -*- mode: python ; coding: utf-8 -*-
# NITROTOOLS PUBG MOBILE - Build Specification
# Version: v3.1.6
# Author: Nitrodz00s
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

_exe_basename = os.environ.get("PYINSTALLER_EXE_NAME", "NITROTOOLS_PUBG_MOBILE_v3.1.6")

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
    'keyboard',
    'numpy',
    'scipy',
    'sklearn',
    'src.ui_images.resources_rc',
    'src',
    'src.ui_functions',
    'src.core',
    'src.core.optimizer',
    'src.core.watcher',
    'src.core.monitor',
    'src.core.ai_engine',
    'src.core.expert_mode',
    'src.core.cache_manager',
    'src.core.compatibility_manager',
    'src.update',
    'src.auto_updater',
    'src.update_script',
    'src.gfx',
    'src.other',
    'src.system',
    'src.ui',
    'src.ui_expert',
    'src.app_functions',
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
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'tkinter',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)

numpy_ret = collect_all('numpy')
datas += numpy_ret[0]
binaries += numpy_ret[1]
hiddenimports += numpy_ret[2]

scipy_ret = collect_all('scipy')
datas += scipy_ret[0]
binaries += scipy_ret[1]
hiddenimports += scipy_ret[2]

sklearn_ret = collect_all('sklearn')
datas += sklearn_ret[0]
binaries += sklearn_ret[1]
hiddenimports += sklearn_ret[2]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=_exe_basename,
)
