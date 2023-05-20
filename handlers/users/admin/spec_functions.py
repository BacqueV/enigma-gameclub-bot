from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline import admin as iadmin
from typing import Union
from loader import db


async def get_pc_list(page: int = 0) -> Union[str | InlineKeyboardMarkup]:
    """
    Takes an integer page value as input, returns 10, or all remaining PCs in the list as a keyboard
    """
    if page < 0:
        return "Это последняя страница"
    markup_pc_list = InlineKeyboardMarkup(row_width=5)
    btn_prev = InlineKeyboardButton(text='◀️', callback_data='prev')
    btn_next = InlineKeyboardButton(text='▶️', callback_data='next')

    pc_count = await db.count_computers()
    delta = (page + 1) * 10 + 1

    if pc_count == 0:
        return "Список пк пуст"
    else:
        for pc in range(page * 10 + 1, delta):
            if pc > pc_count:
                markup_pc_list.add(btn_prev).row(iadmin.btn_back)
                return markup_pc_list
            markup_pc_list.insert(
                InlineKeyboardButton(
                    text=str(pc), callback_data=str(pc)
                )
            )
        markup_pc_list.add(btn_prev, btn_next).row(iadmin.btn_back)
    return markup_pc_list


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
