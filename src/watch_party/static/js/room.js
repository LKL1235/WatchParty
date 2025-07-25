// 房间页面主要功能
class VideoRoom {
    constructor() {
        this.video = document.getElementById('videoElement');
        this.currentPlaylist = [];
        this.currentVideoIndex = -1;
        this.currentSubtitles = null;
        this.subtitleSettings = {
            size: 18,
            color: '#ffffff',
            opacity: 100,
            background: 50
        };

        this.init();
    }

    init() {
        this.initVideoControls();
        this.initPlaylist();
        this.initModals();
        this.loadVideoList();
        this.bindEvents();
    }

    // 初始化视频控制
    initVideoControls() {
        const playPauseBtn = document.getElementById('playPauseBtn');
        const volumeBtn = document.getElementById('volumeBtn');
        const volumeSlider = document.getElementById('volumeSlider');
        const progressBar = document.querySelector('.progress-bar');
        const progressFilled = document.getElementById('progressFilled');
        const progressHandle = document.getElementById('progressHandle');
        const currentTimeEl = document.getElementById('currentTime');
        const durationEl = document.getElementById('duration');
        const settingsBtn = document.getElementById('settingsBtn');
        const fullscreenBtn = document.getElementById('fullscreenBtn');

        // 播放/暂停
        playPauseBtn.addEventListener('click', () => {
            if (this.video.paused) {
                this.video.play();
                playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                this.video.pause();
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        });

        // 音量控制
        volumeBtn.addEventListener('click', () => {
            if (this.video.muted) {
                this.video.muted = false;
                volumeBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                volumeSlider.value = this.video.volume * 100;
            } else {
                this.video.muted = true;
                volumeBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            }
        });

        volumeSlider.addEventListener('input', (e) => {
            const volume = e.target.value / 100;
            this.video.volume = volume;
            this.video.muted = volume === 0;

            if (volume === 0) {
                volumeBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            } else if (volume < 0.5) {
                volumeBtn.innerHTML = '<i class="fas fa-volume-down"></i>';
            } else {
                volumeBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            }
        });

        // 进度条控制
        let isDragging = false;

        const updateProgress = () => {
            if (this.video.duration) {
                const progress = (this.video.currentTime / this.video.duration) * 100;
                progressFilled.style.width = progress + '%';
                progressHandle.style.left = progress + '%';
            }
        };

        progressBar.addEventListener('click', (e) => {
            if (!isDragging) {
                const rect = progressBar.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const width = rect.width;
                const newTime = (clickX / width) * this.video.duration;
                this.video.currentTime = newTime;
            }
        });

        progressHandle.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const rect = progressBar.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const width = rect.width;
                const progress = Math.max(0, Math.min(100, (x / width) * 100));
                const newTime = (progress / 100) * this.video.duration;
                this.video.currentTime = newTime;
                progressFilled.style.width = progress + '%';
                progressHandle.style.left = progress + '%';
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // 时间更新
        this.video.addEventListener('timeupdate', () => {
            if (!isDragging) {
                updateProgress();
            }
            currentTimeEl.textContent = this.formatTime(this.video.currentTime);
            this.updateSubtitles();
        });

        this.video.addEventListener('loadedmetadata', () => {
            durationEl.textContent = this.formatTime(this.video.duration);
        });

        // 设置按钮
        settingsBtn.addEventListener('click', () => {
            this.showSubtitleSettings();
        });

        // 全屏按钮
        fullscreenBtn.addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // 视频结束后播放下一个
        this.video.addEventListener('ended', () => {
            this.playNext();
        });
    }

    // 初始化播放列表
    initPlaylist() {
        const addVideoBtn = document.getElementById('addVideoBtn');
        addVideoBtn.addEventListener('click', () => {
            this.showAddVideoModal();
        });
    }

    // 初始化模态窗口
    initModals() {
        // 添加视频模态窗口
        const addVideoModal = document.getElementById('addVideoModal');
        const modalCloseBtn = document.getElementById('modalCloseBtn');
        const modalCancelBtn = document.getElementById('modalCancelBtn');
        const modalConfirmBtn = document.getElementById('modalConfirmBtn');

        [modalCloseBtn, modalCancelBtn].forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideAddVideoModal();
            });
        });

        modalConfirmBtn.addEventListener('click', () => {
            this.addVideoToPlaylist();
        });

        addVideoModal.addEventListener('click', (e) => {
            if (e.target === addVideoModal) {
                this.hideAddVideoModal();
            }
        });

        // 字幕设置模态窗口
        const subtitleModal = document.getElementById('subtitleSettingsModal');
        const subtitleCloseBtn = document.getElementById('subtitleSettingsCloseBtn');
        const subtitleCancelBtn = document.getElementById('subtitleSettingsCancelBtn');
        const subtitleConfirmBtn = document.getElementById('subtitleSettingsConfirmBtn');

        [subtitleCloseBtn, subtitleCancelBtn].forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideSubtitleSettings();
            });
        });

        subtitleConfirmBtn.addEventListener('click', () => {
            this.applySubtitleSettings();
        });

        subtitleModal.addEventListener('click', (e) => {
            if (e.target === subtitleModal) {
                this.hideSubtitleSettings();
            }
        });

        // 字幕设置滑块事件
        this.initSubtitleSettingsControls();
    }

    // 初始化字幕设置控件
    initSubtitleSettingsControls() {
        const sizeSlider = document.getElementById('subtitleSize');
        const sizeValue = document.getElementById('subtitleSizeValue');
        const opacitySlider = document.getElementById('subtitleOpacity');
        const opacityValue = document.getElementById('subtitleOpacityValue');
        const backgroundSlider = document.getElementById('subtitleBackground');
        const backgroundValue = document.getElementById('subtitleBackgroundValue');

        sizeSlider.addEventListener('input', (e) => {
            sizeValue.textContent = e.target.value + 'px';
        });

        opacitySlider.addEventListener('input', (e) => {
            opacityValue.textContent = e.target.value + '%';
        });

        backgroundSlider.addEventListener('input', (e) => {
            backgroundValue.textContent = e.target.value + '%';
        });
    }

    // 绑定其他事件
    bindEvents() {
        // 视频选择变化时加载字幕
        const videoSelect = document.getElementById('videoSelect');
        videoSelect.addEventListener('change', () => {
            this.loadSubtitlesForVideo(videoSelect.value);
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

            switch (e.code) {
                case 'Space':
                    e.preventDefault();
                    document.getElementById('playPauseBtn').click();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.video.currentTime = Math.max(0, this.video.currentTime - 10);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.video.currentTime = Math.min(this.video.duration, this.video.currentTime + 10);
                    break;
                case 'KeyF':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
            }
        });
    }

    // 格式化时间
    formatTime(seconds) {
        if (isNaN(seconds)) return '00:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // 切换全屏
    toggleFullscreen() {
        const player = document.querySelector('.video-player');

        if (!document.fullscreenElement) {
            player.requestFullscreen().catch(err => {
                console.error('无法进入全屏模式:', err);
            });
        } else {
            document.exitFullscreen();
        }
    }

    // 加载视频列表
    async loadVideoList() {
        try {
            const response = await fetch('/api/video/list');
            const result = await response.json();

            if (result.success && result.data.videos) {
                this.populateVideoSelect(result.data.videos);
            }
        } catch (error) {
            console.error('加载视频列表失败:', error);
        }
    }

    // 填充视频选择下拉框
    populateVideoSelect(videos) {
        const videoSelect = document.getElementById('videoSelect');
        videoSelect.innerHTML = '<option value="">请选择视频文件</option>';

        videos.forEach(video => {
            const option = document.createElement('option');
            option.value = video.name;
            option.textContent = video.name;
            videoSelect.appendChild(option);
        });
    }

    // 加载指定视频的字幕
    async loadSubtitlesForVideo(videoName) {
        if (!videoName) {
            this.populateSubtitleSelect([]);
            return;
        }

        try {
            const response = await fetch(`/api/video/subtitles/${encodeURIComponent(videoName)}`);
            const result = await response.json();

            if (result.success && result.data.subtitles) {
                this.populateSubtitleSelect(result.data.subtitles);
            } else {
                this.populateSubtitleSelect([]);
            }
        } catch (error) {
            console.error('加载字幕列表失败:', error);
            this.populateSubtitleSelect([]);
        }
    }

    // 填充字幕选择下拉框
    populateSubtitleSelect(subtitles) {
        const subtitleSelect = document.getElementById('subtitleSelect');
        subtitleSelect.innerHTML = '<option value="">无字幕</option>';

        subtitles.forEach(subtitle => {
            const option = document.createElement('option');
            option.value = subtitle.name;
            option.textContent = `${subtitle.name} (${subtitle.language})`;
            subtitleSelect.appendChild(option);
        });
    }

    // 显示添加视频模态窗口
    showAddVideoModal() {
        document.getElementById('addVideoModal').classList.add('show');
    }

    // 隐藏添加视频模态窗口
    hideAddVideoModal() {
        document.getElementById('addVideoModal').classList.remove('show');
        document.getElementById('videoSelect').value = '';
        document.getElementById('subtitleSelect').value = '';
    }

    // 添加视频到播放列表
    addVideoToPlaylist() {
        const videoSelect = document.getElementById('videoSelect');
        const subtitleSelect = document.getElementById('subtitleSelect');

        const videoName = videoSelect.value;
        const subtitleName = subtitleSelect.value;

        if (!videoName) {
            alert('请选择一个视频文件');
            return;
        }

        const playlistItem = {
            id: Date.now(),
            videoName: videoName,
            subtitleName: subtitleName,
            title: videoName
        };

        this.currentPlaylist.push(playlistItem);
        this.updatePlaylistDisplay();
        this.hideAddVideoModal();

        // 如果这是第一个视频，自动播放
        if (this.currentPlaylist.length === 1) {
            this.playVideo(0);
        }
    }

    // 更新播放列表显示
    updatePlaylistDisplay() {
        const playlistEmpty = document.getElementById('playlistEmpty');
        const playlistItems = document.getElementById('playlistItems');

        if (this.currentPlaylist.length === 0) {
            playlistEmpty.style.display = 'block';
            playlistItems.style.display = 'none';
        } else {
            playlistEmpty.style.display = 'none';
            playlistItems.style.display = 'block';

            playlistItems.innerHTML = '';
            this.currentPlaylist.forEach((item, index) => {
                const itemEl = this.createPlaylistItemElement(item, index);
                playlistItems.appendChild(itemEl);
            });
        }
    }

    // 创建播放列表项元素
    createPlaylistItemElement(item, index) {
        const itemEl = document.createElement('div');
        itemEl.className = 'playlist-item';
        if (index === this.currentVideoIndex) {
            itemEl.classList.add('active');
        }

        itemEl.innerHTML = `
            <div class="playlist-item-info">
                <h4 class="playlist-item-title">${item.title}</h4>
                <button class="playlist-item-remove" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p class="playlist-item-subtitle">
                字幕: ${item.subtitleName || '无'}
            </p>
        `;

        // 点击播放
        itemEl.addEventListener('click', (e) => {
            if (!e.target.closest('.playlist-item-remove')) {
                this.playVideo(index);
            }
        });

        // 删除按钮
        const removeBtn = itemEl.querySelector('.playlist-item-remove');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeFromPlaylist(index);
        });

        return itemEl;
    }

    // 播放指定索引的视频
    async playVideo(index) {
        if (index < 0 || index >= this.currentPlaylist.length) return;

        const item = this.currentPlaylist[index];
        this.currentVideoIndex = index;

        // 更新视频标题
        document.querySelector('.video-title').textContent = item.title;

        // 加载视频
        const videoUrl = `/api/video/stream/${encodeURIComponent(item.videoName)}`;
        this.video.src = videoUrl;

        // 加载字幕
        if (item.subtitleName) {
            await this.loadSubtitle(item.subtitleName);
        } else {
            this.currentSubtitles = null;
            this.clearSubtitles();
        }

        // 更新播放列表显示
        this.updatePlaylistDisplay();

        // 播放视频
        this.video.load();
        this.video.play().catch(error => {
            console.error('播放失败:', error);
        });
    }

    // 播放下一个视频
    playNext() {
        const nextIndex = this.currentVideoIndex + 1;
        if (nextIndex < this.currentPlaylist.length) {
            this.playVideo(nextIndex);
        }
    }

    // 从播放列表移除
    removeFromPlaylist(index) {
        if (index === this.currentVideoIndex) {
            // 如果删除的是当前播放的视频
            this.video.pause();
            this.video.src = '';
            document.querySelector('.video-title').textContent = '选择一个视频开始观看';
            this.currentVideoIndex = -1;
        } else if (index < this.currentVideoIndex) {
            // 如果删除的是当前视频之前的，调整索引
            this.currentVideoIndex--;
        }

        this.currentPlaylist.splice(index, 1);
        this.updatePlaylistDisplay();
    }

    // 加载字幕文件
    async loadSubtitle(subtitleName) {
        try {
            const response = await fetch(`/api/video/subtitle/${encodeURIComponent(subtitleName)}`);
            const subtitleText = await response.text();
            this.currentSubtitles = this.parseSubtitle(subtitleText);
        } catch (error) {
            console.error('加载字幕失败:', error);
            this.currentSubtitles = null;
        }
    }

    // 解析字幕文件（支持SRT格式）
    parseSubtitle(text) {
        const subtitles = [];
        const blocks = text.trim().split('\n\n');

        blocks.forEach(block => {
            const lines = block.trim().split('\n');
            if (lines.length >= 3) {
                const timeMatch = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
                if (timeMatch) {
                    const startTime = this.parseTimeToSeconds(timeMatch[1], timeMatch[2], timeMatch[3], timeMatch[4]);
                    const endTime = this.parseTimeToSeconds(timeMatch[5], timeMatch[6], timeMatch[7], timeMatch[8]);
                    const textLines = lines.slice(2).join('\n');

                    subtitles.push({
                        start: startTime,
                        end: endTime,
                        text: textLines
                    });
                }
            }
        });

        return subtitles;
    }

    // 将时间转换为秒
    parseTimeToSeconds(hours, minutes, seconds, milliseconds) {
        return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds) + parseInt(milliseconds) / 1000;
    }

    // 更新字幕显示
    updateSubtitles() {
        if (!this.currentSubtitles) return;

        const currentTime = this.video.currentTime;
        const subtitleContainer = document.getElementById('subtitleContainer');

        // 找到当前时间对应的字幕
        const currentSubtitle = this.currentSubtitles.find(subtitle =>
            currentTime >= subtitle.start && currentTime <= subtitle.end
        );

        if (currentSubtitle) {
            subtitleContainer.innerHTML = `<div class="subtitle-text">${currentSubtitle.text}</div>`;
            this.applySubtitleStyles();
        } else {
            subtitleContainer.innerHTML = '';
        }
    }

    // 清除字幕显示
    clearSubtitles() {
        document.getElementById('subtitleContainer').innerHTML = '';
    }

    // 应用字幕样式
    applySubtitleStyles() {
        const subtitleText = document.querySelector('.subtitle-text');
        if (!subtitleText) return;

        const settings = this.subtitleSettings;
        subtitleText.style.fontSize = settings.size + 'px';
        subtitleText.style.color = settings.color;
        subtitleText.style.opacity = settings.opacity / 100;
        subtitleText.style.backgroundColor = `rgba(0, 0, 0, ${settings.background / 100})`;
    }

    // 显示字幕设置窗口
    showSubtitleSettings() {
        const modal = document.getElementById('subtitleSettingsModal');

        // 设置当前值
        document.getElementById('subtitleSize').value = this.subtitleSettings.size;
        document.getElementById('subtitleSizeValue').textContent = this.subtitleSettings.size + 'px';
        document.getElementById('subtitleColor').value = this.subtitleSettings.color;
        document.getElementById('subtitleOpacity').value = this.subtitleSettings.opacity;
        document.getElementById('subtitleOpacityValue').textContent = this.subtitleSettings.opacity + '%';
        document.getElementById('subtitleBackground').value = this.subtitleSettings.background;
        document.getElementById('subtitleBackgroundValue').textContent = this.subtitleSettings.background + '%';

        modal.classList.add('show');
    }

    // 隐藏字幕设置窗口
    hideSubtitleSettings() {
        document.getElementById('subtitleSettingsModal').classList.remove('show');
    }

    // 应用字幕设置
    applySubtitleSettings() {
        this.subtitleSettings = {
            size: parseInt(document.getElementById('subtitleSize').value),
            color: document.getElementById('subtitleColor').value,
            opacity: parseInt(document.getElementById('subtitleOpacity').value),
            background: parseInt(document.getElementById('subtitleBackground').value)
        };

        // 立即应用到当前显示的字幕
        this.applySubtitleStyles();

        this.hideSubtitleSettings();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new VideoRoom();
});

// 阻止视频的默认右键菜单
document.addEventListener('contextmenu', (e) => {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
    }
}); 