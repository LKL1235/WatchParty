import logging
import os
from argparse import ArgumentParser, Namespace


def cmd_args_parse() -> Namespace:
    # 解析命令行参数
    parser = ArgumentParser()
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    return parser.parse_args()


def init_template_and_static_dir(template_dir: str, static_dir: str) -> bool:
    # 确保模板和静态文件目录存在
    try:
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"初始化模板和静态文件目录失败: {e}")
        return False
    return True


