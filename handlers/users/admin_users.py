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


@dp.message_handler(text='Задолженности', user_id=ADMINS, state=AdminState.users)
async def search_for_debtors(message: types.Message):
    await AdminState.search_for_debtors.set()

    btn_help = KeyboardButton(text='В каком формате высылать данные?')
    btn_deny = KeyboardButton(text='Отмена')
    markup_deny = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        btn_help, btn_deny
    )

    await message.answer(
        text='Отправьте мне телеграм id, имя пользователя или номер телефона.',
        reply_markup=markup_deny
    )


@dp.message_handler(text='В каком формате высылать данные?', user_id=ADMINS, state=AdminState.search_for_debtors)
async def explain_info_form(message: types.Message):
    msg = "Номер телефона начинается со знака + и пишется без пробелов.\n\n" \
          "Имя пользователя (юзернейм) отправлять начиная знаком @\n\n" \
          "Телеграм ID цифрами, как есть. Просто перешлите сообщение от нужного человека в этого бота - @getmyid_bot" \
          " и выберите поле Forwarded from"
    await message.answer(msg)


@dp.message_handler(text='Отмена', user_id=ADMINS, state=AdminState.search_for_debtors)
async def stop_searching(message: types.Message):
    await AdminState.users.set()
    await message.answer(text='Эх, щас бы накидали долгов по 10, 15к...', reply_markup=admin.markup_users)


@dp.message_handler(user_id=ADMINS, state=AdminState.search_for_debtors)
async def filter_user_info(message: types.Message, state: FSMContext):
    data = str(message.text)

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


@dp.message_handler(text='Изменить запись', user_id=ADMINS, state=AdminState.debt_panel)
async def ask_for_debt_value(message: types.Message):
    await AdminState.change_debt.set()
    await message.answer(text='Введите новое значение', reply_markup=admin.markup_deny)


@dp.message_handler(user_id=ADMINS, state=AdminState.change_debt)
async def change_debt(message: types.Message, state: FSMContext):
    try:
        debt = int(message.text)

        data = await state.get_data()
        telegram_id = data['telegram_id']

        await db.update_user_debt(debt, telegram_id)
        await AdminState.debt_panel.set()
        await message.reply(text='Значение записано', reply_markup=admin.markup_debt_panel)
    except ValueError as err:
        print(err)
        await message.reply(text='Введите число!')


@dp.message_handler(text='Забыть долг', user_id=ADMINS, state=AdminState.debt_panel)
async def forget_debt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data['telegram_id']
    await db.update_user_debt(0, telegram_id)
    await message.answer(text='Долг забыт')


@dp.message_handler(text='Просмотреть записи', user_id=ADMINS, state=AdminState.debt_panel)
async def refresh_debt_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data['telegram_id']
    user = await db.select_user(telegram_id=telegram_id)
    debt = user[-1]
    await message.answer(
        text=f"Долг пользователя составляет: {debt}"
    )


# надо дописать, сделать функцию более комплексной
@dp.message_handler(
    text=["/advert", "Реклама"],
    user_id=ADMINS,
    state=AdminState.users
)
async def send_ad_to_all(message: types.Message):
    users = await db.select_all_users()
    for user in users:
        user_id = user[3]
        await bot.send_message(chat_id=user_id, text="@aiogram - join us!")
        await asyncio.sleep(0.05)
