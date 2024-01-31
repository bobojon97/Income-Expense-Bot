from datetime import datetime
import psycopg2
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from config import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
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

        # Получаем текущую дату и разделяем ее на год и месяц
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Сохраняем данные о доходе в базу данных
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO income (amount, description, date, year, month) VALUES (%s, %s, %s, %s, %s)", 
                    (data['income_amount'], data['income_description'], current_date, year, month))
        conn.commit()
        cur.close()
        conn.close()

    await message.reply(f'<b>Доход {data["income_amount"]}с добавлен</b>', parse_mode='html')

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

        # Получаем текущую дату и разделяем ее на год и месяц
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Сохраняем данные о расходе в базу данных
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO expense (amount, description, date, year, month) VALUES (%s, %s, %s, %s, %s)", 
                    (data['expense_amount'], data['expense_description'], current_date, year, month))
        conn.commit()
        cur.close()
        conn.close()

    await message.reply(f'<b>Расход {data["expense_amount"]}с добавлен</b>', parse_mode='html')

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

@dp.message_handler(text='Итог')
async def view_total_handler(message: types.Message):
    current_year = datetime.now().year
    years_range = [current_year, current_year - 1]  # Последние два года

    inline_kb_year = InlineKeyboardMarkup(row_width=2)
    for year in years_range:
        inline_kb_year.add(InlineKeyboardButton(str(year), callback_data=f"year:{year}"))

    await message.reply("Выберите год:", reply_markup=inline_kb_year)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('year:'))
async def choose_month(callback_query: types.CallbackQuery):
    year = callback_query.data.split(':')[1]
    inline_kb_month = InlineKeyboardMarkup(row_width=3)
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    for i, month in enumerate(months, start=1):
        inline_kb_month.add(InlineKeyboardButton(month, callback_data=f"month:{year}:{i}"))

    await callback_query.message.edit_text(f"Выберите месяц для {year} года:", reply_markup=inline_kb_month)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('month:'))
async def show_report(callback_query: types.CallbackQuery):
    _, year, month = callback_query.data.split(':')
    year, month = int(year), int(month)

    conn = get_db()
    cursor = conn.cursor()

    # Получение доходов за выбранный месяц и год
    cursor.execute("SELECT amount, description FROM income WHERE year = %s AND month = %s", (year, month))
    incomes = cursor.fetchall()

    # Получение расходов за выбранный месяц и год
    cursor.execute("SELECT amount, description FROM expense WHERE year = %s AND month = %s", (year, month))
    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    income_text = "Доходы:\n" + "\n".join([f"{desc}: {amount}с" for amount, desc in incomes]) if incomes else "Доходы отсутствуют.\n"
    expense_text = "Расходы:\n" + "\n".join([f"{desc}: {amount}с" for amount, desc in expenses]) if expenses else "Расходы отсутствуют.\n"

    await callback_query.message.answer(f"Отчет за {month}-{year}:\n{income_text}\n{expense_text}")


if __name__ == '__main__':
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)