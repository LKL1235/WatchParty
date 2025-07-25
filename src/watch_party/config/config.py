import logging
import os
import yaml
from pydantic import BaseModel
from watch_party.config.default_config import DEFAULT_DATA_PATH, DEFAULT_LOG_PATH


class ServerConfig(BaseModel):
    port: int = 5000
    log_path: str = DEFAULT_LOG_PATH

class DataConfig(BaseModel):
    data_path: str = DEFAULT_DATA_PATH


class AllConfig(BaseModel):
    serverConfig: ServerConfig = ServerConfig()
    dataConfig: DataConfig = DataConfig()

class Config:
    config: AllConfig
    @classmethod
    def InitConfig(cls, configPath: str) -> bool:
        if not os.path.exists(configPath):
            logging.error(f"配置文件{configPath}不存在")
            return False
        with open(configPath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            Config.config = AllConfig(**data)
        return True
