import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, BotCommand, InaccessibleMessage
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Filter, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from converter.requests import get_value_async

from botmq.data.config import SERVER_ADDRESS, SERVER_PORT
from botmq.polling import LIMIT_NAMES
from botmq.loader import dp, router, data_base
from botmq.utility.format import format_to_title_case
from botmq.utility.db import set_limit, list_limits, set_rename, list_renames, get_topic_name
from botmq.utility.commands import register_command

class FloatFilter(Filter):
    def __init__(self) -> None:
        pass
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        try:
            float(message.text)
            return True
        except ValueError:
            return False

class SetLimits(StatesGroup):
    choosing_topic = State()
    choosing_limit = State()
    choosing_value = State()

class SetRenames(StatesGroup):
    choosing_topic = State()
    choosing_name = State()

@register_command(BotCommand(command='/password', description='Enter topic password'))
@dp.message(Command('password'))
async def cmd_password(message: Message, command: CommandObject) -> None:
    logging.info('/password')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    if command.args is None:
        await message.answer(
                "Usage: /password <password>"
                )
        return
    try:
        password = command.args
    except ValueError:
        await message.answer(
                "Usage: /password <password>"
                )
        return
    try:
        result_message = data_base.add_user(message.from_user.id, password)
    except Exception as e:
        data_base.rollback() 
        result_message = f'{e}'
    await message.answer(f'{result_message}')

@register_command(BotCommand(command='/report', description='Show all your topics'))
@dp.message(Command('report'))
async def cmd_report(message: Message) -> None:
    logging.info('/report')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    result_message = ''
    user_groups = data_base.get_group(message.from_user.id)
    if not user_groups:
        await message.answer("You don't have topics")
        return
    logging.info(f'User {message.from_user.id} groups: {user_groups}')
    for topic in user_groups:
        value = await get_value_async(SERVER_ADDRESS, SERVER_PORT, topic)
        value = str(value).strip()
        result_message += f'{get_topic_name(message.from_user.id, topic)}: {value}\n' 
    await message.answer(f'{result_message}')
    logging.info('Message sent')

@register_command(BotCommand(command='/check', description='Check value of the topic'))
@dp.message(Command('check'))
async def cmd_check(message: Message) -> None:
    logging.info('/check')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    user_groups = data_base.get_group(message.from_user.id)
    if not user_groups:
        await message.answer("You don't have topics")
        return
    logging.info(f'User {message.from_user.id} groups: {user_groups}')
    keyboard = InlineKeyboardBuilder()
    for topic in user_groups:
        keyboard.row(InlineKeyboardButton(
            text=get_topic_name(message.from_user.id, topic),
            callback_data=f'check-topic_{topic}'),
            width=1
        )
    await message.answer(
        'Select a topic',
        reply_markup=keyboard.as_markup()
    )
    logging.info('Message sent')

@dp.callback_query(F.data.startswith('check-topic_'))
async def get_topic_value(callback: CallbackQuery) -> None:
    if not callback.data:
        result_message = 'Callback data is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    if not callback.message or isinstance(callback.message, InaccessibleMessage):
        result_message = 'Callback message is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    topic = callback.data.split('_', 1)[1]
    value = await get_value_async(SERVER_ADDRESS, SERVER_PORT, topic)
    await callback.message.edit_text(f'Value of {get_topic_name(callback.from_user.id, topic)} topic: {value}')
    await callback.answer()

@register_command(BotCommand(command='/list_limits', description='Show your limits'))
@router.message(Command('list_limits'))
async def cmd_list_limits(message: Message) -> None:
    logging.info('/list_limits')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    limits = list_limits(message.from_user.id)
    if limits is None:
        await message.answer("You don't have limits")
        return
    result_message = ''
    for topic in limits:
        result_message += f'{get_topic_name(message.from_user.id, topic)}\n'
        for limit in limits[topic]:
            result_message += f'\t{format_to_title_case(limit)}: {limits[topic][limit]}\n'
    await message.answer(result_message)
    logging.info('Message sent')

