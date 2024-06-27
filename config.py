import os
from datetime import date
from pathlib import Path

from fake_useragent import UserAgent
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

root_path = Path(os.path.abspath(__file__)).parent
ua = UserAgent()
today = date.today()


class Settings(BaseSettings):
    driver_name: str
    username: str
    password: SecretStr
    host: str
    port: int
    echo: bool
    database: str
    headless_mode: bool
    job_texts_quantity: int
    model_config = SettingsConfigDict(env_file=f'{root_path}/settings.env', env_file_encoding='utf-8')
