"""Offline, deterministic checks of creative content before model disclosure.

Reports intentionally contain counts and fixed source labels, never matched text.
These rules flag common identifiers; they cannot establish identity or replace
content moderation, consent, or a complete data-loss-prevention system.
"""

import re
import unicodedata
from collections import Counter
from datetime import date

from tome_writer.domain import canonical

VERSION = "local-rules-v1"
LABELS = {
    "phone": "疑似中国大陆手机号",
    "identity": "疑似居民身份证号（校验通过）",
    "bank_card": "疑似银行卡号（有卡号语境且校验通过）",
    "email": "邮箱地址",
    "credential": "疑似 API 密钥或私钥",
}
PHONE = re.compile(
    r"(?<![A-Za-z0-9])(?:\+?86[ -]?)?1[3-9][0-9][ -]?[0-9]{4}[ -]?[0-9]{4}(?![A-Za-z0-9])"
)
IDENTITY = re.compile(r"(?<![A-Za-z0-9])[1-9][0-9]{16}[0-9Xx](?![A-Za-z0-9])")
EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
)
CARD = re.compile(r"(?<![A-Za-z0-9])[1-9](?:[ -]?[0-9]){15,18}(?![A-Za-z0-9])")
CARD_CONTEXT = re.compile(
    r"银行卡|卡号|信用卡|借记卡|bank\s*card|card\s*(?:number|no)", re.I
)
CREDENTIALS = (
    re.compile(
        r"(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})(?![A-Za-z0-9_-])"
    ),
    re.compile(
        r"(?<![A-Za-z0-9])(?:AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35})(?![A-Za-z0-9_-])"
    ),
    re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|secret[_ -]?key)\b[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{16,})"
    ),
    re.compile(r"(?i)\bBearer[ \t]+[A-Za-z0-9_./+=-]{20,}"),
)
PLACEHOLDERS = {"your_api_key_here", "your_access_token", "your_secret_key_here"}


def valid_identity(value):
    """Check date and MOD 11-2, without claiming the identifier is real."""
    try:
        date(int(value[6:10]), int(value[10:12]), int(value[12:14]))
    except ValueError:
        return False
    if not 1900 <= int(value[6:10]) <= 2099:
        return False
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    remainder = (
        sum(int(n) * weight for n, weight in zip(value[:17], weights, strict=True)) % 11
    )
    return value[-1].upper() == "10X98765432"[remainder]


def valid_card(value):
    digits = [int(n) for n in value if n.isascii() and n.isdigit()]
    total = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2:
            digit *= 2
            digit = digit - 9 if digit > 9 else digit
        total += digit
    return len(set(digits)) > 1 and total % 10 == 0


def strings(value):
    """Walk JSON values, avoiding recursion and internal dictionary key names."""
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, (list, tuple)):
            stack.extend(item)


def _counts(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
    counts = Counter()
    # Deduplicate credentials that match both a prefix and an assignment rule.
    secret_spans = set()
    for pattern in CREDENTIALS:
        for match in pattern.finditer(text):
            value = match.group(match.lastindex or 0)
            if value.lower() not in PLACEHOLDERS:
                secret_spans.add(match.span(match.lastindex or 0))
    merged = []
    for start, end in sorted(secret_spans):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    counts["credential"] = len(merged)
    # Do not classify identifiers inside a credential as separate personal data.
    pieces = []
    cursor = 0
    for start, end in merged:
        pieces.extend((text[cursor:start], " " * (end - start)))
        cursor = end
    pieces.append(text[cursor:])
    text = "".join(pieces)
    counts["phone"] = len(PHONE.findall(text))
    counts["identity"] = sum(valid_identity(m.group()) for m in IDENTITY.finditer(text))
    counts["email"] = len(EMAIL.findall(text))
    counts["bank_card"] = sum(
        valid_card(m.group())
        and bool(CARD_CONTEXT.search(text[max(0, m.start() - 24) : m.end() + 8]))
        for m in CARD.finditer(text)
    )
    return counts


def inspect_sources(sources):
    """Sources are (fixed display label, JSON-like content) pairs."""
    findings = []
    for source, value in sources:
        counts = Counter()
        for text in strings(value):
            counts.update(_counts(text))
        for category, label in LABELS.items():
            if counts[category]:
                findings.append(
                    {
                        "category": category,
                        "label": label,
                        "source": source,
                        "count": counts[category],
                        "action": "block" if category == "credential" else "confirm",
                    }
                )
    return {
        "version": VERSION,
        "findings": findings,
        "total": sum(item["count"] for item in findings),
        "blocked": any(item["action"] == "block" for item in findings),
        "requires_confirmation": any(item["action"] == "confirm" for item in findings),
    }


def inspect_book(book, style, skills, author_feedback=""):
    state = book["state"]
    state = state if isinstance(state, dict) else state.to_dict()
    sources = [
        (
            "作品名称与故事构想",
            {key: book["metadata"].get(key, "") for key in ("title", "prompt")},
        ),
        ("文风要求与参考片段", style),
        ("已选写作 Skill", skills),
    ]
    for index, chapter in enumerate(state.get("chapters", []), 1):
        sources.append(
            (
                f"第 {index} 章正文与标题",
                {key: chapter.get(key, "") for key in ("text", "title")},
            )
        )
    sources.append(
        (
            "故事记忆与规划",
            {key: value for key, value in state.items() if key != "chapters"},
        )
    )
    sources.append(("本次作者意见", author_feedback))
    return inspect_sources(sources)


class SensitiveInformationError(ValueError):
    def __init__(self, report):
        self.report = report
        super().__init__(
            "检测到疑似 API 密钥或私钥，请先从创作内容中移除，再重新检查。"
            if report["blocked"]
            else "检测到敏感信息，请查看本地检查结果并确认后再发送。"
        )


def enforce(report, confirmed=False):
    if report["blocked"] or (report["requires_confirmation"] and confirmed is not True):
        raise SensitiveInformationError(report)


class PrivacyGateway:
    """Check the final model request after style, skills and feedback injection."""

    def __init__(self, gateway, confirmed=False):
        self.gateway = gateway
        self.confirmed = confirmed

    def complete(self, request):
        report = inspect_sources(
            [("模型请求", (request.system, canonical(request.payload)))]
        )
        enforce(report, self.confirmed)
        return self.gateway.complete(request)
