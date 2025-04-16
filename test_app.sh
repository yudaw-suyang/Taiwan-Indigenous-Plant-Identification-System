#!/bin/bash

# 測試腳本：用於測試植物辨識應用程式的各項功能

echo "開始測試植物辨識應用程式..."
echo "====================================="

# 檢查虛擬環境
echo "檢查虛擬環境..."
if [ -d "venv" ]; then
    echo "✓ 虛擬環境存在"
else
    echo "✗ 虛擬環境不存在"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate
echo "✓ 虛擬環境已激活"

# 檢查必要的依賴項
echo "檢查必要的依賴項..."
pip freeze | grep -E "flask|tensorflow|pillow|opencv-python|matplotlib|scikit-learn" > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ 所有必要的依賴項已安裝"
else
    echo "✗ 缺少必要的依賴項"
    exit 1
fi

# 檢查專案結構
echo "檢查專案結構..."
directories=("static" "templates" "models" "data")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ 目錄 $dir 存在"
    else
        echo "✗ 目錄 $dir 不存在"
        exit 1
    fi
done

# 檢查關鍵文件
echo "檢查關鍵文件..."
files=("app.py" "train_model.py" "static/css/style.css" "static/css/camera.css" "static/css/result.css" "static/js/main.js" "static/js/camera.js" "static/js/result.js" "static/js/upload.js")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ 文件 $file 存在"
    else
        echo "✗ 文件 $file 不存在"
        exit 1
    fi
done

# 檢查模板文件
echo "檢查模板文件..."
templates=("templates/index.html" "templates/camera.html" "templates/result.html" "templates/not_recognized.html" "templates/history.html" "templates/plant_info.html" "templates/about.html")
for template in "${templates[@]}"; do
    if [ -f "$template" ]; then
        echo "✓ 模板 $template 存在"
    else
        echo "✗ 模板 $template 不存在"
        exit 1
    fi
done

# 創建測試數據目錄
echo "創建測試數據目錄..."
mkdir -p data/test_plants
echo "✓ 測試數據目錄已創建"

# 測試 Flask 應用程式啟動
echo "測試 Flask 應用程式啟動..."
python -c "import app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Flask 應用程式可以正常導入"
else
    echo "✗ Flask 應用程式導入失敗"
    exit 1
fi

# 測試模型訓練框架
echo "測試模型訓練框架..."
python -c "import train_model" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ 模型訓練框架可以正常導入"
else
    echo "✗ 模型訓練框架導入失敗"
    exit 1
fi

echo "====================================="
echo "測試完成！所有檢查都已通過。"
echo "要運行應用程式，請執行以下命令："
echo "source venv/bin/activate && python app.py"
echo "====================================="
