# 部署指南 (Deployment Guide)

本指南将帮助你在服务器上完成首次设置，配合 GitHub Actions 实现自动部署。

## 1. 服务器环境准备

登录到你的服务器：
```bash
ssh <USERNAME>@<HOST>
```

### 1.1 安装 Python 和 Git
确保服务器安装了 Python 3.8+ 和 Git。
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-venv git -y
```

### 1.2 克隆代码
将项目克隆到服务器上（建议路径为 `~/unibook`，如果不同请修改 `.github/workflows/deploy.yml` 中的 `PROJECT_DIR`）。
```bash
cd ~
git clone https://github.com/<YOUR_GITHUB_USERNAME>/unibook.git
cd unibook
```

### 1.3 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置 Systemd 服务 (推荐)

使用 Systemd 可以确保应用在后台运行，并能在崩溃或重启后自动启动。

1.  **修改配置文件**：
    打开项目中的 `unibook.service` 文件，根据你的实际路径修改 `User`, `WorkingDirectory` 和 `ExecStart`。

2.  **复制并启用服务**：
    ```bash
    # 复制服务文件到系统目录
    sudo cp unibook.service /etc/systemd/system/

    # 重新加载 daemon
    sudo systemctl daemon-reload

    # 启动服务
    sudo systemctl start unibook

    # 设置开机自启
    sudo systemctl enable 
    ```

3.  **检查状态**：
    ```bash
    sudo systemctl status 
    ```

## 3. GitHub Secrets 配置

在 GitHub 仓库的 **Settings** -> **Secrets and variables** -> **Actions** 中添加以下 Secrets：

| Secret Name | Value |
|-------------|-------|
| `HOST` | 服务器 IP 地址 |
| `USERNAME` | 服务器登录用户名 (如 `root` 或 `ubuntu`) |
| `SSH_PRIVATE_KEY` | 私钥内容 (确保服务器的 `~/.ssh/authorized_keys` 包含对应的公钥) |

## 4. 测试部署

现在，当你推送到 `main` 或 `master` 分支时，GitHub Action 将自动触发：
1.  SSH 连接到服务器。
2.  进入 `~/unibook` 目录。
3.  拉取最新代码。
4.  安装依赖。
5.  重启 `unibook` 服务。
