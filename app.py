import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import numpy as np
import cv2
from datetime import datetime
import tensorflow as tf
from PIL import Image
import io
import base64
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['HISTORY_FOLDER'] = 'static/history'
app.config['MODEL_PATH'] = 'models/plant_model.h5'

# 確保上傳和歷史記錄目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['HISTORY_FOLDER'], exist_ok=True)

# 植物類別名稱 (需要根據您的12種植物進行修改)
PLANT_CLASSES = [
    "九芎Lagerstroemia subcostata", "山棕Arenga engleri", "山葛Pueraria montana", "冇骨消Sambucus chinensis", 
    "包籜箭竹Pseudosasa usawae", "姑婆芋Alocasia odora", "姑婆芋Alocasia odora", "桂竹Phyllostachys reticulata", 
    "黃藤Calamus jenkinsianus", "臺灣烏心石Michelia compressa", "臺灣櫸Zelkova serrata", "羅氏鹽膚木Rhus chinensis var roxburghii"
]

# 植物資訊 (需要根據您的12種植物進行修改)
PLANT_INFO = {
    "九芎Lagerstroemia subcostata": {"description": "這是植物1的詳細描述...", "care_tips": "照顧提示..."},
    "山棕Arenga engleri": {"description": "這是植物2的詳細描述...", "care_tips": "照顧提示..."},
    "山葛Pueraria montana": {"description": "這是植物3的詳細描述...", "care_tips": "照顧提示..."},
    "冇骨消Sambucus chinensis": {"description": "這是植物4的詳細描述...", "care_tips": "照顧提示..."},
    "包籜箭竹Pseudosasa usawae": {"description": "這是植物5的詳細描述...", "care_tips": "照顧提示..."},
    "姑婆芋Alocasia odora": {"description": "這是植物6的詳細描述...", "care_tips": "照顧提示..."},
    "姑婆芋Alocasia odora": {"description": "這是植物7的詳細描述...", "care_tips": "照顧提示..."},
    "桂竹Phyllostachys reticulata": {"description": "這是植物8的詳細描述...", "care_tips": "照顧提示..."},
    "黃藤Calamus jenkinsianus": {"description": "這是植物9的詳細描述...", "care_tips": "照顧提示..."},
    "臺灣烏心石Michelia compressa": {"description": "這是植物10的詳細描述...", "care_tips": "照顧提示..."},
    "臺灣櫸Zelkova serrata": {"description": "這是植物11的詳細描述...", "care_tips": "照顧提示..."},
    "羅氏鹽膚木Rhus chinensis var roxburghii": {"description": "這是植物12的詳細描述...", "care_tips": "照顧提示..."},
}

# 全局變數用於存儲模型
model = None

def load_model():
    """載入訓練好的模型"""
    global model
    if model is None and os.path.exists(app.config['MODEL_PATH']):
        model = tf.keras.models.load_model(app.config['MODEL_PATH'])
        print("模型已成功載入")
    return model

def preprocess_image(image, target_size=(224, 224)):
    """預處理圖像以適應模型輸入"""
    if isinstance(image, str):  # 如果是文件路徑
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:  # 如果是圖像數據
        img = image
        
    img = cv2.resize(img, target_size)
    img = img / 255.0  # 正規化
    return np.expand_dims(img, axis=0)  # 添加批次維度

def predict_plant(image_data):
    """使用模型預測植物類別"""
    model = load_model()
    
    if model is None:
        return None, None, "模型尚未載入"
    
    try:
        # 預處理圖像
        processed_image = preprocess_image(image_data)
        
        # 進行預測
        predictions = model.predict(processed_image)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        
        # 如果置信度太低，視為無法辨識
        if confidence < 0.5:  # 可以調整這個閾值
            return None, confidence, "無法辨識的植物"
        
        predicted_class = PLANT_CLASSES[predicted_class_index]
        return predicted_class, confidence, None
    except Exception as e:
        return None, None, str(e)

