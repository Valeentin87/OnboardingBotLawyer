import asyncio
import json
import redis.asyncio as redis  # <-- Важно: импортируем именно asyncio модуль
from aiomax.fsm import FSMCursor
#from aiomax import Bot, Dispatcher

# --- КОНФИГУРАЦИЯ ---
TOKEN = "YOUR_BOT_TOKEN"
REDIS_URL = "redis://localhost"

# Глобальная переменная для клиента Redis
redis_client = None

async def init_redis():
    """Инициализирует соединение с Redis. Вызывается при старте бота."""
    global redis_client
  
    # from_url работает точно так же
    redis_client = await redis.from_url("redis://localhost", decode_responses=True)
    print("✅ Redis подключен!")

async def close_redis():
    """Закрывает соединение при остановке бота."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        print("❌ Redis отключен")

# --- ФУНКЦИИ РАБОТЫ С СОСТОЯНИЕМ (CURSOR) ---

async def save_cursor(user_id: int, cursor: FSMCursor = None, extra_data: dict | None = None):
    """Сохраняет курсор в Redis с TTL 7 дней (604800 секунд)."""
    if not redis_client:
        raise RuntimeError("Redis не инициализирован!")
    
    key = f"bot:cursor:{user_id}"
        
    payload = {"cursor": cursor}
    
    payload.setdefault('data', {})
    
    if extra_data:
        payload["data"].update(**extra_data)
    
    ttl_seconds = 7 * 24 * 60 * 60  # 7 дней - безопасно и достаточно долго
    await redis_client.setex(key, ttl_seconds, json.dumps(payload))

async def load_cursor(user_id: int):
    """Загружает курсор из Redis. Возвращает None, если нет записи."""
    if not redis_client:
        return None
        
    key = f"bot:cursor:{user_id}"
    raw_data = await redis_client.get(key)
    print(f'{raw_data=}')
    
    if not raw_data:
        return None
    
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return None

# --- ЛОГИКА БОТА ---

# dp = Dispatcher()
# bot = Bot(token=TOKEN)

# @dp.command("start")
# async def cmd_start(ctx):
#     user_id = ctx.from_user.id
#     # При старте можно сбросить состояние или оставить старое
#     # Здесь мы просто показываем приветствие. 
#     # Старое состояние подхватится автоматически при первом нажатии кнопки.
#     await ctx.reply(
#         "Привет! Нажми кнопку ниже, чтобы начать навигацию.",
#         keyboard=create_keyboard(0)
#     )

# def create_keyboard(current_cursor: int):
#     from aiomax.types import CallbackButton, KeyboardBuilder
#     kb = KeyboardBuilder()
    
#     # Кнопка "Вперед" кодирует действие, но реальное состояние мы берем из БД
#     # Это страховка: если БД недоступна, кнопка все равно имеет смысл
#     kb.add(CallbackButton(text="➡️ Дальше", callback_data=f"nav:next:{current_cursor}"))
    
#     if current_cursor > 0:
#         kb.add(CallbackButton(text="↩️ Назад", callback_data=f"nav:prev:{current_cursor}"))
        
#     return kb.build()

# @dp.callback_query(lambda c: c.data.startswith("nav:"))
# async def handle_navigation(callback):
#     user_id = callback.from_user.id
#     action, direction, current_cursor_str = callback.data.split(":")
#     current_cursor = int(current_cursor_str)
    
#     # 1. ПЫТАЕМСЯ ЗАГРУЗИТЬ РЕАЛЬНОЕ СОСТОЯНИЕ ИЗ БД
#     state = await load_cursor(user_id)
    
#     # Если в БД есть состояние, используем его. Иначе используем то, что пришло в кнопке (страховка)
#     effective_cursor = state["cursor"] if state else current_cursor
    
#     # 2. ВЫЧИСЛЯЕМ НОВОЕ СОСТОЯНИЕ
#     new_cursor = effective_cursor + 1 if direction == "next" else effective_cursor - 1
    
#     # Корректировка границ (чтобы не ушел в минус)
#     if new_cursor < 0:
#         new_cursor = 0
        
#     # 3. СОХРАНЯЕМ ОБНОВЛЕННОЕ СОСТОЯНИЕ В БД
#     await save_cursor(user_id, new_cursor)
    
#     # 4. РЕДАКТИРУЕМ СООБЩЕНИЕ (или отправляем новое, если редактирование не удалось)
#     try:
#         await callback.message.edit_text(
#             f"Вы на шаге: {new_cursor}.\n(Реальное состояние восстановлено из БД)",
#             keyboard=create_keyboard(new_cursor)
#         )
#     except Exception as e:
#         # Если сообщение удалено пользователем или истекло, просто отправляем новое
#         await callback.message.answer(
#             f"Шаг обновлен: {new_cursor}. (Предыдущее сообщение недоступно)",
#             keyboard=create_keyboard(new_cursor)
#         )
        
#     await callback.answer()

# # --- ТОЧКА ВХОДА ---
# async def main():
#     # 1. Сначала подключаем Redis
#     await init_redis()
    
#     try:
#         # 2. Запускаем бота
#         await bot.run(dp)
#     finally:
#         # 3. При остановке (Ctrl+C) корректно закрываем Redis
#         await close_redis()

# if __name__ == "__main__":
#     asyncio.run(main())
