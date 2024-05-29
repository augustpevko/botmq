import asyncio
import logging
logging.basicConfig(level=logging.INFO)

from .utility.generator import generate_password
from .utility.commands import set_default_commands

from .polling import server_polling
from .data import config 
from .loader import data_base, bot, dp, router

async def on_startup():
    logging.info('Bot started')

    for id in config.ADMIN_IDS:
        await bot.send_message(id, 'Bot is started')
    import botmq.handlers
    await set_default_commands()

async def main():
    logging.info('Called main')
    
    dp.include_router(router)
    dp.startup.register(on_startup)
    server_task = asyncio.create_task(server_polling(config.SERVER_ADDRESS, 
                                                     config.SERVER_PORT, 
                                                     generate_password, 
                                                     config.SERVER_TIMEOUT))
    try:
        await dp.start_polling(bot, handle_signals=False)
        await server_task
    except KeyboardInterrupt as e:
        await dp.stop_polling()

if __name__ == "__main__":
    asyncio.run(main())
