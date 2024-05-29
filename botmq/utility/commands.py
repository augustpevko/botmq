import logging

from aiogram.types import BotCommand

from botmq.loader import bot

bot_commands: list[BotCommand] = []

def register_command(command: BotCommand):
    if command not in bot_commands:
        bot_commands.append(command)

    def decorator(func):
        async def wrapper(message, *args, **kwargs):
            await func(message, *args, **kwargs)
        return wrapper
    return decorator

async def set_default_commands() -> bool:
    result = await bot.set_my_commands(bot_commands)
    if result:
        logging.info('Default commands is set')
    else:
        logging.error('Default commands is not set')
    return result
