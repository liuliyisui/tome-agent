"""Offline generation estimates; these are forecasts, never provider bills."""
import math

from inf_writer.domain import canonical, digest, strict_json
from . import service
from . import official_pricing


def signature(book_id, book=None):
    book = book or service.load_book(book_id)
    state = book["state"]
    chapters = state["chapters"] if isinstance(state, dict) else state.chapters
    return digest(canonical({"metadata": book["metadata"], "chapters": chapters,
                             "style": service.load_writing_style(book_id)}))


def estimate(book_id, count=1, approved_first=False):
    book = service.load_book(book_id)
    meta, state = book["metadata"], book["state"]
    chapters = state["chapters"] if isinstance(state, dict) else state.chapters
    remaining = meta["target_chapters"] - len(chapters)
    if type(count) is not int or not 1 <= count <= remaining:
        raise ValueError("本次章节数必须在 1 到剩余章节数之间")
    if count > 1 and (not chapters or approved_first is not True):
        raise ValueError("请先生成并阅读第一章，确认合适后再自动续写多章")
    demo = meta["model"]["model"] == "offline-demo"
    style = service.load_writing_style(book_id)
    used = sum(service.count_units(c["text"]) for c in chapters)
    target = max(300, (meta["target_units"] - used) // max(1, remaining))
    context_chars = len(meta["prompt"]) + sum(len(c["text"]) for c in chapters[-2:]) + sum(map(len, style.values()))
    base_input = 6000 + 2 * context_chars
    base_output = target * 2 + 2500
    basis = "按故事上下文、目标篇幅和多阶段调用粗估，无历史用量时误差较大。"
    usage_path = service.book_path(book_id) / "last-usage.json"
    if usage_path.exists() and not demo:
        try:
            usage = strict_json(usage_path.read_text(encoding="utf-8"))
            samples = max(1, usage.get("chapters_completed", 1))
            incoming, outgoing = usage["input_tokens"], usage["output_tokens"]
            if type(samples) is int and type(incoming) is int and type(outgoing) is int and incoming > 0 and outgoing > 0:
                base_input = max(base_input, incoming / samples)
                base_output = max(base_output, outgoing / samples)
                basis = "结合上次实际用量与本次上下文粗估，并计入后续章节上下文增长。"
        except (OSError, ValueError, TypeError, KeyError):
            pass
    incoming = 0 if demo else math.ceil(sum(base_input * (1 + min(i * .06, .6)) for i in range(count)))
    outgoing = 0 if demo else math.ceil(base_output * count)
    pricing = ({"rates": {"input": 0, "output": 0}, "peak_rates": {"input": 0, "output": 0},
                "label": "离线演示", "period": "offline", "currency": "CNY", "warning": "", "rule": "不调用模型，不产生费用。", "source": official_pricing.SOURCE,
                "checked_at": "", "status": "offline", "model": "offline-demo"}
               if demo else official_pricing.quote(meta["model"]["model"]))
    rates, peak = pricing["rates"], pricing["peak_rates"]
    cost = (incoming * rates["input"] + outgoing * rates["output"]) / 1_000_000 if rates else None
    peak_cost = (incoming * peak["input"] + outgoing * peak["output"]) / 1_000_000 if peak else None
    return {"book_id": book_id, "count": count, "first_chapter": len(chapters) + 1,
            "last_chapter": len(chapters) + count, "input_tokens": incoming, "output_tokens": outgoing,
            "total_tokens": incoming + outgoing, "estimated_cost_cny": cost, "peak_cost_cny": peak_cost,
            "prices": rates, "pricing": pricing, "basis": "固定离线样本，不联网、不消耗额度。" if demo else basis,
            "note": "按输入未命中缓存估算；缓存优惠可能降低费用。按当前时段报价，长任务跨时段时可能变化。实际用量和费用以服务商账单为准，不按估算值强制截断。",
            "signature": signature(book_id, book)}
