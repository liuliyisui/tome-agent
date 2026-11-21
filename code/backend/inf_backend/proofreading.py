"""Conservative offline proofreading. Suggestions always require author review."""

import re
import unicodedata

from tome_writer.domain import canonical, digest

from . import privacy

VERSION = "local-proofreading-v1"
TYPOS = {
    "迫不急待": "迫不及待",
    "按步就班": "按部就班",
    "一愁莫展": "一筹莫展",
    "再接再励": "再接再厉",
    "不径而走": "不胫而走",
    "穿流不息": "川流不息",
    "谈笑风声": "谈笑风生",
    "默守成规": "墨守成规",
    "走头无路": "走投无路",
    "变本加利": "变本加厉",
    "相形见拙": "相形见绌",
    "振耳欲聋": "震耳欲聋",
}
MAX_FINDINGS = 200


def revision(chapters):
    return digest(
        canonical([{k: c[k] for k in ("number", "title", "text")} for c in chapters])
    )


def _normal(text):
    output, starts, ends = [], [], []
    for index, char in enumerate(text):
        for normalized in unicodedata.normalize("NFKC", char):
            if normalized in "\u200b\u200c\u200d\u200e\u200f\u2060\ufeff":
                continue
            output.append(normalized)
            starts.append(index)
            ends.append(index + 1)
    return "".join(output), starts, ends


def sensitive_matches(text):
    """Return locations only, using the same rules as outbound protection."""
    normalized, starts, ends = _normal(text)
    secret = []
    for pattern in privacy.CREDENTIALS:
        for match in pattern.finditer(normalized):
            group = match.lastindex or 0
            if match.group(group).lower() not in privacy.PLACEHOLDERS:
                secret.append(match.span(group))
    merged = []
    for start, end in sorted(set(secret)):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    matches = [("credential", a, b) for a, b in merged]

    def overlaps(start, end):
        return any(a < end and b > start for a, b in merged)

    for category, pattern in (
        ("phone", privacy.PHONE),
        ("email", privacy.EMAIL),
        ("identity", privacy.IDENTITY),
        ("bank_card", privacy.CARD),
    ):
        for match in pattern.finditer(normalized):
            a, b = match.span()
            if overlaps(a, b):
                continue
            if category == "identity" and not privacy.valid_identity(match.group()):
                continue
            if category == "bank_card" and not (
                privacy.valid_card(match.group())
                and privacy.CARD_CONTEXT.search(normalized[max(0, a - 24) : b + 8])
            ):
                continue
            matches.append((category, a, b))
    return [
        (category, starts[a], ends[b - 1])
        for category, a, b in sorted(matches, key=lambda item: item[1])
    ]


def _utf16(text, offset):
    return (
        len(text[:offset].replace("\r\n", "\n").replace("\r", "\n").encode("utf-16-le"))
        // 2
    )


def inspect(chapters):
    findings = []
    truncated = False
    blocked = False

    def add(
        chapter,
        field,
        text,
        category,
        start,
        end,
        message,
        suggestion,
        replacement=None,
        level="warning",
    ):
        nonlocal truncated, blocked
        blocked = blocked or level == "danger"
        if len(findings) >= MAX_FINDINGS:
            truncated = True
            if level != "danger":
                return
            warning = next(
                (i for i, item in enumerate(findings) if item["level"] != "danger"),
                None,
            )
            if warning is None:
                return
            findings.pop(warning)
        findings.append(
            {
                "chapter": chapter,
                "field": field,
                "category": category,
                "start": _utf16(text, start),
                "end": _utf16(text, end),
                "line": text.count("\n", 0, start) + 1,
                "level": level,
                "message": message,
                "suggestion": suggestion,
                "replacement": replacement,
            }
        )

    for chapter in chapters:
        for field in ("title", "text"):
            text = chapter[field]
            number = chapter["number"]
            for category, start, end in sensitive_matches(text):
                add(
                    number,
                    field,
                    text,
                    category,
                    start,
                    end,
                    privacy.LABELS[category],
                    "请删除密钥或私钥。"
                    if category == "credential"
                    else "核实是否为虚构或已获授权的信息，必要时改用占位文字。",
                    level="danger" if category == "credential" else "warning",
                )
            for wrong, correct in TYPOS.items():
                for match in re.finditer(re.escape(wrong), text):
                    add(
                        number,
                        field,
                        text,
                        "typo",
                        *match.span(),
                        f"疑似易错词：{wrong}",
                        f"建议核对是否应为「{correct}」。",
                        correct,
                    )
            for match in re.finditer(r"([的地得了着和与在是把被])\1+", text):
                add(
                    number,
                    field,
                    text,
                    "repeated_word",
                    *match.span(),
                    "疑似重复文字",
                    "核实是否为笔误；若为人物用语或刻意重复，可保留。",
                    match[1],
                )
            seen = {}
            for match in re.finditer(r"[^\r\n]+", text):
                line = match.group().strip()
                if len(line) >= 12:
                    if line in seen:
                        add(
                            number,
                            field,
                            text,
                            "repeated_paragraph",
                            *match.span(),
                            "发现相同段落",
                            "核对是否重复粘贴；不要直接删除有意重复的段落。",
                        )
                    seen[line] = True
            stack = []
            pairs = {"“": "”", "「": "」", "『": "』", "（": "）", "【": "】"}
            for index, char in enumerate(text):
                if char in pairs:
                    stack.append((char, index))
                elif char in pairs.values():
                    if stack and pairs[stack[-1][0]] == char:
                        stack.pop()
                    else:
                        add(
                            number,
                            field,
                            text,
                            "punctuation",
                            index,
                            index + 1,
                            "标点可能未配对",
                            "检查此处括号或引号的配对关系。",
                        )
            for char, index in stack[:20]:
                add(
                    number,
                    field,
                    text,
                    "punctuation",
                    index,
                    index + 1,
                    "标点可能未闭合",
                    f"检查是否缺少「{pairs[char]}」。",
                )
    findings.sort(
        key=lambda item: (
            item["level"] != "danger",
            item["chapter"],
            item["field"] != "title",
            item["start"],
        )
    )
    return {
        "version": VERSION,
        "revision": revision(chapters),
        "findings": findings,
        "total": len(findings),
        "blocked": blocked,
        "truncated": truncated,
        "note": "本地规则只检查常见易错词、重复文字、部分标点与敏感信息，不能代替完整语法、情节和内容审核。疑似问题请作者核实。",
    }
