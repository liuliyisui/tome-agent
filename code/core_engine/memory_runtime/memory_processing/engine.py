"""Reusable atomic memory pipeline, independent of any test novel/run path."""

import copy

from tome_writer.domain import ContractError
from tome_writer.tiered_memory import empty_memory, select_context
from tome_writer.tiered_runtime import TieredMemoryAgent

from .pipeline import ExtractionAdapter, LayerAgent, ReviewedTemporal, recall_probe
from .semantics import guard_extraction, guard_temporal


class MemoryEngine:
    def __init__(self, gateway):
        self.gateway = gateway
        self.transport = ExtractionAdapter(gateway)
        self.agent = TieredMemoryAgent(self.transport)
        self.temporal = ReviewedTemporal(self.transport)
        self.layers = LayerAgent(gateway)

    def advance(self, memory, chapters, number, trace):
        """Publish nothing until extraction, time and tier phases all succeed."""
        if type(number) is not int or number != memory.get("processed_through", 0) + 1:
            raise ContractError(
                "Process chapters sequentially from the last committed checkpoint"
            )
        prefix = copy.deepcopy(chapters[:number])
        if len(prefix) != number or any(
            c["number"] != i for i, c in enumerate(prefix, 1)
        ):
            raise ContractError("Missing or unordered chapter prefix")
        if "event_commit" in prefix[-1]:
            from .event_first import project_memory

            candidate = project_memory(memory, prefix, number, trace)
            if prefix[-1].get("prose_policy") == "unchecked":
                from .projection_grounding import ground, retryable_chapters

                candidate = ground(candidate, prefix, number, self.gateway, trace)
                older = [n for n in retryable_chapters(candidate) if n < number]
                if older:
                    candidate = ground(candidate, prefix, older[0], self.gateway, trace)
            from .meaning_organizer import organize

            trace_start = len(trace)
            candidate = organize(candidate, prefix, number, self.gateway, trace)
            candidate, layer_report = self.layers.run(
                candidate, prefix, number, prefix[-1]["title"], trace
            )
            organization_intake = [
                move
                for entry in trace[trace_start:]
                if entry.get("role") == "memory_meaning_intake"
                for move in entry["moves"]
            ]
            layer_report["intake_moves"] = organization_intake + layer_report.get(
                "intake_moves", []
            )
            layer_report["moves"] = organization_intake + layer_report.get("moves", [])
            return candidate, {
                "chapter": number,
                "layers": layer_report,
                "selection_ids": [],
                "withheld_mutations": 0,
                "temporal_omitted_ids": [],
                "temporal_coverage": "Canonical events own state changes; memory only chooses storage tiers",
                "extraction_transforms": [],
                "canonical_projection": True,
            }
        selection = select_context(memory, query=prefix[-1]["text"], max_bytes=48000)
        start = len(self.transport.transforms)
        self.transport.full_memory = copy.deepcopy(memory)
        candidate = self.agent.extract(
            copy.deepcopy(memory), prefix, number, selection, trace
        )
        candidate = guard_extraction(
            memory, candidate, prefix, number, self.gateway, trace
        )
        timed = self.temporal.run(memory, candidate, prefix, number, selection, trace)
        candidate = guard_temporal(
            candidate, timed, prefix, number, self.gateway, trace
        )
        for entry in self.transport.transforms[start:]:
            for note in entry.get("normalizations", []):
                if note.get("rule") == "attribute_storage_identifier":
                    candidate.setdefault("attribute_labels", {})[note["new"]] = note[
                        "old"
                    ]
        candidate, layer_report = self.layers.run(
            candidate, prefix, number, prefix[-1]["title"], trace
        )
        return candidate, {
            "chapter": number,
            "layers": layer_report,
            "selection_ids": selection["selected_ids"],
            "withheld_mutations": len(candidate.get("withheld_memory_mutations", []))
            - len(memory.get("withheld_memory_mutations", [])),
            "temporal_omitted_ids": selection["omitted_ids"],
            "temporal_coverage": "selected_old_records_only",
            "extraction_transforms": copy.deepcopy(self.transport.transforms[start:]),
        }

    def recall(self, memory, question, trace, label="query"):
        return recall_probe(memory, question, self.gateway, trace, label)

    def repair_structured_memory(self, memory, chapters, trace, *, max_chapters=2):
        """One final bounded catch-up, including the last chapter's failures."""
        from tome_writer.domain import canonical, digest

        from .projection_grounding import ground, pending_chapters, retryable_chapters

        candidate = copy.deepcopy(memory)
        retryable = retryable_chapters(candidate)
        # Rotate final negative rechecks: a permanently absent chapter must not
        # consume every bounded pass and starve later chapters indefinitely.
        negatives = [n for n in pending_chapters(candidate) if n not in retryable]
        negatives.sort(
            key=lambda n: (
                candidate.get("projection_grounding", {})
                .get(str(n), {})
                .get("reconsideration_passes", 0),
                n,
            )
        )
        order = retryable + negatives
        if not order:
            return candidate
        reviewed = []
        attempted = []
        for number in order[:max_chapters]:
            positions = {
                i
                for i, r in enumerate(
                    chapters[number - 1]["event_commit"]["memory_projection"], 1
                )
                if r["ref"] in candidate["projection_omissions"][str(number)]
            }
            start = len(trace)
            attempted.append(number)
            candidate = ground(
                candidate, chapters, number, self.gateway, trace, reconsider_absent=True
            )
            seen = {
                i
                for entry in trace[start:]
                if entry.get("role") == "prose_memory_grounding"
                for i in entry.get("reviewed_positions", [])
            }
            if positions <= seen:
                reviewed.append(number)
        candidate["projection_recheck_coverage"] = {
            "queued_chapters": order,
            "attempted_chapters": attempted,
            "reviewed_chapters": reviewed,
            "unreviewed_chapters": [n for n in order if n not in reviewed],
            "scope": "One bounded pass over queued chapters; coverage does not certify every plan outcome",
        }
        if candidate != memory:
            from .meaning_organizer import organize

            candidate = organize(
                candidate, chapters, len(chapters), self.gateway, trace
            )
            scope = ":structured-repair:" + digest(canonical(memory))[:20]
            candidate, _ = self.layers.run(
                candidate,
                chapters,
                len(chapters),
                chapters[-1]["title"],
                trace,
                transaction_scope=scope,
            )
        return candidate

    @staticmethod
    def empty():
        return empty_memory()
