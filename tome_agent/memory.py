"""Evidence and revision checks; no automatic semantic truth judgment."""
from hashlib import sha256
from .domain import Fact, Story


def update_fact(story: Story, *, subject: str, key: str, value: str,
                chapter: int, quote: str, expected_revision: int) -> None:
    if any(not isinstance(x, str) or not x.strip() for x in (subject, key, value, quote)):
        raise ValueError("Fact fields must be nonempty strings")
    source = next((x for x in story.chapters if x.number == chapter), None)
    if source is None or quote not in source.text:
        raise ValueError("Evidence must occur in the committed source chapter")
    current = next((x for x in story.facts if (x.subject, x.key) == (subject, key)), None)
    revision = current.revision if current else 0
    if type(expected_revision) is not int or expected_revision != revision:
        raise ValueError("Stale or invalid fact revision")
    new = Fact(subject, key, value, revision + 1, chapter, quote,
               sha256(source.text.encode("utf-8")).hexdigest())
    if current:
        story.history.append(current)
        story.facts.remove(current)
    story.facts.append(new)
