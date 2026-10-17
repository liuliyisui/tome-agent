"""Non-streaming chat/completions adapter; external requests are opt-in.

No credential discovery, SDK dependency, redirects, proxies or network retries.
Prices are caller-supplied estimates, never claimed to be a provider bill.
"""
from dataclasses import dataclass, field
import http.client
import math
import socket
from urllib.parse import urlsplit

from .domain import ContractError, canonical, integer, strict_json, text
from .models import ModelReply, ModelRequest


class ProviderError(ContractError):
    """Sanitized failure; no response body, credential or request dump."""


@dataclass(frozen=True)
class ChatCompletionProvider:
    endpoint: str
    model: str
    api_key: str = field(repr=False)
    input_usd_per_million: float
    output_usd_per_million: float
    allow_remote: bool = False
    timeout_seconds: float = 30.0
    max_response_bytes: int = 1_048_576
    thinking_enabled: bool | None = None

    def __post_init__(self):
        url = urlsplit(self.endpoint)
        if (url.scheme not in ("http", "https") or not url.hostname or url.username
                or url.password or url.query or url.fragment or not url.path.endswith("/chat/completions")):
            raise ContractError("Use a complete chat/completions URL without credentials, query or fragment")
        local = url.hostname in ("127.0.0.1", "::1")
        if not local and (not self.allow_remote or url.scheme != "https"):
            raise ContractError("Remote provider disabled; explicit permission and HTTPS are required")
        if type(self.allow_remote) is not bool:
            raise ContractError("allow_remote must be boolean")
        for price in (self.input_usd_per_million, self.output_usd_per_million):
            if type(price) not in (int, float) or not math.isfinite(price) or price < 0:
                raise ContractError("Explicit finite nonnegative token prices required")
        if (type(self.timeout_seconds) not in (int, float) or not math.isfinite(self.timeout_seconds)
                or not 0 < self.timeout_seconds <= 300):
            raise ContractError("Socket timeout must be positive and at most 300 seconds")
        integer(self.max_response_bytes, "max_response_bytes", 1)
        if self.max_response_bytes > 8_388_608:
            raise ContractError("Response cap exceeds 8 MiB")
        text(self.model, "model")
        if self.thinking_enabled is not None and type(self.thinking_enabled) is not bool:
            raise ContractError("thinking_enabled must be boolean or None")
        if (not isinstance(self.api_key, str) or not self.api_key
                or any(ord(c) < 33 or ord(c) > 126 for c in self.api_key)):
            raise ContractError("Explicit printable credential required; never read from environment")
        try:
            url.port
        except ValueError:
            raise ContractError("Invalid endpoint port") from None

    def complete(self, request: ModelRequest) -> ModelReply:
        integer(request.max_output_tokens, "max_output_tokens", 1)
        text(request.system, "system prompt")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": request.system},
                         {"role": "user", "content": canonical(request.payload)}],
            "max_tokens": request.max_output_tokens,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        if self.thinking_enabled is not None:
            payload["thinking"] = {"type": "enabled" if self.thinking_enabled else "disabled"}
        body = canonical(payload).encode("utf-8")
        if len(body) > 1_048_576:
            raise ProviderError("Request exceeds 1 MiB; configure a retrieval policy")
        url = urlsplit(self.endpoint)
        factory = http.client.HTTPSConnection if url.scheme == "https" else http.client.HTTPConnection
        connection = factory(url.hostname, port=url.port, timeout=self.timeout_seconds)
        try:
            connection.request("POST", url.path, body, {
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json", "Accept": "application/json",
            })
            response = connection.getresponse()
            if response.status != 200:
                raise ProviderError(f"Provider HTTP {response.status}; no retry or redirect")
            raw = response.read(self.max_response_bytes + 1)
            if len(raw) > self.max_response_bytes:
                raise ProviderError("Provider response exceeded configured byte cap")
        except (TimeoutError, socket.timeout):
            raise ProviderError("Provider socket timeout; delivery and billing may be unknown") from None
        except (OSError, http.client.HTTPException):
            raise ProviderError("Provider transport failed; delivery and billing may be unknown") from None
        finally:
            connection.close()
        try:
            data = strict_json(raw.decode("utf-8"))
            choices = data["choices"]
            if not isinstance(choices, list) or len(choices) != 1:
                raise ContractError("One completion required")
            choice = choices[0]
            if choice["finish_reason"] != "stop":
                raise ContractError("Completion not normally finished")
            content = text(choice["message"]["content"], "completion")
            usage = data["usage"]
            incoming = integer(usage["prompt_tokens"], "prompt_tokens")
            outgoing = integer(usage["completion_tokens"], "completion_tokens")
            if "total_tokens" in usage and integer(usage["total_tokens"], "total_tokens") != incoming + outgoing:
                raise ContractError("Inconsistent token usage")
            if outgoing > request.max_output_tokens:
                raise ContractError("Completion exceeds requested output token limit")
            cost = (incoming * self.input_usd_per_million + outgoing * self.output_usd_per_million) / 1_000_000
            if not math.isfinite(cost):
                raise ContractError("Nonfinite cost estimate")
            return ModelReply(content, incoming, outgoing, cost)
        except (ContractError, UnicodeError, KeyError, TypeError, IndexError, AttributeError):
            raise ProviderError("Invalid, incomplete or unsupported completion/usage; reservation retained") from None
