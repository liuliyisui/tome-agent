"""V4-style state, implemented independently; not an NST checkpoint format."""
from dataclasses import dataclass, field, asdict
from hashlib import sha256
import json


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":"))


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


@dataclass
class NarrativeState:
    characters: dict = field(default_factory=dict)
    past_events: dict = field(default_factory=dict)
    future_requirements: dict = field(default_factory=dict)
    facts: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    receipts: dict = field(default_factory=dict)
    pending: dict = field(default_factory=dict)
    attempts: list = field(default_factory=list)

    def view(self, max_bytes=12000):
        facts = [f for f in self.facts.values() if f["status"] == "active"]
        if len(canonical(facts).encode("utf-8")) > max_bytes:
            raise ValueError("Active fact budget exceeded; explicit review required")
        return {"characters": self.characters, "past_events": self.past_events,
                "future_requirements": self.future_requirements, "facts": facts}

    def check_sources(self, chapters):
        for fact in self.facts.values():
            self.check_evidence(fact["evidence"], chapters)
        for receipt in self.receipts.values():
            if digest(chapters.get(receipt["chapter"], "")) != receipt["source_hash"]:
                raise ValueError("Accepted group source changed or missing")

    @staticmethod
    def check_evidence(evidence, chapters):
        text = chapters.get(evidence["chapter"])
        if (text is None or digest(text) != evidence["source_hash"]
                or not evidence["quote"] or evidence["quote"] not in text):
            raise ValueError("Evidence source changed or missing")


@dataclass
class Workspace:
    title: str
    prompt: str
    outline: list
    config: dict = field(default_factory=dict)
    planning: dict = field(default_factory=dict)
    chapters: dict = field(default_factory=dict)
    state: NarrativeState = field(default_factory=NarrativeState)

    def fingerprint(self):
        return digest(canonical({"title": self.title, "prompt": self.prompt,
                                 "outline": self.outline, "config": self.config,
                                 "planning": self.planning}))

    def validate(self):
        if not self.outline or any(not isinstance(p, dict) or
                not all(isinstance(p.get(k), str) and p[k].strip() for k in ("title", "goal"))
                for p in self.outline):
            raise ValueError("Outline requires nonempty title and goal per chapter")
        if sorted(self.chapters) != list(range(1, len(self.chapters) + 1)):
            raise ValueError("Completed chapters must be contiguous")
        if len(self.chapters) > len(self.outline):
            raise ValueError("Completed chapters exceed outline")
        if any("target_units" in p and (type(p["target_units"]) is not int or p["target_units"] < 1) for p in self.outline):
            raise ValueError("Chapter target_units must be a positive integer")
        if self.state.pending:
            raise ValueError("Official workspace contains unresolved groups")
        self.state.check_sources(self.chapters)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data["chapters"] = {int(k): v for k, v in data["chapters"].items()}
        data["state"] = NarrativeState(**data["state"])
        return cls(**data)
