"""Optional narrative design, separate from canonical facts and prose review."""

import copy

from tome_writer.domain import canonical, digest

CONTRACT = {
    "optional_output": "narrative_plan",
    "example": {
        "story_question": "读者主要等候的结果",
        "setting_notes": ["人物机构关系、权限来源、年代和季节"],
        "scene_blocks": [
            {
                "event_scene_positions": [1, 2],
                "setting": "同一地点、连续时间",
                "carry_forward": "沿用人物位置、手中物品和正在进行的对话",
            }
        ],
        "threads": [
            {
                "topic": "稳定的线索名称，沿用已有名称",
                "importance": "major",
                "question": "这条线让读者等待什么回答",
                "acceptance": "怎样的正文回应才足够；允许有依据的排除或留白",
                "action": "advance",
                "reason": "本章为何推进或延后",
                "target_chapter": 3,
                "competing_explanations": [
                    "同一物件或痕迹的不同解释、各自依据和未确认处"
                ],
                "next_step": "后续追查、并线、产生后果，或明确交代不追的原因",
            }
        ],
        "chapter_change": "本章怎样改变认识、关系、压力或可用选择",
        "character_choice": "人物已知的风险、可选做法、实际选择及后果",
        "scene_entry": {
            "previous_completion": "上一章实际已经完成的动作及物件去向",
            "opening_action": "从该结果继续的新动作",
            "repeat_reason": "若再次执行同类动作，说明重新取得物件、再召集或新目的；没有则不重复",
        },
        "evidence_profiles": [
            {
                "topic": "稳定、具体的物件名称，当前文书与历史原件分开",
                "document_role": "它为谁、因何事制作",
                "creation_context": "签发/制作的时代、机构和程序",
                "pertains_to": "它记载的是哪一次事件，不等于它自身制作时间",
                "available_materials": [
                    {
                        "material_name": "人物当前可接触的具体材料，原件与副本分别命名",
                        "derived_from": "从哪份原件或上游材料取得；原件可写本件",
                        "acquisition_method": "如何取得：实际看到、拍摄、手抄、手描、转述等具体方式，不猜",
                        "access_status": "谁现在持有或可接触，哪些已归还或仅曾看过",
                        "retained_information": ["这种取得方式实际保留了哪些可用信息"],
                        "unavailable_information": [
                            "哪些原始特征未保留、被裁去或无法判断"
                        ],
                    }
                ],
                "date_fields": [
                    {
                        "field": "具体日期栏名",
                        "meaning": "该栏究竟指签发、申请、收件还是被记载事件",
                        "time_frame": "时间归属及目前未知之处",
                    }
                ],
                "supports": ["凭该物件能得出的有限结论"],
                "does_not_support": ["不能跨越的证明范围"],
                "missing_links": ["若要证明另一事件，还缺哪份独立记录或明确来源桥接"],
            }
        ],
        "inference_links": [
            {
                "question": "本章试图推进的判断",
                "evidence_topics": ["对应物件名称"],
                "observation_requirements": [
                    {
                        "material_name": "实际使用的材料名",
                        "required_information": ["此次观察需要哪些特征"],
                        "available_basis": "现有载体为何保留该信息",
                        "missing_condition": "缺失条件及改用的调查行动；没有则留空",
                    }
                ],
                "observation": "原件/照片/口述实际给了什么",
                "proposed_conclusion": "准备让人物得出的结论",
                "missing_links": ["尚缺的身份、时间、内容或来源关系"],
                "not_established": "不能假装已经证实的部分",
            }
        ],
        "recurring_details": ["可复用的动作意象及此次应有的变化"],
    },
    "instruction": "推荐填写此可选设计，不修改事件操作协议。scene_blocks按顺序覆盖scenes全部位置，"
    "同一场会谈的陈述和宣布处分属于一个连续场景，不按功能重新开场。"
    "不要求每章反转或冲突模板；推进要产生变化，避免只换物证重复手续。"
    "重要威胁、人证与疑点安排后续用途，不必全部解决，但不能无声消失。"
    "threads只有正文已交代后才可附resolution_chapter和resolution_quote逐字引文；"
    "next_step与chapter_change均是计划，不能当作已发生。"
    "人物受处分等后果须有事前能感知的权限边界、风险或选择，不能临时补造过错。",
}
CONTRACT["instruction"] += (
    "每章返回threads；无任何待回应事项时也显式返回threads=[]和thread_review_note说明。"
    "省略整个narrative_plan或threads不会被当成没有问题，保存正文后将登记补录待办。"
    "关键证据第一次出现前填写evidence_profiles：区分文书制作时间、各日期栏含义、所记载事件时间与程序用途。"
    "当前新制的行政文书不能因为日期/签名相似就变成旧事件的原始凭据；若要关联，先给独立历史记录、明确摘录来源或其它桥接。"
    "推理用inference_links分开观察、拟推结论和缺失环节。待核只是结论强度，不能使不相关证据突然有证明力。"
    "比较两句话时先核对对象、时间和流程环节；接收、处理、反馈并不等价，没有后续回音不等于无人接收。"
    "scene_entry以chapter_handoff的实际结尾为起点；已完成的移交/发言不能重置为未做，补手续与再次执行须区别。"
    "先查看实际正文新增的重要人物、作者猜测和威胁是否尚未登记成threads，补登记而不是只沿用原小纲。"
    "同一笔迹的不同作者猜测和不同页不同签名分开，不靠人物说像就建立作者身份；改变猜测交代依据。"
)
CONTRACT["instruction"] += (
    "逐项回应narrative_continuity中的required_thread_decisions，沿用topic。"
    "每项写action（advance/defer/resolve/leave_open/drop）、reason和下一步；延后须给target_chapter，不能原样无限延期。"
    "收尾安排须在剩余篇幅和章节上限内可执行，不能把本卷关键回应推给未计划的下一卷。"
    "question说明读者等待的回答，acceptance说明具体回应标准，不用“以后核实”代替。"
    "本章安排是计划，不是已完成。依据此前实际正文更新时给progress_chapter/progress_quote；"
    "声称已回收或明确留白时给resolution_chapter/resolution_quote及resolution_type。"
    "引文必须来自已保存正文；不能预测本章将写出的句子来提前结账。"
)
CONTRACT["instruction"] += (
    "用已有chapter_change和character_choice安排人的处境：人物想得到或保住什么，"
    "谁出于什么利益阻碍他，他如何选择，选择怎样改变关系或代价；不要求每章填满同一套路。"
    "取证边界约束事实认证，不禁止人物怀疑动机、猜错、撒谎、害怕、争辩或私下行动。"
    "把这些明确写成人物视角，未证实的解释不能冒充客观事实，也不能让所有人只说待核。"
    "再次走访、核对或递交时，安排新信息、新阻力、关系变化或实际后果；"
    "相同说明无需重新演示，允许略写手续，把篇幅留给改变局面的行动。"
    "人物遭到指控时考虑其已知的授权、承诺和反证，安排是否援引及对方回应；"
    "不能为制造代价忘掉已发生的授权，也不预设申辩必然成功。"
    "主线回应须让读者看到被调查的具体事件、受影响的人和可证实的发现，"
    "不以列入待核代替原本承诺的回答；未知之处可以留白，但须区分事实未明与叙事未交代。"
)
CONTRACT["instruction"] += (
    "evidence_profiles用available_materials分别记录原件及每份派生材料的取得方式、接触状态、保留及丢失信息；"
    "不能把“文书确实存在”当作人物现在持有原件。字段均用具体自然语言，不限通信或载体类别。"
    "inference_links的observation_requirements先核对观察所需信息是否存在于当前载体，再安排scenes；"
    "缺少条件则改变行动，不靠“待核”放行不成立的观察。沿用narrative_continuity.evidence_access及其原文来源。"
)


