"""
Обработчики для MAX-бота.

Сейчас это слой-адаптер между core/ и конкретной библиотекой MAX (aiomax).
Пока нет реального Bot-объекта, описываем только функции и протокол.
"""

import asyncio
from datetime import datetime, timedelta
import json
import os
from pprint import pprint

from aiomax  import BotStartPayload, Message, Callback, Router, CommandContext, BotCommand
from aiomax.buttons import CallbackButton, KeyboardBuilder
from aiomax.fsm import FSMCursor, FSMStorage
from aiomax.filters import state
from aiomax import bot
#import logging


from bot.adapters.max.data_utils import format_progress_attempts, get_max_accuracy_item, load_user_data, save_reminder, save_user_data, validate_name_surname
from bot.adapters.max.test_utils import get_block_2_test_1_quests, get_block_2_test_2_quests, get_block_2_test_3_quests, get_block_3_test_1_quests, get_block_3_test_2_quests, get_block_3_test_3_quests, get_block_3_test_4_quests, get_block_3_test_5_quests, get_block_3_test_6_quests, get_block_4_test_1_quests, get_block_4_test_2_quests, get_block_4_test_3_quests, get_block_4_test_4_quests, get_final_test_block_1, get_final_test_block_2, get_final_test_block_3, get_final_test_block_4, get_final_test_block_5, get_final_test_block_6, get_final_test_block_7, get_testing_data_1, get_testing_data_2, get_testing_data_3, get_testing_data_4, get_testing_data_5, get_testing_data_6
from bot.adapters.max.utils_FSM import AnotherEmployerStates, OnboardingStates, TrainingStates, UserInfo
from bot.core.onboarding_flow import flow_about_company, flow_another_emp_training_intro, flow_sales_training_intro, flow_start, flow_start_change_kb
from core.content import get_another_emp_intro_text, get_block1_intro_text, get_block1_section1_intro_text, get_block1_section2_intro_text, get_block1_section_3_intro_text, get_block1_section_4_intro_text, get_block1_section_5_intro_text, get_block1_section_6_intro_text, get_block2_intro_text, get_block2_section1_intro_text, get_block2_section_2_intro_text, get_block2_section_3_intro_text, get_block2_section_4_intro_text, get_block3_intro_text, get_block3_section_1_intro_text, get_block3_section_2_intro_text, get_block3_section_3_intro_text, get_block3_section_4_intro_text, get_block3_section_5_intro_text, get_block3_section_6_intro_text, get_block4_intro_text, get_block4_section_1_intro_text, get_block4_section_2_intro_text, get_block4_section_3_intro_text, get_block4_section_4_intro_text, get_block5_intro_text, get_block5_intro_video1, get_block5_intro_video10, get_block5_intro_video11, get_block5_intro_video12, get_block5_intro_video13, get_block5_intro_video14, get_block5_intro_video15, get_block5_intro_video2, get_block5_intro_video3, get_block5_intro_video4, get_block5_intro_video5, get_block5_intro_video6, get_block5_intro_video7, get_block5_intro_video8, get_block5_intro_video9, get_block6_intro_text, get_block6_section_1_intro_text, get_block7_intro_text, get_change_course_text, get_course_intro_text, get_final_another_emp_text, get_final_intro_text, get_first_day_congrats_text, get_first_mess_another_empl, get_reminder_text, get_start_text, get_text_change_department, get_text_change_status, get_text_in_process, get_text_start_final_test_block_1, get_text_start_final_test_block_2, get_text_start_final_test_block_3, get_text_start_final_test_block_4, get_text_start_final_test_block_5, get_text_start_final_test_block_6, get_text_to_final_test_block_1, get_text_to_final_test_block_2, get_text_to_final_test_block_3, get_text_to_final_test_block_4, get_text_to_final_test_block_5, get_text_to_final_test_block_6, get_text_to_final_test_block_7, get_tomorrow_reminder_text, get_training_step_3_text, go_to_test_1_text
from bot.adapters.max.keyboards import change_another_department_kb, change_course_kb, change_course_to_export_stat_kb, change_department_kb, change_status_kb, continue_studying_kb, education_kb, final_start_test_kb, final_test_kb, finish_studying_kb, main_menu_keyboard, main_one_kb, next_to_educ_to_part_kb, next_to_education_kb, start_test_kb, test_abcd_keyboard, variants_questions_kb, yes_no_kb
#from services.claude_api import ClaudeService
from services.ExelStatisticGenerator import ExcelStatisticGenerator
from services.gigachat_api import GigaChatService
from services.debounce import debounce_button_max
from services.gamification import GamificationService
from services.rag_service import RAGService
from bot.adapters.max.create_bot import logger


#logging.basicConfig(level=logging.INFO)

REMINDERS_FILE = "data/reminders.json"
NAME_DATA_FILE = "data/name_surname.json"

COURSES_NAMES = {"Обучение по продажам": 'sales_training',
                 "Другой сотрудник": 'another_employee'}


router = Router()


def get_current_course(cursor: FSMCursor):
    """Возвращает название курса обучения"""
    cursor_data = cursor.get_data()
    if cursor_data:
        return cursor_data.get("current_course")
    else:
        return "Обучение по продажам"

@router.on_button_callback(lambda data: data.payload == "sales_manager")
async def sales_manager_start_handl(ctx: Callback, cursor: FSMCursor):
    """Обработчик нажатия пользователем кнопки МЕНЕДЖЕР ПО ПРОДАЖАМ 
    при выборе курса обучения"""
    await ctx.message.delete()
    
    data = cursor.get_data()
    logger.info(f'{data=}')
    cursor.change_data({"current_course": "Обучение по продажам"})
    await start_command(ctx, cursor)
    
    
@router.on_button_callback(lambda data: data.payload == "another_employer")
async def another_employer_start_handl(ctx: Callback, cursor: FSMCursor):
    """Обработчик нажатия пользователем кнопки ДРУГОЙ СОТРУДНИК 
    при выборе курса обучения"""
    await ctx.message.delete()
    
    data = cursor.get_data()
    logger.info(f'{data=}')
    cursor.change_data({"current_course": "Другой сотрудник"})
    cursor.change_state(AnotherEmployerStates.user_type)
    await start_command(ctx, cursor, user_type = "another_employer")
    


@router.on_button_callback(lambda data: data.payload == "change_course_name")
async def change_course_name_handl(ctx: Callback, cursor: FSMCursor):
    """Обработчик нажатия кнопки ВЫБРАТЬ ДРУГОЙ ОТДЕЛ"""
    await ctx.message.delete()
    cursor.change_data({"current_course" : None})
    cursor.clear_state()
    text = get_change_course_text()
    
    await ctx.send(text=text, keyboard=change_course_kb(), format='markdown')



@router.on_command('change_status')
async def change_status_command_handler(ctx: CommandContext, cursor: FSMCursor):
    """Обработчик команды change_status"""
    try:
        logger.info(f'[INFO][change_status_command_handler] Стартовал change_status_command_handler')
        text = get_text_change_status()
        kb = change_status_kb()
        await ctx.send(text, keyboard = kb)
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')


