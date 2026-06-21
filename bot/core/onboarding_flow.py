import asyncio
import time
from aiomax.fsm import FSMCursor
#import logging
from bot.adapters.max.keyboards import next_to_education_kb, tomorrow_kb
from bot.adapters.max.create_bot import logger
from core.content import (
    get_another_emp_training_info_text,
    get_change_course_text,
    get_change_date_text,
    get_first_mess_another_empl,
    get_first_mess_lawyer,
    get_start_text,
    get_about_company_text,
    get_sales_training_intro_text,
    get_sales_training_info_text,
    get_course_intro_text,
    get_block1_intro_text,
    get_block1_section1_intro_text,
    get_block1_section1_questions,
    format_block1_section1_question,
    format_block1_section1_result,
    get_start_text_another_employer,
    get_text_change_department,
    get_text_change_status,
)

#logging.basicConfig(level=logging.INFO)


async def flow_start(send, course_name:str, status_user:str):
    """
    Стартовый сценарий:
    отправить приветственное сообщение в зависимости от названия курса обучения,
    переданного в аргументе.
    """
    #state_name = cursor.get_state()
    print(f'{status_user=}')
    if course_name == "Обучение по продажам":
        text = get_start_text(status_user)
    
    elif course_name == "Другой сотрудник":
        #text = get_start_text_another_employer()
        text = get_start_text(status_user)
        
    if course_name == "Обучение для юриста":
        text = get_start_text(status_user)
    
    #if state_name == "another_employer":
    await send(text=text)
     

async def flow_start_change_kb(send):
    """
    Стартовый сценарий:
    выбрать курс обучения.
    """
    logger.info('Стартовал')
    text = get_text_change_status()
    logger.info(f'{text=}')
    #text = get_change_course_text()
    await send(text)


    
async def flow_start_new_empl_change_kb(send, incomplete_flag: bool = False):
    """
    Стартовый сценарий:
    выбрать курс обучения для тех, кто уже есть в JSON.
    """
    logger.info("Стартовал")
    text = get_text_change_department()
    if incomplete_flag:
        text = text[9:]
    #text = get_change_course_text()
    await send(text)


async def flow_about_company(send):
    """
    Сценарий '🏢 О компании'.
    """
    text = get_about_company_text()
    info = get_change_date_text()
    
    await send(text)
    await asyncio.sleep(5)  # 30 секунд !!!!!!
    
    tom_kb = tomorrow_kb
       
    logger.info("Пытаюсь отправить info")
    await send(info, with_keyboard=tom_kb)
    

async def flow_sales_training_intro(send, user_name: str = "коллега"):
    """
    Сценарий '💼 Обучение по продажам' (ШАГ 1 + инфо).
    """
    try:
        logger.info("[flow_sales_training_intro] стартовал")
        intro = get_sales_training_intro_text(user_name)
        #info = get_change_date_text()
        info = get_sales_training_info_text()
        logger.info(f"{intro=}\n{info=}")
        logger.info("Пытаюсь отправить intro")
        await send(intro, with_keyboard="clear")
        await asyncio.sleep(30)  # 10 секунд 
        # Паузы, задержки и т.п. — в адаптере (MAX), чтобы не блокировать CORE.
        next_kb = next_to_education_kb
        logger.info("Пытаюсь отправить info")
        await send(info, with_keyboard=next_kb)
    except Exception as e:
        logger.error(f"[flow_sales_training_intro] произошла ошибка {e}")



async def flow_another_emp_training_intro(send, user_name: str = "коллега"):
    """
    Сценарий '💼 Обучение по продукту' (ШАГ 1 + инфо).
    """
    try:
        logger.info("[flow_another_emp_training_intro] стартовал")
        intro = get_first_mess_another_empl()
        #intro = get_sales_training_intro_text(user_name)
        #info = get_change_date_text()
        info = get_another_emp_training_info_text()
        logger.info(f"{intro=}\n{info=}")
        logger.info("Пытаюсь отправить intro")
        await send(intro, with_keyboard="clear")
        await asyncio.sleep(30)  # 10 секунд 
        # Паузы, задержки и т.п. — в адаптере (MAX), чтобы не блокировать CORE.
        next_kb = next_to_education_kb
        logger.info("Пытаюсь отправить info")
        await send(info, with_keyboard=next_kb)
    except Exception as e:
        logger.error(f"[flow_another_emp_training_intro] произошла ошибка {e}")
        

async def flow_lawyer_training_intro(send, user_name: str = "коллега"):
    """
    Сценарий '💼 Обучение для юриста' (ШАГ 1 + инфо).
    """
    try:
        logger.info("[flow_lawyer_training_intro] стартовал")
        intro = get_first_mess_lawyer()
        #intro = get_sales_training_intro_text(user_name)
        #info = get_change_date_text()
        info = get_sales_training_info_text()
        logger.info(f"{intro=}\n{info=}")
        logger.info("Пытаюсь отправить intro")
        await send(intro, with_keyboard="clear")
        await asyncio.sleep(10)  # 30 секунд 
        # Паузы, задержки и т.п. — в адаптере (MAX), чтобы не блокировать CORE.
        next_kb = next_to_education_kb
        logger.info("Пытаюсь отправить info")
        await send(info, with_keyboard=next_kb)
    except Exception as e:
        logger.error(f"[flow_lawyer_training_intro] произошла ошибка {e}")
    

