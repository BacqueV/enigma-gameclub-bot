import logging

from aiogram import Dispatcher

from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        # remove later the if statement
        if int(admin) == 898757368:
            print(f'{admin} - admin\nremove this feature on production')
            try:
                await dp.bot.send_message(admin, "Бот начал работать")

            except Exception as err:
                logging.exception(err)
