from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message

from utils.task_template import task_media_template, task_text_template
from strings import *


task_router = Router()


@task_router.message(F.text == stories.get("task1_short"))
async def task_1(message: Message):
    await message.answer(task_text_template(stories.get("task1_desc")))


@task_router.message(F.text == stories.get("task2_short"))
async def task_2(message: Message):
    await message.answer(task_media_template(stories.get("task2_desc")))


@task_router.message(F.text == stories.get("task3_short"))
async def task_3(message: Message):
    await message.answer(task_text_template(stories.get("task3_desc")))
