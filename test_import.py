try:
    from services.claude_api import ClaudeService
    print("✅ Импорт ClaudeService успешен!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    
try:
    from bot.config import load_config
    print("✅ Импорт config успешен!")
except ImportError as e:
    print(f"❌ Ошибка config: {e}")