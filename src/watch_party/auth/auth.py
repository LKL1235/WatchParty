
import uuid


def verify(user_id: str, password: str) -> bool:
    # TODO: 从数据库中验证用户名和密码
    return True

def register(user_name: str, password: str) -> str:
    # TODO: 从数据库中注册用户
    return str(uuid.uuid4())