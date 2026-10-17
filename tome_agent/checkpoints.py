"""Official workspace checkpoints and separate unfinished attempt artifacts."""
import json
from pathlib import Path
from .storage import save_payload
from .state import Workspace


def save_checkpoint(workspace, path):
    workspace.validate()
    save_payload({"schema_version": 2, "fingerprint": workspace.fingerprint(),
                  "workspace": workspace.to_dict()}, Path(path))


def load_checkpoint(path, expected_fingerprint=None):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("Not a Tome architecture-v2 checkpoint; no silent migration")
    workspace = Workspace.from_dict(data["workspace"])
    if workspace.fingerprint() != data["fingerprint"] or (
            expected_fingerprint is not None and data["fingerprint"] != expected_fingerprint):
        raise ValueError("Prompt, outline or configuration fingerprint mismatch")
    workspace.validate()
    return workspace
