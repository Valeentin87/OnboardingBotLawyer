import logging
from aiomax import fsm, Bot
from config import load_config

#logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('on_boarding_info.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d (%(funcName)s) - %(message)s")
file_handler.setFormatter(formatter)

# Очищаем старые обработчики и добавляем новый
logger.handlers.clear()
logger.addHandler(file_handler)

# Отключаем передачу в родительские логгеры
logger.propagate = False



config = load_config()
MAX_TOKEN = config.max_bot_token

storage = fsm.FSMStorage()

bot = Bot(MAX_TOKEN, default_format="markdown")



# Простое in-memory состояние
test_state: dict = {}
ask_ai_state: dict = {"mode": False}


