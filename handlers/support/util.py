from aiogram import Router, F
from aiogram.types import Message
from db.store import user_points

util_support_router = Router()

help_message = """
(reply) Текст
(reply) /award points
/setpoints user_id points
"""


@util_support_router.message(F.chat.type.in_({"group", "supergroup"}) & F.text.startswith('/help'))
async def show_help(message: Message):
    await message.answer(help_message)


@util_support_router.message(F.chat.type.in_({"group", "supergroup"}) & F.text.startswith('/points'))
async def show_help(message: Message):
    await message.answer(str(user_points))


@util_support_router.message(F.chat.type.in_({"group", "supergroup"}) & ~F.reply_to_message)
async def handle_non_reply_message(message: Message):
    return
