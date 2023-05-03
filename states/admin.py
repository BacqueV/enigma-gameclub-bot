from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminState(StatesGroup):
    # menus
    categories = State()
    users = State()
    computers = State()

    # users
    search_for_debtors = State()
    change_debt = State()

    # middle states
    choice = State()
