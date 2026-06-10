import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Telegram
    bot_token: str
    # MAX
    max_bot_token: str
    # Сервисы
    claude_api_key: str
    database_url: str

def load_config() -> Config:
    """Загружает конфигурацию из .env файла"""
    return Config(
        bot_token=os.getenv('BOT_TOKEN'),
        max_bot_token=os.getenv('MAX_BOT_TOKEN'),
        claude_api_key=os.getenv('CLAUDE_API_KEY'),
        database_url=os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data/bot.db')
    )