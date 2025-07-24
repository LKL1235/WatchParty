from enum import Enum


class ErrorCode(Enum):
    SUCCESS = 0
    PARAMS_ERROR = 1
    PARAM_TYPE_ERROR = 2
    PARAM_MISSING = 3
    PARAM_EMPTY = 4
    PARAM_INVALID = 5