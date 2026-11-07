"""One persistent budget for chapter planning and incremental writing units."""

import math


def closing_start(plan):
    return max(1, plan["chapters"] - max(1, math.ceil(plan["chapters"] / 4)) + 1)


def chapter_budget(plan, chapters, number):
    total = plan["target_han_chars"]
    count = plan["chapters"]
    from .length_control import han_count

    written = sum(han_count(c["text"]) for c in chapters)
    average = total / count
    closing = closing_start(plan)
    final_count = count - closing + 1
    reserve = math.ceil(total * 0.30) if closing > 1 else total
    minimum = max(1, math.floor(average * 0.65))
    if number < closing:
        available = total - written - reserve
        target = max(minimum, math.floor(available / (closing - number)))
    elif number <= count:
        future = count - number
        reserved_per_final = math.ceil(reserve / final_count)
        available = total - written - future * reserved_per_final
        target = max(reserved_per_final, math.ceil((total - written) / (future + 1)))
    else:
        # A short resolution scene, never an entire extra chapter by default.
        available = total - written
        target = max(minimum, available)
    target = max(1, int(target))
    scene_minimum = max(1, min(400, math.floor(average / 4)))
    return {
        "schema": "inf-length-budget-v2",
        "chapter": number,
        "target": target,
        "target_han_chars": total,
        "written_han_chars": written,
        "ending_reserve_han": reserve,
        "closing_start": closing,
        "remaining_han": total - written,
        "budget_conflict": target > max(0, available),
        "minimum_scene_han": scene_minimum,
        "recommended_max_writing_units": max(1, target // scene_minimum),
        "policy": "Preserve complete scenes and ending reserve; report overrun rather than cutting prose.",
    }


def writing_units(packet_count, target, minimum_scene):
    """Group adjacent transactions before writing, with stable positive budgets."""
    count = (
        packet_count
        if target is None
        else min(packet_count, max(1, target // minimum_scene))
    )
    if not count:
        return []
    result = []
    left = 0
    for i in range(count):
        size = packet_count // count + (i < packet_count % count)
        allocation = None if target is None else target // count + (i < target % count)
        result.append(
            {
                "packet_indexes": list(range(left, left + size)),
                "target_han_chars": allocation,
            }
        )
        left += size
    return result
