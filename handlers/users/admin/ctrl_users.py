from aiogram import types
import asyncpg.exceptions
from data.config import ADMINS
from loader import dp, db, bot
import pandas as pd
import logging
from states.admin import AdminState
from keyboards.default import admin
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# entry to admin panel
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
    await message.answer(
        text='Начата работа с таблицей пользователей',
        reply_markup=admin.markup_users
    )


@dp.message_handler(text=["/allusers", "Список пользователей"], state=AdminState.users)
async def get_all_users(message: types.Message):
    try:
        users = await db.select_all_users()
        telegram_id = []
        name = []
        for user in users:
            telegram_id.append(user[3])
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
    except asyncpg.exceptions.UndefinedTableError as err:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )
        logging.exception(err)


@dp.message_handler(text=["/cleanusers", "Очистить"], state=AdminState.users)
async def cleanusers(message: types.Message):
    try:
        await db.delete_users()
        await message.answer("Таблица пуста!")
    except asyncpg.exceptions.UndefinedTableError as err:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )
        logging.exception(err)


@dp.message_handler(text=['/dropusers', 'Удалить'], state=AdminState.users)
async def dropusers(message: types.Message):
    await AdminState.users_choice.set()

    btn_yes = KeyboardButton(text='Да')
    btn_no = KeyboardButton(text='Нет')
    markup_choice = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1
    ).add(btn_no, btn_yes)

    await message.reply(
        text='Подтверждаете удаление таблицы пользователей?',
        reply_markup=markup_choice
    )


@dp.message_handler(text=['Да', 'Нет'], state=AdminState.users_choice)
async def delete_table_users(message: types.Message):
    if message.text == 'Да':
        await db.drop_users()
        await message.answer(
            text='Такой таблицы больше не существует',
            reply_markup=admin.markup_users
        )
    else:
        await message.answer(text='Откат', reply_markup=admin.markup_users)
    await AdminState.users.set()


@dp.message_handler(text='Задолженности', state=AdminState.users)
async def search_for_debtors(message: types.Message):
    debtors_list = await db.select_debtors()
    await AdminState.search_for_debtors.set()

    btn_help = KeyboardButton(text='В каком формате высылать данные?')
    btn_deny = KeyboardButton(text='Отмена')
    markup_deny = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        btn_help, btn_deny
    )

    if debtors_list:
        name = []
        telegram_id = []
        phone_number = []
        debt = []

        for debtor in debtors_list:
            name.append(debtor[1])
            phone_number.append(debtor[4])
            telegram_id.append(debtor[3])
            debt.append(debtor[-1])
        data = {
            "Долг": debt,
            "Номер телефона": phone_number,
            "Телеграм ID": telegram_id,
            "Имя": name
        }
        pd.options.display.max_rows = 10000
        df = pd.DataFrame(data)
        if len(df) > 50:
            for x in range(0, len(df), 50):
                await bot.send_message(message.chat.id, df[x:x + 50])
        else:
            await message.answer(
                text=str(df),
                reply_markup=markup_deny
            )
    else:
        await message.answer(
            "Отправьте мне телеграм id, имя пользователя или номер" 
            "телефона чтобы найти должника.",
            reply_markup=markup_deny
        )


@dp.message_handler(text='В каком формате высылать данные?', state=AdminState.search_for_debtors)
async def explain_info_form(message: types.Message):
    msg = "Номер телефона начинается со знака + и пишется без пробелов.\n\n" \
          "Имя пользователя (юзернейм) отправлять начиная знаком @\n\n" \
          "Телеграм ID цифрами, как есть. " \
          "Просто перешлите сообщение от нужного человека в этого бота - @getmyid_bot" \
          " и выберите поле id в графе Forwarded from"
    await message.answer(msg)


@dp.message_handler(text='Отмена', state=AdminState.search_for_debtors)
async def stop_searching(message: types.Message):
    await AdminState.users.set()
    await message.answer(
        text='Эх, щас бы накидали долгов по 10, 15к...',
        reply_markup=admin.markup_users
    )


@dp.message_handler(user_id=ADMINS, state=AdminState.search_for_debtors)
async def filter_user_info(message: types.Message, state: FSMContext):
    data = str(message.text)

    # filter user info
    if data.startswith('+'):
        user = await db.select_user(phone_number=data)
    elif data.startswith('@'):
        user = await db.select_user(username=data[1:])
    else:
        user = await db.select_user(telegram_id=int(data))

    # post filter
    try:
        name = user[1]
        username = user[2]
        debt = user[-1]
        await AdminState.debt_panel.set()
        if username:
            await message.answer(
                f"Долг пользователя составляет: {debt}\n\n"
                f"Имя: {name}\n"
                f"Юзернейм: @{username}",
                reply_markup=admin.markup_debt_panel
            )
        else:
            await message.answer(
                f"Долг пользователя составляет: {debt}\n\n"
                f"Имя: {name}\n",
                reply_markup=admin.markup_debt_panel
            )

        # saving data into state storage
        await state.set_data(
            {
                'telegram_id': user[3],
                'name': name,
                'username': username
            }
        )
    except TypeError:
        await message.reply(text='Пользователь не найден')


@dp.message_handler(text='Изменить запись', state=AdminState.debt_panel)
async def ask_for_debt_value(message: types.Message):
    await AdminState.change_debt.set()
    await message.answer(
        text='Введите новое значение',
        reply_markup=admin.markup_deny
    )


@dp.message_handler(user_id=ADMINS, state=AdminState.change_debt)
async def change_debt(message: types.Message, state: FSMContext):
    try:
        debt = int(message.text)

        data = await state.get_data()
        telegram_id = data['telegram_id']

        await db.update_user_debt(debt, telegram_id)
        await AdminState.debt_panel.set()
        await message.reply(
            text='Значение записано', reply_markup=admin.markup_debt_panel
        )
    except ValueError as err:
        await message.reply('Введите число!')
        logging.exception(err)


@dp.message_handler(text='Забыть долг', state=AdminState.debt_panel)
async def forget_debt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data['telegram_id']
    await db.update_user_debt(0, telegram_id)
    await message.answer(text='Долг забыт')


@dp.message_handler(text='Просмотреть записи', state=AdminState.debt_panel)
async def refresh_debt_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data['telegram_id']
    user = await db.select_user(telegram_id=telegram_id)
    debt = user[-1]
    await message.answer(
        text=f"Долг пользователя составляет: {debt}"
    )
