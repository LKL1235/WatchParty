from collections.abc import Callable
from typing import Any
from functools import wraps
from flask import request, jsonify, Response
import logging
from watch_party.api.error_code import ErrorCode


def response_template(code: int, data: Any, message: str, success: bool = True) -> dict[str, Any]:
    return {"code": code, "data": data, "message": message, "success": success}


class ParamsCheckError(Exception):
    """参数检查异常类"""

    def __init__(self, message: str, param_name: str | None = None, error_code: ErrorCode | int | None = None):
        super().__init__(message)
        self.message = message
        self.param_name = param_name  # 出错的参数名
        self.error_code = error_code  # 错误代码，用于前端处理
        self.status_code = 400  # HTTP状态码

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式,方便JSON响应"""
        # 获取错误代码的数值
        error_code_value = self.error_code.value if isinstance(self.error_code, ErrorCode) else self.error_code
        code = error_code_value if error_code_value is not None else ErrorCode.PARAMS_ERROR.value

        # 构建额外的错误数据
        error_data = {}
        if self.param_name:
            error_data["param_name"] = self.param_name

        return response_template(
            code=code, data=error_data if error_data else None, message=self.message, success=False
        )


def params_check(required_params: dict[str, type]) -> dict[str, Any]:
    post_params = request.get_json()
    url_params = request.args.to_dict()
    params = {**url_params, **post_params}
    for param, param_type in required_params.items():
        if param not in params:
            logging.error(f"参数 {param} 不存在")
            raise ParamsCheckError(f"参数 {param} 不存在", param_name=param, error_code=ErrorCode.PARAM_MISSING)
        if params[param] == "":
            logging.error(f"参数 {param} 为空")
            raise ParamsCheckError(f"参数 {param} 为空", param_name=param, error_code=ErrorCode.PARAM_EMPTY)
        if not isinstance(params[param], param_type):
            logging.error(f"参数 {param} 类型错误")
            raise ParamsCheckError(
                f"参数 {param} 类型错误，期望 {param_type.__name__}，得到 {type(params[param]).__name__}",
                param_name=param,
                error_code=ErrorCode.PARAM_TYPE_ERROR,
            )
    return params


def handle_params_error(func: Callable[..., Any]) -> Callable[..., Any]:
    """自动处理参数检查异常的装饰器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> tuple[Response, int]:
        try:
            return func(*args, **kwargs)
        except ParamsCheckError as e:
            return jsonify(e.to_dict()), e.status_code

    return wrapper


# HTTP头部配置类
class HttpHeadersConfig:
    """HTTP头部相关配置"""
    
    # 缓存配置
    DEFAULT_CACHE_MAX_AGE = 3600  # 默认缓存时间（秒）
    NO_CACHE = 'no-cache'
    PUBLIC_CACHE = 'public'
    
    # MIME类型
    VIDEO_MP4 = 'video/mp4'
    APPLICATION_JSON = 'application/json'
    TEXT_VTT = 'text/vtt; charset=utf-8'
    APPLICATION_SUBRIP = 'application/x-subrip; charset=utf-8'
    
    # HTTP状态码
    PARTIAL_CONTENT = 206
    RANGE_NOT_SATISFIABLE = 416
    
    # 通用CORS头部
    @staticmethod
    def get_cors_headers() -> dict[str, str]:
        """获取基础CORS头部"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Range',
            'Access-Control-Expose-Headers': 'Content-Range, Accept-Ranges, Content-Length'
        }
    
    # 视频流CORS头部
    @staticmethod
    def get_video_cors_headers() -> dict[str, str]:
        """获取视频流专用CORS头部"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Access-Control-Allow-Headers': 'Range, Content-Type, Accept',
            'Access-Control-Expose-Headers': 'Content-Range, Accept-Ranges, Content-Length'
        }
    
    # 字幕文件头部
    @staticmethod
    def get_subtitle_headers() -> dict[str, str]:
        """获取字幕文件专用头部"""
        return {
            'Cache-Control': HttpHeadersConfig.NO_CACHE,
            **HttpHeadersConfig.get_cors_headers()
        }
    
    # 视频缓存头部
    @staticmethod
    def get_video_cache_headers(max_age: int | None = None) -> dict[str, str]:
        """获取视频缓存头部"""
        if max_age is None:
            max_age = HttpHeadersConfig.DEFAULT_CACHE_MAX_AGE
        
        return {
            'Accept-Ranges': 'bytes',
            'Cache-Control': f'{HttpHeadersConfig.PUBLIC_CACHE}, max-age={max_age}',
            **HttpHeadersConfig.get_video_cors_headers()
        }
    
    # Range响应头部
    @staticmethod
    def get_range_headers(start: int, end: int, total_size: int, content_type: str | None = None) -> dict[str, str]:
        """获取Range请求响应头部"""
        if content_type is None:
            content_type = HttpHeadersConfig.VIDEO_MP4
            
        return {
            'Content-Type': content_type,
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Content-Range': f'bytes {start}-{end}/{total_size}',
            **HttpHeadersConfig.get_video_cache_headers()
        }


def create_cors_headers() -> dict[str, str]:
    """创建CORS响应头（向后兼容）"""
    return {
        'Cache-Control': HttpHeadersConfig.NO_CACHE,
        **HttpHeadersConfig.get_cors_headers()
    }


def apply_headers(response: Response, headers: dict[str, str]) -> Response:
    """为Response对象应用头部"""
    for key, value in headers.items():
        response.headers[key] = value
    return response


def create_video_response(content: Any, status: int = 200, **header_kwargs: Any) -> Response:
    """创建视频响应"""
    response = Response(content, status=status)
    headers = HttpHeadersConfig.get_video_cache_headers(**header_kwargs)
    return apply_headers(response, headers)


def create_range_response_headers(start: int, end: int, total_size: int, **kwargs: Any) -> dict[str, str]:
    """创建Range响应的头部"""
    return HttpHeadersConfig.get_range_headers(start, end, total_size, **kwargs)
