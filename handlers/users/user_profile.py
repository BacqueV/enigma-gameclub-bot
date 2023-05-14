from loader import dp, db
from aiogram import types
from keyboards.default import client
from states.client import ClientState
from aiogram.dispatcher import FSMContext


@dp.message_handler(text=['Профиль', 'Посмотреть изменения'], state=(None, ClientState.user_profile))
async def get_user_data(message: types.Message):
    await ClientState.user_profile.set()

    user_id = message.from_user.id
    user = await db.select_user(telegram_id=user_id)

    full_name = user.get('full_name')
    telegram_id = user.get('telegram_id')
    debt = user.get('debt')
    username = user.get('username')
    phone_number = user.get('phone_number')


    msg = "<b>Ваш профиль</b>\n\n" \
          f"Полное имя: {full_name}\n" \
          f"Телеграм ID: {telegram_id}\n"
    if username:
        msg += f"Имя пользователя: @{username}\n"
    if phone_number:
        msg += f"Номер телефона: {phone_number}\n\n"
    if debt > 0:
        msg += f"<b>ДОЛГ: {debt}</b>"

    await message.answer(msg, reply_markup=client.markup_user_profile)


@dp.message_handler(text='Назад', state=ClientState.user_profile)
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()

    await message.answer(text='Основное меню', reply_markup=client.markup_main_menu)


@dp.message_handler(text='Изменить имя пользователя', state=ClientState.user_profile)
async def change_username(message: types.Message):
    new_username = message.from_user.username

    if new_username:
        telegram_id = message.from_user.id
        await db.update_user_username(new_username, telegram_id)

        await message.answer('Новое имя пользователя сохранено')
    else:
        await message.reply('Ошибка.\n'
                            'Возможно у вас отсутствует имя пользователя')


@dp.message_handler(content_types=types.ContentType.CONTACT, state=ClientState.user_profile)
async def change_phone_number(message: types.Message):
    new_phone_number = message['contact']['phone_number']
    telegram_id = message.from_user.id

    await db.update_user_phone_number(new_phone_number, telegram_id)
    await message.answer('Новый номер телефона сохранен')
