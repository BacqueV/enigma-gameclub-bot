from aiogram.dispatcher.filters.state import State, StatesGroup


class ClientState(StatesGroup):
    user_profile = State()
