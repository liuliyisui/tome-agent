# Linux 多用户部署

本文面向单台 Linux 轻量应用服务器或虚拟机。使用 Python 3.11、Nginx 和 systemd；应用只监听服务器本机，Nginx 负责 HTTPS。此方案使用一台机器及其持久磁盘，不支持多实例共享同一数据目录。多人模式与本地桌面模式互不替换。

## 准备

- 完成多人模式测试后，将代码部署到 `/opt/tome-agent`；准备 Python 3.11、Git 和 Nginx。
- 准备指向服务器的域名和有效 HTTPS 证书。中国内地服务器对外提供域名网站服务前，需要按当地要求完成备案。
- 持久数据目录使用 `/var/lib/tome-agent`，不放在代码目录中。账号、会话、用户作品、Skill 和模型配置均保存在此目录；必须定期备份，并测试恢复。备份包含用户作品和模型密钥，应限制访问并加密保存。
- 服务器防火墙仅开放网站需要的 80/443；SSH 应限定可信来源，不要向公网开放应用的 8765 端口。

以下命令假定已安装 `python3.11`，域名和目录请按实际情况替换。不要在 GitHub 提交服务器环境文件或用户数据。

```sh
sudo useradd --system --create-home --shell /usr/sbin/nologin tome-agent
sudo install -d -o tome-agent -g tome-agent -m 700 /var/lib/tome-agent
sudo install -d -o tome-agent -g tome-agent /opt/tome-agent
sudo -u tome-agent git clone https://github.com/liuliyisui/tome-agent.git /opt/tome-agent
cd /opt/tome-agent
sudo -u tome-agent python3.11 -m venv code/backend/.venv
sudo -u tome-agent code/backend/.venv/bin/python -m pip install -r code/backend/requirements.txt
```

创建 `/etc/tome-agent.env`，将域名替换为自己的 HTTPS 域名：

```text
TOME_PUBLIC_ORIGIN=https://example.com
TOME_DATA_HOME=/var/lib/tome-agent
TOME_WORKER_LIMIT=3
```

模型服务商的自定义兼容接口默认只允许已列出的官方域名。确需其他服务商时，可由管理员设置 `TOME_MODEL_HOSTS`，以英文逗号分隔**完整域名**；请只加入可信的模型服务商。每位用户登录后自行配置自己的模型 API Key，密钥保存在其独立数据目录的配置文件中；目前不是加密密钥托管，服务器管理员和能读取该目录的人仍可读取这些密钥。

创建 `/etc/systemd/system/tome-agent.service`：

```ini
[Unit]
Description=Tome Agent hosted service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=tome-agent
Group=tome-agent
WorkingDirectory=/opt/tome-agent
EnvironmentFile=/etc/tome-agent.env
Environment=PYTHONPATH=/opt/tome-agent/code/backend:/opt/tome-agent/code/core_engine
ExecStart=/opt/tome-agent/code/backend/.venv/bin/python -m inf_backend.hosted --port 8765
Restart=on-failure
RestartSec=5
UMask=0077
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now tome-agent
sudo systemctl status tome-agent
```

## HTTPS 反向代理

先为域名取得有效证书，再配置 Nginx。以下示例中的域名和证书路径都需要替换；证书续期方式按所用签发服务配置。

```nginx
limit_req_zone $binary_remote_addr zone=tome_auth:10m rate=5r/m;

server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    client_max_body_size 3m;
    access_log off;

    location ~ ^/_account/(login|register)$ {
        limit_req zone=tome_auth burst=5 nodelay;
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8765;
    }
    location / {
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8765;
    }
}
```

检查配置并重载：`sudo nginx -t && sudo systemctl reload nginx`。通过 HTTPS 访问域名，注册两个测试账号，分别创建作品并确认不能互相读取；重启服务后再次登录，确认作品仍在。启动日志位于 `/var/lib/tome-agent/logs/hosted.log`，每位用户的服务日志位于其独立数据目录下。

`TOME_WORKER_LIMIT` 限制同时驻留的用户进程数（1～8，默认 3）；5 分钟未使用且没有正在进行的任务时，空闲进程可被回收。达到上限时，新用户可能需要稍后重试。实际并发能力需要按服务器内存和响应时间实测。当前版本没有自助密码找回，公开注册场景应在上线前补充滥用防护、监控、容量限制和恢复流程。服务器进程重启可能中断正在生成的任务；应检查作品检查点后再续写。

管理员账号需先由本人注册并确认可登录，随后在启动服务时设置 `TOME_ADMIN_USERNAME` 为该用户名。不要指定尚未由本人控制的用户名；指定的账号必须存在且未禁用，否则服务不会启动。管理员在设置中进入账号管理，可以查看用户、启用或禁用用户以及重置密码；操作会保留作品，禁用和重置密码会撤销该用户已有登录。普通用户无法访问管理接口。备份账号数据库及用户数据后再进行部署或升级。
