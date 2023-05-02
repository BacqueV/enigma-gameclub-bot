from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminState(StatesGroup):
    categories = State()
    choice = State()
    users = State()
    computers = State()
