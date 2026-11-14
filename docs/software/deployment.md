# 系统部署

## 本地工作室

Windows 源码启动步骤见 [使用说明](USER_GUIDE.md)；便携版的启动、数据位置和退出方式见 [Windows 便携版](WINDOWS_PORTABLE.md)。本地工作室默认仅供本机访问。

## Linux 多人服务

账号注册、作品隔离及持久数据的部署方式见 [Linux 多用户部署](LINUX_HOSTED.md)。部署前按文档准备服务器、HTTPS 和持久数据目录，并验证备份恢复。单用户历史部署方法见 [旧部署方案](DEPLOY.md)，不能替代多人部署。

涉及 PostgreSQL 的配置和恢复步骤见 [PostgreSQL 使用说明](POSTGRESQL.md)。模型密钥应通过运行环境或应用配置管理，不应提交到仓库。
