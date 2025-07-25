import os
import logging
from typing import Any
from flask import Blueprint, jsonify, send_file, Response, request
from watch_party.api.api_commons import (
    response_template, 
    HttpHeadersConfig, 
    apply_headers, 
    create_range_response_headers
)
from watch_party.commons.subtitle_commons import (
    ensure_directories,
    get_file_info,
    is_video_file,
    is_subtitle_file,
    files_match,
    detect_language,
    decode_subtitle_file,
    get_subtitle_mime_type,
    get_video_dir,
    get_subtitle_dir
)

# 视频流配置常量
class VideoStreamConfig:
    """视频流相关配置"""
    CHUNK_SIZE = 8192  # 数据块大小（字节）

bp = Blueprint("video", __name__, url_prefix="/api/video")

def get_file_size(file_path: str) -> int:
    """获取文件大小"""
    return os.path.getsize(file_path)

def parse_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    """解析HTTP Range头"""
    try:
        # 解析 "bytes=start-end" 格式
        ranges = range_header.replace('bytes=', '').split('-')
        start = int(ranges[0]) if ranges[0] else 0
        end = int(ranges[1]) if ranges[1] else file_size - 1
        
        # 确保范围有效
        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))
        
        return start, end
    except (ValueError, IndexError):
        return 0, file_size - 1

def create_range_response(file_path: str, start: int, end: int, file_size: int, mimetype: str | None = None) -> Response:
    """创建支持Range的响应"""
    if mimetype is None:
        mimetype = HttpHeadersConfig.VIDEO_MP4
        
    def generate_chunks():
        chunk_size = VideoStreamConfig.CHUNK_SIZE
        with open(file_path, 'rb') as f:
            f.seek(start)
            remaining = end - start + 1
            
            while remaining > 0:
                chunk_size_to_read = min(chunk_size, remaining)
                chunk = f.read(chunk_size_to_read)
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
    
    headers = create_range_response_headers(start, end, file_size, content_type=mimetype)
    
    return Response(
        generate_chunks(),
        status=HttpHeadersConfig.PARTIAL_CONTENT,
        headers=headers
    )


@bp.route("/list", methods=["GET"])
def list_videos():
    """获取服务器上的视频文件列表"""
    try:
        ensure_directories()

        videos: list[dict[str, Any]] = []
        for filename in os.listdir(get_video_dir()):
            if is_video_file(filename):
                file_path = os.path.join(get_video_dir(), filename)
                videos.append(get_file_info(file_path, filename))

        logging.info(f"找到 {len(videos)} 个视频文件")
        return jsonify(response_template(code=0, data={"videos": videos}, message="获取视频列表成功"))

    except Exception as e:
        logging.error(f"获取视频列表失败: {str(e)}")
        return jsonify(response_template(code=1, data=None, message=f"获取视频列表失败: {str(e)}", success=False)), 500


@bp.route("/subtitles/<video_name>", methods=["GET"])
def list_subtitles(video_name: str):
    """获取指定视频的字幕文件列表"""
    try:
        ensure_directories()

        logging.info(f"正在查找视频 '{video_name}' 的字幕文件")

        subtitles: list[dict[str, str]] = []
        subtitle_files = os.listdir(get_subtitle_dir())
        logging.info(f"字幕目录中共有 {len(subtitle_files)} 个文件")

        for filename in subtitle_files:
            if is_subtitle_file(filename):
                is_match, match_reason = files_match(video_name, filename)

                if is_match:
                    language = detect_language(filename)
                    subtitle_info = {"name": filename, "path": filename, "language": language}
                    subtitles.append(subtitle_info)
                    logging.info(f"找到匹配字幕: {filename} ({match_reason}, 语言: {language})")

        logging.info(f"为视频 '{video_name}' 找到 {len(subtitles)} 个字幕文件")
        return jsonify(response_template(code=0, data={"subtitles": subtitles}, message="获取字幕列表成功"))

    except Exception as e:
        logging.error(f"获取字幕列表失败: {str(e)}")
        return jsonify(response_template(code=1, data=None, message=f"获取字幕列表失败: {str(e)}", success=False)), 500


@bp.route("/stream/<video_name>", methods=["GET", "HEAD"])
def stream_video(video_name: str):
    """流式传输视频文件，支持HTTP Range请求"""
    try:
        video_path = os.path.join(get_video_dir(), video_name)

        if not os.path.exists(video_path):
            logging.warning(f"请求的视频文件不存在: {video_path}")
            return jsonify(response_template(code=1, data=None, message="视频文件不存在", success=False)), 404

        # 获取文件大小
        file_size = get_file_size(video_path)
        
        # 如果是HEAD请求，只返回头部信息
        if request.method == 'HEAD':
            response = Response()
            response.headers['Content-Type'] = HttpHeadersConfig.VIDEO_MP4
            response.headers['Content-Length'] = str(file_size)
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Cache-Control'] = f'public, max-age={HttpHeadersConfig.DEFAULT_CACHE_MAX_AGE}'
            video_headers = HttpHeadersConfig.get_video_cache_headers()
            apply_headers(response, video_headers)
            return response
        
        # 检查是否有Range请求
        range_header = request.headers.get('Range')
        
        if range_header:
            # 处理Range请求
            start, end = parse_range_header(range_header, file_size)
            
            if start > end or start >= file_size:
                return jsonify(response_template(code=1, data=None, message="Range无效", success=False)), HttpHeadersConfig.RANGE_NOT_SATISFIABLE
            
            logging.info(f"流式传输视频片段: {video_name} (范围: {start}-{end}/{file_size})")
            return create_range_response(video_path, start, end, file_size)
        else:
            # 没有Range请求，返回整个文件，但仍支持Range
            logging.info(f"流式传输整个视频: {video_name}")
            response = send_file(video_path, as_attachment=False, mimetype=HttpHeadersConfig.VIDEO_MP4)
            video_headers = HttpHeadersConfig.get_video_cache_headers()
            apply_headers(response, video_headers)
            return response

    except Exception as e:
        logging.error(f"流式传输视频失败: {str(e)}")
        return jsonify(response_template(code=1, data=None, message=f"流式传输视频失败: {str(e)}", success=False)), 500


@bp.route("/subtitle/<subtitle_name>", methods=["GET"])
def get_subtitle(subtitle_name: str):
    """获取字幕文件"""
    try:
        subtitle_path = os.path.join(get_subtitle_dir(), subtitle_name)

        if not os.path.exists(subtitle_path):
            logging.warning(f"请求的字幕文件不存在: {subtitle_path}")
            return jsonify(response_template(code=1, data=None, message="字幕文件不存在", success=False)), 404

        logging.info(f"尝试获取字幕文件: {subtitle_name}")

        # 解码字幕文件
        content, used_encoding = decode_subtitle_file(subtitle_path)

        # 设置响应
        mime_type = get_subtitle_mime_type(subtitle_name)
        subtitle_headers = HttpHeadersConfig.get_subtitle_headers()
        subtitle_headers['Content-Type'] = mime_type

        response = Response(content.encode('utf-8'), mimetype=mime_type)
        apply_headers(response, subtitle_headers)

        logging.info(f"成功提供字幕文件: {subtitle_name} (使用编码: {used_encoding})")
        return response

    except ValueError as e:
        logging.error(f"字幕文件编码错误: {str(e)}")
        return jsonify(response_template(code=1, data=None, message=str(e), success=False)), 400

    except Exception as e:
        logging.error(f"获取字幕文件失败: {str(e)}")
        return jsonify(response_template(code=1, data=None, message=f"获取字幕文件失败: {str(e)}", success=False)), 500
