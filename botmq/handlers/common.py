import logging

from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.types import Message 

from botmq.loader import dp
from botmq.utility.commands import register_command

@register_command(BotCommand(command='/start', description='Start message'))
@dp.message(Command('start'))
async def cmd_start(message: Message) -> None:
    logging.info('/start')
    await message.answer('Hello! Check the commands menu to start using bot.')