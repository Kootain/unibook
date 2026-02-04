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
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置 Systemd 服务

使用 Systemd 可以确保应用在后台运行，并能在崩溃或重启后自动启动。

1.  **修改配置文件**：
    打开项目中的 `unibook.service` 文件，根据你的实际路径修改 `User`, `WorkingDirectory` 和 `ExecStart`。
    *注意：如果你使用 HTTPS 反向代理，建议将 `ExecStart` 中的 `--host` 设置为 `127.0.0.1`。*

2.  **复制并启用服务**：
    ```bash
    # 复制服务文件到系统目录
    sudo cp unibook.service /etc/systemd/system/

    # 重新加载 daemon
    sudo systemctl daemon-reload

    # 启动服务
    sudo systemctl start unibook

    # 设置开机自启
    sudo systemctl enable unibook
    ```

## 3. 启用 HTTPS (推荐使用 Caddy)

Caddy 是一个自动管理 HTTPS 证书的 Web 服务器，配置极其简单。

### 3.1 安装 Caddy
(以 Ubuntu 为例，其他系统请参考 [Caddy 官方文档](https://caddyserver.com/docs/install))

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### 3.2 配置 Caddy
1.  打开 Caddy 配置文件：
    ```bash
    sudo nano /etc/caddy/Caddyfile
    ```
2.  将内容替换为以下内容：

    **方式 A: 使用域名 (自动 HTTPS)**
    ```
    your-domain.com {
        reverse_proxy 127.0.0.1:8000
    }
    ```

    **方式 B: 使用 IP 直接访问 (HTTP)**
    如果你的服务器没有域名，只想通过 IP 访问（例如 `http://1.2.3.4`）：
    ```
    :80 {
        reverse_proxy 127.0.0.1:8000
    }
    ```

3.  重启 Caddy：
    ```bash
    sudo systemctl restart caddy
    ```
    
🎉 现在，你的 API 就可以通过 `https://your-domain.com` 或者 `http://<YOUR_IP>` 访问了！
(注意：如果是 IP 访问模式，默认为 HTTP 协议)

---

## 4. GitHub Secrets 配置

在 GitHub 仓库的 **Settings** -> **Secrets and variables** -> **Actions** 中添加以下 Secrets：

| Secret Name | Value |
|-------------|-------|
| `HOST` | 服务器 IP 地址 |
| `USERNAME` | 服务器登录用户名 (如 `root` 或 `ubuntu`) |
| `SSH_PRIVATE_KEY` | 私钥内容 (确保服务器的 `~/.ssh/authorized_keys` 包含对应的公钥) |