@router.on_button_callback(lambda data: data.payload in ["new_employer", "upper_qualification"])
async def change_status_handler(ctx: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку НОВЫЙ СОТРУДНИК или ПОВЫШЕНИЕ КВАЛИФИКАЦИИ"""
    try:
        logger.info('Стартовал')
        status_user = ctx.payload
        cursor_data = cursor.get_data()
        cursor_data.update(status_user = status_user)
        cursor.change_data(cursor_data)
        logger.info(f'{status_user=}\n{cursor_data=}')
        text = get_text_change_department()
        kb = change_department_kb()
        await ctx.send(text, keyboard = kb)
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
                 

@router.on_bot_start()
@router.on_command('start')
async def start_command(ctx: CommandContext, cursor: FSMCursor, user_type:str = "manager"):
    """Обработчик команды старт"""
    try:
        logger.info(f'[INFO][start_command] Стартовал')
        user_data = load_user_data()
        user_id = str(ctx.user_id)
        cursor_data = cursor.get_data()
        logger.info(f'[INFO][start_command] {user_id=}')
        if user_id in user_data:
            first_name = user_data[user_id]["first_name"]
            second_name = user_data[user_id]["second_name"]
            logger.info(f'[INFO][start_command] Данные о пользователе уже есть в name_surname.json {user_id=}')
            if not cursor_data:
                logger.info(f'Строка 99')
                await ctx.send(f"Здравствуйте, {first_name} {second_name}!")
            
                
        else:
            # Если информации нет, запрашиваем имя и фамилию
            await ctx.send("Пожалуйста, введите ваше имя и фамилию в формате «Имя Фамилия»")
            cursor.change_state(UserInfo.waiting_for_name_surname)
            return
        
        logger.info(f'[INFO][start_command] Стартовал')
            
        async def change_course_send(text: str):
            await ctx.send(text, keyboard=change_course_kb(), format='markdown')
        
        async def send(text: str, cursor: FSMCursor = cursor):
            state_name = cursor.get_state()
            if state_name == "another_employer":
                await ctx.send(text, keyboard=main_menu_keyboard(educ_button_name = "Обучение по продукту"))
            else:
                await ctx.send(text, keyboard=main_menu_keyboard(educ_button_name = "Обучение по продажам"))

        data = cursor.get_data()
        logger.info(f'{data=}')
        if data:
            if "current_course" in data and data.get("current_course") == "Обучение по продажам":
                course_name = data.get("current_course")
                await flow_start(send, course_name)
                return
            
            if "current_course" in data and data.get("current_course") == "Другой сотрудник":
                cursor.change_state(AnotherEmployerStates.user_type)
                course_name = data.get("current_course")
                await flow_start(send, course_name)
                return
        
        await flow_start_change_kb(change_course_send)
          
    except Exception as e:
        logger.error(f'[ERROR][start_command] Произошла ошибка {e}')





@router.on_message(state(UserInfo.waiting_for_name_surname))
async def process_name_surname(message: Message, cursor: FSMCursor):
    
    text = message.body.text.strip()

    if validate_name_surname(text):
        # Разделяем имя и фамилию
        try:
            first_name, second_name = text.split(' ', 1)
        except ValueError:
            await message.send(
            "Неверный формат. Пожалуйста, введите имя и фамилию в формате «Имя Фамилия», "
            "используя только буквы и один пробел между ними."
        ) 

        # Сохраняем данные пользователя
        user_data = load_user_data()
        user_id = str(message.user_id)
        user_data[user_id] = {
            "first_name": first_name,
            "second_name": second_name
        }
        save_user_data(user_data)

        await message.send(f"Спасибо, {first_name}! Ваши данные сохранены.")
        cursor.clear_state()
        
        async def change_course_send(text: str):
            await message.send(text, keyboard=change_course_kb(), format="html")
        
        # async def send(text: str):
        #     await message.send(text, keyboard=main_menu_keyboard())

        await flow_start_change_kb(change_course_send)
    else:
        await message.send(
            "Неверный формат. Пожалуйста, введите имя и фамилию в формате «Имя Фамилия», "
            "используя только буквы и один пробел между ними."
        )
        

@router.on_command('part2')
async def part2_command(ctx: CommandContext, cursor: FSMCursor):
    """Обработчик команды /part2 - для работы со вторым разделом"""
    try:
        logger.info(f'[INFO][part2_command] Стартовал')
        cursor.clear_state()
        await start_block_2_handler(ctx, cursor)
    except Exception as e:
        logger.error(f'[ERROR][part2_command] Произошла ошибка {e}')
        

@router.on_command('part3')
async def part3_command(ctx: CommandContext, cursor: FSMCursor):
    """Обработчик команды /part3 - для работы с третьим разделом"""
    try:
        logger.info(f'[INFO][part3_command] Стартовал')
        cursor.clear_state()
        await start_block_3_handler(ctx, cursor)
    except Exception as e:
        logger.error(f'[ERROR][part3_command] Произошла ошибка {e}')


@router.on_command('part4')
async def part4_command(ctx: CommandContext, cursor: FSMCursor):
    """Обработчик команды /part4 - для работы с четвёртым разделом"""
    try:
        logger.info(f'[INFO][part4_command] Стартовал')
        cursor.clear_state()
        await start_block_4_handler(ctx, cursor)
    except Exception as e:
        logger.error(f'[ERROR][part4_command] Произошла ошибка {e}')
        

@router.on_button_callback(lambda data: data.payload == 'raiting')
@router.on_command('raiting')
async def raiting_command(ctx: CommandContext | Callback, cursor: FSMCursor):
    """Обработчик команды /raiting - для демонстрации рейтинга обучаемого"""
    try:
        logger.info(f'[INFO][raiting_command] Стартовал')
        cursor.clear_state()
        current_course = get_current_course(cursor)
        
        if isinstance(ctx, Callback):
            await ctx.message.delete()
        
        game = GamificationService(current_course)
              
        course_name = "Обучение по продажам" if current_course != "Другой сотрудник" else "Другой сотрудник"
        logger.info(f'{course_name=}')
        
        # Получаем топ пользователей
        logger.info(f'[INFO][raiting_command] Получаем топ пользователей')
        leaderboard = game.get_all_users_progress(course_name)
        
        if not leaderboard:
            await ctx.send(
                "📊 **Рейтинг пока пуст**\n\n"
                "Пройдите обучение, чтобы попасть в рейтинг!",
                keyboard=main_menu_keyboard(current_course),
                format="markdown"
            )
            return
        
        logger.info(f'[INFO][raiting_command] Находим место текущего пользователя')
        # Находим место текущего пользователя
        user_rank = 0
        user_progress = None
        for i, user_data in enumerate(leaderboard, start=1):
            if user_data['user_id'] == ctx.user_id:
                user_rank = i
                user_progress = user_data
                break
        
        # Формируем текст рейтинга (топ-10)
        if course_name == "Другой сотрудник":
            course_name = "Обучение по продукту"
        rating_text = f"🏆 <b>Рейтинг по курсу</b>\n📚 {course_name}\n\n"
        
        # Показываем топ-10
        for i, user_data in enumerate(leaderboard[:10], start=1):
            logger.info(f'{user_data=}')
            # Эмодзи для топ-3
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            # Отметка для текущего пользователя
            is_current_user = (user_data['user_id'] == ctx.user_id)
            user_marker = " ← Вы" if is_current_user else ""
            
            # Формируем кликабельный username
            username = user_data.get('username')
            user_id = user_data['user_id']
            logger.info(f"[INFO][raiting_command]  {user_id=}")
            
            if username:
                display_name = f'<a href="https://web.max.ru/?id={user_id}">{username}</a>'
            else:
                display_name = f"Пользователь #{user_id}"
                
            completed_lessons = user_data['lessons_completed']
            logger.info(f'{completed_lessons=}') 
            if current_course == 'Другой сотрудник':
                if int(completed_lessons) < 5:
                    completed_lessons = 0
                elif int(completed_lessons) < 10:
                    completed_lessons = 1
                elif int(completed_lessons) < 15:
                    completed_lessons = 2
                elif int(completed_lessons) < 20:
                    completed_lessons = 3
                elif int(completed_lessons) < 25:
                    completed_lessons = 4
                elif int(completed_lessons) < 30:
                    completed_lessons = 5
                elif int(completed_lessons) < 43:
                    completed_lessons = 6
                else:
                    completed_lessons = 7   
            
            
            rating_text += (
                f"{medal}<b>#{i}</b> {display_name} — "
                f"{user_data['accuracy_percent']:.1f}% "
                f"({completed_lessons} уроков){user_marker}\n"
            )
        
        # Если пользователь не в топ-10, показываем его место отдельно
        if user_rank > 10:
            username = user_progress.get('username')
            user_id = user_progress['user_id']
            logger.info(f"[INFO][raiting_command]  {user_id=}")
            completed_lessons = user_progress['lessons_completed']
            logger.info(f'{completed_lessons=}') 
            if current_course == 'Другой сотрудник':
                if int(completed_lessons) < 5:
                    completed_lessons = 0
                elif int(completed_lessons) < 10:
                    completed_lessons = 1
                elif int(completed_lessons) < 15:
                    completed_lessons = 2
                elif int(completed_lessons) < 20:
                    completed_lessons = 3
                elif int(completed_lessons) < 25:
                    completed_lessons = 4
                elif int(completed_lessons) < 30:
                    completed_lessons = 5
                elif int(completed_lessons) < 43:
                    completed_lessons = 6
                else:
                    completed_lessons = 7 
            
            
            if username:
                display_name = f'<a href="https://web.max.ru/?id={user_id}">{username}</a>'
            else:
                display_name = f"Пользователь #{user_id}"
            
            rating_text += f"\n...\n"
            rating_text += (
                f"<b>#{user_rank}</b> {display_name} — "
                f"{user_progress['accuracy_percent']:.1f}% "
                f"({completed_lessons} уроков) ← <b>Вы</b>\n"
            )
        
        # Если пользователь ещё не в рейтинге
        if user_rank == 0:
            rating_text += "\n_Вы ещё не начали обучение. Пройдите первый урок, чтобы попасть в рейтинг!_"
        
        await ctx.send(rating_text, format="html", keyboard=main_menu_keyboard(current_course))
        
    except Exception as e:
        logger.error(f'[ERROR][raiting_command] Произошла ошибка {e}')


FILE_PATH = 'data/statistics.xlsx'


def add_timestamp_to_filename(filename: str = FILE_PATH):
    # Получаем текущую дату и время
    now = datetime.now()
    
    # Форматируем дату и время в нужный вид: ДД_ММ_ГГГГ_time_ЧЧ_ММ
    timestamp = now.strftime("%d_%m_%Y_time_%H_%M")
    
    # Разделяем имя файла и расширение
    if '.' in filename:
        name, extension = filename.rsplit('.', 1)
        new_filename = f"{name}_{timestamp}.{extension}"
    else:
        # Если расширения нет
        new_filename = f"{filename}_{timestamp}"
    
    return new_filename



@router.on_button_callback(lambda data: data.payload == 'all_courses')
async def all_courses_stat_info_handler(ctx: CommandContext, cursor: FSMCursor):
    """Обработчик нажатия на кнопку ПО ВСЕМ КУРСАМ"""
    logger.info(f'Приступаем к формированию статистики прохождения обучения по всем курсам')
    
    game = GamificationService()
    
    data = game._load_data()
    data_to_exel = {}
    logger.info(f'Убираем лишнюю информацию из data - ключи lesson_results и значения по ним')
    
    users_data = {}
    for user, user_data in data.copy().items():
        #del user_data['lesson_results']
        users_data.setdefault(user, user_data)
    pprint(users_data)
    
    logger.info(f'Для каждого пользователя получаем результат прохождения обучения по курсам')
    for user_id, education_info in users_data.items():
        last_first_user_name = f"{education_info.get('user_info')['last_name']} {education_info.get('user_info')['first_name']}"
        if user_id not in data_to_exel:
            data_to_exel.setdefault((user_id, last_first_user_name))
        current_user_result = game.get_info_to_exel_for_user(user_id=int(user_id), education_info=education_info)
        data_to_exel[(user_id, last_first_user_name)] = current_user_result
    
    logger.info(f'{data_to_exel=}')
    pprint(data_to_exel)
    
    excel_gen = ExcelStatisticGenerator(data_to_exel)
    
    file_path = add_timestamp_to_filename()
    
    #excel_gen.generate_excel("data/statistics.xlsx")
    excel_gen.generate_excel(file_path)
    
    if not os.path.exists(file_path):
        await ctx.send(f"❌ Файл {file_path} не найден в папке data.")
        return
    
    try:
        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as file:
            # Отправляем документ в чат
            attachment = await ctx.bot.upload_file(
                file_path
            )
            await ctx.send('Статистика прохождения обучения', attachments=attachment)
        await ctx.send("Для продолжения нажмите ниже", keyboard=main_one_kb())
    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка при отправке файла: {e}")

    
    
    #pprint(data_to_exel)

@router.on_button_callback(lambda data: data.payload.startswith('export_data'))
async def current_course_stat_info_handler(callback: Callback, cursor: FSMCursor):
    course = callback.payload.split('::')[1]
    logger.info(f'{course=}')
        
    course_name = next(key for key, value in COURSES_NAMES.items() if value == course)
    
    logger.info(f'{course_name=}')
    
    logger.info(f'Приступаем к формированию статистики прохождения обучения по курсу: {course_name}')
    
    game = GamificationService()
    
    data = game._load_data()
    data_to_exel = {}
    logger.info(f'Убираем лишнюю информацию из data - ключи lesson_results и значения по ним')
    
    users_data = {}
    for user, user_data in data.copy().items():
        #del user_data['lesson_results']
        users_data.setdefault(user, user_data)
    pprint(users_data)
    
    logger.info(f'Для каждого пользователя получаем результат прохождения обучения по курсам')
    for user_id, education_info in users_data.items():
        last_first_user_name = f"{education_info.get('user_info')['last_name']} {education_info.get('user_info')['first_name']}"
        if user_id not in data_to_exel:
            data_to_exel.setdefault((user_id, last_first_user_name))
        current_user_result = game.get_info_to_exel_for_user(user_id=int(user_id), education_info=education_info, course_name=course_name, all_courses_flag=False)
        data_to_exel[(user_id, last_first_user_name)] = current_user_result
    
    logger.info(f'{data_to_exel=}')
    pprint(data_to_exel)
    
    excel_gen = ExcelStatisticGenerator(data_to_exel)
    
    file_path = add_timestamp_to_filename()
    
    #excel_gen.generate_excel("data/statistics.xlsx")
    logger.info(f'{file_path=}')
    try:
        excel_gen.generate_excel(file_path)
    except Exception as e:
        logger.error(f'При генерации файла статистики произошла ошибка {e}')
    
    
    if not os.path.exists(file_path):
        await callback.send(f"❌ Файл {file_path} не найден в папке data.")
        return
    
    try:
        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as file:
            # Отправляем документ в чат
            attachment = await callback.bot.upload_file(
                file_path
            )
            await callback.send('Статистика прохождения обучения', attachments=attachment)
        await callback.send("Для продолжения нажмите ниже", keyboard=main_one_kb())
    except Exception as e:
        await callback.send(f"❌ Произошла ошибка при отправке файла: {e}")

    
        
        

@router.on_button_callback(lambda data: data.payload == 'my_progress')
@router.on_command("my_progress")
async def my_progress_handler(ctx: CommandContext | Callback, cursor: FSMCursor):
    """Реализация логики прогресса ученика"""
    try:
        logger.info(f'[INFO][my_progress_handler] Стартовал')
        current_course = get_current_course(cursor)
              
        if isinstance(ctx, Callback):
            await ctx.message.delete()
        
        game = GamificationService(current_course)
            
        course_name = "Обучение по продажам"
        
        if current_course == 'Другой сотрудник':
            course_name = current_course
        progress = game.get_user_progress(ctx.user_id, course_name)
        logger.info(f'{course_name=}\n{progress=}')
        
        logger.info(
            'Реализуем логику отображения прогресса в зависимости от того, кто его запрашивает'
            'Для админов будет реализована логика формирования Exel файла'
            )
        
        user_id = str(ctx.user_id)
        user_data = load_user_data()
        logger.info(f'{user_data=}')
              
        if user_id in user_data:
            first_name = user_data[user_id]["first_name"]
            second_name = user_data[user_id]["second_name"]
            
        if isinstance(progress, tuple):
            logger.info(f'[INFO][my_progress_handler] {first_name} {second_name} еще не прошел до конца курс')
            
            completed_lesson = progress[1]['lessons_completed']
            logger.info(f'{completed_lesson=}')
            if current_course == 'Другой сотрудник':
                if int(completed_lesson) < 5:
                    completed_lesson = 0
                elif int(completed_lesson) < 10:
                    completed_lesson = 1
                elif int(completed_lesson) < 15:
                    completed_lesson = 2
                elif int(completed_lesson) < 20:
                    completed_lesson = 3
                elif int(completed_lesson) < 25:
                    completed_lesson = 4
                elif int(completed_lesson) < 30:
                    completed_lesson = 5
                elif int(completed_lesson) < 43:
                    completed_lesson = 6
                else:
                    completed_lesson = 7
            
            text = (
                f"📊 <b>{first_name} {second_name}</b>\n\n"
                f"📚 <b>Курс:</b> {course_name}\n\n"
                f"✅ <b>Уроков пройдено:</b> {completed_lesson} / {progress[1]['total_lessons']}\n"
                f"📈 <b>Процент правильных ответов:</b> {progress[1]['accuracy_percent']:.1f}%\n\n"
                f"⚠️ Вы ещё ни разу не прошли курс до завершения ⚠️\n"
                f"<i>Продолжайте обучение для повышения результатов!</i>"
            )
        else:
            text = format_progress_attempts(progress)
        
        await ctx.send(text, format="html", keyboard=education_kb(True))
            
        
    except Exception as e:
        logger.error(f'[ERROR][my_progress_handler] Произошла ошибка {e}')
        


@router.on_button_callback(lambda data: data.payload == 'send_question')
@router.on_command("send_question")
async def answer_to_send_question(ctx: CommandContext | Callback, cursor: FSMCursor):
    """Активация AI-ассистента с базой знаний"""
    try:
        logger.info(f'[INFO][answer_to_send_question] Стартовал')
        if isinstance(ctx, Callback):
            await ctx.message.delete()
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await ctx.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                format='html',
                keyboard=education_kb(True)
            )
            return
           
        await ctx.send(
            "🤖 <b>AI-ассистент компании</b>\n\n"
            f"📚 База знаний загружена ({stats['total_size']} символов)\n\n"
            "Задавайте вопросы о компании, продукции или процессах.\n"
            "Я буду отвечать на каждый ваш вопрос.\n\n"
            "<i>Например:</i>\n"
            "· О чем говорит ФЗ-123?\n"
            "· Что такое кремнезольная технология?\n"
            "· Какая гарантия на продукцию?\n\n"
            "Напишите ваш вопрос 👇\n\n"
            "Для выхода нажмите <b>🏠 Главное меню</b>",
            format='html',
            keyboard=education_kb(True, True)
        )
        cursor.change_state(TrainingStates.asking_ai)
        
        
    except Exception as e:
        logger.error(f'[ERROR][answer_to_send_question] Произошла ошибка: {e}')


@router.on_button_callback(state(TrainingStates.asking_ai), lambda data: data.payload == 'main_menu_without_ai')
async def exit_ai_handler(callback: Callback, cursor: FSMCursor):
    """Выход из режима AI-ассистента"""
    try:
        logger.info(f'[INFO][exit_ai_handler] Стартовал')
        # if await debounce_button(message, state):
        #     return

        await callback.message.delete()
        current_course = get_current_course(cursor)
        cursor.clear_state()
        await callback.send(
            "✅ Вы вышли из режима AI-ассистента",
            keyboard=main_menu_keyboard(current_course)
        )
        return
    
    except Exception as e:
        logger.error(f'[ERROR][exit_ai_handler] Произошла ошибка: {e}')
        

@router.on_message(state(TrainingStates.asking_ai))
async def process_ai_question_handler(message: Message, cursor: FSMCursor):
    """Обработка вопроса через RAG + Claude (непрерывный диалог)"""
       
    # Показываем процесс
    logger.info(f'[INFO][process_ai_question_handler] Стартовал')
    thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
    
    try:
        rag = RAGService()
        
        text = message.body.text
        logger.info(f'[INFO][process_ai_question_handler] {text=}')
        
        answer = await rag.answer_question(text)
        
        await thinking_msg.delete()
        
        # Форматируем ответ
        response_text = f"💡 **Ответ:**\n\n{answer}\n\n➡️ Задайте следующий вопрос или нажмите 🏠 **Главное меню**"
        
        
        await message.send(response_text, format='markdown', keyboard=education_kb(True, True))
        
        
    except Exception as e:
        await thinking_msg.delete()
        print(f"❌ Ошибка обработки вопроса: {e}")
        logger.error(f'[ERROR][process_ai_question_handler] Произошла ошибка: {e}')
        await message.send(
            "❌ Произошла ошибка. Попробуйте задать вопрос ещё раз или нажмите <b>🏠 Главное меню</b>",
            format="html",
            keyboard=education_kb(True, True)
            )
        # НЕ очищаем state - даём пользователю попробовать снова


@router.on_command("home")
@router.on_button_callback(lambda data: data.payload == 'main_menu')        
async def go_to_main_menu_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия кнопки перехода в Главное меню"""
    try:
        current_course = get_current_course(cursor)
        logger.info(f'{current_course=}')
        cursor.clear()
        cursor.change_data({"current_course": current_course})
        
        await callback.send("Вернулись в главное меню, выберите одно из действий 👇", keyboard=main_menu_keyboard(current_course))
    except Exception as e:
        logger.error(f'[go_to_main_menu_handler] произошла ошибка {e}')    


        
@router.on_command("export_stats")
async def export_stats(message: Message):
    """Экспорт статистики всех пользователей (только для админа)"""
    try:
        # ⚙️ ЗАМЕНИ на свой MAX ID
        logger.info(f'[INFO][export_stats] Стартовал')
        ADMIN_IDS = [51490094, 175082514, 20759321, 85179182] #[175082514]  # Твой ID
        
        user_id = message.user_id
        logger.info(f'Проверим id пользователя на принадлежность к ADMIN')
        
        if user_id not in ADMIN_IDS:
            logger.warning(f'Ваш max_id равен: {message.user_id}')
            await message.send("⛔ У вас нет доступа к этой команде")
            return
        
        game = GamificationService()
        
        all_courses_name = game.get_all_courses_name()
        logger.info(f'{all_courses_name=}')
               
        await message.send(
            text='Выберите название курса, по которому хотите получить статистику, либо нажмите <b>ПО ВСЕМ КУРСАМ</b> для выгрузки всей статистики:',
            keyboard=change_course_to_export_stat_kb(all_courses_name),
            format='html'
        )
        
        return
                
        users = game.get_all_users_progress_new()
        
        pprint(users)
        logger.info(f'Данные для преобразования в exel файл:\n{users=}')
        return
        
        if not users:
            await message.answer("📭 Нет данных о пользователях")
            return
        
        text = "📊 Статистика всех пользователей:\n\n"
        
        for idx, user in enumerate(users, 1):
            name = f"{user.get('first_name', 'Неизвестно')} {user.get('last_name', '')}".strip()
            #username = f"@{user['username']}" if user.get('username') else "—"
            
            text += f"{idx}. 👤 {name} \n\n\n"
            text += f"   🆔 ID: {user['user_id']}\n\n\n"
            
            for j, attemp in enumerate(user['leaderboard_list']):
                date_obj = datetime.fromisoformat(attemp['date_attemp'])
                formatted_date =  date_obj.strftime('%d.%m.%Y')  # date_obj.strftime('%d.%m.%Y в %H:%M')
                
                if j > 0:
                    text += "\n"
                text += f"   ✅ Уроков: {attemp['lessons_completed']}/43\n"
                text += f"   📈 Точность: {attemp['accuracy_percent']:.1f}%\n\n"
                text += f"   📆 Дата: {formatted_date}\n\n"
                
            
        
        await message.send(text, keyboard=education_kb(True))
    except Exception as e:
        logger.error(f'[ERROR][export_stats] Произошла ошибка: {e}')
        

# @router.on_bot_start()
# async def on_bot_start(pd: BotStartPayload):
#     print("Стартовала on_bot_start")
#     async def send(text: str):
#         await pd.send(text, keyboard=main_menu_keyboard())

#     await flow_start(send)


# async def handle_start_max(send_func, user_id: int, user_name: str | None = None):
#     """
#     Обработчик старта в MAX.

#     Параметры:
#     - send_func: асинхронная функция отправки сообщения вида
#         await send_func(text: str, keyboard: dict | None = None)
#     - user_id: ID пользователя в MAX (на будущее, если потребуется логированиe)
#     - user_name: Имя пользователя (можно использовать в тексте, если нужно)
#     """

#     text = get_start_text(fmt="md")
#     kb = main_menu()

#     await send_func(text, kb)

async def send(message: Message | Callback, out: str, with_keyboard: bool = False):
        try:
            logger.info("[send] стартовала функция отправки сообщения")
            if with_keyboard == "clear":
                if isinstance(message, Message):
                    logger.info("отвечаем на Message без клавиатуры")
                    await message.send(out)
                else:
                    logger.info("отвечаем на Callback без клавиатуры")
                    #await message.answer(out)
                    await message.send(out)
            elif callable(with_keyboard):
                logger.info("В качестве параметра для клавиатуры передана функция")
                kb = with_keyboard()
                if isinstance(message, Message):
                    logger.info("отвечаем на Message и прикрепляем клавиатуру")
                    await message.send(out, keyboard=kb)
                else:
                    logger.info("отвечаем на Callback и прикрепляем клавиатуру")
                    await message.send(out, keyboard=kb)
            else:
                kb = main_menu_keyboard()
                if isinstance(message, Message):
                    logger.info("отвечаем на Message и приклепляем главную клавиатуру")
                    await message.send(out, keyboard=kb)
                else:
                    logger.info("отвечаем на Callback и прикрепляем главную клавиатуру")
                    #await message.answer(out, keyboard=kb)
                    await message.send(out, keyboard=kb)
        except Exception as e:
            logger.error(f"[SEND] произошла ошибка {e}")

# ниже нужно раскомментировать
   
@router.on_button_callback(lambda data: data.payload == 'about_company')
async def about_company_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку 🏢 О компании """
    try:
        
        state_name = cursor.get_state()
        logger.info(f'{state_name=}')
        
        await flow_about_company(lambda t, with_keyboard="clear": send(callback, t, with_keyboard))
        
        cursor.change_state(OnboardingStates.waiting_for_start_date)
        logger.info(f"[flow_sales_training_handler] состояние для пользователя {callback.user.user_id} поменяно на `waiting_for_start_date`")
        return
    except Exception as e:
        logger.error(f'Произошла ошибка {e}')

    
@router.on_button_callback(state(OnboardingStates.waiting_for_start_date), lambda data: data.payload == 'tomorrow')
async def start_tomorrow_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку `🚀 Выхожу завтра`"""
    try:
        cursor_data = cursor.get_data()
        logger.info(f'{cursor_data=}')
        
        # Пользователь выходит завтра - сразу присылаем напоминание   
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%d.%m")
        
        # if await debounce_button_max(callback, cursor=cursor):
        #     logger.info(f"[start_tomorrow_handler] Идет обработка нажмите позднее")
        #     return
        
        # Сохраняем напоминание и СРАЗУ помечаем как отправленное
        logger.info(f"[start_tomorrow_handler] Сохраняем напоминание и СРАЗУ помечаем как отправленное")
        os.makedirs("data", exist_ok=True)
        
        reminders = {}
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
                reminders = json.load(f)
        
        reminders[str(callback.user.user_id)] = {
            "start_date": date_str,
            "reminder_sent": True  # ← Сразу помечаем как отправленное
        }
        
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
        logger.info(f"[start_tomorrow_handler] Напоминание сохранено и СРАЗУ помечено как отправленное")
        
        current_course = cursor_data.get("current_course")
        # Сразу отправляем напоминание
                
        if current_course == "Другой сотрудник":
            cursor.change_state(AnotherEmployerStates.user_type)
            current_course = "Обучение по продукту"
            
        text = get_tomorrow_reminder_text(date_str, current_course)
        
        await callback.send(text, keyboard=education_kb(current_cource = current_course))
        #cursor.clear()
    except Exception as e:
        logger.error(f"[start_tomorrow_handler] Произошла ошибка {e}")
        
from services.debounce import debounce_button_max

@router.on_button_callback(state(OnboardingStates.waiting_for_start_date), lambda data: data.payload == 'change_date')
async def change_date_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку `🚀 Указать дату`"""
    try:
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[change_date_handler] Идет обработка нажмите позднее")
        #     return
             
        await callback.send(
        "📝 Напишите дату вашего первого рабочего дня в формате ДД.ММ\n\n"
        "Например: 07.02"
        )
    except Exception as e:
        logger.error(f"[start_tomorrow_handler] Произошла ошибка {e}")
        

@router.on_message(state(OnboardingStates.waiting_for_start_date))
async def input_date_handler(message: Message, cursor: FSMCursor):
    """Обработчик выбора пользователем даты выхода на работу"""
    try:
        # if await debounce_button_max(message, cursor):
        #     logger.info(f"[input_date_handler] Идет обработка нажмите позднее")
        #     return
              
        user_input = message.body.text
        data = cursor.get_data()
        current_course = data.get("current_course")
        logger.info(f"[input_date_handler] {data=} {type(data)=}")
        logger.info(f"[input_date_handler] Вы ввели дату выхода на работу: {user_input}")
        day, month = map(int, user_input.split('.'))
        current_year = datetime.now().year
        start_date = datetime(current_year, month, day)
        
        if start_date < datetime.now():
            await message.send("⚠️ Выбранная Вами дата уже прошла.\nВведите актуальную дату...")
            logger.warning(f"Введенная дата уже прошла")
            return
            
        date_str = start_date.strftime("%d.%m")
        
        dt = datetime.strptime(f"{date_str}.{current_year}", "%d.%m.%Y")
        
        logger.info(f"[input_date_handler] {date_str=} {dt=}")
        
        cursor.change_data({"start_date": date_str, "parsed_date":dt, "current_course": current_course})
        
        months_ru = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
            7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        
        logger.info("Пытаемся отправить сообщение и клавиатуру")
        await message.send(
            f"✅ Правильно ли я понимаю, что ваш первый рабочий день — это {start_date.day} {months_ru[start_date.month]}?\n\n"
            "Нажмите «Да» для подтверждения или «Нет», чтобы указать другую дату.",
            keyboard=yes_no_kb()
        )
        
        cursor.change_state(OnboardingStates.waiting_for_confirmation)  # переходим в состояние подтверждения выбранной даты
    except Exception as e:
        logger.error(f"[input_date_handler] ошибка при вводе даты выхода на работу {e}")
        await message.send(
            "❌ Не удалось распознать дату. Используйте формат ДД.ММ (например, 07.02)"
        )  
    
from services.debounce import debounce_button_max

@router.on_button_callback(state(OnboardingStates.waiting_for_confirmation))
async def confirm_date_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик подтверждения выбора даты пользователем"""
    try:
        logger.info(f"[confirm_date_handler] Стартовал")
        data = cursor.get_data()
        logger.info(f'{data=}')
        start_date_str = data.get("start_date")
        current_course = data.get("current_course")
        
        if callback.payload == "yes":
        
            save_reminder(callback.user.user_id, start_date_str, REMINDERS_FILE)

            # if await debounce_button_max(callback, cursor):
            #     logger.info(f"[confirm_date_handler] Идет обработка нажмите позднее")
            #     return
            
            text = get_reminder_text(start_date_str)
            if current_course == "Другой сотрудник":
                current_course = "Обучение по продукту"
                text = get_reminder_text(start_date_str, current_course)
                await callback.send(text, keyboard=main_menu_keyboard("Обучение по продукту"))
                state_name = cursor.get_state()
                logger.info(f'{state_name=}')
                cursor.change_state(AnotherEmployerStates.user_type)
            else:
                await callback.send(text, keyboard=main_menu_keyboard(current_course))
                cursor.clear_state()
                 
        elif callback.payload == "no":  # пользователь отклонил дату
            
            await callback.send("📝 Напишите правильную дату вашего первого рабочего дня в формате ДД.ММ\n\n"
        "Например: 10.02")
            cursor.change_state(OnboardingStates.waiting_for_start_date)
            
    except Exception as e:
        logger.error(f"[confirm_date_handler] Произошла ошибка {e}")
      
        
from services.debounce import debounce_button_max
                      
@router.on_button_callback(state(TrainingStates.step_2_video), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_3_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 3 - Презентация компании (ссылка на материалы)"""
    try:
        logger.info("[training_step_3_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_3_handler] Идет обработка нажмите позднее")
        #     return
        await callback.message.delete()
        
        text = get_training_step_3_text()
        
        await callback.send(text)

        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
            

        cursor.change_state(TrainingStates.course_intro)
        
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )
         
    except Exception as e:
        logger.error(f"[training_step_3_handler] Произошла ошибка {e}")        


from services.debounce import debounce_button_max        

@router.on_button_callback(state(TrainingStates.course_intro), lambda data: data.payload.split('::')[1] == "not_first")
async def show_course_intro_handler(callback: Callback, cursor: FSMCursor):
    """Интро курса 'Обучение по продажам' (между шагом 2 и 3)"""
    try:
        logger.info("[show_course_intro_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[show_course_intro_handler] Идет обработка нажмите позднее")
        #     return
        cursor_data = cursor.get_data()
        logger.info(f'{cursor_data=}')
        if cursor_data.get("current_course") != "Другой сотрудник":
            await callback.message.delete()
            text = get_course_intro_text()
            await callback.send(text)
            # 2) Через 15 секунд — содержание Блока №1
            await asyncio.sleep(15) # 2
        
        block1_intro = get_block1_intro_text()
        if cursor_data.get("current_course") == "Другой сотрудник":
            block1_intro = get_another_emp_intro_text()
            
        await callback.send(block1_intro)
        
        # 3) Ещё через 10 секунд — сообщение с кнопкой «Продолжить обучение»
        await asyncio.sleep(10) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
        cursor.change_state(TrainingStates.step_3_presentation)
        
        await callback.send(
            "📚 Чтобы перейти к первому разделу и начать обучение, нажмите кнопку ниже 👇",
            keyboard=kb
        )
         
    except Exception as e:
        logger.error(f"[show_course_intro_handler] Произошла ошибка {e}") 


from services.debounce import debounce_button_max

@router.on_button_callback(state(TrainingStates.step_3_presentation), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_3_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """ШАГ 4 - Раздел №1: База теории"""
    try:
        logger.info("[training_step_3_handler] Стартовал")
        if continue_flag:
            intro_text = get_block1_intro_text()
            await callback.send(intro_text)
            await asyncio.sleep(10) # 2
        
        
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_3_handler] Идет обработка нажмите позднее")
        #     return      
        await callback.message.delete()
        intro_text = get_block1_section1_intro_text()
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        # сообщение о тестировании с кнопкой
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_4_ready_for_test)
    
    except Exception as e:
        logger.error(f"[training_step_3_handler] Произошла ошибка {e}") 
        

from services.debounce import debounce_button_max

@router.on_button_callback(state(TrainingStates.step_4_ready_for_test), lambda data: data.payload == "start_test")
async def training_step_4_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 5 - Начало тестирования"""
    try:
        logger.info("[training_step_4_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_1()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_step_4_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_step_4_handler] после добавления вопросов в state: {data=}')  
        
        # Отправляем первый вопрос
        cursor.change_data(data)
        await send_question(callback, cursor, "section_1")
        cursor.change_state(TrainingStates.step_5_testing)
    
    except Exception as e:
        logger.error(f"[training_step_4_handler] Произошла ошибка {e}") 

        
async def send_question(message: Message | Callback, cursor: FSMCursor, lesson_id: str, course_name: str = "Обучение по продажам"):
    """Отправляет текущий вопрос с вариантами ответов"""
    try:
        logger.info("[send_question] Стартовал")
        logger.info(f'[INFO][send_question]state={cursor.get_state()}')
        data:dict = cursor.get_data()
        course_name = data.get('current_course')
        if not course_name:
            course_name = "Обучение по продажам"
        questions = data.get("questions")
        current = data.get("current_question")
        logger.info(f'[send_question] номер текущего вопроса: {current}')
        
        if current >= len(questions):
            # Все вопросы пройдены - показываем результаты
            logger.info("[send_question] все вопросы пройдены, показываем результаты")
            await show_results(message, cursor, lesson_id, course_name)
            return
        
        logger.info("[send_question] еще не все вопросы пройдены, продолжаем...")
        question_data = questions[current]
        logger.info(f"[send_question] текущий вопрос: {question_data=}")
        
        # Текст вопроса
        text = f"📝 **{question_data['question']}**\n"
        
        # Текст вариантов ответов
        answers_text = "\n**Варианты ответов:**\n\n"
        for answer in question_data.get('options'):
            answers_text += f'{answer.strip()}\n'
        
        correct_answer = question_data.get('correct')
        logger.info("[INFO][send_question] обновляем информацию о правильном ответе в cursor")
        data.update(correct = correct_answer)
        logger.info("[INFO][send_question] обновляем значение всего cursor")
        cursor.change_data(data)
        
        kb = variants_questions_kb(question_data)
                
        if isinstance(message, Callback):
            await message.message.delete()
        await message.send(text + answers_text, keyboard=kb)
    
    except Exception as e:
        logger.error(f"[send_question] Произошла ошибка {e}") 



async def show_results(message: Message, cursor: FSMCursor, lesson_id: str, course_name: str):
    """Показывает результаты тестирования"""
    try:
        logger.info("[INFO][show_results] Стартовал")
        if isinstance(message, Callback):
            await message.message.delete()
        data: dict = cursor.get_data()
        questions = data.get("questions")
        answers = data.get("answers")
        logger.info(f"[INFO][show_results] {questions=}\n{answers=}")   
        
        # Подсчитываем правильные ответы
        correct_count = 0
        mistakes = []
        
        for i, question in enumerate(questions):
            logger.info(f"[INFO][show_results] Вопрос № {i}:\n{question}")
            if i < len(answers) and answers[i] == question["correct"]:
                logger.info(f"[INFO][show_results] ответ правильный")
                correct_count += 1
            else:
                user_ans = answers[i] if i < len(answers) else "Нет ответа"
                logger.info(f"[INFO][show_results] ответ не правильный (или нет ответа)")
                correct_ans = question["correct"]
                logger.info(f"[INFO][show_results] правильным должен был быть вариант ответа: {correct_ans}")
                
                # Находим полный текст ответа пользователя
                user_option = "Нет ответа"
                if user_ans != "Нет ответа":
                    user_option = [opt for opt in question["options"] if opt.startswith(user_ans)]
                    user_option = user_option[0] if user_option else user_ans
                logger.info(f"[INFO][show_results] полный текст ответа пользователя: {user_option}")
                
                # Находим полный текст правильного ответа
                correct_option = [opt for opt in question["options"] if opt.startswith(correct_ans)][0]
                logger.info(f"[INFO][show_results] полный текст правильного ответа: {correct_option}")
                
                mistakes.append({
                    "number": i + 1,
                    "question": question["question"],
                    "user_answer": user_option,
                    "correct_answer": correct_option
                })
                
                logger.info(f"[INFO][show_results] добавили информацию об ошибочном ответе пользователя")
        
        # Формируем сообщение с результатами
        result_text = f"📊 **Результаты тестирования**\n\n"
        result_text += f"✅ Правильных ответов: **{correct_count} из {len(questions)}**\n\n"
        
        if correct_count == len(questions):
            result_text += "🎉 **Отлично!** Вы ответили на все вопросы правильно! Так держать! 💪"
        else:
            result_text += "❌ **Неправильные ответы:**\n\n"
            for mistake in mistakes:
                result_text += f"**{mistake['question']}**\n\n"
                result_text += f"Ваш ответ: {mistake['user_answer']}\n"
                result_text += f"Правильный ответ: {mistake['correct_answer']}\n\n"
                result_text += "───────────────────────────\n\n"
            
            result_text += "💡 **Обратите внимание на эти моменты и повторите материал!**"
        
        await send_message_safely(message, result_text)
        #await message.send(result_text)
        
        # ✅ Обновляем прогресс пользователя (НОВЫЙ КОД)
        from services.gamification import GamificationService
        game = GamificationService(course_name)
        user_data = load_user_data()
        user_id = str(message.user_id)
        first_name = user_data.get(user_id).get("first_name")
        last_name = user_data.get(user_id).get("second_name")
        
        await game.update_lesson_progress(
            user_id=message.user_id,
            course_name=course_name, # "Обучение по продажам"
            correct_count=correct_count,
            total_count=len(questions),
            lesson_id=lesson_id, #  "section_1"
            user_data={
                "username": f'{first_name} {last_name}',
                "first_name": first_name,
                "last_name": last_name
            }
        )
        
        # Через 15 секунд предлагаем продолжить
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
            

        if cursor.get_state() == 'step_5_testing':
            cursor.change_state(TrainingStates.step_6_next)
        elif cursor.get_state() == 'step_7_testing':
            cursor.change_state(TrainingStates.step_8_next)
        elif cursor.get_state() == 'step_8_testing':
            cursor.change_state(TrainingStates.step_9_next)
        elif cursor.get_state() == 'step_9_testing':
            cursor.change_state(TrainingStates.step_10_next)
        elif cursor.get_state() == 'step_10_testing':
            cursor.change_state(TrainingStates.step_11_next)
        elif cursor.get_state() == 'block_2_test_1_testing':
            cursor.change_state(TrainingStates.block_2_section_2_next)
        elif cursor.get_state() == 'block_2_test_2_testing':
            cursor.change_state(TrainingStates.block_2_section_3_next)
        elif cursor.get_state() == 'block_2_test_3_testing':
            cursor.change_state(TrainingStates.block_2_section_4_next)
        elif cursor.get_state() == 'block_3_test_1_testing':
            cursor.change_state(TrainingStates.block_3_section_1_next)
        elif cursor.get_state() == 'block_3_test_2_testing':
            cursor.change_state(TrainingStates.block_3_section_2_next)
        elif cursor.get_state() == 'block_3_test_3_testing':
            cursor.change_state(TrainingStates.block_3_section_3_next)
        elif cursor.get_state() == 'block_3_test_4_testing':
            cursor.change_state(TrainingStates.block_3_section_4_next)
        elif cursor.get_state() == 'block_3_test_5_testing':
            cursor.change_state(TrainingStates.block_3_section_5_next)
        elif cursor.get_state() == 'block_3_test_6_testing':
            cursor.change_state(TrainingStates.block3_final_test)
        elif cursor.get_state() == 'block_4_test_1_testing':
            cursor.change_state(TrainingStates.block_4_section_1_next)
        elif cursor.get_state() == 'block_4_test_2_testing':
            cursor.change_state(TrainingStates.block_4_section_2_next)
        elif cursor.get_state() == 'block_4_test_3_testing':
            cursor.change_state(TrainingStates.block_4_section_3_next)
        elif cursor.get_state() == 'block_4_test_4_testing':
            cursor.change_state(TrainingStates.block4_final_test)

        
        
        logger.info(f"[INFO][show_results] state = {cursor.get_state()}")
        if cursor.get_state() != 'step_11_testing':
            await message.send(
                    "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
                    keyboard=kb
                )
        elif cursor.get_state() == 'step_11_testing':
            await continue_after_section6_handler(message, cursor)

        # elif cursor.get_state() == 'block3_final_test':
        #     await continue_after_section17_handler(message, cursor)
                
            
         
    except Exception as e:
        logger.error(f"[show_results] Произошла ошибка {e}")   


@router.on_button_callback(state(TrainingStates.block_4_test_4_testing))
@router.on_button_callback(state(TrainingStates.block_4_test_3_testing))
@router.on_button_callback(state(TrainingStates.block_4_test_2_testing))
@router.on_button_callback(state(TrainingStates.block_4_test_1_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_1_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_2_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_3_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_4_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_5_testing))
@router.on_button_callback(state(TrainingStates.block_3_test_6_testing))
@router.on_button_callback(state(TrainingStates.block_2_test_3_testing))
@router.on_button_callback(state(TrainingStates.block_2_test_2_testing))
@router.on_button_callback(state(TrainingStates.block_2_test_1_testing))
@router.on_button_callback(state(TrainingStates.step_11_testing))
@router.on_button_callback(state(TrainingStates.step_10_testing))
@router.on_button_callback(state(TrainingStates.step_9_testing))
@router.on_button_callback(state(TrainingStates.step_8_testing))
@router.on_button_callback(state(TrainingStates.step_7_testing))
@router.on_button_callback(state(TrainingStates.step_5_testing))
async def process_answer_handler(callback: Callback, cursor: FSMCursor):
    """Обрабатывает ответ пользователя"""
    try:
        logger.info(f"[INFO][process_answer_handler] Стартовал")   
        data:dict = cursor.get_data()
        answers = data.get("answers", [])
        current = data.get("current_question")
        correct = data.get("correct")
        
        call_answer = callback.payload
        logger.info(f"[INFO][process_answer_handler] {answers=}\n{current=}\n{call_answer=}")
        user_answer = call_answer.split('::')[1] if "correct" not in call_answer else call_answer.split('::')[1].split("_")[0]
        logger.info(f"[INFO][process_answer_handler] {user_answer=}\n{call_answer=}\n{correct=}")
        
        answers.append(user_answer)
        logger.info(f"[INFO][process_answer_handler] Сохраняем ответ пользователя и переходим к следующему вопросу")
        data.update(answers=answers, current_question=current + 1)
        logger.info(f'[INFO][process_answer_handler] state={cursor.get_state()}')
        if cursor.get_state() == 'step_5_testing':
            await send_question(callback, cursor, 'section_1')
        elif cursor.get_state() == 'step_7_testing':
            await send_question(callback, cursor, 'section_2')
        elif cursor.get_state() == 'step_8_testing':
            await send_question(callback, cursor, 'section_3')
        elif cursor.get_state() == 'step_9_testing':
            await send_question(callback, cursor, 'section_4')
        elif cursor.get_state() == 'step_10_testing':
            await send_question(callback, cursor, 'section_5')
        elif cursor.get_state() == 'step_11_testing':
            await send_question(callback, cursor, 'section_6')
        elif cursor.get_state() == 'block_2_test_1_testing':
            await send_question(callback, cursor, 'section_7')
        elif cursor.get_state() == 'block_2_test_2_testing':
            await send_question(callback, cursor, 'section_8')
        elif cursor.get_state() == 'block_2_test_3_testing':
            await send_question(callback, cursor, 'section_9')
        elif cursor.get_state() == 'block_3_test_1_testing':
            await send_question(callback, cursor, 'section_11')
        elif cursor.get_state() == 'block_3_test_2_testing':
            await send_question(callback, cursor, 'section_12')
        elif cursor.get_state() == 'block_3_test_3_testing':
            await send_question(callback, cursor, 'section_13')
        elif cursor.get_state() == 'block_3_test_4_testing':
            await send_question(callback, cursor, 'section_14')
        elif cursor.get_state() == 'block_3_test_5_testing':
            await send_question(callback, cursor, 'section_15')
        elif cursor.get_state() == 'block_3_test_6_testing':
            await send_question(callback, cursor, 'section_16')
        elif cursor.get_state() == 'block_4_test_1_testing':
            await send_question(callback, cursor, 'section_18')
        elif cursor.get_state() == 'block_4_test_2_testing':
            await send_question(callback, cursor, 'section_19')
        elif cursor.get_state() == 'block_4_test_3_testing':
            await send_question(callback, cursor, 'section_20')
        elif cursor.get_state() == 'block_4_test_4_testing':
            await send_question(callback, cursor, 'section_21')
    
    except Exception as e:
        logger.error(f"[ERROR][process_answer_handler] Произошла ошибка {e}")      


@router.on_button_callback(state(TrainingStates.step_6_next), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_6_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 6 - Раздел №2: Продукция компании"""
    try:
        await callback.message.delete()
        intro_text = get_block1_section2_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_6_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][training_step_6_handler] Произошла ошибка {e}")
            

# ========== РАЗДЕЛ №2 ==========

@router.on_button_callback(state(TrainingStates.step_6_ready_for_test), lambda data: data.payload == "start_test")
async def training_test_2_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 5 - Начало тестирования"""
    try:
        logger.info("[training_test_2_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_2()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_test_2_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_test_2_handler] после добавления вопросов в state: {data=}')  
        
        # Отправляем первый вопрос
        cursor.change_data(data)
        await send_question(callback, cursor, 'section_2')
        cursor.change_state(TrainingStates.step_7_testing)
    
    except Exception as e:
        logger.error(f"[training_test_2_handler] Произошла ошибка {e}")       


from services.debounce import debounce_button_max


# ========== РАЗДЕЛ №3 ==========

@router.on_button_callback(state(TrainingStates.step_8_next), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_8_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 6 - Раздел №3: Кремнезольная технология"""
    try:
        await callback.message.delete()
        intro_text = get_block1_section_3_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_8_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][training_step_8_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.step_8_ready_for_test), lambda data: data.payload == "start_test")
async def training_test_3_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 6 - Начало тестирования"""
    try:
        logger.info("[training_test_3_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_3()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_test_3_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_test_3_handler] после добавления вопросов в state: {data=}')  
        
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_3')
        cursor.change_state(TrainingStates.step_8_testing)
    
    except Exception as e:
        logger.error(f"[training_test_3_handler] Произошла ошибка {e}")     


# ========== РАЗДЕЛ №4 ==========

@router.on_button_callback(state(TrainingStates.step_9_next), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_9_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 7 - Раздел №4: Производственный процесс: как это делается"""
    try:
        await callback.message.delete()
        intro_text = get_block1_section_4_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_9_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][training_step_9_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.step_9_ready_for_test), lambda data: data.payload == "start_test")
async def training_test_4_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 8 - Начало тестирования"""
    try:
        logger.info("[training_test_4_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_4()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_test_4_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_test_4_handler] после добавления вопросов в state: {data=}')  
        
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_4')
        cursor.change_state(TrainingStates.step_9_testing)
    
    except Exception as e:
        logger.error(f"[training_test_4_handler] Произошла ошибка {e}")     


# ========== РАЗДЕЛ №5 ==========

@router.on_button_callback(state(TrainingStates.step_10_next), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_10_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 9 - Раздел №5: Группировка продуктов по назначению и условиям"""
    try:
        await callback.message.delete()
        intro_text = get_block1_section_5_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, format='markdown', keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_10_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][training_step_10_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.step_10_ready_for_test), lambda data: data.payload == "start_test")
async def training_test_5_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 9 - Начало тестирования"""
    try:
        logger.info("[training_test_45handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_5()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_test_5_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_test_5_handler] после добавления вопросов в state: {data=}')  
        
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_5')
        cursor.change_state(TrainingStates.step_10_testing)
    
    except Exception as e:
        logger.error(f"[training_test_5_handler] Произошла ошибка {e}")     


# ========== РАЗДЕЛ №6 ==========

@router.on_button_callback(state(TrainingStates.step_11_next), lambda data: data.payload.split('::')[1] == "not_first")
async def training_step_11_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 9 - Раздел №6: Ценообразование: как формируется стоимость"""
    try:
        await callback.message.delete()
        intro_text = get_block1_section_6_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.step_11_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][training_step_11_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.step_11_ready_for_test), lambda data: data.payload == "start_test")
async def training_test_6_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 9 - Начало тестирования"""
    try:
        logger.info("[training_test_6_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_testing_data_6()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_test_6_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_test_6_handler] после добавления вопросов в state: {data=}')  
        
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_6')
        cursor.change_state(TrainingStates.step_11_testing)
    
    except Exception as e:
        logger.error(f"[training_test_6_handler] Произошла ошибка {e}")  
        
        
@router.on_button_callback(state(TrainingStates.step_11_testing), lambda data: data.payload.split('::')[1] == "not_first")
async def continue_after_section6_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №1 - Продукт. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_section6_handler] Стартовал")
        await callback.message.delete()
        current_course = get_current_course(cursor)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        cursor_data = cursor.get_data()
                
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_1()
        if cursor_data.get("current_course") == "Другой сотрудник":
            text = get_text_to_final_test_block_1(True)
        
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block1_questions)
    
    except Exception as e:
        logger.error(f"[continue_after_section6_handler] Произошла ошибка {e}")



@router.on_button_callback(state(TrainingStates.block1_questions), lambda data: data.payload == 'to_final_test')
async def start_block1_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №1 - ШАГ 10"""
    try:
        logger.info(f"[INFO][start_block1_final_test_handler] Стартовал")
        current_course = get_current_course(cursor)
        text = get_text_start_final_test_block_1()
        
        if current_course == "Другой сотрудник":
            text = get_text_start_final_test_block_1(True)
        
        data = cursor.get_data()
        if not data:
            data = dict()
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.step_12_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block1_final_test_handler] Произошла ошибка {e}")
        

@router.on_message(state(TrainingStates.block1_questions))
async def answer_block1_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 1 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block1_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block1_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №1:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block1_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )


@router.on_message(state(TrainingStates.step_12_testing))
async def block1_final_testing_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 1 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block1_question_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete()
        await asyncio.sleep(2) 
        course_name = get_current_course(cursor)
        logger.info(f'{course_name=}')
        if course_name != "Другой сотрудник":
            await send_question_step_12(message, cursor, 'final_test', 'Обучение по продажам')
        else:
            await send_question_step_12(message, cursor, 'final_test', 'Другой сотрудник')
        
        
        
        # Форматируем ответ
        # logger.info(f"[INFO][answer_block1_question_handler] Форматируем ответ") 
        # response_text = (
        #     f"💡 **Ответ по Блоку №1:**\n\n"
        #     f"{answer}\n\n"
        #     "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        # )
        
        # await message.send(response_text, keyboard=final_start_test_kb())
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block1_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )
       
# ============================================================================
# ШАГ 17: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ №1 (10 закрытых + 5 открытых)
# ============================================================================

@router.on_button_callback(state(TrainingStates.step_12_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block1_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ 12 - Запуск финального тестирования по Блоку 1"""
    try:
        logger.info(f"[INFO][start_testing_block1_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_1('close')
        logger.info(f"[INFO][start_testing_block1_handler] {closed_questions=}")
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_1('open')
        logger.info(f"[INFO][start_testing_block1_handler] {open_questions=}")
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block1_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "step_12_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "step_12_testing"
                )
            
        logger.info(f'[start_testing_block1_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block1_handler] Отправляем первый закрытый вопрос')
        course_name = get_current_course(cursor)
        logger.info(f'{course_name=}')
        if course_name != "Другой сотрудник":
            await send_question_step_12(callback, cursor, "final_test", "Обучение по продажам")
        else:
            await send_question_step_12(callback, cursor, 'final_test', 'Другой сотрудник')
        #cursor.change_data(data)  # !!!!!!!!!!
        cursor.change_state(TrainingStates.step_12_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block1_handler] Произошла ошибка {e}") 


async def send_question_step_12(message: Message | Callback, cursor: FSMCursor, lesson_id: str, course_name: str = "Обучение по продажам"):
    """Отправка вопроса для step_12 (закрытые или открытые)"""
    try:
        logger.info("[send_question_step12] Стартовал")
        data:dict = cursor.get_data()
        
        course_name = get_current_course(cursor)
        if not course_name:
            course_name = "Обучение по продажам"
        
        if not data:
            data = dict()
            stage = data.get("test_stage", "closed")
        else:
            stage = data.get("test_stage")
        
        
        
        if stage == "closed":
            # ЗАКРЫТЫЕ ВОПРОСЫ (с кнопками)
            closed_questions = data.get("closed_questions")
            current = data.get("current_question")
            logger.info(f"[send_question_step12] {closed_questions=} {current=}")
            
            if current >= len(closed_questions):
                # Закрытые вопросы закончились → переходим к открытым
                logger.info("[send_question_step12] Закрытые вопросы закончились → переходим к открытым")
                data.update(test_stage="open", current_question=0)
                cursor.change_data(data)
                
                # Сообщение о переходе к открытым вопросам
                if isinstance(message, Callback):
                    await message.message.delete()
                await message.send(
                "✅ **Часть 1 завершена!**\n\n"
                "Теперь переходим к **открытым вопросам**.\n\n"
                "Отвечайте своими словами, развёрнуто. Ваши ответы будут оценены автоматически."
                )
            
                await asyncio.sleep(2)
                await send_question_step_12(message, cursor, lesson_id, course_name)
                return   

            logger.info("[send_question_step12] еще не все вопросы пройдены, продолжаем...")
            question_data = closed_questions[current]
            logger.info(f"[send_question_step12] текущий вопрос: {question_data=}")
        
            # Текст вопроса
            text = f"**Вопрос {int(current) + 1}/{len(closed_questions)}**\n\n📝 **{question_data['question']}**\n"
            
            # Текст вариантов ответов
            answers_text = "\n**Варианты ответов:**\n\n"
            for answer in question_data.get('options'):
                answers_text += f'{answer}\n'
            
            correct_answer = question_data.get('correct')
            logger.info("[INFO][send_question_step12] обновляем информацию о правильном ответе в cursor")
            data.update(correct = correct_answer)
            
            logger.info(f"[INFO][send_question_step12] обновляем значение всего cursor\nstate = {cursor.get_state()}")
            cursor.change_data(data)
                
            kb = variants_questions_kb(question_data)
            
            if isinstance(message, Callback):
                await message.message.delete()
            await message.send(text + answers_text, keyboard=kb)

        elif stage == "open":
            # ОТКРЫТЫЕ ВОПРОСЫ (текстовый ввод)
            open_questions = data.get("open_questions")
            current = data.get("current_question")
            
            if current >= len(open_questions):
                logger.info(f"[INFO][send_question_step12] Все вопросы закончились → показываем результаты")
                # Все вопросы закончились → показываем результаты
                await show_results_step12(message, cursor, lesson_id, course_name)
                return
            
            # Отправляем открытый вопрос
            question_data = open_questions[current]
            if cursor.get_state() == 'block_7_final_testing':
                text = f"**Вопрос {21 + current}/30** (открытый вопрос)\n\n{question_data['question']}\n\n_Ответьте развёрнуто своими словами._"
            else:
                text = f"**Вопрос {11 + current}/15** (открытый вопрос)\n\n{question_data['question']}\n\n_Ответьте развёрнуто своими словами._"
        
            await message.send(text, format="markdown")
            cursor.change_state(TrainingStates.check_answer_to_open_question)
            return
        
    except Exception as e:
        logger.error(f'[ERROR][send_question_step12] Произошла ошибка {e}')
        

@router.on_message(state(TrainingStates.check_answer_to_open_question))
async def check_valid_answer_of_question(message: Message, cursor: FSMCursor):
    """Проверка валидности введенного пользователем ответа на открытый вопрос"""
    try:
    
        data = cursor.get_data()
        open_answers = data.get("open_answers", [])
        current = data.get("current_question")
        user_answer = message.body.text.strip()
        migration_state = data.get("migration_state")
        
        if len(user_answer) < 10:
            await message.send(
                "⚠️ Ответ слишком короткий. Пожалуйста, дайте более развёрнутый ответ."
            )
            return
        
        logger.info(f"[INFO][check_valid_answer_of_question] Сохраняем ответ пользователя и переходим к следующему вопросу")
        open_answers.append(user_answer)
        data.update(open_answers=open_answers, current_question=current + 1)
        cursor.change_data(data)
        cursor.change_state(migration_state) # 'step_12_testing' или 'block_2_final_testing'
        
        if migration_state == 'step_12_testing': 
            await block1_final_testing_handler(message, cursor)
        elif migration_state == 'block_2_final_testing': 
            await block2_final_testing_handler(message, cursor)
        elif migration_state == 'block_3_final_testing': 
            await block3_final_testing_handler(message, cursor)
        elif migration_state == 'block_4_final_testing': 
            await block4_final_testing_handler(message, cursor)
        elif migration_state == 'block_5_final_testing': 
            await block5_final_testing_handler(message, cursor)
        elif migration_state == 'block_6_final_testing': 
            await block6_final_testing_handler(message, cursor)
        elif migration_state == 'block_7_final_testing': 
            await block7_final_testing_handler(message, cursor)
               
        #await send_question_step_12(message, cursor, 'final_test', 'Обучение по продажам')
        
    except Exception as e:
        logger.error(f'[ERROR][check_valid_answer_of_question] Произошла ошибка {e}')



async def send_message_safely(message, text: str, max_length: int = 3700, format: str = "markdown"):
    """
    Безопасно отправляет сообщение, разбивая его на части, если оно превышает max_length.

    Args:
        message: объект сообщения для отправки (должен иметь метод send)
        text: текст для отправки
        max_length: максимальная длина одной части сообщения (по умолчанию 3700)
        format: формат сообщения для параметра format в send (по умолчанию "markdown")
    """
    if len(text) <= max_length:
        # Отправляем целиком, если длина в пределах лимита
        await message.send(text, format=format)
    else:
        # Разбиваем текст на части по max_length символов
        parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]

        # Отправляем каждую часть последовательно
        for part in parts:
            await message.send(part, format=format)



async def show_results_step12(message: Message, cursor: FSMCursor, lesson_id: str, course_name: str):
    """Показ результатов финального теста step_12"""
    try:
        logger.info("[INFO][show_results_step12] Стартовал")
        if isinstance(message, Callback):
            await message.message.delete()
        data = cursor.get_data()
        closed_questions = data.get("closed_questions")
        open_questions = data.get("open_questions")
        closed_answers = data.get("closed_answers")
        open_answers = data.get("open_answers")
        if "migration_state" in data:
            migration_state = data.get("migration_state")
            logger.info(f"[INFO][show_results_step12] {closed_answers=} {open_answers=} {migration_state=}")
        else:
            logger.info(f"[INFO][show_results_step12] {closed_answers=} {open_answers=}")
        
        # Показываем сообщение о проверке
        checking_msg = await message.send("⏳ **Проверяю ваши ответы...**\n\nЭто может занять некоторое время.", format="markdown")
        
        # ==========================================
        # ЧАСТЬ 1: Проверка закрытых вопросов
        # ==========================================
        closed_correct = 0
        closed_mistakes = []
        
        for i, question in enumerate(closed_questions):
            logger.info(f"[INFO][show_results_step12] Вопрос № {i}:\n{question}")
            if i < len(closed_answers) and closed_answers[i] == question["correct"]:
                logger.info(f"[INFO][show_results_step12] ответ правильный")
                closed_correct += 1
            else:
                user_ans = closed_answers[i] if i < len(closed_answers) else "Нет ответа"
                logger.info(f"[INFO][show_results_step12] ответ не правильный (или нет ответа)")
                correct_ans = question["correct"]
                logger.info(f"[INFO][show_results_step12] правильным должен был быть вариант ответа: {correct_ans}")
                
                # Находим полный текст ответа пользователя
                user_option = "Нет ответа"
                if user_ans != "Нет ответа":
                    user_option = [opt for opt in question["options"] if opt.startswith(user_ans)]
                    user_option = user_option[0] if user_option else user_ans
                logger.info(f"[INFO][show_results_step12] полный текст ответа пользователя: {user_option}")
                
                # Находим полный текст правильного ответа
                correct_option = [opt for opt in question["options"] if opt.startswith(correct_ans)][0]
                logger.info(f"[INFO][show_results_step12] полный текст правильного ответа: {correct_option}")
                
                closed_mistakes.append({
                    "number": i + 1,
                    "question": question["question"],
                    "user_answer": user_option,
                    "correct_answer": correct_option
                })
                
                logger.info(f"[INFO][show_results_step12] добавили информацию об ошибочном ответе пользователя")
                
        # ==========================================
        # ЧАСТЬ 2: Проверка открытых вопросов через AI
        # ==========================================
        
        giga_service = GigaChatService()
        #claude = ClaudeService()
        open_scores = []
        open_mistakes = []
        giga_comments = []
        logger.info(f'[INFO][show_results_step12] Инициализировали список {open_mistakes=}')
        
        for i, question in enumerate(open_questions):
            if i >= len(open_answers):
                open_scores.append(0)
                open_mistakes.append({
                    "number": 11 + i,
                    "question": question["question"],
                    "user_answer": "Нет ответа",
                    "feedback": "Вы не ответили на вопрос.",
                    "score": 0
                })
                continue
            
            user_answer = open_answers[i]
            ideal_answer = question["ideal_answer"]
            
            # Оцениваем через GigaChat
            logger.info(f"[INFO][show_results_step12] Оцениваем через Claude AI")
            evaluation = await giga_service.evaluate_answer(
                user_answer=user_answer,
                ideal_answer=ideal_answer,
                question=question["question"]
            )
            
            logger.info(f'[INFO][show_results_step12] Инициализировали список {evaluation=}')
            
            score = evaluation.get("score", 0)
            feedback = evaluation.get("feedback", "Нет фидбека")
            passed = evaluation.get("passed", False)
                  
            open_scores.append(score)
            
            if not passed:  # Если оценка < 7.0
                open_mistakes.append({
                    "number": 11 + i,
                    "question": question["question"],
                    "user_answer": user_answer[:200] + "..." if len(user_answer) > 200 else user_answer,
                    "feedback": feedback,
                    "score": score
                })
            
            if 7.0 < score < 10.0:
                giga_comments.append({
                    "number": 11 + i,
                    "question": question["question"],
                    "user_answer": user_answer[:200] + "..." if len(user_answer) > 200 else user_answer,
                    "feedback": feedback,
                    "score": score
                })
                
                
    
        await checking_msg.delete()
        
        # ==========================================
        # РАСЧЁТ ДЛЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ
        # ==========================================
        logger.info(f"[INFO][show_results_step12] РАСЧЁТ ДЛЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ")
        open_correct = sum(1 for score in open_scores if score >= 7.0)
        total_correct = closed_correct + open_correct
        total_questions = len(closed_questions) + len(open_questions)
        
        # Процент для отображения
        accuracy_percent = (total_correct / total_questions) * 100 if total_questions > 0 else 0
        
        # ==========================================
        # ОБНОВЛЯЕМ ПРОГРЕСС (нормализация к 15 вопросам)
        # ==========================================
        logger.info(f"[INFO][show_results_step12] ОБНОВЛЯЕМ ПРОГРЕСС (нормализация к 15 вопросам)")
        # Закрытые: считаем как есть (из 10)
        closed_correct_for_progress = closed_correct
        
        # Открытые: нормализуем баллы к количеству вопросов (из 5)
        # Максимум баллов за открытые: 5 вопросов × 10 баллов = 50
        open_max_score = len(open_questions) * 10
        open_total_score = sum(open_scores)
        open_correct_equivalent = (open_total_score / open_max_score) * len(open_questions) if open_max_score > 0 else 0
        
        # Итого для статистики (из 15 вопросов)
        logger.info(f"[INFO][show_results_step12] Итого для статистики (из 15 вопросов)")
        total_correct_for_progress = closed_correct_for_progress + open_correct_equivalent
        total_questions_for_progress = len(closed_questions) + len(open_questions)  # 15
        
        game = GamificationService(course_name)
        user_data = load_user_data()
        user_id = str(message.user_id)
        
        
        
        first_name = user_data.get(user_id).get("first_name")
        last_name = user_data.get(user_id).get("second_name")
               
        await game.update_lesson_progress(
            user_id=message.user_id,
            course_name=course_name, #  "Обучение по продажам",
            correct_count=int(round(total_correct_for_progress)),  # Округляем
            total_count=total_questions_for_progress,               # 15
            lesson_id=lesson_id, #"final_test",
            user_data={
                "username": f'{first_name} {last_name}',
                "first_name": first_name,
                "last_name": last_name
            }
        )
        
        if cursor.get_state() == 'block_7_final_testing':
            data = game._load_data()
            course_progress = data[user_id]['courses'][course_name]
            correct_answers = course_progress.get('correct_answers')
            total_answers = course_progress.get('total_answers')       
            game.record_course_completion_attempt(int(user_id), correct_answers=correct_answers, total_answers=total_answers)
        
        if cursor.get_state() == 'step_12_testing':
            data = game._load_data()
            course_progress = data[user_id]['courses'][course_name]
            correct_answers = course_progress.get('correct_answers')
            total_answers = course_progress.get('total_answers')       
            game.record_course_completion_attempt(int(user_id), correct_answers=correct_answers, total_answers=total_answers, course_name="Другой сотрудник")
            
        
        # ==========================================
        # ИТОГОВЫЙ ОТЧЁТ
        # ==========================================
        logger.info(f"[INFO][show_results_step12] ИТОГОВЫЙ ОТЧЁТ")
        
        migration_header = ''
        if migration_state == 'step_12_testing':
            cursor_data = cursor.get_data()
            migration_header = '№1'
            if cursor_data.get("current_course") == "Другой сотрудник":
                migration_header = ''
        elif migration_state == 'block_2_final_testing':
            migration_header = '№2'
        elif migration_state == 'block_3_final_testing':
            migration_header = '№3'
        elif migration_state == 'block_4_final_testing':
            migration_header = '№4'
        elif migration_state == 'block_5_final_testing':
            migration_header = '№5'
        elif migration_state == 'block_6_final_testing':
            migration_header = '№6'
        elif migration_state == 'block_7_final_testing':
            migration_header = '№7'
        
        result_text = f"📊 **Результаты финального теста по Блоку {migration_header}**\n\n" if migration_header else f"📊 **Результаты финального теста по Блоку**\n\n"
        result_text += f"**Правильных ответов: {total_correct}/{total_questions}**\n\n"
        result_text += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        result_text += f"**Часть 1 (тестовые вопросы):** {closed_correct}/10\n"
        result_text += f"**Часть 2 (открытые вопросы):** {open_correct}/5\n"
        result_text += f"**Итоговый процент:** {accuracy_percent:.1f}%\n\n"
        
        if total_correct == total_questions:
            if giga_comments:
                logger.info('[INFO][show_results_step12] Были неточности в ответах на открытые вопросы')
                
                result_text += "**Не точные ответы в открытых вопросах:**\n\n"
                for comment in giga_comments:
                    result_text += f"⚠️ **Вопрос {comment['number']}:** {comment['question']}\n"
                    result_text += f"Ваш ответ: {comment['user_answer']}\n"
                    result_text += f"Оценка: {comment['score']}/10\n"
                    result_text += f"Фидбек: {comment['feedback']}\n\n"
                
            
            result_text += f"🎉 **Отлично!**\n\nВы успешно прошли финальный тест! Поздравляем с завершением Блока {migration_header}!"

        
        else:
            result_text += "📝 **Есть ошибки**\n\nОзнакомьтесь с правильными ответами ниже:\n\n"
            
            # Показываем ошибки в закрытых вопросах
            if closed_mistakes:
                result_text += "**Ошибки в тестовых вопросах:**\n\n"
                for mistake in closed_mistakes:
                    result_text += f"❌ **Вопрос {mistake['number']}:** {mistake['question']}\n"
                    result_text += f"Ваш ответ: {mistake['user_answer']}\n"
                    result_text += f"Правильный ответ: {mistake['correct_answer']}\n\n"
            
            # Показываем ошибки в открытых вопросах
            if giga_comments:
                logger.info('[INFO][show_results_step12] Были неточности в ответах на открытые вопросы')
                
                result_text += "**Не точные ответы в открытых вопросах:**\n\n"
                for comment in giga_comments:
                    result_text += f"⚠️ **Вопрос {comment['number']}:** {comment['question']}\n"
                    result_text += f"Ваш ответ: {comment['user_answer']}\n"
                    result_text += f"Оценка: {comment['score']}/10\n"
                    result_text += f"Фидбек: {comment['feedback']}\n\n"
            
            if open_mistakes:
                result_text += "**Ошибки в открытых вопросах:**\n\n"
                for mistake in open_mistakes:
                    result_text += f"❌ **Вопрос {mistake['number']}:** {mistake['question']}\n"
                    result_text += f"Ваш ответ: {mistake['user_answer']}\n"
                    result_text += f"Оценка: {mistake['score']}/10\n"
                    result_text += f"Фидбек: {mistake['feedback']}\n\n"
            
            result_text += "\n**Рекомендуем изучить материалы ещё раз!**"
        
        await send_message_safely(message, result_text, format="markdown")
        
        #game = GamificationService()
        
        # Переход дальше (или завершение)
        await asyncio.sleep(15) # 2
        
        # ==========================================
        # ПОКАЗЫВАЕМ РЕЙТИНГ ПО ИТОГАМ ПРОЙДЕННОГО БЛОКА
        # ==========================================
        
        # Получаем обновлённый прогресс пользователя
        logger.info(f"[INFO][show_results_step12] Получаем обновлённый прогресс пользователя")
        
        progress = ''
        
        current_course = get_current_course(cursor)
        if current_course == 'Другой сотрудник':
            progress = game.get_user_progress(message.user_id, current_course)
        else:
            progress = game.get_user_progress(message.user_id, "Обучение по продажам")
        
        logger.info(f"[INFO][show_results_step12] {progress=}")
        
        # Получаем место пользователя в рейтинге
        logger.info(f"[INFO][show_results_step12] Получаем место пользователя в рейтинге")
        leaderboard = game.get_all_users_progress("Обучение по продажам")
        user_rank = 0
        for i, user_data in enumerate(leaderboard, start=1):
            logger.info(f"[INFO][show_results_step12] {i=} \n{user_data=}")
            if isinstance(user_data, tuple):
                if user_data[1]['user_id'] == message.user_id:
                    user_rank = i
                    break
            else:    
                if user_data['user_id'] == message.user_id:
                    user_rank = i
                    break
        
        # Формируем сообщение о рейтинге
        logger.info(f"[INFO][show_results_step12] Формируем сообщение о рейтинге")
        user_data = load_user_data()
        logger.info(f"[INFO][show_results_step12] {user_data=}")
        user_id = str(message.user_id)
        first_name = user_data.get(user_id).get("first_name")
        last_name = user_data.get(user_id).get("second_name")
        
        
        current_course = get_current_course(cursor)
        # Определяем количество пройденных уроков для пользователей на курсе ДРУГОЙ СОТРУДНИК
        complet_less = 0
        completed_lesson = 0
        
        completed_dict = {'0': 0, '1': 5, '2': 10, '3': 15, '4': 20, '5': 25, '6': 30, '7': 45}
        
        if isinstance(progress, list):
            max_progress = get_max_accuracy_item(progress)
            completed_lesson = max_progress['lessons_completed']
            logger.info(f'{completed_lesson=}')
            if current_course == 'Другой сотрудник':
                if int(completed_lesson) < 5:
                    completed_lesson = 0
                elif int(completed_lesson) < 10:
                    completed_lesson = 1
                elif int(completed_lesson) < 15:
                    completed_lesson = 2
                elif int(completed_lesson) < 20:
                    completed_lesson = 3
                elif int(completed_lesson) < 25:
                    completed_lesson = 4
                elif int(completed_lesson) < 30:
                    completed_lesson = 5
                elif int(completed_lesson) < 43:
                    completed_lesson = 6
                else:
                    completed_lesson = 7
                
            first_phrase = f"🏆 **Ваш рейтинг по итогам Блока {migration_header}**\n\n" if migration_header else "🏆 **Ваш рейтинг по итогам Блока**\n\n"
            
            rating_text = (
                f"{first_phrase}"
                f"👤 **Ваше имя:** {first_name} {last_name}\n"
                f"📚 **Курс:** {'Обучение по продажам' if current_course != 'Другой сотрудник' else current_course}\n\n"
                f"✅ **Уроков пройдено:** {completed_lesson} / {43 if current_course != 'Другой сотрудник' else 7}\n"   # f"✅ **Уроков пройдено:** {progress['lessons_completed']} / {progress['total_lessons']}\n"
                f"📈 **Процент правильных ответов:** {max_progress['accuracy_percent']:.1f}%\n"
            )
        else:            
            
            completed_lesson = progress[1]['lessons_completed']
            logger.info(f'{completed_lesson=}')
            if current_course == 'Другой сотрудник':
                if int(completed_lesson) < 5:
                    completed_lesson = 0
                elif int(completed_lesson) < 10:
                    completed_lesson = 1
                elif int(completed_lesson) < 15:
                    completed_lesson = 2
                elif int(completed_lesson) < 20:
                    completed_lesson = 3
                elif int(completed_lesson) < 25:
                    completed_lesson = 4
                elif int(completed_lesson) < 30:
                    completed_lesson = 5
                elif int(completed_lesson) < 43:
                    completed_lesson = 6
                else:
                    completed_lesson = 7
            
            first_phrase = f"🏆 **Ваш рейтинг по итогам Блока {migration_header}**\n\n" if migration_header else "🏆 **Ваш рейтинг по итогам Блока**\n\n"
            
            rating_text = (
                f"{first_phrase}"
                f"👤 **Ваше имя:** {first_name} {last_name}\n"
                f"📚 **Курс:** {'Обучение по продажам' if current_course != 'Другой сотрудник' else current_course}\n\n"
                f"✅ **Уроков пройдено:** {completed_lesson} / {43 if current_course != 'Другой сотрудник' else 7}\n"  #  f"✅ **Уроков пройдено:** {progress[1]['lessons_completed']} / {progress[1]['total_lessons']}\n"
                f"📈 **Процент правильных ответов:** {progress[1]['accuracy_percent']:.1f}%\n"
            )
        
        if user_rank > 0:
            rating_text += f"🥇 **Ваше место в рейтинге:** #{user_rank}\n"
        else:
            rating_text += f"📊 **Место в рейтинге:** не определено\n"
        
        rating_text += "\n_Продолжайте обучение для повышения результатов!_"
        
        await message.send(rating_text, format="markdown")
        
        # Пауза перед кнопкой продолжения
        await asyncio.sleep(5) # 2
        
        logger.info(f'Строка 2198: {migration_header=}')
        
        if migration_header == "":
            block_intro = get_final_another_emp_text()
            await message.send(block_intro, format="markdown", keyboard=education_kb(current_cource="Другой сотрудник", final_flag=True))
            cursor.clear_state()
            return       
        if migration_header == "№1":
            block_intro = get_block2_intro_text()
            # await message.send(block_intro, format="markdown", keyboard=next_to_educ_to_part_kb())
            # return
        elif migration_header == "№2":
            block_intro = get_block3_intro_text()
        elif migration_header == "№3":
            block_intro = get_block4_intro_text()
        elif migration_header == "№4":
            block_intro = get_block5_intro_text()
        elif migration_header == "№5":
            block_intro = get_block6_intro_text()
        elif migration_header == "№6":
            block_intro = get_block7_intro_text()
        elif migration_header == "№7":
            block_intro = get_final_intro_text()
            await message.send(block_intro, format="markdown", keyboard=education_kb(final_flag=True))
            cursor.clear_state()
            return
        
        await message.send(block_intro, format="markdown", keyboard=next_to_educ_to_part_kb())
        
                   
    except Exception as e:
        logger.error(f'[ERROR][show_results_step12] Произошла ошибка {e}')
        
        
# ============================================================================
# БЛОК №2: КЛИЕНТ И ЦЕЛЕВАЯ АУДИТОРИЯ
# ============================================================================

# РАЗДЕЛ № 1 ------------------

@router.on_button_callback(state(TrainingStates.step_12_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_2_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик завершения обучения по 1 блоку и перехода к блоку № 2 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_2_handler] Стартовал')
        cursor.change_state(TrainingStates.block2_start)
        if continue_flag:
            intro_text = get_block2_intro_text()
            await callback.send(intro_text)
            await asyncio.sleep(10) # 2        
        
        # if await debounce_button_max(callback, cursor):
        #     return
        
        intro_text = get_block2_section1_intro_text()
        
        await callback.send(intro_text, format='markdown', disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(10)
        await callback.send(test_text, format="markdown", keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block2_section1_ready)
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_2_handler] Произошла ошибка {e}')
        

@router.on_button_callback(state(TrainingStates.block2_section1_ready), lambda data: data.payload == "start_test")
async def training_block_2_test_1_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 2 Тест 1 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_2_test_1_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_2_test_1_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_2_test_1_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_2_test_1_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_7')
        cursor.change_state(TrainingStates.block_2_test_1_testing)
    
    except Exception as e:
        logger.error(f"[training_block_2_test_1_handler] Произошла ошибка {e}")   


# ============================================================================
# БЛОК №2 - РАЗДЕЛ №2: Сложные клиенты и стратегические партнёры
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_2_section_2_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_2_test_2_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №2 - Раздел №2: Сложные клиенты и стратегические партнёры"""
    try:
        await callback.message.delete()
        intro_text = get_block2_section_2_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(10)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_2_test_2_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_2_test_2_ready_for_test_handl] Произошла ошибка {e}") 


@router.on_button_callback(state(TrainingStates.block_2_test_2_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_2_test_2_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 2 Тест 2 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_2_test_2_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_2_test_2_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_2_test_2_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_2_test_2_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_8')
        cursor.change_state(TrainingStates.block_2_test_2_testing)
    
    except Exception as e:
        logger.error(f"[training_block_2_test_2_handler] Произошла ошибка {e}")
        
        
# ============================================================================
# БЛОК №2 - РАЗДЕЛ №3: CHAMP: метод квалификации клиентов
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_2_section_3_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_2_test_3_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №2 - Раздел №3: CHAMP: метод квалификации клиентов"""
    try:
        await callback.message.delete()
        intro_text = get_block2_section_3_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(10)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_2_test_3_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_2_test_3_ready_for_test_handl] Произошла ошибка {e}") 
        

@router.on_button_callback(state(TrainingStates.block_2_test_3_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_2_test_3_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 2 Тест 3 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_2_test_3_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_2_test_3_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_2_test_3_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_2_test_3_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_8')
        cursor.change_state(TrainingStates.block_2_test_3_testing)
    
    except Exception as e:
        logger.error(f"[training_block_2_test_3_handler] Произошла ошибка {e}")
   

# ============================================================================
# БЛОК №2 - РАЗДЕЛ №4: Видео-инструкция по AI-Агенту для CHAMP
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_2_section_4_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_2_go_to_final_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №2 - Раздел №4: Видео-инструкция по AI-Агенту для CHAMP предложение 
    для перехода к финальному тесту"""
    try:
        await callback.message.delete()
        intro_text = get_block2_section_4_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        current_course = get_current_course(cursor)
        
        await asyncio.sleep(15) # 2
        game = GamificationService(current_course)
        game.increment_lessons_completed(callback.user_id, increment_lesson=1)
        
        continue_text = "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇"
    
        kb = next_to_educ_to_part_kb()
    
        await callback.send(continue_text, keyboard=kb)
        cursor.change_state(TrainingStates.block2_final_test)
                
        # test_text = go_to_test_1_text()
        # await callback.send(test_text, keyboard=start_test_kb())
        
        # cursor.change_state(TrainingStates.block_2_test_3_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_2_test_3_ready_for_test_handl] Произошла ошибка {e}") 
        


@router.on_button_callback(state(TrainingStates.block2_final_test), lambda data: data.payload == "next_educ_to_part_2")
async def continue_after_block2_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №2 - Клиент и ЦА. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block2_handler] Стартовал")
        current_course = get_current_course(cursor)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_2()
        
        #await callback.send(text)
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block2_questions)
        
        # await asyncio.sleep(2)
        # await start_block2_final_test_handler(callback, cursor)
        return
        
    
    except Exception as e:
        logger.error(f"[continue_after_block2_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.block2_questions), lambda data: data.payload == 'to_final_test')
async def start_block2_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №2"""
    try:
        logger.info(f"[INFO][start_block2_final_test_handler] Стартовал")
        text = get_text_start_final_test_block_2()
        
        data = cursor.get_data()
        if not data:
            data = dict()
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_2_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block2_final_test_handler] Произошла ошибка {e}")
    

@router.on_message(state(TrainingStates.block2_questions))
async def answer_block2_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 2 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block2_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block2_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №2:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block2_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )


@router.on_message(state(TrainingStates.block_2_final_testing))
async def block2_final_testing_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 2 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block2_question_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_10')
        
        # Форматируем ответ
        # logger.info(f"[INFO][answer_block2_question_handler] Форматируем ответ") 
        # response_text = (
        #     f"💡 **Ответ по Блоку №2:**\n\n"
        #     f"{answer}\n\n"
        #     "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        # )
        
        # await message.send(response_text, keyboard=final_start_test_kb())
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block2_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )

# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ № 2 (10 закрытых + 5 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_2_final_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block2_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по Блоку 2"""
    try:
        logger.info(f"[INFO][start_testing_block2_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_2('close')
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_2('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block2_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_2_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_2_final_testing"
                )
            
        logger.info(f'[start_testing_block2_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block2_handler] Отправляем первый закрытый вопрос')
        await send_question_step_12(callback, cursor, "section_10")
       
        cursor.change_state(TrainingStates.block_2_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block2_handler] Произошла ошибка {e}") 




#####################################################

@router.on_button_callback(state(TrainingStates.block_7_final_testing))
@router.on_button_callback(state(TrainingStates.block_6_final_testing))
@router.on_button_callback(state(TrainingStates.block_5_final_testing))
@router.on_button_callback(state(TrainingStates.block_4_final_testing))
@router.on_button_callback(state(TrainingStates.block_3_final_testing))
@router.on_button_callback(state(TrainingStates.block_2_final_testing))
@router.on_button_callback(state(TrainingStates.step_12_testing))
async def final_process_answer_handler(callback: Callback, cursor: FSMCursor):
    """Обрабатывает ответ пользователя в финальном блоке тестирования"""
    try:
        logger.info(f"[INFO][final_process_answer_handler] Стартовал")   
        data:dict = cursor.get_data()
        #logger.info(f"[INFO][final_process_answer_handler] {data=}")   
        answers = data.get("open_answers", [])
        closed_answers = data.get("closed_answers", [])
        current = data.get("current_question")
        correct = data.get("correct")
        migration_state = data.get('migration_state')
        
        call_answer = callback.payload
        logger.info(f"[INFO][final_process_answer_handler] {answers=}\n{current=}\n{call_answer=}")
        if '::' in callback.payload:
            user_answer = call_answer.split('::')[1] if "correct" not in call_answer else call_answer.split('::')[1].split("_")[0]
            logger.info(f"[INFO][final_process_answer_handler] {user_answer=}\n{call_answer=}\n{correct=}")
            #answers.append(user_answer)
            closed_answers.append(user_answer)
            logger.info(f"[INFO][final_process_answer_handler] Сохраняем ответ пользователя и переходим к следующему вопросу")
            #data.update(open_answers=answers, current_question=current + 1)
            data.update(closed_answers=closed_answers, current_question=current + 1)
            cursor.change_data(data)
            logger.info(f'[INFO][final_process_answer_handler] state={cursor.get_state()}')
            if migration_state == 'step_12_testing':
                await send_question_step_12(callback, cursor, 'final_test')
            elif migration_state == 'block_2_final_testing':
                await send_question_step_12(callback, cursor, 'section_10')
            elif migration_state == 'block_3_final_testing':
                await send_question_step_12(callback, cursor, 'section_17')
            elif migration_state == 'block_4_final_testing':
                await send_question_step_12(callback, cursor, 'section_22')
            elif migration_state == 'block_5_final_testing':
                await send_question_step_12(callback, cursor, 'section_39')
            elif migration_state == 'block_6_final_testing':
                await send_question_step_12(callback, cursor, 'section_41')
            elif migration_state == 'block_7_final_testing':
                await send_question_step_12(callback, cursor, 'section_42')
        elif callback.payload == 'to_final_test':
            if migration_state == 'step_12_testing':
                await send_question_step_12(callback, cursor, 'final_test')
            elif migration_state == 'block_2_final_testing':
                await send_question_step_12(callback, cursor, 'section_10')
            elif migration_state == 'block_3_final_testing':
                await send_question_step_12(callback, cursor, 'section_17')
            elif migration_state == 'block_4_final_testing':
                await send_question_step_12(callback, cursor, 'section_22')
            elif migration_state == 'block_5_final_testing':
                await send_question_step_12(callback, cursor, 'section_39')
            elif migration_state == 'block_6_final_testing':
                await send_question_step_12(callback, cursor, 'section_41')
            elif migration_state == 'block_7_final_testing':
                await send_question_step_12(callback, cursor, 'section_42')
        
     
    except Exception as e:
        logger.error(f"[ERROR][final_process_answer_handler] Произошла ошибка {e}")  


# ============================================================================
# БЛОК №3: Технология продаж: этапы, скрипты и работа с возражениями
# ============================================================================

# РАЗДЕЛ № 1 ------------------

@router.on_button_callback(state(TrainingStates.block_2_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_3_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик завершения обучения по 2 блоку и перехода к блоку № 3 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_3_handler] Стартовал')
        #cursor.change_state(TrainingStates.block3_section1_ready)
        if continue_flag:
            intro_text = get_block3_intro_text()
            await callback.send(intro_text)
            await asyncio.sleep(10) # 2 
        
        await callback.message.delete()
        
        intro_text = get_block3_section_1_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, format="markdown", keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_1_ready_for_test)
        
        
        # cursor.change_state(TrainingStates.block3_start)
        
        # if await debounce_button_max(callback, cursor):
        #     return
        
        # intro_text = get_block3_intro_text()
        
        # kb = next_to_educ_to_part_kb()
        # await callback.send(intro_text, format='markdown', disable_link_preview=True, keyboard=kb)
                       
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_2_handler] Произошла ошибка {e}')


# ============================================================================
# БЛОК №3 - РАЗДЕЛ №1: Воронка продаж: 8 этапов от лида до закрытия сделки
# ============================================================================


@router.on_button_callback(state(TrainingStates.block3_section1_ready), lambda data: data.payload == "next_educ_to_part_2")
async def go_to_block3_section1_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик перехода к изучению раздела 1 блока 3"""
    try:
        logger.info(f'[INFO][go_to_block3_section1_handler] Стартовал')
        await callback.message.delete()
        
        intro_text = get_block3_section_1_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, format="markdown", keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_1_ready_for_test)
    
    except Exception as e:
        logger.error(f'[ERROR][go_to_block3_section1_handler] Произошла ошибка {e}')



@router.on_button_callback(state(TrainingStates.block_3_test_1_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_1_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 1 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_1_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_1_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_1_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_1_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_8')
        cursor.change_state(TrainingStates.block_3_test_1_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_1_handler] Произошла ошибка {e}")
        


# ============================================================================
# БЛОК №3 - РАЗДЕЛ №2: Работа с возражениями клиентов и конкуренты
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_section_1_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_3_test_2_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №2 - Раздел №2: Работа с возражениями клиентов и конкуренты"""
    try:
        await callback.message.delete()
        intro_text = get_block3_section_2_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_2_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_3_test_2_ready_for_test_handl] Произошла ошибка {e}") 
        

@router.on_button_callback(state(TrainingStates.block_3_test_2_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_2_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 2 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_2_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_2_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_2_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_2_handler] после добавления вопросов в state: ')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_12')
        cursor.change_state(TrainingStates.block_3_test_2_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_2_handler] Произошла ошибка {e}")



# ============================================================================
# БЛОК №3 - РАЗДЕЛ №3: Скрипты диалогов: как правильно начать разговор с клиентом
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_section_2_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_3_test_3_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №2 - Раздел №3: Скрипты диалогов: как правильно начать разговор с клиентом"""
    try:
        await callback.message.delete()
        intro_text = get_block3_section_3_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_3_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_3_test_2_ready_for_test_handl] Произошла ошибка {e}") 


@router.on_button_callback(state(TrainingStates.block_3_test_3_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_3_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 3 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_3_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_3_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_3_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_3_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_13')
        cursor.change_state(TrainingStates.block_3_test_3_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_3_handler] Произошла ошибка {e}")

# ============================================================================
# БЛОК №3 - РАЗДЕЛ №4: Психотипы клиентов: как адаптировать стиль общения
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_section_3_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_3_test_4_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №3 - Раздел №4: Психотипы клиентов: как адаптировать стиль общения"""
    try:
        await callback.message.delete()
        intro_text = get_block3_section_4_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_4_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_3_test_2_ready_for_test_handl] Произошла ошибка {e}") 


@router.on_button_callback(state(TrainingStates.block_3_test_4_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_4_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 4 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_4_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_4_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_4_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_4_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_14')
        cursor.change_state(TrainingStates.block_3_test_4_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_3_handler] Произошла ошибка {e}")
        
        
# ============================================================================
# БЛОК №3 - РАЗДЕЛ №5: Шпаргалка менеджера: продукты, проблемы, решения
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_section_4_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_3_test_5_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №3 - Раздел №5: Шпаргалка менеджера: продукты, проблемы, решения"""
    try:
        await callback.message.delete()
        intro_text = get_block3_section_5_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_5_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_3_test_5_ready_for_test_handl] Произошла ошибка {e}") 
        

@router.on_button_callback(state(TrainingStates.block_3_test_5_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_5_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 5 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_5_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_5_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_5_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_5_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_15')
        cursor.change_state(TrainingStates.block_3_test_5_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_5_handler] Произошла ошибка {e}")        
        

# ============================================================================
# БЛОК №3 - РАЗДЕЛ №6: Простой алгоритм работы для менеджера-стажёра
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_section_5_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_3_test_6_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №3 - Раздел №6: Простой алгоритм работы для менеджера-стажёра"""
    try:
        await callback.message.delete()
        intro_text = get_block3_section_6_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_3_test_6_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_3_test_6_ready_for_test_handl] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.block_3_test_6_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_3_test_6_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 3 Тест 6 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_3_test_6_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_3_test_6_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_3_test_6_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_3_test_6_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_17')
        cursor.change_state(TrainingStates.block_3_test_6_testing)
    
    except Exception as e:
        logger.error(f"[training_block_3_test_6_handler] Произошла ошибка {e}")
               

        
@router.on_button_callback(state(TrainingStates.block3_final_test), lambda data: data.payload.split('::')[1] == "not_first")
async def continue_after_section17_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №3 - Продукт. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_section17_handler] Стартовал")
        current_course = get_current_course(cursor)
        await callback.message.delete()
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_3()
        
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block3_questions)
    
    except Exception as e:
        logger.error(f"[continue_after_section17_handler] Произошла ошибка {e}")


@router.on_button_callback(state(TrainingStates.block3_final_test), lambda data: data.payload == "next_educ_to_part_2")
async def continue_after_block3_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №3. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block3_handler] Стартовал")
        current_course = get_current_course(cursor)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_3()
        
        await callback.send(text)
        #await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block3_questions)
        
        await asyncio.sleep(5)
        await start_block3_final_test_handler(callback, cursor)
        return
        
    
    except Exception as e:
        logger.error(f"[continue_after_block3_handler] Произошла ошибка {e}")

        

@router.on_button_callback(state(TrainingStates.block3_questions), lambda data: data.payload == 'to_final_test')
async def start_block3_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №3"""
    try:
        logger.info(f"[INFO][start_block3_final_test_handler] Стартовал")
        text = get_text_start_final_test_block_3()
        
        data = cursor.get_data()
        if not data:
            data = dict()
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_3_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block23_final_test_handler] Произошла ошибка {e}")



@router.on_message(state(TrainingStates.block3_questions))
async def answer_block3_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 3 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block3_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block3_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №3:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block3_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )

        

@router.on_message(state(TrainingStates.block_3_final_testing))
async def block3_final_testing_handler(message: Message, cursor: FSMCursor):
    """Обработка ответов на открытые вопросы по Блоку 3 в финальном тесте через RAG + Claude"""
    try:
        logger.info(f"[INFO][block3_final_testing_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_17')
        
        # Форматируем ответ
        # logger.info(f"[INFO][answer_block2_question_handler] Форматируем ответ") 
        # response_text = (
        #     f"💡 **Ответ по Блоку №2:**\n\n"
        #     f"{answer}\n\n"
        #     "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        # )
        
        # await message.send(response_text, keyboard=final_start_test_kb())
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][block3_final_testing_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте набрать свой ответ ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb())
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][block3_final_testing_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте набрать свой ответ ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )
        
# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ № 3 (10 закрытых + 5 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_3_final_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block3_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по Блоку 3"""
    try:
        logger.info(f"[INFO][start_testing_block3_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_3('close')
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_3('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block3_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_3_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_3_final_testing"
                )
            
        logger.info(f'[start_testing_block3_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block3_handler] Отправляем первый закрытый вопрос')
        await send_question_step_12(callback, cursor, "section_17")

        cursor.change_state(TrainingStates.block_3_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block3_handler] Произошла ошибка {e}") 
        

# ============================================================================
# БЛОК №4: Технология продаж: этапы, скрипты и работа с возражениями - 
# РАЗДЕЛ №1: Теория по расчёту стоимости противопожарного стекла и стеклопакета
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_3_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_4_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик завершения обучения по 3 блоку и перехода к блоку № 4 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_4_handler] Стартовал')
        
        #cursor.change_state(TrainingStates.block3_section1_ready)
        if continue_flag:
            intro_text = get_block4_intro_text()
            await callback.send(intro_text)
            await asyncio.sleep(10) # 2 
        
        await callback.message.delete()
        
        intro_text = get_block4_section_1_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(10)
        await callback.send(test_text, format="markdown", keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_4_test_1_ready_for_test)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_4_handler] Произошла ошибка {e}')



@router.on_button_callback(state(TrainingStates.block4_section1_ready), lambda data: data.payload == "next_educ_to_part_2")
async def go_to_block4_section1_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик перехода к изучению раздела 1 блока 4"""
    try:
        logger.info(f'[INFO][go_to_block4_section1_handler] Стартовал')
        await callback.message.delete()
        
        intro_text = get_block4_section_1_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(10)
        await callback.send(test_text, format="markdown", keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_4_test_1_ready_for_test)
    
    except Exception as e:
        logger.error(f'[ERROR][go_to_block4_section1_handler] Произошла ошибка {e}')


@router.on_button_callback(state(TrainingStates.block_4_test_1_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_4_test_1_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 4 Тест 1 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_4_test_1_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_4_test_1_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_4_test_1_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_4_test_1_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_18')
        cursor.change_state(TrainingStates.block_4_test_1_testing)
    
    
    except Exception as e:
        logger.error(f"[training_block_4_test_1_handler] Произошла ошибка {e}")


# ============================================================================
# БЛОК №4 - РАЗДЕЛ №2: Методичка по расчёту стоимости противопожарного стекла
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_4_section_1_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_4_test_2_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №4 - Раздел №2: Методичка по расчёту стоимости противопожарного стекла/стеклопакета"""
    try:
        await callback.message.delete()
        intro_text = get_block4_section_2_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_4_test_2_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_4_test_2_ready_for_test_handl] Произошла ошибка {e}") 
        

@router.on_button_callback(state(TrainingStates.block_4_test_2_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_4_test_2_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 4 Тест 2 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_4_test_2_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_4_test_2_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_4_test_2_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_4_test_2_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_19')
        cursor.change_state(TrainingStates.block_4_test_2_testing)
    
    except Exception as e:
        logger.error(f"[training_block_4_test_2_handler] Произошла ошибка {e}")

# ============================================================================
# БЛОК №4 - РАЗДЕЛ №3: Инструкция по заполнению примечаний к работам для распределения стоимости
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_4_section_2_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_4_test_3_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №4 - Раздел №3: Инструкция по заполнению примечаний к работам для распределения стоимости"""
    try:
        await callback.message.delete()
        intro_text = get_block4_section_3_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_4_test_3_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_4_test_2_ready_for_test_handl] Произошла ошибка {e}") 


@router.on_button_callback(state(TrainingStates.block_4_test_3_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_4_test_3_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 4 Тест 3 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_4_test_3_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_4_test_3_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_4_test_3_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_4_test_3_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_20')
        cursor.change_state(TrainingStates.block_4_test_3_testing)
    
    except Exception as e:
        logger.error(f"[training_block_4_test_3_handler] Произошла ошибка {e}")
        


# ============================================================================
# БЛОК №4 - РАЗДЕЛ №4: Быстрый расчёт: ИИ-Агент
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_4_section_3_next), lambda data: data.payload.split('::')[1] == "not_first")
async def block_4_test_4_ready_for_test_handl(callback: Callback, cursor: FSMCursor):
    """БЛОК №4 - Раздел №4: Быстрый расчёт: ИИ-Агент"""
    try:
        await callback.message.delete()
        intro_text = get_block4_section_4_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        test_text = go_to_test_1_text(5)
        await callback.send(test_text, keyboard=start_test_kb())
        
        cursor.change_state(TrainingStates.block_4_test_4_ready_for_test)
        
        
    except Exception as e:
        logger.error(f"[ERROR][block_4_test_4_ready_for_test_handl] Произошла ошибка {e}")

        
@router.on_button_callback(state(TrainingStates.block_4_test_4_ready_for_test), lambda data: data.payload == "start_test")
async def training_block_4_test_4_handler(callback: Callback, cursor: FSMCursor):
    """БЛО№ № 4 Тест 4 - Начало тестирования"""
    try:
        logger.info("[INFO][training_block_4_test_4_handler] Стартовал")
        # if await debounce_button_max(callback, cursor):
        #     logger.info(f"[training_step_4_handler] Идет обработка нажмите позднее")
        #     return
        
        questions = get_block_4_test_4_quests()
        logger.info(f"Вопросы для тестирования получены:\nПервый вопрос: {questions[0]}")
        
        data = cursor.get_data()
        logger.info(f'[training_block_4_test_4_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(questions=questions, current_question=0, answers=[])
        else:
            data = dict()
            data.update(questions=questions, current_question=0, answers=[])
            
        logger.info(f'[training_block_4_test_4_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)
        # Отправляем первый вопрос
        await send_question(callback, cursor, 'section_21')
        cursor.change_state(TrainingStates.block_4_test_4_testing)
    
    except Exception as e:
        logger.error(f"[training_block_4_test_4_handler] Произошла ошибка {e}")


@router.on_button_callback(state(TrainingStates.block4_final_test), lambda data: data.payload.split('::')[1] == "not_first")
async def continue_after_section21_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №4. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_section21_handler] Стартовал")
        current_course = get_current_course(cursor)
        await callback.message.delete()
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_4()
        
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block4_questions)
    
    except Exception as e:
        logger.error(f"[continue_after_section21_handler] Произошла ошибка {e}")        



@router.on_button_callback(state(TrainingStates.block4_final_test), lambda data: data.payload == "next_educ_to_part_2")
async def continue_after_block4_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №4. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block4_handler] Стартовал")
        current_course = get_current_course(cursor)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_4()
        
        await callback.send(text)
        #await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block4_questions)
        
        await asyncio.sleep(2)
        await start_block4_final_test_handler(callback, cursor)
        return
        
    
    except Exception as e:
        logger.error(f"[continue_after_block4_handler] Произошла ошибка {e}") 
        
        
@router.on_button_callback(state(TrainingStates.block4_questions), lambda data: data.payload == 'to_final_test')
async def start_block4_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №4"""
    try:
        logger.info(f"[INFO][start_block4_final_test_handler] Стартовал")
        text = get_text_start_final_test_block_4()
        
        data = cursor.get_data()
        if not data:
            data = dict()
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_4_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block4_final_test_handler] Произошла ошибка {e}")


@router.on_message(state(TrainingStates.block4_questions))
async def answer_block4_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 4 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block4_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block4_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №3:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block4_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )

       
@router.on_message(state(TrainingStates.block_4_final_testing))
async def block4_final_testing_handler(message: Message, cursor: FSMCursor):
    """Обработка ответов на открытые вопросы по Блоку 4 в финальном тесте через RAG + Claude"""
    try:
        logger.info(f"[INFO][block4_final_testing_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_22')
        
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][block4_final_testing_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте набрать свой ответ ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb())
        

# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ № 3 (10 закрытых + 5 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_4_final_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block4_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по Блоку 4"""
    try:
        logger.info(f"[INFO][start_testing_block4_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_4('close')
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_4('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block4_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_4_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_4_final_testing"
                )
            
        logger.info(f'[start_testing_block4_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block4_handler] Отправляем первый закрытый вопрос')
        await send_question_step_12(callback, cursor, "section_22")

        cursor.change_state(TrainingStates.block_4_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block4_handler] Произошла ошибка {e}")         


# ============================================================================
# БЛОК №5: Работа с Битрикс 
# РАЗДЕЛ №1: 15 видео уроков
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_4_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_5_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик завершения обучения по 4 блоку и перехода к блоку № 5 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_5_handler] Стартовал')
        
        if continue_flag:
            intro_text = get_block5_intro_text()
            await callback.send(intro_text)
            await asyncio.sleep(15) # 2
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id
                
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video1()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_1")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_2_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_5_handler] Произошла ошибка {e}')


@router.on_button_callback(state(TrainingStates.block_5_video_2_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_2_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 2"""
    try:
        logger.info(f'[INFO][block_5_video_2_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id      
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video2()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_2")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_3_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_2_handler] Произошла ошибка {e}')
        
        
@router.on_button_callback(state(TrainingStates.block_5_video_3_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_3_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 3"""
    try:
        logger.info(f'[INFO][block_5_video_3_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id       
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video3()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_3")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_4_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_3_handler] Произошла ошибка {e}')


@router.on_button_callback(state(TrainingStates.block_5_video_4_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_4_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 4"""
    try:
        logger.info(f'[INFO][block_5_video_4_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id
                
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video4()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_4")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_5_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_4_handler] Произошла ошибка {e}')        
         
         
@router.on_button_callback(state(TrainingStates.block_5_video_5_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_5_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 5"""
    try:
        logger.info(f'[INFO][block_5_video_5_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id        
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video5()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_5")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_6_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_5_handler] Произошла ошибка {e}')   
        

@router.on_button_callback(state(TrainingStates.block_5_video_6_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_6_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 6"""
    try:
        logger.info(f'[INFO][block_5_video_6_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id          
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video6()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_6")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_7_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_6_handler] Произошла ошибка {e}')         
     
        
@router.on_button_callback(state(TrainingStates.block_5_video_7_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_7_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 7"""
    try:
        logger.info(f'[INFO][block_5_video_7_handler] Стартовал')
        
        current_course = get_current_course(cursor)
        
        game = GamificationService(current_course)
        user_id = callback.user_id            
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video7()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_7")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_8_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_7_handler] Произошла ошибка {e}')          


@router.on_button_callback(state(TrainingStates.block_5_video_8_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_8_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 8"""
    try:
        logger.info(f'[INFO][block_5_video_8_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id        
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video8()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_8")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_9_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_8_handler] Произошла ошибка {e}')
        

@router.on_button_callback(state(TrainingStates.block_5_video_9_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_9_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 9"""
    try:
        logger.info(f'[INFO][block_5_video_9_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id             
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video9()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_9")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_10_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_9_handler] Произошла ошибка {e}')              


@router.on_button_callback(state(TrainingStates.block_5_video_10_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_10_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 10"""
    try:
        logger.info(f'[INFO][block_5_video_10_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id               
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video10()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_10")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_11_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_10_handler] Произошла ошибка {e}')


@router.on_button_callback(state(TrainingStates.block_5_video_11_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_11_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 11"""
    try:
        logger.info(f'[INFO][block_5_video_11_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id          
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video11()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_11")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_12_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_11_handler] Произошла ошибка {e}')        


@router.on_button_callback(state(TrainingStates.block_5_video_12_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_12_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 12"""
    try:
        logger.info(f'[INFO][block_5_video_12_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id          
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video12()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_12")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_13_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_12_handler] Произошла ошибка {e}')
        
        
@router.on_button_callback(state(TrainingStates.block_5_video_13_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_13_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 13"""
    try:
        logger.info(f'[INFO][block_5_video_13_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id              
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video13()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_13")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_14_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_13_handler] Произошла ошибка {e}')
        
        
@router.on_button_callback(state(TrainingStates.block_5_video_14_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_14_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 14"""
    try:
        logger.info(f'[INFO][block_5_video_14_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id          
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video14()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_14")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block_5_video_15_viewer)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_14_handler] Произошла ошибка {e}')
        

@router.on_button_callback(state(TrainingStates.block_5_video_15_viewer), lambda data: data.payload.split('::')[1] == "not_first")
async def block_5_video_15_handler(callback: Callback, cursor: FSMCursor):
    """БЛОК № 5 - Переход  к просмотру видео № 15"""
    try:
        logger.info(f'[INFO][block_5_video_15_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id           
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
          
        intro_text = get_block5_intro_video15()
        
        await callback.send(intro_text)
        
        game.mark_video_section_viewed(user_id, "video_section_15")
        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
                 
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )  

        cursor.change_state(TrainingStates.block5_final_test)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][block_5_video_15_handler] Произошла ошибка {e}')
        


@router.on_button_callback(state(TrainingStates.block5_final_test), lambda data: data.payload.split('::')[1] == "not_first")
async def continue_after_block5_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №5 - Клиент и ЦА. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block5_handler] Стартовал")
        logger.info(f"[continue_after_block5_handler] Прибавляем к прогрессу прохождения курса 15 видео-уроков")
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id
        
        current_course = get_current_course(cursor)
               
        lessons_completed = game.get_lessons_completed(user_id) if current_course != "Другой сотрудник" else game.get_lessons_completed(user_id, "Другой сотрудник")
        
        #lessons_completed = game.get_lessons_completed(user_id)
        if lessons_completed < 38:
            game.increment_lessons_completed(user_id, increment_lesson=15)    
        
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_5()
        
        #await callback.send(text)
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block5_questions)
        
        # await asyncio.sleep(2)
        # await start_block2_final_test_handler(callback, cursor)
        return
        
    
    except Exception as e:
        logger.error(f"[continue_after_block5_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.block5_questions), lambda data: data.payload == 'to_final_test')
async def start_block5_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №5"""
    try:
        logger.info(f"[INFO][start_block5_final_test_handler] Стартовал")
        text = get_text_start_final_test_block_5()
        
        data = cursor.get_data()
        if not data:
            data = {}
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_5_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block5_final_test_handler] Произошла ошибка {e}")
               

@router.on_message(state(TrainingStates.block5_questions))
async def answer_block5_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 5 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block5_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block5_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №5:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block5_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )
        

@router.on_message(state(TrainingStates.block_5_final_testing))
async def block5_final_testing_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 5 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block5_question_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_39')
        
        # Форматируем ответ
        # logger.info(f"[INFO][answer_block2_question_handler] Форматируем ответ") 
        # response_text = (
        #     f"💡 **Ответ по Блоку №2:**\n\n"
        #     f"{answer}\n\n"
        #     "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        # )
        
        # await message.send(response_text, keyboard=final_start_test_kb())
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block2_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )                                               


# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ № 5 (10 закрытых + 5 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_5_final_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block5_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по Блоку 5"""
    try:
        logger.info(f"[INFO][start_testing_block5_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_5('close')
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_5('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block5_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_5_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_5_final_testing"
                )
            
        logger.info(f'[start_testing_block5_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block5_handler] Отправляем первый закрытый вопрос')
        await send_question_step_12(callback, cursor, "section_39")

        cursor.change_state(TrainingStates.block_5_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block5_handler] Произошла ошибка {e}") 


# ============================================================================
# БЛОК №6: Power BI: инструмент для аналитики
# ============================================================================
'''
@router.on_button_callback(state(TrainingStates.block_5_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_6_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик завершения обучения по 5 блоку и перехода к блоку № 6 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_6_handler] Стартовал')
        #cursor.change_state(TrainingStates.block4_start)
        
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
        intro_text = get_block6_intro_text()
        
        kb = next_to_educ_to_part_kb()
        await callback.send(intro_text, format='markdown', disable_link_preview=True, keyboard=kb)
        cursor.change_state(TrainingStates.block_6_section_1_next)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_6_handler] Произошла ошибка {e}')
'''     

#@router.on_button_callback(state(TrainingStates.block_6_section_1_next), lambda data: data.payload == "next_educ_to_part_2")        
@router.on_button_callback(state(TrainingStates.block_5_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_6_section_1_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик единственного учебного раздела блока 6 и переход к завершению 
    обучения по 5 блоку и перехода к блоку № 6 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_6_section_1_handler] Стартовал')
        if continue_flag:
            intro_text = get_block6_intro_text()
            await callback.send(intro_text, disable_link_preview=True)
            await asyncio.sleep(10) # 2
        #cursor.change_state(TrainingStates.block4_start)
        
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        intro_text = get_block6_section_1_intro_text()  
        await callback.send(intro_text, disable_link_preview=True)
        
        await asyncio.sleep(15) # 2
        
        kb = next_to_educ_to_part_kb()
        await callback.send(intro_text, format='markdown', disable_link_preview=True, keyboard=kb)
        cursor.change_state(TrainingStates.block_6_final_test)
               
        return
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_6_section_1_handler] Произошла ошибка {e}')
        

@router.on_button_callback(state(TrainingStates.block_6_final_test), lambda data: data.payload == "next_educ_to_part_2")
async def continue_after_block6_handler(callback: Callback, cursor: FSMCursor):
    """Завершение Блока №6 - Клиент и ЦА. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block6_handler] Стартовал")
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id
        
        current_course = get_current_course(cursor)
               
        lessons_completed = game.get_lessons_completed(user_id) if current_course != "Другой сотрудник" else game.get_lessons_completed(user_id, "Другой сотрудник")
        if lessons_completed < 41:
            game.increment_lessons_completed(user_id, increment_lesson=1)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_6()
        
        #await callback.send(text)
        await callback.send(text, keyboard=final_start_test_kb())
        cursor.change_state(TrainingStates.block6_questions)
        
        # await asyncio.sleep(2)
        # await start_block2_final_test_handler(callback, cursor)
        return
        
    
    except Exception as e:
        logger.error(f"[continue_after_block6_handler] Произошла ошибка {e}")
        

@router.on_button_callback(state(TrainingStates.block6_questions), lambda data: data.payload == 'to_final_test')
async def start_block6_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №6"""
    try:
        logger.info(f"[INFO][start_block6_final_test_handler] Стартовал")
        text = get_text_start_final_test_block_6()
        
        data = cursor.get_data()
        if not data:
            data = dict()
        data.update(current_question=0)
        cursor.change_data(data)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_6_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block6_final_test_handler] Произошла ошибка {e}")
        

@router.on_message(state(TrainingStates.block6_questions))
async def answer_block6_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 6 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block6_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block6_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №6:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        )
        
        await message.send(response_text, keyboard=final_start_test_kb(), format='markdown')
                
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block6_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )

        
@router.on_message(state(TrainingStates.block_6_final_testing))
async def block6_final_testing_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 6 через RAG + Claude"""
    try:
        logger.info(f"[INFO][block6_final_testing_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_41')
        
        # Форматируем ответ
        # logger.info(f"[INFO][answer_block2_question_handler] Форматируем ответ") 
        # response_text = (
        #     f"💡 **Ответ по Блоку №2:**\n\n"
        #     f"{answer}\n\n"
        #     "➡️ Задайте следующий вопрос или нажмите 📝 **Перейти к тестированию**"
        # )
        
        # await message.send(response_text, keyboard=final_start_test_kb())
        
        # Остаёмся в состоянии block1_questions для непрерывного диалога
         
    
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][block6_final_testing_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )                         
        
# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО БЛОКУ № 6 (10 закрытых + 5 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block_6_final_testing), lambda data: data.payload == 'start_final_test')
async def start_testing_block6_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по Блоку 6"""
    try:
        logger.info(f"[INFO][start_testing_block6_handler] Стартовал")
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_6('close') 
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_6('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block6_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_6_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_6_final_testing"
                )
            
        logger.info(f'[start_testing_block6_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block6_handler] Отправляем первый закрытый вопрос')
        await send_question_step_12(callback, cursor, "section_41")

        cursor.change_state(TrainingStates.block_6_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block6_handler] Произошла ошибка {e}") 


# ============================================================================
# БЛОК №7: Финальный этап обучения
# ============================================================================

@router.on_button_callback(state(TrainingStates.block_6_final_testing), lambda data: data.payload == "next_educ_to_part_2")
async def start_block_7_handler(callback: Callback, cursor: FSMCursor, continue_flag:bool=False):
    """Обработчик завершения обучения по 6 блоку и перехода к блоку № 7 при нажатии на кнопку ПРОДОЛЖИТЬ ОБУЧЕНИЕ"""
    try:
        logger.info(f'[INFO][start_block_7_handler] Стартовал')
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id
        
        current_course = get_current_course(cursor)
               
        lessons_completed = game.get_lessons_completed(user_id) if current_course != "Другой сотрудник" else game.get_lessons_completed(user_id, "Другой сотрудник")
        
        #lessons_completed = game.get_lessons_completed(user_id)
        if lessons_completed < 41:
            game.increment_lessons_completed(user_id, increment_lesson=1)
        #cursor.change_state(TrainingStates.block4_start)
        
        # if await debounce_button_max(callback, cursor):
        #     return
        await callback.message.delete()
        
        # intro_text = get_block7_intro_text()
        
        # await callback.send(intro_text)
        if continue_flag:
            intro_text = get_block7_intro_text()
            await callback.send(intro_text)
        await asyncio.sleep(15) # 2
        
               
        await continue_after_block7_handler(callback, cursor)
        
    except Exception as e:
        logger.error(f'[ERROR][start_block_6_handler] Произошла ошибка {e}')
        
        

async def continue_after_block7_handler(callback: Callback, cursor: FSMCursor):
    """Блока №7 - Финальный этап обучения. Переход к вопросам или финальному тесту"""
    try:
        logger.info(f"[continue_after_block7_handler] Стартовал")
        current_course = get_current_course(cursor)
        # Проверяем загрузку базы знаний
        rag = RAGService()
        stats = rag.get_stats()
        
        if not stats['is_loaded']:
            await callback.send(
                "❌ База знаний не загружена. Обратитесь к администратору.",
                keyboard=main_menu_keyboard(current_course)
            )
            cursor.clear()
            return
        
        text = get_text_to_final_test_block_7()
        
        #await callback.send(text)
        await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block7_questions)
        
    except Exception as e:
        logger.error(f"[continue_after_block7_handler] Произошла ошибка {e}")
        
'''
@router.on_button_callback(state(TrainingStates.block7_questions), lambda data: data.payload == 'to_final_test')
async def start_block7_final_test_handler(callback: Callback, cursor: FSMCursor):
    """Переход к финальному тесту по Блоку №7"""
    try:
        logger.info(f"[INFO][start_block7_final_test_handler] Стартовал")
        #text = get_text_start_final_test_block_6()
        
        data = cursor.get_data()
        data.update(current_question=0)
        cursor.change_data(data)
        #await callback.send(text, keyboard=final_test_kb())
        cursor.change_state(TrainingStates.block_7_final_testing)
           
    
    except Exception as e:
        logger.error(f"[ERROR][start_block7_final_test_handler] Произошла ошибка {e}")
'''        

@router.on_message(state(TrainingStates.block7_questions))
async def answer_block7_question_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 7 через RAG + Claude"""
    try:
        logger.info(f"[INFO][answer_block7_question_handler] Стартовал")   
        # Показываем процесс
        thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        rag = RAGService()
        answer = await rag.answer_question(message.body.text)
        
        await thinking_msg.delete() 
        
        # Форматируем ответ
        logger.info(f"[INFO][answer_block7_question_handler] Форматируем ответ") 
        response_text = (
            f"💡 **Ответ по Блоку №7:**\n\n"
            f"{answer}\n\n"
            "➡️ Задайте следующий вопрос или нажмите 🚀 **Начать тест**"
        )
              
        await message.send(response_text, keyboard=final_test_kb(), format='markdown')
                
    
    except Exception as e:
        await thinking_msg.delete()
        logger.error(f"[ERROR][answer_block7_question_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )
        

@router.on_message(state(TrainingStates.block_7_final_testing))
async def block7_final_testing_handler(message: Message, cursor: FSMCursor):
    """Ответы на вопросы по Блоку 7 через RAG + Claude"""
    try:
        logger.info(f"[INFO][block7_final_testing_handler] Стартовал")   
        # Показываем процесс
        #thinking_msg = await message.send("🔍 Ищу информацию в базе знаний...")
        
        #rag = RAGService()
        #answer = await rag.answer_question(message.body.text)
        
        #await thinking_msg.delete() 
        await asyncio.sleep(2)
        await send_question_step_12(message, cursor, 'section_42')
        
    except Exception as e:
        #await thinking_msg.delete()
        logger.error(f"[ERROR][block7_final_testing_handler] Произошла ошибка {e}")   

        await message.send(
            "❌ Произошла ошибка при обработке вопроса.\n\n"
            "Попробуйте задать вопрос ещё раз или обратитесь к администратору.",
            keyboard=final_start_test_kb()
        )                                 


# ============================================================================
# ШАГ № __: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПО ВСЕМУ КУРСУ (20 закрытых + 10 открытых)
# ============================================================================


@router.on_button_callback(state(TrainingStates.block7_questions), lambda data: data.payload == 'start_final_test')
async def start_testing_block7_handler(callback: Callback, cursor: FSMCursor):
    """ШАГ № __ - Запуск финального тестирования по итогам обучения"""
    try:
        logger.info(f"[INFO][start_testing_block7_handler] Стартовал")
        cursor.change_state(TrainingStates.block_7_final_testing)
        
        # ЧАСТЬ 1: Закрытые вопросы (10 вопросов с вариантами A/B/C/D)
        closed_questions = get_final_test_block_7('close') 
        
        # ЧАСТЬ 2: Открытые вопросы (5 вопросов с эталонными ответами)
        open_questions = get_final_test_block_7('open')
        
        data = cursor.get_data()
        logger.info(f'[start_testing_block7_handler] до добавления вопросов в state: {data=}')
        # Сохраняем вопросы и начинаем с первого
        if data and isinstance(data, dict):
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_7_final_testing"
                )
        else:
            data = dict()
            data.update(
                closed_questions=closed_questions,
                open_questions=open_questions,
                current_question=0,
                closed_answers=[],  # Ответы на закрытые вопросы
                open_answers=[],    # Ответы на открытые вопросы
                test_stage="closed",  # Начинаем с закрытых вопросов
                migration_state = "block_7_final_testing"
                )
            
        logger.info(f'[start_testing_block7_handler] после добавления вопросов в state: {data=}')  
        cursor.change_data(data)  # !!!!!!!!!!
        # Отправляем первый закрытый вопрос
        logger.info(f'[start_testing_block7_handler] Отправляем первый закрытый вопрос')
        
        await send_question_step_12(callback, cursor, "section_42")
        
        cursor.change_state(TrainingStates.block_7_final_testing)
        

    except Exception as e:
        logger.error(f"[ERROR][start_testing_block7_handler] Произошла ошибка {e}") 

        
#################################################        
   

@router.on_button_callback(state(AnotherEmployerStates.user_type), lambda data: data.payload == 'another_emp')
async def another_employer_training_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку 📚 Обучение по продукту"""
    try:
        state_name = cursor.get_state()
        logger.info(f'{state_name=}')
        await callback.message.delete()
        #await callback.send(text)
        
        logger.info("Cтартовал обработчик нажатия кнопки 📚 Обучение по продукту")
        logger.info(f"[another_employer_training_handler] Определяем прогресс пользователя в обучении")
        
        current_course = get_current_course(cursor)
        game = GamificationService(current_course)
        user_id = callback.user_id
        
        current_course = get_current_course(cursor)
        logger.info(f'{current_course=}')
               
        lessons_completed = game.get_lessons_completed(user_id) if current_course != "Другой сотрудник" else game.get_lessons_completed(user_id, "Другой сотрудник")
        #lessons_completed = game.get_lessons_completed(user_id)
        #lessons_completed = None
        
        if not lessons_completed:
            await flow_another_emp_training_intro(
                lambda text, with_keyboard=None: send(callback, text, with_keyboard)
                )
            return
                
        return
    except Exception as e:
        logger.error(f'Произошла ошибка {e}')    
        


@router.on_button_callback(lambda data: data.payload == 'education')
async def flow_sales_training_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку 📚 Обучение по продажам"""
    try:
        state_name = cursor.get_state()
        logger.info(f'{state_name=}')
        logger.info("Cтартовал обработчик нажатия кнопки 📚 Обучение по продажам")
        logger.info(f"[flow_sales_training_handler] Определяем прогресс пользователя в обучении")
        current_course = get_current_course(cursor)
        logger.info(f'{current_course=}')
        game = GamificationService(current_course)
        user_id = callback.user_id
                       
        lessons_completed = game.get_lessons_completed(user_id) if current_course != "Другой сотрудник" else game.get_lessons_completed(user_id, "Другой сотрудник")
        
        #lessons_completed = game.get_lessons_completed(user_id)
        
        logger.info(f'{lessons_completed=}')
        
        full_completed_lessons = game.get_full_completed_lessons(course_name = current_course, user_id = user_id)
        
        full_block = 1
                
        if not lessons_completed:
            if current_course == 'Обучение по продажам':
                await flow_sales_training_intro(
                    lambda text, with_keyboard=None: send(callback, text, with_keyboard)
                    )
            elif current_course == 'Другой сотрудник':
                await flow_another_emp_training_intro(
                    lambda text, with_keyboard=None: send(callback, text, with_keyboard)
                    )
            return
        
        elif lessons_completed < 7 and current_course == 'Другой сотрудник':
            logger.info(f"[next_education_handler] Обучение по курсу ДРУГОЙ СОТРУДНИК не завершено")
            data = game._load_data()
            logger.info(f'{data=}')
            
        
        elif lessons_completed < 7:
            logger.info(f"[next_education_handler] Обучение по блоку № 1 не завершено")
            full_block = 1
            
                                  
        elif lessons_completed < 12:
            logger.info(f"[next_education_handler] Обучение по блоку № 2 не завершено")
            full_block = 2
            
            
        elif lessons_completed < 19:
            logger.info(f"[next_education_handler] Обучение по блоку № 3 не завершено")
            full_block = 3
            
        elif lessons_completed < 24:
            logger.info(f"[next_education_handler] Обучение по блоку № 4 не завершено")
            full_block = 4
            
        elif lessons_completed < 40:
            logger.info(f"[next_education_handler] Обучение по блоку № 5 не завершено")
            full_block = 5
            
        elif lessons_completed < 42:
            logger.info(f"[next_education_handler] Обучение по блоку № 6 не завершено")
            full_block = 6
            
        elif lessons_completed < 43:
            logger.info(f"[next_education_handler] Обучение по блоку № 7 не завершено")
            full_block = 7
              
        text = (
            f"Вы уже приступили к обучению и в настоящий момент полностью прошли **{full_block - 1} из 7** блоков обучения\n"
            " Вы можете 📚 **Продолжить обучение** \n либо попытаться ⬆️ **Улучшить результат**, нажав на соответствующие  кнопки ниже 👇"
        ) if current_course == 'Обучение по продажам' else (
            f"Вы уже приступили к обучению и в настоящий момент полностью прошли **{full_completed_lessons} из 7** этапов обучения\n"
            " Вы можете 📚 **Продолжить обучение** \n либо попытаться ⬆️ **Улучшить результат**, нажав на соответствующие  кнопки ниже 👇"
        )
        
        
        
        if lessons_completed == 43 and current_course == 'Обучение по продажам':
            logger.info(f"[next_education_handler] Обучение ранее было завершено")
            full_block = 8
            text = (
            f"Вы ранее уже полностью прошли **все 7** блоков обучения\n"
            " Вы можете попытаться ⬆️ **Улучшить результат**, нажав на соответствующую  кнопку ниже 👇\n"
            "либо вернуться в 🏠 **Главное меню**"
            )
            await callback.message.delete()
            await callback.send(text, keyboard=finish_studying_kb())
            return
        
        elif lessons_completed == 7 and current_course == 'Другой сотрудник':
            logger.info(f"[next_education_handler] Обучение по курсу ДРУГОЙ СОТРУДНИК ранее было завершено")
            full_block = 7
            text = (
            f"Вы ранее уже полностью прошли курс обучения **ДРУГОЙ СОТРУДНИК**\n"
            " Вы можете попытаться ⬆️ **Улучшить результат**, нажав на соответствующую  кнопку ниже 👇\n"
            "либо вернуться в 🏠 **Главное меню**"
            )
            await callback.message.delete()
            await callback.send(text, keyboard=finish_studying_kb())
            return
        
        await callback.message.delete()
        if current_course == "Обучение по продажам":
            await callback.send(text, keyboard=continue_studying_kb(full_block))
        elif current_course == "Другой сотрудник":
            await callback.send(text, keyboard=continue_studying_kb(full_completed_lessons))
        
        return
    except Exception as e:
        logger.error(f'Произошла ошибка {e}')    
        
from services.debounce import debounce_button_max   


   
@router.on_button_callback(lambda data: data.payload == "next_education")
async def next_education_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку 📚 Продолжить обучение
    ШАГ 2 - Видео от директора"""
    try:
        logger.info(f"[next_education_handler] Стартовал")
        
        await callback.message.delete()
        
        if await debounce_button_max(callback, cursor):
            logger.info(f"[next_education_handler] Идет обработка нажмите позднее")
            return
        
        text = get_first_day_congrats_text()
        await callback.send(text)

        await asyncio.sleep(15) # 2
        
        kb = KeyboardBuilder().add(CallbackButton(text="📚 Продолжить обучение", payload="next_education::not_first"))
            

        cursor.change_state(TrainingStates.step_2_video)
        
        await callback.send(
            "📚 Вы можете продолжить обучение, нажав кнопку ниже 👇",
            keyboard=kb
        )
                
    except Exception as e:
        logger.error(f"[next_education_handler] Произошла ошибка {e}")         
        

@router.on_button_callback(lambda data: data.payload.split('::')[0] == "continue_studying")
async def continue_studying_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку 📚 Продолжить обучение для реализации возможности
    продолжить с блока, следующего за полностью завершенным"""
    try:
        logger.info(f"[continue_studying_handler] Стартовал")
        current_course = get_current_course(cursor)
        logger.info(f'{current_course=}')
        full_block_id = callback.payload.split("::")[1]
        logger.info(f"[continue_studying_handler] {full_block_id=}")
        if current_course == "Обучение по продажам":
            if full_block_id == '1':
                cursor.change_state(TrainingStates.step_2_video)
                await training_step_3_handler(callback, cursor)
            elif full_block_id == '2':
                cursor.change_state(TrainingStates.step_12_testing)
                await start_block_2_handler(callback, cursor, True)
            elif full_block_id == '3':
                cursor.change_state(TrainingStates.block_2_final_testing)
                await start_block_3_handler(callback, cursor, True)
            elif full_block_id == '4':
                cursor.change_state(TrainingStates.block_3_final_testing)
                await start_block_4_handler(callback, cursor, True)
            elif full_block_id == '5':
                cursor.change_state(TrainingStates.block_4_final_testing)
                await start_block_5_handler(callback, cursor, True)
            elif full_block_id == '6':
                cursor.change_state(TrainingStates.block_5_final_testing)
                await start_block_6_section_1_handler(callback, cursor, True)
            elif full_block_id == '7':
                cursor.change_state(TrainingStates.block_6_final_testing)
                await start_block_7_handler(callback, cursor, True)
        elif current_course == "Другой сотрудник":
            if full_block_id == '1':
                cursor.change_state(TrainingStates.step_6_next)
                await training_step_6_handler(callback, cursor)
            elif full_block_id == '2':
                cursor.change_state(TrainingStates.step_8_next)
                await training_step_8_handler(callback, cursor)
            elif full_block_id == '3':
                cursor.change_state(TrainingStates.step_9_next)
                await training_step_9_handler(callback, cursor)
            elif full_block_id == '4':
                cursor.change_state(TrainingStates.step_10_next)
                await training_step_10_handler(callback, cursor)
            elif full_block_id == '5':
                cursor.change_state(TrainingStates.step_11_next)
                await training_step_11_handler(callback, cursor)
            elif full_block_id == '6':
                cursor.change_state(TrainingStates.step_11_next)
                await continue_after_section6_handler(callback, cursor)
                
            
    except Exception as e:
        logger.error(f"[continue_studying_handler] Произошла ошибка {e}")  
            

@router.on_button_callback(lambda data: data.payload == "start_again")
async def high_result_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопку "⬆️ Улучшить результат"""
    try:
        logger.info(f"[high_result_handler] Стартовал")
        current_course = get_current_course(cursor)
        logger.info(f'{current_course=}')
        game = GamificationService(current_course)
        game.reset_user_course_progress(callback.user_id, current_course)
        if current_course == 'Обучение по продажам':
            await training_step_3_handler(callback, cursor, True)
        elif current_course == 'Другой сотрудник':
            await training_step_3_handler(callback, cursor, True)
            
    except Exception as e:
        logger.error(f"[high_result_handler] Произошла ошибка {e}")  
        


@router.on_button_callback(lambda data: data.startswith("change_department::"))
async def change_department_handler(callback: Callback, cursor: FSMCursor):
    """Обработчик нажатия на кнопки с названиями курсов обучения"""
    try:
        logger.info('Стартовал')
        cursor_data = cursor.get_data()
        status_user = cursor_data.get('status_user')
        logger.info(f'{status_user=}')
        payload_data = callback.payload
        department_name = payload_data.split('::')[1]
        logger.info(f'{department_name=}')
        if department_name == 'in_process':
            text = get_text_in_process()
            kb = change_another_department_kb()
            await callback.send(text, keyboard = kb)
            return
        elif department_name == 'manager':
            await sales_manager_start_handl(callback, cursor)
        elif department_name == 'lawyer':
            logger.info('Ветка ЮРИСТ находится в разработке')
            await callback.send("Ветка ЮРИСТ находится в разработке")
            
        
    except Exception as e:
        logger.error(f"[change_department_handler] Произошла ошибка {e}") 
        
