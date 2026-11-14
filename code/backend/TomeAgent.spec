# Run build-windows.cmd; generated files stay inside the existing backend/data directory.
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata

backend = Path(SPECPATH)
project = backend.parents[1]
core = project / 'code' / 'core_engine'
core_files = [
    (str(path), str(Path('tome-core') / path.relative_to(core).parent))
    for package in ('memory_runtime', 'tome_writer')
    for path in (core / package).rglob('*.py')
    if '__pycache__' not in path.parts
]
core_files += [(str(core / name), 'tome-core') for name in (
    'check_memory.py', 'write_novel.py', 'user_runtime.py',
    'package_migration_fingerprints.json',
)]
a = Analysis(
    [str(backend / 'desktop.py')],
    pathex=[str(backend), str(core)],
    binaries=[],
    datas=[(str(project / 'code' / 'frontend' / name), 'frontend')
           for name in ('index.html', 'app.js', 'style.css', 'vue-components.js', 'vue.runtime.global.prod.js', 'vue.LICENSE.txt')] + core_files + copy_metadata('langgraph'),
    hiddenimports=['langgraph.graph', 'langgraph.checkpoint.memory'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'unittest', 'pip', 'setuptools', 'tome_writer', 'memory_runtime', 'check_memory', 'write_novel', 'user_runtime'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='TomeAgent',
          debug=False, bootloader_ignore_signals=False, strip=False,
          upx=False, console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='TomeAgent')
