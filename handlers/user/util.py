from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.intro import make_row_keyboard
from strings import stories
from db.store import available_shortcut_tasks, user_selected_task

START_STORY = stories.get("start_story")

util_user_router = Router()

help_message = """
/points
"""


@util_user_router.message(F.text == "Назад")
async def go_back(message: Message):
    user_selected_task[message.from_user.id] = None
    await message.answer("Выберите задание")


@util_user_router.message(Command("start"))
async def user_start(message: Message):
    await message.answer(
        text=START_STORY,
        reply_markup=make_row_keyboard(available_shortcut_tasks)
    )


@util_user_router.message(Command('help'))
async def show_help(message: Message):
    await message.answer(help_message)


@util_user_router.message(Command("getchatid"))
async def get_chat_id(message: Message):
    try:
        await message.answer(f"Chat id is: *{message.chat.id}*\nYour id is: *{message.from_user.id}*",
                             parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Error from get_chat_id {e}",
                             parse_mode='Markdown')
