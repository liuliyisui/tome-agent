"""Stream prose from supported providers while keeping usage accounting intact."""

import http.client
import json
import math
import time
from urllib.parse import urlsplit

from tome_writer.chat_provider import ProviderError
from tome_writer.domain import ContractError, canonical, integer, strict_json, text
from tome_writer.models import ModelReply


def _partial_json_prose(raw):
    """Read a top-level prose field, even when its JSON string is incomplete."""
    decoder = json.JSONDecoder()
    index = 0

    def skip_space(pos):
        while pos < len(raw) and raw[pos].isspace():
            pos += 1
        return pos

    index = skip_space(index)
    if index >= len(raw) or raw[index] != "{":
        return ""
    index += 1
    while True:
        index = skip_space(index)
        try:
            key, index = decoder.raw_decode(raw, index)
        except (ValueError, IndexError):
            return ""
        index = skip_space(index)
        if index >= len(raw) or raw[index] != ":":
            return ""
        index = skip_space(index + 1)
        if key in ("text", "new_stage_text") and index < len(raw) and raw[index] == '"':
            start = index + 1
            end = start
            escaped = False
            while end < len(raw):
                char = raw[end]
                if char == '"' and not escaped:
                    break
                if char == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False
                end += 1
            encoded = raw[start:end]
            # A chunk may end midway through an escape such as \\u4e2d.
            for trim in range(min(len(encoded), 6) + 1):
                prefix = encoded[: len(encoded) - trim] if trim else encoded
                try:
                    return json.loads('"' + prefix + '"')
                except ValueError:
                    continue
            return ""
        try:
            _, index = decoder.raw_decode(raw, index)
        except (ValueError, IndexError):
            return ""
        index = skip_space(index)
        if index >= len(raw) or raw[index] != ",":
            return ""
        index += 1


def describe_prose_request(book, request, count_units):
    """Distinguish accepted chapter stages from the current model response."""
    payload = request.payload
    number = payload.get("chapter_number")
    prepared = book.get("prepared_events", {}).get(str(number), {})
    stages = prepared.get("stage_realizations", [])
    task = payload.get("stage_task")
    task = task if isinstance(task, dict) else {}
    draft = payload.get("current_draft")
    return {
        "live_completed_units": sum(
            count_units(stage.get("text", "")) for stage in stages
        ),
        "live_unit_number": task.get("unit_number"),
        "live_unit_total": task.get("total_units"),
        "live_draft_units": count_units(draft) if isinstance(draft, str) else None,
    }


class ProseProgressProvider:
    """Count received prose from one request; never store partial prose as a chapter."""

    def __init__(self, provider, progress, count_units, describe_request=None):
        self.provider = provider
        self.progress = progress
        self.count_units = count_units
        self.describe_request = describe_request
        self.output_number = 0

    def reset_chapter(self):
        self.output_number = 0

    def complete(self, request):
        if request.role != "writer":
            return self.provider.complete(request)
        plain_prose = request.payload.get("output_mode") == "plain_prose"
        provider = self.provider
        integer(request.max_output_tokens, "max_output_tokens", 1)
        text(request.system, "system prompt")
        payload = {
            "model": provider.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": canonical(request.payload)},
            ],
            provider.token_limit_field: request.max_output_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if not plain_prose:
            payload["response_format"] = {"type": "json_object"}
        if provider.thinking_enabled is not None:
            payload["thinking"] = {
                "type": "enabled" if provider.thinking_enabled else "disabled"
            }
        body = canonical(payload).encode("utf-8")
        if len(body) > 1_048_576:
            raise ProviderError("Request exceeds 1 MiB; configure a retrieval policy")
        url = urlsplit(provider.endpoint)
        factory = (
            http.client.HTTPSConnection
            if url.scheme == "https"
            else http.client.HTTPConnection
        )
        connection = factory(
            url.hostname, port=url.port, timeout=provider.timeout_seconds
        )
        chunks = []
        size = 0
        usage = None
        finish = None
        done = False
        last_report = 0.0
        details = self.describe_request(request) if self.describe_request else {}
        if self.describe_request:
            self.output_number += 1
            details["live_output_number"] = self.output_number
        self.progress({**details, "live_units": 0, "live_phase": "writing"})
        try:
            connection.request(
                "POST",
                url.path,
                body,
                {
                    "Authorization": "Bearer " + provider.api_key,
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
            )
            response = connection.getresponse()
            if response.status != 200:
                raise ProviderError(
                    f"Provider HTTP {response.status}; no retry or redirect",
                    http_status=response.status,
                )
            while True:
                line = response.readline(provider.max_response_bytes + 1)
                if not line:
                    break
                size += len(line)
                if size > provider.max_response_bytes:
                    raise ProviderError(
                        "Provider response exceeded configured byte cap"
                    )
                if not line.startswith(b"data:"):
                    continue
                data = line[5:].strip()
                if data == b"[DONE]":
                    done = True
                    break
                event = strict_json(data.decode("utf-8"))
                if not isinstance(event, dict):
                    raise ContractError("Invalid stream event")
                if event.get("usage") is not None:
                    usage = event["usage"]
                choices = event.get("choices")
                if not isinstance(choices, list) or len(choices) > 1:
                    raise ContractError("Invalid streamed choices")
                if not choices:
                    continue
                choice = choices[0]
                if choice.get("finish_reason") is not None:
                    finish = choice["finish_reason"]
                delta = choice.get("delta") or {}
                content = delta.get("content")
                if content is not None:
                    if not isinstance(content, str):
                        raise ContractError("Invalid streamed content")
                    chunks.append(content)
                    now = time.monotonic()
                    if now - last_report >= 0.5:
                        self.progress(
                            {
                                "live_units": self.count_units(
                                    "".join(chunks)
                                    if plain_prose
                                    else _partial_json_prose("".join(chunks))
                                ),
                                "live_phase": "writing",
                            }
                        )
                        last_report = now
            if (
                not done
                or finish not in ("stop", "length")
                or not isinstance(usage, dict)
            ):
                raise ContractError("Incomplete stream or missing usage")
            incoming = integer(usage["prompt_tokens"], "prompt_tokens")
            outgoing = integer(usage["completion_tokens"], "completion_tokens")
            if (
                "total_tokens" in usage
                and integer(usage["total_tokens"], "total_tokens")
                != incoming + outgoing
            ):
                raise ContractError("Inconsistent token usage")
            if outgoing > request.max_output_tokens:
                raise ContractError("Completion exceeds requested output token limit")
            content = text("".join(chunks), "completion")
            cost = (
                incoming * provider.input_usd_per_million
                + outgoing * provider.output_usd_per_million
            ) / 1_000_000
            if not math.isfinite(cost):
                raise ContractError("Nonfinite cost estimate")
            self.progress(
                {
                    "live_units": self.count_units(
                        content if plain_prose else _partial_json_prose(content)
                    ),
                    "live_phase": "processing",
                }
            )
            return ModelReply(content, incoming, outgoing, cost, finish)
        except ProviderError:
            raise
        except (TimeoutError, OSError, http.client.HTTPException):
            raise ProviderError(
                "Provider transport failed; delivery and billing may be unknown"
            ) from None
        except (
            ContractError,
            UnicodeError,
            KeyError,
            TypeError,
            IndexError,
            AttributeError,
        ):
            raise ProviderError(
                "Invalid, incomplete or unsupported completion/usage; reservation retained"
            ) from None
        finally:
            connection.close()
