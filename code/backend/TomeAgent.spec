# Run build-windows.cmd; generated files stay inside the existing backend/data directory.
from pathlib import Path

backend = Path(SPECPATH)
project = backend.parents[1]
core = project / 'code' / 'core_engine'
a = Analysis(
    [str(backend / 'desktop.py')],
    pathex=[str(backend), str(core)],
    binaries=[],
    datas=[(str(project / 'code' / 'frontend' / name), 'frontend')
           for name in ('index.html', 'app.js', 'style.css', 'vue-components.js', 'vue.runtime.global.prod.js', 'vue.LICENSE.txt')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'unittest', 'pip', 'setuptools'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='TomeAgent',
          debug=False, bootloader_ignore_signals=False, strip=False,
          upx=False, console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='TomeAgent')
