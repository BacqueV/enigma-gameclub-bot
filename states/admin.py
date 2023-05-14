from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminState(StatesGroup):
    # menus
    categories = State()
    users = State()
    computers = State()

    # users
    search_for_debtors = State()
    debt_panel = State()
    change_debt = State()

    get_ad_msg = State()
    users_choice = State()

    # computers
    pc_choice = State()
    add_pc = State()
    delete_pc = State()
