from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    builder = ReplyKeyboardBuilder()

    for item in items:
        builder.button(text=item)

    builder.adjust(2)
    builder.row(
        KeyboardButton(
            text="Кол-во баллов на вкладе"
        ),
        KeyboardButton(
            text="Кол-во баллов"
        )
    )
    builder.row(
        KeyboardButton(
            text="Написать в техподдержку"
        ),
        KeyboardButton(
            text="Назад"
        )
    )
    return builder.as_markup(resize_keyboard=True)
