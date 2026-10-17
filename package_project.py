"""Build a source delivery ZIP from an allowlist; excludes secrets and runs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256

root = Path(__file__).resolve().parent
destination = root.parent / "tome-agent-framework.zip"
root_files = {"README.md", "setup.cmd", "start.cmd", "pyproject.toml",
              "requirements.txt", "requirements-lock.txt", ".env.example", ".gitignore",
              "package_project.py"}
folders = {"code", "tests", "docs", ".github", ".streamlit"}
files = []
for path in root.rglob("*"):
    relative = path.relative_to(root)
    if not path.is_file() or "__pycache__" in relative.parts or path.suffix == ".pyc":
        continue
    if (len(relative.parts) == 1 and relative.name in root_files) or relative.parts[0] in folders or relative.as_posix() == "data/.gitkeep":
        files.append(path)
with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, "tome-agent/" + path.relative_to(root).as_posix())
with ZipFile(destination) as archive:
    if archive.testzip() is not None:
        raise ValueError("Archive validation failed")
    if any(Path(name).name == ".env" or "/.venv/" in name for name in archive.namelist()):
        raise ValueError("Sensitive file included")
print(f"Packaged {len(files)} files: {destination.name}")
print("SHA256: " + sha256(destination.read_bytes()).hexdigest())
