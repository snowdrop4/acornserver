import string
import datetime
from random import choice, choices, randint


def random_bool() -> bool:
    return choice([True, False])


def random_str(k: int = 10) -> str:
    return choice(string.ascii_uppercase) + "".join(
        choices(string.ascii_lowercase, k=k - 1)
    )


def random_prose(k: int = 20) -> str:
    return " ".join([random_str(randint(1, 12)) for _ in range(0, k)])


def random_date() -> datetime.date:  # the date object is lowercase???
    year = randint(1982, 2020)

    month = randint(1, 12)

    days_in_month = 31

    if month == 2:
        days_in_month = 28
    elif month in [4, 6, 9, 11]:
        days_in_month = 30

    day = randint(1, days_in_month)

    return datetime.date(year, month, day)
