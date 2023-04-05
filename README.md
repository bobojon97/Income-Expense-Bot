# Income-Expense

Income-Expense Bot - это телеграм-бот, который позволяет пользователям отслеживать свои доходы и расходы, добавлять новые записи о доходах и расходах, а также просматривать общую сумму доходов и расходов

Установка

    Установите Python 3.7+ на вашем сервере или компьютере, если он еще не установлен.
    Установите необходимые библиотеки с помощью команды: pip install -r requirements.txt
    Создайте бота в Telegram и получите его токен. Инструкции по созданию бота можно найти здесь: https://core.telegram.org/bots#botfather
    Запустите файл bot.py, указав полученный токен в переменной TOKEN:

TOKEN = 'YOUR_BOT_TOKEN'

Использование

После успешной установки и запуска, бот будет готов к использованию. Вы можете использовать команды для взаимодействия с ботом:

    /start - Начать взаимодействие с ботом
    /add_income - Добавить новый доход
    /add_expense - Добавить новый расход
    /view_expenses - Просмотреть список всех расходов
    /view_incomes - Просмотреть список всех доходов
    /total - Посмотреть общую сумму доходов и расходов
    
База данных
    Установите Postgres на свой компьютер.
    Создайте новую базу данных в Postgres, например:
    
    createdb income_expense_bot
    
Создайте таблицы для доходов и расходов в созданной базе данных, используя следующие запросы SQL:

CREATE TABLE incomes (
  id SERIAL PRIMARY KEY,
  description TEXT NOT NULL,
  amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE expenses (
  id SERIAL PRIMARY KEY,
  description TEXT NOT NULL,
  amount NUMERIC(10, 2) NOT NULL
);

Укажите данные для подключения к базе данных в файле config.py

host = 'host'

port = ''

user = 'user'

password = 'password'

database = 'database'

Зависимости
- aiogram
- psycopg2

Вы можете установить их с помощью команды:

pip install -r requirements.txt

Автор
Бот разработан bobojon97.
