from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline import admin as iadmin
from typing import Union
from loader import db


async def get_pc_list(page: int = 0) -> Union[str | InlineKeyboardMarkup]:
    """
    Takes an integer page value as input, returns 10, or all remaining PCs in the list as a keyboard
    """
    i = 0
    if page < 0:
        return "Это последняя страница"

    pc_list = await db.select_computers()
    if len(pc_list) == 0:
        return "Список пк пуст"

    markup_pc_list = InlineKeyboardMarkup(row_width=5)
    btn_prev = InlineKeyboardButton(text='◀️', callback_data='prev')
    btn_next = InlineKeyboardButton(text='▶️', callback_data='next')

    if page == 0:
        i = 1
        for pc in pc_list[:10]:
            markup_pc_list.insert(
                InlineKeyboardButton(
                    text=pc[0], callback_data=pc[0]
                )
            )
    else:
        page_start = int(f"{page}0")
        page_end = int(f"{page + 1}0")

        for pc in pc_list[page_start:page_end]:
            i = 0
            if str(pc[0]).startswith(str(page)):
                i += 1
                markup_pc_list.insert(
                    InlineKeyboardButton(
                        text=pc[0], callback_data=pc[0]
                    )
                )
            else:
                print('holy shit')
                return "Это последняя страница"

    markup_pc_list.add(btn_prev, btn_next).row(iadmin.btn_back)
    if i > 0:
        return markup_pc_list
    return "Это последняя страница"


async def get_pc_info(pc_id: int) -> str:
    pc = await db.select_pc(pc_id)

    price = pc[1]
    available = pc[2]
    is_booked = pc[3]
    customer_id = pc[4]
    booking_time_start = pc[5]
    booking_time_end = pc[6]

    msg = f"ПК №{pc_id}\n\n" \
          f"Цена: {price}\n" \
          f"Доступность: {available}\n"

    if is_booked:
        msg += f"Бронь: {available}\n" \
               f"Клиент: {customer_id}\n" \
               f"Начало бронирования: {booking_time_start}\n" \
               f"Конец: {booking_time_end}"
    else:
        msg += "\n<i>Пк не забронирован</i>"

    return msg
