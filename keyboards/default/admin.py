from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# buttons
btn_back = KeyboardButton(text='Назад')

btn_users = KeyboardButton(text='Пользователи')
btn_computers = KeyboardButton(text='Компьютеры')

btn_user_list = KeyboardButton(text='Список пользователей')
btn_clean_users = KeyboardButton(text='Очистить')
btn_delete_users = KeyboardButton(text='Удалить')


btn_add_pc = KeyboardButton(text='Добавить пк')
btn_remove_pc = KeyboardButton(text='Удалить пк')

# external data

# markups
markup_categories = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=1
).add(btn_users, btn_computers)

markup_users = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_user_list).add(btn_clean_users, btn_delete_users, btn_back)
