# JavaScript 模块化结构

播放器JavaScript代码已经重构为模块化结构，采用简化的预加载策略。

## 文件结构

### `config.js` - 配置管理
- 包含所有播放器配置常量
- 简化的缓冲预加载参数（5分钟预加载）
- 键盘快捷键配置
- 默认字幕样式

### `buffer-manager.js` - 简化缓冲管理器
- `BufferManager` 类：基于字节范围的简单预加载管理
- 监控缓冲状态，只向后预加载
- 全局记录已加载的字节范围
- 跳转时智能重置预加载位置

### `controls.js` - 控件管理器
- `VideoControls` 类：视频播放控件管理
- `SubtitleControls` 类：字幕样式控制
- 进度条、音量控制、全屏等功能
- 控件显示/隐藏逻辑

### `player-core.js` - 核心播放器
- `VideoPlayer` 类：主播放器逻辑
- 整合所有模块功能
- 视频/字幕加载和管理
- 跳转事件处理

## 新的预加载策略

### 简化原则
1. **删除复杂逻辑**：移除智能预测、历史分析等复杂功能
2. **基于字节范围**：直接计算字节位置，使用HTTP Range请求
3. **只向后加载**：从当前位置向后预加载，不向前加载
4. **全局范围记录**：统一记录已加载的字节范围，避免重复下载

### 核心逻辑
```javascript
// 1. 计算当前时间对应的字节位置
const currentBytePosition = (currentTime / videoDuration) * fileSize;

// 2. 计算5分钟预加载对应的字节数
const preloadBytes = (300 / videoDuration) * fileSize;

// 3. 只向后预加载，不重复加载
const rangeStart = Math.max(currentBytePosition, lastPreloadPosition);
const rangeEnd = rangeStart + preloadBytes;

// 4. 跳过已加载的部分，只加载需要的范围
const neededRanges = calculateNeededRanges(rangeStart, rangeEnd);
```

### 跳转行为
- **向后跳转**：继续从新位置预加载，保留已加载的内容
- **向前跳转**：重置预加载位置，从新位置开始，保留后续已加载的内容

## 配置参数

简化后的预加载配置：
- `PRELOAD_DURATION`: 300秒（5分钟预加载时长）
- `LOW_BUFFER_THRESHOLD`: 120秒（2分钟缓冲不足阈值）
- `CHECK_INTERVAL`: 10000ms（10秒检查间隔）
- `LOW_BUFFER_WARNING`: 30秒（低缓冲警告）

## 主要改进

1. **简化架构**：删除复杂的预测和智能逻辑
2. **字节精确控制**：直接控制下载的字节范围
3. **避免重复下载**：全局记录已加载范围
4. **高效跳转**：智能处理跳转后的预加载
5. **更好的调试**：清晰的字节范围日志

## 依赖关系

```
player-core.js
├── config.js
├── buffer-manager.js (简化版)
└── controls.js
```

所有文件按顺序加载，确保依赖关系正确。 