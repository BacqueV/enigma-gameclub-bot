from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# buttons
btn_back = KeyboardButton(text='Назад')
btn_user_profile = KeyboardButton(text='Профиль')
btn_see_changes = KeyboardButton(text='Посмотреть изменения')
btn_my_orders = KeyboardButton(text='Забронированные мной')
btn_pc_list = KeyboardButton(text='Все пк')
btn_free_pc_list = KeyboardButton(text='Свободные пк')
btn_change_username = KeyboardButton(text='Изменить имя пользователя')
btn_change_phone_number = KeyboardButton(text='Изменить номер телефона', request_contact=True)

# external data

# markups
markup_main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_user_profile).add(btn_free_pc_list, btn_pc_list, btn_my_orders)

markup_user_profile = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_see_changes).add(btn_change_username, btn_change_phone_number).row(btn_back)