def normalize(value, scene_count):
    """Bad optional design is reported and ignored; event planning continues."""
    if value is None:
        return {}, []
    if not isinstance(value, dict) or len(canonical(value).encode("utf-8")) > 32000:
        return {}, ["Optional narrative_plan is not a bounded object; ignored"]
    result = {}
    notes = []
    for key in ("story_question", "chapter_change", "character_choice"):
        if isinstance(value.get(key), str) and value[key].strip():
            result[key] = value[key]
    if (
        isinstance(value.get("thread_review_note"), str)
        and value["thread_review_note"].strip()
    ):
        result["thread_review_note"] = value["thread_review_note"]
    for key in ("setting_notes", "recurring_details"):
        if isinstance(value.get(key), list):
            result[key] = [s for s in value[key] if isinstance(s, str) and s.strip()]

    def strings(values):
        return (
            [s for s in values if isinstance(s, str) and s.strip()]
            if isinstance(values, list)
            else []
        )

    if isinstance(value.get("scene_entry"), dict):
        result["scene_entry"] = {
            k: v
            for k, v in value["scene_entry"].items()
            if k in ("previous_completion", "opening_action", "repeat_reason")
            and isinstance(v, str)
        }
    for name in ("evidence_profiles", "inference_links"):
        if not isinstance(value.get(name), list):
            continue
        result[name] = []
        for row in value[name]:
            required = "topic" if name == "evidence_profiles" else "question"
            if (
                not isinstance(row, dict)
                or not isinstance(row.get(required), str)
                or not row[required].strip()
            ):
                notes.append(
                    "Optional " + name + " item without " + required + " ignored"
                )
                continue
            text_keys = (
                ("topic", "document_role", "creation_context", "pertains_to")
                if name == "evidence_profiles"
                else (
                    "question",
                    "observation",
                    "proposed_conclusion",
                    "not_established",
                )
            )
            list_keys = (
                ("supports", "does_not_support", "missing_links")
                if name == "evidence_profiles"
                else ("evidence_topics", "missing_links")
            )
            view = {k: row[k] for k in text_keys if isinstance(row.get(k), str)}
            for key in list_keys:
                if key in row:
                    view[key] = strings(row[key])
            if name == "evidence_profiles" and isinstance(row.get("date_fields"), list):
                view["date_fields"] = [
                    {
                        k: v
                        for k, v in item.items()
                        if k in ("field", "meaning", "time_frame")
                        and isinstance(v, str)
                    }
                    for item in row["date_fields"]
                    if isinstance(item, dict) and isinstance(item.get("field"), str)
                ]
            nested = (
                "available_materials"
                if name == "evidence_profiles"
                else "observation_requirements"
            )
            if isinstance(row.get(nested), list):
                view[nested] = []
                required_key = "material_name"
                for item in row[nested]:
                    if (
                        not isinstance(item, dict)
                        or not isinstance(item.get(required_key), str)
                        or not item[required_key].strip()
                    ):
                        notes.append(
                            "Optional " + nested + " item without material_name ignored"
                        )
                        continue
                    text_fields = (
                        (
                            "material_name",
                            "derived_from",
                            "acquisition_method",
                            "access_status",
                        )
                        if name == "evidence_profiles"
                        else ("material_name", "available_basis", "missing_condition")
                    )
                    list_fields = (
                        ("retained_information", "unavailable_information")
                        if name == "evidence_profiles"
                        else ("required_information",)
                    )
                    material = {
                        k: item[k] for k in text_fields if isinstance(item.get(k), str)
                    }
                    for k in list_fields:
                        if k in item:
                            material[k] = strings(item[k])
                    view[nested].append(material)
            result[name].append(view)
    blocks = value.get("scene_blocks")
    if isinstance(blocks, list) and blocks:
        positions = []
        valid = []
        for block in blocks:
            if not isinstance(block, dict):
                break
            indexes = block.get("event_scene_positions")
            if (
                not isinstance(indexes, list)
                or not indexes
                or any(type(i) is not int for i in indexes)
            ):
                break
            positions.extend(indexes)
            valid.append(
                {
                    "event_scene_positions": indexes,
                    "setting": block.get("setting", "")
                    if isinstance(block.get("setting", ""), str)
                    else "",
                    "carry_forward": block.get("carry_forward", "")
                    if isinstance(block.get("carry_forward", ""), str)
                    else "",
                }
            )
        if len(valid) == len(blocks) and positions == list(range(1, scene_count + 1)):
            result["scene_blocks"] = valid
        else:
            notes.append(
                "Invalid optional scene grouping ignored; canonical event sequence retained"
            )
    if isinstance(value.get("threads"), list):
        result["threads"] = []
        for thread in value["threads"]:
            if (
                not isinstance(thread, dict)
                or not isinstance(thread.get("topic"), str)
                or not thread["topic"].strip()
            ):
                notes.append("Optional thread without a topic ignored")
                continue
            row = {
                k: thread[k]
                for k in (
                    "topic",
                    "importance",
                    "next_step",
                    "resolution_quote",
                    "question",
                    "acceptance",
                    "action",
                    "reason",
                    "progress_quote",
                    "resolution_type",
                )
                if isinstance(thread.get(k), str)
            }
            if isinstance(thread.get("competing_explanations"), list):
                row["competing_explanations"] = strings(
                    thread["competing_explanations"]
                )
            if type(thread.get("resolution_chapter")) is int:
                row["resolution_chapter"] = thread["resolution_chapter"]
            for key in ("target_chapter", "progress_chapter"):
                if type(thread.get(key)) is int:
                    row[key] = thread[key]
            result["threads"].append(row)
    return result, notes


