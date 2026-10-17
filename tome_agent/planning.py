"""Premise → detailed synopsis → acts → frozen chapter outline and cache."""
import json
from copy import deepcopy
from pathlib import Path
from .state import canonical, digest, Workspace
from .storage import save_payload


class OutlinePlanner:
    def __init__(self, model):
        self.model = model

    def generate(self, title, prompt, chapter_count, target_units, config, cache_path=None):
        if type(chapter_count) is not int or chapter_count < 1 or type(target_units) is not int or target_units < chapter_count:
            raise ValueError("Positive chapter count and sufficient target units required")
        descriptor = {"version": 1, "title": title, "prompt": prompt, "count": chapter_count,
                      "target_units": target_units, "config": config}
        fingerprint = digest(canonical(descriptor))
        if cache_path and Path(cache_path).exists():
            cached = json.loads(Path(cache_path).read_text(encoding="utf-8"))
            if cached["fingerprint"] != fingerprint:
                raise ValueError("Outline cache configuration mismatch")
            workspace = Workspace.from_dict(cached["workspace"])
            if workspace.fingerprint() != cached["workspace_fingerprint"]:
                raise ValueError("Outline cache content changed")
            workspace.validate()
            return workspace
        stages = {}
        for stage in ("premise", "synopsis", "acts", "chapters"):
            request = {**descriptor, "stage": stage, "previous_stages": stages,
                       "instruction": "Return JSON only. For chapters return exactly count objects with title and goal; otherwise return an object describing this stage."}
            result = self.model.complete([{"role": "user", "content": canonical(request)}], [])
            if result.finish_reason != "stop" or result.calls:
                raise ValueError("Planning response incomplete or unexpectedly used tools")
            value = json.loads(result.content)
            if stage == "chapters":
                if not isinstance(value, list) or len(value) != chapter_count:
                    raise ValueError("Wrong number of planned chapters")
            elif not isinstance(value, dict) or not value:
                raise ValueError("Planning stage requires a nonempty object")
            stages[stage] = value
        outline = deepcopy(stages.pop("chapters"))
        base, extra = divmod(target_units, chapter_count)
        for index, chapter in enumerate(outline):
            if not isinstance(chapter, dict) or set(chapter) != {"title", "goal"}:
                raise ValueError("Chapter plan requires exactly title and goal")
            chapter["target_units"] = base + (index < extra)
        workspace = Workspace(title, prompt, outline, deepcopy(config), stages)
        workspace.validate()
        if cache_path:
            save_payload({"fingerprint": fingerprint, "workspace_fingerprint": workspace.fingerprint(),
                          "workspace": workspace.to_dict()}, Path(cache_path))
        return workspace
