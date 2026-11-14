"""Durable writing adapter for the verified three-tier memory pipeline."""

import copy
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from inf_writer.agents import JsonAgent
from inf_writer.domain import ContractError, canonical, digest, evidence_segments
from inf_writer.tiered_memory import (
    legacy_projection,
    select_context,
    select_history_context,
)

from .completion import (
    ContextCapacityError,
    PlanningOutputFailure,
    continue_prose,
    unplanned_packet,
)
from .continuity import CONTRACT as CONTINUITY_CONTRACT
from .continuity import context_view as writing_state_view
from .continuity import empty as empty_writing_state
from .continuity import guard as guard_continuity
from .engine import MemoryEngine
from .event_contract import validate_plan_shape
from .event_first import CONTRACT as EVENT_CONTRACT
from .event_first import STATE_CONTRACT as EVENT_STATE_CONTRACT
from .event_first import normalize_plan, writer_view
from .event_first import prepare as prepare_events
from .event_first import verify as verify_events
from .event_references import catalogue as reference_catalogue
from .event_references import public_state_view, public_type, reference_id
from .interface_contract import public_memory_rows
from .numeric_grounding import POLICY as QUANTITY_POLICY
from .numeric_grounding import sources as quantity_sources
from .pipeline import source_evidence_view
from .prose_rendering import render as render_prose
from .story_review import StoryReferenceGateway, StoryReviewAgent
from .time_calculation import CONTRACT as TIME_CONTRACT
from .time_calculation import calculate, write_with_calculations


class StageRevisionRequested(Exception):
    """Writer requests replanning before any chapter prose is committed."""


def record_future_plan(book, proposal, max_chapters):
    """Keep the saved outline inside the book's configured chapter cap."""
    for future in proposal.get("future_updates", []):
        number = future.get("number")
        if type(number) is int and number <= max_chapters:
            book["plan"][str(number)] = copy.deepcopy(future)


def runtime_hashes():
    from importlib.metadata import version

    from check_memory import ROOT, sha, source_hashes

    return {
        "memory_runtime": source_hashes(),
        "entrypoints": {
            name: sha(ROOT / name)
            for name in ("write_novel.py", "user_runtime.py", "check_memory.py")
        },
        "orchestration": {"framework": "langgraph", "version": version("langgraph")},
    }


# LF and CRLF digests for source files changed by the reviewed Sonar refactor.
_SONAR_REFACTOR_DIGESTS = {
    "chapter_titles.py": (
        (
            "34239ce11a8600107fc73be5528d04fea4cacb1746c51a306679e0af20ddc87d",
            "aff94ec2e3381470aa52b71928bd276b53dafb3cb2401de0f9884b5a58aea240",
        ),
        (
            "3d2b9ab442f25da5004e191fee5ad006abe4b47ecd983b80800789d999907832",
            "edf3fd726b6da9ec79398294d7706f9485d05d3d5c007c5a52ff775b96a5fa98",
        ),
    ),
    "evidence_access.py": (
        (
            "c3dbc87f2642f52f36773015b91d1f4fa294700bcfeb3f83c68d45fca107605e",
            "907825c51ce52dd3f6b00f5c24dd28fbfbd43aaa583e45fce29dac1c8c0b27df",
        ),
        (
            "143c3e291e651853789cfe1b1d253fc4cf3dae04719381e26898807c11704200",
            "96083f74553c22f9886acffacfae99769b598b412a0c37519e5038767ebe7e4d",
        ),
    ),
    "stage_planning.py": (
        (
            "cf46d4be394adc22d74b9415546d76f2e5483d1edc1be8014eed974a4a876570",
            "3c97c90aa9c585c6c92f02705a65ddc3cf7ca1e58fc349f817441d3b0c39dc2a",
        ),
        (
            "a3b1414ad83fbdee3fdd9736635543dbae9cc31028af0cd08ed52711099cbb04",
            "bcc38e93880b5e0d9912a580af0594f5e29e7534b19e7e72184d97436aa2f532",
        ),
    ),
}


def _matches_checkpoint_source(name, saved_digest, current_digest):
    if saved_digest == current_digest:
        return True
    reviewed = _SONAR_REFACTOR_DIGESTS.get(name)
    if reviewed is None:
        return False
    previous_digests, current_digests = reviewed
    return saved_digest in previous_digests and current_digest in current_digests


def _compatible_runtime(saved, current):
    """Accept only reviewed predecessor runtimes, while checking all other files."""
    if saved == current:
        return True
    if not isinstance(saved, dict) or set(saved) != set(current):
        return False
    if saved.get("orchestration") != current["orchestration"]:
        return False
    memory = saved.get("memory_runtime")
    entries = saved.get("entrypoints")
    if not isinstance(memory, dict) or not isinstance(entries, dict):
        return False
    if set(memory) != set(current["memory_runtime"]) or set(entries) != set(
        current["entrypoints"]
    ):
        return False
    if any(
        not _matches_checkpoint_source(name, value, current["memory_runtime"][name])
        for name, value in memory.items()
        if name not in {"writing.py", "test_regression.py"}
    ) or any(
        value != current["entrypoints"][name]
        for name, value in entries.items()
        if name != "check_memory.py"
    ):
        return False
    # Each pair is the LF and CRLF digest of a reviewed Git revision.
    previous = (
        (
            (
                "b1ea19c9ed227aa993874357fdf99e68227386d654a46217f288ca9f40cf94e4",
                "3eab57edf49f68672c72ff6bbec411c7b18df2b3b36dd70cbaca9a09802595d2",
            ),
            (
                "87b5a3b46326d949cd47e54d89d76ebdbf1ea90ea31390a75c727523a68fd7a1",
                "ab3a8456d22277e5605bd136e26ea3aafab001a8ebfe562badbba55e83b7cf10",
            ),
            (
                "a8cc33a3b15635d5ce1cfb6e7a2a9eae338eda4e3223342c55b4f4ad43d679af",
                "f14e8d8f7c4ed0a449465d6bbbfc79d3e502d84d5d042ae70bb9265f7cf726ac",
            ),
        ),
        (
            (
                "0c2766414351d40a678edcc9b5e3af881ca0e6d85a21fcc87fcebb0ee0b91d19",
                "5a7908ae8111e04ab5036d06b380599cf0e9cfe2724458c9efd2798ca481753d",
            ),
            (
                "951ce0598085e687988ab30fee10d14c5cf8e734009e3a17e0eff7dbd3ea21f0",
                "52d52d11e64e0a53f2e16f23c698d0994c2591deabc416f4a1365b66f97940db",
            ),
            (
                "f68f288c068dbc4c432ce18407fe565ef65f8aa1b3fe53824377e1172f3fe6da",
                "d0f8ee07b8e5e1160daa81c6cb4d2046f16e70454bf9bf76349d49f212fc0d04",
            ),
        ),
        (
            (
                "2176393d3b0be40a9f2c9f7a852bf115ed19a08450933ebb73d96a86aed574ed",
                "c9816f23d1e96ecb033ef92d9caed870ac59253dbe61eaef6dda2378198816db",
                "dc1352ee81f6d7b71942a9ad5178f0a65e2d8108a8b657c05d35f190d86df28e",
                "2d80bd6b4cdf4d9cce3cdf2103c4ac79fac99c92560b06aac66e03ece8b4cd98",
            ),
            (
                "87b5a3b46326d949cd47e54d89d76ebdbf1ea90ea31390a75c727523a68fd7a1",
                "ab3a8456d22277e5605bd136e26ea3aafab001a8ebfe562badbba55e83b7cf10",
            ),
            (
                "a8cc33a3b15635d5ce1cfb6e7a2a9eae338eda4e3223342c55b4f4ad43d679af",
                "f14e8d8f7c4ed0a449465d6bbbfc79d3e502d84d5d042ae70bb9265f7cf726ac",
            ),
        ),
    )
    return any(
        memory["writing.py"] in writing
        and memory["test_regression.py"] in regression
        and entries["check_memory.py"] in check
        for writing, regression, check in previous
    )


def _verify_resume_envelope(record, plan):
    if record.get("schema") != "inf-writing-checkpoint-v1":
        raise ContractError("仅可恢复新写作入口的完整检查点；旧小说需显式迁移")
    if not _compatible_runtime(record.get("runtime_sha256"), runtime_hashes()):
        raise ContractError("写作运行时版本不一致，不能直接恢复旧检查点")
    if record.get("writing_plan_sha256") != digest(canonical(plan)):
        raise ContractError("恢复时小说配置必须与原运行一致")
    book = record["book"]
    if record.get("book_sha256") != digest(canonical(book)):
        raise ContractError("写作检查点内容校验失败")


