"""Generate drafts separately; commit only after author acceptance."""
from copy import deepcopy
from pathlib import Path
from typing import Protocol
from .domain import Chapter, ChapterPlan, Story
from .memory import update_fact
from .storage import save_story


class Planner(Protocol):
    def plan(self, premise: str, chapter_count: int) -> list[ChapterPlan]: ...


class Writer(Protocol):
    def draft(self, story: Story, plan: ChapterPlan) -> Chapter: ...


class MemoryExtractor(Protocol):
    def propose(self, story: Story, accepted_chapter: Chapter) -> list[dict]: ...


def commit_chapter(story: Story, chapter: Chapter, approved_updates: list[dict],
                   path: Path) -> Story:
    """Return new state only after all approved updates and persistence succeed."""
    if chapter.number != story.next_chapter or not chapter.text.strip():
        raise ValueError("Expected a nonempty next chapter")
    if chapter.number > len(story.outline):
        raise ValueError("Chapter must have an outline entry")
    trial = deepcopy(story)
    trial.chapters.append(deepcopy(chapter))
    for update in approved_updates:
        if update.get("chapter") != chapter.number:
            raise ValueError("New proposals must cite the accepted chapter")
        update_fact(trial, **update)
    save_story(trial, path)
    return trial
