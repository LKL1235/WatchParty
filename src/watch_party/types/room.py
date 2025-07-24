from typing import Any
from watch_party.types.user import User
from watch_party.types.video import Video


class Room:
    def __init__(self, room_id: str, room_name: str):
        self.room_id = room_id
        self.room_name = room_name
        self.public = False
        self.users: list[User] = []
        self.play_list: list[Video] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "public": self.public,
            "users": [user.user_name for user in self.users],
        }

    def add_user(self, user: User):
        user.join_room(self.room_id)
        self.users.append(user)

    def remove_user(self, user: User):
        user.leave_room()
        self.users.remove(user)

    def add_video(self, video: Video):
        self.play_list.append(video)

    def remove_video(self, video: Video):
        self.play_list.remove(video)

    def is_room_empty(self) -> bool:
        return len(self.users) == 0

    def is_public(self) -> bool:
        return self.public

    def set_public(self, public: bool):
        self.public = public

    def get_room_name(self) -> str:
        return self.room_name

    def get_room_id(self) -> str:
        return self.room_id

    def get_users(self) -> list[User]:
        return self.users

    def get_play_list(self) -> list[Video]:
        return self.play_list

    def get_user_count(self) -> int:
        return len(self.users)
