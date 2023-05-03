from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, db, bot
from data.config import ADMINS
from aiogram.dispatcher import FSMContext
from keyboards.default.client import markup_main_menu


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await db.create_table_users()
    await state.finish()

    if message.from_user.username:
        name = f"@{message.from_user.username}"
    else:
        name = message.from_user.full_name

    try:
        user = await db.select_user(telegram_id=message.from_user.id)
        if user is None:
            user = await db.add_user(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name,
                username=message.from_user.username,
            )
            # informing ADMINS
            count = await db.count_users()
            if message.from_user.username:
                msg = f"@{user[2]} Был добавлен в БД.\nВ БД {count} пользователей."
            else:
                msg = f"{user[1]} Был добавлен в БД.\nВ БД {count} пользователей."
            await bot.send_message(chat_id=ADMINS[0], text=msg)
        # user = await db.select_user(telegram_id=message.from_user.id)
        # await bot.send_message(chat_id=ADMINS[0], text=f"@{name} уже числится в БД")
        await message.answer(f"Привет! {name}", reply_markup=markup_main_menu)
    except Exception as ex:
        print(ex)
        await message.answer(str(ex))
