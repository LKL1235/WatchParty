import os
import logging
from typing import Any
import chardet
import re
from watch_party.config.config import Config

# 常量定义
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
SUBTITLE_EXTENSIONS = {'.srt', '.vtt', '.ass', '.ssa', '.sub'}

# MIME类型映射
SUBTITLE_MIME_TYPES = {
    '.vtt': 'text/vtt; charset=utf-8',
    '.srt': 'application/x-subrip; charset=utf-8',
    'default': 'application/x-subrip; charset=utf-8',
}

# 语言识别模式
LANGUAGE_PATTERNS = {
    'zh': ['zh', 'chinese', 'chs', 'cht', '中文', '简体', '繁体'],
    'en': ['en', 'english', 'eng'],
    'ja': ['ja', 'japanese', 'jpn', '日语'],
    'ko': ['ko', 'korean', 'kor', '韩语'],
    'fr': ['fr', 'french', 'fra'],
    'de': ['de', 'german', 'ger'],
    'es': ['es', 'spanish', 'spa'],
    'ru': ['ru', 'russian', 'rus'],
}

# 编码尝试列表
ENCODING_LIST = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'cp936']


def get_data_base_dir() -> str:
    """获取数据基础目录路径"""
    return Config.config.dataConfig.data_path


def get_video_dir() -> str:
    """获取视频目录路径"""
    return os.path.join(get_data_base_dir(), "videos")


def get_subtitle_dir() -> str:
    """获取字幕目录路径"""
    return os.path.join(get_data_base_dir(), "subtitles")


def ensure_directories() -> None:
    """确保必要的目录存在"""
    for directory in [get_video_dir(), get_subtitle_dir()]:
        os.makedirs(directory, exist_ok=True)


def get_file_info(file_path: str, filename: str) -> dict[str, Any]:
    """获取文件基本信息"""
    file_stats = os.stat(file_path)
    return {"name": filename, "path": filename, "size": file_stats.st_size, "modified": file_stats.st_mtime}


def is_video_file(filename: str) -> bool:
    """检查是否为视频文件"""
    return any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)


def is_subtitle_file(filename: str) -> bool:
    """检查是否为字幕文件"""
    return any(filename.lower().endswith(ext) for ext in SUBTITLE_EXTENSIONS)


def clean_filename_for_matching(name: str) -> str:
    """清理文件名用于模糊匹配"""
    # 移除常见分隔符
    name = re.sub(r'[._\-\s]+', ' ', name)
    # 移除版本信息
    name = re.sub(r'\b(1080p|720p|480p|4k|hd|dvd|blu-?ray|bdrip|webrip|hdtv)\b', '', name, flags=re.IGNORECASE)
    # 移除年份和括号内容
    name = re.sub(r'\b(19|20)\d{2}\b', '', name)
    name = re.sub(r'[\(\[][^\)\]]*[\)\]]', '', name)
    # 清理空格
    return ' '.join(name.split()).strip().lower()


def files_match(video_name: str, subtitle_name: str) -> tuple[bool, str]:
    """检查视频和字幕文件是否匹配"""
    video_base = os.path.splitext(video_name)[0].lower()
    subtitle_base = os.path.splitext(subtitle_name)[0].lower()

    # 完全匹配
    if video_base == subtitle_base:
        return True, "完全匹配"

    # 包含匹配
    if video_base in subtitle_base:
        return True, "字幕名包含视频名"

    if len(subtitle_base) >= 3 and subtitle_base in video_base:
        return True, "视频名包含字幕名"

    # 模糊匹配
    clean_video = clean_filename_for_matching(video_base)
    clean_subtitle = clean_filename_for_matching(subtitle_base)

    if clean_video and clean_subtitle and len(clean_subtitle) >= 5:
        if clean_video == clean_subtitle or clean_subtitle in clean_video or clean_video in clean_subtitle:
            return True, "模糊匹配"

    return False, ""


def detect_language(filename: str) -> str:
    """从文件名检测语言"""
    filename_lower = filename.lower()

    for lang_code, patterns in LANGUAGE_PATTERNS.items():
        if any(pattern in filename_lower for pattern in patterns):
            return lang_code

    return 'auto'


def decode_subtitle_file(file_path: str) -> tuple[str, str]:
    """解码字幕文件内容"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    # 检测编码
    detected = chardet.detect(raw_data)
    detected_encoding = detected.get('encoding', 'utf-8')

    logging.info(f"检测到编码: {detected_encoding} (置信度: {detected.get('confidence', 0):.2f})")

    # 尝试解码
    encodings_to_try = [detected_encoding] + ENCODING_LIST

    for encoding in encodings_to_try:
        if encoding is None:
            continue
        try:
            content = raw_data.decode(encoding)
            logging.info(f"成功使用编码 {encoding} 解码文件")
            return content, encoding
        except (UnicodeDecodeError, LookupError):
            continue

    raise ValueError("无法解码字幕文件，请转换为UTF-8格式")


def get_subtitle_mime_type(filename: str) -> str:
    """获取字幕文件的MIME类型"""
    extension = os.path.splitext(filename)[1].lower()
    return SUBTITLE_MIME_TYPES.get(extension, SUBTITLE_MIME_TYPES['default'])
