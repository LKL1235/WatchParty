// 主应用JavaScript文件

// 全局变量
const App = {
    apiUrl: '/api',

    // 初始化函数
    init: function () {
        console.log('Flask应用已加载');
        this.setupEventListeners();
        this.showWelcomeMessage();
    },

    // 设置事件监听器
    setupEventListeners: function () {
        // 页面加载完成后的处理
        document.addEventListener('DOMContentLoaded', function () {
            // 添加平滑滚动效果
            App.setupSmoothScrolling();

            // 设置工具提示
            App.setupTooltips();
        });

        // 窗口调整大小时的处理
        window.addEventListener('resize', function () {
            App.handleResize();
        });
    },

    // 显示欢迎消息
    showWelcomeMessage: function () {
        console.log('欢迎使用 Video Together Flask 应用！');

        // 检查是否是首次访问
        if (!localStorage.getItem('visited')) {
            setTimeout(() => {
                this.showNotification('欢迎使用Flask应用！', 'success');
                localStorage.setItem('visited', 'true');
            }, 1000);
        }
    },

    // 设置平滑滚动
    setupSmoothScrolling: function () {
        const links = document.querySelectorAll('a[href^="#"]');
        links.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },

    // 设置工具提示
    setupTooltips: function () {
        // 如果页面上有Bootstrap的工具提示，初始化它们
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    // 处理窗口大小调整
    handleResize: function () {
        // 可以在这里添加响应式处理逻辑
        const width = window.innerWidth;
        if (width < 768) {
            // 移动端处理
            console.log('切换到移动端视图');
        } else {
            // 桌面端处理
            console.log('切换到桌面端视图');
        }
    },

    // 显示通知
    showNotification: function (message, type = 'info', duration = 3000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';

        alertDiv.innerHTML = `
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // 自动移除通知
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, duration);
    },

    // API调用辅助函数
    api: {
        // GET请求
        get: async function (endpoint) {
            try {
                const response = await fetch(`${App.apiUrl}${endpoint}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API GET错误:', error);
                App.showNotification('API请求失败', 'danger');
                throw error;
            }
        },

        // POST请求
        post: async function (endpoint, data) {
            try {
                const response = await fetch(`${App.apiUrl}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API POST错误:', error);
                App.showNotification('API请求失败', 'danger');
                throw error;
            }
        }
    },

    // 工具函数
    utils: {
        // 格式化日期
        formatDate: function (date) {
            return new Date(date).toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        // 防抖函数
        debounce: function (func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // 节流函数
        throttle: function (func, limit) {
            let inThrottle;
            return function () {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // 验证邮箱
        validateEmail: function (email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },

        // 生成随机ID
        generateId: function () {
            return Math.random().toString(36).substr(2, 9);
        }
    }
};

// 页面特定功能
const PageFunctions = {
    // 首页功能
    index: {
        // 测试API（全局函数，供HTML调用）
        testApi: async function () {
            try {
                // 显示加载状态
                const button = event.target;
                const originalText = button.textContent;
                button.innerHTML = '<span class="loading"></span> 测试中...';
                button.disabled = true;

                const data = await App.api.get('/hello');

                document.getElementById('api-response').textContent = JSON.stringify(data, null, 2);
                document.getElementById('api-result').style.display = 'block';

                // 滚动到结果区域
                document.getElementById('api-result').scrollIntoView({ behavior: 'smooth' });

                App.showNotification('API测试成功！', 'success');

            } catch (error) {
                document.getElementById('api-response').textContent = '错误: ' + error.message;
                document.getElementById('api-result').style.display = 'block';
                App.showNotification('API测试失败', 'danger');
            } finally {
                // 恢复按钮状态
                const button = event.target;
                button.textContent = '测试 API';
                button.disabled = false;
            }
        }
    },

    // 用户页面功能
    user: {
        // 加载用户数据（全局函数，供HTML调用）
        loadUserData: function () {
            const username = document.querySelector('[data-username]')?.dataset.username ||
                document.title.match(/用户: (.*?) -/)?.[1] || 'Unknown';

            // 模拟API调用
            const userData = {
                username: username,
                email: `${username}@example.com`,
                joinDate: App.utils.formatDate(new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000)),
                lastLogin: App.utils.formatDate(new Date()),
                status: "活跃用户",
                posts: Math.floor(Math.random() * 100),
                followers: Math.floor(Math.random() * 1000)
            };

            const dataHtml = `
                <table class="table table-striped">
                    <tr><th>用户名</th><td>${userData.username}</td></tr>
                    <tr><th>邮箱</th><td>${userData.email}</td></tr>
                    <tr><th>加入日期</th><td>${userData.joinDate}</td></tr>
                    <tr><th>最后登录</th><td>${userData.lastLogin}</td></tr>
                    <tr><th>发帖数量</th><td>${userData.posts}</td></tr>
                    <tr><th>关注者</th><td>${userData.followers}</td></tr>
                    <tr><th>状态</th><td><span class="badge bg-success">${userData.status}</span></td></tr>
                </table>
            `;

            document.getElementById('data-content').innerHTML = dataHtml;
            document.getElementById('user-data').style.display = 'block';

            // 滚动到数据区域
            document.getElementById('user-data').scrollIntoView({ behavior: 'smooth' });

            App.showNotification('用户数据加载完成', 'success');
        }
    }
};

// 全局函数（供HTML调用）
function testApi() {
    PageFunctions.index.testApi();
}

function loadUserData() {
    PageFunctions.user.loadUserData();
}

// 初始化应用
App.init();

// 导出App对象（如果需要在其他地方使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
} 