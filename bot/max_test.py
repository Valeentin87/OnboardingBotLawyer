"""
Тестовый запуск MAX-бота.
Запускать отдельно: python max_test.py
"""
import asyncio
import logging
import aiomax
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

MAX_TOKEN = os.getenv("MAX_BOT_TOKEN")

bot = aiomax.Bot(MAX_TOKEN, default_format="markdown")


@bot.on_bot_start()
async def on_start(pd: aiomax.BotStartPayload):
    """Срабатывает когда пользователь нажимает 'Начать' в MAX"""
    await pd.send(
        "👋 Привет! Я **FPS Онбординг**.\n\n"
        "Бот работает корректно ✅\n\n"
        "Скоро здесь будет полный курс обучения."
    )


@bot.on_command("start")
async def on_command_start(ctx: aiomax.CommandContext):
    """Обработчик команды /start"""
    await ctx.reply(
        "✅ Команда /start получена.\n"
        f"Ваш ID в MAX: `{ctx.user.user_id}`"
    )


@bot.on_message()
async def echo(message: aiomax.Message):
    """Эхо — отвечает на любое сообщение"""
    await message.reply(
        f"📨 Вы написали: {message.content}\n\n"
        "_(Это тестовый режим, эхо-ответ)_"
    )


if __name__ == "__main__":
    print("🚀 MAX-бот запускается...")
    bot.run()