import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import load_config
from datetime import datetime
from docx import Document
from difflib import SequenceMatcher
import unicodedata
import re
#import logging
import services.gigachat_api as GiAPI
from bot.adapters.max.create_bot import logger
#from services.gigachat_api import GigaChatService


#logging.basicConfig(level=logging.INFO)



BLOCKS_MAP = {
    'block_1_product.docx': {
        'name': 'Блок 1: Продукт',
        'keywords': [
            'стекло', 'стёкла', 'стеклопакет', 'остекление', 'стеклянный',
            'огнестойкий', 'огнестойкость', 'противопожарный', 'пожарный',
            'E-15', 'E-30', 'E-45', 'E-60',
            'EIW', 'EIW-15', 'EIW-30', 'EIW-45', 'EIW-60', 'EIW-90',
            'EIWS', 'EIWS-15', 'EIWS-30', 'EIWS-60',
            'профиль', 'рама', 'рамка', 'импост', 'штапик', 'уплотнитель',
            'EPDM', 'монтаж', 'монтажный', 'установка', 'крепление',
            'конструкция', 'система', 'серия',
            'ГОСТ', '-123', 'норматив', 'норма', 'сертификат', 'испытание',
            'класс огнестойкости', 'предел', 'протокол', 'лицензия',
            'UV', 'ультрафиолет', 'светопропускание', 'теплопотеря',
            'RAL', 'цвет', 'покраска', 'анодирование', 'порошок',
            'продукт', 'продукция', 'ассортимент', 'линейка', 'модель',
            'характеристика', 'параметр', 'спецификация', 'преимущество',
            'отличие', 'разница', 'чем отличается', 'что такое',
            'размер', 'ширина', 'высота', 'толщина', 'вес', 'масса',
            '45', '65', '-45', '-65', '-50300',
        ],
    },
    'block_2_client.docx': {
        'name': 'Блок 2: Клиент',
        'keywords': [
            'клиент', 'клиенты', 'заказчик', 'покупатель', 'потребитель',
            'B2B', 'корпоративный', 'бизнес-клиент',
            'застройщик', 'девелопер', 'строительная компания', 'строитель',
            'архитектор', 'проектировщик', 'проектная организация',
            'дизайнер', 'интерьер', 'объект',
            'аудитория', 'целевая аудитория', 'сегмент', 'сегментация',
            'портрет', 'профиль клиента', 'ЛПР', 'лицо принимающее решение',
            'ЛВР', 'ЛФР', 'влиятель',
            'лид', 'лиды', 'источник', 'источники лидов', 'канал',
            'входящий', 'исходящий', 'холодный', 'тёплый',
            'реклама', 'рекомендация', 'партнёр',
            '44-ФЗ', '223-ФЗ', 'закупка', 'государственный',
            'аукцион', 'конкурс', 'котировка', 'госзаказ',
            'CHAMP', 'квалификация', 'квалифицировать', 'воронка',
            'бюджет', 'полномочия', 'потребность', 'срок',
            'прогрев', 'цикл сделки',
            'потенциальный', 'целевой', 'нецелевой',
            'боль клиента', 'мотив', 'интерес',
        ],
    },
    'block_3_sales_technology.docx': {
        'name': 'Блок 3: Технология продаж',
        'keywords': [
            'продажа', 'продажи', 'продавать', 'этап', 'этапы',
            'технология продаж', 'воронка продаж', 'процесс продажи',
            'звонок', 'холодный звонок', 'первый звонок',
            'скрипт', 'скрипты', 'речевой модуль', 'фраза', 'реплика',
            'встреча', 'переговоры', 'презентация', 'демонстрация',
            'КП', 'коммерческое предложение', 'предложение', 'оффер',
            'возражение', 'возражения', 'работа с возражениями',
            'отказ', 'не интересно', 'дорого', 'подумаю',
            'обработка', 'аргумент', 'контраргумент',
            'закрытие', 'дожим', 'следующий шаг', 'договор',
            'счёт', 'оплата', 'аванс', 'предоплата',
            'письмо', 'email', 'почта', 'мессенджер',
            'переписка', 'коммуникация', 'напоминание',
            'кейс', 'пример', 'опыт', 'Luciano', 'Foros', 'IT-Park',
        ],
    },
    'block_4_glass.docx': {
        'name': 'Блок 4: Расчёт стекла',
        'keywords': [
            'расчёт', 'рассчитать', 'посчитать', 'считать', 'формула',
            'калькулятор', 'быстрый расчёт', 'расчёт стекла',
            '4-16-4', '4-10-4', '4-14-4', '4-10-4-10-4', '4-14-4-14-4',
            'однокамерный', 'двухкамерный', 'трёхкамерный',
            'камера', 'дистанционная рамка',
            'Stopsol', 'Phoenix', 'Comfort', 'AGC', 'Float',
            'солнцезащитное', 'энергосберегающее', 'зеркальное',
            'матовое', 'Matt', 'Mattelux', 'zak', 'закалённое',
            'ламинированное', 'триплекс',
            'аргон', 'Ar', 'аргоновое', 'инертный газ',
            'площадь', 'метраж', 'квадрат', 'кв.м',
            'Excel', 'таблица', 'шаблон', 'файл расчёта', 'ZAPOLNENIE',
            'скачать', 'ссылка', 'диск', 'Яндекс диск',
            'стоимость', 'цена', 'прайс', 'сколько стоит',
            # 'стекло' намеренно убрано — оно есть в блоке 1,
            # при запросе про стекло будут активированы оба блока
        ],
    },
    'block_5_b24.docx': {
        'name': 'Блок 5: Битрикс24',
        'keywords': [
            'Битрикс', 'Битрикс24', 'Bitrix', 'Bitrix24', 'b24', 'CRM',
            'crm-система', 'корпоративный портал',
            'лид CRM', 'сделка', 'сделки', 'контакт',
            'карточка', 'карточка сделки', 'карточка клиента',
            'воронка CRM', 'стадия', 'этап воронки', 'статус сделки',
            'задача', 'задачи', 'дело', 'активность',
            'напоминание CRM', 'уведомление CRM',
            'отчёт CRM', 'конверсия CRM',
            'rusprofile', 'rusprofile.ru', 'проверка компании',
            'автоматизация', 'роботы', 'триггеры', 'бизнес-процесс',
            'pipeline', 'канбан',
            'интерфейс', 'как найти', 'где находится',
            'урок', 'видео', 'обучение CRM', 'инструкция CRM',
        ],
    },
    'block_6_pbi.docx': {
        'name': 'Блок 6: Power BI',
        'keywords': [
            'Power BI', 'PowerBI', 'power bi', 'пауэр би', 'BI',
            'бизнес-аналитика', 'аналитика',
            'дашборд', 'dashboard', 'отчёт BI',
            'визуализация', 'диаграмма',
            'KPI', 'показатель', 'метрика', 'индикатор',
            '11-й день', '51-й день', '91-й день',
            '11 день', '51 день', '91 день',
            'выручка', 'оборот', 'план', 'факт', 'выполнение плана',
            'конверсия', 'средний чек', 'количество сделок',
            'фильтр', 'срез', 'период', 'диапазон',
            'доступ', 'обновление данных',
            'как открыть', 'как смотреть', 'как пользоваться Power BI',
        ],
    }
}


