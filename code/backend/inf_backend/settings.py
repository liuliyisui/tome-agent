"""Local configuration for the official DeepSeek chat-completions endpoint."""

import hashlib
import ipaddress
import os
import re
import tempfile
import threading
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

BACKEND_ROOT = Path(
    os.environ.get("TOME_DATA_HOME") or Path(__file__).resolve().parents[1]
)
_config_lock = threading.Lock()


def _key_name(endpoint):
    return (
        "TOME_MODEL_KEY_"
        + hashlib.sha256(endpoint.encode("utf-8")).hexdigest()[:24].upper()
    )


def _validate_endpoint(endpoint):
    if (
        not isinstance(endpoint, str)
        or len(endpoint) > 2048
        or any(ord(c) < 33 or ord(c) > 126 for c in endpoint)
    ):
        raise ValueError("请输入有效的模型接口地址")
    url = urlsplit(endpoint)
    try:
        port = url.port
    except ValueError:
        raise ValueError("模型接口端口无效") from None
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or not url.path.endswith("/chat/completions")
        or port not in (None, 443)
        or url.hostname.lower() == "localhost"
    ):
        raise ValueError("接口须为 HTTPS 地址并以 /chat/completions 结尾")
    try:
        ipaddress.ip_address(url.hostname)
    except ValueError:
        pass
    else:
        raise ValueError("模型接口请使用服务商域名")
    return endpoint


def configure_model(provider, model, endpoint, api_key):
    if provider not in ("deepseek", "openai", "compatible"):
        raise ValueError("请选择支持的模型服务类型")
    if not isinstance(model, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}", model
    ):
        raise ValueError("请输入有效的模型名称")
    if provider == "deepseek":
        endpoint = "https://api.deepseek.com/chat/completions"
    elif provider == "openai":
        endpoint = "https://api.openai.com/v1/chat/completions"
    endpoint = _validate_endpoint(endpoint)
    if not isinstance(api_key, str) or not re.fullmatch(
        r"[A-Za-z0-9._~+\-/=]{1,512}", api_key
    ):
        raise ValueError("请填写有效的 API Key")
    values = {
        "TOME_PROVIDER": provider,
        "TOME_MODEL": model,
        "TOME_ENDPOINT": endpoint,
        _key_name(endpoint): api_key,
    }
    with _config_lock:
        path = BACKEND_ROOT / ".env"
        if path.is_symlink():
            raise ValueError("配置文件路径不安全")
        lines = (
            path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
        )
        lines = [line for line in lines if line.split("=", 1)[0].strip() not in values]
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=BACKEND_ROOT,
                prefix=".env-",
                delete=False,
            ) as output:
                temporary = Path(output.name)
                output.write(
                    "\n".join(
                        lines + [f"{key}={value}" for key, value in values.items()]
                    )
                    + "\n"
                )
            os.replace(temporary, path)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
    return Settings.load(require_key=False)


