from aiogram.fsm.state import StatesGroup, State

class AdminSizes(StatesGroup):
    add_title = State()
    add_qty = State()
    rename = State()
    set_qty = State()
