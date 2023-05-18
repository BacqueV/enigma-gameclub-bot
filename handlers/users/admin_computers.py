import aiogram.utils.exceptions
import asyncpg.exceptions
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loader import dp, db
from states.admin import AdminState
from keyboards.default import admin
from aiogram.dispatcher import FSMContext


@dp.message_handler(text='Компьютеры', state=AdminState.categories)
async def open_computers(message: types.Message):
    await AdminState.computers.set()
    await message.answer(text='Начата работа с таблицей компьютеров', reply_markup=admin.markup_computers)


@dp.message_handler(text='Список компьютеров', state=AdminState.computers)
async def get_pc_list(message: types.Message):
    try:
        pc_list = await db.select_computers()

        markup_pc_list = InlineKeyboardMarkup(row_width=5)
        btn_prev = InlineKeyboardButton(text='◀️', callback_data='prev')
        btn_next = InlineKeyboardButton(text='▶️', callback_data='next')

        for pc in pc_list:
            markup_pc_list.insert(InlineKeyboardButton(text=pc[0], callback_data=pc[0]))
        markup_pc_list.add(btn_prev, btn_next).row(admin.ibtn_back)

        await message.answer(text='Переключение клавиатуры...', reply_markup=ReplyKeyboardRemove())
        await message.answer(
            text='Нажмите на один из списка чтобы перейти к его настройке',
            reply_markup=markup_pc_list
        )
    except asyncpg.exceptions.UndefinedTableError:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )


@dp.message_handler(text='Очистить', state=AdminState.computers)
async def cleanpc(message: types.Message):
    try:
        await db.clean_pc_list()
        await message.answer('Таблица компьютеров очищена')
    except asyncpg.exceptions.UndefinedTableError:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )


@dp.message_handler(text=['/droppc', 'Удалить'], state=AdminState.computers)
async def droppc(message: types.Message):
    await AdminState.pc_choice.set()

    btn_yes = KeyboardButton(text='Да')
    btn_no = KeyboardButton(text='Нет')
    markup_choice = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1
    ).add(btn_yes, btn_no)

    await message.reply(
        text='Подтверждаете удаление таблицы компьютеров?',
        reply_markup=markup_choice
    )


@dp.message_handler(text=['Да', 'Нет'], state=AdminState.pc_choice)
async def delete_table_computers(message: types.Message):
    if message.text == 'Да':
        await db.drop_computers()
        await message.answer(
            text='Такой таблицы больше не существует',
            reply_markup=admin.markup_computers
        )
    else:
        await message.answer(text='Откат', reply_markup=admin.markup_computers)
    await AdminState.computers.set()


@dp.message_handler(text='Добавить пк', state=AdminState.computers)
async def ask_for_price(message: types.Message):
    await AdminState.add_pc.set()
    await message.answer(
        text='Назначьте цену\n'
             'Или нажмите на кнопку чтобы задать значение по умолчанию (6к)',
        reply_markup=admin.deny_default
    )


@dp.message_handler(text='По умолчанию', state=AdminState.add_pc)
async def add_pc_default(message: types.Message):
    await db.add_pc(6000)
    await AdminState.computers.set()
    await message.answer(
        text='Новый компьютер был успешно добавлен!',
        reply_markup=admin.markup_computers
    )


@dp.message_handler(state=AdminState.add_pc)
async def add_pc(message: types.Message):
    try:
        price = int(message.text)
        await db.add_pc(price)
        await AdminState.computers.set()
        await message.answer(
            text='Новый компьютер успешно добавлен!',
            reply_markup=admin.markup_computers
        )
    except ValueError:
        await message.answer('Введите значение верно!')


@dp.callback_query_handler(state=AdminState.computers)
async def open_pc_menu(call: types.CallbackQuery, state: FSMContext):
    try:
        pc_id = int(call.data)

        await AdminState.pc_menu.set()
        pc = await db.select_pc(pc_id)

        price = pc[1]
        available = pc[2]
        is_booked = pc[3]
        customer_id = pc[4]
        booking_time_start = pc[5]
        booking_time_end = pc[6]

        msg = f"ПК №{pc_id}\n\n" \
              f"Цена: {price}\n" \
              f"Доступность: {available}\n"

        if is_booked:
            msg += f"Бронь: {available}\n" \
                   f"Клиент: {customer_id}\n" \
                   f"Начало бронирования: {booking_time_start}\n" \
                   f"Конец: {booking_time_end}"
        else:
            msg += "\n<i>Пк не забронирован</i>"

        await call.message.edit_text(
            text=msg,
            reply_markup=admin.imarkup_pc_menu
        )
        await state.set_data({"pc_id": pc_id})
    except ValueError:
        await call.answer('Не надо сюда нажимать!')


@dp.callback_query_handler(text='change_price', state=AdminState.pc_menu)
async def ask_for_new_price(call: types.CallbackQuery):
    await call.message.edit_text(
        text='Введите новое значение', reply_markup=admin.imarkup_deny
    )


@dp.message_handler(state=AdminState.pc_menu)
async def change_price(message: types.Message, state: FSMContext):
    try:
        new_price = int(message.text)
        data = await state.get_data('pc_id')
        pc_id = data['pc_id']
        await db.update_pc_price(new_price, pc_id)

        pc = await db.select_pc(pc_id)
        price = pc[1]
        available = pc[2]
        is_booked = pc[3]
        customer_id = pc[4]
        booking_time_start = pc[5]
        booking_time_end = pc[6]

        msg = f"ПК №{pc_id}\n\n" \
              f"Цена: {price}\n" \
              f"Доступность: {available}\n"

        if is_booked:
            msg += f"Бронь: {available}\n" \
                   f"Клиент: {customer_id}\n" \
                   f"Начало бронирования: {booking_time_start}\n" \
                   f"Конец: {booking_time_end}"
        else:
            msg += "\n<i>Пк не забронирован</i>"

        try:
            await message.edit_text(
                text=msg,
                reply_markup=admin.imarkup_pc_menu
            )
        except aiogram.utils.exceptions.MessageCantBeEdited:
            await message.answer(
                text=msg,
                reply_markup=admin.imarkup_pc_menu
            )
        await state.set_data({"pc_id": pc_id})
    except ValueError:
        await message.answer('Введите число!')


@dp.callback_query_handler(text='change_availability', state=AdminState.pc_menu)
async def change_availability(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data('pc_id')
    pc_id = data['pc_id']
    await db.update_pc_availability(pc_id)

    pc = await db.select_pc(pc_id)
    price = pc[1]
    available = pc[2]
    is_booked = pc[3]
    customer_id = pc[4]
    booking_time_start = pc[5]
    booking_time_end = pc[6]

    msg = f"ПК №{pc_id}\n\n" \
          f"Цена: {price}\n" \
          f"Доступность: {available}\n"

    if is_booked:
        msg += f"Бронь: {available}\n" \
               f"Клиент: {customer_id}\n" \
               f"Начало бронирования: {booking_time_start}\n" \
               f"Конец: {booking_time_end}"
    else:
        msg += "\n<i>Пк не забронирован</i>"

    await call.message.edit_text(
        text=msg,
        reply_markup=admin.imarkup_pc_menu
    )
    await state.set_data({"pc_id": pc_id})
    await call.answer('Пользователи (не) могут бронировать этот пк')
