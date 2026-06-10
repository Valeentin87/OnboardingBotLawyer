import asyncio
import os

from services.rag_service import RAGService

print("🔍 Диагностика...")

# Тест 1: структура
print("1. Файлы services:", len(os.listdir("services")))
print("2. База знаний:", os.path.exists("materials/knowledge_base"))

# Тест 2: RAG без импортов
try:
    exec(open("services/rag_service.py").read())
    rag = RAGService()
    print("3. RAG база:", len(rag.knowledge_base), "символов")
except Exception as e:
    print("RAG ошибка:", e)

print("✅ Диагностика готова!")