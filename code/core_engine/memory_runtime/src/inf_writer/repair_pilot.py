"""Isolated, bounded repair probes. Never commits memory or changes prose."""
import copy
from datetime import datetime
from pathlib import Path
import time

from .agents import PROMPTS, validate
from .domain import ContractError, Snapshot, canonical, digest, strict_json
from .drafting import DuplicateMemoryError, normalize_memory
from .models import Budget, ModelGateway, ModelRequest
from .trial import RecordedProvider, save_new


def repair_payload(case):
    payload = copy.deepcopy(case["payload"])
    state = Snapshot.from_dict(case["state"])
    previous = validate("memory", strict_json(case["previous_output"]))
    try:
        normalize_memory(previous, state, payload["chapter_plan"], payload["current_draft"])
    except DuplicateMemoryError as exc:
        payload["repair"] = {"error": str(exc), "previous_output": case["previous_output"],
                             "details": copy.deepcopy(exc.repair_details),
                             "instruction": "只修复该记忆提案；返回完整changes，保留正文支持的知识与无关正确候选，不改正文、不捏造证据。"}
        return payload
    raise ContractError("Pilot case is not a duplicate-memory rejection")


def run_repair_pilot(output, provider, cases, *, max_calls=4, max_cost_usd=0.30):
    if type(max_calls) is not int or not 1 <= max_calls <= 4 or not 0 < max_cost_usd <= 0.30:
        raise ContractError("Pilot authorization cap is four calls and 0.30 USD estimate")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 4 or len({c["id"] for c in cases}) != len(cases):
        raise ContractError("One to four uniquely identified frozen cases required")
    before = digest(canonical(cases))
    requests = [ModelRequest("memory", PROMPTS["memory"], repair_payload(case), 8192) for case in cases]
    if any(len(canonical({"system": request.system, "payload": request.payload}).encode("utf-8")) > 120_000 for request in requests):
        raise ContractError("Pilot request input exceeds 120000-byte bound")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    save_new(output / "execution.json", {"started_at": datetime.now().astimezone().isoformat(),
                                        "case_hash": before, "max_calls": max_calls, "max_cost_usd": max_cost_usd})
    budget = Budget(max_calls=max_calls, max_cost_usd=max_cost_usd, max_seconds=600)
    recorder = RecordedProvider(provider, output)
    gateway = ModelGateway(recorder, budget, reserve_per_call=0.06)
    outcomes, termination = [], "ALL_CASES_ATTEMPTED"
    started = time.monotonic()
    for case, request in zip(cases, requests):
        if budget.calls >= max_calls:
            termination = "CALL_CAP"
            break
        row = {"id": case["id"], "mechanically_accepted": False, "error": None,
               "semantic_review": "PENDING_SEPARATE_REVIEW", "memory_committed": False}
        try:
            reply = gateway.complete(request)
        except Exception as exc:
            row.update(error=type(exc).__name__, usage_may_be_unknown=True)
            outcomes.append(row)
            termination = "PROVIDER_OR_RESOURCE_ERROR"
            break  # No network retry or extra repair, even if delivery is unknown.
        try:
            validated = validate("memory", strict_json(reply.content))
            state = Snapshot.from_dict(case["state"])
            normalized = normalize_memory(validated, state, case["payload"]["chapter_plan"], case["payload"]["current_draft"])
            row.update(mechanically_accepted=True, normalized_memory=normalized)
        except ContractError as exc:
            row["error"] = str(exc)
            if isinstance(getattr(exc, "repair_details", None), dict):
                row["repair_details"] = exc.repair_details
        outcomes.append(row)
        save_new(output / f"case_{len(outcomes):02d}.json", row)
        print({"case": row["id"], "mechanically_accepted": row["mechanically_accepted"]}, flush=True)
    result = {"scope": "KNOWN_DEVELOPMENT_CASE_REPAIR_PROBE_NOT_GENERALIZATION_OR_NST_COMPARISON",
              "ended_at": datetime.now().astimezone().isoformat(), "termination": termination,
              "case_count": len(cases), "attempted": len(outcomes), "not_run": len(cases) - len(outcomes),
              "calls": budget.calls, "recorded_provider_calls": recorder.calls,
              "mechanically_accepted": sum(r["mechanically_accepted"] for r in outcomes),
              "semantic_evaluation": "PENDING_SEPARATE_REVIEW", "outcomes": outcomes,
              "input_tokens": budget.input_tokens, "output_tokens": budget.output_tokens,
              "cost_estimate_not_bill": budget.cost_upper_usd,
              "max_calls": max_calls, "max_cost_usd": max_cost_usd,
              "elapsed_seconds": time.monotonic() - started, "inputs_unchanged": before == digest(canonical(cases))}
    save_new(output / "result.json", result)
    print({key: result[key] for key in ("termination", "calls", "mechanically_accepted", "cost_estimate_not_bill")}, flush=True)
    return result
