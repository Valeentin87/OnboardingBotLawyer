class UserInfo:
    """Состояния конечных автоматов информации о пользователе"""
    waiting_for_name_surname =  'waiting_for_name_surname'



class AnotherEmployerStates:
    """Состояния для ветки ДРУГОЙ СОТРУДНИК"""
    user_type = "another_employer"
    

class LawyerStates:
    """Состояния для ветки ЮРИСТ"""
    user_type = "lawyer"
    

class OnboardingStates:
    """Состояния конечных атвоматов для подготовки к обучению"""
    waiting_for_start_date = 'waiting_for_start_date'
    waiting_for_confirmation = 'waiting_for_confirmation'
    
    
class TrainingStates:
    """Состояния конечных автоматов для прохождения обучения"""
    
    step_1_welcome = 'step_1_welcome'
    step_2_video = 'step_2_video'
    course_intro = 'course_intro'
    step_3_presentation = 'step_3_presentation'
    # =========== БЛОК1 ===============
    step_4_ready_for_test = 'step_4_ready_for_test'
    step_5_testing = 'step_5_testing'
    step_6_next = 'step_6_next'
    step_6_ready_for_test = 'step_6_ready_for_test'
    step_7_testing = 'step_7_testing'
    step_8_next = 'step_8_next'
    step_8_ready_for_test = 'step_8_ready_for_test'
    step_8_testing = 'step_8_testing'
    step_9_next = 'step_9_next'
    step_9_ready_for_test = 'step_9_ready_for_test'
    step_9_testing = 'step_9_testing'
    step_10_next = 'step_10_next'
    step_10_ready_for_test = 'step_10_ready_for_test'
    step_10_testing = 'step_10_testing'
    step_11_testing = 'step_11_testing'
    step_11_next = 'step_11_next'
    step_11_ready_for_test = 'step_11_ready_for_test'
    block1_questions = 'block1_questions'
    step_12_testing = 'step_12_testing'
    check_answer_to_open_question = 'check_answer_to_open_question'
    # =========== БЛОК2 ===============
    block2_start = 'block2_start'
    block2_section1_ready = 'block2_section1_ready'
    block_2_test_1_testing = 'block_2_test_1_testing'
    block_2_section_2_next = 'block_2_section_2_next'
    block_2_test_2_ready_for_test = 'block_2_test_2_ready_for_test'
    block_2_test_2_testing = 'block_2_test_2_testing'
    block_2_section_3_next = 'block_2_section_3_next'
    block_2_test_3_ready_for_test = 'block_2_test_3_ready_for_test'
    block_2_test_3_testing = 'block_2_test_3_testing'
    block_2_section_4_next = 'block_2_section_4_next'
    block2_final_test = 'block2_final_test'
    block2_questions = 'block2_questions'
    block_2_final_testing = 'block_2_final_testing'
    # =========== БЛОК3 ================
    block3_start = 'block3_start'
    block3_section1_ready = 'block3_section1_ready'
    block_3_test_1_ready_for_test = 'block_3_test_1_ready_for_test'
    block_3_test_1_testing = 'block_3_test_1_testing'
    block_3_section_1_next = 'block_3_section_1_next'
    block_3_test_2_ready_for_test = 'block_3_test_2_ready_for_test'
    block_3_test_2_testing = 'block_3_test_2_testing'
    block_3_section_2_next = 'block_3_section_2_next'
    block_3_test_3_ready_for_test = 'block_3_test_3_ready_for_test'
    block_3_test_3_testing = 'block_3_test_3_testing'
    block_3_section_3_next = 'block_3_section_3_next'
    block_3_test_4_ready_for_test = 'block_3_test_4_ready_for_test'
    block_3_test_4_testing = 'block_3_test_4_testing'
    block_3_section_4_next = 'block_3_section_4_next'
    block_3_test_5_ready_for_test = 'block_3_test_5_ready_for_test'
    block_3_test_5_testing = 'block_3_test_5_testing'
    block_3_section_5_next = 'block_3_section_5_next'
    block_3_test_6_ready_for_test = 'block_3_test_6_ready_for_test'
    block_3_test_6_testing = 'block_3_test_6_testing'
    block3_final_test = 'block3_final_test'
    block3_questions = 'block3_questions'
    block_3_final_testing = 'block_3_final_testing'
    # =========== БЛОК4 ================
    block4_start = 'block4_start'
    block4_section1_ready = 'block4_section1_ready'
    block_4_test_1_ready_for_test = 'block_4_test_1_ready_for_test'
    block_4_test_1_testing = 'block_4_test_1_testing'
    block_4_section_1_next = 'block_4_section_1_next'
    block_4_test_2_ready_for_test = 'block_4_test_2_ready_for_test'
    block_4_test_2_testing = 'block_4_test_2_testing'
    block_4_section_2_next = 'block_4_section_2_next'
    block_4_test_3_ready_for_test = 'block_4_test_3_ready_for_test'
    block_4_test_3_testing = 'block_4_test_3_testing'
    block_4_section_3_next = 'block_4_section_3_next'
    block_4_test_4_ready_for_test = 'block_4_test_4_ready_for_test'
    block_4_test_4_testing = 'block_4_test_4_testing'
    block_4_section_4_next = 'block_4_section_4_next'
    block4_questions = 'block4_questions'
    block_4_final_testing = 'block_4_final_testing'
    block4_final_test = 'block4_final_test'
    block5_start = 'block5_section1_ready'
    # =========== БЛОК5 =================
    block_5_video_2_viewer = 'block_5_video_2_viewer'
    block_5_video_3_viewer = 'block_5_video_3_viewer'
    block_5_video_4_viewer = 'block_5_video_4_viewer'
    block_5_video_5_viewer = 'block_5_video_5_viewer'
    block_5_video_6_viewer = 'block_5_video_6_viewer'
    block_5_video_7_viewer = 'block_5_video_7_viewer'
    block_5_video_8_viewer = 'block_5_video_8_viewer'
    block_5_video_9_viewer = 'block_5_video_9_viewer'
    block_5_video_10_viewer = 'block_5_video_10_viewer'
    block_5_video_11_viewer = 'block_5_video_11_viewer'
    block_5_video_12_viewer = 'block_5_video_12_viewer'
    block_5_video_13_viewer = 'block_5_video_13_viewer'
    block_5_video_14_viewer = 'block_5_video_14_viewer'
    block_5_video_15_viewer = 'block_5_video_15_viewer'
    block5_final_test = 'block5_final_test'
    block5_questions = 'block5_questions'
    block_5_final_testing = 'block_5_final_testing'
    # ============ БЛОК6 =================
    block_6_final_test = 'block_6_final_test'
    block_6_final_testing = 'block_6_final_testing'
    block_6_section_1_next = 'block_6_section_1_next'
    block6_questions = 'block6_questions'
    # ============ БЛОК7 =================
    block7_questions = 'block7_questions'
    block_7_final_testing = 'block_7_final_testing'
    
    asking_ai = 'asking_ai'
    
    # =========== ОБУЧЕНИЕ ДЛЯ ЮРИСТА =============
    lawyer = {
        'block_1': 'block_1',
        'block_1_ready_for_test': 'block_1_ready_for_test',
        'block1_questions': 'block1_questions_lawyer',  # аналог step12_testing
        'block_2_start': 'block_2_start',
        'block2_section_2': 'block2_section_2',
        'block2_questions': 'block2_questions_lawyer',
        'block_3_start': 'block_3_start',
        'block3_questions': 'block3_questions_lawyer',
        'block_4_start': 'block_4_start',
        'block4_questions': 'block4_questions_lawyer',
        'block_5_start': 'block_5_start',
        'block5_questions': 'block5_questions_lawyer',
        'final_test_start': 'final_test_start',
        'final_test_questions': 'final_test_questions_lawyer',
    }