def design_units(packets, target, minimum, design):
    from .story_budget import writing_units

    blocks = design.get("scene_blocks", [])
    # Scene design is not a request for another model call. Write a normal
    # chapter together, keeping all underlying state transactions untouched.
    if target is not None and target <= 3000 and packets:
        unit = {
            "packet_indexes": list(range(len(packets))),
            "target_han_chars": target,
            "continuity_scope": "Whole chapter; physical scene layout remains a writing reference",
        }
        if blocks:
            unit["scene_block_positions"] = list(range(1, len(blocks) + 1))
        return [unit]
    if not blocks:
        return writing_units(
            len(packets), target, max(minimum, 1500) if target is not None else minimum
        )
    # Deferred transactions may leave holes. Their original stage positions,
    # never renumbered compact positions, identify the physical scene block.
    groups = []
    for block_index, block in enumerate(blocks):
        indexes = [
            i
            for i, p in enumerate(packets)
            if p["stage"] + 1 in block["event_scene_positions"]
        ]
        if indexes:
            groups.append((block_index, indexes))
    if [i for _, indexes in groups for i in indexes] != list(range(len(packets))):
        return writing_units(len(packets), target, minimum)
    units = []
    for allocation in writing_units(len(groups), target, minimum):
        chosen = [groups[i] for i in allocation["packet_indexes"]]
        units.append(
            {
                "packet_indexes": [p for _, indexes in chosen for p in indexes],
                "target_han_chars": allocation["target_han_chars"],
                "scene_block_positions": [i + 1 for i, _ in chosen],
            }
        )
    return units


def writer_contract(prepared, unit, ordinal, total, earlier):
    design = prepared.get("narrative_plan", {})
    selected = set(unit["packet_indexes"])
    first = min(selected)
    outline = [
        {
            "stage": p["stage"],
            "purpose": s["purpose"],
            "statements": [b["statement"] for b in s["beats"]],
            "writing_status": "current"
            if i in selected
            else "written"
            if i < first
            else "not_started",
        }
        for i, p in enumerate(prepared["stage_packets"])
        for s in p["commit"]["scenes"]
    ]
    return {
        "chapter_event_outline": outline,
        "outline_scope": "Plan reference only; later events must not be narrated early",
        "chapter_intent": {
            k: copy.deepcopy(design[k])
            for k in (
                "story_question",
                "chapter_change",
                "character_choice",
                "setting_notes",
                "recurring_details",
            )
            if k in design
        },
        "scene_entry": copy.deepcopy(design.get("scene_entry", {}))
        if not earlier
        else {},
        "evidence_profiles": copy.deepcopy(design.get("evidence_profiles", [])),
        "inference_links": copy.deepcopy(design.get("inference_links", [])),
        "physical_scene_blocks": [
            design["scene_blocks"][i - 1] for i in unit.get("scene_block_positions", [])
        ],
        "may_end_current_scene": bool(unit.get("scene_block_positions"))
        or ordinal == total,
        "previous_prose_sha256": digest(earlier),
        "instruction": "writing_status只表示写作覆盖，不认证计划事件已在正文发生；实际位置、持有人和完成动作以已写原文为准。"
        "written场景不是待写任务，不再演一遍；current场景若前文已提前写完，承接其结果，不为完成清单重复动作。"
        "再次移交、领取、发言须有新物件版本、补手续或新场合等明确原因。"
        "从已写前情的动作、人物位置和对话接着写。已放下的杯子不能无故再放下一次；"
        "已入座的会谈不能再介绍座位和主持人开场。只有授权事件要求离场或结束时才收场，"
        "中间阶段不写散会、离开或总结结论。截止时间、身份和物件去向沿用章内方案及实际前情，"
        "不得在衔接描写中擅自新增另一套日期或流程。不得因outline出现后续事件就提前写。"
        "physical_scene_blocks是整章场景布局，不要求每块重新介绍环境、人物和任务。"
        "同一单元内也须保持动作先后：打算做、正在做、已经完成分开；"
        "不能先记已完成再实际执行同一件事，不能把走向某处写成已交付。"
        "跨地点转换须交代实际去向；若改变目的地或未办成原事，给出原因和结果。"
        "chapter_intent是叙事意图，不是已发生事实。人物可以猜错、隐瞒、争辩和害怕；"
        "保留其视角及利害，不把猜测认证为真，也不把所有反应缩成待核和誊录。",
    }


