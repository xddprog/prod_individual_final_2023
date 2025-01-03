from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    bot_token: str
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str


@dataclass
class BotConfig:
    token: str
    redis_url: str


def load_database_config() -> DatabaseConfig:
    env = Env()
    env.read_env()
    return DatabaseConfig(
        bot_token=env('BOT_TOKEN'),
        db_name=env('DB_NAME'),
        db_user=env('DB_USER'),
        db_password=env('DB_PASSWORD'),
        db_host=env('DB_HOST'),
        db_port=env('DB_PORT'),
    )


def load_config() -> BotConfig:
    env = Env()
    env.read_env()
    return BotConfig(
        token=env('BOT_TOKEN'),
        redis_url=env('REDIS_URL')
    )


def load_geoapify_token() -> str:
    env = Env()
    env.read_env()
    return env("GEOAPIFY_KEY")