def configure_api_key(api_key):
    if not isinstance(api_key, str) or not re.fullmatch(
        r"sk-[A-Za-z0-9_-]{16,250}", api_key.strip()
    ):
        raise ValueError("请填写有效的 DeepSeek API Key（以 sk- 开头）")
    with _config_lock:
        if Settings.load(require_key=False).api_key.strip():
            raise ValueError("API Key 已配置，无需重复初始化")
        path = BACKEND_ROOT / ".env"
        if path.is_symlink():
            raise ValueError("配置文件路径不安全")
        lines = (
            path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
        )
        lines = [
            line
            for line in lines
            if line.split("=", 1)[0].strip() != "DEEPSEEK_API_KEY"
        ]
        lines.append("DEEPSEEK_API_KEY=" + api_key.strip())
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=BACKEND_ROOT,
                prefix=".env-",
                delete=False,
            ) as output:
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
    provider: str = "deepseek"

    @classmethod
    def load(cls, path=None, require_key=True):
        file_values = _dotenv(path or BACKEND_ROOT / ".env")
        values = {**file_values, **os.environ}
        if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
            values["DEEPSEEK_API_KEY"] = file_values.get("DEEPSEEK_API_KEY", "")

        def get(name, default):
            return values.get(name) or default

        raw_thinking = str(get("DEEPSEEK_THINKING", "false")).lower()
        provider = get("TOME_PROVIDER", "deepseek")
        endpoint = (
            get("TOME_ENDPOINT", "")
            if values.get("TOME_PROVIDER")
            else get("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/chat/completions")
        )
        _validate_endpoint(endpoint)
        if provider not in ("deepseek", "openai", "compatible"):
            raise ValueError("模型服务类型无效")
        if provider == "deepseek" and (
            urlsplit(endpoint).hostname != "api.deepseek.com"
            or urlsplit(endpoint).path
            not in ("/chat/completions", "/v1/chat/completions")
        ):
            raise ValueError("DeepSeek 必须使用官方接口地址")
        if (
            provider == "openai"
            and endpoint != "https://api.openai.com/v1/chat/completions"
        ):
            raise ValueError("OpenAI 必须使用官方接口地址")
        result = cls(
            api_key=get(_key_name(endpoint), "")
            or (get("DEEPSEEK_API_KEY", "") if provider == "deepseek" else ""),
            model=get("TOME_MODEL", "deepseek-chat")
            if values.get("TOME_PROVIDER")
            else get("DEEPSEEK_MODEL", "deepseek-chat"),
            endpoint=endpoint,
            thinking=(raw_thinking == "true") if provider == "deepseek" else None,
            provider=provider,
            timeout=float(get("DEEPSEEK_TIMEOUT", "180")),
            max_calls=int(get("INF_MAX_CALLS", "40")),
            max_cost_usd=float(get("INF_MAX_COST_USD", "100")),
            input_usd_per_million=float(get("INF_INPUT_USD_PER_MILLION", "0"))
            if provider == "deepseek"
            else 0.0,
            output_usd_per_million=float(get("INF_OUTPUT_USD_PER_MILLION", "0"))
            if provider == "deepseek"
            else 0.0,
        )
        if require_key and not result.api_key.strip():
            raise ValueError("请先配置对应模型服务的 API Key")
        if result.max_calls <= 0 or result.max_cost_usd < 0:
            raise ValueError("INF 预算必须为有效正数")
        return result

    def public_config(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "endpoint": self.endpoint,
            "thinking": self.thinking,
        }

    @classmethod
    def for_book(cls, config):
        from dataclasses import replace

        current = cls.load(require_key=False)
        if current.public_config() == config and current.api_key.strip():
            return current
        endpoint = _validate_endpoint(config["endpoint"])
        provider = config.get("provider", "deepseek")
        if provider not in ("deepseek", "openai", "compatible"):
            raise ValueError("作品使用的模型服务不受支持")
        if provider == "deepseek" and (
            urlsplit(endpoint).hostname != "api.deepseek.com"
            or urlsplit(endpoint).path
            not in ("/chat/completions", "/v1/chat/completions")
        ):
            raise ValueError("作品的 DeepSeek 接口地址无效")
        if (
            provider == "openai"
            and endpoint != "https://api.openai.com/v1/chat/completions"
        ):
            raise ValueError("作品的 OpenAI 接口地址无效")
        values = {**_dotenv(BACKEND_ROOT / ".env"), **os.environ}
        key = values.get(_key_name(endpoint), "")
        if not key and provider == "deepseek":
            key = values.get("DEEPSEEK_API_KEY", "") or _dotenv(
                BACKEND_ROOT / ".env"
            ).get("DEEPSEEK_API_KEY", "")
        if not key.strip():
            raise ValueError("请先配置此作品所用模型服务的 API Key")
        return replace(
            current,
            api_key=key,
            provider=provider,
            endpoint=endpoint,
            model=config["model"],
            thinking=config.get("thinking"),
            input_usd_per_million=float(values.get("INF_INPUT_USD_PER_MILLION") or 0)
            if provider == "deepseek"
            else 0.0,
            output_usd_per_million=float(values.get("INF_OUTPUT_USD_PER_MILLION") or 0)
            if provider == "deepseek"
            else 0.0,
        )