def advance_writer_context(payload, book, number, earlier, *, current_draft=""):
    """One literal progress view for stage writing, fallback and length editing.

    No new model call or inferred facts: coverage describes writing work only.
    The saved prefix remains authoritative when plans and prose disagree.
    """
    if earlier:
        tail = earlier[-4000:]
        head = earlier[: min(2000, max(0, len(earlier) - 4000))]
        payload["chapter_handoff"] = {
            "source_chapter": number,
            "source": "current_chapter_written_prefix",
            "prefix_sha256": digest(earlier),
            "closing_text": tail[-1600:],
            "omitted_prefix_characters": max(0, len(earlier) - 1600),
            "instruction": "这是本章最新停笔处，优先于上一章结尾和开场计划；接着实际结果写，不重新执行已完成的动作。",
        }
        payload["previous_prose_tail"] = {
            "text": tail,
            "read_only": True,
            "omitted_characters": max(0, len(earlier) - len(tail)),
        }
        payload["current_chapter_progress"] = {
            "source": "literal_written_prefix",
            "prefix_sha256": digest(earlier),
            "written_characters": len(earlier),
            "opening_text": head,
            "latest_text_ref": "previous_prose_tail.text",
            "omitted_middle_characters": max(0, len(earlier) - len(head) - len(tail)),
            "instruction": "从这些原文延续人物所在、在场者、物件持有人、已做动作及未完对话；不把旧状态或计划当作当前状态。"
            "开头用于保留早先完成事项，结尾是最新状态；同类动作再次发生要有明确的新原因。",
        }
        # Remove competing chapter-opening anchors in every writer route.
        for key in ("narrative_plan", "chapter_plan"):
            if isinstance(payload.get(key), dict):
                payload[key] = copy.deepcopy(payload[key])
                payload[key].pop("scene_entry", None)
                nested = payload[key].get("narrative_plan")
                if isinstance(nested, dict):
                    nested.pop("scene_entry", None)
        if isinstance(payload.get("stage_task"), dict):
            payload["stage_task"] = copy.deepcopy(payload["stage_task"])
            payload["stage_task"].get("scene_continuity", {}).pop("scene_entry", None)
    else:
        payload["chapter_handoff"] = handoff(book)
    if current_draft:
        payload["revision_scope"] = {
            "mode": "replace_current_unit_only",
            "draft_sha256": digest(current_draft),
            "instruction": "current_draft是本次要改写的单元，不是待续写前情；保留它已经完成的动作及结尾结果，"
            "只改写一次，不在末尾再执行一遍。previous_prose_tail属于此前单元，只读且不返回。",
        }
    return payload


def publish(book, chapter, design, *, recovered=False):
    """Plan intent persists; closure claims additionally require saved quotes."""
    ledger = book.setdefault(
        "narrative_planning",
        {
            "schema": "inf-narrative-planning-v1",
            "threads": {},
            "chapters": {},
            "issues": [],
        },
    )
    number = chapter["number"]
    design = design if isinstance(design, dict) else {}
    expected = {
        k
        for k, r in ledger["threads"].items()
        if r.get("importance", "major") in ("core", "major")
        and r["introduced_in_chapter"] <= number
        and not _settled(r)
    }
    mentioned = set()
    if recovered:
        stored = ledger["chapters"][str(number)]
        stored["recovered_design"] = copy.deepcopy(design)
        stored["recovered_design_sha256"] = digest(canonical(design))
    else:
        ledger["chapters"][str(number)] = {
            "chapter_sha256": chapter["sha256"],
            "design": copy.deepcopy(design),
            "scope": "Planning intentions, not certified prose outcomes",
        }
    for profile in [] if recovered else design.get("evidence_profiles", []):
        key = digest(profile["topic"])[:24]
        row = ledger.setdefault("evidence_profiles", {}).setdefault(
            key,
            {
                "topic": profile["topic"],
                "introduced_in_chapter": number,
                "first_profile": copy.deepcopy(profile),
                "updates": [],
            },
        )
        row["latest_profile"] = copy.deepcopy(profile)
        row["last_planned_chapter"] = number
        row["updates"].append({"chapter": number, "profile": copy.deepcopy(profile)})
    for item in design.get("threads", []):
        key = digest(item["topic"])[:24]
        mentioned.add(key)
        row = ledger["threads"].setdefault(
            key,
            {
                "topic": item["topic"],
                "introduced_in_chapter": number,
                "status": "open",
                "updates": [],
            },
        )
        if recovered and row.get("last_planned_chapter", 0) > number:
            row["introduced_in_chapter"] = min(row["introduced_in_chapter"], number)
            row["updates"].append(
                {
                    "chapter": number,
                    "proposal": copy.deepcopy(item),
                    "recovered_from_saved_prose": True,
                }
            )
            row["updates"].sort(key=lambda u: u["chapter"])
            continue
        incoming = item.get("importance", row.get("importance", "major"))
        if incoming not in ("core", "major", "minor"):
            incoming = row.get("importance", "major")
        priority = {"core": 0, "major": 1, "minor": 2}
        previous = row.get("importance", incoming)
        row["importance"] = (
            previous
            if priority.get(previous, 1) < priority.get(incoming, 1)
            else incoming
        )
        row["next_step"] = item.get("next_step", row.get("next_step", ""))
        row["last_planned_chapter"] = number
        for field in ("question", "acceptance"):
            if item.get(field):
                row[field] = item[field]
        if item.get("action"):
            row["planning_decision"] = {
                k: item[k] for k in ("action", "reason", "target_chapter") if k in item
            }
            row["planning_decision"]["chapter"] = number
        progress = item.get("progress_quote")
        source = item.get("progress_chapter")
        if progress and type(source) is int and 1 <= source <= len(book["chapters"]):
            text = book["chapters"][source - 1]["text"]
            if progress in text:
                row["last_progress_chapter"] = source
                row["progress_evidence"] = {
                    "chapter": source,
                    "quote": progress,
                    "chapter_sha256": digest(text),
                }
        if "competing_explanations" in item:
            row["competing_explanations"] = copy.deepcopy(
                item["competing_explanations"]
            )
        quote = item.get("resolution_quote")
        source = item.get("resolution_chapter", number)
        if quote:
            if (
                1 <= source <= len(book["chapters"])
                and quote in book["chapters"][source - 1]["text"]
            ):
                row.update(
                    status="addressed",
                    resolution={
                        "chapter": source,
                        "quote": quote,
                        "chapter_sha256": book["chapters"][source - 1]["sha256"],
                        "semantic_certification": False,
                    },
                )
                row["last_progress_chapter"] = source
                if item.get("resolution_type") in THREAD_SETTLED:
                    if row.get("prose_assessment"):
                        row.setdefault("assessment_history", []).append(
                            copy.deepcopy(row["prose_assessment"])
                        )
                    row["prose_assessment"] = {
                        "status": item["resolution_type"],
                        "reason": item.get("reason")
                        or "规划根据已保存正文更新，收尾仍需结合全文确认",
                        "evidence": [
                            {
                                "chapter": source,
                                "quote": quote,
                                "chapter_sha256": digest(
                                    book["chapters"][source - 1]["text"]
                                ),
                            }
                        ],
                        "reviewed_after_chapter": number,
                        "semantic_certification": False,
                    }
            else:
                ledger["issues"].append(
                    {
                        "chapter": number,
                        "topic": item["topic"],
                        "reason": "Unbound resolution quote; remains open",
                    }
                )
        row["introduced_in_chapter"] = min(row["introduced_in_chapter"], number)
        row["updates"].append({"chapter": number, "proposal": copy.deepcopy(item)})
        row["updates"].sort(key=lambda u: u["chapter"])
    invalid = []
    for identifier in expected & mentioned:
        item = next(
            i
            for i in design.get("threads", [])
            if digest(i["topic"])[:24] == identifier
        )
        if (
            item.get("action")
            not in ("advance", "defer", "resolve", "leave_open", "drop")
            or not item.get("reason")
            or (
                item.get("action") == "defer"
                and (
                    type(item.get("target_chapter")) is not int
                    or item["target_chapter"] <= number
                )
            )
        ):
            invalid.append(identifier)
    ledger["chapters"][str(number)]["thread_accountability"] = {
        "design_status": "RECOVERED"
        if recovered
        else "PROVIDED"
        if design
        else "MISSING",
        "required_thread_ids": sorted(expected),
        "mentioned_thread_ids": sorted(expected & mentioned),
        "missing_thread_ids": sorted(expected - mentioned),
        "incomplete_decision_thread_ids": sorted(invalid),
        "scope": "Planning coverage only; mentioning or scheduling is not prose progress",
    }
    # Discovery must be acknowledged even when no old thread exists yet.
    discovery_missing = "threads" not in design or (
        not design["threads"] and not design.get("thread_review_note")
    )
    jobs = ledger.setdefault("planning_jobs", {})
    key = str(number)
    if discovery_missing or expected - mentioned or invalid:
        old = jobs.get(key, {})
        jobs[key] = {
            "chapter": number,
            "chapter_sha256": chapter["sha256"],
            "status": "PENDING",
            "discovery_review_required": discovery_missing,
            "missing_thread_ids": sorted(expected - mentioned),
            "incomplete_decision_thread_ids": sorted(invalid),
            "attempts": old.get("attempts", 0),
            "last_attempt_boundary": old.get("last_attempt_boundary"),
        }
    elif key in jobs:
        jobs[key].update(
            status="DONE",
            resolution="SOURCE_BOUND_ACCOUNTABILITY_REPAIR"
            if recovered
            else "VALID_DESIGN",
        )


