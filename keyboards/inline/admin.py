from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


btn_change_price = InlineKeyboardButton(
    text='Изменить цену', callback_data='change_price'
)
btn_change_availability = InlineKeyboardButton(
    text='Изменить доступность', callback_data='change_availability'
)
btn_back = InlineKeyboardButton(
    text='Назад', callback_data='back'
)

markup_pc_menu = InlineKeyboardMarkup(row_width=2).add(
    btn_change_price, btn_change_availability,
    btn_back
)

markup_gap = InlineKeyboardMarkup().add(InlineKeyboardButton(text='...', callback_data='...'))

markup_deny = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Отмена', callback_data='deny')
)