@register_command(BotCommand(command='/limit', description='Set limit for the topic'))
@router.message(Command('limit'))
async def set_limits_cmd_limit(message: Message, state: FSMContext) -> None:
    logging.info('/limit')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    user_groups = data_base.get_group(message.from_user.id)
    logging.info(f'User {message.from_user.id} groups: {user_groups}')
    if not user_groups:
        await message.answer("You don't have topics")
        return
    keyboard = InlineKeyboardBuilder()
    for topic in user_groups:
        keyboard.row(InlineKeyboardButton(
            text=get_topic_name(message.from_user.id, topic),
            callback_data=f'limit-topic_{topic}'),
            width=1
        )
    await message.answer(
        'Select a topic',
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(SetLimits.choosing_topic)
    logging.info('Message sent')

@router.callback_query(SetLimits.choosing_topic, F.data.startswith('limit-topic_'))
async def set_limits_choosing_topic(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        result_message = 'Callback data is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    if not callback.message or isinstance(callback.message, InaccessibleMessage):
        result_message = 'Callback message is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    topic = callback.data.split('_', 1)[1]
    await state.update_data(SetLimits_chosen_topic=topic)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Lower Limit", callback_data=f'limit-limitname_{LIMIT_NAMES[0]}'),
        InlineKeyboardButton(text="Upper Limit", callback_data=f'limit-limitname_{LIMIT_NAMES[1]}'),
        InlineKeyboardButton(text="Lower Panic", callback_data=f'limit-limitname_{LIMIT_NAMES[2]}'),
        InlineKeyboardButton(text="Upper Panic", callback_data=f'limit-limitname_{LIMIT_NAMES[3]}'),
        width=2
    )
    await callback.message.edit_text(
        'Select a limit:',
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(SetLimits.choosing_limit)
    logging.info('Message sent')

@router.callback_query(SetLimits.choosing_limit, F.data.startswith('limit-limitname_'))
async def set_limits_choosing_limit(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        result_message = 'Callback data is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    if not callback.message or isinstance(callback.message, InaccessibleMessage):
        result_message = 'Callback message is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    limit_type = callback.data.split('_', 1)[1]
    await state.update_data(SetLimits_chosen_limit=limit_type)
    user_data = await state.get_data()
    topic = user_data['SetLimits_chosen_topic']
    await callback.message.edit_text(
        text=f'Set a value of {format_to_title_case(limit_type)} for the {get_topic_name(callback.from_user.id, topic)} topic:', 
    )
    await state.set_state(SetLimits.choosing_value)
    logging.info('Message sent')

@router.message(SetLimits.choosing_value, FloatFilter())
async def set_limits_choosing_value(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    user_data = await state.get_data()
    topic = user_data['SetLimits_chosen_topic']
    limit = user_data['SetLimits_chosen_limit']
    set_limit(message.from_user.id, topic, limit, message.text)
    await message.answer('Limit set')
    await state.clear()
    logging.info('Message sent')

@register_command(BotCommand(command='/list_renames', description='Show your renames'))
@router.message(Command('list_renames'))
async def cmd_list_renames(message: Message) -> None:
    logging.info('/list_renames')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    renames = list_renames(message.from_user.id)
    if renames is None:
        await message.answer("You don't have renames")
        return
    result_message = ''
    for topic in renames:
        result_message += f'{topic} -> {renames[topic]}\n'
    await message.answer(result_message)
    logging.info('Message sent')

@register_command(BotCommand(command='/rename', description='Rename the topic'))
@router.message(Command('rename'))
async def set_renames_cmd_rename(message: Message, state: FSMContext) -> None:
    logging.info('/rename')
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    user_groups = data_base.get_group(message.from_user.id)
    logging.info(f'User {message.from_user.id} groups: {user_groups}')
    if not user_groups:
        await message.answer("You don't have topics")
        return
    keyboard = InlineKeyboardBuilder()
    for topic in user_groups:
        keyboard.row(InlineKeyboardButton(
            text=get_topic_name(message.from_user.id, topic),
            callback_data=f'rename-topic_{topic}',
            width=1)
        )
    await message.answer(
        'Select a topic',
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(SetRenames.choosing_topic)
    logging.info('Message sent')

@router.callback_query(SetRenames.choosing_topic, F.data.startswith('rename-topic_'))
async def set_renames_choosing_topic(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        result_message = 'Callback data is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    if not callback.message or isinstance(callback.message, InaccessibleMessage):
        result_message = 'Callback message is missing'
        logging.error(result_message)
        await callback.answer(result_message)
        return
    topic = callback.data.split('_', 1)[1]
    await state.update_data(SetRenames_chosen_topic=topic)
    await callback.message.edit_text(
        text=f'Set a name of the {get_topic_name(callback.from_user.id, topic)} topic:', 
    )
    await state.set_state(SetRenames.choosing_name)
    logging.info('Message sent')

@router.message(SetRenames.choosing_name)
async def set_renames_choosing_name(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        result_message = 'User ID is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    if not message.text:
        result_message = 'Message text is missing'
        logging.error(result_message)
        await message.answer(result_message)
        return
    user_data = await state.get_data()
    topic = user_data['SetRenames_chosen_topic']
    set_rename(message.from_user.id, topic, message.text)
    await message.answer('Rename set')
    await state.clear()
    logging.info('Message sent')