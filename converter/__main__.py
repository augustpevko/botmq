import asyncio
import logging
from aiohttp import web

from .data import config
from .convertible.mqtt import Mqtt

logging.basicConfig(level=logging.INFO)

class HttpConverter:
    def __init__(self, host, port, client):
        self.host = host
        self.port = port
        # So we can pass any client not only mqtt
        self.client = client

    async def handle_list_topics(self, request):
        # Handles /list_topics
        return web.Response(text=','.join(self.client.list_topics()))

    async def handle_get_value(self, request):
        # Handles /get_value?topic=<topic>
        topic = request.query.get('topic', None)
        if topic in self.client.list_topics():
            return web.Response(text=self.client.get_value(topic))
        else:
            return web.Response(text=f'Topic "{topic}" not found', status=404)

    async def run(self):
        # Client loop
        self.client.run()
        # Server init
        app = web.Application() 
        app.router.add_get('/list_topics', self.handle_list_topics)
        app.router.add_get('/get_value', self.handle_get_value)
        await web._run_app(app, host=self.host, port=self.port)

async def main():
    server = HttpConverter('0.0.0.0', config.SERVER_PORT, Mqtt(config.MQTT_ADDRESS, 
                                                               config.MQTT_PORT, 
                                                               config.MQTT_USERNAME, 
                                                               config.MQTT_PASSWORD, 
                                                               config.MQTT_TOPICS))
    await server.run()

if __name__ == '__main__':
    asyncio.run(main())