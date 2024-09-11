from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from decouple import config

from main import bot
from db.store import message_mapping, user_points
from keyboards.intro import make_row_keyboard
from strings import stories

user_router = Router()
GROUP_CHAT_ID = config('GROUP')
START_STORY = stories.get("start_story")

help_message = """
/points
"""

available_shortcut_tasks = [
    stories.get("task1_short"),
    stories.get("task2_short"),
    stories.get("task3_short"),
                            ]


@user_router.message(Command("start"))
async def user_start(message: Message):
    await message.answer(
        text=START_STORY,
        reply_markup=make_row_keyboard(available_shortcut_tasks)
    )


@user_router.message(Command('points'))
async def show_user_points(message: Message):
    user_id = message.from_user.id
    points = user_points.get(user_id)
    await message.answer(points)


@user_router.message(Command('help'))
async def show_help(message: Message):
    await message.answer(help_message)


@user_router.message(lambda message: message.chat.type in ["private"] and message.text not in available_shortcut_tasks)
async def forward_text_to_support(message: Message):
    if message.chat.id != GROUP_CHAT_ID:
        forwarded_message = await bot.forward_message(
            chat_id=GROUP_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id)
            # f"User {message.from_user.full_name} sent:\n{message.text}")
        message_mapping[forwarded_message.message_id] = message.from_user.id

        # await bot.send_message(chat_id=message.chat.id, text="Your message has been forwarded to support")
        await message.answer("Отправлено на проверку.")


@user_router.message(F.photo)
async def forward_photo_to_support(message: Message):
    photo = message.photo[-1]
    forwarded_message = await bot.send_photo(
        GROUP_CHAT_ID,
        photo.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил фото"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")


@user_router.message(F.video)
async def forward_video_to_support(message: Message):
    video = message.video
    forwarded_message = await bot.send_video(
        GROUP_CHAT_ID,
        video.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил видео"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")


@user_router.message(F.video_note)
async def forward_video_note_to_support(message: Message):
    video_note = message.video_note
    forwarded_message = await bot.send_video_note(
        GROUP_CHAT_ID,
        video_note.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил кружочек"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")


@user_router.message(Command("getchatid"))
async def get_chat_id(message: Message):
    try:
        await message.answer(f"Chat id is: *{message.chat.id}*\nYour id is: *{message.from_user.id}*", parse_mode='Markdown')
    except Exception as e:
        await message.answer("Error from get_chat_id",
                             parse_mode='Markdown')