def ensure_accountability(book):
    """Explicit migration/backfill: never infer events or rewrite an old proposal."""
    for chapter in book.get("chapters", []):
        if str(chapter["number"]) not in book.get("narrative_planning", {}).get(
            "chapters", {}
        ):
            publish(book, chapter, chapter.get("narrative_plan", {}))


def pending_planning_jobs(book):
    return [
        copy.deepcopy(j)
        for j in book.get("narrative_planning", {}).get("planning_jobs", {}).values()
        if j.get("status") == "PENDING"
    ]


def context(book, number):
    from .evidence_access import context as evidence_access_context

    ledger = book.get("narrative_planning", {})
    rows = list(ledger.get("threads", {}).values())
    rows.sort(
        key=lambda r: (
            _settled(r),
            r.get("importance") != "core",
            r.get("last_progress_chapter", r["introduced_in_chapter"]),
        )
    )
    selected = []
    for row in rows:
        view = {
            k: v for k, v in row.items() if k not in ("updates", "assessment_history")
        }
        view["chapters_since_introduced"] = number - row["introduced_in_chapter"]
        view["chapters_without_verified_progress"] = number - row.get(
            "last_progress_chapter", row["introduced_in_chapter"]
        )
        view.pop("prose_assessment", None)
        if len(canonical(selected + [view]).encode("utf-8")) <= 10000:
            selected.append(view)
    recent = []
    for stored in list(ledger.get("chapters", {}).values())[-2:]:
        view = {
            "chapter_sha256": stored["chapter_sha256"],
            "scope": stored["scope"],
            "design": {},
        }
        for key in (
            "story_question",
            "chapter_change",
            "character_choice",
            "setting_notes",
            "recurring_details",
            "scene_entry",
            "inference_links",
        ):
            if key in stored["design"]:
                candidate = copy.deepcopy(view)
                candidate["design"][key] = stored["design"][key]
                if len(canonical(recent + [candidate]).encode("utf-8")) <= 6000:
                    view = candidate
        recent.append(view)
    profiles = []
    for row in sorted(
        ledger.get("evidence_profiles", {}).values(),
        key=lambda r: -r["last_planned_chapter"],
    ):
        view = {k: v for k, v in row.items() if k != "updates"}
        if len(canonical(profiles + [view]).encode("utf-8")) <= 6000:
            profiles.append(view)
    return {
        "scope": "Persistent planning commitments, not a fourth fact-memory bank",
        "threads": selected,
        "evidence_access": evidence_access_context(book),
        "evidence_profiles": profiles,
        "omitted_evidence_profile_count": len(ledger.get("evidence_profiles", {}))
        - len(profiles),
        "omitted_thread_count": len(rows) - len(selected),
        "recent_designs": recent,
        "previous_planning_coverage": copy.deepcopy(
            ledger.get("chapters", {})
            .get(str(number - 1), {})
            .get("thread_accountability", {})
        ),
        "pending_planning_repairs": pending_planning_jobs(book)[-8:],
        "omitted_planning_repair_count": max(0, len(pending_planning_jobs(book)) - 8),
        "required_thread_decisions": [
            {
                "thread_id": digest(r["topic"])[:24],
                "topic": r["topic"],
                "question": r.get("question", r["topic"]),
                "acceptance": r.get("acceptance"),
                "definition_ready": _definition_ready(r),
                "last_progress_chapter": r.get(
                    "last_progress_chapter", r["introduced_in_chapter"]
                ),
            }
            for r in selected
            if r.get("importance", "major") in ("core", "major")
            and not _settled(ledger["threads"][digest(r["topic"])[:24]])
        ],
        "instruction": "逐项交代required_thread_decisions的安排，缺项保留为规划待办。优先安排长期未推进的重要线索；"
        "next_step更新不算正文推进，不能靠重复延后清账。可合并、产生后果、失败或明确放弃，不强制所有支线闭合。"
        "避免连续章节重复同样的发现→手续→待核；检查人物选择与关系如何改变。"
        "动作意象再次出现须有变化，不能靠扣笔帽、核编号等填补字数。",
    }


