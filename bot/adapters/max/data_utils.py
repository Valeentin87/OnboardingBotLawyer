import json
import os
import re
#import logging
from datetime import datetime
from bot.adapters.max.create_bot import logger

#logging.basicConfig(level=logging.INFO)

NAME_DATA_FILE = "data/name_surname.json"

def save_reminder(user_id: int, start_date: str, REMINDERS_FILE:str):
    """Сохраняет напоминание в файл"""
    try:
        os.makedirs("data", exist_ok=True)
        
        reminders = {}
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
                reminders = json.load(f)
        
        reminders[str(user_id)] = {
            "start_date": start_date,
            "reminder_sent": False
        }
        
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
            
        logger.info("[save_reminder] Информация о первом рабочем дне успешно сохранена")
        
    except Exception as e:
        logger.error(f"[save_reminder] Произошла ошибка {e}")


def ensure_data_file():
    """Гарантирует существование файла data/name_surname.json с валидным JSON"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(NAME_DATA_FILE):
        with open(NAME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    else:
        # Проверяем, что файл не пустой и содержит валидный JSON
        try:
            with open(NAME_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    # Если файл пустой, записываем пустой словарь
                    with open(NAME_DATA_FILE, 'w', encoding='utf-8') as f_write:
                        json.dump({}, f_write, ensure_ascii=False, indent=4)
                else:
                    # Пробуем распарсить JSON, чтобы убедиться в его валидности
                    json.loads(content)
        except json.JSONDecodeError:
            # Если JSON невалиден, перезаписываем файл
            with open(NAME_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)


def load_user_data():
    """Загрузка данных пользователей из JSON-файла с обработкой ошибок"""
    ensure_data_file()
    try:
        with open(NAME_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Ошибка загрузки данных: {e}. Создаём новый файл.")
        return {}


def save_user_data(data):
    """Сохранение данных пользователей в JSON-файл"""
    with open(NAME_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def validate_name_surname(text):
    """
    Проверка формата «Имя Фамилия»:
    - между именем и фамилией один пробел;
    - имя и фамилия состоят только из букв.
    """
    pattern = r'^[А-Яа-яЁёA-Za-z]+[ А-Яа-яЁёA-Za-z]+$'
    return re.match(pattern, text) is not None


def format_progress_attempts(attempts: list) -> str:
    """
    Форматирует список попыток прохождения курса в стилизованное сообщение с эмодзи.

    Для попытки с максимальным accuracy_percent добавляет эмодзи кубка слева и справа.

    Args:
        attempts: список словарей с данными о попытках прохождения курса

    Returns:
        Строка с форматированным сообщением
    """
    logger.info('Стартовал')    
    if not attempts:
        return "Нет данных о попытках прохождения курса."

    # Находим максимальный accuracy_percent
    max_accuracy = max(attempt['accuracy_percent'] for attempt in attempts)
    logger.info(f'{max_accuracy=}')

    formatted_blocks = []

    for attempt in attempts:
        # Преобразуем дату в читаемый формат
        date_obj = datetime.fromisoformat(attempt['date_completed'])
        formatted_date =  date_obj.strftime('%d.%m.%Y')  # date_obj.strftime('%d.%m.%Y в %H:%M')

        if attempt["course_name"] == "Обучение по продажам":
            # Формируем блок для одной попытки
            block_lines = [
                f"🗓️ Дата прохождения: {formatted_date}",
                f"✅ Уроков пройдено: {attempt['lessons_completed']} / 43",
                f"📈 Процент правильных ответов: {attempt['accuracy_percent']}%"
            ]
        elif attempt["course_name"] == "Другой сотрудник":
            block_lines = [
                f"🗓️ Дата прохождения: {formatted_date}",
                f"✅ Уроков пройдено: {attempt['lessons_completed']} / 7",
                f"📈 Процент правильных ответов: {attempt['accuracy_percent']}%"
            ]
        elif attempt["course_name"] == "Обучение для юриста":
            block_lines = [
                f"🗓️ Дата прохождения: {formatted_date}",
                f"✅ Уроков пройдено: {attempt['lessons_completed']} / 12",
                f"📈 Процент правильных ответов: {attempt['accuracy_percent']}%"
            ]
            

        block = "\n".join(block_lines)

        # Если это попытка с максимальным accuracy, добавляем кубки
        if attempt['accuracy_percent'] == max_accuracy:
            block = f"🏆 {block} 🏆"

        formatted_blocks.append(block)
    
    
    
    # Объединяем все блоки с двумя переносами строк между ними
    return f"<b>Вот результаты Ваших прохождений обучения по курсу «{attempts[0]['course_name']}»:</b>\n" + "\n\n".join(formatted_blocks)


def get_max_accuracy_item(data):
    """
    Возвращает словарь с максимальным значением 'accuracy_percent' из списка.
    Обрабатывает возможные ошибки: пустой список, отсутствие ключа.
    """
    if not data:
        return None  # или {} — зависит от требований

    try:
        return max(data, key=lambda x: x['accuracy_percent'])
    except KeyError:
        raise KeyError("В одном или нескольких словарях отсутствует ключ 'accuracy_percent'")
    except TypeError:
        raise TypeError("Значения 'accuracy_percent' должны быть числовыми")
