from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def contribute_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Закинуть баллы", callback_data="contribute"))
    return builder.as_markup()


def withdraw_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Вывести баллы", callback_data="withdraw"))
    return builder.as_markup()
