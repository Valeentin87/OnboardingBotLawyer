from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
# from bot.config import load_config
from typing import Dict, Any
import json
import re
import os, sys
import unicodedata
from dotenv import load_dotenv
#import logging
from bot.adapters.max.create_bot import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import RAGService

#logging.basicConfig(level = logging.INFO)


class GigaChatService:
    def __init__(self):
        load_dotenv()
        #config = load_config()
        AUTH_KEY = os.getenv('AUTHORIZATION_KEY')
        TYPE_SCOPE = os.getenv('TYPE_SCOPE')
        #credentials = str(config.gigachat_credentials).strip()
        credentials = str(AUTH_KEY).strip()
        credentials = ''.join(c for c in credentials if c.isalnum() or c in '-_=+/')
        print(f"🔑 GigaChat credentials готов (длина: {len(credentials)} символов)")
        self.credentials = credentials
        self.scope = TYPE_SCOPE
        #self.scope = getattr(config, 'gigachat_scope', 'GIGACHAT_API_PERS')
        #self.model = "GigaChat-Max"
        self.model = 'GigaChat-2-Max'
        logger.info(f'[INFO][GigaChatService] Экземпляр класса GigaChatService успешно создан')

    
    def _clean_text(self, text: str) -> str:
        if not text:
            return text
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(char for char in text if not unicodedata.combining(char))
        for char in ['\xad', '\u00ad', '\u200b', '\u200c', '\u200d', '\ufeff', '\u2060']:
            text = text.replace(char, '')
        text = text.replace('\xa0', ' ').replace('\u202f', ' ').replace('\u2009', ' ')
        replacements = {
            '\u2013': '-', '\u2014': '-',
            '\u2018': "'", '\u2019': "'", '\u201a': "'",
            '\u201c': '"', '\u201d': '"', '\u201e': '"',
            '\u2026': '...', '\u2022': '*',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        safe = []
        for char in text:
            code = ord(char)
            if 32 <= code <= 126 or 0x0400 <= code <= 0x04FF or char in '\n\r\t ':
                safe.append(char)
        text = ''.join(safe)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        return text.strip()

    def _remove_markdown(self, text: str) -> str:
        if not text:
            return text
        text = re.sub(r'#+\s+', '', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        return text.strip()

    async def answer_with_context(self, question: str, knowledge_base: str) -> str:
        question = self._clean_text(question)
        knowledge_base = self._clean_text(knowledge_base)

        # system_prompt = (
        #     "Ты AI-ассистент компании по производству противопожарных систем. "
        #     "Твоя задача - помогать новым сотрудникам, отвечая на их вопросы ТОЛЬКО на основе базы знаний компании.\n\n"
        #     "СТРОГИЕ ПРАВИЛА:\n"
        #     "1. Используй ТОЛЬКО информацию из базы знаний ниже\n"
        #     "2. ЗАПРЕЩЕНО использовать внешние знания или придумывать информацию\n"
        #     "3. Если есть прямая цитата - используй её дословно\n"
        #     "4. Если точной цитаты нет, но информация есть - сформулируй ответ своими словами\n"
        #     "5. Если информации нет в базе - честно скажи об этом\n"
        #     "6. Отвечай кратко, по делу, профессионально на русском языке"
        # )
        
        system_prompt = (
                    "Ты AI‑ассистент компании по производству противопожарных систем. "
                    "Твоя задача — помогать новым сотрудникам, отвечая на их вопросы ТОЛЬКО на основе базы знаний компании.\n\n"
                    "СТРОГИЕ ПРАВИЛА:\n"
                    "1. Используй ТОЛЬКО информацию из базы знаний ниже\n"
                    "2. ЗАПРЕЩЕНО использовать внешние знания или придумывать информацию\n"
                    "3. Если есть прямая цитата — используй её дословно\n"
                    "4. Если точной цитаты нет, но информация есть — сформулируй ответ своими словами\n"
                    "5. Если информации нет в базе — честно скажи об этом\n"
                    "6. Отвечай кратко, по делу, профессионально на русском языке\n\n"
                    "КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ К ФОРМАТИРОВАНИЮ (ОБЯЗАТЕЛЬНО ВЫПОЛНЯТЬ):\n"
                    "• Для выделения заголовков смысловых блоков используй полужирное начертание в Markdown — оборачивай текст в двойные звёздочки: Текст заголовка\n"
                    "• Примеры заголовков блоков: Ссылка на материалы, Прямая цитата из базы знаний, Что вы найдёте в материалах, Результат изучения, Инструкция по установке и т. д.\n"
                    "• Все перечисления оформляй как маркированный список в Markdown с использованием символа «•» в начале каждой строки:\n"
                    "• Пункт 1\n"
                    "• Пункт 2\n"
                    "• Пункт 3\n"
                    "• Если описываешь последовательность действий или этапов, используй нумерованный список в Markdown:\n"
                    "1. Шаг 1\n"
                    "2. Шаг 2\n"
                    "3. Шаг 3\n"
                    "• Ссылки оставляй в обычном виде, без дополнительного форматирования\n"
                    "• Прямые цитаты заключай в кавычки и не изменяй формулировку\n"
                    "• Каждый смысловой блок начинай с новой строки\n"
                    "• Перед началом списка делай перевод строки\n"
                    "• Не используй другие виды форматирования (курсив, подчёркивание и т. п.), если это не указано в инструкции\n"
                    "• Фразу: Ознакомиться с материалами можно здесь: всегда обрамляй ** слева и ** справа, чтобы она всегда выводилась полужирным начертанием\n"
                    "• Фразу: Ознакомиться с материалами можно здесь : если она следует после фразы: Ссылка на материалы : не применяй\n"
                    )
        
        # user_prompt = (
        #     "=== БАЗА ЗНАНИЙ КОМПАНИИ ===\n"
        #     f"{knowledge_base}\n\n"
        #     "=== ВОПРОС СОТРУДНИКА ===\n"
        #     f"{question}\n\n"
        #     "Проанализируй базу знаний и ответь на вопрос. "
        #     "Используй прямые цитаты если возможно. Если информации нет - так и скажи."
        # )
        
        user_prompt = (
            "=== БАЗА ЗНАНИЙ КОМПАНИИ ===\n"
            f"{knowledge_base}\n\n"
            "=== ВОПРОС СОТРУДНИКА ===\n"
            f"{question}\n\n"
            "Проанализируй базу знаний и ответь на вопрос. При составлении ответа:\n"
            "1. Строго соблюдай требования к форматированию из system_prompt\n"
            "2. Вставляй прямые цитаты дословно в соответствующих смысловых блоках\n"
            "3. Оформляй списки согласно правилам Markdown\n"
            "4. Проверь, что все заголовки блоков выделены двойными звёздочками\n"
            "5. Если нужной информации нет в базе знаний, ответь одной фразой: «Информации по данному вопросу в базе знаний нет»\n"
            "Не добавляй никаких комментариев или пояснений сверх того, что требуется по структуре."
            )

        try:
            async with GigaChat(
                credentials=self.credentials,
                scope=self.scope,
                model=self.model,
                verify_ssl_certs=False
                # max_tokens=32768,  # максимальный для GigaChat 2 Max
                # temperature=0.2,
            ) as giga:
                response = await giga.achat(Chat(
                    model=self.model,
                    messages=[
                        Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                        Messages(role=MessagesRole.USER, content=user_prompt),
                    ],
                    max_tokens=32768,
                    temperature=0.2
                ))
                answer = response.choices[0].message.content.strip()

            logger.info(f'[INFO][GigaChatService][answer_with_context]{answer=}')
            #answer = self._remove_markdown(answer)
            if len(answer) < 10:
                return "❌ Информация по вашему вопросу не найдена в базе знаний."
            return answer

        except Exception as e:
            print(f"❌ Ошибка GigaChatService.answer_with_context: {e}")
            import traceback
            traceback.print_exc()
            return "❌ Произошла ошибка при обработке запроса."

    
    async def evaluate_answer(self, user_answer: str, ideal_answer: str,
                               question: str = "") -> Dict[str, Any]:
        user_answer = self._clean_text(user_answer)
        ideal_answer = self._clean_text(ideal_answer)
        question = self._clean_text(question)

        
        prompt = (
            "Ты эксперт по оценке ответов новых сотрудников компании по производству "
            "противопожарных систем.\n\n"
            f"Вопрос: {question}\n\n"
            f"Эталонный ответ: {ideal_answer}\n\n"
            f"Ответ сотрудника: {user_answer}\n\n"
            "Оцени ответ по шкале от 1 до 10.\n"
            "• 9-10: Отличный, все ключевые моменты раскрыты\n"
            "• 7-8: Хороший, основные моменты упомянуты\n"
            "• 5-6: Удовлетворительно, есть пробелы\n"
            "• 1-4: Слабый, многое упущено\n\n"
            'Верни СТРОГО в формате JSON:\n'
            '{"score": число от 1 до 10, "feedback": "комментарий до 150 символов"}'
        )

        try:
            async with GigaChat(
                credentials=self.credentials,
                scope=self.scope,
                model=self.model,
                verify_ssl_certs=False,
                # max_tokens=2048,  # ответ оценки всегда короткий JSON
                # temperature=0.3,
            ) as giga:
                response = await giga.achat(Chat(
                    model=self.model,
                    messages=[Messages(role=MessagesRole.USER, content=prompt)],
                    max_tokens=2048,
                    temperature=0.3
                ))
                result_text = response.choices[0].message.content.strip()

            try:
                json_match = re.search(r'\{[^}]+\}', result_text)
                if json_match:
                    result_json = json.loads(json_match.group())
                    score = float(result_json.get('score', 7.0))
                    feedback = result_json.get('feedback', 'Ответ принят')
                else:
                    raise ValueError("JSON не найден")
            except (json.JSONDecodeError, ValueError):
                numbers = re.findall(r'\b([1-9]|10)(?:\.\d+)?\b', result_text)
                score = float(numbers) if numbers else 7.0
                feedback = result_text[:150]

            score = max(1.0, min(10.0, score))
            logger.info(f"[INFO][GigaChatService][evaluate_answer] 'score': {score}, 'feedback': {feedback}, 'passed': {score >= 7.0}")
            return {'score': score, 'feedback': feedback, 'passed': score >= 7.0}

        except Exception as e:
            print(f"❌ Ошибка GigaChatService.evaluate_answer: {e}")
            logger.error(f'[ERROR][GigaChatService][evaluate_answer] Произошла ошибка {e}')
            return {'score': 7.0, 'feedback': 'Оценка временно недоступна.', 'passed': True}
        



if __name__ == '__main__':
    import asyncio
    
    gigaChatService = GigaChatService()
    rag = RAGService()
    
    result = asyncio.run(gigaChatService.answer_with_context("Что есть у тебя в базе?", knowledge_base=rag.knowledge_base))
    logger.info(f'{result=}')
    
    
    
    