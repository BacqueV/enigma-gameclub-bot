import asyncpg
from loader import dp, db
from states.admin import AdminState
from states.client import ClientState
from keyboards.default import admin, client
from keyboards.inline import admin as iadmin
from aiogram import types
from aiogram.dispatcher import FSMContext
from handlers.users.admin import spec_functions


@dp.message_handler(text='Назад', state=[AdminState.get_ad_msg, AdminState.computers, AdminState.users])
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
    await message.answer(
        text=f'Долг пользователя составляет: {debt}\n\n'
             f'Имя: {name}\n'
             f'Юзернейм: @{username}',
        reply_markup=admin.markup_debt_panel
    )


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
        reply_markup=iadmin.markup_gap
    )
    await call.message.answer(
        text='Таблица компьютеров', reply_markup=admin.markup_computers
    )


@dp.callback_query_handler(text='back', state=AdminState.pc_menu)
async def back_to_pc_list(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    try:
        markup_pc_list = await spec_functions.get_pc_list(page)
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
    data = await state.get_data()
    pc_id = data['pc_id']

    msg = await spec_functions.get_pc_info(pc_id)

    await call.message.edit_text(
        text=msg,
        reply_markup=iadmin.markup_pc_menu
    )


@dp.message_handler(text='Назад', state=ClientState.user_profile)
async def exit_user_profile(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text='Основное меню', reply_markup=client.markup_main_menu)


@dp.message_handler(text='Назад', state=AdminState.del_pc)
async def stop_removing_pc(message: types.Message):
    await AdminState.computers.set()
    await message.answer(
        text='Откат',
        reply_markup=admin.markup_computers
    )


@dp.callback_query_handler(text='...', state='*')
async def answer_the_gap(call: types.CallbackQuery):
    await call.answer('Не надо сюда нажимать')