# async def flow_course_intro(send):
#     """
#     Сценарий интро курса + интро блока №1.
#     """
#     course = get_course_intro_text()
#     block1 = get_block1_intro_text()

#     await send(course)
#     await send(block1)


# async def flow_block1_section1_intro(send):
#     """
#     Сценарий: Раздел №1 Блока 1.
#     1) Интро раздела + ссылка на материалы.
#     2) Сообщение о том, что дальше будет тест.
#     """
#     intro = get_block1_section1_intro_text()
#     await send(intro)

#     test_text = (
#         "✅ *Отлично!*\n\n"
#         "Если вы уже изучили весь материал по разделу, переходите к тестированию.\n\n"
#         "Вам предстоит ответить на *5 вопросов*, чтобы проверить свои знания.\n\n"
#         "Когда будете готовы, напишите `тест 1` или `раздел 1 тест`."
#     )
#     await send(test_text)


# async def flow_block1_section1_test_start(send, state: dict):
#     """
#     Старт теста по Разделу №1: сохраняем вопросы, сбрасываем прогресс,
#     отправляем первый вопрос (A/B/C/D).
#     """
#     questions = get_block1_section1_questions()
#     state["questions"] = questions
#     state["current"] = 0
#     state["answers"] = []

#     text = format_block1_section1_question(0, questions[0])
#     await send(text)


# async def flow_block1_section1_test_answer(send, state: dict, user_answer: str):
#     """
#     Обрабатывает ответ пользователя (A/B/C/D), задаёт следующий вопрос
#     или показывает результат.
#     """
#     questions = state.get("questions", [])
#     current = state.get("current", 0)
#     answers = state.get("answers", [])

#     if not questions or current >= len(questions):
#         await send(
#             "Тест по этому разделу уже завершён. Напишите `раздел 1`, чтобы повторить материалы."
#         )
#         return

#     # Сохраняем ответ (берём первую букву, на всякий случай)
#     ua = (user_answer or "").strip().upper()
#     if ua:
#         ua = ua[0]
#     answers.append(ua)
#     state["answers"] = answers
#     state["current"] = current + 1

#     # Если есть ещё вопросы — следующий
#     if state["current"] < len(questions):
#         q_index = state["current"]
#         next_q = questions[q_index]
#         text = format_block1_section1_question(q_index, next_q)
#         await send(text)
#         return

#     # Иначе — результаты
#     result_text = format_block1_section1_result(questions, answers)
#     await send(result_text)

#     # Завершаем режим теста
#     state.pop("mode", None)

# from services.rag_service import RAGService

# async def flow_ask_ai_intro(send):
#     """
#     Интро режима 'Задать вопрос' с проверкой базы знаний.
#     """
#     rag = RAGService()
#     stats = rag.get_stats()

#     if not stats["is_loaded"]:
#         await send(
#             "❌ База знаний не загружена. Обратитесь к администратору.\n\n"
#             "Режим вопросов сейчас недоступен."
#         )
#         return False

#     total_size = stats.get("total_size", 0)

#     text = (
#         "🤖 **AI-ассистент компании**\n\n"
#         f"📚 База знаний загружена (**{total_size}** символов)\n\n"
#         "Задавайте вопросы о компании, продукции или процессах.\n"
#         "Я буду отвечать на каждый ваш вопрос.\n\n"
#         "_Например:_\n"
#         "· О чем говорит ФЗ-123?\n"
#         "· Что такое кремнезольная технология?\n"
#         "· Какая гарантия на продукцию?\n\n"
#         "Напишите ваш вопрос ниже 👇\n\n"
#         "Для выхода из режима напишите `стоп` или `выход`."
#     )
#     await send(text)
#     return True


# async def flow_ask_ai(send, question: str):
#     """
#     Ответ на конкретный вопрос через RAG/ИИ.
#     """
#     rag = RAGService()

#     if not question.strip():
#         await send(
#             "Напишите, пожалуйста, ваш вопрос текстом.\n\n"
#             "Например:\n"
#             "· `что такое EIWS-30`\n"
#             "· `как считается стоимость стекла`\n"
#             "· `какие у нас основные этапы сделки`"
#         )
#         return

#     await send("🔎 Ищу ответ в базе знаний, подождите пару секунд...")

#     answer = await rag.answer_question(question)
#     if not answer or not answer.strip():
#         await send(
#             "Пока не нашёл точного ответа в базе знаний.\n\n"
#             "Попробуйте переформулировать вопрос или задать его более конкретно."
#         )
#         return

#     await send(f"💬 **Ответ из базы знаний:**\n\n{answer}")