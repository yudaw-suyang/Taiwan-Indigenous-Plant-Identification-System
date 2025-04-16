# 植物辨識應用程式部署指南

本文檔提供了將植物辨識應用程式部署到不同環境的詳細指南。

## 目錄
1. [本地部署](#本地部署)
2. [Docker 部署](#docker-部署)
3. [雲端部署](#雲端部署)
4. [多用戶設置](#多用戶設置)
5. [安全性考量](#安全性考量)

## 本地部署

### 基本部署（開發環境）

這是最簡單的部署方式，適合個人使用或開發測試：

1. 確保已完成 README.md 中的安裝步驟
2. 運行應用程式：

```bash
./run_app.sh
```

應用程式將在 http://localhost:5000 運行，僅能從本機訪問。

### 區域網路部署

如果您希望在區域網路中的其他設備（如手機、平板）上訪問應用程式：

1. 修改 `app.py` 中的 host 參數：

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

2. 找出您電腦的區域網路 IP 地址：

```bash
# macOS 或 Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

3. 運行應用程式：

```bash
./run_app.sh
```

4. 在區域網路中的其他設備上，使用瀏覽器訪問 `http://您的IP地址:5000`

### 使用 Gunicorn 部署（生產環境）

對於更穩定的生產環境部署，建議使用 Gunicorn：

1. 安裝 Gunicorn：

```bash
pip install gunicorn
```

2. 創建 `wsgi.py` 文件：

```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. 使用 Gunicorn 運行應用程式：

```bash
gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
```

4. 設置開機自啟動（可選）：

對於 macOS，創建一個 LaunchAgent：

```bash
mkdir -p ~/Library/LaunchAgents
```

創建文件 `~/Library/LaunchAgents/com.user.plant-recognition.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.plant-recognition</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/plant_recognition/venv/bin/gunicorn</string>
        <string>--workers=4</string>
        <string>--bind=0.0.0.0:5000</string>
        <string>wsgi:app</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/plant_recognition</string>
    <key>StandardOutPath</key>
    <string>/path/to/plant_recognition/logs/gunicorn.out.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/plant_recognition/logs/gunicorn.err.log</string>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

載入 LaunchAgent：

```bash
launchctl load ~/Library/LaunchAgents/com.user.plant-recognition.plist
```

## Docker 部署

使用 Docker 可以簡化部署過程並確保環境一致性：

1. 創建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "wsgi:app"]
```

2. 創建 `requirements.txt`：

```
flask==3.1.0
tensorflow==2.19.0
pillow==11.1.0
opencv-python==4.11.0.86
matplotlib==3.10.1
scikit-learn==1.6.1
gunicorn==21.2.0
```

3. 構建 Docker 映像：

```bash
docker build -t plant-recognition .
```

4. 運行 Docker 容器：

```bash
docker run -d -p 5000:5000 -v $(pwd)/models:/app/models -v $(pwd)/data:/app/data plant-recognition
```

這將使應用程式在 http://localhost:5000 運行，並將模型和數據目錄掛載到容器中，以便保留數據。

## 雲端部署

### 部署到 Heroku

1. 安裝 Heroku CLI 並登入：

```bash
brew install heroku/brew/heroku
heroku login
```

2. 創建 `Procfile`：

```
web: gunicorn wsgi:app
```

3. 創建 `runtime.txt`：

```
python-3.10.12
```

4. 初始化 Git 儲存庫（如果尚未初始化）：

```bash
git init
git add .
git commit -m "Initial commit"
```

5. 創建 Heroku 應用程式並部署：

```bash
heroku create plant-recognition-app
git push heroku main
```

6. 打開應用程式：

```bash
heroku open
```

### 部署到 AWS EC2

1. 啟動 EC2 實例（建議 t2.medium 或更高配置）
2. 安裝必要的軟體：

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
```

3. 克隆儲存庫：

```bash
git clone <儲存庫網址> plant_recognition
cd plant_recognition
```

4. 設置虛擬環境並安裝依賴項：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. 設置 Systemd 服務以確保應用程式持續運行：

```bash
sudo nano /etc/systemd/system/plant-recognition.service
```

添加以下內容：

```
[Unit]
Description=Plant Recognition Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/plant_recognition
ExecStart=/home/ubuntu/plant_recognition/venv/bin/gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

6. 啟動服務：

```bash
sudo systemctl start plant-recognition
sudo systemctl enable plant-recognition
```

7. 設置防火牆（如果需要）：

```bash
sudo ufw allow 5000
```

## 多用戶設置

對於支援多用戶同時使用的環境，建議進行以下優化：

1. 增加 Gunicorn 工作進程數：

```bash
gunicorn --workers=8 --threads=2 --bind=0.0.0.0:5000 wsgi:app
```

2. 添加 Redis 用於會話管理：

```bash
pip install redis flask-session
```

修改 `app.py`：

```python
from flask_session import Session
from redis import Redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)
Session(app)
```

3. 考慮使用負載均衡器（如 Nginx）：

安裝 Nginx：

```bash
sudo apt install nginx
```

配置 Nginx：

```
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 安全性考量

1. 在生產環境中禁用調試模式：

```python
app.run(debug=False)
```

2. 設置安全的密鑰：

```python
import os
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
```

3. 添加 HTTPS 支援（使用 Let's Encrypt）：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

4. 限制上傳文件大小和類型：

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
```

5. 實施基本的速率限制：

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

如有任何部署相關問題，請參考各平台的官方文檔或聯繫開發者獲取支援。