def save_history(image_data, predicted_class, confidence):
    """保存辨識歷史記錄"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}.jpg"
    filepath = os.path.join(app.config['HISTORY_FOLDER'], filename)
    
    # 保存圖像
    if isinstance(image_data, str) and image_data.startswith('data:image'):
        # 處理 base64 圖像數據
        image_data = image_data.split(',')[1]
        image_data = base64.b64decode(image_data)
        with open(filepath, 'wb') as f:
            f.write(image_data)
    elif isinstance(image_data, np.ndarray):
        # 處理 numpy 數組
        cv2.imwrite(filepath, cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR))
    else:
        # 處理文件路徑
        if os.path.exists(image_data):
            import shutil
            shutil.copy(image_data, filepath)
    
    # 返回歷史記錄信息
    return {
        'id': unique_id,
        'timestamp': timestamp,
        'filename': filename,
        'filepath': filepath,
        'predicted_class': predicted_class,
        'confidence': confidence
    }

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/camera')
def camera():
    """相機頁面"""
    return render_template('camera.html')

@app.route('/upload', methods=['POST'])
def upload():
    """處理上傳的圖像"""
    if 'file' not in request.files and 'image_data' not in request.form:
        return redirect(request.url)
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        # 保存上傳的文件
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 預測植物類別
        predicted_class, confidence, error = predict_plant(filepath)
        
        # 保存歷史記錄
        if predicted_class:
            history = save_history(filepath, predicted_class, confidence)
            session['last_prediction'] = {
                'class': predicted_class,
                'confidence': confidence,
                'image': url_for('static', filename=f'uploads/{filename}'),
                'history_id': history['id']
            }
            return redirect(url_for('result'))
        else:
            session['error'] = error
            return redirect(url_for('not_recognized'))
    
    elif 'image_data' in request.form:
        image_data = request.form['image_data']
        
        # 解碼 base64 圖像
        image_data_decoded = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data_decoded))
        image_array = np.array(image)
        
        # 預測植物類別
        predicted_class, confidence, error = predict_plant(image_array)
        
        # 保存歷史記錄
        if predicted_class:
            history = save_history(image_data, predicted_class, confidence)
            session['last_prediction'] = {
                'class': predicted_class,
                'confidence': confidence,
                'image': url_for('static', filename=f'history/{history["filename"]}'),
                'history_id': history['id']
            }
            return redirect(url_for('result'))
        else:
            session['error'] = error
            return redirect(url_for('not_recognized'))

@app.route('/result')
def result():
    """顯示辨識結果"""
    if 'last_prediction' not in session:
        return redirect(url_for('index'))
    
    prediction = session['last_prediction']
    plant_class = prediction['class']
    plant_info = PLANT_INFO.get(plant_class, {})
    
    return render_template('result.html', 
                          prediction=prediction,
                          plant_info=plant_info)

@app.route('/not_recognized')
def not_recognized():
    """顯示無法辨識頁面"""
    error = session.get('error', '無法辨識的植物')
    return render_template('not_recognized.html', error=error)

@app.route('/history')
def history():
    """顯示歷史記錄頁面"""
    history_files = os.listdir(app.config['HISTORY_FOLDER'])
    history_files.sort(reverse=True)  # 最新的排在前面
    
    history_records = []
    for filename in history_files:
        if filename.endswith('.jpg'):
            parts = filename.split('_')
            if len(parts) >= 2:
                date_str = parts[0]
                time_str = parts[1].split('.')[0]
                timestamp = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
                
                # 這裡我們沒有存儲預測結果，所以顯示為未知
                # 在實際應用中，您可能需要將預測結果存儲在數據庫或文件中
                history_records.append({
                    'timestamp': timestamp,
                    'image': url_for('static', filename=f'history/{filename}'),
                    'filename': filename
                })
    
    return render_template('history.html', history=history_records)

@app.route('/plant_info')
def plant_info():
    """顯示植物資訊頁面"""
    return render_template('plant_info.html', plants=PLANT_CLASSES, plant_info=PLANT_INFO)

@app.route('/about')
def about():
    """關於頁面"""
    return render_template('about.html')

if __name__ == '__main__':
    # 確保模型已載入
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)