def _verify_resume_memory_coverage(book):
    from inf_writer.memory_meaning import verify_meanings

    from .narrative_planning import verify_ledger

    verify_ledger(book)
    verify_meanings(book["memory"], book["chapters"])
    done = book["memory"]["processed_through"]
    chapters = book["chapters"]
    if type(done) is not int or not 0 <= done <= len(chapters):
        raise ContractError("Invalid memory coverage")
    if [c["number"] for c in chapters] != list(range(1, len(chapters) + 1)):
        raise ContractError("Invalid chapter sequence")
    if book["pending"] != list(range(done + 1, len(chapters) + 1)):
        raise ContractError("Memory pending coverage gap")
    if [r["chapter_number"] for r in book["outcomes"]] != list(
        range(1, len(chapters) + 1)
    ):
        raise ContractError("Invalid writing outcome sequence")
    if any(int(n) < 1 or int(n) > len(chapters) for n in book["review_jobs"]):
        raise ContractError("Invalid pending prose review")
    for fragment in book.get("prose_fragments", {}).values():
        if digest(fragment["text"]) != fragment["sha256"]:
            raise ContractError("Saved prose fragment hash mismatch")
    return done


def _verify_resume_event_history(book, done):
    from .projection_grounding import verify_grounding
    from .state_recovery import verify_recoveries

    chapters = book["chapters"]
    verify_recoveries(book)
    verify_grounding(book["memory"], chapters)
    expected = digest(canonical(empty_writing_state()))
    for chapter in chapters:
        expected = _verify_resume_chapter(book, chapter, done, expected)
    if digest(canonical(book["writing_state"])) != expected:
        raise ContractError("Current world state differs from committed event outcomes")
    _verify_prepared_resume_events(book, chapters, expected)


def _verify_resume_chapter(book, chapter, done, expected):
    from .narrative_planning import verify_design
    from .prose_rendering import saved_text

    verify_design(chapter)
    commit = verify_events(chapter.get("event_commit"))
    if (
        digest(chapter["text"]) != chapter["sha256"]
        or saved_text(chapter) != chapter["text"]
    ):
        raise ContractError("Saved prose data integrity failure")
    _verify_resume_event_stages(chapter, commit)
    if (
        commit["chapter"] != chapter["number"]
        or commit["base_state_sha256"] != expected
    ):
        raise ContractError("Canonical event history has a state-chain gap")
    expected = commit["state_sha256"]
    _verify_resume_projection(book, chapter, done, commit)
    return _verify_resume_recoveries(book, chapter, expected)


def _verify_resume_event_stages(chapter, commit):
    if "event_stage_sources" not in chapter:
        return
    chunks = chapter["event_stage_sources"]
    parts = commit.get("stage_transactions", [])
    if "\n\n".join(c["text"] for c in chunks) != chapter["text"]:
        raise ContractError("Saved event stages differ from chapter prose")
    from .writing_units import verify_chunks

    stages = [
        report["stage"]
        for report in commit.get("stage_reports", [])
        if report["status"] == "PREPARED"
    ]
    verify_chunks(chunks, parts, stages or list(range(len(parts))), complete=True)


def _verify_resume_projection(book, chapter, done, commit):
    if chapter["number"] > done:
        return
    if (
        book["memory"].get("canonical_commits", {}).get(str(chapter["number"]))
        != commit["sha256"]
    ):
        raise ContractError("Memory projection does not match committed event source")
    if chapter.get("prose_policy") == "unchecked":
        from .prose_memory import verify_prose_coverage

        if not verify_prose_coverage(book["memory"], chapter):
            raise ContractError("Saved prose memory coverage is missing or damaged")


def _verify_resume_recoveries(book, chapter, expected):
    for recovered in book.get("state_recovery_commits", []):
        if recovered["after_chapter"] != chapter["number"]:
            continue
        transaction = verify_events(recovered["commit"])
        if transaction["base_state_sha256"] != expected:
            raise ContractError("Recovered state history has a chain gap")
        expected = transaction["state_sha256"]
    return expected


def _verify_prepared_resume_events(book, chapters, expected):
    for key, prepared in book.get("prepared_events", {}).items():
        commit = verify_events(prepared["commit"])
        if (
            key != str(len(chapters) + 1)
            or commit["chapter"] != len(chapters) + 1
            or commit["base_state_sha256"] != expected
        ):
            raise ContractError(
                "Prepared event transaction has an invalid chapter or base state"
            )
        if (
            digest(canonical(prepared["candidate_state"])) != commit["state_sha256"]
            or digest(canonical(prepared["proposal"])) != commit["proposal_sha256"]
        ):
            raise ContractError("Prepared event proposal/state integrity failure")
        verify_stage_realizations(prepared)


def load_resume(path, plan):
    from check_memory import read

    record = read(path)
    _verify_resume_envelope(record, plan)
    book = record["book"]
    done = _verify_resume_memory_coverage(book)
    if plan.get("event_first", True):
        _verify_resume_event_history(book, done)
    return copy.deepcopy(book)


def verify_stage_realizations(prepared):
    from .narrative_planning import verify_design

    verify_design(prepared)
    packets = prepared.get("stage_packets", [])
    chunks = prepared.get("stage_realizations", [])
    for packet in packets:
        verify_events(packet["commit"])
        if (
            digest(canonical(packet["candidate_state"]))
            != packet["commit"]["state_sha256"]
        ):
            raise ContractError("Saved event-stage prose/state integrity failure")
    from .writing_units import verify_chunks

    verify_chunks(chunks, [p["commit"] for p in packets], [p["stage"] for p in packets])


@dataclass
class _EventPlanDraft:
    """Keep the last planner outputs available at each recovery boundary."""

    public_proposal: dict | None = None
    last_public: dict | None = None
    last_compiled: dict | None = None
    last_design: dict = field(default_factory=dict)


