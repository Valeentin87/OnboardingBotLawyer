import os, sys

from aiomax.buttons import CallbackButton, MessageButton, KeyboardBuilder

COURSES_NAMES = {"Обучение по продажам": 'sales_training',
                 "Другой сотрудник": 'another_employee'}

def test_abcd_keyboard():
    """
    Клавиатура для вопросов A/B/C/D.
    """
    kb = KeyboardBuilder()
    kb.row(
        MessageButton("A"),
        MessageButton("B"),
        MessageButton("C"),
        MessageButton("D"),
    )
    return kb.to_list()


def change_course_kb():
    """Клавиатура для выбора курса обучения
    """
    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="👨‍💻 Менеджер по продажам", payload="sales_manager"))
    kb.row(CallbackButton(text="💢 Другой сотрудник", payload="another_employer"))
    
    return kb.to_list()


def main_menu_keyboard(educ_button_name:str = "Обучение по продажам", status_user:str = "new_employer"):
    """
    Главное меню для MAX:
    - О компании
    - Обучение
    - Мой прогресс / Рейтинг
    - Задать вопрос
    """
    kb = KeyboardBuilder()
    
    # if educ_button_name == 'Другой сотрудник':
    #     educ_button_name = 'Обучение по продукту'
    if status_user == "new_employer":
        kb.row(CallbackButton(text="🏢 О компании", payload="about_company"))
    kb.row(CallbackButton(text=f"📚 {educ_button_name if educ_button_name != 'Другой сотрудник' else 'Обучение по продукту'}", payload="education"))
    kb.row(
        CallbackButton(text="📊 Мой прогресс", payload="my_progress"),
        CallbackButton(text="🏆 Рейтинг", payload="raiting"),
    )
    kb.row(CallbackButton(text="❓ Задать вопрос", payload="send_question"))
    #kb.row(CallbackButton(text="🔄 Выбрать другой отдел", payload="change_course_name"))
    kb.row(CallbackButton(text="🔄 Выбрать другой отдел", payload="another_department"))
    return kb.to_list()


def tomorrow_kb():
    tomorrow_kb = KeyboardBuilder()
    tomorrow_kb.row(CallbackButton(text="🚀 Выхожу завтра", payload="tomorrow"))
    tomorrow_kb.row(CallbackButton(text="📅 Указать дату", payload="change_date"))
    
    return tomorrow_kb.to_list()


def continue_studying_kb(block_id):
    continue_kb = KeyboardBuilder()
    continue_kb.row(CallbackButton(text="📚 Продолжить обучение", payload=f"continue_studying::{block_id}"))
    continue_kb.row(CallbackButton(text="⬆️ Улучшить результат", payload="start_again"))
    
    return continue_kb.to_list()



def finish_studying_kb():
    finish_kb = KeyboardBuilder()
    finish_kb.row(CallbackButton(text="⬆️ Улучшить результат", payload="start_again"))
    finish_kb.row(CallbackButton(text="🏠 Главное меню", payload="main_menu"))
    
    return finish_kb.to_list()


def change_course_to_export_stat_kb(courses_name: list[str]):
    '''Возвращает клавиатуру для выбора названия курса для выгрузки статистики'''
    export_stat_kb = KeyboardBuilder()
    for course_name in courses_name:
        course = COURSES_NAMES.get(course_name)
        if course_name == "Обучение по продажам":
            course_name = '📚 ' + course_name
        elif course_name == 'Другой сотрудник':
            course_name = '💢 ' + 'Обучение по продукту'
        print(f'{course=}')
        export_stat_kb.row(CallbackButton(text=course_name, payload=f'export_data::{course}'))
    export_stat_kb.row(CallbackButton(text="🎯 По всем курсам", payload="all_courses"))
    
    print('Успешное формирование клавиатуры')
    return export_stat_kb.to_list()


