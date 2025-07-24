from watch_party.types.room import Room
import uuid


class RoomManager:
    rooms_by_id: dict[str, Room] = {}
    # 可选：如果需要频繁按名称精确查找，可以添加name索引
    rooms_by_name: dict[str, list[Room]] = {}

    @classmethod
    def create_room(cls, room_name: str) -> Room:
        room_id = str(uuid.uuid4())
        room = Room(room_id, room_name)
        cls.rooms_by_id[room_id] = room
        # 修复bug：使用setdefault确保key存在
        cls.rooms_by_name.setdefault(room_name, []).append(room)
        return room

    @classmethod
    def get_room(cls, room_id: str) -> Room | None:
        # O(1) 时间复杂度查找
        if room_id not in cls.rooms_by_id:
            return None
        return cls.rooms_by_id[room_id]

    @classmethod
    def get_all_rooms(cls) -> list[Room]:
        # 返回所有房间的列表
        return list(cls.rooms_by_id.values())

    @classmethod
    def get_room_count(cls) -> int:
        return len(cls.rooms_by_id)

    @classmethod
    def delete_room(cls, room_id: str) -> bool:
        """删除房间，返回是否成功删除"""
        if room_id in cls.rooms_by_id:
            del cls.rooms_by_id[room_id]
            room = cls.rooms_by_id[room_id]
            room_name = room.room_name
            if room_name in cls.rooms_by_name:
                cls.rooms_by_name[room_name].remove(room)
                if not cls.rooms_by_name[room_name]:
                    del cls.rooms_by_name[room_name]
            return True
        return False

    @classmethod
    def room_exists(cls, room_id: str) -> bool:
        """检查房间是否存在,O(1)时间复杂度"""
        return room_id in cls.rooms_by_id

    @classmethod
    def search_room(cls, search_name: str) -> list[Room]:
        """根据关键字模糊匹配房间名字，返回匹配的房间列表"""
        result: list[Room] = []
        # 在房间名字的keys中搜索，更符合数据结构设计
        for room_name in cls.rooms_by_name.keys():
            if search_name.lower() in room_name.lower():
                # 添加该名字下的所有房间
                result.extend(cls.rooms_by_name[room_name])
        return result
