"""Package README and the four required top-level directories without secrets or runs."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

project = Path(__file__).resolve().parents[2]
destination = project.parent / "tome-agent-inf.zip"
allowed = {"README.md", "docs", "code", "tests", ".github"}
files = []
for path in project.rglob("*"):
    relative = path.relative_to(project)
    if not path.is_file() or relative.parts[0] not in allowed:
        continue
    posix = relative.as_posix()
    if ("__pycache__" in relative.parts or path.suffix in (".pyc", ".pyo")
            or posix == "code/backend/.env" or "code/backend/.venv/" in posix
            or (posix.startswith("code/backend/data/") and not posix.endswith("/.gitkeep"))):
        continue
    files.append(path)
with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, "tome-agent/" + path.relative_to(project).as_posix())
with ZipFile(destination) as archive:
    if archive.testzip() is not None:
        raise ValueError("Archive validation failed")
print(f"Packaged {len(files)} files: {destination.name}")
print("SHA256: " + sha256(destination.read_bytes()).hexdigest())
