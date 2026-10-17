"""Serializable records; chapter order is not a story-world timestamp."""
from dataclasses import dataclass, field


@dataclass
class ChapterPlan:
    number: int
    title: str
    goal: str


@dataclass
class Chapter:
    number: int
    title: str
    text: str


@dataclass
class Fact:
    subject: str
    key: str
    value: str
    revision: int
    chapter: int
    quote: str
    source_hash: str


@dataclass
class Story:
    title: str
    premise: str
    outline: list[ChapterPlan] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    history: list[Fact] = field(default_factory=list)

    @property
    def next_chapter(self) -> int:
        return len(self.chapters) + 1
