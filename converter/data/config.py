from environs import Env

env = Env()
env.read_env()

SERVER_PORT: int = env.int('SERVER_PORT')

MQTT_ADDRESS: str = env.str('MQTT_ADDRESS')
MQTT_PORT: int = env.int('MQTT_PORT')
MQTT_USERNAME: str = env.str('MQTT_USERNAME')
MQTT_PASSWORD: str = env.str('MQTT_PASSWORD')
MQTT_TOPICS: list = env.str('MQTT_TOPICS').split(', ')