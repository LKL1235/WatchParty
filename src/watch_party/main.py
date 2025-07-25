import logging
import os
from flask import Flask, render_template
from flask_cors import CORS
from watch_party.commons.commons import cmd_args_parse, init_template_and_static_dir
from watch_party.config.config import Config
from watch_party.config.default_config import DEFAULT_CONFIG_PATH
from watch_party.log.logController import init_log_format
from watch_party.api import room_api, video_api

template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")

# 创建Flask应用实例
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# 启用CORS
CORS(app)

# 注册蓝图
app.register_blueprint(room_api.bp)
app.register_blueprint(video_api.bp)


# 主页路由
@app.route("/")
def index():
    """主页"""
    return render_template("index.html")


# 播放页路由
@app.route("/player")
def player():
    """播放页"""
    return render_template("player.html")


# 房间页路由
@app.route("/room")
def room():
    """房间页"""
    return render_template("room.html")


def main() -> None | int:
    init_log_format()
    if not init_template_and_static_dir(template_dir, static_dir):
        logging.error("初始化模板和静态文件目录失败")
        return
    args = cmd_args_parse()
    config_path = DEFAULT_CONFIG_PATH
    if args.config:
        config_path = args.config
    if not Config.InitConfig(config_path):
        logging.error("初始化配置失败")
        return
    return Config.config.serverConfig.port


if __name__ == "__main__":
    port = main()
    app.run(host="0.0.0.0", port=port, debug=True)
