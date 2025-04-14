# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import pathlib
import PyInstaller.config

# Try to locate whisper assets
try:
    import whisper
    whisper_dir = os.path.dirname(whisper.__file__)
    whisper_assets = os.path.join(whisper_dir, 'assets')
    print(f"Found whisper assets at: {whisper_assets}")
    whisper_assets_data = [(whisper_assets, 'whisper/assets')]
except ImportError:
    print("WARNING: Could not import whisper package to locate assets")
    whisper_assets_data = []

a = Analysis(
    ['src\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')] + whisper_assets_data,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'torch',
        'whisper',
        'whisper.tokenizer',
        'whisper.audio',
        'whisper.model',
        'whisper.utils',
        'whisper.transcribe',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Whisper Transcriber',
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
)