def handoff(book):
    """Pinned literal endpoint, not an invented summary of what happened."""
    if not book.get("chapters"):
        return {}
    c = book["chapters"][-1]
    tail = c["text"][-1600:]
    return {
        "source_chapter": c["number"],
        "chapter_sha256": c["sha256"],
        "closing_text": tail,
        "omitted_prefix_characters": len(c["text"]) - len(tail),
        "scope": "Literal saved ending, not a completion classifier",
        "instruction": "先读取实际收尾，再决定scene_entry。人物已离场、物件已移交、陈述已做出的结果要延续；"
        "不要重新发放已经交走的物品。再次发生同类行动须有新的来源、场合或目的并明确衔接。",
    }


def verify_design(container):
    if "narrative_plan" in container and container.get(
        "narrative_plan_sha256"
    ) != digest(canonical(container["narrative_plan"])):
        from tome_writer.domain import ContractError

        raise ContractError("Narrative design integrity failure")


def verify_ledger(book):
    from tome_writer.domain import ContractError

    chapters = {c["number"]: c for c in book["chapters"]}
    ledger = book.get("narrative_planning", {})
    for key, job in book.get("chapter_title_jobs", {}).items():
        c = chapters.get(int(key))
        if not c or job["chapter_sha256"] != c["sha256"]:
            raise ContractError("Chapter title job source mismatch")
    for c in chapters.values():
        source = c.get("title_source")
        if source and source.get("chapter_sha256") != c["sha256"]:
            raise ContractError("Chapter title source mismatch")
    for key, row in ledger.get("chapters", {}).items():
        c = chapters.get(int(key))
        if (
            not c
            or row["chapter_sha256"] != c["sha256"]
            or row["design"] != c.get("narrative_plan", {})
        ):
            raise ContractError("Narrative planning source mismatch")
        if "recovered_design" in row and row.get("recovered_design_sha256") != digest(
            canonical(row["recovered_design"])
        ):
            raise ContractError("Recovered narrative design integrity failure")
    for job in ledger.get("planning_jobs", {}).values():
        c = chapters.get(job["chapter"])
        if not c or job["chapter_sha256"] != c["sha256"]:
            raise ContractError("Narrative planning job source mismatch")
    for row in ledger.get("threads", {}).values():
        for assessment in row.get("assessment_history", []) + [
            row.get("prose_assessment", {})
        ]:
            for evidence in assessment.get("evidence", []):
                if not _valid_thread_source(book, evidence):
                    raise ContractError("Thread assessment source mismatch")
        if row.get("progress_evidence") and not _valid_thread_source(
            book, row["progress_evidence"]
        ):
            raise ContractError("Thread progress source mismatch")
        if row["status"] != "addressed":
            continue
        source = row.get("resolution", {})
        c = chapters.get(source.get("chapter"))
        if (
            not c
            or source.get("chapter_sha256") != c["sha256"]
            or not source.get("quote")
            or source["quote"] not in c["text"]
        ):
            raise ContractError("Narrative thread resolution source mismatch")
    for row in ledger.get("evidence_profiles", {}).values():
        updates = row.get("updates", [])
        if (
            not updates
            or row["first_profile"] != updates[0]["profile"]
            or row["latest_profile"] != updates[-1]["profile"]
        ):
            raise ContractError("Evidence profile history mismatch")
        for update in updates:
            design = (
                ledger.get("chapters", {})
                .get(str(update["chapter"]), {})
                .get("design", {})
            )
            if update["profile"] not in design.get("evidence_profiles", []):
                raise ContractError("Evidence profile planning source missing")


THREAD_SETTLED = ("resolved", "ruled_out", "open_ending")
THREAD_REVIEW_POLICY = "explicit_question_and_intent_v1"
THREAD_REVIEW_INSTRUCTION = (
    "同时依据已保存正文更新narrative_threads中的线索，不评价文风、不写或修改正文。"
    "thread_updates必须逐项返回thread_id、status、reason、evidence。"
    "status为resolved（回答已展示）、ruled_out（有依据排除）、open_ending（正文明确交代无法回答的原因、结果或选择）、"
    "pending（仍未处理）或uncertain（证据不足以判断）。"
    "前三种状态必须给evidence中的source_choice，程序绑定原文；其余可给空数组。"
    "对照每条question/acceptance：声称查明、递交、归档、停止追查本身不等于展示具体答案；"
    "泛泛说“不再查”不能替所有未提及的线索结账。明确留白须确实回应该问题及其不能解决的原因或后果。"
    "不要求所有疑点查明、不把人物余生或次要细节升级为强制条件。"
    "计划、next_step及旧完成标签不是正文证据。证据未提供时返回uncertain，不猜测缺失正文。"
    "旧答案被后文推翻时改pending/uncertain。不得凭删除、漏项或降级重要程度清账。"
)
THREAD_REVIEW_INSTRUCTION += (
    "original_setup保留最初提出的问题和竞争解释，不能用后来缩小的next_step替代原问题。"
    "先读purpose=thread_setup且thread_id对应的原始正文，区分不同文书、不同页的笔迹、不同人物和不同时代的程序。"
    "后来的办理程序完成不能证明旧文书的用途已查明；一处字迹未核不能替另一处痕迹交代结果。"
    "复合线索逐个检查问题，部分回答不能把整条标resolved。若返回remaining_questions非空，则整条保持pending。"
)


def _settled(row):
    status = row.get("prose_assessment", {}).get("status")
    return (
        status in THREAD_SETTLED
        and _definition_ready(row)
        and (
            status != "open_ending"
            or (
                row.get("planning_decision", {}).get("action") in ("leave_open", "drop")
                and bool(row["planning_decision"].get("reason"))
            )
        )
    )


def _definition_ready(row):
    return all(
        isinstance(row.get(k), str) and row[k].strip()
        for k in ("question", "acceptance")
    )


def _valid_thread_source(book, source):
    if not isinstance(source, dict):
        return False
    chapter = next(
        (c for c in book.get("chapters", []) if c["number"] == source.get("chapter")),
        None,
    )
    quote = source.get("quote")
    return bool(
        chapter
        and isinstance(quote, str)
        and quote
        and quote in chapter["text"]
        and source.get("chapter_sha256") == digest(chapter["text"])
    )


