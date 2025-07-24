
from typing import Optional
from enum import Enum


class UserStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class User:
    def __init__(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.room_id: Optional[str] = None
        self.status: UserStatus = UserStatus.OFFLINE
        self.avatar: Optional[str] = None

    def join_room(self, room_id: str):
        self.room_id = room_id

    def leave_room(self):
        self.room_id = None
        
    def __set_status(self, status: UserStatus):
        self.status = status
    
    def login(self):
        self.__set_status(UserStatus.ONLINE)
        
    def logout(self):
        self.__set_status(UserStatus.OFFLINE)
