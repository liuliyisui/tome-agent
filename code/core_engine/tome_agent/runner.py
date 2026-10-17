"""Sequential whole-book coordinator; checkpoints after each successful chapter."""
import json
from pathlib import Path
from tome_backend.checkpoints import load_checkpoint, save_checkpoint
from .state import digest, canonical


class StoryRunner:
    def __init__(self, chapter_agent):
        self.agent = chapter_agent

    def run(self, workspace, checkpoint, chapter_limit=1, should_stop=lambda: False, resume_attempt=False):
        if type(chapter_limit) is not int or chapter_limit < 1:
            raise ValueError("Positive explicit chapter limit required")
        checkpoint = Path(checkpoint)
        if checkpoint.exists():
            workspace = load_checkpoint(checkpoint, workspace.fingerprint())
        else:
            save_checkpoint(workspace, checkpoint)
        for _ in range(chapter_limit):
            if should_stop() or len(workspace.chapters) == len(workspace.outline):
                break
            attempt = None
            attempt_path = Path(str(checkpoint) + ".attempt.json")
            if resume_attempt and attempt_path.exists():
                candidate = json.loads(attempt_path.read_text(encoding="utf-8"))
                if candidate["base_hash"] == digest(canonical(workspace.to_dict())):
                    attempt = candidate
            workspace = self.agent.run(workspace, checkpoint, attempt)
        return workspace
