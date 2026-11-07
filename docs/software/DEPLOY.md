# 部署到服务器（对外提供网址）

> 本文保留的是**单用户旧部署方案**，不能隔离不同用户的作品或模型密钥。多人服务器请使用 [Linux 多用户部署说明](LINUX_HOSTED.md)。部署示例文件现位于 `code/backend/deploy/`。

本项目原本面向本机单用户，现已支持对外部署：后端可用 `--host` / `TOME_ALLOWED_HOSTS` 放行域名，前端无需改动。

> ⚠️ 该应用**没有账号体系**。暴露到公网前必须：
> 1. 使用 HTTPS；
> 2. 在反向代理上加一层鉴权（Basic Auth / 或只允许 VPN、SSH 隧道访问）；
> 3. 保管好 `DEEPSEEK_API_KEY`，它决定谁能花你的模型额度。
>
> 另外后端基于 Python 标准库 `http.server`，适合个人或小流量，不建议作为高并发生产服务。

## 一、准备

1. **服务器**：Linux（Ubuntu 22.04+ 或其他发行版），有公网 IP。
2. **域名**：在域名服务商处添加 A 记录，例如 `tome.example.com → 服务器IP`。
3. **防火墙**：放行 80/443（以及你 SSH 用的端口）。
4. **模型 Key**：`DEEPSEEK_API_KEY`。

## 二、方案 A：Docker（推荐）

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx apache2-utils
sudo git clone https://github.com/liuliyisui/tome-agent.git /opt/tome-agent
cd /opt/tome-agent

# 配置运行参数（Compose 会自动读取同目录 .env）
cat > .env <<'EOF'
DEEPSEEK_API_KEY=sk-你的key
TOME_ALLOWED_HOSTS=tome.example.com
EOF

# 构建并启动（容器只监听 127.0.0.1:8765）
sudo docker compose --env-file .env -f code/backend/deploy/docker-compose.yml up -d --build
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/   # 期望 200
```

配置 Nginx（使用仓库里的 `code/backend/deploy/nginx.conf`）：

```bash
sudo cp code/backend/deploy/nginx.conf /etc/nginx/sites-available/tome
sudo ln -sf /etc/nginx/sites-available/tome /etc/nginx/sites-enabled/tome
sudo htpasswd -c /etc/nginx/.htpasswd 你的用户名      # 设置访问密码
sudo certbot --nginx -d tome.example.com              # 申请 HTTPS 证书
sudo nginx -t && sudo systemctl reload nginx
```

现在访问 `https://tome.example.com` 即可（会先弹出 Basic Auth 登录框）。

> 需要 PostgreSQL 时：`docker compose --env-file .env -f code/backend/deploy/docker-compose.yml --profile postgres up -d`，并在 `.env` 里设置
> `POSTGRES_PASSWORD=...` 与 `DATABASE_URL=postgresql://tome:同一个密码@postgres:5432/tome`。

## 三、方案 B：systemd + Nginx（不用 Docker）

```bash
sudo apt install -y python3.11 python3.11-venv git nginx certbot python3-certbot-nginx apache2-utils
sudo useradd -r -s /usr/sbin/nologin tome
sudo git clone https://github.com/liuliyisui/tome-agent.git /opt/tome-agent
sudo chown -R tome:tome /opt/tome-agent
cd /opt/tome-agent

sudo -u tome python3.11 -m venv code/backend/.venv
sudo -u tome code/backend/.venv/bin/pip install -r code/backend/requirements.txt

# 配置 Key 与允许域名
sudo -u tome cp code/backend/.env.example code/backend/.env
sudo -u tome sed -i 's/^DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=sk-你的key/' code/backend/.env
```

安装服务（修改 `code/backend/deploy/tome-agent.service` 里的域名后复制）：

```bash
sudo cp code/backend/deploy/tome-agent.service /etc/systemd/system/tome-agent.service
sudo systemctl daemon-reload
sudo systemctl enable --now tome-agent
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/   # 期望 200
```

Nginx 与证书步骤同方案 A。

## 四、没有域名，想先临时分享一个网址

用 Cloudflare 快速隧道即可（HTTPS 自动、无需备案域名）：

```bash
# 服务器上先确保后端在 127.0.0.1:8765 运行
cloudflared tunnel --url http://127.0.0.1:8765
```

它会打印形如 `https://xxxx-yyyy.trycloudflare.com` 的网址。把这个域名写进允许列表并重启后端：

```bash
# systemd 部署：编辑 Environment=TOME_ALLOWED_HOSTS=xxxx-yyyy.trycloudflare.com
sudo systemctl edit --full tome-agent && sudo systemctl restart tome-agent
# Docker 部署：把 .env 的 TOME_ALLOWED_HOSTS 改成该域名后
docker compose --env-file .env -f code/backend/deploy/docker-compose.yml up -d
```

> 快速隧道的域名每次重启都会变，适合临时演示；长期使用请配置命名隧道或直接用域名。

## 五、数据与备份

- 所有作品、检查点、技能都在 `code/backend/data/`，**必须持久化并定期备份**：
  ```bash
  tar czf tome-data-$(date +%F).tgz -C /opt/tome-agent/code/backend data
  ```
- 使用 PostgreSQL 时，备份数据库而不是只备份文件。

## 六、常见问题

| 现象 | 原因 / 处理 |
|---|---|
| 访问域名返回 403「仅允许同源访问」 | 没设 `TOME_ALLOWED_HOSTS`，或其中未包含浏览器地址栏的域名（含端口则写 `域名:端口`）。 |
| 页面能开但操作报 403 | 反向代理改写了 Host（如 `proxy_set_header Host 127.0.0.1:8765`）。应改成 `proxy_set_header Host $host;`。 |
| 生成章节时请求中断 | 反向代理超时。`proxy_read_timeout` 调到 900s。 |
| 刷新后进度丢失 | 生成任务保存在后端内存。单实例部署正常；请勿多副本负载均衡。 |
| 只想自己用 | 不必暴露公网，用 SSH 隧道：`ssh -N -L 8765:127.0.0.1:8765 user@服务器`，本地访问 `http://127.0.0.1:8765`。 |

## 七、启动参数参考

```
python -m inf_backend.web --host 127.0.0.1 --port 8765 --allowed-hosts tome.example.com
```

也可以用环境变量：`TOME_HOST`、`TOME_ALLOWED_HOSTS`（逗号分隔）。
默认仍只监听 `127.0.0.1`，不设置允许列表时仅本机可访问。
