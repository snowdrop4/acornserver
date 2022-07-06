from random import randint, choice, choices
import datetime
import string


def random_bool():
	return choice([True, False])


def random_str(k=10):
	return choice(string.ascii_uppercase) + ''.join(choices(string.ascii_lowercase, k=k - 1))


def random_prose(k=20):
	return ' '.join([ random_str(randint(1, 12)) for _ in range(0, k) ])


def random_date():
	year = randint(1982, 2020)
	
	month = randint(1,12)
	
	days_in_month = 31
	
	if month == 2:
		days_in_month = 28
	elif month in [4, 6, 9, 11]:
		days_in_month = 30
	
	day = randint(1, days_in_month)
	
	return datetime.date(year, month, day)
