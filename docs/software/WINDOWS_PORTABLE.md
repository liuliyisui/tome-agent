# Tome Windows 免安装版

适用于 Windows 10/11 64 位。程序包含 Python 运行时，无需安装 Python、Node.js 或前端开发工具。

## 开始使用

1. 将 `TomeAgent-Windows-x64.zip` 完整解压到可读取的文件夹。
2. 双击 `TomeAgent.exe`。保留同目录下的 `_internal` 文件夹。
3. 程序自动启动本地服务，并用系统默认浏览器打开创作页面。
4. 首次运行会提示填写自己的 DeepSeek API Key，保存后即可创建作品。
5. 使用期间保留 Tome 启动窗口；关闭此窗口即停止服务。仅关闭浏览器不会停止服务，可点击启动窗口中的“打开工作室”重新打开。

生成内容和请求官方定价需要联网；阅读本机已保存的作品不需要调用模型。每次生成前仍显示费用预估，确认后才开始生成。

## 数据与升级

配置、作品和日志保存在 `%LOCALAPPDATA%\TomeAgent\`：

- `.env`：本机密钥和配置，请勿分享。
- `data\inf_books\`：作品、记忆和存档。
- `desktop.log` / `runtime.log`：本地运行日志。

启动窗口提供“打开作品与配置目录”按钮。升级时先退出旧程序，再将新版解压到新文件夹；同一 Windows 用户的数据会继续保留。移除程序文件夹不会删除用户目录中的作品。分发包不含开发者 API Key 或作品。

服务仅监听本机 `127.0.0.1`，默认端口 18765；端口被占用时自动选择空闲端口。重复双击同一用户的程序只会重新打开现有服务页面。

## 问题排查

页面无法访问时，确认 Tome 启动窗口仍在运行，再点击“打开工作室”。启动失败可查看数据目录中的日志。

本版本使用浏览器展示 HTML/CSS/JavaScript 前端，作品书架与废案箱使用 Vue 3 响应式组件，Python 负责本机服务；不包含独立嵌入式浏览器内核。Vue 运行时和 MIT 许可证随程序分发，无需联网加载框架。分发程序尚未进行商业代码签名。

## 开发者重新构建

在 Windows x64 下运行 `code\backend\build-windows.cmd`。构建依赖见 `requirements-build.txt`，构建结果位于 `code\backend\data\dist\TomeAgent-Windows-x64.zip`。打包脚本放在已有的 `code/backend/`，说明文档放在已有的 `docs/software/`，构建缓存和分发产物统一放在已有的 `code/backend/data/` 内，不新增仓库顶层目录。生成目录由现有忽略规则排除，不上传运行产物。

打包依据：[PyInstaller 打包说明](https://pyinstaller.org/en/stable/usage.html) 与 [运行时资源路径说明](https://pyinstaller.org/en/stable/runtime-information.html)。
