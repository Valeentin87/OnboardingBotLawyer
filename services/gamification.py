import json
import os
from typing import Dict, Any
from datetime import datetime
#import logging
from bot.adapters.max.create_bot import logger


class GamificationService:
    def __init__(self, current_course: str = "Обучение по продажам"):
        self.progress_file = 'data/progress.json'
        self.total_lessons_info = {
            "Обучение по продажам": 43,
            "Другой сотрудник": 7,
            "Обучение для юриста": 12
        }
        self.current_course = current_course
        os.makedirs('data', exist_ok=True)
    
    def _load_data(self) -> Dict:
        """Загружает данные из файла прогресса"""
        logger.info(f'[INFO][GamificationService][_load_data] Загружаем данные из файла прогресса')
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                logger.info(f'[INFO][GamificationService][_load_data] данные из файла прогресса успешно загружены')
                return json.load(f)
        except Exception as e:
            logger.error(f'[INFO][GamificationService][_load_data] Произошла ошибка {e=}')
            return {}
    
    def _save_data(self, data: Dict):
        """Сохраняет данные в файл прогресса"""
        logger.info(f'[INFO][GamificationService][_save_data] Загружаем данные из файла прогресса')
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    '''
    def get_user_progress(self, user_id: int, course_name: str = "Обучение по продажам") -> Dict[str, Any]:
        """Получить прогресс пользователя по конкретному курсу"""
        logger.info(f'[INFO][GamificationService][get_user_progress] Получаем прогресс пользователя по курсу: {course_name}')
        data = self._load_data()
        user_data = data.get(str(user_id), {})
        courses = user_data.get('courses', {})
        
        # Дефолтная структура для курса
        default_course = {
            'lessons_completed': 0,
            'total_lessons': 43,  
            'correct_answers': 0,
            'total_answers': 0,
            'accuracy_percent': 0.0
        }
        
        return courses.get(course_name, default_course)
    '''
    
    def get_user_progress(self, user_id: int, course_name: str = "Обучение по продажам") -> Any:
        """
        Получить прогресс пользователя по конкретному курсу.

        Логика:
        1. Если у пользователя есть ключ 'completed_attempts', вернуть отсортированный
        список попыток (по дате в порядке возрастания).
        2. Иначе вернуть кортеж: (last_activity, курс_данные).
        """
        logger.info(f'[INFO][GamificationService][get_user_progress] Получаем прогресс пользователя {user_id} по курсу: {course_name}')

        data = self._load_data()
        user_key = str(user_id)
        user_data = data.get(user_key, {})

        # Проверяем наличие completed_attempts
        completed_attempts = user_data.get('completed_attempts', [])
        
        # Фильтруем все попытки прохождения по требуемому названию курса
        completed_attempts_by_course = list(filter(lambda c: c.get("course_name") == course_name, completed_attempts)) if completed_attempts else [] 

        if completed_attempts_by_course:
            # Сортируем попытки по дате в порядке возрастания
            sorted_attempts = sorted(
                completed_attempts_by_course,
                key=lambda attempt: attempt['date_completed']
            )
            logger.info(f'[INFO][GamificationService][get_user_progress] '
                    f'Для пользователя {user_id} найдены {len(sorted_attempts)} попыток, возвращаем отсортированный список')
            
            return sorted_attempts

        else:
            # Берём last_activity и данные курса
            last_activity = user_data.get('user_info', {}).get('last_activity')

            courses = user_data.get('courses', {})
            course_data = courses.get(course_name)

            # Если данных курса нет, используем дефолтную структуру
            if not course_data:
                logger.warning(f'[WARNING][GamificationService][get_user_progress] '
                        f'Для пользователя {user_id} не найдены данные курса {course_name}, используем дефолтные значения')
                
                total_lessons = self.total_lessons_info[self.current_course]
                
                logger.info(f'{total_lessons=}')
                
                course_data = {
                    'lessons_completed': 0,
                    'total_lessons': total_lessons,
                    'correct_answers': 0,
                    'total_answers': 0,
                    'accuracy_percent': 0.0
                }

            result = (last_activity, course_data)
            logger.info(f'[INFO][GamificationService][get_user_progress] '
                f'Для пользователя {user_id} возвращаем кортеж (last_activity, данные курса)')
            return result

    
    async def update_lesson_progress(
        self, 
        user_id: int, 
        course_name: str,
        correct_count: int, 
        total_count: int,
        lesson_id: str,
        user_data: dict = None
    ) -> Dict[str, Any]:
        """
        Обновить прогресс после прохождения теста раздела
        
        Args:
            user_id: ID пользователя
            course_name: Название курса
            correct_count: Количество правильных ответов
            total_count: Общее количество вопросов
            lesson_id: Уникальный ID урока (например, "section_1", "final_test")
            user_data: Данные пользователя (username, first_name, last_name)
        """
        logger.info(f'[INFO][GamificationService][update_lesson_progress] Обновляем прогресс пользователя по курсу: {course_name}')
        # Загружаем все данные
        data = self._load_data()
        
        # Инициализируем структуру пользователя
        user_key = str(user_id)
        logger.info(f'[INFO][GamificationService][update_lesson_progress] {data=} {user_key=}')
        
        if user_key not in data:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] Пользователь: {user_id} - новый, добавляем информацию по нему')
            data[user_key] = {
                'user_info': {},
                'courses': {},
                'lesson_results': {}
            }
        
        # Обновляем информацию о пользователе
        if user_data:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] Информация о пользователе: {user_data}')
            data[user_key]['user_info'] = {
                'user_id': user_id,
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'last_activity': datetime.now().isoformat()
            }
        
        # Инициализируем структуру курса
        if 'courses' not in data[user_key]:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] Инициализируем структуру курса')
            data[user_key]['courses'] = {}
        
        if 'lesson_results' not in data[user_key]:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] Инициализируем lesson_results пустым словарем')
            data[user_key]['lesson_results'] = {}
        
        # Получаем текущий прогресс по курсу
        logger.info(f'[INFO][GamificationService][update_lesson_progress] Получаем текущий прогресс по курсу {course_name=}')
        if course_name not in data[user_key]['courses']:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] Пользователь еще не проходил этот курс')
            total_lessons = self.total_lessons_info[self.current_course]
            data[user_key]['courses'][course_name] = {
                'lessons_completed': 0,
                'total_lessons': total_lessons,
                'correct_answers': 0,
                'total_answers': 0,
                'accuracy_percent': 0.0
            }
        
        course_progress = data[user_key]['courses'][course_name]
        logger.info(f'[INFO][GamificationService][update_lesson_progress] {course_progress=}')
        
        # Проверяем, был ли урок уже пройден
        info_dict = data[user_key]['lesson_results']
        course_result_flag = info_dict.setdefault(course_name, {})
        is_first_attempt = lesson_id not in data[user_key]['lesson_results'][course_name]
        
        if not is_first_attempt:
            logger.info(f'[INFO][GamificationService][update_lesson_progress] повторная попытка — вычитаем старый результат')
            # Если повторная попытка — вычитаем старый результат
            old_result = data[user_key]['lesson_results'][course_name][lesson_id]
            old_correct = old_result.get('correct_count', 0)
            old_total = old_result.get('total_count', 0)
            
            course_progress['correct_answers'] -= old_correct
            course_progress['total_answers'] -= old_total
        else:
            # Если первая попытка — увеличиваем счётчик уроков
            logger.info(f'[INFO][GamificationService][update_lesson_progress] первая попытка — увеличиваем счётчик уроков')
            course_progress['lessons_completed'] += 1
        
        # Обновляем статистику (добавляем новый результат)
        course_progress['correct_answers'] += correct_count
        course_progress['total_answers'] += total_count
        logger.info(f'[INFO][GamificationService][update_lesson_progress] Обновляем статистику (добавляем новый результат)')
        
        # Пересчитываем средний процент правильных ответов
        logger.info(f'[INFO][GamificationService][update_lesson_progress] Пересчитываем средний процент правильных ответов')
        if course_progress['total_answers'] > 0:
            accuracy = (course_progress['correct_answers'] / course_progress['total_answers']) * 100
            course_progress['accuracy_percent'] = round(accuracy, 1)
        else:
            course_progress['accuracy_percent'] = 0.0
        
        # Сохраняем результат урока
        data[user_key]['lesson_results'][course_name][lesson_id] = {
            'correct_count': correct_count,
            'total_count': total_count,
            'accuracy': round((correct_count / total_count * 100), 1) if total_count > 0 else 0
        }
        
        # Сохраняем
        self._save_data(data)
        logger.info(f'[INFO][GamificationService][update_lesson_progress] Завершение работы метода. {course_progress=}')
        
        return course_progress
    
    '''    
        def get_all_users_progress(self, course_name: str = "Обучение по продажам") -> list:
            """Получить прогресс всех пользователей для рейтинга"""
            data = self._load_data()
            
            leaderboard = []
            for user_id, user_data in data.items():
                courses = user_data.get('courses', {})
                user_info = user_data.get('user_info', {})
                
                if course_name in courses:
                    course_data = courses[course_name]
                    leaderboard.append({
                        'user_id': int(user_id),
                        'username': user_info.get('username'),
                        'first_name': user_info.get('first_name'),
                        'last_name': user_info.get('last_name'),
                        'lessons_completed': course_data['lessons_completed'],
                        'accuracy_percent': course_data['accuracy_percent']
                    })
            
            # Сортируем по проценту правильных ответов (убывание)
            leaderboard.sort(key=lambda x: x['accuracy_percent'], reverse=True)
            return leaderboard
    '''
    
    
    def get_all_users_progress(self, course_name: str = "Обучение по продажам") -> list:
        """
        Получить прогресс всех пользователей для рейтинга.

        Логика:
        1. Если у пользователя есть непустой список completed_attempts, берём попытку
        с максимальным accuracy_percent.
        2. Иначе берём данные из courses[course_name].
        3. Сортируем по accuracy_percent (убывание).
        """
        logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                f'Получаем рейтинг пользователей по курсу: {course_name}')

        data = self._load_data()
        leaderboard = []

        for user_id, user_data in data.items():
            user_info = user_data.get('user_info', {})
            courses = user_data.get('courses', {})

            # Проверяем наличие и непустоту completed_attempts
            logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                f'Проверяем наличие и непустоту completed_attempts')
            completed_attempts = user_data.get('completed_attempts', [])
            
            completed_attempts_by_course = list(filter(lambda c: c.get("course_name") == course_name, completed_attempts)) if completed_attempts else [] 
            
            best_progress = None

            if completed_attempts_by_course:  # Если список не пустой
                logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                f'Находим попытку с максимальным accuracy_percent')
                # Находим попытку с максимальным accuracy_percent
                best_attempt = max(
                    completed_attempts_by_course,
                    key=lambda attempt: attempt['accuracy_percent']
                )
                best_progress = {
                    'lessons_completed': best_attempt['lessons_completed'],  # В completed_attempts нет данных о пройденных уроках
                    'accuracy_percent': best_attempt['accuracy_percent']
                }
                logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                        f'Для пользователя {user_id} использована лучшая попытка: {best_attempt["accuracy_percent"]}%')
            else:
                # Берём данные из курса
                if course_name in courses:
                    course_data = courses[course_name]
                    logger.info(f'[INFO][GamificationService][get_all_users_progress] {course_data=}')
                    best_progress = {
                        'lessons_completed': course_data['lessons_completed'],
                        'accuracy_percent': course_data['accuracy_percent']
                    }
                    logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                        f'Для пользователя {user_id} использованы данные курса: {course_data["accuracy_percent"]}%')
                else:
                    # Пропускаем пользователя, если у него нет данных ни по attempts, ни по курсу
                    logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                        f'Пользователь {user_id} не имеет данных ни по attempts, ни по курсу')
                    continue

            # Добавляем пользователя в рейтинг
            leaderboard.append({
                'user_id': int(user_id),
                'username': user_info.get('username'),
                'first_name': user_info.get('first_name'),
                'last_name': user_info.get('last_name'),
                'lessons_completed': best_progress['lessons_completed'],
                'accuracy_percent': best_progress['accuracy_percent']
            })

        # Сортируем по проценту правильных ответов (убывание)
        leaderboard.sort(key=lambda x: x['accuracy_percent'], reverse=True)
        logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                f'Рейтинг сформирован. Всего пользователей: {len(leaderboard)}')

        return leaderboard
    
    
    def get_all_users_progress_new(self, course_name: str = "Обучение по продажам") -> dict:
        """
        Получить прогресс всех пользователей для рейтинга.

        Логика:
        1. Если у пользователя есть непустой список completed_attempts, берём результаты всех попыток оттуда
        2. Далее берём данные из courses[course_name].
        3. Сортируем по дате прохождения.
        """
        logger.info(f'[INFO][GamificationService][get_all_users_progress_new] '
                f'Получаем рейтинг пользователей по курсу: {course_name}')

        data = self._load_data()
        leaderboard = []

        for user_id, user_data in data.items():
            leaderboard_list = []
            user_info = user_data.get('user_info', {})
            courses = user_data.get('courses', {})

            # Проверяем наличие и непустоту completed_attempts
            logger.info(f'[INFO][GamificationService][get_all_users_progress_new] '
                f'Проверяем наличие и непустоту completed_attempts')
            completed_attempts = user_data.get('completed_attempts', [])
            
            if completed_attempts:  # Если список не пустой
                logger.info(f'[INFO][GamificationService][get_all_users_progress_new] '
                f'Добавляем значения попыток полного прохождения курса по ключу {user_id}')
                for attemp in completed_attempts:
                    leaderboard_list.append(
                        {
                           'date_attemp': attemp['date_completed'],
                           'lessons_completed': attemp['lessons_completed'],  
                            'accuracy_percent': attemp['accuracy_percent'] 
                        }
                    )
            else:
                # Берём данные из курса
                if course_name in courses:
                    course_data = courses[course_name]
                    logger.info(f'[INFO][GamificationService][get_all_users_progress_new] {course_data=}')
                    leaderboard_list.append(
                        {
                           'date_attemp': user_info['last_activity'],
                           'lessons_completed': course_data['lessons_completed'],  
                            'accuracy_percent': course_data['accuracy_percent'] 
                        }
                    )
                    logger.info(f'[INFO][GamificationService][get_all_users_progress_new] '
                        f'Для пользователя {user_id} использованы данные курса: {course_data["accuracy_percent"]}%')
                else:
                    # Пропускаем пользователя, если у него нет данных ни по attempts, ни по курсу
                    logger.info(f'[INFO][GamificationService][get_all_users_progress] '
                        f'Пользователь {user_id} не имеет данных ни по attempts, ни по курсу')
                    continue

            # Добавляем пользователя в рейтинг
            leaderboard.append({
                'user_id': int(user_id),
                'username': user_info.get('username'),
                'first_name': user_info.get('first_name'),
                'last_name': user_info.get('last_name'),
                'leaderboard_list': leaderboard_list
            })

        # Сортируем по проценту правильных ответов (убывание)
        logger.info(f'[INFO][GamificationService][get_all_users_progress] {leaderboard=} '
                f'Подготовлена информация для формирования статистики. Всего пользователей: {len(leaderboard)}')

        return leaderboard


    
    
    def mark_video_section_viewed(
            self,
            user_id: int,
            video_section_id: str,
            course_name: str = "Обучение по продажам",
        ) -> Dict[str, Any]:
        """
        Добавляет отметку о просмотре видео‑раздела в lesson_results.

        Args:
            user_id: ID пользователя
            course_name: Название курса (по умолчанию «Обучение по продажам»)
            video_section_id: Уникальный ID видео‑раздела 

        Returns:
            Обновлённый прогресс пользователя по курсу
        """
        logger.info(f'[INFO][GamificationService][mark_video_section_viewed] '
                f'Добавляем отметку о просмотре для пользователя {user_id}, раздел: {video_section_id}')

        # Загружаем все данные
        data = self._load_data()
        user_key = str(user_id)

        # Добавляем отметку о просмотре
        data[user_key]['lesson_results'][course_name][video_section_id] = {
            'viewed_flag': 1
        }
        logger.info(f'[INFO][GamificationService][mark_video_section_viewed] '
                f'Отметка о просмотре добавлена: {video_section_id}')

        # Сохраняем изменения
        self._save_data(data)

        # Возвращаем обновлённый прогресс
        return data[user_key]['courses'][course_name]
    
    
    def increment_lessons_completed(
            self,
            user_id: int,
            course_name: str = "Обучение по продажам",
            increment_lesson: int = 0
        ) -> Dict[str, Any]:
        """
        Увеличивает счётчик пройденных уроков на указанное значение.

        Args:
            user_id: ID пользователя
            course_name: Название курса (по умолчанию «Обучение по продажам»)
            increment_lesson: На сколько увеличить счётчик (по умолчанию 0)

        Returns:
            Обновлённый прогресс пользователя по курсу
        """
        if increment_lesson == 0:
            logger.info(f'[INFO][GamificationService][increment_lessons_completed] '
                    f'increment_lesson = 0, изменений не требуется для пользователя {user_id}')
            # Возвращаем текущий прогресс без изменений
            return self.get_user_progress(user_id, course_name)

        logger.info(f'[INFO][GamificationService][increment_lessons_completed] '
                f'Увеличиваем счётчик уроков для пользователя {user_id} на {increment_lesson}')

        # Загружаем все данные
        data = self._load_data()
        user_key = str(user_id)

        # Увеличиваем счётчик уроков
        data[user_key]['courses'][course_name]['lessons_completed'] += increment_lesson
        logger.info(f'[INFO][GamificationService][increment_lessons_completed] '
                f'Счётчик уроков увеличен. Новое значение: '
                f'{data[user_key]["courses"][course_name]["lessons_completed"]}')

        # Сохраняем изменения
        self._save_data(data)

        # Возвращаем обновлённый прогресс
        return data[user_key]['courses'][course_name]

  
    

    def record_course_completion_attempt(
        self,
        user_id: int,
        course_name: str = "Обучение по продажам",
        correct_answers: int = 0,
        total_answers: int = 0
    ) -> Dict[str, Any]:
        """
        Сохраняет историю попыток прохождения всего курса в completed_attempts.
        Каждое выполнение добавляет новую запись, не перезаписывая существующие.

        Args:
            user_id: ID пользователя
            course_name: Название курса (по умолчанию «Обучение по продажам»)
            correct_answers: Количество правильных ответов за курс
            total_answers: Общее количество вопросов за курс

        Returns:
            Словарь с данными текущей попытки и всей истории попыток
        """
        logger.info(f'[INFO][GamificationService][record_course_completion_attempt] '
                f'Сохраняем попытку прохождения курса для пользователя {user_id}, курс: {course_name}')

        # Загружаем все данные
        data = self._load_data()
        user_key = str(user_id)

        # Инициализируем структуру пользователя, если её нет
        if user_key not in data:
            logger.info(f'[INFO][GamificationService][record_course_completion_attempt] '
                    f'Пользователь {user_id} — новый, добавляем базовую структуру')
            data[user_key] = {
                'user_info': {},
                'courses': {},
                'lesson_results': {},
                'completed_attempts': []
            }

        # Инициализируем completed_attempts, если его нет
        if 'completed_attempts' not in data[user_key]:
            data[user_key]['completed_attempts'] = []

        # Рассчитываем процент точности
        accuracy_percent = 0.0
        if total_answers > 0:
            accuracy = (correct_answers / total_answers) * 100
            accuracy_percent = round(accuracy, 1)

        # Создаём запись о попытке
        lessons_completed = 43
        if course_name == 'Другой сотрудник':
            lessons_completed = 7
        elif course_name == 'Обучение для юриста':
            lessons_completed = 12
        else:
            logger.warning("Кажется не корректное название курса обучения, возможно надо поменять на ОБУЧЕНИЕ ПО ПРОДУКТУ")
            
        attempt_record = {
            'date_completed': datetime.now().isoformat(),
            'correct_answers': correct_answers,
            'total_answers': total_answers,
            'accuracy_percent': accuracy_percent,
            'lessons_completed': lessons_completed,
            'course_name': course_name            
        }

        # Добавляем новую попытку в историю (дописываем, не заменяем)
        data[user_key]['completed_attempts'].append(attempt_record)
        logger.info(f'[INFO][GamificationService][record_course_completion_attempt] '
                f'Попытка добавлена в историю. Всего попыток: {len(data[user_key]["completed_attempts"])}')

        # Сохраняем изменения
        self._save_data(data)

        # Возвращаем данные текущей попытки и всей истории
        return {
            'current_attempt': attempt_record,
            'history': data[user_key]['completed_attempts']
        }
        
    
    def get_lessons_completed(
            self,
            user_id: int,
            course_name: str = "Обучение по продажам"
        ) -> int:
        """
        Получает количество пройденных уроков (lessons_completed) для конкретного пользователя и курса.

        Args:
            user_id: ID пользователя
            course_name: Название курса (по умолчанию «Обучение по продажам»)

        Returns:
            int: Количество пройденных уроков. Возвращает 0, если данные отсутствуют.
        """
        logger.info(f'[INFO][GamificationService][get_lessons_completed] '
                f'Получаем количество пройденных уроков для пользователя {user_id}, курс: {course_name}')

        # Загружаем все данные
        data = self._load_data()
        user_key = str(user_id)

        # Проверяем, есть ли пользователь в данных
        if user_key not in data:
            logger.warning(f'[WARNING][GamificationService][get_lessons_completed] '
                    f'Пользователь {user_id} не найден в данных')
            return 0

        # Проверяем, есть ли указанный курс у пользователя
        if course_name not in data[user_key]['courses']:
            logger.warning(f'[WARNING][GamificationService][get_lessons_completed] '
                    f'Курс {course_name} не найден для пользователя {user_id}')
            return 0

        # Получаем количество пройденных уроков
        lessons_completed = data[user_key]['courses'][course_name].get('lessons_completed', 0)

        logger.info(f'[INFO][GamificationService][get_lessons_completed] '
                f'Для пользователя {user_id} по курсу {course_name}: {lessons_completed} пройденных уроков')

        return lessons_completed
    
    
    def get_info_to_exel_for_user(self, user_id:int, education_info:dict, course_name: str = "Обучение по продажам", all_courses_flag: bool = True):
        result_info = {}
        completed_attempts = []
        not_completed_courses = []
        logger.info(f'{education_info=}')
        logger.info(f'{list(education_info.keys())}')
        if 'completed_attempts' in education_info:
            logger.info(f'Информация по завершенным попыткам: {education_info.get('completed_attempts')}')
            for attemp in education_info.get('completed_attempts'):
                logger.info(f'{attemp=}')
                logger.info(f'Название курса: {course_name=}')
                if not all_courses_flag and attemp.get('course_name') == course_name:
                    logger.info(f'Для пользователя {user_id} обнаружили завершенную попытку пройти курс {course_name}')
                    completed_attempts.append({course_name: attemp})
                elif all_courses_flag:
                    course_name = attemp.get('course_name')
                    completed_attempts.append({course_name: attemp})
        
        if 'courses' in education_info:
            for course in education_info.get('courses'):
                if not all_courses_flag:
                    if all([course == course_name, education_info.get('courses')[course]['lessons_completed'] != 0, 
                            education_info.get('courses')[course]['lessons_completed'] != self.total_lessons_info.get(course_name)]):
                        logger.info(f'Для пользователя {user_id} обнаружили не завершенную попытку пройти курс {course_name}')
                        not_completed_courses.append({course: education_info.get('courses')[course]})
                else:
                    #course_name = list(course.keys()[0])
                    logger.info(f'Полученный ключ: {course=}')
                    if all([education_info.get('courses')[course]['lessons_completed'] != 0, 
                            education_info.get('courses')[course]['lessons_completed'] != self.total_lessons_info.get(course)]):
                        logger.info(f'Для пользователя {user_id} обнаружили не завершенную попытку пройти курс {course_name}')
                        not_completed_courses.append({course: education_info.get('courses')[course]})
                    
        
        result_info.update(completed_attemps=completed_attempts, not_completed_courses=not_completed_courses)
        return result_info
    
    def get_all_courses_name(self):
        '''Возвращает названия всех курсов'''
        data = self._load_data()
        
        all_courses_name = []
        
        for user, user_data in data.items():
            for course_name, course_result in user_data.get('courses').items():
                all_courses_name.append(course_name)
        
        return list(set(all_courses_name))
    
    
    def get_full_completed_lessons(self, course_name: str, user_id: int):
        """Возвращает количество полных уроков, завершенных пользователем
        по курсу обучения, переданному в аргументе"""
        try:
            logger.info(f'{course_name=}')
            data = self._load_data()
            
            user_data = data.get(str(user_id))
            logger.info(f'{user_data=}')
            if user_data:
                courses_data = user_data.get("courses")
                logger.info(f'{courses_data=}')
                if courses_data:
                    current_course_data = courses_data.get(course_name)
                else:
                    current_course_data = {}
            else:
                current_course_data = {}
            
            lessons_completed = current_course_data.get("lessons_completed") if current_course_data else 0
            total_lessons = current_course_data.get("lessons_completed") if current_course_data else 0
            
            full_completed_lessons = lessons_completed if total_lessons else None
            logger.info(f'{data=}\n{current_course_data=}\n{full_completed_lessons=}')
            
            return full_completed_lessons
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')
        
        
        
                
    
    
    def reset_user_course_progress(self, user_id: int, course_name: str = "Обучение по продажам") -> Dict[str, Any]:
        """
        Сбрасывает прогресс пользователя по указанному курсу:
        - устанавливает значения lessons_completed, correct_answers и т. д. в 0;
        - очищает словарь lesson_results для этого пользователя.

        Args:
            user_id: ID пользователя
            course_name: Название курса (по умолчанию «Обучение по продажам»)

        Returns:
            Обновлённый прогресс пользователя по курсу
        """
        logger.info(f'[INFO][GamificationService][reset_user_course_progress] '
                f'Сброс прогресса для пользователя {user_id}, курс: {course_name}')

        # Загружаем все данные
        data = self._load_data()
        user_key = str(user_id)
        total_lessons = 43 
        if course_name == "Другой сотрудник":
            total_lessons = 7
        elif course_name == "Обучение для юриста":
            total_lessons = 12
        else:
            logger.warning("Кажется не корректное название курса обучения, возможно надо поменять на ОБУЧЕНИЕ ПО ПРОДУКТУ")

        # Проверяем, существует ли пользователь в данных
        if user_key not in data:
            logger.warning(f'[WARNING][GamificationService][reset_user_course_progress] '
                    f'Пользователь {user_id} не найден в данных')
            return {}

        # Проверяем, есть ли указанный курс у пользователя
        if 'courses' not in data[user_key] or course_name not in data[user_key]['courses']:
            logger.warning(f'[WARNING][GamificationService][reset_user_course_progress] '
                    f'Курс {course_name} не найден для пользователя {user_id}')
            # Инициализируем курс с дефолтными значениями, если его нет
            
            if 'courses' not in data[user_key]:
                data[user_key]['courses'] = {}
            data[user_key]['courses'][course_name] = {
                'lessons_completed': 0,
                'total_lessons': total_lessons,
                'correct_answers': 0,
                'total_answers': 0,
                'accuracy_percent': 0.0
            }
        else:
            # Сбрасываем прогресс по курсу
            data[user_key]['courses'][course_name] = {
                'lessons_completed': 0,
                'total_lessons': total_lessons,
                'correct_answers': 0,
                'total_answers': 0,
                'accuracy_percent': 0.0
            }

        # Очищаем словарь lesson_results
        data[user_key]['lesson_results'][course_name] = {}
        logger.info(f'[INFO][GamificationService][reset_user_course_progress] '
                f'lesson_results очищен для пользователя {user_id} по курсу {course_name}')

        # Сохраняем изменения
        self._save_data(data)

        # Возвращаем обновлённый прогресс
        return data[user_key]['courses'][course_name]

    
if __name__ == '__main__':
    game = GamificationService()
    
    game.get_full_completed_lessons(course_name="Другой сотрудник", user_id=1234)
    
    


