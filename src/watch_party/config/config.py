import logging
import os
import yaml
from pydantic import BaseModel


class ServerConfig(BaseModel):
    port: int = 5000
    log_path: str = "logs"
    data_path: str = "data"


class AllConfig(BaseModel):
    serverConfig: ServerConfig = ServerConfig()


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
