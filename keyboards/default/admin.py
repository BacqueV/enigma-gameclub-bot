from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# buttons
btn_back = KeyboardButton(text='Назад')

btn_advert = KeyboardButton(text='Реклама')
btn_users = KeyboardButton(text='Пользователи')
btn_computers = KeyboardButton(text='Компьютеры')

btn_user_list = KeyboardButton(text='Список пользователей')
btn_pc_list = KeyboardButton(text='Список компьютеров')
btn_clean = KeyboardButton(text='Очистить')
btn_update_debt = KeyboardButton(text='Задолженности')
btn_delete = KeyboardButton(text='Удалить')

btn_refresh_debt_info = KeyboardButton(text='Просмотреть записи')
btn_change_debt = KeyboardButton(text='Изменить запись')
btn_delete_debt = KeyboardButton(text='Забыть долг')

btn_add_pc = KeyboardButton(text='Добавить пк')
btn_remove_pc = KeyboardButton(text='Удалить пк')

# inline buttons
ibtn_change_price = InlineKeyboardButton(
    text='Изменить цену', callback_data='change_price'
)
ibtn_change_availability = InlineKeyboardButton(
    text='Изменить доступность', callback_data='change_availability'
)
ibtn_back = InlineKeyboardButton(
    text='Назад', callback_data='back'
)

# markups
markup_categories = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_advert).add(btn_users, btn_computers, btn_back)

markup_users = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_user_list).row(btn_clean, btn_update_debt, btn_delete).insert(btn_back)

markup_debt_panel = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).row(btn_refresh_debt_info).add(btn_change_debt, btn_delete_debt).insert(btn_back)

markup_deny = ReplyKeyboardMarkup(resize_keyboard=True).row(btn_back)

deny_default = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(btn_back, KeyboardButton(text='По умолчанию'))

markup_computers = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).add(btn_pc_list, btn_add_pc).add(btn_clean, btn_delete, btn_back)

imarkup_pc_menu = InlineKeyboardMarkup(row_width=2).add(
    ibtn_change_price, ibtn_change_availability,
    ibtn_back
)

imarkup_gap = InlineKeyboardMarkup().add(InlineKeyboardButton(text='...', callback_data='...'))

imarkup_deny = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Отмена', callback_data='deny')
)
