"""DeepSeek Chat Completions transport, explicit budgets, no automatic retries."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse
from dotenv import dotenv_values
from openai import OpenAI, APIError
from tome_agent.agent import Response, ToolCall

PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass
class Settings:
    api_key: str = field(repr=False)
    model: str = "deepseek-flash"
    base_url: str = "https://api.deepseek.com"
    thinking: bool = False
    max_tokens: int = 8192
    timeout: float = 180
    max_requests: int = 100
    max_total_tokens: int = 300000

    @classmethod
    def load(cls, path=None, require_key=True):
        values = {**dotenv_values(path or PROJECT_ROOT / ".env"), **os.environ}
        def get(name, default):
            return values.get(name) or default
        settings = cls(api_key=get("DEEPSEEK_API_KEY", ""),
            model=get("DEEPSEEK_MODEL", "deepseek-flash"),
            base_url=get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
            thinking=str(get("DEEPSEEK_THINKING", "false")).lower() == "true",
            max_tokens=int(get("DEEPSEEK_MAX_TOKENS", "8192")),
            timeout=float(get("DEEPSEEK_TIMEOUT", "180")),
            max_requests=int(get("TOME_MAX_REQUESTS", "100")),
            max_total_tokens=int(get("TOME_MAX_TOTAL_TOKENS", "300000")))
        parsed = urlparse(settings.base_url)
        if parsed.scheme != "https" or parsed.hostname != "api.deepseek.com" or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port not in (None, 443) or parsed.path not in ("", "/v1", "/beta"):
            raise ValueError("Only official DeepSeek HTTPS API addresses are accepted")
        if require_key and not settings.api_key.strip():
            raise ValueError("请在项目 .env 中填写 DEEPSEEK_API_KEY")
        if min(settings.max_tokens, settings.timeout, settings.max_requests, settings.max_total_tokens) <= 0:
            raise ValueError("Model limits must be positive")
        return settings

    def public_config(self):
        return {"provider": "deepseek", "model": self.model, "base_url": self.base_url,
                "thinking": self.thinking, "max_tokens": self.max_tokens}


class DeepSeekModel:
    def __init__(self, settings, client=None):
        self.settings = settings
        self.client = client or OpenAI(api_key=settings.api_key, base_url=settings.base_url,
                                      timeout=settings.timeout, max_retries=0)
        self.requests = 0
        self.total_tokens = 0
        self.usage_log = []

    def complete(self, messages, tools):
        cfg = self.settings
        if self.requests >= cfg.max_requests or self.total_tokens >= cfg.max_total_tokens:
            raise ValueError("本次运行预算已达上限；请检查用量后调整预算")
        self.requests += 1
        kwargs = dict(model=cfg.model, messages=messages,
                      max_tokens=cfg.max_tokens, stream=False,
                      extra_body={"thinking": {"type": "enabled" if cfg.thinking else "disabled"}})
        if tools:
            kwargs["tools"] = tools
        try:
            result = self.client.chat.completions.create(**kwargs)
        except APIError as exc:
            # Do not expose request bodies, authorization headers or provider error bodies.
            raise RuntimeError(f"DeepSeek 请求失败（{type(exc).__name__}）；未自动重试") from None
        usage = result.usage.model_dump() if result.usage else {}
        tokens = usage.get("total_tokens")
        if type(tokens) is not int or tokens < 0:
            raise ValueError("DeepSeek未返回有效用量；停止以避免无法追踪预算")
        self.total_tokens += tokens
        self.usage_log.append(usage)
        if self.total_tokens > cfg.max_total_tokens:
            raise ValueError("本次响应使token预算超限；停止后续请求")
        if not result.choices:
            raise ValueError("DeepSeek响应缺少choices")
        choice = result.choices[0]
        message = choice.message
        calls = []
        for call in message.tool_calls or []:
            try:
                arguments = json.loads(call.function.arguments)
            except (ValueError, TypeError):
                raise ValueError("DeepSeek工具参数不是有效JSON；保留原检查点") from None
            calls.append(ToolCall(call.id, call.function.name, arguments))
        return Response(content=message.content or "", calls=calls,
                        finish_reason=choice.finish_reason, usage=usage,
                        reasoning_content=getattr(message, "reasoning_content", None))
