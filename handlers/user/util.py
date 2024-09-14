import random
from asyncio import sleep
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards.intro import make_row_keyboard
from keyboards.kasino import contribute_keyboard, withdraw_keyboard
from strings import stories
from db.store import (available_shortcut_tasks,
                      user_selected_task,
                      user_points,
                      user_contributions,
                      message_ids_to_delete)
from main import bot

START_STORY = stories.get("start_story")

util_user_router = Router()

help_message = """
/points - выводит текущее количество баллов
"""


class ContributeState(StatesGroup):
    waiting_for_contribution = State()
    waiting_for_withdrawal = State()


@util_user_router.message(Command("start"))
async def user_start(message: Message):
    await message.answer(
        text=START_STORY,
        reply_markup=make_row_keyboard(available_shortcut_tasks)
    )
    # await message.answer(text="Задонать", reply_markup=contribute_keyboard())


@util_user_router.message(F.text == "Назад")
async def go_back(message: Message):
    user_selected_task[message.from_user.id] = None
    await message.answer("Выберите задание")


@util_user_router.message(F.text == "Кол-во баллов на вкладе")
async def go_back(message: Message):
    user_id = message.from_user.id
    await message.answer(f"{user_contributions[user_id] if user_contributions[user_id] is not None else 0}")


@util_user_router.message(F.text == "Кол-во баллов")
async def go_back(message: Message):
    user_id = message.from_user.id
    await message.answer(f"{user_points[user_id] if user_points[user_id] is not None else 0}")


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


async def schedule_transfer_option():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    for i in range(14, 17):
        scheduler.add_job(make_contribute_available, trigger='cron', hour=i, minute=0)
        scheduler.add_job(delete_message, trigger='cron', hour=i, minute=9)
        scheduler.add_job(make_withdraw_available, trigger='cron', hour=i, minute=50)
        scheduler.add_job(delete_message, trigger='cron', hour=i, minute=59)
    scheduler.start()


# @util_user_router.message(Command("dice_deposit"))
async def roll_user_deposit(message: Message):
    print("dice_deposit")
    user_id = message.from_user.id
    if user_id in user_points.keys():

        dice = await bot.send_dice(user_id)
        value_dice = dice.dice.value
        await sleep(4)

        if value_dice > 3:
            user_points[user_id] *= 2
            await message.answer("Количество баллов на вкладе удвоилось!")
        else:
            user_points[user_id] /= 2
            await message.answer("Количество баллов на вкладе уменьшилось(")


async def make_contribute_available():
    for user_id in user_contributions:
        if user_contributions[user_id] > 0:
            try:
                message = await bot.send_message(chat_id=user_id, text="Положи на вклад", reply_markup=contribute_keyboard())
                message_ids_to_delete[user_id] = message.message_id
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")


@util_user_router.callback_query(F.data == "contribute")
async def handle_contribute(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    points = user_points.get(user_id, 0)

    if points > 0:
        await callback.message.answer(f"У вас столько баллов {points}\nСколько хотите внести?")
        await state.set_state(ContributeState.waiting_for_contribution)
    else:
        await callback.message.answer(f"У вас {points} баллов(")

    await callback.answer()


@util_user_router.message(ContributeState.waiting_for_contribution)
async def handle_contribution(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contribution_amount = int(message.text)
    points = user_points.get(user_id, 0)

    if user_contributions.get(user_id) is None:
        user_contributions[user_id] = 0

    if contribution_amount > points or contribution_amount <= 0:
        await message.answer(f"...")
    else:
        user_points[user_id] -= contribution_amount
        user_contributions[user_id] += contribution_amount
        await message.answer(f"Положили баллов: {contribution_amount}", reply_markup=withdraw_keyboard())

    await roll_user_deposit(message)
    await state.clear()


async def make_withdraw_available():
    for user_id in user_contributions:
        if user_contributions[user_id] > 0:
            message = await bot.send_message(chat_id=user_id, text="Время пришло! Ты можешь снять баллы со счета.",
                                             reply_markup=contribute_keyboard())
            message_ids_to_delete[user_id] = message.message_id


@util_user_router.callback_query(F.data == "withdraw")
async def handle_withdraw(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    contribution_amount = user_contributions.get(user_id, 0)

    if contribution_amount > 0:
        await callback.message.answer(f"Баллов на вкладе: {contribution_amount}. Сколько хотите вывести?")
        await state.set_state(ContributeState.waiting_for_withdrawal)
    else:
        await callback.message.answer("У вас недостаточно баллов на вкладе(")

    await callback.answer()


@util_user_router.message(ContributeState.waiting_for_withdrawal)
async def handle_withdrawal(message: Message, state: FSMContext):
    user_id = message.from_user.id
    withdrawal_amount = int(message.text)
    contribution_amount = user_contributions.get(user_id, 0)

    if user_contributions.get(user_id) is None:
        user_contributions[user_id] = 0

    if withdrawal_amount > contribution_amount or withdrawal_amount <= 0:
        await message.answer(f"...")
    else:
        user_points[user_id] += withdrawal_amount
        user_contributions[user_id] -= withdrawal_amount
        await message.answer(f"Вывод произошёл успешно. Осталось на вкладе: {user_contributions[user_id]}")

    await state.clear()


async def delete_message():
    for user_id, message_id in message_ids_to_delete.items():
        try:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
        except Exception as e:
            print(f"Failed to delete message for user {user_id}: {e}")