class RAGService:
    """RAG для AI-чата - отвечает на основе базы знаний"""
    
    
    def __init__(self):
        try:
            logger.info(f'[INFO][RAGService][__init__] Создаем экземпляр класса RAGService')
            config = load_config()
            # Определяем абсолютный путь от корня проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.kb_path = os.path.join(base_dir, 'materials', 'knowledge_base')
            
            # Создаём папку если её нет
            os.makedirs(self.kb_path, exist_ok=True)
            
            print(f"📁 Путь к базе знаний: {self.kb_path}")
            #self.knowledge_base = self._load_knowledge()
            
            self.blocks = self._load_all_blocks()
            self.knowledge_base = '\n\n'.join(self.blocks.values())
        except Exception as e:
            logger.error(f'[ERROR][RAGService][__init__] Произошла ошибка при создании экземпляра класса RAGService: {e}')
    
    
    def _aggressive_clean(self, text: str) -> str:
        """
        МАКСИМАЛЬНО агрессивная очистка текста сразу при загрузке из docx
        """
        try:
            #logger.info(f'[INFO][RAGService][_aggressive_clean]  к очистке данных, взятых из базы')
            if not text:
                return text
            
            # Нормализуем Unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Убираем combining characters
            text = ''.join(char for char in text if not unicodedata.combining(char))
            
            # Список ВСЕХ проблемных символов для удаления
            remove_chars = [
                '\xad', '\u00ad',  # Soft hyphen
                '\u200b', '\u200c', '\u200d',  # Zero-width chars
                '\ufeff', '\u2060',  # BOM and word joiner
                '\u00a0', '\u202f', '\u2009',  # Various spaces
            ]
            
            for char in remove_chars:
                text = text.replace(char, '')
            
            # Заменяем типографские символы
            replacements = {
                '\u2013': '-', '\u2014': '-',  # Dashes
                '\u2018': "'", '\u2019': "'", '\u201a': "'",  # Quotes
                '\u201c': '"', '\u201d': '"', '\u201e': '"',
                '\u2026': '...', '\u2022': '*',  # Ellipsis and bullet
            }
            
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            # Оставляем только безопасные символы: ASCII + кириллица + базовые знаки
            clean = []
            for char in text:
                code = ord(char)
                if (32 <= code <= 126) or (0x0400 <= code <= 0x04FF) or char in '\n\r\t ':
                    clean.append(char)
            
            text = ''.join(clean)
            
            # Убираем множественные пробелы
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\n\n+', '\n\n', text)
            
            return text.strip()
        
        except Exception as e:
            logger.error(f'[ERROR][RAGService][_aggressive_clean] Произошла ошибка при очистке информации, взятой из базы: {e}')
            
    
    def _load_docx(self, filepath: str) -> str:
        """
        Загружает содержимое .docx файла с НЕМЕДЛЕННОЙ очисткой
        """
        try:
            logger.info(f'[INFO][RAGService][_load_docx] Стартовал')
            doc = Document(filepath)
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    # Очищаем СРАЗУ при загрузке
                    cleaned = self._aggressive_clean(text)
                    if cleaned:
                        paragraphs.append(cleaned)
            
            result = "\n\n".join(paragraphs)
            
            # Дополнительная проверка на проблемные символы
            if '\xad' in result:
                print("⚠️ Найден \\xad после очистки, удаляю принудительно")
                result = result.replace('\xad', '')
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка чтения .docx файла {filepath}: {e}")
            logger.error(f'[ERROR][RAGService][_load_docx] Произошла ошибка {filepath}: {e}')
            return f"[Ошибка загрузки docx файла]"
    
    
    def _load_all_blocks(self) -> dict:
        try:
            logger.info(f'[INFO][RAGService][_load_all_blocks] Стартовал')
            blocks = {}
            for filename in BLOCKS_MAP.keys():
                filepath = os.path.join(self.kb_path, filename)
                if not os.path.exists(filepath):
                    print(f"⚠️ Файл не найден: {filepath}")
                    continue
                content = self._load_docx(filepath)
                if content and '[Ошибка' not in content:
                    section_name = BLOCKS_MAP[filename]['name'].upper()
                    blocks[filename] = f"=== {section_name} ===\n{content}"
                    print(f"✅ Загружен: {filename} ({len(content)} символов)")
                    logger.info(f'✅ Загружен: {filename} ({len(content)} символов)')
                else:
                    print(f"⚠️ Пустой или ошибка: {filename}")
                    logger.warning(f"⚠️ Пустой или ошибка: {filename}")
            return blocks
        except Exception as e:
            logger.error(f'[ERROR][RAGService][_load_all_blocks] Произошла ошибка {e}')
            return {}
    
    
    # Логика работы по нечеткому совпадению
    def _fuzzy_match(self, word: str, keyword: str, threshold: float = 0.80) -> bool:
        """
        Проверяет нечёткое совпадение слова из вопроса с ключевым словом.
        Возвращает True, если схожесть >= threshold (80% по умолчанию).
        Примеры: 'стёкла' → 'стекло', 'рассчитать' → 'расчёт',
                 'возражения' → 'возражение'.
        """
        try:
            #logger.info(f'[INFO][RAGService][_fuzzy_match] {word=} {keyword=}')
            ratio = SequenceMatcher(None, word.lower(), keyword[0].lower()).ratio()
            return ratio >= threshold
        except Exception as e:
            logger.error(f'[ERROR][RAGService][_fuzzy_match] Произошла ошибка {e}')
            
    
    
    # ------- Маршрутизация --------
    def _route_question(self, question: str) -> list:
        """
        Трёхуровневая маршрутизация:

        Уровень 1 — точное вхождение (substring match), вес = 2.
        Уровень 2 — нечёткое совпадение слова из вопроса с однословным
                    ключевым словом (SequenceMatcher >= 80%), вес = 1.

        Возвращает СПИСОК всех блоков, где score > 0.
        Если список пуст — система читает всю базу знаний (fallback).

        Таким образом:
        - слово найдено только в 1 блоке  → возвращает [блок1]
        - слово найдено в 2+ блоках       → возвращает [блок1, блок2, ...]
        - совпадений нет                  → возвращает []
        """
        try:
            logger.info(f'[INFO][RAGService][_route_question] Стартовал')
            question_lower = question.lower()
            # Разбиваем вопрос на отдельные слова для нечёткого поиска
            question_words = re.findall(r'[\w\u0400-\u04ff]+', question_lower)

            scores = {}  # {filename: score}

            for filename, meta in BLOCKS_MAP.items():
                if filename not in self.blocks:
                    continue

                block_score = 0
                for keyword in meta['keywords']:
                    #logger.info(f'[INFO][RAGService][_route_question] {keyword=}')
                    kw_lower = keyword.lower()

                    # Уровень 1: точное вхождение подстроки
                    #logger.info(f'[INFO][RAGService][_route_question] Уровень 1: точное вхождение подстроки, проверка')
                    if kw_lower in question_lower:
                        block_score += 2
                        logger.info(f'[INFO][RAGService][_route_question] Уровень 1: ЕСТЬ точное вхождение подстроки, добавляем этот блок и переходим к следующему')
                        continue

                    # Уровень 2: нечёткое совпадение (только для однословных keywords)
                    #logger.info(f'[INFO][RAGService][_route_question] Уровень 2: нечёткое совпадение (только для однословных keywords). ПРОВЕРКА')
                    kw_words = re.findall(r'[\w\u0400-\u04ff]+', kw_lower)
                    if len(kw_words) == 1:
                        for q_word in question_words:
                            if self._fuzzy_match(q_word, kw_words):
                                block_score += 1
                                #logger.info(f'[INFO][RAGService][_route_question] одно совпадение - на keyword достаточно')
                                break  # одно совпадение на keyword достаточно

                if block_score > 0:
                    scores[filename] = block_score

            if not scores:
                logger.warning(f'[INFO][RAGService][_route_question] Совпадений не найдено → читаю всю базу знаний')
                print("⚪ Совпадений не найдено → читаю всю базу знаний")
                return []

            # Возвращаем ВСЕ блоки с ненулевым score, сортируем по убыванию
            matched = sorted(scores.keys(), key=lambda f: scores[f], reverse=True)
            names = ', '.join(BLOCKS_MAP[f]['name'] for f in matched)
            logger.info(f"[INFO][RAGService][_route_question] Маршрут: '{question[:60]}' → [{names}] (scores: {scores})")
            print(f"🎯 Маршрут: '{question[:60]}' → [{names}] (scores: {scores})")
            return matched
        except Exception as e:
            logger.error(f'[ERROR][RAGService][_route_question] Произошла ошибка {e}')
            return []
    
    
    # Основной метод
    async def answer_question(self, question: str) -> str:
        """
        Умный RAG:
        1. _route_question возвращает список блоков (1, 2+ или пусто)
        2. Объединяем тексты всех найденных блоков → один запрос к GigaChat
        3. Если блоков нет → читаем всю базу (fallback)
        """
        try:
            logger.info(f'[INFO][RAGService][answer_question] Стартовал')
            if not self.blocks:
                return "❌ База знаний пока не загружена."

            giga = GiAPI.GigaChatService()
            target_blocks = self._route_question(question)

            if target_blocks:
                combined_text = '\n\n'.join(
                    self.blocks[f] for f in target_blocks if f in self.blocks
                )
                block_names = ', '.join(BLOCKS_MAP[f]['name'] for f in target_blocks)
                token_est = len(combined_text) // 4
                print(f"📖 Читаю блок(и): {block_names} (~{token_est} токенов)")

                try:
                    return await giga.answer_with_context(
                        question=question,
                        knowledge_base=combined_text
                    )
                except Exception as e:
                    print(f"❌ Ошибка при чтении [{block_names}]: {e}")

            print(f"📚 Читаю всю базу знаний ({len(self.knowledge_base)} символов)...")
            try:
                return await giga.answer_with_context(
                    question=question,
                    knowledge_base=self.knowledge_base
                )
            except Exception as e:
                logger.error(f'[ERROR][RAGService][answer_question] Произошла ошибка {e}')
                print(f"❌ Ошибка RAGService.answer_question (full KB): {e}")
                return "❌ Произошла ошибка при обработке запроса."
        except Exception as e:
            logger.error(f'[ERROR][RAGService][answer_question] Произошла ошибка {e}')
            return "❌ Произошла ошибка при обработке запроса."
    
    #  Вспомогательные методы
    def reload_knowledge(self):
        self.blocks = self._load_all_blocks()
        self.knowledge_base = '\n\n'.join(self.blocks.values())
        kb_size = len(self.knowledge_base)
        print(f"🔄 База знаний перезагружена. Размер: {kb_size} символов")
        return kb_size

    
    def add_content(self, content: str, filename: str = "additional_info.txt"):
        if not filename.endswith('.txt'):
            print("⚠️ Можно добавлять контент только в .txt файлы")
            return False
        filepath = os.path.join(self.kb_path, filename)
        os.makedirs(self.kb_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"[{timestamp}]\n{content}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания файла: {e}")
            return False

    def get_stats(self) -> dict:
        return {
            'total_size': len(self.knowledge_base),
            'is_loaded': bool(self.blocks),
            'blocks_loaded': list(self.blocks.keys()),
            'has_block1': 'block_1_product.docx' in self.blocks,
            'has_block2': 'block_2_client.docx' in self.blocks,
            'has_block3': 'block_3_sales_technology.docx' in self.blocks,
            'has_block4': 'block_4_glass.docx' in self.blocks,
            'has_block5': 'block_5_b24.docx' in self.blocks,
            'has_block6': 'block_6_pbi.docx' in self.blocks,
        }
    
    
    # ✅ ИЗМЕНЕНО: загружает все файлы из списка и объединяет в одну базу знаний
    def _load_knowledge(self) -> str:
        """Загружает базу знаний из нескольких .docx файлов ПОЛНОСТЬЮ"""

        filenames = [
            'block_1_product.docx',
            'block_2_client.docx',
            'block_3_sales_technology.docx',
            'block_4_glass.docx',
            'block_5_b24.docx',
            'block_6_pbi.docx'
        ]

        sections = []

        for filename in filenames:
            filepath = os.path.join(self.kb_path, filename)

            if not os.path.exists(filepath):
                print(f"⚠️ Файл не найден, пропускаю: {filepath}")
                continue

            try:
                file_content = self._load_docx(filepath)

                if file_content and "[Ошибка" not in file_content:
                    # Добавляем заголовок раздела
                    section_name = filename.replace('.docx', '').replace('_', ' ').upper()
                    result = f"=== {section_name} ===\n{file_content}"

                    # Финальная проверка - нет ли проблемных символов
                    problem_count = sum(1 for char in result if ord(char) == 0xad)
                    if problem_count > 0:
                        print(f"⚠️ Обнаружено {problem_count} символов \\xad, очищаю...")
                        result = result.replace('\xad', '').replace('\u00ad', '')

                    print(f"✅ Загружен файл: {filename} ({len(file_content)} символов)")
                    sections.append(result)
                else:
                    print(f"⚠️ Файл пустой или ошибка: {filename}")

            except Exception as e:
                print(f"❌ Ошибка чтения {filename}: {e}")

        if not sections:
            print("❌ Ни один файл базы знаний не загружен")
            return "База знаний пока не загружена."

        combined = "\n\n".join(sections)
        print(f"✅ База знаний собрана: {len(combined)} символов из {len(sections)} файлов")
        return combined
    
    
            
if __name__ == '__main__':
    
    import asyncio
    rag_service = RAGService()
    answer = asyncio.run(rag_service.answer_question("Расскажи про триггеры и шаблоны"))
    logger.info(f'Ответ на вопрос: {answer}')
    
    
