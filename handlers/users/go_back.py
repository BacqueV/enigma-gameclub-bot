from loader import dp
from states.admin import AdminState
from keyboards.default import admin, client
from aiogram import types
from aiogram.dispatcher import FSMContext


# прекратить работу с конкретной таблицей из БД и вернуться к их выбору
@dp.message_handler(text='Назад', state=AdminState.users)
async def go_to_categories(message: types.Message):
    await AdminState.categories.set()
    await message.answer(text='Выберите таблицу с которой будете работать', reply_markup=admin.markup_categories)


# возврат из админ панели
@dp.message_handler(text='Назад', state=AdminState.categories)
async def close_admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text='Закрытие админ панели', reply_markup=client.markup_main_menu)


# возврат к таблице пользователей после просмотра долгов
@dp.message_handler(text='Назад', state=AdminState.change_debt)
async def go_to_users(message: types.Message, state: FSMContext):
    await state.finish()
    await AdminState.users.set()
    await message.answer(text='Таблица пользователей', reply_markup=admin.markup_users)
