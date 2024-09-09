from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()')


@router.message(Command('start2'))
async def cmd_start2(message: Message):
    await message.answer('Запуск сообщения по команде /start_2 используя фильтр Command()')


@router.message(F.text == '/start3')
async def cmd_start3(message: Message):
    await message.answer('Запуск сообщения по команде /start_3 используя магический фильтр F.text!')