def _thread_definition_hash(book):
    rows = book.get("narrative_planning", {}).get("threads", {})
    return digest(
        canonical(
            {
                "policy": THREAD_REVIEW_POLICY,
                "threads": {
                    k: {
                        f: r.get(f)
                        for f in (
                            "topic",
                            "question",
                            "acceptance",
                            "importance",
                            "planning_decision",
                        )
                    }
                    for k, r in rows.items()
                },
            }
        )
    )


def thread_review_input(book, limit=14000):
    """Bound only the transmitted view. Omitted important entries prevent certification."""
    ledger = book.get("narrative_planning", {})
    rows = ledger.get("threads", {})
    marker = ledger.get("latest_thread_review", {})
    latest = book.get("chapters", [])[-1] if book.get("chapters") else {}
    prior = (
        set(marker.get("reviewed_thread_ids", []))
        if (
            marker.get("chapter") == latest.get("number")
            and marker.get("chapter_sha256") == digest(latest.get("text", ""))
            and marker.get("definition_sha256") == _thread_definition_hash(book)
        )
        else set()
    )
    ordered = sorted(
        rows.items(),
        key=lambda item: (
            item[1].get("importance", "major") not in ("core", "major"),
            item[0] in prior,
            item[1].get("importance") != "core",
            item[1].get("last_progress_chapter", item[1]["introduced_in_chapter"]),
        ),
    )
    selected = []
    for identifier, row in ordered:
        view = {
            "thread_id": identifier,
            "topic": row["topic"][:240],
            "importance": row.get("importance", "major"),
            "definition_ready": _definition_ready(row),
            "question": row.get("question", row["topic"])[:400],
            "acceptance": row.get(
                "acceptance",
                "回应本线问题；明确的排除或有依据的留白也可，不能只宣布移交或停止",
            )[:600],
            "next_step": row.get("next_step", "")[:500],
            "introduced_in_chapter": row["introduced_in_chapter"],
            "last_progress_chapter": row.get(
                "last_progress_chapter", row["introduced_in_chapter"]
            ),
        }
        original = (row.get("updates") or [{}])[0].get("proposal", {})
        view["original_setup"] = {
            "question": original.get("question", row["topic"])[:300],
            "next_step": original.get("next_step", "")[:200],
            "competing_explanations": [
                s[:140] for s in original.get("competing_explanations", [])[:3]
            ],
            "scope": "Original planning questions, not confirmed facts",
        }
        if len(canonical(selected + [view]).encode("utf-8")) <= limit:
            selected.append(view)
    included = {r["thread_id"] for r in selected}
    return {
        "threads": selected,
        "omitted_thread_ids": [k for k in rows if k not in included],
        "definition_sha256": _thread_definition_hash(book),
        "scope": "Persistent thread ledger, not proposed facts",
    }


def apply_thread_review(book, value, sources, chapter):
    """Commit valid peer rows independently; bad/missing updates remain visible."""
    from tome_writer.domain import ContractError

    ledger = book.get("narrative_planning", {})
    targets = thread_review_input(book)
    old = ledger.get("threads", {})
    if not old:
        return []
    submitted = value.get("thread_updates")
    grouped = {}
    issues = []
    reviewed = []
    if not isinstance(submitted, list):
        submitted = []
    target_ids = {r["thread_id"] for r in targets["threads"]}
    for row in submitted:
        identifier = row.get("thread_id") if isinstance(row, dict) else None
        if not isinstance(identifier, str) or identifier not in target_ids:
            issues.append(
                {"thread_id": None, "error": "Unknown thread update; ignored"}
            )
            continue
        grouped.setdefault(identifier, []).append(row)
    by_choice = {r["source_choice"]: r for r in sources}
    for identifier in target_ids:
        previous = old[identifier]
        if previous.get("prose_assessment"):
            previous.setdefault("assessment_history", []).append(
                copy.deepcopy(previous["prose_assessment"])
            )
        try:
            rows = grouped.get(identifier, [])
            if len(rows) != 1:
                raise ContractError("Thread update missing or duplicated")
            row = rows[0]
            status = row.get("status")
            reason = row.get("reason")
            evidence = row.get("evidence")
            if status not in THREAD_SETTLED + ("pending", "uncertain"):
                raise ContractError("Invalid thread status")
            if not isinstance(reason, str) or not reason.strip() or len(reason) > 1500:
                raise ContractError("Invalid thread reason")
            if not isinstance(evidence, list):
                raise ContractError("Invalid thread evidence")
            remaining = row.get("remaining_questions", [])
            if not isinstance(remaining, list) or any(
                not isinstance(s, str) for s in remaining
            ):
                raise ContractError("Invalid remaining thread questions")
            if remaining and status == "resolved":
                status = "pending"
            bound = []
            for item in evidence:
                if not isinstance(item, dict):
                    raise ContractError("Invalid thread evidence item")
                choice = item.get("source_choice")
                if type(choice) is not int or choice not in by_choice:
                    raise ContractError("Unknown thread evidence choice")
                source = by_choice[choice]
                record = {k: source[k] for k in ("chapter", "quote", "chapter_sha256")}
                if not _valid_thread_source(book, record):
                    raise ContractError("Thread evidence source changed")
                if record not in bound:
                    bound.append(record)
            if status in THREAD_SETTLED and not bound:
                raise ContractError("Thread disposition requires saved prose evidence")
            candidate = status
            # The reviewer cannot invent a smaller contract at the finish line.
            # Old ledgers remain readable, but their missing definitions are
            # explicitly handed back to planning instead of silently certified.
            if status in THREAD_SETTLED and not _definition_ready(previous):
                status = "uncertain"
                reason = (
                    "线索缺少明确question/acceptance，须先由规划补全，不能在结尾临时缩小问题。模型候选判断："
                    + reason
                )
            elif status == "open_ending" and not (
                previous.get("planning_decision", {}).get("action")
                in ("leave_open", "drop")
                and previous["planning_decision"].get("reason")
            ):
                status = "pending"
                reason = (
                    "尚无针对本线索的明确留白安排，泛称停止追查不能代替逐项处置。模型候选判断："
                    + reason
                )
            previous["prose_assessment"] = {
                "status": status,
                "reason": reason,
                "evidence": bound,
                "candidate_disposition": candidate,
                "remaining_questions": remaining,
                "reviewed_after_chapter": chapter,
                "semantic_certification": False,
            }
            if bound and status in THREAD_SETTLED:
                previous["last_progress_chapter"] = max(r["chapter"] for r in bound)
            reviewed.append(identifier)
        except ContractError as exc:
            # A prior answer cannot certify new text after an unreadable update.
            previous["prose_assessment"] = {
                "status": "uncertain",
                "reason": str(exc),
                "evidence": [],
                "reviewed_after_chapter": chapter,
                "semantic_certification": False,
            }
            issues.append({"thread_id": identifier, "error": str(exc)})
    latest = next(c for c in book["chapters"] if c["number"] == chapter)
    prior = ledger.get("latest_thread_review", {})
    if (
        prior.get("chapter") == chapter
        and prior.get("chapter_sha256") == digest(latest["text"])
        and prior.get("definition_sha256") == targets["definition_sha256"]
    ):
        reviewed = list(
            (set(prior.get("reviewed_thread_ids", [])) - target_ids) | set(reviewed)
        )
        issues = [
            r for r in prior.get("issues", []) if r.get("thread_id") not in target_ids
        ] + issues
    marker = {
        "chapter": chapter,
        "chapter_sha256": digest(latest["text"]),
        "review_policy": THREAD_REVIEW_POLICY,
        "definition_sha256": targets["definition_sha256"],
        "reviewed_thread_ids": sorted(reviewed),
        "omitted_thread_ids": targets["omitted_thread_ids"],
        "issues": issues,
    }
    ledger.setdefault("thread_review_history", []).append(copy.deepcopy(marker))
    ledger["latest_thread_review"] = marker
    return issues


