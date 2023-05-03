from loader import dp, db
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from states.client import ClientState


@dp.message_handler(text='Свободные пк')
async def get_pc_list(message: types.Message, state: FSMContext):
    pc_list = await db.select_free_pc()
    pc_keyboard = InlineKeyboardMarkup(row_width=5)

    await ClientState.ordering_pc.set()

    for pc in pc_list:
        pc_keyboard.insert(InlineKeyboardButton(text=pc[0], callback_data=pc[0]))

    await message.answer(text='Успейте забронировать!', reply_markup=pc_keyboard)
