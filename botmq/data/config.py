from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str('BOT_TOKEN')
ADMIN_IDS: list = []
ADMIN_IDS = env.str('ADMIN_IDS', '').split(', ') if env.str('ADMIN_IDS', '') else []
SERVER_ADDRESS: str = env.str('SERVER_ADDRESS')
SERVER_PORT: int = env.int('SERVER_PORT')
SERVER_TIMEOUT: int = env.int('SERVER_TIMEOUT')

POSTGRES_HOST: str = env.str("POSTGRES_HOST")
POSTGRES_PORT: int = env.int("POSTGRES_PORT")
POSTGRES_USER: str = env.str("POSTGRES_USER")
POSTGRES_PASSWORD: str = env.str("POSTGRES_PASSWORD")
POSTGRES_DB: str = env.str("POSTGRES_DB")