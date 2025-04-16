// 結果頁面的JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    // 處理置信度條的動畫效果
    const confidenceFill = document.querySelector('.confidence-fill');
    if (confidenceFill) {
        // 獲取置信度值
        const confidenceStyle = confidenceFill.getAttribute('style');
        const confidenceValue = confidenceStyle ? 
            parseFloat(confidenceStyle.split(':')[1]) : 0;
        
        // 先設置為0寬度
        confidenceFill.style.width = '0';
        
        // 使用setTimeout來確保CSS過渡效果能夠正常工作
        setTimeout(() => {
            confidenceFill.style.width = `${confidenceValue}%`;
        }, 300);
    }
    
    // 添加植物詳情的展開/收起功能
    const plantDetailsHeadings = document.querySelectorAll('.plant-details h4');
    if (plantDetailsHeadings.length > 0) {
        plantDetailsHeadings.forEach(heading => {
            heading.addEventListener('click', function() {
                const content = this.nextElementSibling;
                if (content) {
                    // 切換展開/收起狀態
                    if (content.style.maxHeight) {
                        content.style.maxHeight = null;
                        this.classList.remove('expanded');
                    } else {
                        content.style.maxHeight = content.scrollHeight + 'px';
                        this.classList.add('expanded');
                    }
                }
            });
            
            // 添加展開/收起指示器
            heading.innerHTML += '<span class="toggle-indicator">+</span>';
            
            // 默認展開第一個詳情
            if (heading === plantDetailsHeadings[0]) {
                const content = heading.nextElementSibling;
                if (content) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                    heading.classList.add('expanded');
                    heading.querySelector('.toggle-indicator').textContent = '-';
                }
            }
        });
    }
    
    // 添加分享功能
    const shareButton = document.getElementById('shareResult');
    if (shareButton && navigator.share) {
        shareButton.style.display = 'inline-block';
        shareButton.addEventListener('click', async () => {
            try {
                const plantName = document.querySelector('.result-header h3').textContent;
                await navigator.share({
                    title: `植物辨識結果: ${plantName}`,
                    text: `我使用植物辨識系統辨識出了${plantName}！`,
                    url: window.location.href
                });
                console.log('分享成功');
            } catch (err) {
                console.error('分享失敗:', err);
            }
        });
    }
    
    // 添加CSS樣式
    const style = document.createElement('style');
    style.textContent = `
        .plant-details h4 {
            cursor: pointer;
            position: relative;
            padding-right: 30px;
            transition: color 0.3s ease;
        }
        
        .plant-details h4:hover {
            color: var(--primary-color);
        }
        
        .toggle-indicator {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            font-weight: bold;
        }
        
        .plant-details h4.expanded .toggle-indicator {
            content: '-';
        }
        
        .plant-details p {
            overflow: hidden;
            transition: max-height 0.3s ease;
            max-height: 0;
        }
        
        #shareResult {
            display: none;
            background-color: #4267B2;
            color: white;
        }
        
        #shareResult:hover {
            background-color: #365899;
        }
    `;
    document.head.appendChild(style);
});
