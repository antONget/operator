from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import logging
from module.data_base import get_list_users, get_user, set_operator

from keyboards.keyboards_admin_operator import keyboards_set_operator, keyboard_set_user_operator
from filter.admin_filter import chek_manager
from config_data.config import Config, load_config
import requests

config: Config = load_config()

router = Router()
user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()

# ДЕЖУРНЫЙ
@router.message(F.text == 'Назначить дежурного', lambda message: chek_manager(message.chat.id))
async def process_set_operator(message: Message) -> None:
    logging.info(f'process_set_operator: {message.chat.id}')
    """
    Функция позволяет назначить дежурного
    :param message:
    :return:
    """
    list_user = get_list_users()
    await message.answer(text="Выберите пользователя, которого нужно назначить дежурным",
                         reply_markup=keyboards_set_operator(list_users=list_user, back=0, forward=2, count=6))


# >>>>
@router.callback_query(F.data.startswith('forwardoperator'))
async def process_forward(callback: CallbackQuery) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    list_user = get_list_users()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_set_operator(list_users=list_user, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите назначить дежурным',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите назначить дежурным',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('backoperator'))
async def process_back(callback: CallbackQuery) -> None:
    logging.info(f'process_back: {callback.message.chat.id}')
    list_user = get_list_users()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_set_operator(list_users=list_user, back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите назначить дежурным',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите назначить дежурным',
                                         reply_markup=keyboard)


# подтверждение назначения пользователя дежурным
@router.callback_query(F.data.startswith("setoperator"))
async def process_setoperator(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_setoperator: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(set_telegram_id_operator=telegram_id)
    await callback.message.edit_text(text=f'Назначить пользователя {user_info[0]} дежурным?',
                                     reply_markup=keyboard_set_user_operator())


@router.callback_query(F.data == "donesetoperator")
async def process_setoperatordone(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_setoperatordone: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    set_telegram_id_operator = user_dict[callback.message.chat.id]['set_telegram_id_operator']
    set_operator(telegram_id=set_telegram_id_operator)
    get_user(set_telegram_id_operator)
    user_name = get_user(telegram_id=set_telegram_id_operator)
    list_users = get_list_users()
    for user in list_users:
        result = get_telegram_user(user_id=user[0], bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=user[0],
                                   text=f"Пользователь {user_name[0]} назначен дежурным")
        else:
            user_name = get_user(telegram_id=user[0])
            await callback.message.answer(text=f"Пользователь {user[1]} не оповещен")
    await callback.message.answer(text="Рассылка завершена!")


@router.callback_query(F.data.startswith("yes_"))
async def process_setoperatoryes(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_setoperatoryes: {callback.message.chat.id}')
    set_telegram_id_operator = int(callback.data.split('_')[1])
    print(set_telegram_id_operator)
    set_operator(telegram_id=set_telegram_id_operator)
    get_user(set_telegram_id_operator)
    user_name = get_user(telegram_id=set_telegram_id_operator)
    list_users = get_list_users()
    print(list_users)
    for user in list_users:
        result = get_telegram_user(user_id=user[0], bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=user[0],
                                   text=f"Пользователь {user_name[0]} взял дежурство")
        else:
            for admin_id in config.tg_bot.admin_ids.split(','):
                result = get_telegram_user(user_id=int(admin_id), bot_token=config.tg_bot.token)
                if 'result' in result:
                    await bot.send_message(chat_id=int(admin_id),
                                           text=f"Пользователь {user[1]} не оповещен")



