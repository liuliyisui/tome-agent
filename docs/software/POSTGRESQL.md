# PostgreSQL 本机开发与迁移

## 数据存在哪里

配置 DATABASE_URL 后，作品资料、文风、故事状态、章节正文、章节版本、生成任务和用量记录存入 PostgreSQL。数据库故障会明确报错，不自动切回 JSON 写入。引擎检查点继续保存在 code/backend/data/inf_books，数据库记录其相对位置。备份时需要同时备份数据库与该目录。

没有配置 DATABASE_URL 时保留旧文件模式，供旧版本运行和回滚。新开发环境请按下列步骤使用 PostgreSQL。前端通过 Python API 访问数据库，不向浏览器返回数据库连接串。

## 首次启动

安装 Python 3.11+ 与 Docker Desktop，启动 Docker Desktop。已有本机 PostgreSQL 的成员也可以直接创建专用 tome 数据库并配置其连接串，不需要 Docker。

直接安装 PostgreSQL 17 或 18 时，在 pgAdmin 创建 tome 登录角色（开启 Can login，设置自己的密码），再创建 tome 数据库并将 Owner 设为 tome。数据库服务使用 5432 端口；跳过下方 run-db.cmd，直接初始化表和迁移。不要同时启动占用同一端口的 Docker 数据库。

在仓库根目录运行：

~~~cmd
code\backend\setup.cmd
~~~

编辑 code/backend/.env，保留自己的 DeepSeek 配置，增加：

~~~dotenv
POSTGRES_PASSWORD=replace_with_your_local_password
DATABASE_URL=postgresql://tome:replace_with_your_local_password@127.0.0.1:5432/tome
~~~

两处密码要一致。建议开发密码只使用英文字母、数字、下划线；其他字符需要在连接 URL 中百分号编码。已有 .env 不会被 setup.cmd 覆盖，需要手动补上这两项。不要将 .env 提交 Git。

~~~cmd
code\backend\run-db.cmd
code\backend\migrate-db.cmd init
code\backend\migrate-db.cmd import
~~~

最后一条只预览原有作品和章节数量，不改数据库。确认导入范围后：

~~~cmd
code\backend\migrate-db.cmd import --apply
code\backend\run-web.cmd
~~~

新用户没有旧作品时可以跳过 import，直接启动网页。访问 http://127.0.0.1:8765。

Docker 端口仅绑定 127.0.0.1。数据库保存在命名卷 tome_postgres 中，停止容器不会清空数据。停止数据库可在 code/backend 目录运行 docker compose stop。不要使用 docker compose down -v，除非确实要删除本地数据库。

## 迁移、兼容与回滚

- 导入现有活动作品和废案箱；保留 ID、文风、置顶和正文，重复导入相同内容会跳过。
- 整批导入在一个事务中执行；发现冲突或损坏时回滚，不覆盖数据库中的新作品。
- 导入不移动、不删除原文件。请在网页服务停止时迁移，并先备份原数据目录。
- 废案箱中的旧检查点保留原来的目录位置，恢复作品后也能按原路径定位。
- 旧引擎检查点仍受运行时哈希校验约束，导入数据库不代表能在新版引擎继续写。
- 清空 DATABASE_URL 可以回到文件模式，但数据库启用后新增的作品、文风修改和状态不会自动反向同步为旧格式；迁移后的回滚需要数据库备份，不能以旧文件替代当前数据库。

## 中断恢复

任务记录在数据库中持久化。服务重启可查询之前的结果；尚在 running 的任务不会自动重新调用付费模型。停止网页服务后运行：

~~~cmd
code\backend\migrate-db.cmd recover-jobs --apply
~~~

命令把可取得作品锁的遗留 running 任务标为 interrupted；然后启动网页，重新确认费用后续写。若另一个进程仍持有作品锁，恢复会拒绝该作品。

文件系统和 PostgreSQL 不能组成同一个原子事务。生成时先写不可变检查点及文件索引，再用一个数据库事务提交正文、记忆状态、版本和用量。若数据库写入失败，网页任务报错，旧数据库存档仍然有效。恢复数据库后可显式重建对应作品的数据投影：

~~~cmd
code\backend\migrate-db.cmd reconcile --book-id book-具体ID --apply
~~~

该操作校验引擎检查点与运行时版本，不重新调用模型；先处理检查点，再恢复任务记录。请保留检查点，不手工修改校验哈希。当前支持单机工作区；多台机器同时使用时还需要共享检查点存储及任务调度服务。

## 测试与 GitHub

常规应用测试中设置 DATABASE_URL 为空，避免读取个人 .env。PostgreSQL 集成测试使用 TOME_TEST_DATABASE_URL，逐项创建独立随机 schema，并只删除自己创建的 schema：

~~~powershell
$env:PYTHONPATH="$PWD\code\core_engine;$PWD\code\backend"
$env:DATABASE_URL=""
$env:TOME_TEST_DATABASE_URL="postgresql://tome:你的密码@127.0.0.1:5432/tome"
python -m unittest discover -s tests -v
~~~

CI 已配置 PostgreSQL 服务与独立集成测试任务。本地没有设置测试连接时，数据库专项测试会明确跳过，不能据此宣称数据库集成已通过。

GitHub 只提交源码、schema.sql、compose.yaml、依赖、配置模板和文档；每位成员维护各自 .env 与数据库。模型密钥、真实数据库密码、数据库卷和作品记录不上传。

## 本次本地验证

2026-10-24：在独立 PostgreSQL 17.6 实例上运行完整测试，104 项通过，其中 7 项为真实数据库集成测试。生成接入测试使用模拟写作会话，未调用付费模型；另验证数据库故障不回退文件、章节版本幂等与回滚、旧文件导入不变、作品软删除恢复、任务持久化及跨连接互斥。

随后使用本机正式安装的 PostgreSQL 18.6 和独立 tome 数据库账号，七项隔离 schema 集成测试全部通过。测试只清理自己创建的随机 schema；原作品没有被测试覆盖。CI 配置分别覆盖 PostgreSQL 17 和 18。

本机未安装 Docker，因此 Docker Compose 启动配置及 GitHub Actions 尚未在本机实际执行。临时测试实例不作为正式开发数据库；按首次启动步骤建立各成员自己的数据库。
