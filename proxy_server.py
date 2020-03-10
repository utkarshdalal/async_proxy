from aiohttp import web, ClientSession
from datetime import datetime


class AsyncProxy(object):
    def __init__(self):
        self.bytes_received = 0
        self.bytes_sent = 0
        self.start_time = datetime.now()

    async def handle(self, request):
        url = request.query.get('url')
        range_header = request.headers.get('Range', None)
        range_param = request.query.get('range', None)
        headers = self.format_request_headers(request.headers.copy())

        if not self.validate_range(range_header, range_param):
            return web.Response(text='Range header and query parameter are inconsistent', content_type='text/html',
                                status=416)

        if range_param:
            headers['Range'] = range_param

        print(request.headers)
        print(headers)
        async with ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                text = await resp.text()
                print(resp.headers)
                print(resp.status)
                return web.Response(text=text, headers=resp.headers, status=resp.status)

    async def get_stats(self, request):
        text = f'Total bytes transferred: {self.bytes_received} <br> Total time up: {datetime.now() - self.start_time}'
        return web.Response(text=text, content_type='text/html', status=200)

    def format_request_headers(self, headers):
        if 'Connection' in headers:
            for connection_token in headers['Connection']:
                headers.pop(connection_token, None)
            headers.pop('Connection', None)
        return headers

    def validate_range(self, range_header, range_param):
        if (range_header and range_param) and (range_header != range_param):
            return False
        return True


app = web.Application()
async_proxy = AsyncProxy()
app.add_routes([web.get('/', async_proxy.handle), web.get('/stats', async_proxy.get_stats)])

if __name__ == '__main__':
    web.run_app(app)
