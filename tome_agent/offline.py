"""Scripted model fixture; exercises architecture without provider/network."""
from .agent import Response, ToolCall, ChapterAgent
from .state import Workspace
from .runner import StoryRunner


def group(gid, entries=(), **changes):
    result = {"id": gid, "depends_on": [], "entries": list(entries),
              "upsert_character_state": [], "add_past_event": [],
              "add_future_requirement": [], "resolve_future_requirement": []}
    result.update(changes)
    return result


def entry(value, quote, revision=None, action="store", **changes):
    result = dict(subject="林舟", key="fire_starter_count", action=action, value=value,
        temporal_scope="current", time_anchor="current", expected_revision=revision,
        category="quantity_time", epistemic_status="objective", support_basis="explicit_statement",
        quote=quote, reason="本章明确说明库存", consequence="约束后续生火能力")
    result.update(changes)
    return result


class ScriptedModel:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, messages, tools):
        self.requests.append((messages, tools))
        return next(self.responses)


def tool(name, args, call_id="call"):
    return Response(calls=[ToolCall(call_id, name, args)], finish_reason="tool_calls")


def demo(path):
    text1 = "林舟清点背包，里面有两支火折。他拆开了那封信。"
    text2 = "林舟用掉一支火折，背包中还剩一支。他朝渡口走去。"
    responses = [tool("write", {"text": text1}),
        tool("update", {"groups": [group("inventory", [entry(2, "里面有两支火折")],
            upsert_character_state=[{"name": "林舟", "description": "收到信件，准备出发"}],
            add_past_event=[{"key": "letter_received", "description": "收到未来来信"}],
            add_future_requirement=[{"key": "find_sender", "description": "找到寄信者"}])]}), Response("DONE"),
        tool("read", {"chapter": 1}), tool("search", {"query": "火折"}),
        tool("write", {"text": text2}),
        tool("update", {"groups": [group("inventory", [entry(1, "背包中还剩一支", 1, "update")])]}), Response("DONE")]
    workspace = Workspace("灯塔来信", "守塔人收到未来来信。", [
        {"title": "来信", "goal": "发现信件", "target_units": 24},
        {"title": "启程", "goal": "准备出发", "target_units": 24}], {"model": "offline-scripted"})
    return StoryRunner(ChapterAgent(ScriptedModel(responses))).run(workspace, path, chapter_limit=2)
