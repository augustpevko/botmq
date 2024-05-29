from aiogram import Bot, Dispatcher, Router

from .data import config
from .db.context import Context
from .db.postgresql import PostgreSQL

db_settings = {
    'host': config.POSTGRES_HOST,
    'port': config.POSTGRES_PORT,
    'user': config.POSTGRES_USER,
    'password': config.POSTGRES_PASSWORD,
    'database': config.POSTGRES_DB,
}
data_base = Context(PostgreSQL(db_settings))
data_base.create_table()

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
router = Router()