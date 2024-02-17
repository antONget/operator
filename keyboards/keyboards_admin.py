from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# ГЛАВНОЕ МЕНЮ СУПЕРАДМИН
def keyboards_superadmin():
    logging.info("keyboards_superadmin")
    button_1 = KeyboardButton(text='Пользователь')
    button_2 = KeyboardButton(text='Назначить дежурного')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_question(telegram_id) -> None:
    """
    ПОЛЬЗОВАТЕЛЬ -> Удалить -> подтверждение удаления пользователя из базы
    :return:
    """
    logging.info("keyboard_set_user_operator")
    button_1 = InlineKeyboardButton(text='Да',  callback_data=f'yes_{telegram_id}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard