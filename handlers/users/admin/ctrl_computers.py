import aiogram.utils.exceptions
from typing import Union
import asyncpg.exceptions
from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

import handlers.users.go_back
from loader import dp, db
from states.admin import AdminState
from keyboards.default import admin
from keyboards.inline import admin as iadmin
from aiogram.dispatcher import FSMContext
from handlers.users.admin import spec_functions


@dp.message_handler(text='Компьютеры', state=AdminState.categories)
async def open_computers(message: types.Message):
    await AdminState.computers.set()
    await message.answer(text='Начата работа с таблицей компьютеров', reply_markup=admin.markup_computers)


@dp.message_handler(text='Список компьютеров', state=AdminState.computers)
async def get_pc_list(message: Union[types.Message | types.CallbackQuery], state: FSMContext):
    try:
        pc_info = await spec_functions.get_pc_list()
        if not isinstance(pc_info, str):
            await message.answer(
                text='Переключение клавиатуры...', reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                text='Нажмите на один из списка чтобы перейти к его настройке',
                reply_markup=pc_info
            )
            await state.set_data({'page': 0})
        else:
            await message.answer(pc_info)
    except asyncpg.exceptions.UndefinedTableError:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )


@dp.callback_query_handler(text='prev', state=AdminState.computers)
async def get_prev_page(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data['page']

    new_page = await spec_functions.get_pc_list(page - 1)
    if isinstance(new_page, str):
        await call.answer(new_page)
    else:
        await call.message.edit_text(
            text=f"Страница №{page}",
            reply_markup=new_page
        )
        await state.update_data({'page': page - 1})


@dp.callback_query_handler(text='next', state=AdminState.computers)
async def get_next_page(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data['page']

    new_page = await spec_functions.get_pc_list(page + 1)
    if isinstance(new_page, str):
        await call.answer(new_page)
    else:
        await call.message.edit_text(
            text=f"Страница №{page + 2}",
            reply_markup=new_page
        )
        await state.update_data({'page': page + 1})


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


@dp.message_handler(text='Удалить пк', state=AdminState.computers)
async def ask_for_pc_id(message: types.Message):
    await AdminState.del_pc.set()
    await message.answer(
        text='Введите id компьютера, чтобы удалить его и все данные о нем.',
        reply_markup=admin.markup_deny
    )


@dp.message_handler(state=AdminState.del_pc)
async def delete_pc(message: types.Message):
    try:
        pc_id = int(message.text)
        await db.delete_pc(pc_id)
        await message.reply(
            text='ПК был удален',
            reply_markup=admin.markup_computers
        )
        await AdminState.computers.set()
    except Exception as err:
        if isinstance(err, ValueError):
            await message.answer('Введите число!')
        else:
            await message.answer("Ошибка. Возможно этого пк не существует\n\n"
                                 f"{err}")


@dp.callback_query_handler(state=AdminState.computers)
async def open_pc_menu(call: types.CallbackQuery, state: FSMContext):
    try:
        pc_id = int(call.data)
        msg = await spec_functions.get_pc_info(pc_id)
        await call.message.edit_text(
            text=msg,
            reply_markup=iadmin.markup_pc_menu
        )
        await state.update_data({'pc_id': pc_id})
        await AdminState.pc_menu.set()
    except (ValueError, TypeError):
        try:
            await handlers.users.go_back.exit_pc_menu(call, state)
        except aiogram.utils.exceptions.MessageNotModified:
            await call.answer('Не надо сюда нажимать')


@dp.callback_query_handler(text='change_price', state=AdminState.pc_menu)
async def ask_for_new_price(call: types.CallbackQuery):
    await call.message.edit_text(
        text='Введите новое значение', reply_markup=iadmin.markup_deny
    )


@dp.message_handler(state=AdminState.pc_menu)
async def change_price(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data('pc_id')
        new_price = int(message.text)
        pc_id = data['pc_id']
        await db.update_pc_price(new_price, pc_id)

        msg = await spec_functions.get_pc_info(pc_id)

        try:
            await message.edit_text(
                text=msg,
                reply_markup=iadmin.markup_pc_menu
            )
        except aiogram.utils.exceptions.MessageCantBeEdited:
            await message.answer(
                text=msg,
                reply_markup=iadmin.markup_pc_menu
            )
    except ValueError:
        await message.reply('Введите число!')


@dp.callback_query_handler(text='change_availability', state=AdminState.pc_menu)
async def change_availability(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data('pc_id')
    pc_id = data['pc_id']
    await db.update_pc_availability(pc_id)

    msg = await spec_functions.get_pc_info(pc_id)

    await call.message.edit_text(
        text=msg,
        reply_markup=iadmin.markup_pc_menu
    )
    await call.answer('Пользователи (не) могут бронировать этот пк')
