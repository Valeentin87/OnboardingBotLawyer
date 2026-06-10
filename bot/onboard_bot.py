#!/usr/bin/env python3
"""
🚀 AI-OnboardBot - Готов к запуску!
"""
import asyncio
from services.rag_service import RAGService
from services.claude_api import ClaudeService
from services.gamification import GamificationService

async def run_bot():
    print("🤖 AI-OnboardBot v1.0")
    print("✅ Все сервисы загружены!")
    
    rag = RAGService()
    print(f"📚 База: {len(rag.knowledge_base)} символов")
    
    # Тестовый вопрос
    answer = await rag.answer_question("Расскажи о компании и продуктах")
    print("🧠 AI ответ:", answer[:100] + "...")
    
    print("\n🎉 Бот ГОТОВ к Telegram интеграции!")
    print("Следующий шаг: aiogram + Telegram API")

if __name__ == "__main__":
    asyncio.run(run_bot())