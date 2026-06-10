import time
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiomax import Callback
from aiomax.fsm import FSMCursor
#import logging
from bot.adapters.max.create_bot import logger

#logging.basicConfig(level=logging.INFO)

DEBOUNCE_SECONDS = 10  # окно защиты в секундах


async def debounce_button(message: Message, state: FSMContext) -> bool:
    """
    Антидубль для нажатия по кнопке.

    Возвращает:
        True  - если НУЖНО прервать хендлер (нажатие слишком рано,
                пользователю уже отправлено сообщение "обработка идёт").
        False - если можно продолжать выполнение хендлера.
    """
    last_ts = None
    data = await state.get_data()
    if isinstance(data, dict):
        last_ts = data.get("last_click_ts")

    now = time.time()
    if last_ts and now - last_ts < DEBOUNCE_SECONDS:
        await message.answer("⏳ Подождите немного, обработка уже идёт.")
        return True

    # обновляем таймстемп последнего клика
    await state.update_data(last_click_ts=now)
    return False


async def debounce_button_max(callback: Callback, cursor: FSMCursor):
    """
    Антидубль для нажатия по кнопке (вариант для Max).

    Возвращает:
        True  - если НУЖНО прервать хендлер (нажатие слишком рано,
                пользователю уже отправлено сообщение "обработка идёт").
        False - если можно продолжать выполнение хендлера.
    """
    try:
        last_ts = None
        data = cursor.get_data()
        if isinstance(data, dict):
            last_ts = data.get("last_click_ts")
        else:
            data = {}
        
        logger.info(f"[debounce_button_max] {data=} {type(data)=} {last_ts=}")
        
        now = time.time()
        
        if last_ts:
            logger.info(f"[debounce_button_max] ⚠️ с момента последнего нажатия прошло {now - last_ts} секунд ⚠️")
        
        if last_ts and now - last_ts < DEBOUNCE_SECONDS:
            await callback.send("⏳ Подождите немного, обработка уже идёт.")
            return True
        
        data.update(last_click_ts=now)
        cursor.change_data(data)
        new_data = cursor.get_data()
        logger.info(f"[debounce_button_max] {new_data=} {type(new_data)=}")
        return False
    except Exception as e:
        logger.error(f'[debounce_button_max] Произошла ошибка {e}')
        