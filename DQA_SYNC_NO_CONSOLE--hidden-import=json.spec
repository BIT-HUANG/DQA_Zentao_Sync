# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DQA_SYNC.py'],
    pathex=[],
    binaries=[],
    datas=[('portal.py', '.'), ('service_manager.py', '.'), ('system_setting_ui.py', '.'), ('libmirror/mstr.py', '.'), ('libmirror/mconfig.py', '.'), ('libmirror/mio.py', '.'), ('libmirror/mlogger.py', '.'), ('libmirror/mpath.py', '.'), ('libmirror/mjira/const.py', 'mjira'), ('libmirror/mjira/field.py', 'mjira'), ('libmirror/mjira/issue.py', 'mjira'), ('libmirror/mjira/http.py', 'mjira'), ('libmirror/mjira/net_sony.py', 'mjira'), ('libmirror/mzentao/*.py', 'mzentao'), ('README.md', '.')],
    hiddenimports=['colorama', 'jira', 'translate', 'openpyxl', 'flask', 'flask.json', 'werkzeug', 'jinja2', 'werkzeug.serving', 'werkzeug._internal', 'click', 'ngrok', 'ngrok._ffi', 'ngrok._impl', 'ngrok.api', 'asyncio', 'threading', 'ctypes', 'psutil'],
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
    name='DQA_SYNC_NO_CONSOLE--hidden-import=json',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
