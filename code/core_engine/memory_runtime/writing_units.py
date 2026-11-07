"""Compose read-only writing views without merging or dropping state commits."""

import copy
import re

from inf_writer.domain import ContractError, canonical, digest

from .event_first import verify


def join_fragment(previous, raw):
    """Normalize only an exact whole-paragraph overlap at a unit boundary."""
    old = previous.split("\n\n")
    new = raw.split("\n\n")
    for count in range(min(len(old), len(new)), 0, -1):
        shared = "\n\n".join(new[:count])
        if not shared or "\n\n".join(old[-count:]) != shared:
            continue
        if len(re.findall(r"[\u3400-\u9fff]", shared)) < 12 and len(shared) < 60:
            continue
        if count == len(new):
            return raw, {
                "policy": "PRESERVE_COMPLETE_DUPLICATE_OUTPUT",
                "removed_characters": 0,
            }
        removed = len(shared) + 2
        return raw[removed:], {
            "policy": "EXACT_BOUNDARY_PARAGRAPH_OVERLAP",
            "removed_characters": removed,
        }
    return raw, {"policy": "NO_EXACT_BOUNDARY_OVERLAP", "removed_characters": 0}


def combined_commit(commits):
    if len(commits) == 1:
        return copy.deepcopy(commits[0])
    first = verify(commits[0])
    last = verify(commits[-1])
    scenes = [copy.deepcopy(s) for c in commits for s in c["scenes"]]
    for i, beat in enumerate([b for s in scenes for b in s["beats"]], 1):
        beat["token_id"] = f"slot_{i:03d}"
    times = []
    for c in commits:
        for value in c["computed_times"]:
            if value not in times:
                times.append(copy.deepcopy(value))
    body = {
        "version": 1,
        "chapter": first["chapter"],
        "base_state_sha256": first["base_state_sha256"],
        "state_sha256": last["state_sha256"],
        "proposal_sha256": digest(canonical([c["proposal_sha256"] for c in commits])),
        "scenes": scenes,
        "computed_times": times,
        "memory_projection": [
            copy.deepcopy(r) for c in commits for r in c["memory_projection"]
        ],
        "identifier_normalizations": [],
        "stage_transactions": copy.deepcopy(commits),
    }
    result = dict(body, sha256=digest(canonical(body)))
    verify(result)
    return result


def verify_chunks(chunks, commits, stages, *, complete=False):
    cursor = 0
    previous = ""
    for chunk in chunks:
        if "raw_text" in chunk or "raw_sha256" in chunk or "seam_report" in chunk:
            raw = chunk.get("raw_text")
            if not isinstance(raw, str) or digest(raw) != chunk.get("raw_sha256"):
                raise ContractError("Raw writing-unit integrity failure")
            cleaned, report = join_fragment(previous, raw)
            if cleaned != chunk["text"] or report != chunk.get("seam_report"):
                raise ContractError(
                    "Writing-unit boundary normalization differs from raw source"
                )
        hashes = chunk.get("source_commit_sha256s", [chunk["commit_sha256"]])
        if (
            not isinstance(hashes, list)
            or not hashes
            or cursor + len(hashes) > len(commits)
        ):
            raise ContractError("Invalid writing-unit transaction coverage")
        selected = commits[cursor : cursor + len(hashes)]
        expected_stages = stages[cursor : cursor + len(hashes)]
        if (
            hashes != [c["sha256"] for c in selected]
            or chunk["stage"] != expected_stages[0]
            or chunk.get("source_stages", expected_stages) != expected_stages
            or chunk["commit_sha256"] != combined_commit(selected)["sha256"]
            or digest(chunk["text"]) != chunk["sha256"]
        ):
            raise ContractError("Saved writing-unit source/text integrity failure")
        cursor += len(hashes)
        previous += "\n\n" + chunk["text"] if previous else chunk["text"]
    if complete and cursor != len(commits):
        raise ContractError("Writing units omitted event transactions")
