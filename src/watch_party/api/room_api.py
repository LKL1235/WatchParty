from watch_party.manager.roomManager import RoomManager
from watch_party.manager.userManager import UserManager
from watch_party.types.room import Room
from watch_party.api.api_commons import params_check, handle_params_error
from flask import Blueprint, jsonify

bp = Blueprint("room", __name__, url_prefix="/room")


@bp.route("/get_all_public_rooms", methods=["GET"])
def get_all_public_room():
    rooms = RoomManager.get_all_rooms()
    public_rooms = [room for room in rooms if room.is_public()]
    return jsonify(public_rooms)


@bp.route("/join_room", methods=["POST"])
@handle_params_error
def join_room():
    # 使用params_check进行参数验证
    params = params_check({"room_id": str, "user_id": str})
    room_id: str = params["room_id"]
    user_id: str = params["user_id"]

    room: Room | None = RoomManager.get_room(room_id)
    if room is None or not room.is_public():
        return jsonify({"success": False, "error": "Room not found or not public"}), 404

    user = UserManager.get_user(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found"}), 404

    room.add_user(user)
    user.join_room(room_id)

    return jsonify(room.to_dict())


@bp.route("/leave_room", methods=["POST"])
@handle_params_error
def leave_room():
    # 使用params_check进行参数验证
    params = params_check({"room_id": str})
    room_id = params["room_id"]

    room = RoomManager.get_room(room_id)
    if room is None or not room.is_public():
        return jsonify({"success": False, "error": "Room not found or not public"}), 404

    return jsonify({"success": True})
