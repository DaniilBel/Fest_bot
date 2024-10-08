from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from decouple import config

from main import bot
from db.store import *

user_router = Router()
GROUP_CHAT_ID = config('GROUP')

user_can_send_to_support = {}


@user_router.message(F.chat.type.in_("private") & F.text.startswith('/points'))
async def show_user_points(message: Message):
    print("/points")
    try:
        user_id = message.from_user.id

        user_info = await get_user_info(user_id)
        points = user_info['points']
        # deposit = user_info['deposit']
        # await message.answer(f"Welcome! You have {points} points and {deposit} in your deposit.")

        await message.answer(f"{points}" if points is not None else 0)
    except Exception as e:
        print(e)
        await message.answer("0")


@user_router.message(lambda message: message.chat.type in ["private"] and message.text in available_text_tasks)
async def select_text_task(message: Message):
    print("text_task")
    user_id = message.from_user.id
    user_selected_task[user_id] = message.text
    await message.answer(f"{message.text}\n\nОтвет напишите текстом:")


@user_router.message(lambda message: message.chat.type in ["private"] and message.text in available_media_tasks)
async def select_media_task(message: Message):
    print("text_task")
    user_id = message.from_user.id
    user_selected_task[user_id] = message.text
    await message.answer(f"{message.text}\n\nВ качестве ответа пришлите фото/видео/кружочек:")


@user_router.message(F.chat.type.in_("private") & F.text == 'Написать в техподдержку')
async def tech_support_menu(message: Message):
    print("Check")
    user_id = message.from_user.id
    user_can_send_to_support[user_id] = True
    await message.answer("Опишите, что вас беспокоит")


@user_router.message(lambda message: message.chat.type in ["private"] and message.text not in available_shortcut_tasks
                                     and not user_can_send_to_support.get(message.from_user.id) is None)
# @user_router.message(F.chat.type.in_("private") & F.text)
# @user_router.message(lambda message: not user_can_send_to_support.get(message.from_user.id) is None)
async def forward_text_to_support(message: Message):
    print("forward to support")
    # if message.chat.id != GROUP_CHAT_ID:
    user_id = message.from_user.id

    print(user_can_send_to_support.get(user_id))
    if user_can_send_to_support.get(user_id) and not user_can_send_to_support.get(user_id) is None:
        forwarded_message = await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Игрок {message.from_user.full_name} с id: {message.from_user.id} отправил:\n{message.text}")

        message_mapping[forwarded_message.message_id] = message.from_user.id

        # await bot.send_message(chat_id=message.chat.id, text="Your message has been forwarded to support")
        user_can_send_to_support[user_id] = False
        await message.answer("Ответ получен.")


@user_router.message(lambda message: message.chat.type in ["private"] and user_selected_task.get(
    message.from_user.id) in available_text_tasks)
# @user_router.message(F.chat.type.in_("private") & F.text)
async def forward_text_to_support(message: Message):
    if message.text.lower() == "aboba".lower():
        await message.answer("Ответ засчитан")
    else:
        await message.answer("Ответ не засчитан\nВ случае несогласия пишите в техподдержку")


@user_router.message(F.chat.type.in_("private") & F.photo and (lambda message: user_selected_task.get(
    message.from_user.id) in available_media_tasks or user_can_send_to_support.get(message.from_user.id) is True))
async def forward_photo_to_support(message: Message):
    photo = message.photo[-1]
    forwarded_message = await bot.send_photo(
        GROUP_CHAT_ID,
        photo.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил фото"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")


@user_router.message(F.chat.type.in_("private") & F.video and (lambda message: user_selected_task.get(
    message.from_user.id) in available_media_tasks or user_can_send_to_support.get(message.from_user.id) is True))
@user_router.message(lambda message: user_selected_task.get(message.from_user.id) in available_media_tasks)
async def forward_video_to_support(message: Message):
    video = message.video
    forwarded_message = await bot.send_video(
        GROUP_CHAT_ID,
        video.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил видео"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")


@user_router.message(F.chat.type.in_("private") & F.video_note and (lambda message: user_selected_task.get(
    message.from_user.id) in available_media_tasks or user_can_send_to_support.get(message.from_user.id) is True))
@user_router.message(lambda message: user_selected_task.get(message.from_user.id) in available_media_tasks)
async def forward_video_note_to_support(message: Message):
    video_note = message.video_note
    forwarded_message = await bot.send_video_note(
        GROUP_CHAT_ID,
        video_note.file_id,
        caption=f"Игрок {message.from_user.full_name} отправил кружочек"
    )

    message_mapping[forwarded_message.message_id] = message.from_user.id
    await message.answer("Отправлено на проверку.")