def thread_report(book):
    """Separate open narrative commitments from engineering repair queues."""
    ledger = book.get("narrative_planning", {})
    rows = ledger.get("threads", {})
    items = []
    for identifier, row in rows.items():
        assessment = row.get("prose_assessment", {})
        status = assessment.get("status", "unverified")
        if status in THREAD_SETTLED and not _settled(row):
            status = "unverified"
        items.append(
            {
                "thread_id": identifier,
                "topic": row["topic"],
                "importance": row.get("importance", "major"),
                "definition_ready": _definition_ready(row),
                "status": status,
                "reason": assessment.get("reason", "尚未依据正文确认处置"),
                "evidence": copy.deepcopy(assessment.get("evidence", [])),
                "remaining_questions": copy.deepcopy(
                    assessment.get("remaining_questions", [])
                ),
                "last_planned_chapter": row.get("last_planned_chapter"),
                "last_progress_chapter": row.get("last_progress_chapter"),
                "planning_status": row.get("status", "open"),
            }
        )
    important = {r["thread_id"] for r in items if r["importance"] in ("core", "major")}
    pending = [
        r["thread_id"]
        for r in items
        if r["thread_id"] in important and r["status"] not in THREAD_SETTLED
    ]
    marker = ledger.get("latest_thread_review", {})
    latest = book.get("chapters", [])[-1] if book.get("chapters") else {}
    jobs = pending_planning_jobs(book)
    current = not jobs and (
        not important
        or (
            marker.get("chapter") == latest.get("number")
            and marker.get("chapter_sha256") == digest(latest.get("text", ""))
            and marker.get("definition_sha256") == _thread_definition_hash(book)
            and important.issubset(set(marker.get("reviewed_thread_ids", [])))
        )
    )
    return {
        "scope": "Model disposition of saved prose; not a literary quality certificate",
        "total": len(items),
        "items": items,
        "important_thread_ids": sorted(important),
        "pending_planning_chapters": sorted(j["chapter"] for j in jobs),
        "requires_definition_thread_ids": [
            r["thread_id"]
            for r in items
            if r["thread_id"] in important and not r["definition_ready"]
        ],
        "unhandled_important_thread_ids": pending,
        "current_review_complete": bool(current),
        "important_threads_accounted_for": bool(current and not pending),
        "latest_review": copy.deepcopy(marker),
        "planning_coverage": copy.deepcopy(
            ledger.get("chapters", {})
            .get(str(latest.get("number")), {})
            .get("thread_accountability", {})
        ),
    }


def thread_setup_sources(book, max_chars=6000):
    """Retrieve each transmitted thread's introduction, rather than only late conclusions."""
    chapters = {c["number"]: c["text"] for c in book.get("chapters", [])}
    result = []
    remaining = max_chars

    def grams(text):
        text = "".join(c for c in text.casefold() if c.isalnum())
        return {text[i : i + 2] for i in range(max(0, len(text) - 1))}

    for row in thread_review_input(book)["threads"]:
        n = row["introduced_in_chapter"]
        text = chapters.get(n, "")
        if not text or remaining <= 0:
            continue
        query = grams(row["topic"] + " " + row["question"])
        paragraphs = []
        start = 0
        frequency = {}
        for paragraph in text.split("\n\n"):
            overlap = query & grams(paragraph)
            paragraphs.append((overlap, start, len(paragraph)))
            for term in overlap:
                frequency[term] = frequency.get(term, 0) + 1
            start += len(paragraph) + 2
        # Common carrier names occur throughout a chapter. Prefer rarer trace
        # terms rather than selecting an unrelated paragraph about the same paper.
        ranked = sorted(
            paragraphs,
            key=lambda r: sum(1 / (frequency[g] ** 2) for g in r[0]),
            reverse=True,
        )
        windows = []
        allowance = min(650, remaining)
        # Two distinct windows avoid betting the whole view on one paragraph
        # about the carrier rather than the trace on it. No text is rewritten.
        for _, start, _length in ranked:
            if len(windows) == 2 or allowance <= 0:
                break
            left = max(0, start - 50)
            right = min(len(text), left + min(325, allowance))
            if any(left < end and right > begin for begin, end in windows):
                continue
            windows.append((left, right))
            result.append(
                {
                    "thread_id": row["thread_id"],
                    "purpose": "thread_setup",
                    "chapter": n,
                    "start": left,
                    "end": right,
                    "quote": text[left:right],
                    "chapter_sha256": digest(text),
                }
            )
            remaining -= right - left
            allowance -= right - left
    return result
