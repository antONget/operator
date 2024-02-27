import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import admin_main_handlers, admin_user_handlers, admin_operator_handlers
from handlers import user_auth_handler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.admin_main_handlers import update_operator, sendler_question

# Инициализируем logger
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(update_operator, 'cron', hour=9, minute=0, second=0)
    # scheduler.add_job(update_operator, 'interval', seconds=60*5)
    scheduler.add_job(sendler_question, 'interval', seconds=60 * 30, args=(bot,))
    scheduler.start()
    # Регистрируем router в диспетчере
    dp.include_router(admin_main_handlers.router)
    dp.include_router(admin_user_handlers.router)
    dp.include_router(admin_operator_handlers.router)
    dp.include_router(user_auth_handler.router)

    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
