import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from filter.admin_filter import chek_manager
from module.data_base import create_table_users, add_super_admin, get_list_users, get_operator, update_operator
from module.calendar import is_working_day
from keyboards.keyboards_admin import keyboards_superadmin, keyboard_question

router = Router()


async def sendler_question(bot: Bot):
    logging.info(f'sendler_question')
    # если дежурный не назначен и сегодня будний день
    print(not get_operator())
    print(is_working_day())
    if not get_operator() and is_working_day():
        list_users = get_list_users()
        print(list_users)
        for user in list_users:
            await bot.send_message(chat_id=user[0],
                                   text=f"Вы дежурный?",
                                   reply_markup=keyboard_question(telegram_id=user[0]))

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


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
    # запускаем процесс обновления таблицы
    scheduler.add_job(update_operator, 'cron', hour=8, minute=0, second=0)
    # scheduler.add_job(update_operator, 'interval', seconds=60*5)
    scheduler.add_job(sendler_question, 'interval', seconds=60*30, args=(bot,))
    scheduler.start()
    await message.answer(text="Вы администратор проекта, вы можете приглашать новых пользователей и назначать дежурных",
                         reply_markup=keyboards_superadmin())