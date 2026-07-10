"""FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class AddCard(StatesGroup):
    name = State()
    number = State()
    holder = State()


class EditCard(StatesGroup):
    name = State()
    holder = State()
    number = State()


class SetPin(StatesGroup):
    new = State()
    confirm = State()


class RemovePin(StatesGroup):
    current = State()


class ManagePin(StatesGroup):
    verify = State()  # PIN boshqaruvini ochish uchun joriy PIN'ni tekshirish


class Unlock(StatesGroup):
    pin = State()


class Backup(StatesGroup):
    file = State()
