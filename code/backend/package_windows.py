"""Create a redistributable zip from the allowlisted PyInstaller output."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

project = Path(__file__).resolve().parents[2]
dist = project / "code" / "backend" / "data" / "dist"
bundle = dist / "TomeAgent"
if not (bundle / "TomeAgent.exe").is_file():
    raise SystemExit("Build TomeAgent.exe first")
shutil.copyfile(project / "docs" / "software" / "WINDOWS_PORTABLE.md", bundle / "使用说明.txt")
files = sorted(p for p in bundle.rglob("*") if p.is_file())
for file in files:
    relative = file.relative_to(bundle)
    if file.name.startswith(".env") or any(part in {"data", ".trash", "inf_books", ".venv"} for part in relative.parts):
        raise ValueError("Refusing to package local configuration or book data")
destination = dist / "TomeAgent-Windows-x64.zip"
with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, "TomeAgent/" + file.relative_to(bundle).as_posix())
with ZipFile(destination) as archive:
    if archive.testzip():
        raise ValueError("Archive verification failed")
checksum = sha256(destination.read_bytes()).hexdigest()
(dist / (destination.name + ".sha256")).write_text(checksum + "  " + destination.name + "\n", encoding="ascii")
print(f"Created {destination.name}: {destination.stat().st_size:,} bytes; SHA256 {checksum}")
