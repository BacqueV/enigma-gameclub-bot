import asyncio
from aiogram import types
from data.config import ADMINS
from loader import dp, db, bot
from states.admin import AdminState
from keyboards.default import admin


@dp.message_handler(text=['/advert', 'Реклама'], user_id=ADMINS, state=AdminState.categories)
async def get_ad_msg(message: types.Message):
    await AdminState.get_ad_msg.set()
    await message.answer(text='Можно отравлять сообщения, фотографии, видео, аудио и голосовые сообщения. По одному',
                         reply_markup=admin.markup_deny)


@dp.message_handler(user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_msg(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    for user in users:
        user_id = user[3]
        await bot.send_message(chat_id=user_id, text=message.text)
        await asyncio.sleep(0.05)

    await message.answer('<i>Сообщение разослано всем</i>')


@dp.message_handler(content_types=types.ContentTypes.PHOTO, user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_photo(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    try:
        for user in users:
            user_id = user[3]
            await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
            await asyncio.sleep(0.05)

        await message.answer('<i>Картинка разослана всем</i>')
    except Exception as err:
        await message.answer(text=f'Во время рассылки возникла ошибка:\n{err}')


@dp.message_handler(content_types=types.ContentTypes.VIDEO, user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_video(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    try:
        for user in users:
            user_id = user[3]
            await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption)
            await asyncio.sleep(0.05)

        await message.answer('<i>Видео разослано всем</i>')
    except Exception as err:
        await message.answer(text=f'Во время рассылки возникла ошибка:\n{err}')


@dp.message_handler(content_types=types.ContentTypes.AUDIO, user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_audio(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    try:
        for user in users:
            user_id = user[3]
            await bot.send_audio(chat_id=user_id, audio=message.audio.file_id, caption=message.caption)
            await asyncio.sleep(0.05)

        await message.answer('<i>Аудио разослано всем</i>')
    except Exception as err:
        await message.answer(text=f'Во время рассылки возникла ошибка:\n{err}')


@dp.message_handler(content_types=types.ContentTypes.VOICE, user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_voice(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    try:
        for user in users:
            user_id = user[3]
            await bot.send_voice(chat_id=user_id, voice=message.voice.file_id, caption=message.caption)
            await asyncio.sleep(0.05)

        await message.answer('<i>Голосовое сообщение разослано всем</i>')
    except Exception as err:
        await message.answer(text=f'Во время рассылки возникла ошибка:\n{err}')


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, user_id=ADMINS, state=AdminState.get_ad_msg)
async def send_ad_document(message: types.Message):
    users = await db.select_all_users()
    await message.answer(text='Сообщение рассылается...', reply_markup=admin.markup_categories)
    await AdminState.categories.set()

    try:
        for user in users:
            user_id = user[3]
            await bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption)
            await asyncio.sleep(0.05)

        await message.answer('<i>Документ разослан всем</i>')
    except Exception as err:
        await message.answer(text=f'Во время рассылки возникла ошибка:\n{err}')
