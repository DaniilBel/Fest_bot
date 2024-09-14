from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards.intro import make_row_keyboard
from keyboards.kasino import contribute_keyboard, withdraw_keyboard
from strings import stories
from db.store import *

START_STORY = stories.get("start_story")

util_user_router = Router()

help_message = """
/points - выводит текущее количество баллов
"""


@util_user_router.message((lambda message: message.chat.type in ["private"]) and Command("start"))
async def user_start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    await add_user(user_id, user_name)

    await message.answer(
        text=START_STORY,
        reply_markup=make_row_keyboard(available_shortcut_tasks)
    )
    # if user_contributions.get(user_id) is None:
    #     user_contributions[user_id] = 0
    #
    # if user_points.get(user_id) is None:
    #     user_points[user_id] = 0

    # user_info = await get_user_info(user_id)
    # points = user_info['points']
    # deposit = user_info['deposit']
    # await message.answer(f"Welcome {user_name}! You have {points} points and {deposit} in your deposit.")


@util_user_router.message((lambda message: message.chat.type in ["private"]) and F.text == "Назад")
async def go_back(message: Message):
    user_selected_task[message.from_user.id] = None
    await message.answer("Выберите задание")


@util_user_router.message((lambda message: message.chat.type in ["private"]) and F.text == "Кол-во баллов на вкладе")
async def point_in_deposit(message: Message):
    user_id = message.from_user.id
    user_info = await get_user_info(user_id)
    await message.answer(f"{user_info['deposit']}")


@util_user_router.message((lambda message: message.chat.type in ["private"]) and F.text == "Кол-во баллов")
async def point_into_user(message: Message):
    user_id = message.from_user.id
    user_info = await get_user_info(user_id)
    await message.answer(f"{user_info['points']}")


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
