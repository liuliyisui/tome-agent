"""Local configuration for the official DeepSeek chat-completions endpoint."""
import os
import re
import tempfile
import threading
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

BACKEND_ROOT = Path(os.environ.get("TOME_DATA_HOME") or Path(__file__).resolve().parents[1])
_config_lock = threading.Lock()


def configure_api_key(api_key):
    if not isinstance(api_key, str) or not re.fullmatch(r"sk-[A-Za-z0-9_-]{16,250}", api_key.strip()):
        raise ValueError("请填写有效的 DeepSeek API Key（以 sk- 开头）")
    with _config_lock:
        if Settings.load(require_key=False).api_key.strip():
            raise ValueError("API Key 已配置，无需重复初始化")
        path = BACKEND_ROOT / ".env"
        if path.is_symlink():
            raise ValueError("配置文件路径不安全")
        lines = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
        lines = [line for line in lines if line.split("=", 1)[0].strip() != "DEEPSEEK_API_KEY"]
        lines.append("DEEPSEEK_API_KEY=" + api_key.strip())
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=BACKEND_ROOT, prefix=".env-", delete=False) as output:
                temporary = Path(output.name)
                output.write("\n".join(lines) + "\n")
            os.replace(temporary, path)
        except OSError:
            raise ValueError("无法保存配置，请检查后端目录的写入权限") from None
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
    return Settings.load(require_key=False)


def _dotenv(path):
    values = {}
    path = Path(path)
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if value[:1] == value[-1:] and value[:1] in ("'", '"'):
            value = value[1:-1]
        values[key] = value
    return values


@dataclass
class Settings:
    api_key: str = field(repr=False)
    model: str = "deepseek-chat"
    endpoint: str = "https://api.deepseek.com/chat/completions"
    thinking: bool | None = False
    timeout: float = 180.0
    max_calls: int = 40
    max_cost_usd: float = 100.0
    input_usd_per_million: float = 0.0
    output_usd_per_million: float = 0.0

    @classmethod
    def load(cls, path=None, require_key=True):
        file_values = _dotenv(path or BACKEND_ROOT / ".env")
        values = {**file_values, **os.environ}
        if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
            values["DEEPSEEK_API_KEY"] = file_values.get("DEEPSEEK_API_KEY", "")
        def get(name, default):
            return values.get(name) or default
        raw_thinking = str(get("DEEPSEEK_THINKING", "false")).lower()
        result = cls(
            api_key=get("DEEPSEEK_API_KEY", ""),
            model=get("DEEPSEEK_MODEL", "deepseek-chat"),
            endpoint=get("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/chat/completions"),
            thinking=raw_thinking == "true",
            timeout=float(get("DEEPSEEK_TIMEOUT", "180")),
            max_calls=int(get("INF_MAX_CALLS", "40")),
            max_cost_usd=float(get("INF_MAX_COST_USD", "100")),
            input_usd_per_million=float(get("INF_INPUT_USD_PER_MILLION", "0")),
            output_usd_per_million=float(get("INF_OUTPUT_USD_PER_MILLION", "0")),
        )
        url = urlsplit(result.endpoint)
        if (url.scheme != "https" or url.hostname != "api.deepseek.com" or url.username
                or url.password or url.query or url.fragment
                or url.path.rstrip("/") not in ("/chat/completions", "/v1/chat/completions")):
            raise ValueError("只允许使用 DeepSeek 官方 HTTPS chat/completions 地址")
        if require_key and not result.api_key.strip():
            raise ValueError("请先在页面中配置 DeepSeek API Key")
        if result.max_calls <= 0 or result.max_cost_usd < 0:
            raise ValueError("INF 预算必须为有效正数")
        return result

    def public_config(self):
        return {"provider": "deepseek", "model": self.model, "endpoint": self.endpoint,
                "thinking": self.thinking}
