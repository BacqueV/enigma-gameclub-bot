import asyncpg
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, db
from states.admin import AdminState
from keyboards.default import admin, client
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(text='...', state='*')
async def answer_the_gap(call: types.CallbackQuery):
    await call.answer('Не надо сюда нажимать')


@dp.message_handler(text='Назад', state=(AdminState.users, AdminState.get_ad_msg, AdminState.computers))
async def go_choose_table(message: types.Message):
    await AdminState.categories.set()
    await message.answer(text='Выберите таблицу с которой будете работать', reply_markup=admin.markup_categories)


@dp.message_handler(text='Назад', state=AdminState.categories)
async def close_admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text='Закрытие админ панели', reply_markup=client.markup_main_menu)


@dp.message_handler(text='Назад', state=AdminState.debt_panel)
async def go_to_users_from_debtors(message: types.Message, state: FSMContext):
    await state.finish()
    await AdminState.users.set()
    await message.answer(text='Таблица пользователей', reply_markup=admin.markup_users)


@dp.message_handler(text='Назад', state=AdminState.change_debt)
async def deny_changing_debt_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    username = data['username']
    telegram_id = data['telegram_id']

    debt = await db.select_user(telegram_id=telegram_id)[-1]

    await AdminState.debt_panel.set()
    await message.answer(text=f'Долг пользователя составляет: {debt}\n\n'
                              f'Имя: {name}\n'
                              f'Юзернейм: @{username}',
                         reply_markup=admin.markup_debt_panel)


@dp.message_handler(text='Назад', state=AdminState.add_pc)
async def stop_adding_pc(message: types.Message):
    await AdminState.computers.set()
    await message.answer(text='Таблица компьютеров', reply_markup=admin.markup_computers)


@dp.callback_query_handler(text='back', state=AdminState.computers)
async def exit_pc_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await AdminState.computers.set()

    await call.message.edit_text(
        text='Переключение клавиатуры...',
        reply_markup=admin.imarkup_gap
    )
    await call.message.answer(
        text='Таблица компьютеров', reply_markup=admin.markup_computers
    )


@dp.callback_query_handler(text='back', state=AdminState.pc_menu)
async def show_pc_list(call: types.CallbackQuery):
    try:
        pc_list = await db.select_computers()

        markup_pc_list = InlineKeyboardMarkup(row_width=5)
        btn_prev = InlineKeyboardButton(text='◀️', callback_data='prev')
        btn_next = InlineKeyboardButton(text='▶️', callback_data='next')

        for pc in pc_list:
            markup_pc_list.insert(InlineKeyboardButton(text=pc[0], callback_data=pc[0]))
        markup_pc_list.add(btn_prev, btn_next).row(admin.ibtn_back)

        await call.message.edit_text(
            text='Выберите пк чтобы перейти к его настройке',
            reply_markup=markup_pc_list
        )
        await AdminState.computers.set()
    except asyncpg.exceptions.UndefinedTableError:
        await call.message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )


@dp.callback_query_handler(text='deny', state=AdminState.pc_menu)
async def deny_changing_pc_price(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data('pc_id')
    pc_id = data['pc_id']

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
