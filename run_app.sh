#!/bin/bash

# 啟動腳本：用於啟動植物辨識應用程式

echo "啟動植物辨識應用程式..."
echo "====================================="

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "錯誤：虛擬環境不存在，請先設置虛擬環境"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate
echo "✓ 虛擬環境已激活"

# 檢查是否有模型文件
if [ ! -f "models/plant_model.h5" ]; then
    echo "注意：模型文件不存在，請先訓練模型或將訓練好的模型放入models目錄"
    mkdir -p models
fi

# 創建必要的目錄
mkdir -p static/uploads
mkdir -p static/history

# 啟動應用程式
echo "啟動 Flask 應用程式..."
echo "應用程式將在 http://localhost:5000 運行"
echo "按 Ctrl+C 停止應用程式"
echo "====================================="

# 啟動 Flask 應用程式
python app.py
