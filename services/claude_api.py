import anthropic
from bot.config import load_config
from typing import Dict, Any
import json
import re
import sys
import os
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ClaudeService:
    def __init__(self):
        config = load_config()
        
        # Очищаем API key от проблемных символов
        api_key = str(config.claude_api_key)
        
        # Удаляем мягкие переносы и другие невидимые символы
        api_key = api_key.replace('\xad', '')
        api_key = api_key.replace('\u00ad', '')
        api_key = api_key.replace('\u200b', '')
        api_key = api_key.replace(' ', '')
        api_key = api_key.replace('\n', '')
        api_key = api_key.replace('\r', '')
        api_key = api_key.replace('\t', '')
        
        # Оставляем только разрешённые символы (буквы, цифры, дефис)
        api_key = ''.join(char for char in api_key if char.isalnum() or char == '-')
        
        print(f"🔑 API key очищен и готов (длина: {len(api_key)} символов)")
        
        # Создаём клиент с очищенным ключом
        self.client = anthropic.Anthropic(
            api_key=config.claude_api_key, #api_key,
            max_retries=2,
            timeout=60.0
        )
    
    def _clean_text(self, text: str) -> str:
        """
        МАКСИМАЛЬНО агрессивная очистка - используем unicodedata
        """
        if not text:
            return text
        
        # Нормализуем Unicode (разложение составных символов)
        text = unicodedata.normalize('NFKD', text)
        
        # Убираем все combining characters (диакритические знаки и т.д.)
        text = ''.join(char for char in text if not unicodedata.combining(char))
        
        # Удаляем известные проблемные символы
        dangerous_chars = [
            '\xad',      # Soft hyphen
            '\u00ad',    # Soft hyphen (другая запись)
            '\u200b',    # Zero width space
            '\u200c',    # Zero width non-joiner
            '\u200d',    # Zero width joiner
            '\ufeff',    # Zero width no-break space (BOM)
            '\u2060',    # Word joiner
        ]
        
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Заменяем специальные пробелы на обычные
        text = text.replace('\xa0', ' ')      # Non-breaking space
        text = text.replace('\u202f', ' ')    # Narrow no-break space
        text = text.replace('\u2009', ' ')    # Thin space
        
        # Заменяем типографские знаки на простые ASCII
        replacements = {
            '\u2013': '-',    # En dash
            '\u2014': '-',    # Em dash
            '\u2018': "'",    # Left single quote
            '\u2019': "'",    # Right single quote
            '\u201a': "'",    # Single low quote
            '\u201c': '"',    # Left double quote
            '\u201d': '"',    # Right double quote
            '\u201e': '"',    # Double low quote
            '\u2026': '...',  # Ellipsis
            '\u2022': '*',    # Bullet
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Оставляем только безопасные символы
        safe_chars = []
        for char in text:
            code = ord(char)
            # ASCII printable
            if 32 <= code <= 126:
                safe_chars.append(char)
            # Кириллица
            elif 0x0400 <= code <= 0x04FF:
                safe_chars.append(char)
            # Переносы строк и табуляция
            elif char in '\n\r\t':
                safe_chars.append(char)
            # Пробел (на всякий случай)
            elif char == ' ':
                safe_chars.append(char)
        
        text = ''.join(safe_chars)
        
        # Убираем множественные пробелы и переносы
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        
        return text.strip()
    
    def _verify_clean(self, text: str) -> str:
        """
        Финальная проверка - убеждаемся что можно закодировать
        """
        if not text:
            return text
        
        # Убираем всё что не ASCII и не кириллица
        clean = []
        for char in text:
            try:
                code = ord(char)
                # Проверяем что символ безопасен
                if code < 128 or (0x0400 <= code <= 0x04FF) or char in '\n\r\t ':
                    clean.append(char)
            except:
                pass
        
        return ''.join(clean)
    
    def _remove_markdown(self, text: str) -> str:
        """
        Удаляет Markdown разметку из текста
        """
        if not text:
            return text
        
        # Убираем заголовки (## Заголовок или ### Заголовок)
        text = re.sub(r'#+\s+', '', text)
        
        # Убираем жирный текст (**текст** или __текст__)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Убираем курсив (*текст* или _текст_)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Убираем маркеры списков в начале строки (- пункт или * пункт)
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
        
        # Убираем нумерованные списки (1. пункт, 2. пункт)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Убираем код в обратных кавычках (`код` или ```код```)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        return text.strip()
    
    async def answer_with_context(self, question: str, knowledge_base: str) -> str:
        """
        Отвечает на вопрос на основе базы знаний.
        """
        # Двухэтапная очистка
        question = self._clean_text(question)
        question = self._verify_clean(question)
        
        knowledge_base = self._clean_text(knowledge_base)
        knowledge_base = self._verify_clean(knowledge_base)
        
        print(f"🔍 Длина очищенной базы знаний: {len(knowledge_base)} символов")
        
        # Принудительная очистка от \xad
        knowledge_base = knowledge_base.replace('\xad', '').replace('\u00ad', '')
        question = question.replace('\xad', '').replace('\u00ad', '')
        
        system_prompt = (
            "Ты AI-ассистент компании по производству противопожарных систем. "
            "Твоя задача - помогать новым сотрудникам, отвечая на их вопросы ТОЛЬКО на основе базы знаний компании.\n\n"
            "СТРОГИЕ ПРАВИЛА:\n"
            "1. Используй ТОЛЬКО информацию из базы знаний ниже\n"
            "2. ЗАПРЕЩЕНО использовать внешние знания или придумывать информацию\n"
            "3. Если есть прямая цитата - используй её дословно\n"
            "4. Если точной цитаты нет, но информация есть - сформулируй ответ своими словами на основе базы\n"
            "5. Если информации вообще нет в базе - честно скажи об этом\n"
            "6. Отвечай кратко, по делу, профессионально на русском языке"
        )
        
        user_prompt = (
            "=== БАЗА ЗНАНИЙ КОМПАНИИ ===\n"
            f"{knowledge_base}\n\n"
            "=== ВОПРОС СОТРУДНИКА ===\n"
            f"{question}\n\n"
            "Проанализируй базу знаний и ответь на вопрос. "
            "Используй прямые цитаты если возможно, или сформулируй ответ на основе имеющейся информации. "
            "Если информации нет - так и скажи."
        )
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514", #"claude-3-5-sonnet-20240620",
                max_tokens=4096,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            answer = response.content[0].text.strip()
            
            # Убираем Markdown разметку
            answer = self._remove_markdown(answer)
            
            if len(answer) < 10:
                return (
                    "❌ Не удалось найти информацию по вашему вопросу в базе знаний.\n\n"
                    "Обратитесь к администратору"
                )
            
            if any(phrase in answer.lower() for phrase in [
                'нет информации', 
                'не содержит', 
                'не найдено',
                'отсутствует информация'
            ]):
                return (
                    f"{answer}\n\n"
                    "Для получения дополнительной информации обратитесь к администратору."
                )
            
            return answer
            
        except Exception as e:
            print(f"❌ Ошибка ClaudeService.answer_with_context: {e}")
            import traceback
            traceback.print_exc()
            
            return (
                "❌ Произошла ошибка при обработке вашего вопроса.\n\n"
                "Обратитесь к администратору."
            )
    
    async def evaluate_answer(self, user_answer: str, ideal_answer: str, question: str = "") -> Dict[str, Any]:
        """
        Оценивает ответ пользователя для тестов по шкале 1-10.
        """
        # Агрессивная очистка
        user_answer = self._verify_clean(self._clean_text(user_answer))
        ideal_answer = self._verify_clean(self._clean_text(ideal_answer))
        question = self._verify_clean(self._clean_text(question))
        
        prompt = (
            "Ты эксперт по оценке ответов новых сотрудников компании по производству противопожарных систем.\n\n"
            f"Вопрос: {question}\n\n"
            f"Эталонный ответ: {ideal_answer}\n\n"
            f"Ответ сотрудника: {user_answer}\n\n"
            "Оцени ответ по шкале от 1 до 10, где:\n"
            "• 9-10: Отличный ответ, все ключевые моменты раскрыты\n"
            "• 7-8: Хороший ответ, упомянуты основные моменты\n"
            "• 5-6: Удовлетворительно, но есть пробелы\n"
            "• 1-4: Слабый ответ, многое упущено\n\n"
            "Верни результат СТРОГО в формате JSON:\n"
            '{"score": число от 1 до 10, "feedback": "короткий комментарий на русском (до 150 символов)"}'
        )
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip()
            
            try:
                json_match = re.search(r'\{[^}]+\}', result_text)
                if json_match:
                    result_json = json.loads(json_match.group())
                    score = float(result_json.get('score', 7.0))
                    feedback = result_json.get('feedback', 'Ответ принят')
                else:
                    raise ValueError("JSON не найден в ответе")
            except (json.JSONDecodeError, ValueError):
                numbers = re.findall(r'\b([1-9]|10)(?:\.\d+)?\b', result_text)
                score = float(numbers[0]) if numbers else 7.0
                feedback = result_text[:150]
            
            score = max(1.0, min(10.0, score))
            
            return {
                'score': score,
                'feedback': feedback,
                'passed': score >= 7.0
            }
            
        except Exception as e:
            print(f"❌ Ошибка ClaudeService.evaluate_answer: {e}")
            return {
                'score': 7.0,
                'feedback': 'Ответ принят. Оценка временно недоступна.',
                'passed': True
            }