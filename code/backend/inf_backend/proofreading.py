"""Conservative offline proofreading. Suggestions always require author review."""

import re
import unicodedata
from dataclasses import dataclass

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
PUNCTUATION_PAIRS = {"“": "”", "「": "」", "『": "』", "（": "）", "【": "】"}


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


def _credential_spans(normalized):
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
    return merged


def _personal_match_is_valid(category, match, normalized):
    if category == "identity":
        return privacy.valid_identity(match.group())
    if category == "bank_card":
        start, end = match.span()
        context = normalized[max(0, start - 24) : end + 8]
        return privacy.valid_card(match.group()) and bool(
            privacy.CARD_CONTEXT.search(context)
        )
    return True


def sensitive_matches(text):
    """Return locations only, using the same rules as outbound protection."""
    normalized, starts, ends = _normal(text)
    merged = _credential_spans(normalized)
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
            if not _personal_match_is_valid(category, match, normalized):
                continue
            matches.append((category, a, b))
    return [
        (category, starts[a], ends[b - 1])
        for category, a, b in sorted(matches, key=lambda item: item[1])
    ]


@dataclass(frozen=True, slots=True)
class _Finding:
    category: str
    span: tuple[int, int]
    message: str
    suggestion: str
    replacement: str | None = None
    level: str = "warning"

    def in_field(self, chapter, field, text):
        start, end = self.span
        prefix = _editor_text(text[:start])
        return {
            "chapter": chapter,
            "field": field,
            "category": self.category,
            "start": len(prefix.encode("utf-16-le")) // 2,
            "end": len(_editor_text(text[:end]).encode("utf-16-le")) // 2,
            "line": prefix.count("\n") + 1,
            "level": self.level,
            "message": self.message,
            "suggestion": self.suggestion,
            "replacement": self.replacement,
        }


def _editor_text(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _word_findings(text):
    for wrong, correct in TYPOS.items():
        for match in re.finditer(re.escape(wrong), text):
            yield _Finding(
                "typo",
                match.span(),
                f"疑似易错词：{wrong}",
                f"建议核对是否应为「{correct}」。",
                correct,
            )
    for match in re.finditer(r"([的地得了着和与在是把被])\1+", text):
        yield _Finding(
            "repeated_word",
            match.span(),
            "疑似重复文字",
            "核实是否为笔误；若为人物用语或刻意重复，可保留。",
            match[1],
        )


def _paragraph_findings(text):
    seen = set()
    for match in re.finditer(r"[^\r\n]+", text):
        line = match.group().strip()
        if len(line) < 12:
            continue
        if line in seen:
            yield _Finding(
                "repeated_paragraph",
                match.span(),
                "发现相同段落",
                "核对是否重复粘贴；不要直接删除有意重复的段落。",
            )
        seen.add(line)


def _punctuation_findings(text):
    stack = []
    for index, char in enumerate(text):
        if char in PUNCTUATION_PAIRS:
            stack.append((char, index))
        elif char in PUNCTUATION_PAIRS.values():
            if stack and PUNCTUATION_PAIRS[stack[-1][0]] == char:
                stack.pop()
            else:
                yield _Finding(
                    "punctuation",
                    (index, index + 1),
                    "标点可能未配对",
                    "检查此处括号或引号的配对关系。",
                )
    for char, index in stack[:20]:
        yield _Finding(
            "punctuation",
            (index, index + 1),
            "标点可能未闭合",
            f"检查是否缺少「{PUNCTUATION_PAIRS[char]}」。",
        )


def _field_findings(text):
    for category, start, end in sensitive_matches(text):
        credential = category == "credential"
        yield _Finding(
            category,
            (start, end),
            privacy.LABELS[category],
            "请删除密钥或私钥。"
            if credential
            else "核实是否为虚构或已获授权的信息，必要时改用占位文字。",
            level="danger" if credential else "warning",
        )
    yield from _word_findings(text)
    yield from _paragraph_findings(text)
    yield from _punctuation_findings(text)


def _finding_candidates(chapters):
    for chapter in chapters:
        for field in ("title", "text"):
            text = chapter[field]
            for issue in _field_findings(text):
                yield issue, chapter["number"], field, text


def inspect(chapters):
    findings = []
    truncated = False
    blocked = False
    for issue, number, field, text in _finding_candidates(chapters):
        is_danger = issue.level == "danger"
        blocked = blocked or is_danger
        if len(findings) >= MAX_FINDINGS:
            truncated = True
            if not is_danger:
                continue
            warning = next(
                (i for i, item in enumerate(findings) if item["level"] != "danger"),
                None,
            )
            if warning is None:
                continue
            findings.pop(warning)
        findings.append(issue.in_field(number, field, text))
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
