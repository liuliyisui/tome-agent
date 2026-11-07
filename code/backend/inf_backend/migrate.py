"""Initialize PostgreSQL and import legacy files without changing the originals."""
import argparse
import json
import re
from pathlib import Path
from . import database as db, service
from inf_writer.domain import Snapshot, digest, canonical, project_id


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def collect(root):
    results = []
    paths = sorted(root.glob("*/metadata.json")) + sorted(root.glob(".trash/*/metadata.json"))
    for path in paths:
        folder = path.parent
        if path.is_symlink() or folder.is_symlink() or not folder.resolve().is_relative_to(root.resolve()):
            raise ValueError("迁移源目录包含不安全链接")
        meta = read(path)
        required = {"schema_version", "title", "prompt", "target_chapters", "target_units", "model"}
        if set(meta) != required or meta["schema_version"] != 1:
            raise ValueError("作品元数据格式不受支持")
        deleted = read(folder / "deleted-book.json") if folder.parent.name == ".trash" else None
        book_id = deleted["book_id"] if deleted else folder.name
        project_id(book_id)
        style = service.validate_writing_style(read(folder / "writing-style.json")) if (folder / "writing-style.json").exists() else {"instructions": "", "reference": ""}
        checkpoint = None
        if (folder / "longform-current.json").exists():
            checkpoint = read(folder / "longform-current.json")["checkpoint"]
            target = (folder / checkpoint).resolve()
            if not target.is_relative_to(folder.resolve()) or target.is_symlink():
                raise ValueError("检查点路径不安全")
            record = read(target)
            if record.get("schema") != "inf-writing-checkpoint-v1":
                raise ValueError("不支持的长文本检查点格式")
            state, kind = record["book"], "longform"
            if record.get("book_sha256") != digest(canonical(state)):
                raise ValueError("检查点内容校验失败")
        else:
            state, kind = Snapshot.from_dict(read(folder / "checkpoint.json")).to_dict(), "snapshot"
            if state["project_id"] != book_id:
                raise ValueError("检查点作品 ID 与目录不一致")
        token = folder.name if deleted else None
        if token and not re.fullmatch(r"[a-f0-9]{32}", token):
            raise ValueError("废案箱恢复标识无效")
        usage = read(folder / "last-usage.json") if (folder / "last-usage.json").exists() else None
        pinned = read(folder / "shelf.json").get("pinned") is True if (folder / "shelf.json").exists() else False
        results.append(dict(id=book_id, metadata=meta, style=style, state=state, kind=kind,
                            checkpoint=checkpoint, storage_key=folder.relative_to(root).as_posix(),
                            deleted=deleted, token=token, usage=usage, pinned=pinned))
    if len({x["id"] for x in results}) != len(results):
        raise ValueError("源目录中存在重复作品 ID")
    return results


def import_books(root, apply=False):
    rows = collect(Path(root))
    summary = {"books": len(rows), "chapters": sum(len(x["state"].get("chapters", [])) for x in rows),
               "applied": False, "imported": 0, "skipped": 0}
    if not apply:
        return summary
    # One transaction for the entire import. Any collision rolls everything back.
    with db.connect() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(731592025)")
        for r in rows:
            existing = conn.execute("SELECT * FROM tome_books WHERE id=%s", (r["id"],)).fetchone()
            if existing:
                if (existing["metadata"] != r["metadata"] or existing["state"] != r["state"]
                        or existing["style"] != r["style"] or existing["checkpoint"] != r["checkpoint"]
                        or bool(existing["deleted_at"]) != bool(r["deleted"])
                        or existing["restore_token"] != r["token"] or existing["pinned"] != r["pinned"]
                        or existing["storage_key"] != r["storage_key"] or existing["last_usage"] != r["usage"]):
                    raise ValueError("数据库存在不同版本的作品，迁移已回滚：" + r["id"])
                summary["skipped"] += 1
                continue
            db.create(r["id"], r["metadata"], r["state"], r["style"], conn=conn)
            db.save(r["id"], r["state"], r["kind"], r["checkpoint"], r["usage"], conn=conn)
            conn.execute("""UPDATE tome_books SET storage_key=%s,pinned=%s,deleted_at=%s,restore_token=%s
                WHERE id=%s""", (r["storage_key"], r["pinned"],
                r["deleted"]["deleted_at"] if r["deleted"] else None, r["token"], r["id"]))
            summary["imported"] += 1
    summary["applied"] = True
    return summary


def recover_jobs():
    with db.connect() as conn:
        pending = list(conn.execute("SELECT id,book_id,payload FROM tome_jobs WHERE status='running'"))
    count = 0
    for r in pending:
        with service.operation_lock(service.book_path(r["book_id"])):
            db.job(r["id"], {**r["payload"], "status": "interrupted",
                            "error": "服务中断，已保存章节仍可阅读。请重新确认后续写。"})
            count += 1
    return {"interrupted": count}


def reconcile(book_id):
    # Repair the DB projection after a checkpoint was saved but its DB transaction failed.
    with service.operation_lock(service.book_path(book_id)):
        folder = service.book_path(book_id)
        relative = read(folder / "longform-current.json")["checkpoint"]
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError("检查点路径不安全")
        from memory_runtime.writing import load_resume
        state = load_resume(path, service._longform_plan(service._metadata(book_id)))
        usage = read(folder / "last-usage.json") if (folder / "last-usage.json").exists() else None
        db.save(book_id, state, "longform", relative, usage)
    return {"reconciled": book_id}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "import", "recover-jobs", "reconcile"])
    parser.add_argument("--source", type=Path, default=service.BOOKS)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--book-id")
    args = parser.parse_args()
    try:
        if args.command == "init":
            db.initialize()
            result = {"schema_version": 1}
        elif args.command == "import":
            if args.source.resolve() != service.BOOKS.resolve():
                raise ValueError("请用 TOME_DATA_HOME 指向包含原作品的后端目录，避免迁移后检查点路径变化")
            result = import_books(args.source, args.apply)
        elif args.command == "recover-jobs":
            if not args.apply:
                raise ValueError("停止网页服务后使用 --apply 恢复中断任务")
            result = recover_jobs()
        else:
            if not args.apply or not args.book_id:
                raise ValueError("请指定 --book-id 和 --apply")
            result = reconcile(args.book_id)
        print(json.dumps(result, ensure_ascii=False))
    except (db.DatabaseUnavailable, ValueError, OSError, KeyError):
        raise SystemExit("数据库操作未完成。请检查数据库、源存档格式、冲突作品及命令参数。")


if __name__ == "__main__":
    main()
