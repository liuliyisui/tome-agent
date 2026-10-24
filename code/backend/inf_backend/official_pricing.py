"""Official DeepSeek price snapshots with automatic refresh, in CNY / 1M tokens."""
import copy
from datetime import datetime, timedelta, timezone
import html
import http.client
import math
import re
import threading

from .settings import BACKEND_ROOT

SOURCE = "https://api-docs.deepseek.com/zh-cn/quick_start/pricing/"
HOLIDAY_SOURCE = "https://www.beijing.gov.cn/fuwu/bmfw/sy/jrts/202511/t20251104_4258838.html"
BEIJING = timezone(timedelta(hours=8))
CACHE = BACKEND_ROOT / "data" / "official-pricing.json"
SNAPSHOT = {
    "deepseek-flash": {"off_peak": {"input": 1.0, "cache_hit": .02, "output": 4.0},
                       "peak": {"input": 2.0, "cache_hit": .04, "output": 8.0}},
    "deepseek-v4-pro": {"off_peak": {"input": 4.5, "cache_hit": .15, "output": 13.5},
                        "peak": {"input": 9.0, "cache_hit": .30, "output": 27.0}},
}
# National holiday breaks, per the State Council's 2026 notice. DeepSeek's
# pricing explicitly treats all weekends as off-peak, including makeup days.
HOLIDAYS = {2026: [("01-01", "01-03"), ("02-15", "02-23"), ("04-04", "04-06"),
                   ("05-01", "05-05"), ("06-19", "06-21"), ("09-25", "09-27"), ("10-01", "10-07")]}
_lock = threading.Lock()
_cached = None
_attempted_at = None


def validate_models(models):
    if not isinstance(models, dict) or set(models) != set(SNAPSHOT):
        raise ValueError("Unrecognized official models")
    for model in models.values():
        if set(model) != {"peak", "off_peak"}:
            raise ValueError("Incomplete peak/off-peak price table")
        for rates in model.values():
            if set(rates) != {"input", "output", "cache_hit"} or any(
                    type(v) not in (float, int) or not math.isfinite(v) or not 0 < v < 10000 for v in rates.values()):
                raise ValueError("Invalid cached price table")
    return models


def parse_prices(document):
    """Read numeric table cells only; never execute page markup or instructions."""
    result = {model: {"peak": {}, "off_peak": {}} for model in SNAPSHOT}
    category = None
    for raw in re.findall(r"<tr\b[^>]*>(.*?)</tr>", document, re.S | re.I):
        cells = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", cell)).split())
                 for cell in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", raw, re.S | re.I)]
        if len(cells) < 3:
            continue
        label = " ".join(cells[:-2])
        if "缓存未命中" in label:
            category = "input"
        elif "缓存命中" in label:
            category = "cache_hit"
        elif "tokens输出" in label:
            category = "output"
        period = "off_peak" if "空闲时段" in label else "peak" if "高峰时段" in label else None
        if category and period:
            values = [re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*元", cell) for cell in cells[-2:]]
            if not all(values):
                raise ValueError("Official price table changed")
            for model, match in zip(result, values):
                value = float(match.group(1))
                if not math.isfinite(value) or not 0 < value < 10000:
                    raise ValueError("Invalid official price")
                result[model][period][category] = value
    for model in result.values():
        for period in model.values():
            if set(period) != {"input", "output", "cache_hit"}:
                raise ValueError("Incomplete official price table")
    plain = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", document)).split())
    if not all(part in plain for part in ("deepseek-flash", "deepseek-v4-pro", "周一至周五", "9:00 - 12:00", "14:00 - 18:00", "中国法定节假日")):
        raise ValueError("Official models or time rules changed; retain verified snapshot")
    return validate_models(result)


def get_table():
    global _cached, _attempted_at
    now = datetime.now(timezone.utc)
    with _lock:
        if _cached is None:
            _cached = {"models": copy.deepcopy(SNAPSHOT), "checked_at": "2026-10-24", "status": "verified_snapshot"}
            try:
                import json
                saved = json.loads(CACHE.read_text(encoding="utf-8"))
                if saved.get("source") == SOURCE and saved.get("models"):
                    validate_models(saved["models"])
                    _cached = saved
            except (OSError, ValueError, TypeError):
                pass
        if _attempted_at is not None and now - _attempted_at < timedelta(hours=6):
            return copy.deepcopy(_cached)
        _attempted_at = now
        connection = http.client.HTTPSConnection("api-docs.deepseek.com", timeout=5)
        try:
            connection.request("GET", "/zh-cn/quick_start/pricing/", headers={"User-Agent": "TomeAgent/1.0", "Accept": "text/html"})
            response = connection.getresponse()
            raw = response.read(2_000_001)
            if response.status != 200 or len(raw) > 2_000_000:
                raise ValueError("Official pricing page unavailable")
            models = parse_prices(raw.decode("utf-8"))
            _cached = {"models": models, "checked_at": now.astimezone(BEIJING).isoformat(timespec="seconds"), "status": "live", "source": SOURCE}
            try:
                from .service import _atomic_json
                _atomic_json(CACHE, _cached)
            except OSError:
                pass
        except Exception:
            _cached = {**_cached, "status": "cached"}
        finally:
            connection.close()
        return copy.deepcopy(_cached)


def period_at(moment):
    if moment.tzinfo is None:
        raise ValueError("Pricing time must include timezone")
    local = moment.astimezone(BEIJING)
    day = local.strftime("%m-%d")
    holiday = any(start <= day <= end for start, end in HOLIDAYS.get(local.year, []))
    peak = local.weekday() < 5 and not holiday and (9 <= local.hour < 12 or 14 <= local.hour < 18)
    return "peak" if peak else "off_peak"


def quote(model, moment=None):
    moment = moment or datetime.now(timezone.utc)
    table = get_table()
    aliases = {"deepseek-v4-flash": "deepseek-flash", "deepseek-v4-flash-vision-exp": "deepseek-flash"}
    reference_only = model in ("deepseek-chat", "deepseek-reasoner")
    priced_model = "deepseek-flash" if reference_only else aliases.get(model, model)
    period = period_at(moment)
    rates = table["models"].get(priced_model, {}).get(period)
    peak = table["models"].get(priced_model, {}).get("peak")
    warning = "当前旧模型名不在官方现价表中，按 Flash 参考价估算；不代表已确认其实际路由或计费。" if reference_only else ""
    if moment.astimezone(BEIJING).year not in HOLIDAYS:
        warning += " 该年度节假日历尚未更新，工作日峰时按高峰价保守估算。"
    return {"model": priced_model, "requested_model": model, "period": period,
            "label": "高峰时段" if period == "peak" else "空闲时段",
            "rates": rates, "peak_rates": peak, "source": SOURCE,
            "checked_at": table["checked_at"], "status": table["status"],
            "currency": "CNY", "time": moment.astimezone(BEIJING).isoformat(timespec="seconds"),
            "rule": "北京时间周一至周五（不含法定节假日）9:00–12:00、14:00–18:00为高峰；其余含周末为空闲时段。",
            "warning": warning or ("该模型不在已核验价表内，暂无法自动估算费用。" if rates is None else "")}
