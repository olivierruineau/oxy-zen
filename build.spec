# -*- mode: python ; coding: utf-8 -*-
"""
Configuration PyInstaller pour Oxy-Zen
Génère un exécutable Windows unique (.exe) sans dépendances externes
Usage: pyinstaller build.spec
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
from pathlib import Path

block_cipher = None

# Données à inclure dans l'exécutable
datas = [
    ('data/exercises.yaml', 'data'),  # Fichier YAML des exercices
]

# Imports cachés (modules non détectés automatiquement)
hiddenimports = [
    'pystray._win32',
    'PIL._tkinter_finder',
    'pkg_resources.extern',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OxyZen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compression UPX pour réduire la taille
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de fenêtre console (application GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Optionnel : ajouter un fichier .ico ici
    version_file=None,  # Optionnel : fichier de version Windows
)
