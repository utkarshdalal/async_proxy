import aiohttp
from aiohttp import web
import socket
from datetime import datetime, timedelta


class AsyncProxy(object):
    def __init__(self):
        self.bytes_received = 0
        self.bytes_sent = 0
        self.start_time = datetime.now()

    async def handle(self, request):
        url = request.query.get('url')
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET)) as session:
            async with session.get(url) as resp:
                text = await resp.text()
                # return BeautifulSoup(text, 'html.parser')
                return web.Response(text=text, content_type='text/html')

    async def get_stats(self, request):
        text = f'Total bytes transferred: {self.bytes_received} <br> Total time up: {datetime.now() - self.start_time}'
        return web.Response(text=text, content_type='text/html')



app = web.Application()
async_proxy = AsyncProxy()
app.add_routes([web.get('/', async_proxy.handle), web.get('/stats', async_proxy.get_stats)])

if __name__ == '__main__':
    web.run_app(app)
