import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

dir_path = os.path.dirname(os.path.realpath(__file__))

if os.name == 'posix':
    DEVELOPE_MODE = os.getenv('DEVELOPE_MODE', 'False') == 'True'
else:
    DEVELOPE_MODE = True

class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(dir_path, '.dev_env' if DEVELOPE_MODE else '.prod_env'),
        env_file_encoding='utf-8',
        extra='ignore',
    )


class TelegramConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='TG_')

    TOKEN: str


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='DB_')

    HOST: str
    PORT: int
    USER: str
    DATABASE: str
    PASSWORD: str

    def get_url(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


class ArtixCashDatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='ARTIXCASH_DB_')

    PORT: int
    USER: str
    PASSWORD: str

    def get_url(self, database: str, host: str):
        return f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{host}:{self.PORT}/{database}?charset=utf8mb4"


class RedisConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='REDIS_')

    HOST: str
    PORT: int

    async def url(self):
        return f'redis://{self.HOST}:{self.PORT}'


class CashServerConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='CS_')

    HOST: str
    PORT: int
    LOGIN: str
    PASSWORD: str

    def cs_url(self):
        return f'http://{self.HOST}:{self.PORT}/CSrest/rest'

    def acc_url(self):
        return f'http://{self.HOST}:{self.PORT}/ACC/rest/v1'


class ForemanConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='FOREMAN_')

    URL_14: str
    USERNAME_14: str
    PASSWORD_14: str

    URL_18: str
    USERNAME_18: str
    PASSWORD_18: str

class OpenAIConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='OPENAI_')

    TOKEN: str

cs_cfg = CashServerConfig()
db_cfg = DatabaseConfig()
tg_cfg = TelegramConfig()
redis_cfg = RedisConfig()
foreman_cfg = ForemanConfig()
artixcash_db_cfg = ArtixCashDatabaseConfig()
openai_cfg = OpenAIConfig()