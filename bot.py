import psycopg2
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from config import *
from aiogram.types import KeyboardButton

# Создаем подключение к базе данных
def get_db():
    conn = psycopg2.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database
    )
    return conn

bot = Bot(token=TOKKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Определяем класс для FSM
class AddIncomeExpense(StatesGroup):
    add_income = State()
    add_income_amount = State()
    add_income_description = State()
    add_expense = State() 
    add_expense_amount = State()
    add_expense_description = State()

# Создаем объекты кнопок
add_income_button = types.KeyboardButton('Добавить доход')
add_expense_button = types.KeyboardButton('Добавить расход')
incomes_button = types.KeyboardButton('Просмотреть доходы')
expenses_button = types.KeyboardButton('Просмотреть расходы')
total_icome_expense = types.KeyboardButton('Итог')

# Создаем объекты клавиатур
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(add_income_button)
keyboard.add(add_expense_button)
keyboard.add(incomes_button)
keyboard.add(expenses_button)
keyboard.add(total_icome_expense)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.reply('<b>Привет! Добавьте свои доходы и расходы, и просмотрите свои расходы и конечно контролируете свои деньги</b>', parse_mode='html', reply_markup=keyboard)

# Обработчик кнопки "Добавить доход"
@dp.message_handler(text='Добавить доход')
async def add_income_handler(message: types.Message):
    await message.reply('<b>Введите сумму дохода</b>:', parse_mode='html')
    await AddIncomeExpense.add_income_amount.set()


# Обработчик ответа на запрос суммы дохода
@dp.message_handler(state=AddIncomeExpense.add_income_amount)
async def process_income_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['income_amount'] = message.text

    await message.reply('<b>Введите описание дохода</b>:', parse_mode='html')
    await AddIncomeExpense.add_income_description.set()

# Обработчик ответа на запрос описания дохода
@dp.message_handler(state=AddIncomeExpense.add_income_description)
async def process_income_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['income_description'] = message.text

        # Сохраняем данные о доходе в базу данных
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO income (amount, description) VALUES (%s, %s)", (data['income_amount'], data['income_description']))
        conn.commit()
        cur.close()
        conn.close()

    await message.reply(f'<b>Доход {data["income_amount"]}.с добавлен</b>', parse_mode='html')

    # Возвращаемся в начальное состояние
    await state.finish()


# Обработчик кнопки "Добавить расход"
@dp.message_handler(text='Добавить расход')
async def add_expense_handler(message: types.Message):
    await message.reply('<b>Введите сумму расхода</b>:', parse_mode='html')
    await AddIncomeExpense.add_expense_amount.set()

# Обработчик ответа на запрос суммы расхода
@dp.message_handler(state=AddIncomeExpense.add_expense_amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expense_amount'] = message.text

    await message.reply('<b>Введите описание расхода</b>:', parse_mode='html')
    await AddIncomeExpense.add_expense_description.set()

# Обработчик ответа на запрос описания расхода
@dp.message_handler(state=AddIncomeExpense.add_expense_description)
async def process_expense_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expense_description'] = message.text

        # Сохраняем данные о расходе в базу данных
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO expense (amount, description) VALUES (%s, %s)", (data['expense_amount'], data['expense_description']))
        conn.commit()
        cur.close()
        conn.close()

    await message.reply(f'<b>Расход {data["expense_amount"]}.с добавлен</b>', parse_mode='html')

    # Возвращаемся в начальное состояние
    await state.finish()

# Обработчик кнопки "Просмотреть доходы"
@dp.message_handler(text='Просмотреть доходы')
async def view_incomes_handler(message: types.Message):
    # Ваш код для просмотра доходов
    # Например, вы можете использовать функцию get_db() для получения соединения с базой данных
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, amount FROM income")
    rows = cursor.fetchall()
     # Обработка полученных данных, например, отправка пользователю
    incomes_text = "<b>Доходы</b>:\n"
    total_amount = 0  # Общая сумма доходов
    for row in rows:
        incomes_text += f"<b>ID: {row[0]}, Описание: {row[1]}, Сумма: {row[2]}c</b>\n"
        total_amount += row[2]
        
    incomes_text += f"<b>Общая сумма: {total_amount}.с</b>\n"  # Вывод общей суммы
    await message.reply(incomes_text, parse_mode='html')
    
    cursor.close()
    conn.close()

@dp.message_handler(text='Просмотреть расходы')
async def view_expenses_handler(message: types.Message):
    # Получаем список всех расходов из базы данных
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expense")
    expenses = cur.fetchall()
    expense = "<b>Расходы</b>:\n"
    total_amount = 0  # Общая сумма расходов
    for row in expenses:
        expense += f"<b>ID: {row[0]}, Описание: {row[1]}, Сумма: {row[2]}с</b>\n"
        total_amount += row[2]
        
    expense += f"<b>Общая сумма: {total_amount}.с</b>\n"  # Вывод общей суммы
    if len(expenses) == 0:
        await message.reply('<b>Расходов пока нет.</b>', parse_mode='html')
    else:
        await message.reply(expense, parse_mode='html')
    
    cur.close()
    conn.close()

# Обработчик кнопки "Итог"
@dp.message_handler(text='Итог')
async def view_total_handler(message: types.Message):
    # Ваш код для подсчета общей суммы доходов и расходов
    # Например, вы можете использовать функцию get_db() для получения соединения с базой данных
    conn = get_db()
    
    def get_total_income_expense(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM income")
        total_income = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(amount) FROM expense")
        total_expense = cursor.fetchone()[0]
        cursor.close()
        return total_income, total_expense
    
    total_income, total_expense = get_total_income_expense(conn)
    conn.close()
    # Формирование текста для ответа
    response_text = f"<b>Общий доход: {total_income}\nОбщий расход: {total_expense}</b>\n"
    if total_income > total_expense:
        response_text += "<b>Вы в прибыли! 😄🚀</b>"
    elif total_income < total_expense:
        response_text += "<b>Вы в убытке... 😞💸</b>"
    else:
        response_text += "<b>Вы на нуле. 🤷‍♂️💰</b>"
    # Отправка ответа пользователю
    await message.reply(response_text, parse_mode='html')

if __name__ == '__main__':
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)