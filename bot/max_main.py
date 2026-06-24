import os
import sys
import asyncio
import logging

# --- Настройка путей ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Импорты ---
from bot.adapters.max.create_bot import bot, logger
from bot.adapters.max.handlers import router
from services.redis_storage import close_redis, init_redis, save_cursor
from aiomax import BotCommand

# --- ПАТЧ КНОПОК (Выполняется сразу при импорте файла) ---
import aiomax.buttons

original_from_json = aiomax.buttons.CallbackButton.from_json

def patched_from_json(data):
    if "intent" not in data:
        data["intent"] = "default"
    return original_from_json(data)

aiomax.buttons.CallbackButton.from_json = patched_from_json
logger.info("✅ Патч кнопок применен")

# --- Хендлер on_ready ---
@bot.on_ready()
async def send_commands():
    logger.info("[INFO][send_commands] Устанавливаем команды")
    try:
        await bot.patch_me(commands=[
            BotCommand('start', 'Начало работы с ботом'),
            BotCommand('my_progress', 'Мой прогресс'),
            BotCommand('rating', 'Рейтинг'),
            BotCommand('export_stats', 'Статистика'),
            BotCommand('home', 'Главное меню'),
            BotCommand('change_status', 'Сменить статус')
        ])
        logger.info("✅ Команды успешно установлены")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке команд: {e}")

if __name__ == "__main__":
    print("🚀 Подготовка окружения...")
    
    # ЭТАП 1: Инициализация Redis (короткий цикл)
    try:
        asyncio.run(init_redis())
        logger.info("✅ Redis успешно подключен!")
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка: Не удалось подключиться к Redis: {e}")
        sys.exit(1)

    # ЭТАП 2: Регистрация роутеров
    bot.add_router(router)
    logger.info("✅ Роутеры зарегистрированы")

    print("🚀 Запускаем MAX-бота (основной цикл событий)...")
    
    # ЭТАП 3: Запуск бота
    # ВАЖНО: Здесь НЕТ asyncio.run(). Метод bot.run() внутри себя сам создает event loop.
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка работы бота: {e}")
    finally:
        # ЭТАП 4: Корректное закрытие Redis после остановки бота
        logger.info("���крываем соединение с Redis...")
        try:
            # Снова используем короткий asyncio.run для асинхронного закрытия
            asyncio.run(close_redis())
            logger.info("✅ Redis корректно закрыт.")
        except Exception as e:
            # Даже если закрытие Redis упадет с ошибкой, мы не должны блокировать остановку бота
            logger.error(f"⚠️ Не удалось корректно закрыть Redis: {e}")
            # Можно добавить логику повторных попыток или алерт, но сейчас просто логируем
    
    print("👋 Бот остановлен.")
