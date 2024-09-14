from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# def make_inline_keyboard(items: list[str]) -> InlineKeyboardMarkup:
#     row = [InlineKeyboardButton(text=item, callback_data="change_text") for item in items]
#     return InlineKeyboardMarkup(inline_keyboard=[row])


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
