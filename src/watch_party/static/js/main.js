// 主页功能
document.addEventListener('DOMContentLoaded', function () {
    // 移动端导航菜单切换
    const navToggle = document.getElementById('mobile-menu');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 加载房间列表（如果页面包含房间列表容器）
    loadRooms();
});

// 加载房间列表
async function loadRooms() {
    const roomsList = document.getElementById('rooms-list');
    if (!roomsList) return;

    try {
        // 这里可以调用API获取房间列表
        // 目前显示静态内容
        roomsList.innerHTML = `
            <div class="room-card">
                <div class="room-header">
                    <h3>视频观看房间</h3>
                    <span class="room-status online">在线</span>
                </div>
                <div class="room-info">
                    <p>在这里与朋友一起观看视频，支持实时同步播放</p>
                    <div class="room-actions">
                        <a href="/room" class="btn btn-primary">
                            <i class="fas fa-play"></i>
                            进入房间
                        </a>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('加载房间列表失败:', error);
        roomsList.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>暂时无法加载房间列表</p>
            </div>
        `;
    }
}

// 添加房间卡片样式（如果CSS中没有的话）
if (!document.querySelector('style[data-main-js]')) {
    const style = document.createElement('style');
    style.setAttribute('data-main-js', 'true');
    style.textContent = `
        .room-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }

        .room-card:hover {
            transform: translateY(-2px);
        }

        .room-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .room-header h3 {
            margin: 0;
            color: #333;
        }

        .room-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .room-status.online {
            background: #d4edda;
            color: #155724;
        }

        .room-info p {
            color: #666;
            margin-bottom: 15px;
        }

        .room-actions {
            text-align: right;
        }

        .error-message {
            text-align: center;
            color: #666;
            padding: 40px;
        }

        .error-message i {
            font-size: 2rem;
            margin-bottom: 10px;
            color: #ccc;
        }
    `;
    document.head.appendChild(style);
} 