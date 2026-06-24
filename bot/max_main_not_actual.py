import os
import sys
import asyncio

# Добавляем корень проекта (C:\onboarding-bot) в sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

#from adapters.max.bot import run_max_bot
from bot.adapters.max.create_bot import bot
import aiomax
from aiomax import BotCommand
#import logging
from bot.adapters.max.handlers import router
from bot.adapters.max.create_bot import logger

from services.redis_storage import close_redis, init_redis


async def run_max_bot(bot) -> None:
    # 1. Сначала подключаем Redis
    logger.info("[INFO][run_max_bot] Подключаем Redis")
    await init_redis()
    logger.info("[INFO][run_max_bot] Регистрируем router")
    bot.add_router(router)
    
    
    import aiomax.buttons

    original_from_json = aiomax.buttons.CallbackButton.from_json

    def patched_from_json(data):
        if "intent" not in data:
            data["intent"] = "default"  # подставляем значение по умолчанию
        return original_from_json(data)

    aiomax.buttons.CallbackButton.from_json = patched_from_json
    logger.info("🚀 Запускаем MAX-бота...")
    logger.info("[INFO][run_max_bot] Стартуем бот")
    try:
        bot.run()
    finally:
        # 3. При остановке (Ctrl+C) корректно закрываем Redis
        await close_redis()


@bot.on_ready()
async def send_commands():
    logger.info("[INFO][send_commands] Устанавливаем команды")
    await bot.patch_me(commands=[
        BotCommand('start', 'Начало работы с ботом'),
        BotCommand('my_progress', 'Мой прогресс'),
        BotCommand('rating', 'Рейтинг'),
        BotCommand('export_stats', 'Статистика'),
        BotCommand('home', 'Главное меню'),
        BotCommand('change_status', 'Сменить статус')
    ])

if __name__ == "__main__":
    # run_max_bot(bot)
    
    
    
    print("���пуск бота...")
    
    # 2. Запускаем асинхронную функцию через asyncio.run
    # Это создаст цикл событий, запустит бота и дождется его завершения
    asyncio.run(run_max_bot(bot))
    
    print("👋 Бот остановлен.")
