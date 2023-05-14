from loader import dp, db
from states.admin import AdminState
from keyboards.default import admin, client
from aiogram import types
from aiogram.dispatcher import FSMContext


# прекратить работу с конкретной таблицей из БД и вернуться к их выбору
@dp.message_handler(text='Назад', state=(AdminState.users, AdminState.get_ad_msg, AdminState.computers))
async def go_to_categories(message: types.Message):
    await AdminState.categories.set()
    await message.answer(text='Выберите таблицу с которой будете работать', reply_markup=admin.markup_categories)


# выход из админ панели
@dp.message_handler(text='Назад', state=AdminState.categories)
async def close_admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text='Закрытие админ панели', reply_markup=client.markup_main_menu)


# возврат к таблице пользователей после просмотра долгов
@dp.message_handler(text='Назад', state=AdminState.debt_panel)
async def go_to_users(message: types.Message, state: FSMContext):
    await state.finish()
    await AdminState.users.set()
    await message.answer(text='Таблица пользователей', reply_markup=admin.markup_users)


# отказ от изменения значения долга
@dp.message_handler(text='Назад', state=AdminState.change_debt)
async def go_to_debt_panel(message: types.Message, state: FSMContext):
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
