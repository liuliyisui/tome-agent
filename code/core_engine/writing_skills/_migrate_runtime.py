"""Update a book's longform checkpoint runtime fingerprint to the current engine.

Backs up the checkpoint before touching it; prints what it did. Only the
`runtime_sha256` envelope field is replaced; `book`, `book_sha256` and
`writing_plan_sha256` are left untouched.
"""

import json
import os
import shutil
import sys
from pathlib import Path


def main():
    folder = Path(sys.argv[1])
    from memory_runtime.writing import runtime_hashes

    current = runtime_hashes()
    pointer = json.loads(
        (folder / "longform-current.json").read_text(encoding="utf-8-sig")
    )
    checkpoint = folder / pointer["checkpoint"]
    if not checkpoint.exists():
        print("MISSING", checkpoint)
        return 1
    record = json.loads(checkpoint.read_text(encoding="utf-8-sig"))
    if record.get("runtime_sha256") == current:
        print("ALREADY_CURRENT", checkpoint.name)
        return 0
    backup = checkpoint.with_name(checkpoint.name + ".prehash.bak")
    if not backup.exists():
        shutil.copy2(checkpoint, backup)
    record["runtime_sha256"] = current
    temporary = checkpoint.with_name(checkpoint.name + ".tmp")
    temporary.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, checkpoint)
    print("PATCHED", checkpoint.name, "backup=", backup.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
