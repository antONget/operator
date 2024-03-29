from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
sql = db.cursor()


# СОЗДАНИЕ ТАБЛИЦ
def create_table_users() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    sql.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        token_auth TEXT,
        telegram_id INTEGER,
        username TEXT,
        is_admin INTEGER,
        operator INTEGER,
        id_message DEFAULT 0
    )""")
    db.commit()


# ПОЛЬЗОВАТЕЛЬ - верификация токена и добавление пользователя
def check_token(message: Message) -> bool:
    logging.info("check_token")
    # Выполнение запроса для получения token_auth
    sql.execute('SELECT token_auth, telegram_id  FROM users')
    list_token = [row for row in sql.fetchall()]
    # Извлечение результатов запроса и сохранение их в список
    print('check_token', list_token)
    for row in list_token:
        token = row[0]
        telegram_id = row[1]
        if token == message.text and telegram_id == 'telegram_id':
            sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                        (message.chat.id, message.from_user.username, message.text))
            db.commit()
            return True
    db.commit()
    return False


def add_token(token_new) -> None:
    logging.info(f'add_token: {token_new}')
    sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, operator) '
                f'VALUES ("{token_new}", "telegram_id", "username", 0, 0)')
    db.commit()


def add_super_admin(id_admin, user_name) -> None:
    """
    Добавление суперадмина в таблицу пользователей
    :param id_admin:
    :param user:
    :return:
    """
    logging.info(f'add_super_admin')
    sql.execute('SELECT telegram_id FROM users')
    list_user = [row[0] for row in sql.fetchall()]

    if int(id_admin) not in list_user:
        sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, operator) '
                    f'VALUES ("SUPERADMIN", {id_admin}, "{user_name}", 1, 0)')
        db.commit()


def get_list_users() -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return:
    """
    logging.info(f'get_list_users')
    sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ?', ('username',))
    list_username = [row for row in sql.fetchall()]
    return list_username


def get_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param telegram_id:
    :return:
    """
    logging.info(f'get_user')
    return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


def delete_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - удалить пользователя
    :param telegram_id:
    :return:
    """
    logging.info(f'delete_user')
    sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
    db.commit()


def set_operator(telegram_id):
    """
    Установить дежурного
    :param telegram_id:
    :return:
    """
    logging.info(f'set_operator')
    sql.execute('UPDATE users SET operator = ? WHERE telegram_id = ?', (1, telegram_id))
    db.commit()


def del_operator(telegram_id):
    """
    Установить дежурного
    :param telegram_id:
    :return:
    """
    logging.info(f'set_operator')
    sql.execute('UPDATE users SET operator = ? WHERE telegram_id = ?', (0, telegram_id))
    db.commit()

def update_operator():
    logging.info(f'update_operator')
    sql.execute('UPDATE users SET operator = ?', (0,))
    db.commit()


def get_operator():
    logging.info(f'get_operator')
    list_operator = sql.execute('SELECT * FROM users WHERE operator = ?', (1,)).fetchall()
    is_operator = [operator for operator in list_operator]
    print(is_operator)
    return is_operator

def set_message(telegram_id, id_message):
    """
    Установить дежурного
    :param telegram_id:
    :return:
    """
    logging.info(f'set_message')
    sql.execute('UPDATE users SET id_message = ? WHERE telegram_id = ?', (id_message, telegram_id))
    db.commit()

def get_id_message():
    logging.info(f'get_id_message')
    list_message = sql.execute('SELECT telegram_id, id_message FROM users').fetchall()
    list_id_message = [message for message in list_message]
    return list_id_message
