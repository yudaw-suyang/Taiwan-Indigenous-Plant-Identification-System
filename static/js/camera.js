// 優化的相機功能JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    // 獲取DOM元素
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const switchCameraBtn = document.getElementById('switchCamera');
    const previewContainer = document.querySelector('.preview-container');
    const cameraContainer = document.querySelector('.camera-container');
    const preview = document.getElementById('preview');
    const retakeBtn = document.getElementById('retakeBtn');
    const submitBtn = document.getElementById('submitBtn');
    const imageForm = document.getElementById('imageForm');
    const imageData = document.getElementById('imageData');
    
    // 相機設置
    let stream = null;
    let facingMode = 'environment'; // 預設使用後置相機
    let currentConstraints = null;
    
    // 檢測設備類型
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // 啟動相機
    async function startCamera() {
        try {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            // 根據設備類型設置不同的約束條件
            if (isMobile) {
                currentConstraints = {
                    video: {
                        facingMode: facingMode,
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                };
            } else {
                // 桌面設備可能沒有前後置相機的區分
                currentConstraints = {
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                };
            }
            
            stream = await navigator.mediaDevices.getUserMedia(currentConstraints);
            video.srcObject = stream;
            
            // 顯示相機容器，隱藏預覽容器
            cameraContainer.style.display = 'block';
            previewContainer.style.display = 'none';
            
            // 根據設備類型顯示或隱藏切換相機按鈕
            if (switchCameraBtn) {
                if (isMobile) {
                    switchCameraBtn.style.display = 'block';
                } else {
                    switchCameraBtn.style.display = 'none';
                }
            }
            
            console.log('相機已啟動，使用模式：', facingMode);
        } catch (err) {
            console.error('無法啟動相機：', err);
            
            // 顯示更友好的錯誤訊息
            const errorMessage = document.createElement('div');
            errorMessage.className = 'camera-error';
            errorMessage.innerHTML = `
                <h3>無法啟動相機</h3>
                <p>可能的原因：</p>
                <ul>
                    <li>您尚未授予相機權限</li>
                    <li>您的設備沒有相機</li>
                    <li>相機正被其他應用程式使用</li>
                    <li>瀏覽器不支援相機功能</li>
                </ul>
                <p>請確保您已授予相機權限，並嘗試重新整理頁面或使用其他瀏覽器。</p>
                <p>您也可以選擇上傳照片而不使用相機。</p>
                <a href="/" class="btn">返回首頁</a>
            `;
            
            if (cameraContainer) {
                cameraContainer.innerHTML = '';
                cameraContainer.appendChild(errorMessage);
            }
        }
    }
    
    // 切換相機（前置/後置）
    function switchCamera() {
        if (!isMobile) return; // 只在移動設備上啟用
        
        facingMode = facingMode === 'environment' ? 'user' : 'environment';
        startCamera();
    }
    
    // 拍攝照片
    function capturePhoto() {
        if (!stream) {
            alert('相機尚未啟動');
            return;
        }
        
        // 設置canvas大小與視頻相同
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // 在canvas上繪製當前視頻幀
        const context = canvas.getContext('2d');
        
        // 如果是前置相機，需要水平翻轉
        if (facingMode === 'user') {
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
        }
        
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // 如果是前置相機，恢復變換
        if (facingMode === 'user') {
            context.setTransform(1, 0, 0, 1, 0, 0);
        }
        
        // 獲取圖像數據
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9); // 使用較高的質量
        
        // 顯示預覽
        preview.src = dataUrl;
        
        // 隱藏相機容器，顯示預覽容器
        cameraContainer.style.display = 'none';
        previewContainer.style.display = 'block';
        
        // 將圖像數據存儲到表單中
        imageData.value = dataUrl;
    }
    
    // 重新拍攝
    function retakePhoto() {
        // 隱藏預覽容器，顯示相機容器
        previewContainer.style.display = 'none';
        cameraContainer.style.display = 'block';
    }
    
    // 提交照片進行辨識
    function submitPhoto() {
        if (!imageData.value) {
            alert('請先拍攝照片');
            return;
        }
        
        // 顯示載入指示器
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.innerHTML = `
            <div class="spinner"></div>
            <p>正在辨識植物，請稍候...</p>
        `;
        document.body.appendChild(loadingIndicator);
        
        // 提交表單
        setTimeout(() => {
            imageForm.submit();
        }, 500);
    }
    
    // 處理視頻載入事件
    video.addEventListener('loadedmetadata', function() {
        // 調整視頻容器的寬高比
        const aspectRatio = video.videoHeight / video.videoWidth;
        video.style.aspectRatio = `${video.videoWidth} / ${video.videoHeight}`;
    });
    
    // 事件監聽器
    if (captureBtn) {
        captureBtn.addEventListener('click', capturePhoto);
    }
    
    if (switchCameraBtn) {
        switchCameraBtn.addEventListener('click', switchCamera);
    }
    
    if (retakeBtn) {
        retakeBtn.addEventListener('click', retakePhoto);
    }
    
    if (submitBtn) {
        submitBtn.addEventListener('click', submitPhoto);
    }
    
    // 檢查瀏覽器是否支援相機API
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // 頁面載入時啟動相機
        startCamera();
        
        // 添加方向變化監聽器，以處理設備旋轉
        window.addEventListener('orientationchange', function() {
            // 等待方向變化完成
            setTimeout(() => {
                // 重新啟動相機以適應新的方向
                startCamera();
            }, 200);
        });
    } else {
        // 瀏覽器不支援相機API
        const errorMessage = document.createElement('div');
        errorMessage.className = 'camera-error';
        errorMessage.innerHTML = `
            <h3>您的瀏覽器不支援相機功能</h3>
            <p>請使用現代瀏覽器如Chrome、Firefox、Safari或Edge的最新版本。</p>
            <p>您也可以選擇上傳照片而不使用相機。</p>
            <a href="/" class="btn">返回首頁</a>
        `;
        
        if (cameraContainer) {
            cameraContainer.innerHTML = '';
            cameraContainer.appendChild(errorMessage);
        }
        
        console.error('瀏覽器不支援getUserMedia API');
    }
    
    // 頁面關閉時停止相機
    window.addEventListener('beforeunload', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
    
    // 添加CSS樣式
    const style = document.createElement('style');
    style.textContent = `
        .loading-indicator {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
        }
        
        .spinner {
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 5px solid white;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .camera-error {
            padding: 20px;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }
        
        .camera-error h3 {
            margin-bottom: 15px;
        }
        
        .camera-error ul {
            text-align: left;
            display: inline-block;
            margin: 10px 0;
        }
        
        .camera-error .btn {
            margin-top: 15px;
        }
    `;
    document.head.appendChild(style);
});