def education_kb(final_flag:bool = False, with_out_ai_flag:bool = False, current_cource: str = "Обучение по продажам"):
    educ_kb = KeyboardBuilder()
    payload_data = 'education'
    if current_cource == 'Обучение по продукту':
        payload_data = 'another_emp'
    elif current_cource == 'Обучение для юриста':
        payload_data = 'lawyer_educ'
    
    if not final_flag:
        educ_kb.row(CallbackButton(text=f"💼 {current_cource}", payload=payload_data))
    if not with_out_ai_flag:
        educ_kb.row(CallbackButton(text="🏠 Главное меню", payload="main_menu"))
    else:
        educ_kb.row(CallbackButton(text="🏠 Главное меню", payload="main_menu_without_ai"))
    
    return educ_kb.to_list()


def yes_no_kb():
    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="Да", payload="yes"),
    CallbackButton(text="Нет", payload="no"))
    
    return kb.to_list()


def next_to_education_kb():

    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="📚 Продолжить обучение", payload="next_education"))
    kb.row(CallbackButton(text="🏠 Выйти в главное меню", payload="main_menu"))

    return kb.to_list()


def next_to_educ_to_part_kb():

    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="📚 Продолжить обучение", payload="next_educ_to_part_2"))
    kb.row(CallbackButton(text="🏠 Выйти в главное меню", payload="main_menu"))

    return kb.to_list()
    

def start_test_kb(final_test_flag: bool = False) -> KeyboardBuilder:
    if not final_test_flag:
        kb = KeyboardBuilder().add(CallbackButton(text="✅ Приступить к тестированию", payload="start_test"))
    else:
        kb = KeyboardBuilder().add(CallbackButton(text="✅ Приступить к тестированию", payload="to_final_test"))
    
    return kb


def main_one_kb() -> KeyboardBuilder:
    kb = KeyboardBuilder().add(CallbackButton(text="🏠 Главное меню", payload="main_menu"))
    
    return kb


def final_start_test_kb() -> KeyboardBuilder:
    kb = KeyboardBuilder().add(CallbackButton(text="📝 Перейти к тестированию", payload="to_final_test"))
    
    return kb


def final_test_kb() -> KeyboardBuilder:
    kb = KeyboardBuilder().add(CallbackButton(text="🚀 Начать тест", payload="start_final_test"))
    
    return kb



def variants_questions_kb(question_data:dict) -> list[list[dict]]:
    """Возвращает клавиатуру с вариантами ответов 
    по текущему вопросу"""
    correct_answer = question_data.get('correct')
    all_answers = question_data.get("options")
    kb = KeyboardBuilder()
    for i in range(1, 5):
        current_variant = question_data["options"][i -1].split(')')[0].strip()
        kb.add(CallbackButton(text=current_variant, payload=f'user_answer::{current_variant + "_correct" if  current_variant == correct_answer else current_variant}'))

    return kb.to_list()


def change_status_kb():
    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="👨‍💻 Новый сотрудник", payload="new_employer"))
    kb.row(CallbackButton(text="📈 Повышение квалификации", payload="upper_qualification"))
    
    return kb.to_list()


def change_department_kb():
    change_dp_kb = KeyboardBuilder()
 
    change_dp_kb.row(CallbackButton(text="👨‍💻 Отдел продаж", payload="change_department::manager"))
    change_dp_kb.row(CallbackButton(text="📐 Конструкторский отдел", payload="change_department::in_process"))
    change_dp_kb.row(CallbackButton(text="🔧 Производственно-технический отдел", payload="change_department::in_process"))
    change_dp_kb.row(CallbackButton(text="🧾 Бухгалтерский отдел", payload="change_department::in_process"))
    change_dp_kb.row(CallbackButton(text="⚖️ Юридический отдел", payload="change_department::lawyer"))
    change_dp_kb.row(CallbackButton(text="👥 Кадровый отдел", payload="change_department::in_process"))
    change_dp_kb.row(CallbackButton(text="🛠️ Отдел сервиса", payload="change_department::in_process"))
    change_dp_kb.row(CallbackButton(text="🏭 Производство", payload="change_department::in_process"))
    
    return change_dp_kb.to_list()


def change_another_department_kb():
    kb = KeyboardBuilder()
    kb.row(CallbackButton(text="🏠 Выбрать другой отдел ", payload="another_department"))
    kb.row(CallbackButton(text="🔍Изучить продукт", payload="another_employer"))
    
    return kb.to_list()