class WritingSession:
    def __init__(self, output, gateway, plan, book=None):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=False)
        self.plan = copy.deepcopy(plan)
        self.gateway = gateway
        self.engine = MemoryEngine(gateway)
        if self.plan.get("event_first", True):
            self.plan["story_review_enabled"] = False
        self.story_gateway = StoryReferenceGateway(gateway)
        self.agents = {
            "planner": JsonAgent(
                "planner",
                gateway,
                compact_narrative=True,
                max_format_retries=0,
                max_output_tokens=16384,
            ),
            "writer": JsonAgent(
                "writer", gateway, compact_narrative=True, max_output_tokens=16384
            ),
            "reviewer": StoryReviewAgent(self.story_gateway),
        }
        self.book = (
            copy.deepcopy(book)
            if book is not None
            else {
                "schema_version": "inf-writing-book-v1",
                "goal": plan["goal"],
                "constraints": copy.deepcopy(plan["constraints"]),
                "chapters": [],
                "plan": {},
                "memory": MemoryEngine.empty(),
                "pending": [],
                "outcomes": [],
                "review_jobs": {},
            }
        )
        self.book.setdefault("writing_state", empty_writing_state())
        self.book.setdefault("prepared_events", {})
        from .narrative_planning import ensure_accountability

        ensure_accountability(self.book)
        from .graph_runtime import build_writing_graph

        self.graph = build_writing_graph(self)
        self.serial = 0
        self.latest_checkpoint = None
        self.hashes = runtime_hashes()
        self._save([], "RESUMED" if book is not None else "EMPTY_START")

    def _save(self, trace, reason):
        from check_memory import save_new

        path = self.output / f"checkpoint_{self.serial:04d}.json"
        save_new(
            path,
            {
                "schema": "inf-writing-checkpoint-v1",
                "runtime_sha256": self.hashes,
                "writing_plan_sha256": digest(canonical(self.plan)),
                "book_sha256": digest(canonical(self.book)),
                "book": self.book,
                "trace": trace,
                "reason": reason,
                "orchestration": "langgraph",
            },
        )
        self.latest_checkpoint = path
        self.serial += 1

    def context(self, instruction, query):
        book = self.book
        memory = book["memory"]
        number = len(book["chapters"]) + 1
        event_first = self.plan.get("event_first", True)
        selection = select_context(
            memory, query=query, max_bytes=22000 if event_first else 32000
        )
        bindings = {
            i: {"memory_id": i, "view": "current"} for i in selection["selected_ids"]
        }
        evidence = source_evidence_view(
            memory,
            selection["selected_ids"],
            bindings,
            query,
            max_bytes=8000 if event_first else 12000,
        )
        history = select_history_context(
            memory, query=query, max_bytes=4000 if event_first else 6000
        )
        context = {
            "goal": book["goal"],
            "constraints": book["constraints"],
            "chapter_number": number,
            "instruction": instruction,
            "checkpoint_revision": memory["revision"],
            "recent_chapters": [
                {k: c[k] for k in ("number", "title", "text", "sha256")}
                for c in book["chapters"][-2:]
            ],
            "planned_next_chapters": [
                v
                for k, v in sorted(book["plan"].items(), key=lambda r: int(r[0]))
                if int(k) >= number
            ],
            "active_facts": legacy_projection(selection),
            "historical_memory": history,
            "source_evidence": evidence["items"],
            "memory_coverage": {
                "processed_through": memory["processed_through"],
                "selected_ids": selection["selected_ids"],
                "omitted_ids": selection["omitted_ids"],
                "source_evidence_omitted": evidence["omitted"],
                "pending_chapters": copy.deepcopy(book["pending"]),
                "complete": not book["pending"],
            },
            "unresolved_chapters": [
                r["chapter_number"]
                for r in book["outcomes"]
                if r["status"] != "DRAFT_CHECKED"
            ],
            "fact_bank_status": f"Memory committed through chapter {memory['processed_through']}; pending chapters {book['pending']}. "
            "Pending chapter changes may be absent from memory. Read recent prose for newer events; do not treat older memory or historical quotes as unconditionally current authority.",
        }
        context["calculation_contract"] = copy.deepcopy(TIME_CONTRACT)
        context["quantity_policy"] = QUANTITY_POLICY
        from .narrative_planning import context as narrative_context

        context["narrative_continuity"] = narrative_context(book, number)
        from .narrative_planning import handoff as chapter_handoff

        context["chapter_handoff"] = chapter_handoff(book)
        context["unprojected_chapters"] = [
            c["number"]
            for c in book["chapters"]
            if c.get("event_plan_status") in ("partial", "unavailable")
            and c.get("state_recovery_status") != "reconciled"
        ]
        if context["unprojected_chapters"]:
            context["fact_bank_status"] += (
                " Some chapters have prose only; event state omits their changes. Prefer saved prose for these chapters."
            )
        context["continuity_contract"] = copy.deepcopy(CONTINUITY_CONTRACT)
        if event_first:
            references = reference_catalogue(book)
            self._add_event_state_context(context, query, references)
            self._add_event_reference_context(context, references)
            self._add_event_memory_context(context)
        else:
            context["writing_state"] = writing_state_view(book["writing_state"], query)
        if self.plan.get("closure_enabled", True):
            from .story_closure import context as closure_context

            context["story_closure"] = closure_context(book, self.plan)
        self._bound(context)
        return context

    @staticmethod
    def _add_state_meaning(record, meaning):
        if not meaning:
            return
        record["memory_meaning"] = meaning
        if meaning["validity"] in ("historical", "mixed") or any(
            u["conflict_ids"] for u in meaning["units"]
        ):
            if "value" in record:
                record["recorded_value"] = record.pop("value")
            record["reference_usage"] = (
                "保留的历史/混合记录，可作为更新目标；recorded_value不能整体当作当前事实，按memory_meaning使用。"
            )

    def _add_event_state_context(self, context, query, references):
        book = self.book
        # Detailed future briefs were authored before their preceding
        # chapters existed. Reusing them as execution instructions can
        # repeat completed actions and force invented evidence outcomes.
        # Keep the archive, expose only scheduling hints, and rebase from
        # saved prose, current state and still-open narrative commitments.
        forecasts = context.pop("planned_next_chapters")
        context["future_outline_goals"] = [
            {
                "number": r["number"],
                "working_title": r["title"],
                "scope": "Unwritten scheduling hint; not facts, frozen scenes or an obligatory outcome",
            }
            for r in forecasts
        ]
        context["planning_rebase_policy"] = (
            "本章按已保存正文、当前状态和未完成线索重新规划；旧详细预告不作为执行依据。不得为兑现旧预告重复已完成动作、改写物件来历或把拟发生结论当成事实。需要新的发现就先安排真实来源与桥接。"
        )
        from .meaning_organizer import reference_meanings

        meanings = reference_meanings(book)
        active_plans = {
            i: r
            for i, r in references["plans"].items()
            if meanings.get(reference_id("plan", i), {}).get("task_state")
            not in ("completed", "cancelled", "superseded")
        }
        context["resolved_intentions"] = [
            {"record": r, "meaning": meanings[reference_id("plan", i)]}
            for i, r in references["plans"].items()
            if i not in active_plans
        ]
        context["writing_state"] = public_state_view(
            writing_state_view(book["writing_state"], query, plans=active_plans)
        )
        for record in context["writing_state"]["records"]:
            self._add_state_meaning(record, meanings.get(record["reference_id"]))
        from .input_budget import select_qualified_state

        context["writing_state"] = select_qualified_state(context["writing_state"])

    def _add_event_reference_context(self, context, references):
        book = self.book
        context["event_first_contract"] = copy.deepcopy(EVENT_CONTRACT)
        for item in context["active_facts"]:
            binding = references["memory"].get(item["memory_id"])
            if binding:
                item["canonical_reference"] = {
                    "record_kind": public_type(binding["type"]),
                    "record_id": binding["id"],
                    "record_revision": binding["revision"],
                }
                item["reference_id"] = reference_id(binding["type"], binding["id"])
                item["reference_scope"] = binding["scope"]
        context.pop("continuity_contract")
        context["state_record_contract"] = copy.deepcopy(EVENT_STATE_CONTRACT)
        context["fact_bank_status"] += (
            " event_plan_state is simulated plan state. prose_excerpt quotes saved text, not current-world fact declarations. Memory IDs are never state preconditions; select references via reference_selection_contract."
        )
        context["calculation_contract"]["instruction"] += (
            " Only planner declares time_calculations before event freeze. Writer can use frozen tokens but cannot add or change calculation inputs."
        )
        context["interface_contract_version"] = 2
        context["memory_bank_revision"] = context.pop("checkpoint_revision")
        for record in context["writing_state"]["records"]:
            if record["record_kind"] == "fact_record":
                record["update_selector"] = {
                    "record_subject": record["subject"],
                    "record_property_name": record["property_name"],
                }
        from .input_budget import select_qualified_state
        from .projection_grounding import qualify_state_view

        context["event_plan_state"] = select_qualified_state(
            qualify_state_view(book, context.pop("writing_state"))
        )
        from .reference_choices import CONTRACT as CHOICE_CONTRACT
        from .reference_choices import formal_operation_catalogue

        context["reference_choices"] = list(
            dict.fromkeys(
                r["reference_id"] for r in context["event_plan_state"]["records"]
            )
        )
        context["reference_selection_contract"] = CHOICE_CONTRACT
        context["reference_choices_by_kind"] = {
            kind: [
                i
                for i, v in enumerate(context["reference_choices"], 1)
                if v.startswith(kind + ":")
            ]
            for kind in sorted(
                {v.split(":", 1)[0] for v in context["reference_choices"]}
            )
        }
        from .reference_choices import FIELD_KINDS

        context["reference_choices_by_field"] = {
            field: [
                i
                for i, v in enumerate(context["reference_choices"], 1)
                if v.split(":", 1)[0] in kinds
            ]
            for field, kinds in FIELD_KINDS.items()
        }
        context["state_record_contract"]["instruction"] = (
            "operation选操作，record_kind是只读类别；按目录字段填值。新编号由程序生成，引用仅用reference_selection_contract选择器，属性显示名自由。"
        )
        context["state_record_contract"].pop("reference_contract", None)
        for index, row in enumerate(context["event_plan_state"]["records"], 1):
            row["record_choice"] = index
        context["event_first_contract"]["instruction"] = (
            "scenes每项必须purpose/participants/beats；beats每项必须statement/assertion_scope/requires/changes。requires和changes无内容填[]。不填id。引用遵循reference_selection_contract，changes用state_record_contract的operation及字段。"
        )
        context["event_first_contract"].pop("dependency_examples", None)
        context["state_record_contract"]["schemas"] = formal_operation_catalogue()
        context["reference_protocol"] = "choices_v1"

    def _add_event_memory_context(self, context):
        book = self.book
        memory = book["memory"]
        context["retrieved_memory"] = public_memory_rows(context.pop("active_facts"))
        context["retrieved_prose_evidence"] = [
            r
            for r in context["retrieved_memory"]
            if r["memory_kind"] == "prose_excerpt"
        ]
        context["retrieved_memory"] = [
            r
            for r in context["retrieved_memory"]
            if r["memory_kind"] != "prose_excerpt"
        ]
        context["memory_meaning_policy"] = (
            "meaning按原话含义单元标明视角、证实程度、当前有效性及任务进度；原文证据单列，不能整体当作当前事实。降级/召回不改变这些标签。"
        )
        context["memory_context_status"] = context.pop("fact_bank_status")
        context["content_unchecked_chapters"] = context.pop("unresolved_chapters")
        from .prose_memory import verify_prose_coverage

        context["memory_coverage"].update(
            processing_complete=not book["pending"],
            prose_storage_complete=all(
                verify_prose_coverage(memory, c)
                for c in book["chapters"]
                if c.get("prose_policy") == "unchecked"
            ),
            event_alignment_complete=not memory.get("projection_omissions", {})
            and not context["unprojected_chapters"],
        )
        from .projection_grounding import retryable_chapters

        context["memory_coverage"]["structured_pending_chapters"] = retryable_chapters(
            memory
        )
        context["memory_context_status"] += (
            " Structured prose memories quote actual saved prose with model-selected subject/property bindings; their semantic correctness is not certified. They do not confirm simulated plan-state preconditions."
        )
        context["memory_coverage"].pop("complete", None)

    @staticmethod
    def _bound(context):
        size = len(canonical(context).encode("utf-8"))
        from inf_writer.narrative_context import REPAIR_HEADROOM_BYTES

        limit = 84000 + (
            REPAIR_HEADROOM_BYTES if context.get("event_preflight_error") else 0
        )
        if size > limit:
            from .input_budget import fit

            bounded = fit(context, limit)
            context.clear()
            context.update(bounded)
            size = len(canonical(context).encode("utf-8"))
        if size > limit:
            raise ContextCapacityError(
                f"Writing context exceeds explicit budget: {size}>{limit}; no silent truncation"
            )

    def catch_up(self, trace):
        while self.book["pending"]:
            number = self.book["pending"][0]
            row = self.book["outcomes"][number - 1]
            try:
                candidate, report = self.engine.advance(
                    self.book["memory"], self.book["chapters"], number, trace
                )
            except BaseException:
                row.update(memory_update_status="PENDING", status="DRAFT_UNCHECKED")
                self._save(trace, "MEMORY_PENDING")
                raise
            self.book["memory"] = candidate
            self.book["pending"].pop(0)
            row.update(
                memory_update_status="APPLIED",
                memory_promoted=True,
                memory_report=report,
                withheld_mutations=report["withheld_mutations"],
                memory_semantic_review="canonical_event_projection"
                if report.get("canonical_projection")
                else "independent_model_review_not_certified",
                stop_reason=None,
            )
            if row.get("review", {}).get("approved") and not row["withheld_mutations"]:
                row["status"] = "DRAFT_CHECKED"
            self._save(trace, "MEMORY_COMMITTED")

    def attempt_memory(self, trace):
        """One ordered queue pass per chapter; failure never blocks prose."""
        try:
            self.catch_up(trace)
        except Exception as exc:
            failure = {
                "chapter": self.book["pending"][0],
                "after_written_chapter": len(self.book["chapters"]),
                "error_type": type(exc).__name__,
                "error": str(exc)
                if isinstance(exc, ContractError)
                else "Memory processing failed",
                "policy": "DEFERRED_CONTINUE_WRITING",
            }
            self.book.setdefault("memory_failures", []).append(failure)
            self.book["outcomes"][failure["chapter"] - 1].setdefault(
                "memory_errors", []
            ).append(failure)
            self._save(trace, "MEMORY_DEFERRED_CONTINUE_WRITING")
            return False
        return True

    def finish_structured_memory(self):
        from .projection_grounding import pending_chapters

        if not pending_chapters(self.book["memory"]):
            return
        trace = []
        try:
            candidate = self.engine.repair_structured_memory(
                self.book["memory"],
                self.book["chapters"],
                trace,
                max_chapters=len(pending_chapters(self.book["memory"])),
            )
            self.book["memory"] = candidate
            self._save(trace, "STRUCTURED_MEMORY_FINAL_CATCHUP")
        except Exception as exc:
            self.book.setdefault("structured_memory_failures", []).append(
                {
                    "error_type": type(exc).__name__,
                    "policy": "DEFERRED_CONTINUE_WRITING",
                }
            )
            self._save(trace, "STRUCTURED_MEMORY_FINAL_DEFERRED")

    def finish_memory_organization(self):
        if not self.plan.get("event_first", True):
            return
        from inf_writer.memory_meaning import pending_ids

        if not self.book["chapters"] or not pending_ids(self.book["memory"]):
            return
        from .meaning_organizer import organize

        trace = []
        self.book["memory"] = organize(
            self.book["memory"],
            self.book["chapters"],
            len(self.book["chapters"]),
            self.gateway,
            trace,
            max_batches=3,
        )
        self._save(trace, "MEMORY_MEANING_FINAL_PASS")

    def finish_titles(self):
        from .chapter_titles import assign

        trace = []
        for key in list(self.book.get("chapter_title_jobs", {}))[:3]:
            assign(self.book, self.book["chapters"][int(key) - 1], self.gateway, trace)
        if trace:
            self._save(trace, "CHAPTER_TITLES_FINAL_PASS")

    def attempt_state_repair(self, trace=None, *, final=False, force=False):
        """One pending chapter per phase; recovery never blocks new prose."""
        if self.book.get("prepared_events"):
            return False
        trace = trace if trace is not None else []
        phase = ("final:" if final else "after:") + str(len(self.book["chapters"]))
        jobs = self.book.get("state_repair_jobs", {})
        eligible = [
            n
            for n in sorted(jobs, key=int)
            if force or phase not in jobs[n].get("attempted_phases", [])
        ]
        if not eligible:
            return False
        key = eligible[0]
        job = jobs[key]
        job.setdefault("attempted_phases", []).append(phase)
        job["attempts"] = job.get("attempts", 0) + 1
        self._save(trace, "SAVED_PROSE_STATE_RECOVERY_STARTED")
        before = copy.deepcopy(self.book)
        try:
            from .state_recovery import recover

            candidate = recover(self.book, int(key), self.gateway, trace)
            self.book = candidate
            try:
                self._save(trace, "SAVED_PROSE_STATE_RECOVERED")
            except BaseException:
                self.book = before
                raise
            return True
        except Exception as exc:
            self.book = before
            self.book["state_repair_jobs"][key]["last_error"] = (
                str(exc) if isinstance(exc, ContractError) else type(exc).__name__
            )
            self._save(trace, "SAVED_PROSE_STATE_RECOVERY_DEFERRED")
            return False

    def _review_pending(self, trace):
        if not self.plan.get("story_review_enabled", True):
            return
        for key in sorted(self.book["review_jobs"], key=int):
            row = self.book["outcomes"][int(key) - 1]
            context = self.book["review_jobs"][key]
            start = len(self.story_gateway.transforms)
            try:
                review = self.agents["reviewer"].run(context, trace)
            except Exception as exc:
                row.update(status="DRAFT_UNCHECKED", stop_reason=None)
                failure = {
                    "chapter": int(key),
                    "after_written_chapter": len(self.book["chapters"]),
                    "error_type": type(exc).__name__,
                    "error": str(exc)
                    if isinstance(exc, ContractError)
                    else "Review service failed",
                    "policy": "DEFERRED_CONTINUE_WRITING",
                }
                row.setdefault("review_errors", []).append(failure)
                self.book.setdefault("review_failures", []).append(failure)
                self._save(trace, "REVIEW_DEFERRED_CONTINUE_WRITING")
                # End this queue pass: do not retry the same failing service for
                # every pending chapter before allowing another prose chapter.
                break
            finally:
                trace.extend(copy.deepcopy(self.story_gateway.transforms[start:]))
            row.update(
                review=review,
                issues=review["issues"],
                suggestions=review["suggestions"],
                stop_reason=None,
                story_review_status="REPORTED",
                unresolved_review_issues=review.get("unresolved_issues", []),
                dismissed_review_issues=review.get("dismissed_issues", []),
                status="DRAFT_CHECKED"
                if review["approved"]
                and row["memory_update_status"] == "APPLIED"
                and not row.get("withheld_mutations")
                else "DRAFT_UNCHECKED",
            )
            del self.book["review_jobs"][key]
            self._save(trace, "CHAPTER_REVIEWED")

    def finish_pending(self):
        from .graph_runtime import new_run

        run = new_run(self, "")
        run["recovery_only"] = True
        self.last_graph_trace = run["trace"]
        self.graph.invoke({"run": run}, config={"recursion_limit": 32})

    def attempt_narrative_repair(self, trace=None, *, final=False):
        from .narrative_planning import pending_planning_jobs
        from .narrative_repair import attempt, queue_ending_intent_review

        if final:
            queue_ending_intent_review(self.book)
        if not pending_planning_jobs(self.book):
            return
        attempt(
            self,
            trace if trace is not None else [],
            final=final,
            max_jobs=len(pending_planning_jobs(self.book)) if final else 1,
        )

    def write_next(self, instruction):
        from .graph_runtime import new_run

        run = new_run(self, instruction)
        row = run["row"]
        trace = run["trace"]
        number = run["number"]
        self.last_graph_trace = trace
        try:
            self.graph.invoke({"run": run}, config={"recursion_limit": 32})
        except Exception as exc:
            row["errors"].append(
                str(exc) if isinstance(exc, ContractError) else type(exc).__name__
            )
            if self.plan.get("event_first", True):
                row["stop_reason"] = "EVENT_FIRST_WRITING_UNRESOLVED"
                trace.append(
                    {
                        "role": "event_first_attempt",
                        "chapter": number,
                        "status": "UNRESOLVED",
                        "error_type": type(exc).__name__,
                        "error": str(exc)
                        if isinstance(exc, ContractError)
                        else "Writing step failed; prepared events retained",
                    }
                )
            else:
                row["stop_reason"] = row["stop_reason"] or "NO_USABLE_DRAFT"
            self._save(trace, row["stop_reason"])
        return copy.deepcopy(row)

    def _prepare_events(self, instruction, number, trace):
        saved = self._load_prepared_events(number, trace)
        if saved and not saved.get("revision_request"):
            return copy.deepcopy(saved)
        context = self._event_planning_context(instruction, number, saved)
        return self._run_event_planner(context, saved, number, trace)

    def _run_event_planner(self, context, saved, number, trace):
        key = str(number)
        draft = _EventPlanDraft()

        def accept(prepared, source):
            return self._accept_event_plan(
                prepared, source, draft, saved, number, trace
            )

        attempts = self.book.setdefault("planning_attempts", {})
        remaining = max(0, 5 - attempts.get(key, 0))
        for _attempt in range(remaining):
            self._bound_event_planning(context)
            start = len(trace)
            attempts[key] = attempts.get(key, 0) + 1
            agent = self._event_planner(context)
            validate = partial(
                self._validate_event_plan,
                context=context,
                number=number,
                trace=trace,
                draft=draft,
            )
            try:
                proposal = agent.run(context, trace, validator=validate)
            except ContractError as exc:
                if not self._planner_output_rejected(trace[start:]):
                    raise
                if attempts[key] >= 5:
                    return self._recover_event_plan(
                        exc, context, draft, number, trace, accept
                    )
                context = self._retry_event_plan_format(context, exc, trace[start:])
                self._save(trace, "PLANNING_OUTPUT_REJECTED_RETRY")
                continue
            try:
                prepared = self._simulate_event_plan(proposal, number)
                return accept(prepared, draft.public_proposal)
            except ContractError as exc:
                self._record_event_simulation_rejection(proposal, exc, trace)
                if attempts[key] >= 5:
                    return self._recover_event_plan(
                        exc, context, draft, number, trace, accept
                    )
                self._event_preflight_feedback(
                    context, proposal, draft.public_proposal, exc
                )
        raise PlanningOutputFailure("Five planner outputs exhausted for this chapter")

    def _load_prepared_events(self, number, trace):
        key = str(number)
        saved = self.book["prepared_events"].get(key)
        from .evidence_access import OBSERVATION_POLICY_VERSION

        if saved and not saved.get("revision_request"):
            # Cache invalidation may replace a valid outdated plan, never hide
            # damaged state or broken source chains by silently replanning it.
            verify_events(saved["commit"])
            verify_stage_realizations(saved)
            if saved["commit"]["base_state_sha256"] != digest(
                canonical(self.book["writing_state"])
            ):
                raise ContractError(
                    "Prepared events no longer match committed canonical state"
                )
        if (
            saved
            and "public_proposal" in saved
            and not saved.get("stage_realizations")
            and not saved.get("revision_request")
            and saved.get("evidence_observation_policy") != OBSERVATION_POLICY_VERSION
        ):
            saved = copy.deepcopy(saved)
            saved["revision_request"] = (
                "证据载体与观察条件规则已更新，旧方案尚未落笔；依据已保存原文重新核对材料身份、取得方式与观察条件，不能沿用不成立的取证行动。"
            )
            self.book["prepared_events"][key] = copy.deepcopy(saved)
            self._save(trace, "PREPARED_OBSERVATION_POLICY_CHANGED_REPLAN")
        return saved

    def _event_planning_context(self, instruction, number, saved):
        key = str(number)
        try:
            context = self.context(instruction, instruction)
        except ContextCapacityError as exc:
            raise PlanningOutputFailure(str(exc)) from exc
        from .narrative_planning import CONTRACT as NARRATIVE_CONTRACT

        context["narrative_design_contract"] = copy.deepcopy(NARRATIVE_CONTRACT)
        if getattr(self, "chapter_length_target", None) is not None:
            from .story_budget import chapter_budget

            context["length_budget"] = copy.deepcopy(
                self.book.get("length_budget", {}).get("chapters", {}).get(key)
                or chapter_budget(self.plan, self.book["chapters"], number)
            )
            context["length_budget"]["instruction"] = (
                "写作前按预算规划场景，空间不足时合并相邻场景；为最后的主线终局保留完整场景。"
            )
        if saved:
            context["event_revision_request"] = saved["revision_request"]
            if "public_proposal" not in saved:
                raise ContractError(
                    "Prepared revision lacks the original public proposal"
                )
            context["previous_event_plan"] = copy.deepcopy(saved["public_proposal"])
        return context

    def _validate_event_plan(
        self, value, context, number, trace, draft, *, preserve_design=False
    ):
        from .narrative_planning import normalize as normalize_design

        value = copy.deepcopy(value)
        draft.last_design, notes = normalize_design(
            value.pop(
                "narrative_plan",
                copy.deepcopy(draft.last_design) if preserve_design else None,
            ),
            len(value["scenes"]) if isinstance(value.get("scenes"), list) else 0,
        )
        if notes:
            trace.append(
                {
                    "role": "narrative_design",
                    "status": "OPTIONAL_FIELDS_IGNORED",
                    "notes": notes,
                }
            )
        incoming = copy.deepcopy(value)
        draft.last_public = copy.deepcopy(value)
        from .reference_choices import compile_plan

        value = compile_plan(
            value,
            context["reference_choices"],
            number,
            reference_records=context["event_plan_state"]["records"],
            require_target_identity=True,
        )
        if type(value["number"]) is not int or value["number"] != number:
            raise ContractError("Planner must address next chapter")
        numbers = [r["number"] for r in value["future_updates"]]
        if len(numbers) != len(set(numbers)) or any(
            n <= number or n > self.plan["max_chapters"] for n in numbers
        ):
            raise ContractError(
                "Future updates must address distinct unwritten chapters"
            )
        if not isinstance(value.get("scenes"), list):
            raise ContractError("Event-first planner must declare scenes")
        normalized = value
        try:
            normalized, _ = normalize_plan(
                value,
                self.book["writing_state"],
                number,
                references=reference_catalogue(self.book),
            )
            validate_plan_shape(normalized)
        except ContractError as exc:
            from .interface_contract import public_repair_details

            exc.repair_details = public_repair_details(
                getattr(exc, "repair_details", {}), normalized
            )
            raise
        calculate(value.get("time_calculations", []))
        draft.public_proposal = incoming
        draft.last_compiled = copy.deepcopy(value)
        return value

    def _accept_event_plan(self, prepared, source, draft, saved, number, trace):
        from .evidence_access import OBSERVATION_POLICY_VERSION

        key = str(number)
        prepared["evidence_observation_policy"] = OBSERVATION_POLICY_VERSION
        if draft.last_design:
            prepared["narrative_plan"] = copy.deepcopy(draft.last_design)
            prepared["narrative_plan_sha256"] = digest(canonical(draft.last_design))
        prepared["public_proposal"] = copy.deepcopy(source)
        prepared["revision_count"] = (saved or {}).get("revision_count", 0)
        self.book["prepared_events"][key] = copy.deepcopy(prepared)
        trace.append(
            {
                "role": "event_simulation",
                "status": "PREPARED",
                "commit_sha256": prepared["commit"]["sha256"],
                "before_state_sha256": prepared["commit"]["base_state_sha256"],
                "after_state_sha256": prepared["commit"]["state_sha256"],
            }
        )
        self._save(trace, "EVENTS_PREPARED_NOT_COMMITTED")
        return prepared

    def _repair_event_plan(self, error, context, draft, number, trace):
        from .interface_contract import public_repair_details
        from .plan_repair import repair
        from .stage_planning import prepare_stages

        def validate_repair(fixed):
            checked = self._validate_event_plan(
                fixed, context, number, trace, draft, preserve_design=True
            )
            prepare_events(
                self.book["writing_state"],
                checked,
                number,
                references=reference_catalogue(self.book),
            )

        fixed = repair(
            self.gateway,
            draft.last_public,
            context["reference_choices"],
            public_repair_details(
                getattr(error, "repair_details", {}), draft.last_compiled or {}
            ),
            trace,
            reference_records=context["event_plan_state"]["records"],
            validator=validate_repair,
        )
        compiled = self._validate_event_plan(
            fixed, context, number, trace, draft, preserve_design=True
        )
        prepare_events(
            self.book["writing_state"],
            compiled,
            number,
            references=reference_catalogue(self.book),
        )
        return (
            prepare_stages(
                self.book["writing_state"],
                compiled,
                number,
                reference_catalogue(self.book),
            ),
            fixed,
        )

    def _recover_event_plan(self, error, context, draft, number, trace, accept):
        from .stage_planning import prepare_stages

        if draft.last_public is not None:
            try:
                packet, fixed = self._repair_event_plan(
                    error, context, draft, number, trace
                )
                return accept(packet, fixed)
            except Exception as repair_error:
                trace.append(
                    {
                        "role": "state_repair",
                        "status": "DEFERRED",
                        "error_type": type(repair_error).__name__,
                        "error": str(repair_error)
                        if isinstance(repair_error, ContractError)
                        else "Local repair unavailable",
                    }
                )
        if draft.last_compiled is not None:
            packet = prepare_stages(
                self.book["writing_state"],
                draft.last_compiled,
                number,
                reference_catalogue(self.book),
            )
            return accept(packet, draft.public_proposal)
        if draft.last_public is not None:
            try:
                from .reference_choices import compile_independent_stages

                compiled, deferred = compile_independent_stages(
                    draft.last_public,
                    context["reference_choices"],
                    number,
                    reference_records=context["event_plan_state"]["records"],
                    require_target_identity=True,
                )
                packet = prepare_stages(
                    self.book["writing_state"],
                    compiled,
                    number,
                    reference_catalogue(self.book),
                    deferred,
                )
            except ContractError:
                raise PlanningOutputFailure(str(error)) from error
            return accept(packet, draft.last_public)
        raise PlanningOutputFailure(str(error)) from error

    def _bound_event_planning(self, context):
        try:
            self._bound(context)
        except ContextCapacityError as exc:
            raise PlanningOutputFailure(str(exc)) from exc

    def _event_planner(self, context):
        agent = copy.copy(self.agents["planner"])
        if context.get("output_was_truncated"):
            agent.max_output_tokens = min(65536, agent.max_output_tokens * 2)
        return agent

    def _retry_event_plan_format(self, context, error, attempt_trace):
        from .interface_contract import public_repair_details

        previous = next(
            (
                r.get("raw_output")
                for r in reversed(attempt_trace)
                if r.get("role") == "planner"
            ),
            None,
        )
        details = public_repair_details(getattr(error, "repair_details", {}), {})
        from inf_writer.narrative_context import prepare_repair

        context = prepare_repair(context, error, previous, details)
        context["event_preflight_error"] = {
            "error": str(error),
            "instruction": "Repair listed output errors; do not invent references or treat intentions as completed actions.",
        }
        if any(r.get("finish_reason") == "length" for r in attempt_trace):
            context["output_was_truncated"] = True
        return context

    def _simulate_event_plan(self, proposal, number):
        # Verify the whole event plan before preparing independent writing stages.
        prepare_events(
            self.book["writing_state"],
            proposal,
            number,
            references=reference_catalogue(self.book),
        )

        from .stage_planning import prepare_stages

        return prepare_stages(
            self.book["writing_state"],
            proposal,
            number,
            reference_catalogue(self.book),
        )

    @staticmethod
    def _planner_output_rejected(attempt_trace):
        return any(
            row.get("role") == "planner"
            and row.get("status") in ("FORMAT_FAILED", "INPUT_REJECTED")
            for row in attempt_trace
        )

    @staticmethod
    def _record_event_simulation_rejection(proposal, error, trace):
        trace.append(
            {
                "role": "event_simulation",
                "status": "REJECTED",
                "proposal": proposal,
                "error": str(error),
                "repair_details": getattr(error, "repair_details", None),
            }
        )

    @staticmethod
    def _event_preflight_feedback(context, proposal, source, error):
        from .interface_contract import public_repair_details

        context.pop("repair", None)
        context["event_preflight_error"] = {
            "error": str(error),
            "details": public_repair_details(
                getattr(error, "repair_details", {}), proposal
            ),
            "previous_plan": copy.deepcopy(source),
            "instruction": "Replan only unwritten events; resolve preconditions before any prose, preserve committed history. Keep the public fields; IDs are program-owned.",
        }

    def _continue_prose(self, instruction, number, trace, prior_outputs=(), **scope):
        return continue_prose(
            self.gateway,
            self.book,
            instruction,
            number,
            trace,
            prior_outputs,
            save_progress=lambda: self._save(trace, "PROSE_FRAGMENT_SAVED"),
            **scope,
        )

    def _realize_stages(self, prepared, number, trace, row):
        """Append one scoped writing unit, preserving its source transactions."""
        units = self._ensure_writing_units(prepared, number, trace)
        for unit in units[len(prepared["stage_realizations"]) :]:
            self._write_stage_unit(prepared, unit, number, trace, row)
        return "\n\n".join(c["text"] for c in prepared["stage_realizations"])

    def _ensure_writing_units(self, prepared, number, trace):
        from .narrative_planning import design_units

        packets = prepared["stage_packets"]
        key = str(number)
        verify_stage_realizations(prepared)
        target = getattr(self, "chapter_length_target", None)
        budget = self.book.get("length_budget", {}).get("chapters", {}).get(key, {})
        minimum = budget.get("minimum_scene_han", max(1, (target or 1) // 4))
        if "writing_units" not in prepared:
            prepared["writing_units"] = design_units(
                packets, target, minimum, prepared.get("narrative_plan", {})
            )
            self.book["prepared_events"][key] = copy.deepcopy(prepared)
            self._save(trace, "WRITING_UNITS_PLANNED")
        units = prepared["writing_units"]
        if [i for unit in units for i in unit["packet_indexes"]] != list(
            range(len(packets))
        ):
            raise ContractError(
                "Writing units must cover every event transaction in order"
            )
        return units

    def _write_stage_unit(self, prepared, unit, number, trace, row):
        from inf_writer.narrative_context import event_role_context

        from .narrative_planning import advance_writer_context, writer_contract
        from .writing_units import combined_commit, join_fragment

        packets = prepared["stage_packets"]
        units = prepared["writing_units"]
        key = str(number)
        sources = [packets[i] for i in unit["packet_indexes"]]
        packet = {"commit": combined_commit([p["commit"] for p in sources])}
        ordinal = len(prepared["stage_realizations"]) + 1
        earlier = "\n\n".join(c["text"] for c in prepared["stage_realizations"])
        view = writer_view(packet)
        purpose = "；".join(s["purpose"] for s in view["scenes"])
        task = {
            "unit_number": ordinal,
            "total_units": len(units),
            "target_han_chars": unit["target_han_chars"],
            "purpose": purpose,
            "events": view["scenes"],
            "completed_scene_ids": [
                s["id"]
                for p in packets[: unit["packet_indexes"][0]]
                for s in p["commit"]["scenes"]
            ],
            "output_scope": "Only newly written prose for these events; prior prose is read-only and must not be returned.",
        }
        task["scene_continuity"] = writer_contract(
            prepared, unit, ordinal, len(units), earlier
        )
        stage_instruction = (
            f"仅写第{ordinal}/{len(units)}个写作单元：{purpose}。"
            f"本单元约{unit['target_han_chars']}汉字。只返回本单元新增正文，不重开整章，不改写前文，不提前写后续事件。"
        )
        try:
            context = self.context(stage_instruction, purpose)
            context["chapter_plan"] = {
                "number": number,
                "title": prepared["proposal"]["title"],
                "brief": purpose,
            }
            context.pop("planned_next_chapters", None)
            context["frozen_events"] = view
            context["quantity_sources"] = quantity_sources(packet["commit"])
            context["quantity_policy"] = QUANTITY_POLICY
            context["prose_content_checks"] = "disabled"
            context["stage_task"] = task
            context["previous_prose_tail"] = {
                "text": earlier[-4000:],
                "read_only": True,
                "omitted_characters": max(0, len(earlier) - 4000),
            }
            advance_writer_context(context, self.book, number, earlier)
            context = event_role_context(context, "writer")
            self._bound(context)
            output = self._run_stage_writer(
                context, stage_instruction, number, trace, task, earlier
            )
            if "event_revision_request" in output:
                if not earlier:
                    raise StageRevisionRequested(output["event_revision_request"])
                output = {
                    "text": self._continue_prose(
                        stage_instruction,
                        number,
                        trace,
                        stage_task=task,
                        previous_tail=earlier[-4000:],
                    )
                }
                row.setdefault("generation_warnings", []).append(
                    {
                        "stage": "stage_revision",
                        "event_stage": sources[0]["stage"],
                        "policy": "CONTINUE_STAGE_PROSE",
                    }
                )
            try:
                prose = render_prose(
                    output["text"], packet["commit"], context["quantity_sources"]
                )
            except ContractError as exc:
                prose = output["text"]
                row.setdefault("generation_warnings", []).append(
                    {
                        "stage": "stage_prose_reference",
                        "event_stage": sources[0]["stage"],
                        "error": str(exc),
                        "policy": "PRESERVE_LITERAL_PROSE",
                    }
                )
        except ContextCapacityError:
            prose = self._continue_prose(
                stage_instruction,
                number,
                trace,
                stage_task=task,
                previous_tail=earlier[-4000:],
            )
        report = None
        if unit["target_han_chars"] is not None:
            from .length_control import adjust

            prose, report = adjust(
                prose,
                unit["target_han_chars"],
                self.book,
                number,
                self.gateway,
                trace,
                stage_task=task,
            )
        raw_prose = prose
        prose, seam_report = join_fragment(earlier, raw_prose)
        prepared["stage_realizations"].append(
            {
                "stage": sources[0]["stage"],
                "text": prose,
                "sha256": digest(prose),
                "raw_text": raw_prose,
                "raw_sha256": digest(raw_prose),
                "seam_report": seam_report,
                "source_stages": [p["stage"] for p in sources],
                "source_commit_sha256s": [p["commit"]["sha256"] for p in sources],
                "commit_sha256": packet["commit"]["sha256"],
                "length_report": report,
            }
        )
        self.book["prepared_events"][key] = copy.deepcopy(prepared)
        self._save(trace, "EVENT_STAGE_PROSE_SAVED_NOT_CHAPTER_COMMITTED")

    def _run_stage_writer(
        self, context, stage_instruction, number, trace, task, earlier
    ):
        ordinal = task["unit_number"]
        start = len(trace)
        try:
            if (
                self.book.get("prose_fragments", {})
                .get(f"{number}:{ordinal}", {})
                .get("status")
                == "PENDING"
            ):
                output = {
                    "text": self._continue_prose(
                        stage_instruction,
                        number,
                        trace,
                        stage_task=task,
                        previous_tail=earlier[-4000:],
                    )
                }
            else:
                output = self.agents["writer"].run(context, trace)
        except ContractError:
            if not any(
                t.get("role") == "writer"
                and t.get("status") in ("FORMAT_FAILED", "INPUT_REJECTED")
                for t in trace[start:]
            ):
                raise
            raw = [
                t.get("raw_output")
                for t in trace[start:]
                if t.get("role") == "writer"
                and t.get("finish_reason") in ("stop", None)
            ]
            output = {
                "text": self._continue_prose(
                    stage_instruction,
                    number,
                    trace,
                    raw,
                    stage_task=task,
                    previous_tail=earlier[-4000:],
                )
            }
        return output

    def _graph_event_plan(self, run):
        instruction = run["instruction"]
        number = run["number"]
        key = str(number)
        trace = run["trace"]
        row = run["row"]
        try:
            prepared = self._prepare_events(instruction, number, trace)
        except PlanningOutputFailure as exc:
            prepared = unplanned_packet(
                self.book["writing_state"],
                number,
                instruction,
                title=self.book["plan"].get(key, {}).get("title"),
            )
            self.book["prepared_events"][key] = copy.deepcopy(prepared)
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "planning",
                    "error": str(exc),
                    "policy": "CONTINUE_PROSE_WITHOUT_STATE_CHANGES",
                }
            )
            self._save(trace, "PLANNING_DEFERRED_CONTINUE_PROSE")

        run.update(prepared=prepared, revision_requested=False)

    def _graph_event_writer(self, run):
        row = run["row"]
        prepared = run["prepared"]
        while True:
            deferred = self._record_deferred_stages(prepared, row)
            staged = bool(prepared.get("stage_packets")) and (
                len(prepared["stage_packets"]) > 1 or bool(deferred)
            )
            if staged:
                context, output = self._write_staged_chapter(run, prepared)
            else:
                context, output = self._write_event_chapter(run, prepared)
            if "event_revision_request" not in output:
                break

            revision = output["event_revision_request"]
            if prepared["revision_count"] < 1:
                self._save_event_revision(run, prepared, revision)
                return
            prepared = self._defer_event_revision(run, revision, staged=staged)
            if staged:
                run["prepared"] = prepared
        run.update(
            prepared=prepared, context=context, output=output, revision_requested=False
        )

    def _write_staged_chapter(self, run, prepared):
        context = {
            "recent_chapters": self.book["chapters"][-2:],
            "historical_memory": {"items": []},
            "quantity_sources": quantity_sources(prepared["commit"]),
        }
        try:
            prose = self._realize_stages(
                prepared, run["number"], run["trace"], run["row"]
            )
        except StageRevisionRequested as exc:
            return context, {"event_revision_request": str(exc)}
        return context, {"text": prose}

    def _save_event_revision(self, run, prepared, revision):
        prepared["revision_count"] += 1
        prepared["revision_request"] = revision
        self.book["prepared_events"][str(run["number"])] = copy.deepcopy(prepared)
        self._save(run["trace"], "EVENT_REVISION_REQUESTED_NOT_COMMITTED")
        run["revision_requested"] = True

    def _defer_event_revision(self, run, revision, *, staged):
        number = run["number"]
        prepared = unplanned_packet(
            self.book["writing_state"], number, run["instruction"]
        )
        self.book["prepared_events"][str(number)] = copy.deepcopy(prepared)
        warning = {
            "stage": "revision",
            "policy": "CONTINUE_PROSE_WITHOUT_STATE_CHANGES",
        }
        reason = "REVISION_DEFERRED_CONTINUE_PROSE"
        if staged:
            warning = {
                "stage": "stage_revision",
                "error": revision,
                "policy": "CONTINUE_PROSE_WITHOUT_STATE_CHANGES",
            }
            reason = "STAGE_REVISION_DEFERRED_CONTINUE_PROSE"
        run["row"].setdefault("generation_warnings", []).append(warning)
        self._save(run["trace"], reason)
        return prepared

    def _record_deferred_stages(self, prepared, row):
        deferred = [
            r for r in prepared.get("stage_reports", []) if r["status"] == "DEFERRED"
        ]
        if deferred:
            row["deferred_event_stages"] = copy.deepcopy(deferred)
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "event_stages",
                    "policy": "COMMIT_INDEPENDENT_VALID_STAGES",
                    "deferred_stages": [r["stage"] for r in deferred],
                }
            )
        return deferred

    def _write_event_chapter(self, run, prepared):
        instruction = run["instruction"]
        number = run["number"]
        trace = run["trace"]
        row = run["row"]
        if (
            prepared["commit"].get("event_plan_status") == "unavailable"
            or self.book.get("prose_fragments", {})
            .get(f"{number}:chapter", {})
            .get("status")
            == "PENDING"
        ):
            context = {
                "recent_chapters": self.book["chapters"][-2:],
                "historical_memory": {"items": []},
                "quantity_sources": [],
            }
            output = {"text": self._continue_prose(instruction, number, trace)}
            return context, output
        try:
            context = self.context(
                instruction,
                prepared["proposal"]["title"] + " " + prepared["proposal"]["brief"],
            )
        except ContextCapacityError as exc:
            context = {
                "recent_chapters": self.book["chapters"][-2:],
                "historical_memory": {"items": []},
                "quantity_sources": quantity_sources(prepared["commit"]),
            }
            output = {"text": self._continue_prose(instruction, number, trace)}
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "writer_context",
                    "error": str(exc),
                    "policy": "CONTINUE_WITH_BOUNDED_PROSE_CONTEXT",
                }
            )
            return context, output
        context["chapter_plan"] = {
            k: prepared["proposal"][k] for k in ("number", "title", "brief")
        }
        context["chapter_plan"]["narrative_plan"] = copy.deepcopy(
            prepared.get("narrative_plan", {})
        )
        context["frozen_events"] = writer_view(prepared)
        context["quantity_sources"] = quantity_sources(prepared["commit"])
        context["quantity_policy"] = QUANTITY_POLICY
        context["prose_content_checks"] = "disabled"
        from inf_writer.narrative_context import event_role_context

        context = event_role_context(context, "writer")
        try:
            self._bound(context)
        except ContextCapacityError as exc:
            output = {"text": self._continue_prose(instruction, number, trace)}
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "writer_context",
                    "error": str(exc),
                    "policy": "CONTINUE_WITH_BOUNDED_PROSE_CONTEXT",
                }
            )
            return context, output
        start = len(trace)
        try:
            output = self.agents["writer"].run(context, trace)
        except ContractError as exc:
            rejected = [
                r.get("raw_output")
                for r in trace[start:]
                if r.get("role") == "writer"
                and r.get("status") == "FORMAT_FAILED"
                and r.get("finish_reason") in ("stop", None)
            ]
            if not rejected and not any(
                r.get("role") == "writer" and r.get("status") == "INPUT_REJECTED"
                for r in trace[start:]
            ):
                raise
            output = {
                "text": self._continue_prose(instruction, number, trace, rejected)
            }
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "writer_format",
                    "error": str(exc),
                    "policy": "PRESERVE_PROSE_CONTINUE",
                }
            )
        return context, output

    def _render_event_draft(self, run):
        number = run["number"]
        trace = run["trace"]
        row = run["row"]
        prepared = run["prepared"]
        context = run["context"]
        template = run["output"]["text"]
        verify_events(prepared["commit"])
        if canonical(context["quantity_sources"]) != canonical(
            quantity_sources(prepared["commit"])
        ):
            raise ContractError("Quantity source table differs from its event data")
        encoding = "references"
        try:
            draft = render_prose(
                template, prepared["commit"], context["quantity_sources"]
            )
        except ContractError as exc:
            draft = template
            encoding = "literal"
            row.setdefault("generation_warnings", []).append(
                {
                    "stage": "prose_reference",
                    "error": str(exc),
                    "policy": "PRESERVE_LITERAL_PROSE",
                }
            )
        if draft != template:
            trace.append(
                {
                    "role": "event_realization",
                    "status": "REFERENCES_RENDERED",
                    "input_sha256": digest(template),
                    "output_sha256": digest(draft),
                }
            )
        length_report = None
        if getattr(
            self, "chapter_length_target", None
        ) is not None and not prepared.get("stage_realizations"):
            from .length_control import adjust

            revised, length_report = adjust(
                draft,
                self.chapter_length_target,
                self.book,
                number,
                self.gateway,
                trace,
            )
            if revised != draft:
                draft = revised
                template = revised
                encoding = "literal"
        return draft, template, encoding, length_report

    def _graph_event_commit(self, run):
        number = run["number"]
        key = str(number)
        trace = run["trace"]
        row = run["row"]
        prepared = run["prepared"]
        context = run["context"]
        draft, template, encoding, length_report = self._render_event_draft(run)
        if (
            digest(canonical(prepared["candidate_state"]))
            != prepared["commit"]["state_sha256"]
        ):
            raise ContractError("Prepared candidate state integrity failure")
        proposal = prepared["proposal"]
        from .chapter_titles import resolve_title

        title = resolve_title(
            proposal["title"],
            draft,
            number,
            self.book["plan"].get(key, {}).get("title"),
            gateway=self.gateway,
            trace=trace,
        )
        chapter = {
            "number": number,
            "title": title,
            "text": draft,
            "sha256": digest(draft),
            "event_commit": copy.deepcopy(prepared["commit"]),
            "realization_template": template,
            "prose_policy": "unchecked",
            "quantity_sources": copy.deepcopy(context["quantity_sources"]),
            "prose_encoding": encoding,
            "event_plan_status": prepared["commit"].get(
                "event_plan_status", "prepared"
            ),
            "time_calculations": copy.deepcopy(prepared["commit"]["computed_times"]),
        }
        if length_report is not None:
            chapter["length_report"] = length_report
        if "narrative_plan" in prepared:
            chapter["narrative_plan"] = copy.deepcopy(prepared["narrative_plan"])
            chapter["narrative_plan_sha256"] = prepared["narrative_plan_sha256"]
        if prepared.get("stage_realizations"):
            chapter["event_stage_sources"] = copy.deepcopy(
                prepared["stage_realizations"]
            )
        if prepared.get("stage_reports"):
            chapter["event_stage_reports"] = copy.deepcopy(prepared["stage_reports"])
        refs = {
            f"constraint_{i}": rule
            for i, rule in enumerate(self.book["constraints"], 1)
        }
        refs.update({f"draft_{s['id']}": s["text"] for s in evidence_segments(draft)})
        refs.update(
            {f"past_{c['number']}": c["text"] for c in context["recent_chapters"]}
        )
        refs.update(
            {
                f"past_memory_{i}": canonical(h)
                for i, h in enumerate(context["historical_memory"]["items"], 1)
            }
        )
        review_context = dict(context, current_draft=draft, hard_references=refs)
        # Event outcome and prose enter the same durable checkpoint. The
        # candidate was never treated as already happened before this point.
        previous_book = copy.deepcopy(self.book)
        self.book["chapters"].append(chapter)
        self.book["pending"].append(number)
        from .narrative_planning import publish

        publish(self.book, chapter, chapter.get("narrative_plan", {}))
        self.book["writing_state"] = copy.deepcopy(prepared["candidate_state"])
        del self.book["prepared_events"][key]
        self.book["plan"][key] = {k: proposal[k] for k in ("number", "title", "brief")}
        self.book["plan"][key]["title"] = title
        record_future_plan(self.book, proposal, self.plan["max_chapters"])
        row.update(
            status="DRAFT_UNCHECKED",
            memory_update_status="PENDING",
            writing_invariants="EVENT_DATA_COMMITTED_PROSE_UNCHECKED",
            event_commit_sha256=prepared["commit"]["sha256"],
            story_review_status="PENDING"
            if self.plan.get("story_review_enabled", True)
            else "DISABLED",
        )
        self.book["outcomes"].append(row)
        if chapter["event_plan_status"] in ("partial", "unavailable"):
            self.book.setdefault("state_repair_jobs", {})[key] = {
                "status": "PENDING",
                "chapter_sha256": chapter["sha256"],
                "deferred_stages": copy.deepcopy(row.get("deferred_event_stages", [])),
                "instruction": "Rebuild only from saved prose with source evidence; rejected proposals are not facts.",
            }
        if self.plan.get("story_review_enabled", True):
            self.book["review_jobs"][key] = review_context
        try:
            self._save(trace, "DRAFT_SAVED_MEMORY_PENDING")
        except BaseException:
            self.book = previous_book
            row.update(
                status="NO_DRAFT", memory_update_status="NOT_RUN", memory_promoted=False
            )
            raise

    def _graph_legacy_plan(self, run):
        instruction = run["instruction"]
        number = run["number"]
        trace = run["trace"]
        context = self.context(
            instruction,
            instruction
            + " "
            + (self.book["chapters"][-1]["title"] if self.book["chapters"] else ""),
        )

        def validate_plan(value):
            if type(value["number"]) is not int or value["number"] != number:
                raise ContractError("Planner must address next chapter")
            numbers = [r["number"] for r in value["future_updates"]]
            if any(
                n <= number or n > self.plan["max_chapters"] for n in numbers
            ) or len(numbers) != len(set(numbers)):
                raise ContractError(
                    "Future updates must address distinct unwritten chapters within the configured cap"
                )
            calculate(value.get("time_calculations", []))
            return value

        proposal = self.agents["planner"].run(context, trace, validator=validate_plan)

        run["proposal"] = proposal

    def _graph_legacy_writer(self, run):
        instruction = run["instruction"]
        number = run["number"]
        trace = run["trace"]
        row = run["row"]
        proposal = run["proposal"]
        context = self.context(
            instruction, proposal["title"] + " " + proposal["brief"] + " " + instruction
        )
        context["chapter_plan"] = proposal
        context["computed_times"] = calculate(proposal.get("time_calculations", []))
        self._bound(context)
        try:
            draft, calculations, metadata = write_with_calculations(
                self.agents["writer"], context, trace
            )
        except Exception:
            row["stop_reason"] = (
                "WRITING_TIME_CALCULATION_UNRESOLVED"
                if any(t["role"] == "writer_time_calculation" for t in trace)
                else "WRITING_OUTPUT_UNRESOLVED"
            )
            raise
        try:
            draft, writing_state = guard_continuity(
                self.book["writing_state"],
                metadata["updates"],
                metadata["no_change_reason"],
                draft,
                number,
                calculations,
                self.gateway,
                trace,
            )
        except Exception:
            row["stop_reason"] = "WRITING_CONTINUITY_UNRESOLVED"
            raise

        run.update(
            context=context,
            draft=draft,
            calculations=calculations,
            writing_state=writing_state,
        )

    def _graph_legacy_commit(self, run):
        number = run["number"]
        trace = run["trace"]
        row = run["row"]
        proposal = run["proposal"]
        context = run["context"]
        draft = run["draft"]
        calculations = run["calculations"]
        writing_state = run["writing_state"]
        from .chapter_titles import resolve_title

        title = resolve_title(
            proposal["title"],
            draft,
            number,
            self.book["plan"].get(str(number), {}).get("title"),
            gateway=self.gateway,
            trace=trace,
        )
        chapter = {
            "number": number,
            "title": title,
            "text": draft,
            "sha256": digest(draft),
            "time_calculations": calculations,
        }
        review_context = dict(context, current_draft=draft)
        refs = {
            f"constraint_{i}": rule
            for i, rule in enumerate(self.book["constraints"], 1)
        }
        refs.update({f"draft_{s['id']}": s["text"] for s in evidence_segments(draft)})
        refs.update(
            {f"past_{c['number']}": c["text"] for c in context["recent_chapters"]}
        )
        refs.update(
            {
                f"past_memory_{i}": canonical(h)
                for i, h in enumerate(context["historical_memory"]["items"], 1)
            }
        )
        review_context["hard_references"] = refs
        self.book["chapters"].append(chapter)
        self.book["pending"].append(number)
        from .narrative_planning import publish

        publish(self.book, chapter, chapter.get("narrative_plan", {}))
        self.book["writing_state"] = writing_state
        self.book["plan"][str(number)] = {
            k: proposal[k] for k in ("number", "title", "brief")
        }
        self.book["plan"][str(number)]["title"] = title
        record_future_plan(self.book, proposal, self.plan["max_chapters"])
        row.update(
            status="DRAFT_UNCHECKED",
            memory_update_status="PENDING",
            stop_reason=None,
            writing_invariants="VALIDATED_DECLARATIONS",
            story_review_status="PENDING"
            if self.plan.get("story_review_enabled", True)
            else "DISABLED",
        )
        self.book["outcomes"].append(row)
        if self.plan.get("story_review_enabled", True):
            self.book["review_jobs"][str(number)] = review_context
        self._save(trace, "DRAFT_SAVED_MEMORY_PENDING")
