"""Versioned JSON snapshots, replaced atomically on the same filesystem."""
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from tome_agent.domain import Chapter, ChapterPlan, Fact, Story


def save_story(story: Story, path: Path) -> None:
    save_payload({"schema_version": 1, "story": asdict(story)}, path)


def save_payload(payload: dict, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False, suffix=".tmp") as handle:
            tmp = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def load_story(path: Path) -> Story:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot version")
    data = payload["story"]
    story = Story(data["title"], data["premise"],
                  [ChapterPlan(**x) for x in data["outline"]],
                  [Chapter(**x) for x in data["chapters"]],
                  [Fact(**x) for x in data["facts"]],
                  [Fact(**x) for x in data["history"]])
    if [c.number for c in story.chapters] != list(range(1, len(story.chapters) + 1)):
        raise ValueError("Snapshot chapters must be contiguous")
    return story
