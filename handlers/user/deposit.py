from asyncio import sleep
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from main import bot
from keyboards.kasino import contribute_keyboard, withdraw_keyboard
from db.store import *

deposit_router = Router()


class ContributeState(StatesGroup):
    waiting_for_contribution = State()
    waiting_for_withdrawal = State()


async def schedule_transfer_option():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    for i in range(7, 17):
        # scheduler.add_job(make_contribute_available, trigger='cron', hour=i, minute=55)
        scheduler.add_job(delete_message, trigger='cron', hour=i, minute=56)
        # scheduler.add_job(make_withdraw_available, trigger='cron', hour=i, minute=57)
        scheduler.add_job(delete_message, trigger='cron', hour=i, minute=58)
    scheduler.start()


@deposit_router.message(Command("test"))
async def make_contribute_available(message: Message):
    user_contributions = await get_all_users()
    for user_id in user_contributions:
        u_d = user_id['user_id']
        try:
            message = await bot.send_message(chat_id=u_d, text="Положи на вклад баллы", reply_markup=contribute_keyboard())
            message_ids_to_delete[u_d] = message.message_id
        except Exception as e:
            print(f"Failed to send message to user {u_d}: {e}")


@deposit_router.callback_query(F.data == "contribute")
async def handle_callback_contribute(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_info = await get_user_info(user_id)
    points = user_info['points']

    if points > 0:
        await callback.message.answer(f"У вас столько баллов: {points}\nСколько хотите внести?")
        await state.set_state(ContributeState.waiting_for_contribution)
    else:
        await callback.message.answer(f"У вас не хватает баллов(")

    await callback.answer()


@deposit_router.message(ContributeState.waiting_for_contribution)
async def handle_contribution(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contribution_amount = int(message.text)
    user_info = await get_user_info(user_id)
    points = user_info['points']
    deposit = user_info['deposit']

    if contribution_amount > points or contribution_amount <= 0:
        await message.answer(f"...")
    else:
        await update_user_points(user_id, points - contribution_amount)
        await update_user_deposit(user_id, deposit + contribution_amount)
        await message.answer(f"Положили баллов: {contribution_amount}\n"
                             f"Посмотреть количество баллов можете по кнопке 'Кол-во баллов на вкладе'")

    await state.clear()


async def roll_user_deposit(user_id):
    user_contributions = await get_user_info(user_id)

    u_d = user_contributions['user_id']
    user_info = await get_user_info(u_d)
    deposit = user_info['deposit']

    dice = await bot.send_dice(u_d)
    value_dice = dice.dice.value
    await sleep(5)

    if value_dice > 3:
        await update_user_deposit(u_d, deposit*2)
        await bot.send_message(chat_id=u_d, text="Количество баллов на вкладе удвоилось!")
    else:
        await update_user_deposit(u_d, 0)
        await bot.send_message(chat_id=u_d, text="Ставка не удалась(")


@deposit_router.message(Command("test3"))
async def make_withdraw_available(message: Message):
    user_contributions = await get_all_users()
    for user_id in user_contributions:
        u_d = user_id['user_id']
        if user_id['deposit'] > 0:
            await roll_user_deposit(u_d)
            await sleep(10)

            user_info = await get_user_info(u_d)
            deposit = user_info['deposit']
            # contribution_amount = user_contributions.get(u_d, 0)

            if deposit > 0:
                message = await bot.send_message(chat_id=u_d, text="Время пришло! Вы можете снять баллы со счета.",
                                                 reply_markup=withdraw_keyboard())
                message_ids_to_delete[u_d] = message.message_id
            else:
                await bot.send_message(chat_id=u_d, text="Баллы сгорели(")


@deposit_router.callback_query(F.data == "withdraw")
async def handle_withdraw(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_info = await get_user_info(user_id)
    deposit = user_info['deposit']

    await callback.message.answer(f"Баллов на вкладе: {deposit}. Сколько хотите вывести?")
    await state.set_state(ContributeState.waiting_for_withdrawal)
    # else:
    #     await callback.message.answer("У вас недостаточно баллов на вкладе(")

    await callback.answer()


@deposit_router.message(ContributeState.waiting_for_withdrawal)
async def handle_withdrawal(message: Message, state: FSMContext):
    user_id = message.from_user.id
    withdrawal_amount = int(message.text)
    user_info = await get_user_info(user_id)
    points = user_info['points']
    deposit = user_info['deposit']

    if withdrawal_amount > deposit or withdrawal_amount <= 0:
        await message.answer(f"...")
    else:
        await update_user_points(user_id, points + withdrawal_amount)
        await update_user_deposit(user_id, deposit - withdrawal_amount)
        await message.answer(f"Вывод произошёл успешно. Осталось на вкладе: {user_info['deposit']}")

    await state.clear()


async def delete_message():
    for user_id, message_id in message_ids_to_delete.items():
        try:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
        except Exception as e:
            print(f"Failed to delete message for user {user_id}: {e}")
