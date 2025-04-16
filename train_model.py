import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt

# 啟用GPU加速配置 (針對NVIDIA顯卡)
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    try:
        # 啟用混合精度訓練 (需要RTX系列以上顯卡)
        tf.keras.mixed_precision.set_global_policy('mixed_float16')
        # 設定GPU記憶體動態增長
        for device in physical_devices:
            tf.config.experimental.set_memory_growth(device, True)
        print(f"GPU加速已啟用：{physical_devices}")
    except RuntimeError as e:
        print(e)

def create_model(input_shape=(224, 224, 3), num_classes=12):
    """
    創建並優化植物辨識模型（使用遷移學習）
    
    參數:
    - input_shape: 輸入圖像形狀，預設 (224, 224, 3)
    - num_classes: 分類數量
    
    返回:
    - 編譯好的模型
    """
    # 使用預訓練的MobileNetV2（針對移動設備優化）
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet',
        pooling='avg'  # 直接使用全局池化提升效率
    )
    
    # 凍結基礎模型的前75%層數（平衡遷移學習效率）
    freeze_up_to = int(len(base_model.layers) * 0.75)
    for layer in base_model.layers[:freeze_up_to]:
        layer.trainable = False
    
    # 使用更高效的模型結構
    model = models.Sequential([
        base_model,
        layers.Dropout(0.3),  # 增加Dropout防止過擬合
        layers.Dense(256, activation='relu', dtype=tf.float32),  # 最後一層保持float32精度
        layers.Dense(num_classes, activation='softmax', dtype=tf.float32)
    ])
    
    # 使用優化的學習率配置
    optimizer = Adam(learning_rate=1e-4)
    
    # 編譯模型（啟用XLA編譯加速）
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy'],
        experimental_run_tf_function=False  # 兼容性設定
    )
    return model

def load_and_preprocess_data(data_dir, img_size=(224, 224), batch_size=32):
    """
    使用tf.data API高效加載和預處理數據（針對Windows優化）
    
    參數:
    - data_dir: 數據目錄
    - img_size: 圖像尺寸
    - batch_size: 批次大小
    
    返回:
    - 訓練集、驗證集數據管道
    """
    # 創建數據管道
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        label_mode='categorical'
    )

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=img_size,
        batch_size=batch_size,
        label_mode='categorical'
    )

    # 數據增強層（GPU加速）
    augmentation = tf.keras.Sequential([
        layers.experimental.preprocessing.RandomFlip("horizontal"),
        layers.experimental.preprocessing.RandomRotation(0.1),
        layers.experimental.preprocessing.RandomZoom(0.2),
    ])

    # 配置數據管道優化
    def process_data(image, label):
        image = tf.cast(image, tf.float32) / 255.0  # 正規化
        return augmentation(image), label

    # 應用數據管道優化
    train_ds = train_ds.map(
        process_data,
        num_parallel_calls=tf.data.AUTOTUNE
    ).prefetch(tf.data.AUTOTUNE)

    val_ds = val_ds.map(
        lambda x, y: (x / 255.0, y),
        num_parallel_calls=tf.data.AUTOTUNE
    ).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds

def train_model(data_dir, model_save_path, epochs=20, batch_size=32, img_size=(224, 224)):
    """
    高效訓練模型（針對Windows和硬體配置優化）
    
    參數:
    - data_dir: 數據目錄
    - model_save_path: 模型保存路徑
    - epochs: 訓練輪數
    - batch_size: 批次大小（根據顯存調整）
    - img_size: 圖像尺寸
    
    返回:
    - 訓練歷史記錄和模型
    """
    # 創建保存目錄
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)

    # 加載數據
    train_ds, val_ds = load_and_preprocess_data(data_dir, img_size, batch_size)
    class_names = train_ds.class_names
    num_classes = len(class_names)

    # 創建模型
    model = create_model(input_shape=(*img_size, 3), num_classes=num_classes)

    # 配置回調函數
    callbacks = [
        ModelCheckpoint(
            model_save_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6
        )
    ]

    # 啟用XLA編譯加速
    tf.config.optimizer.set_jit(True)

    # 開始訓練
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )

    # 保存模型和類別信息
    model.save(model_save_path)
    with open(os.path.join(os.path.dirname(model_save_path), 'class_names.txt'), 'w') as f:
        f.write('\n'.join(class_names))

    return history, model, class_names

# 以下可視化和評估函數保持不變（根據需要可添加GPU加速選項）
# ... [保持原有plot_training_history和evaluate_model函數不變] ...

if __name__ == "__main__":
    # 配置參數（根據顯存調整批次大小）
    DATA_DIR = "data/plants"        # 數據目錄
    MODEL_SAVE_PATH = "models/plant_model_v2.h5"  # 模型保存路徑
    BATCH_SIZE = 64  # 3060 Ti建議批次大小
    EPOCHS = 30
    IMG_SIZE = (224, 224)

    # 檢查數據路徑
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"數據目錄不存在：{DATA_DIR}")

    # 訓練模型
    history, model, class_names = train_model(
        data_dir=DATA_DIR,
        model_save_path=MODEL_SAVE_PATH,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        img_size=IMG_SIZE
    )

    # 可視化訓練過程
    plot_training_history(history, save_path="models/training_history_v2.png")

    # 評估模型
    evaluate_model(model, DATA_DIR, batch_size=BATCH_SIZE, img_size=IMG_SIZE)

    print("模型訓練和評估完成！")