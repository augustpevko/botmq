import requests
import aiohttp

def list_topics(host, port):
    return requests.get(f'http://{host}:{port}/list_topics').text

def get_value(host, port, topic):
    return requests.get(f'http://{host}:{port}/get_value?topic={topic}').text

async def list_topics_async(host, port):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f'http://{host}:{port}/list_topics')
        return await response.text()

async def get_value_async(host, port, topic):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f'http://{host}:{port}/get_value?topic={topic}')
        return await response.text()
