import asyncpg.exceptions
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import logging
from loader import dp, db
from states.admin import AdminState
from keyboards.default import admin


@dp.message_handler(text='Компьютеры', state=AdminState.categories)
async def open_computers(message: types.Message):
    await AdminState.computers.set()
    await message.answer(text='Начата работа с таблицей компьютеров', reply_markup=admin.markup_computers)


@dp.message_handler(text='Список компьютеров', state=AdminState.computers)
async def get_pc_list(message: types.Message):
    try:
        pc_count = await db.count_computers()

        pc_list = InlineKeyboardMarkup(row_width=5)
        btn_prev = InlineKeyboardButton(text='◀️', callback_data='prev')
        btn_next = InlineKeyboardButton(text='▶️', callback_data='next')
        btn_clean = InlineKeyboardButton(text='🧹', callback_data='clean')
        btn_accept = InlineKeyboardButton(text='👌', callback_data='accept')

        for pc in range(pc_count):
            pc_list.insert(InlineKeyboardButton(text=str(pc + 1), callback_data=str(pc)))

        await message.answer(text='Список пк', reply_markup=pc_list)
    except asyncpg.exceptions.UndefinedTableError as err:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )
        logging.exception(err)


@dp.message_handler(text='Очистить', state=AdminState.computers)
async def cleanpc(message: types.Message):
    try:
        await db.clean_pc_list()
        await message.answer('Таблица компьютеров очищена')
    except asyncpg.exceptions.UndefinedTableError as err:
        await message.answer(
            'Ошибка, возможно вы еще не создали эту таблицу\n'
            'Чтобы это сделать, введите /start'
        )
        logging.exception(err)


@dp.message_handler(text=['/dropusers', 'Удалить'], state=AdminState.computers)
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
    await AdminState.delete_pc.set()
    await message.answer(text='Введите номер пк', reply_markup=admin.markup_deny)


@dp.message_handler(state=AdminState.delete_pc)
async def delete_pc(message: types.Message):
    try:
        pc_id = int(message.text)
        await db.remove_pc(pc_id)
        await AdminState.computers.set()
        await message.answer(
            text='Компьютера с таким номером больше нет',
            reply_markup=admin.markup_computers
        )
    except Exception as err:
        if isinstance(err, ValueError):
            await message.answer('Введите число!')
        else:
            await message.answer(
                'Произошла непонятная ошибка.\n'
                'Обратитесь к создателю с временем и датой возникновения ошибки')
            logging.exception(err)
