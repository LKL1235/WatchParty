import sys
import os

if sys.platform == "win32":
    default_config_path = os.path.join(os.path.expandvars("%APPDATA%"), "watch_party", "config.yaml")
    default_data_path = os.path.join(os.path.expandvars("%APPDATA%"), "watch_party", "data")
    default_log_path = os.path.join(os.path.expandvars("%APPDATA%"), "watch_party", "logs")
else:
    default_config_path = os.path.join(os.path.expandvars("%HOME%"), ".config", "watch_party", "config.yaml")
    default_data_path = os.path.join(os.path.expandvars("%HOME%"), ".watch_party", "data")
    default_log_path = os.path.join(os.path.expandvars("%HOME%"), ".watch_party", "logs")

DEFAULT_CONFIG_PATH = default_config_path
DEFAULT_DATA_PATH = default_data_path
DEFAULT_LOG_PATH = default_log_path