import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from filter.admin_filter import chek_manager
from module.data_base import create_table_users, add_super_admin, get_list_users, get_operator, set_message
from module.calendar import is_working_day
from keyboards.keyboards_admin import keyboards_superadmin, keyboard_question
import requests
from config_data.config import Config, load_config
from datetime import datetime, time
router = Router()
config: Config = load_config()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()


def temp_func(bot: Bot, my_int_var):
    logging.info(f'temp_func')
    my_int_var.add_job(sendler_question, 'interval', id='sendler_question', seconds=60 * 30, args=(bot,))


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


async def sendler_question(bot: Bot):
    logging.info(f'sendler_question')
    # если дежурный не назначен и сегодня будний день
    print(not get_operator())
    print(is_working_day())
    if not get_operator() and is_working_day() and is_time_between(time(7-3, 50), time(23-3, 30)):
        list_users = get_list_users()
        print(list_users)
        for user in list_users:
            print(user)
            result = get_telegram_user(user[0], config.tg_bot.token)
            if 'result' in result:
                msg = await bot.send_message(chat_id=user[0],
                                             text=f"Вы дежурный?",
                                             reply_markup=keyboard_question(telegram_id=user[0]))
                set_message(telegram_id=user[0], id_message=msg.message_id)
            else:
                await bot.send_message(chat_id=843554518,
                                       text=f"Пользователь: {user[1]} id:{user[0]} не запустил бот",
                                       reply_markup=keyboard_question(telegram_id=user[0]))




@router.message(CommandStart(), lambda message: chek_manager(message.chat.id))
async def process_start_command_superadmin(message: Message, bot: Bot) -> None:
    logging.info("process_start_command")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_super_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    await message.answer(text="Вы администратор проекта, вы можете приглашать новых пользователей и назначать дежурных",
                         reply_markup=keyboards_superadmin())