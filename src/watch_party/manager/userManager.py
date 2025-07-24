import logging
from watch_party.types.user import User
from watch_party.auth.auth import register, verify


class UserManager:
    users_by_id: dict[str, User] = {}
    users_by_name: dict[str, list[User]] = {}

    @classmethod
    def load_all_users(cls):
        # TODO: 从数据库中加载所有用户
        pass

    @classmethod
    def _create_user(cls, user_id: str, user_name: str) -> User | None:
        user = User(user_id, user_name)
        if user_id in cls.users_by_id:
            logging.error(f"User with id {user_id} already exists")
            return None
        cls.users_by_id[user_id] = user
        cls.users_by_name.setdefault(user_name, []).append(user)
        return user

    @classmethod
    def get_user(cls, user_id: str) -> User | None:
        if user_id not in cls.users_by_id:
            return None
        return cls.users_by_id[user_id]

    @classmethod
    def get_all_users(cls) -> list[User]:
        return list(cls.users_by_id.values())

    @classmethod
    def get_user_count(cls) -> int:
        return len(cls.users_by_id)

    @classmethod
    def _delete_user(cls, user_id: str) -> bool:
        if user_id in cls.users_by_id:
            del cls.users_by_id[user_id]
            user = cls.users_by_id[user_id]
            user_name = user.user_name
            if user_name in cls.users_by_name:
                cls.users_by_name[user_name].remove(user)
                if not cls.users_by_name[user_name]:
                    del cls.users_by_name[user_name]
            return True
        return False

    @classmethod
    def is_user_exists(cls, user_id: str) -> bool:
        return user_id in cls.users_by_id

    @classmethod
    def search_user(cls, search_name: str) -> list[User]:
        result: list[User] = []
        for user_name in cls.users_by_name.keys():
            if search_name.lower() in user_name.lower():
                result.extend(cls.users_by_name[user_name])
        return result

    @classmethod
    def user_login(cls, user_id: str, password: str) -> bool:
        if not verify(user_id, password):
            return False
        user: User | None = cls.get_user(user_id)
        if user is None:
            return False
        user.login()
        return True

    @classmethod
    def user_register(cls, user_name: str, password: str) -> User | None:
        user_id = register(user_name, password)
        user: User | None = cls._create_user(user_id, user_name)
        if user is None:
            logging.error(f"Failed to create user {user_name}")
            return None
        return user

    @classmethod
    def user_logout(cls, user_id: str):
        user: User | None = cls.get_user(user_id)
        if user is None:
            return False
        user.logout()
        return True
