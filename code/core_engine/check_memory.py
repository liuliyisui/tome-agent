"""Opt-in continuous memory check on existing prose; never generates prose."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from memory_runtime.engine import MemoryEngine
from tome_writer.chat_provider import ChatCompletionProvider
from tome_writer.domain import ContractError, canonical
from tome_writer.trial import RecordedProvider, load_authorized_nst_secret


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _exception_details(exc):
    return {
        "error_type": type(exc).__name__,
        "error": str(exc)
        if isinstance(exc, ContractError)
        else "Sanitized runtime failure",
    }


def save_new(path, value):
    """Atomic create, no overwrite: a checkpoint is complete or absent."""
    path = Path(path)
    body = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=".memory-pending-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "nt":
            os.rename(temporary, path)  # Windows rename refuses existing targets.
        else:
            os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def source_hashes():
    folder = ROOT / "memory_runtime"
    result = {}
    for path in sorted(folder.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(folder)
        if (
            len(relative.parts) == 2
            and relative.parts[0] == "regression_tests"
            and path.name.startswith("test_")
        ):
            relative = Path(path.name)
        if len(relative.parts) == 2 and relative.parts[0] in (
            "writing_flow",
            "memory_processing",
            "events",
            "planning_review",
            "support",
        ):
            relative = Path(relative.name)
        name = relative.as_posix()
        if name in result:
            raise ContractError("Duplicate runtime source path")
        result[name] = sha(path)
    shared = ROOT / "tome_writer"
    for path in sorted(shared.rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "__init__.py":
            continue
        relative = path.relative_to(shared)
        if len(relative.parts) == 2 and relative.parts[0] in (
            "model_io",
            "writing_flow",
            "memory_system",
            "review_system",
            "foundation",
        ):
            relative = Path(relative.name)
        name = "src/tome_writer/" + relative.as_posix()
        if name in result:
            raise ContractError("Duplicate shared runtime source path")
        result[name] = sha(path)
    package_init = shared / "__init__.py"
    if package_init.is_file():
        result["src/tome_writer/__init__.py"] = sha(package_init)
    return result


_MIGRATION_MANIFEST_SHA256 = (
    "13f07c3f62833914bc04f8ddbfd64a97ef92e3874f531300505697bb615d8d26"
)


def _migration_manifest():
    path = ROOT / "package_migration_fingerprints.json"
    try:
        raw = path.read_bytes()
        if (
            hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
            != _MIGRATION_MANIFEST_SHA256
        ):
            return None
        result = json.loads(raw)
        return result if isinstance(result, dict) else None
    except (OSError, ValueError):
        return None


def _migration_key(name):
    parts = name.split("/")
    if len(parts) >= 3 and parts[0] == "src":
        parts[1] = "@package"
    return "/".join(parts)


def _matches_migration_profile(saved, current, manifest, profile):
    if not isinstance(saved, dict) or not isinstance(current, dict):
        return False
    old = {_migration_key(k): v for k, v in saved.items()}
    new = {_migration_key(k): v for k, v in current.items()}
    expected = manifest["sources"]
    historical = profile["sources"]
    if len(old) != len(saved) or len(new) != len(current):
        return False
    if set(old) != set(new) or set(old) != set(expected) or set(old) != set(historical):
        return False
    return all(old[k] in historical[k] and new[k] in expected[k]["new"] for k in old)


def reviewed_package_sources(saved, current):
    manifest = _migration_manifest()
    return bool(
        manifest
        and any(
            _matches_migration_profile(saved, current, manifest, profile)
            for profile in manifest["profiles"]
        )
    )


def reviewed_package_migration(saved, current):
    if not isinstance(saved, dict) or set(saved) != set(current):
        return False
    if saved.get("orchestration") != current.get("orchestration"):
        return False
    manifest = _migration_manifest()
    if not manifest:
        return False
    old_entries = saved.get("entrypoints")
    new_entries = current.get("entrypoints")
    if (
        not isinstance(old_entries, dict)
        or not isinstance(new_entries, dict)
        or set(old_entries) != set(new_entries)
    ):
        return False
    return any(
        _matches_migration_profile(
            saved.get("memory_runtime"),
            current.get("memory_runtime"),
            manifest,
            profile,
        )
        and set(old_entries) == set(profile["entrypoints"])
        and all(old_entries[k] in profile["entrypoints"][k] for k in old_entries)
        and all(
            new_entries[k] in manifest["entrypoints"][k]["new"]
            for k in new_entries
            if k != "check_memory.py"
        )
        for profile in manifest["profiles"]
    )


def _source_hashes_compatible(saved, current):
    """Recognize the reviewed test layout migration without weakening other checks."""
    if saved == current:
        return True
    if reviewed_package_sources(saved, current):
        return True
    if not isinstance(saved, dict) or set(saved) != set(current):
        return False
    reviewed = {
        "__init__.py": (
            {
                "975bd3f06cd496a8bd99d99467758577b900f26dbeedaa777540bf6a5cf7033e",
                "890b6e5312ce34b2350fc83fb84e8da10e5867875e834e9ba8d2a21c56db64f6",
            },
            {
                "d73c64e420486de88f16b05114eca36f2b5cf11981a112dc12c0d25a19d89355",
                "60dd234dbb192ae55a406466af02b3b8819365a96d4ed2143199bfc1952e942c",
                "75971f1cd086d6d8ffce07867bfa1eb9791c91c134b7808eaa19119a03ee7c7a",
                "246072924a44e69d8fea5549b05216a7e0a6f49289803f8c60c5c29c3973df35",
                "4dc82c78af81c1b7a1fcebe3093d6ad987b18aec7b397224ca2282e3814798b2",
                "ee83b48b652c7899954ba9e76cbc2125e216a24603282ad84562075100f8849f",
                "e89627fdde7480c129527bf3147df80a0ea9491c355de9873478585d1aa22117",
                "5ba85c8e98f0afad19d53097290909e2f5bb89de519bb7d5eabd5b209b4d5756",
            },
        ),
        "writing.py": (
            {
                "4dfe525d3bd41eb370a9aa1399685a2aa157e7ff7199493dc697475c8391a2ee",
                "e1ae27700b004b85c51ae4f10ee2b4419f78c9dd1ceeea398d313f8eba84af52",
                "c53fdec660b9366a27bd96c007f17337c3b49f1cb5a5592908e884f1e52238e4",
                "3117fbd1d9dced1b6198a9b7a1339d5529f61255a113c8ee62aa61fcd2bddc9c",
            },
            {
                "4e410553e296cdf8807d7011818a7fe3a32714ff5562f7d38e06a324d37b6923",
                "1b9a3cf8f32235c1965ec1a375df01771de2cb3f28e076213cbfc9cea740f365",
                "c5798af629f78c42d694eba56a97131bf8039e4f1cd30e5108daa09aaa81a40b",
                "2fe7734631e712ba9bb7b228ccfeb245429902033ed7aa0a130a1984cbfe3af3",
                "cd5c2cc06c09ba2e4c4f56d7799581300058ec5509c1a65caf37f2bc84d00f5c",
                "40070d46922d015b28509af2cef81c269117bfa081cab7c5614fbc8a876de61a",
                "5b3e1a6bdab21d8330a134d0e25eace13fcd9995f586fd1eed66294b2dbf04c7",
                "337b99a9cc8cb168e5c46e18e7fd36d4f37800aa16e5f9cf5f4bf638943f6a82",
                "e5601c0f69180e12300e1487876310b13f2997ef7e53c5a0e2f46a81485df287",
                "fa0bfefce93bb9fb649de433b4c853c70dbd230acc13ee092b2c139d6d185b27",
            },
        ),
        "src/tome_writer/chat_provider.py": (
            {
                "377bd96ce20115e12289834857b3d1b3ad6202154741cbd3556e3f297b7f1934",
                "08379dd7c866461fdc0ba132cadc8186dbecc847b2b0e42f042db7147e6d516d",
            },
            {
                "e71130cfc924ede737a959a51f145047002875231ef4ea1a854d900d00bb552f",
                "f46ccc6a166cb79c0c37fddc94026647132342e0584ea2e0f2a816e52dc56fce",
            },
        ),
    }
    return all(
        old == current[name]
        or (
            name in reviewed
            and old in reviewed[name][0]
            and current[name] in reviewed[name][1]
        )
        for name, old in saved.items()
    )


def execute(
    output, gateway, chapters, through, questions=None, resume=None, input_hash=None
):
    output = Path(output)
    memory = MemoryEngine.empty() if resume is None else resume["memory"]
    done = 0 if resume is None else resume["done_through"]
    if resume is not None and (
        resume.get("input_sha256") != input_hash
        or not _source_hashes_compatible(resume.get("runtime_sha256"), source_hashes())
    ):
        raise ContractError(
            "Resume input/runtime differs; require an explicit migration rather than silent reuse"
        )
    engine = MemoryEngine(gateway)
    rows = []
    probes = []
    save_new(output / "initial_memory.json", memory)
    for number in range(done + 1, through + 1):
        folder = output / f"chapter_{number:03d}"
        folder.mkdir()
        trace = []
        save_new(folder / "memory_before.json", memory)
        print(
            canonical(
                {"chapter": number, "phase": "memory", "items": len(memory["items"])}
            ),
            flush=True,
        )
        try:
            candidate, report = engine.advance(memory, chapters, number, trace)
        except Exception as exc:
            save_new(folder / "trace.json", trace)
            save_new(
                output / "pending.json",
                {
                    "pending_chapter": number,
                    "done_through": done,
                    "memory": memory,
                    "input_sha256": input_hash,
                    "runtime_sha256": source_hashes(),
                    **_exception_details(exc),
                },
            )
            raise
        save_new(folder / "memory_after.json", candidate)
        save_new(folder / "report.json", report)
        memory = candidate
        done = number
        rows.append(report)
        save_new(
            output / f"checkpoint_{number:03d}.json",
            {
                "done_through": done,
                "memory": memory,
                "input_sha256": input_hash,
                "runtime_sha256": source_hashes(),
            },
        )
        # Diagnostic answers do not roll back a valid memory transaction.
        if questions and str(number) in questions:
            try:
                probe = engine.recall(
                    memory, questions[str(number)], trace, f"after-{number}"
                )
            except ContractError as exc:
                probe = {"status": "INVALID_REPLY", "error": str(exc)}
            probe["after_chapter"] = number
            probes.append(probe)
            save_new(folder / "recall.json", probe)
        save_new(folder / "trace.json", trace)
    save_new(output / "final_memory.json", memory)
    return {
        "completed_through": done,
        "chapters": rows,
        "probes": probes,
        "initial_items": 0 if resume is None else len(resume["memory"]["items"]),
        "final_counts": {
            t: sum(row["tier"] == t for row in memory["items"].values())
            for t in ("working", "recent", "long")
        },
        "final_items": len(memory["items"]),
        "withheld_mutations": len(memory.get("withheld_memory_mutations", [])),
        "novel_rewritten": False,
        "semantic_certification": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--through", type=int, default=12)
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--resume", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--allow-remote", action="store_true")
    args = parser.parse_args()
    data = read(args.input)
    chapters = data["chapters"] if isinstance(data, dict) else data
    if not 1 <= args.through <= len(chapters):
        raise ContractError("Invalid chapter range")
    if any(
        c["number"] != i
        or not isinstance(c.get("title"), str)
        or not isinstance(c.get("text"), str)
        for i, c in enumerate(chapters[: args.through], 1)
    ):
        raise ContractError("Invalid chapter prefix")
    questions = read(args.questions) if args.questions else {}
    if not isinstance(questions, dict) or any(
        not isinstance(v, str) for v in questions.values()
    ):
        raise ContractError(
            "Questions must map chapter numbers to text; no expected answers"
        )
    hashes = source_hashes()
    original = sha(args.input)
    if args.preflight:
        print(
            canonical(
                {
                    "status": "PREFLIGHT_PASS",
                    "input_sha256": original,
                    "runtime_sha256": hashes,
                    "through": args.through,
                    "no_remote_calls": True,
                    "novel_rewritten": False,
                }
            )
        )
        return
    args.output.mkdir(parents=True, exist_ok=False)
    save_new(
        args.output / "manifest.json",
        {
            "input": str(args.input.resolve()),
            "input_sha256": original,
            "runtime_sha256": hashes,
            "runner_sha256": sha(__file__),
            "through": args.through,
            "resume": str(args.resume) if args.resume else None,
            "questions": questions,
            "network_retries": 0,
            "format_repairs_per_phase": 1,
            "temporal_coverage": "selected_old_records_only",
            "scope": "MEMORY_ONLY_NO_PROSE_GENERATION",
        },
    )
    result = {}
    recorder = None
    started = time.monotonic()
    try:
        key, endpoint, model = load_authorized_nst_secret(ROOT / "NstAgent/.env")
        provider = ChatCompletionProvider(
            endpoint,
            model,
            key,
            0.3,
            1.2,
            allow_remote=True,
            timeout_seconds=60,
            thinking_enabled=False,
        )
        recorder = RecordedProvider(provider, args.output)
        result = execute(
            args.output,
            recorder,
            chapters,
            args.through,
            questions,
            read(args.resume) if args.resume else None,
            original,
        )
        result["status"] = "COMPLETE"
    except Exception as exc:
        result = {"status": "FAILED_OR_PENDING", **_exception_details(exc)}
        if (args.output / "pending.json").exists():
            result["done_through"] = read(args.output / "pending.json")["done_through"]
    replies = [read(p) for p in args.output.glob("call_*.response.json")]
    result.update(
        calls=recorder.calls if recorder else 0,
        input_tokens=sum(r["input_tokens"] for r in replies),
        output_tokens=sum(r["output_tokens"] for r in replies),
        cost_usd_historical_estimate_not_bill=sum(r["cost_usd"] for r in replies),
        elapsed_seconds=time.monotonic() - started,
        novel_unchanged=sha(args.input) == original,
        runtime_unchanged=source_hashes() == hashes,
    )
    save_new(args.output / "result.json", result)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ("chapters", "probes")},
            ensure_ascii=False,
            indent=2,
        )
    )
    if result["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
