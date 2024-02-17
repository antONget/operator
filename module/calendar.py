from datetime import datetime


def is_working_day():
    today = datetime.now()
    day = today.weekday()
    return day < 5

if __name__ == '__main__':
    print(is_working_day())