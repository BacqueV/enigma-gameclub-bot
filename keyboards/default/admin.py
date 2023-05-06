from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# buttons
btn_back = KeyboardButton(text='Назад')

btn_advert = KeyboardButton(text='Реклама')
btn_users = KeyboardButton(text='Пользователи')
btn_computers = KeyboardButton(text='Компьютеры')

btn_user_list = KeyboardButton(text='Список пользователей')
btn_clean_users = KeyboardButton(text='Очистить')
btn_update_debt = KeyboardButton(text='Задолженности')
btn_delete_users = KeyboardButton(text='Удалить')

btn_refresh_debt_info = KeyboardButton(text='Просмотреть записи')
btn_change_debt = KeyboardButton(text='Изменить запись')
btn_delete_debt = KeyboardButton(text='Забыть долг')

btn_add_pc = KeyboardButton(text='Добавить пк')
btn_remove_pc = KeyboardButton(text='Удалить пк')

# external data

# markups
markup_categories = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_advert).add(btn_users, btn_computers, btn_back)

markup_users = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_user_list).row(btn_clean_users, btn_update_debt, btn_delete_users).insert(btn_back)

markup_debt_panel = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_refresh_debt_info).add(btn_change_debt, btn_delete_debt).insert(btn_back)

markup_deny = ReplyKeyboardMarkup(resize_keyboard=True).row(btn_back)
