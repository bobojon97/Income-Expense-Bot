import psycopg2
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from config import *


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


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.reply('Привет! Для начала добавь доход или расход командой /add_income или /add_expense или /expenses.')

# Обработчик команды /add_income
@dp.message_handler(commands=['add_income'])
async def add_income_handler(message: types.Message):
    await message.reply('Введите сумму дохода:')
    await AddIncomeExpense.add_income_amount.set()

# Обработчик ответа на запрос суммы дохода
@dp.message_handler(state=AddIncomeExpense.add_income_amount)
async def process_income_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['income_amount'] = message.text

    await message.reply('Введите описание дохода:')
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

    await message.reply(f'Доход {data["income_amount"]} добавлен')

    # Возвращаемся в начальное состояние
    await state.finish()


# Обработчик команды /add_expense
@dp.message_handler(commands=['add_expense'])
async def add_expense_handler(message: types.Message):
    await message.reply('Введите сумму расхода:')
    await AddIncomeExpense.add_expense_amount.set()

# Обработчик ответа на запрос суммы расхода
@dp.message_handler(state=AddIncomeExpense.add_expense_amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expense_amount'] = message.text

    await message.reply('Введите описание расхода:')
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

    await message.reply(f'Расход {data["expense_amount"]} добавлен')

    # Возвращаемся в начальное состояние
    await state.finish()

# Обработчик команды /expenses
@dp.message_handler(commands=['expenses'])
async def expenses_handler(message: types.Message):
    # Получаем список всех расходов из базы данных
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expense")
    expenses = cur.fetchall()
    cur.close()
    conn.close()

    # Отправляем список расходов пользователю
    if len(expenses) == 0:
        await message.reply('Расходов пока нет.')
    else:
        expense_list = ['Расходы:\n']
        for expense in expenses:
            expense_list.append(f'{expense[1]} руб. - {expense[2]}')
        await message.reply('\n'.join(expense_list))

if __name__ == '__main__':
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)