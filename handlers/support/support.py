import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions, ReactionTypeEmoji
from decouple import config

from main import bot
from db.store import *

support_router = Router()
GROUP_CHAT_ID = config('GROUP')
emo = ["👎", "🔥"]


@support_router.message(F.chat.type.in_({"group", "supergroup"}) & F.reply_to_message & ~F.text.startswith('/award') & ~F.text.startswith('/setpoints'))
async def forward_reply_to_user(message: Message):
    original_message = message.reply_to_message

    if original_message.message_id in message_mapping:
        user_id = message_mapping[original_message.message_id]

        react = ReactionTypeEmoji(emoji=emo[1])
        await message.react([react])

        if message.text:
            await bot.send_message(user_id, f"Ответ поддержки:\n{message.text}")
        elif message.photo:
            photo = message.photo[-1]
            await bot.send_photo(user_id, photo.file_id, caption="Поддержка решила ответить фоткой")
        elif message.video:
            video = message.video
            await bot.send_video(user_id, video.file_id, caption="Поддержка решила ответить видео")
        elif message.video_chat_ended:
            video_note = message.video_note
            await bot.send_video(user_id, video_note.file_id, caption="Поддержка решила ответить кружочком")

        # del message_mapping[original_message.message_id]

    else:
        print(f"Сообщение не может быть отослано обратно: {message.text}")


@support_router.message(F.chat.type.in_({"group", "supergroup"}) & F.reply_to_message & F.text.startswith('/award'))
async def handle_support_award(message: Message):
    original_message = message.reply_to_message

    if original_message.message_id in message_mapping:
        user_id = message_mapping[original_message.message_id]

        try:
            _, points = message.text.split()
            points = int(points)
        except ValueError:
            await message.answer("Неправильный формат `/award <points>`")
            return

        if points == 0:
            await bot.send_message(user_id, "Задание не зачтено.")

        user_info = await get_all_users()
        user_points = await get_user_info(user_id)
        p = user_points['points']

        if user_id in user_info['user_id']:
            await update_user_points(user_id, p + points)
        else:
            await update_user_points(user_id, points)

        await bot.send_message(user_id, "Задание зачтено.")
        await message.answer(f"Игрок с id {user_id} получил {points} чего-то от {message.from_user.username}. "
                             f"Сейчас у него {user_points.get(user_id)} чего-то")

        # Optionally, remove the message from pending after points are awarded
        del message_mapping[original_message.message_id]


@support_router.message(F.chat.type.in_({"group", "supergroup"}) & F.text.startswith('/setpoints'))
async def handle_edit_points(message: Message):
    try:
        # Parse the command /edit_points <user_id> <points>
        _, user_id, points = message.text.split()
        user_id = int(user_id)
        points = int(points)

        user_points = await get_user_info(user_id)
        username = user_points['name']
        p = user_points['points']

        # Edit the user's points manually
        await update_user_points(user_id, points)
        # Inform the support member and the user about the updated points
        await message.answer(f"У игрока {username}({user_id}) было изменено количество баллов до {points}. "
                             f"Изменил {message.from_user.username}")
        await bot.send_message(user_id, f"Количество баллов обновлено")
    except ValueError:
        await message.answer(f"Неправильный формат `/setpoints <user_id> <points>`")
    except KeyError:
        await message.answer("Игрок не найден")


async def unrestrict_user(user_id: int):
    """Function to lift restriction after 5 minutes."""
    await asyncio.sleep(180)
    if user_id in restricted_users:
        await bot.restrict_chat_member(
            GROUP_CHAT_ID,
            user_id,
            ChatPermissions(can_send_messages=True)  # Allow sending messages again
        )
        restricted_users.pop(user_id)

        await bot.send_message(user_id, "Теперь снова можете отправить сообщение")


