from aiogram.types import BotCommand, BotCommandScopeDefault
from main import bot


async def set_commands():
    commands = [BotCommand(command='help', description='Помощь по командам'),
                BotCommand(command='points', description='Количество баллов')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
