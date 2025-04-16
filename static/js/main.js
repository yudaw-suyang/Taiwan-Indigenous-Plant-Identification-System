// main.js - 一般功能的JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    // 檢查頁面載入完成後的初始化操作
    console.log('植物辨識系統已載入');
    
    // 檔案上傳預覽功能
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileLabel = document.querySelector('.file-upload label');
            if (this.files.length > 0) {
                fileLabel.textContent = `已選擇: ${this.files[0].name}`;
                fileLabel.style.borderColor = 'var(--primary-color)';
                fileLabel.style.backgroundColor = 'var(--primary-light)';
            } else {
                fileLabel.textContent = '選擇照片';
                fileLabel.style.borderColor = 'var(--primary-light)';
                fileLabel.style.backgroundColor = 'var(--background-color)';
            }
        });
    }
    
    // 植物資訊頁面的搜尋功能
    const plantSearch = document.getElementById('plantSearch');
    if (plantSearch) {
        const plantCards = document.querySelectorAll('.plant-info-card');
        
        plantSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            plantCards.forEach(card => {
                const plantName = card.querySelector('h3').textContent.toLowerCase();
                if (plantName.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // 結果頁面的置信度條動畫
    const confidenceFill = document.querySelector('.confidence-fill');
    if (confidenceFill) {
        // 使用動畫效果顯示置信度條
        setTimeout(() => {
            confidenceFill.style.transition = 'width 1s ease-in-out';
            confidenceFill.style.width = confidenceFill.getAttribute('style').split(':')[1];
        }, 100);
    }
    
    // 歷史記錄頁面的卡片點擊效果
    const historyCards = document.querySelectorAll('.history-card');
    if (historyCards.length > 0) {
        historyCards.forEach(card => {
            card.addEventListener('click', function() {
                // 可以在這裡添加點擊歷史記錄卡片的功能，例如顯示詳細資訊
                console.log('點擊了歷史記錄卡片');
            });
        });
    }
    
    // 響應式導航欄
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('nav ul');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }
});
