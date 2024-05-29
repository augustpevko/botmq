import asyncio
import logging

from converter.requests import list_topics_async, get_value_async 

from .utility.format import format_to_title_case
from .utility.db import get_topic_name
from .data.config import ADMIN_IDS, SERVER_ADDRESS, SERVER_PORT
from .loader import data_base, bot

async def exceed_limit_default(limit_name: str, limit_value: str, current_value: str, topic: str, user_id) -> None:
    #TODO Customize each case 
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    
    result = await bot.send_message(user_id, f'The {get_topic_name(user_id, topic)} topic has exceeded its {format_to_title_case(limit_name)} limit of {limit_value} with a current value of {current_value}.')
    finish_time = loop.time()
    duration = (finish_time - start_time) * 1000
    logging.info(f'The {topic} topic has exceeded its {limit_name} limit of {limit_value} with a current value of {current_value}.')
    logging.info('User id: %d. Duration: %dms' % (user_id, duration))

LIMITS = {
    'lower_limit': exceed_limit_default,
    'upper_limit': exceed_limit_default,
    'lower_panic': exceed_limit_default,
    'upper_panic': exceed_limit_default,
}

LIMIT_NAMES = list(LIMITS.keys())

async def check_limits() -> None:
    logging.info('Check limits')
    user_ids = data_base.list_users()
    for user_id in user_ids:
        user_config = data_base.get_config(user_id)
        if user_config is None:
            continue
        limit_config = user_config.get('limits', None)
        if limit_config is None:
            continue
        for topic, limits in limit_config.items():
            try:
                current_value = await get_value_async(SERVER_ADDRESS, SERVER_PORT, topic)
                current_value_float = float(current_value)
            except (ValueError, TypeError):
                logging.error(f"Error: Current value for topic {topic} is not convertible to float")
                continue
            for limit_name, limit_value in limits.items():
                if (limit_name.startswith('lower') and float(limit_value) > current_value_float) or \
                   (limit_name.startswith('upper') and float(limit_value) < current_value_float):
                        callback = LIMITS.get(limit_name, exceed_limit_default)
                        await callback(limit_name, limit_value, current_value, topic, user_id)

async def server_polling(host, port, generator, timeout) -> None:
    logging.info('Start polling')
    while True:
        try:
            topics = await list_topics_async(host, port)
            topics_list: list[str] = []
            if topics:
                topics_list = topics.split(',')
            groups_list = data_base.list_groups()
            topics_list = [x for x in topics_list if x not in groups_list]
            logging.info(f'topics list: {topics_list}')
            for topic in topics_list:
                password = generator()
                data_base.add_group(topic, password)
                password_info = f'Password for {topic} groups is: {password}'
                logging.info(password_info)
                for id in ADMIN_IDS:
                    await bot.send_message(id, password_info)
        except Exception as e:
            logging.error(f'Error adding topics to database: {e}') 
        try:
            await check_limits()
        except Exception as e:
            logging.error(f'Error checking limits: {e}') 
        await asyncio.sleep(timeout)