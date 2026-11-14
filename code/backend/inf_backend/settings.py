"""Local configuration for the official DeepSeek chat-completions endpoint."""

import hashlib
import http.client
import ipaddress
import json
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


def _validate_endpoint(endpoint, *, allow_base_url=False):
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
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or port not in (None, 443)
        or url.hostname.lower() == "localhost"
    ):
        raise ValueError(
            "请填写有效的 HTTPS 模型地址，地址中不能包含账号、密码、查询参数或片段"
        )
    try:
        ipaddress.ip_address(url.hostname)
    except ValueError:
        pass
    else:
        raise ValueError("模型接口请使用服务商域名")
    suffix = "/chat/completions"
    path = url.path
    if allow_base_url:
        if "?" in endpoint or "#" in endpoint or "\\" in endpoint:
            raise ValueError("Base URL 不能包含查询参数、片段或反斜杠")
        endpoint = endpoint.rstrip("/")
        path = path.rstrip("/")
        if not path.endswith(suffix):
            endpoint += suffix
            path += suffix
    if len(endpoint) > 2048 or not path.endswith(suffix):
        raise ValueError("接口须为 HTTPS 地址并以 /chat/completions 结尾")
    return endpoint


def _model_values(provider, model, endpoint, api_key, provider_name=None):
    if provider_name is None:
        provider_name = {
            "deepseek": "DeepSeek",
            "openai": "OpenAI",
            "compatible": "自定义",
        }.get(provider, "")
    if (
        not isinstance(provider_name, str)
        or not provider_name.strip()
        or len(provider_name.strip()) > 80
        or any(ord(char) < 32 or ord(char) == 127 for char in provider_name)
    ):
        raise ValueError("请输入有效的供应商名称")
    provider_name = provider_name.strip()
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
    endpoint = _validate_endpoint(endpoint, allow_base_url=provider == "compatible")
    if api_key == "":
        name = _key_name(endpoint)
        values = {**_dotenv(BACKEND_ROOT / ".env"), **os.environ}
        api_key = values.get(name, "") or (
            values.get("DEEPSEEK_API_KEY", "") if provider == "deepseek" else ""
        )
    if not isinstance(api_key, str) or not re.fullmatch(
        r"[A-Za-z0-9._~+\-/=]{1,512}", api_key
    ):
        raise ValueError("请填写有效的 API Key，或先保存此接口的密钥")
    return provider, model, endpoint, api_key, provider_name


def test_model_connection(provider, model, endpoint, api_key, provider_name=None):
    provider, model, endpoint, api_key, _ = _model_values(
        provider, model, endpoint, api_key, provider_name
    )
    url = urlsplit(endpoint)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with OK."}],
        "max_completion_tokens" if provider == "openai" else "max_tokens": 64,
        "stream": False,
    }
    connection = http.client.HTTPSConnection(url.hostname, port=url.port, timeout=30)
    try:
        connection.request(
            "POST",
            url.path,
            json.dumps(payload).encode("utf-8"),
            {
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(
                f"连接测试失败：服务商返回 HTTP {response.status}，请检查密钥、地址、模型和额度"
            )
        raw = response.read(262145)
        if len(raw) > 262144:
            raise ValueError("连接测试失败：服务商返回内容过大")
        result = json.loads(raw)
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("choices"), list)
            or not result["choices"]
        ):
            raise ValueError("连接测试失败：服务商返回的接口格式不兼容")
    except (OSError, http.client.HTTPException, UnicodeError, json.JSONDecodeError):
        raise ValueError(
            "连接测试失败：无法连接服务商或返回格式无效，请检查网络和接口地址"
        ) from None
    finally:
        connection.close()
    return True


def configure_model(provider, model, endpoint, api_key, provider_name=None):
    provider, model, endpoint, api_key, provider_name = _model_values(
        provider, model, endpoint, api_key, provider_name
    )
    values = {
        "TOME_PROVIDER": provider,
        "TOME_PROVIDER_NAME": provider_name,
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
    provider_name: str = ""

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
            provider_name=get(
                "TOME_PROVIDER_NAME",
                {
                    "deepseek": "DeepSeek",
                    "openai": "OpenAI",
                    "compatible": "自定义",
                }.get(provider, ""),
            ),
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
