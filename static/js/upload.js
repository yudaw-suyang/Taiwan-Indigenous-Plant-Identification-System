// 用於處理上傳圖片的預覽功能
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const previewContainer = document.createElement('div');
    previewContainer.className = 'file-preview-container';
    previewContainer.style.display = 'none';
    
    if (fileInput) {
        // 在檔案輸入後插入預覽容器
        const fileUploadDiv = fileInput.closest('.file-upload');
        if (fileUploadDiv) {
            fileUploadDiv.parentNode.insertBefore(previewContainer, fileUploadDiv.nextSibling);
        }
        
        fileInput.addEventListener('change', function() {
            const fileLabel = document.querySelector('.file-upload label');
            
            if (this.files.length > 0) {
                const file = this.files[0];
                fileLabel.textContent = `已選擇: ${file.name}`;
                fileLabel.style.borderColor = 'var(--primary-color)';
                fileLabel.style.backgroundColor = 'var(--primary-light)';
                
                // 顯示圖片預覽
                if (file.type.match('image.*')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        previewContainer.innerHTML = `
                            <h4>圖片預覽</h4>
                            <div class="image-preview">
                                <img src="${e.target.result}" alt="預覽圖片">
                            </div>
                        `;
                        previewContainer.style.display = 'block';
                    };
                    
                    reader.readAsDataURL(file);
                }
            } else {
                fileLabel.textContent = '選擇照片';
                fileLabel.style.borderColor = 'var(--primary-light)';
                fileLabel.style.backgroundColor = 'var(--background-color)';
                previewContainer.style.display = 'none';
            }
        });
    }
    
    // 添加CSS樣式
    const style = document.createElement('style');
    style.textContent = `
        .file-preview-container {
            margin: 20px 0;
            text-align: center;
        }
        
        .image-preview {
            max-width: 100%;
            margin: 10px auto;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--box-shadow);
        }
        
        .image-preview img {
            max-width: 100%;
            max-height: 300px;
            display: block;
            margin: 0 auto;
        }
    `;
    document.head.appendChild(style);
});
