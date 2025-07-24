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
