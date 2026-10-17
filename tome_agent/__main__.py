"""CLI: offline demos and explicitly requested DeepSeek operations."""
import argparse
from pathlib import Path
from .domain import Chapter, ChapterPlan, Story
from .pipeline import commit_chapter
from .storage import load_story
from .checkpoints import load_checkpoint
from .offline import demo as architecture_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Tome Agent offline framework demo")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo")
    demo.add_argument("--output", type=Path, default=Path("data/demo.json"))
    export = commands.add_parser("export")
    export.add_argument("--input", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    v4 = commands.add_parser("demo-v4")
    v4.add_argument("--output", type=Path, default=Path("data/v4-demo.json"))
    export_v4 = commands.add_parser("export-v4")
    export_v4.add_argument("--input", type=Path, required=True)
    export_v4.add_argument("--output", type=Path, required=True)
    commands.add_parser("check", help="Check local configuration without network")
    plan = commands.add_parser("plan", help="Generate an outline using DeepSeek (paid)")
    plan.add_argument("--id", required=True)
    plan.add_argument("--title", required=True)
    plan.add_argument("--prompt-file", type=Path, required=True)
    plan.add_argument("--chapters", type=int, default=8)
    plan.add_argument("--target-units", type=int, default=10000)
    plan.add_argument("--allow-paid", action="store_true")
    run = commands.add_parser("generate", help="Continue a book using DeepSeek (paid)")
    run.add_argument("--id", required=True)
    run.add_argument("--chapters", type=int, default=1)
    run.add_argument("--resume-attempt", action="store_true")
    run.add_argument("--max-turns", type=int, default=30)
    run.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args()
    if args.command == "check":
        from .providers.deepseek import Settings
        cfg = Settings.load(require_key=False)
        print(f"Model: {cfg.model}; API key: {'configured' if cfg.api_key else 'missing'}; network: not used")
    elif args.command in ("plan", "generate"):
        if not args.allow_paid:
            parser.error("真实模型调用会产生费用，请明确添加 --allow-paid")
        from .service import create_book, generate
        try:
            if args.command == "plan":
                workspace = create_book(args.id, args.title, args.prompt_file.read_text(encoding="utf-8"), args.chapters, args.target_units)
            else:
                workspace = generate(args.id, args.chapters, args.resume_attempt, args.max_turns)
        except (ValueError, RuntimeError) as exc:
            parser.exit(1, f"{exc}\n")
        print(f"Saved: {workspace.title}; completed chapters: {len(workspace.chapters)}")
    elif args.command == "demo-v4":
        workspace = architecture_demo(args.output)
        print(f"Offline architecture demo: {len(workspace.chapters)} chapters; {len(workspace.state.history)} archived fact versions")
    elif args.command == "export-v4":
        workspace = load_checkpoint(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# {workspace.title}\n\n" + "\n\n".join(
            f"## 第{n}章 {workspace.outline[n-1]['title']}\n\n{text}"
            for n, text in sorted(workspace.chapters.items())), encoding="utf-8")
        print(f"Exported: {args.output}")
    elif args.command == "demo":
        story = Story("灯塔来信", "一位守塔人收到未来的来信。",
                      [ChapterPlan(1, "来信", "发现信件"), ChapterPlan(2, "启程", "准备出发")])
        for number, text, value, quote in [
            (1, "林舟清点背包，里面有两支火折。他拆开了那封信。", "2", "里面有两支火折"),
            (2, "林舟用掉一支火折，背包中还剩一支。他朝渡口走去。", "1", "背包中还剩一支"),
        ]:
            story = commit_chapter(story, Chapter(number, story.outline[number-1].title, text),
                [dict(subject="林舟", key="fire_starter_count", value=value,
                      chapter=number, quote=quote, expected_revision=number-1)], args.output)
        print(f"Offline demo saved: {args.output}; next chapter: {story.next_chapter}")
    else:
        story = load_story(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# {story.title}\n\n" + "\n\n".join(
            f"## 第{c.number}章 {c.title}\n\n{c.text}" for c in story.chapters), encoding="utf-8")
        print(f"Exported: {args.output}")


if __name__ == "__main__":
    main()
