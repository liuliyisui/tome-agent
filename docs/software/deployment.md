# Tome Agent 部署指南

本文介绍 Tome Agent 的本地运行和 Linux 多用户部署，以本项目实际使用的阿里云服务器为例，涵盖部署、验证、更新、备份与常见问题。文档结构参考 [WindOnMAgent 部署案例](https://github.com/bettermorn/AIAgent/blob/main/code/IndustryAgent/WindOnMAgent/deployment.md)，具体配置以本项目代码和服务器设置为准。

## 一、部署架构

```text
浏览器 ──HTTPS 443──> Nginx ──HTTP──> 127.0.0.1:18765
                      │                    │
                HTTP 80 跳转 HTTPS      Tome Agent hosted
                                           │
                              /var/lib/tome-agent
                              账号、用户作品和用户配置
                                           │
                                    外部模型服务 API
```

Nginx 负责证书和请求转发，`tome-agent` 服务运行多人模式。应用端口仅监听服务器本机，用户数据与代码目录分开保存。模型调用依赖用户配置的模型服务和有效 API Key。

| 项目 | 本次部署配置 |
| --- | --- |
| 操作系统 | Alibaba Cloud Linux 3.2104 LTS，64 位 |
| 服务器规格 | 2 核、2 GiB；这是当前机器规格，不代表已验证的并发容量 |
| 运行环境 | Python 3.11、Git、Nginx、systemd |
| 应用地址 | `https://www.tome-story-weaver.cn` |
| 应用监听 | `127.0.0.1:18765` |
| 运行账号 | `tome-agent`，不使用 root 运行应用 |
| 代码 / 数据目录 | `/opt/tome-agent` / `/var/lib/tome-agent` |
| 证书目录 | `/etc/nginx/tome-certs`，私钥不应公开或提交仓库 |
| 本次部署的提交 | `ad4ddaa`；后续升级需重新记录版本 |

多人托管模式的账号库为数据目录下的 `accounts.sqlite3`，用户数据位于各自的数据目录。不要将其与 [旧版单用户部署](DEPLOY.md) 混用；多人服务并不要求必须启用 PostgreSQL。若另外使用 PostgreSQL，参见 [PostgreSQL 使用说明](POSTGRESQL.md)。

## 二、部署前准备

1. 准备 Linux 服务器、Python 3.11、Git、Nginx、`curl` 和可用磁盘空间；示例命令以 root 执行为前提。
2. 将域名解析到服务器，取得覆盖访问域名的有效 HTTPS 证书。中国内地服务器对外提供网站服务应按要求办理备案。
3. 在云服务器安全组和系统防火墙配置入站规则：网站使用 TCP 80、443，SSH 仅允许需要的可信来源；不要把 18765 开放到公网。
4. 明确发布的 Git 提交，确认已完成适用的测试；更新已有服务前备份数据并预留短暂的服务中断时间。
5. 不要把用户作品、模型密钥、证书私钥或服务器环境文件上传到仓库。模型密钥需要在应用内按账号配置，不要写进本文或截图。

## 三、首次安装

以下适用于新服务器；已有目录、账号或服务的服务器应先检查，避免覆盖已有配置。

### 3.1 运行账号、代码与依赖

```bash
useradd --system --home-dir /var/lib/tome-agent --no-create-home --shell /sbin/nologin tome-agent
install -d -o tome-agent -g tome-agent -m 700 /var/lib/tome-agent
git clone https://github.com/liuliyisui/tome-agent.git /opt/tome-agent
chown -R tome-agent:tome-agent /opt/tome-agent
cd /opt/tome-agent
runuser -u tome-agent -- python3.11 -m venv code/backend/.venv
runuser -u tome-agent -- code/backend/.venv/bin/python -m pip install -r code/backend/requirements.txt
```

确认代码版本：`runuser -u tome-agent -- git -C /opt/tome-agent log -1 --oneline`。正式发布应选择已检查的提交或标签，而不是未经验证地跟随最新提交。前端的运行文件已纳入仓库，服务器运行无需安装 Node.js。

### 3.2 systemd 服务

以下为本次服务器的服务配置示例，保存为 `/etc/systemd/system/tome-agent.service`。更换域名或目录时需相应调整；`TOME_PUBLIC_ORIGIN` 要与用户访问的 HTTPS 地址一致。

```ini
[Unit]
Description=Tome Agent hosted service
After=network.target

[Service]
Type=simple
User=tome-agent
Group=tome-agent
WorkingDirectory=/opt/tome-agent
Environment=TOME_PUBLIC_ORIGIN=https://www.tome-story-weaver.cn
Environment=TOME_DATA_HOME=/var/lib/tome-agent
Environment=TOME_WORKER_LIMIT=4
Environment=PYTHONPATH=/opt/tome-agent/code/backend:/opt/tome-agent/code/core_engine
ExecStart=/opt/tome-agent/code/backend/.venv/bin/python -m inf_backend.hosted --port 18765
Restart=on-failure
RestartSec=5
UMask=0077
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

`TOME_WORKER_LIMIT` 限制同时驻留的用户进程数，当前值为 4；实际可支持的并发量需要结合内存和模型响应时间测试。域名也可能通过 `/etc/systemd/system/tome-agent.service.d/domain.conf` 覆盖，排查时应检查完整配置：

```bash
systemctl cat tome-agent
systemctl daemon-reload
systemctl enable --now tome-agent
systemctl status tome-agent --no-pager
```

### 3.3 域名、证书与 Nginx

在 DNS 控制台为实际使用的域名添加指向服务器的解析记录，并为该域名申请证书。当前部署使用的证书文件为：

```text
/etc/nginx/tome-certs/www.tome-story-weaver.cn.pem
/etc/nginx/tome-certs/www.tome-story-weaver.cn.key
```

证书目录和私钥应限制为管理员访问；证书到期前需重新签发、替换并验证。不要把私钥内容放入文档、聊天或仓库。域名证书不能直接证明 IP 地址的身份。

本次部署的 `/etc/nginx/conf.d/tome-agent.conf`：

```nginx
server {
    listen 80;
    server_name www.tome-story-weaver.cn;
    return 301 https://www.tome-story-weaver.cn$request_uri;
}

server {
    listen 443 ssl;
    server_name www.tome-story-weaver.cn;
    ssl_certificate /etc/nginx/tome-certs/www.tome-story-weaver.cn.pem;
    ssl_certificate_key /etc/nginx/tome-certs/www.tome-story-weaver.cn.key;

    location / {
        proxy_pass http://127.0.0.1:18765;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

安装或修改配置后先测试：

```bash
nginx -t
systemctl enable --now nginx
```

修改正在运行的 Nginx 配置时，测试成功后执行 `systemctl reload nginx`。如果服务器上已运行其他网站，应先检查原有配置，避免监听端口或域名冲突。此前用于本机测试的 `127.0.0.1:18443` 是独立测试实例，并非正式服务入口。

## 四、部署验证与检查单

### 4.1 服务与链路

```bash
systemctl is-active tome-agent
systemctl is-active nginx
ss -ltnp | grep -E ':(80|443|18765)\b'
curl -sS -H 'Host: www.tome-story-weaver.cn' http://127.0.0.1:18765/healthz
curl --noproxy '*' --resolve www.tome-story-weaver.cn:443:127.0.0.1 https://www.tome-story-weaver.cn/healthz
```

两个服务预期均为 `active`，健康检查预期返回 `{"status": "ok"}`。第二条 HTTPS 检查从服务器本机连接 Nginx，同时验证域名与证书；它不等于公网访问或完整业务测试。

### 4.2 上线检查

- [ ] 已记录部署的 Git 提交和部署时间，相关测试通过。
- [ ] DNS、证书有效期、备案状态及安全组配置符合当前部署要求。
- [ ] 80、443 可按预期访问；应用端口 18765 未对公网开放。
- [ ] 服务以 `tome-agent` 账号运行，数据目录、证书私钥和模型密钥权限受控。
- [ ] 浏览器通过 HTTPS 打开网站，登录后可打开已有作品；刷新后检查当前作品和章节是否恢复。
- [ ] 使用两个测试账号确认作品相互隔离，并检查一次实际生成或续写流程。
- [ ] 已备份数据并在隔离环境验证恢复；定期检查磁盘空间、证书有效期及服务日志。

本次已观察到：服务为 `active`，本机 HTTPS `/healthz` 返回 `ok`，浏览器可打开网站。上述业务、隔离和恢复检查应分别执行并记录，不以健康检查代替。

## 五、更新与回退

### 5.1 更新已有部署

更新会使运行中的生成任务中断，应先等待任务结束并备份。先确认工作目录和当前版本，再获取远程改动：

```bash
runuser -u tome-agent -- git -C /opt/tome-agent status --short
runuser -u tome-agent -- git -C /opt/tome-agent log -1 --oneline
runuser -u tome-agent -- git -C /opt/tome-agent fetch origin main
```

确认没有需要保留的未提交修改，检查发布提交及依赖变化，再将 `<已验证提交>` 替换为实际提交：

```bash
runuser -u tome-agent -- git -C /opt/tome-agent merge --ff-only <已验证提交>
```

若依赖文件发生变化，按新版本要求更新虚拟环境依赖，再重启服务：

```bash
systemctl restart tome-agent
systemctl is-active tome-agent
curl --noproxy '*' --resolve www.tome-story-weaver.cn:443:127.0.0.1 https://www.tome-story-weaver.cn/healthz
```

最后在浏览器验证登录、已有作品与本次更新涉及的功能。`--ff-only` 失败时应检查分支关系及工作区，避免强制覆盖。代码更新不应删除或重置 `/var/lib/tome-agent`。

### 5.2 备份与恢复

`/var/lib/tome-agent` 包含账号数据库、作品和用户配置，可能包含模型密钥。备份前应停止应用并确认没有仍在运行的用户进程或写入任务，避免数据库与作品文件处于不一致状态；按维护窗口操作，完成后重新启动服务。将完整数据目录复制到受限、加密的独立存储，定期在隔离环境验证恢复；不要把备份包提交到 Git。

回退前记录当前版本和故障日志，确认目标版本与现有数据格式兼容；如需恢复数据，先保留故障现场的完整副本，在隔离环境验证备份，再按维护流程切换。不能假设旧代码一定可以读取新版本写入的数据。

## 六、常见问题

| 现象 | 检查方向 |
| --- | --- |
| 网站打不开 | 查看域名解析、备案状态、云安全组、系统防火墙及 Nginx 状态。 |
| 502 Bad Gateway | 检查 `systemctl status tome-agent`、18765 监听和应用日志。 |
| 证书不可信或域名不匹配 | 确认证书有效期、证书链、访问域名与证书名称；不要使用 IP 代替域名验证证书。 |
| 页面打开但登录或操作失败 | 检查 `TOME_PUBLIC_ORIGIN`、Nginx 转发的 `Host` 和服务日志。 |
| 部署后界面仍是旧版 | 确认服务器 Git 提交，浏览器按 Ctrl+F5 强制刷新后再检查。 |
| `dubious ownership` | 使用仓库所属的 `tome-agent` 用户执行 Git，例如 `runuser -u tome-agent -- git -C /opt/tome-agent status --short`。 |
| 内部健康检查成功但公网失败 | 内部测试不经过公网入口；继续检查 DNS、安全组、系统防火墙及接入规则。 |

常用诊断命令：

```bash
systemctl status tome-agent nginx --no-pager
journalctl -u tome-agent -n 100 --no-pager
tail -n 100 /var/lib/tome-agent/logs/hosted.log
nginx -t
```

## 七、本地运行与相关资料

- 本地工作室：见 [使用说明](USER_GUIDE.md)；Windows 便携版见 [WINDOWS_PORTABLE.md](WINDOWS_PORTABLE.md)。
- Linux 多用户的完整配置、管理员账号与隔离说明：见 [LINUX_HOSTED.md](LINUX_HOSTED.md)。
- 单用户历史部署：见 [DEPLOY.md](DEPLOY.md)，不要直接作为多人部署方案。
- 参考案例：[WindOnMAgent Linux 云服务器部署指南](https://github.com/bettermorn/AIAgent/blob/main/code/IndustryAgent/WindOnMAgent/deployment.md)。
