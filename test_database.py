import asyncio
from bot.database import create_tables, get_or_create_user

async def test_db():
    print("🔄 Создание таблиц...")
    await create_tables()
    print("✅ Таблицы созданы!")
    
    print("🔄 Создание тестового пользователя...")
    user = await get_or_create_user(999999999, "testuser", "Test User")
    print(f"✅ Пользователь создан: ID={user.id}, XP={user.total_xp}")

asyncio.run(test_db())