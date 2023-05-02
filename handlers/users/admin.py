import asyncio
from aiogram import types
from data.config import ADMINS
from loader import dp, db, bot
import pandas as pd
from states.admin import AdminState
from keyboards.default import admin
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


@dp.message_handler(text='/admin', user_id=ADMINS, state='*')
async def open_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await AdminState.categories.set()

    await message.answer(
        'Разворачиваем панель администратора...',
        reply_markup=admin.markup_categories
    )


@dp.message_handler(text='Пользователи', state=AdminState.categories)
async def open_users(message: types.Message):
    await AdminState.users.set()
    await message.answer(text='Начата работа с таблицей пользователей', reply_markup=admin.markup_users)


@dp.message_handler(
    text=["/allusers", "Список пользователей"],
    user_id=ADMINS,
    state=AdminState.users
)
async def get_all_users(message: types.Message):
    try:
        users = await db.select_all_users()
        telegram_id = []
        name = []
        for user in users:
            telegram_id.append(user[-2])
            name.append(user[1])
        data = {
            "Телеграм ID": telegram_id,
            "Имя": name
        }
        pd.options.display.max_rows = 10000
        df = pd.DataFrame(data)
        if len(df) > 50:
            for x in range(0, len(df), 50):
                await bot.send_message(message.chat.id, df[x:x + 50])
        else:
            await bot.send_message(message.chat.id, df)
    except Exception:
        await message.answer('Ошибка, возможно вы еще не создали эту таблицу\n'
                             'Чтобы это сделать, введите /start')


@dp.message_handler(
    text=["/cleanusers", "Очистить"],
    user_id=ADMINS,
    state=AdminState.users
)
async def cleanusers(message: types.Message):
    try:
        await db.delete_users()
        await message.answer("Таблица пуста!")
    except Exception:
        await message.answer('Ошибка, возможно вы еще не создали эту таблицу\n'
                             'Чтобы это сделать, введите /start')


@dp.message_handler(
    text=['/dropusers', 'Удалить'],
    user_id=ADMINS,
    state=AdminState.users
)
async def dropusers(message: types.Message):
    await AdminState.choice.set()

    btn_yes = KeyboardButton(text='Да')
    btn_no = KeyboardButton(text='Нет')
    markup_choice = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(btn_no, btn_yes)

    await message.reply(text='Подтверждаете удаление таблицы пользователей?', reply_markup=markup_choice)


@dp.message_handler(
    text=['Да', 'Нет'],
    user_id=ADMINS,
    state=AdminState.choice
)
async def delete_table_users(message: types.Message):
    if message.text == 'Да':
        await db.drop_users()
        await message.answer(text='Такой таблицы больше не существует', reply_markup=admin.markup_users)
    else:
        await message.answer(text='Откат', reply_markup=admin.markup_users)
    await AdminState.users.set()


# надо дописать, сделать функцию более комплексной
@dp.message_handler(
    text=["/advert", "Реклама"],
    user_id=ADMINS,
    state=AdminState.users
)
async def send_ad_to_all(message: types.Message):
    users = await db.select_all_users()
    for user in users:
        user_id = user[-2]
        await bot.send_message(chat_id=user_id, text="@aiogram - join us!")
        await asyncio.sleep(0.05)


@dp.message_handler(text='Назад', state=AdminState.users)
async def go_back(message: types.Message):
    await AdminState.categories.set()
    await message.answer(text='Разворачиваем административную панель...', reply_markup=admin.markup_categories)
