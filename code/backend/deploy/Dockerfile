# Tome Agent — Linux 部署镜像
# 构建：docker build -f code/backend/deploy/Dockerfile -t tome-agent .
# 运行前请设置 DEEPSEEK_API_KEY 与 TOME_ALLOWED_HOSTS（见 docs/software/DEPLOY.md）
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/code/core_engine:/app/code/backend

WORKDIR /app

# 先装依赖，利用镜像层缓存
COPY code/backend/requirements.txt /app/code/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/code/backend/requirements.txt

COPY . /app

# 作品、检查点、技能等本地数据；请用卷持久化
VOLUME ["/app/code/backend/data"]

EXPOSE 8765
CMD ["python", "-m", "inf_backend.web", "--host", "0.0.0.0", "--port", "8765"]
