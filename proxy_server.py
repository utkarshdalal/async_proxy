from aiohttp import web, ClientSession, TCPConnector
import socket
from datetime import datetime


def add_via_header(headers):
    via_header = headers.get('Via', None)
    headers['Via'] = via_header + ', 1.1 asyncproxy' if via_header else '1.1 asyncproxy'
    return headers


def validate_range(range_header, range_param):
    if (range_header and range_param) and (range_header != range_param):
        return False
    return True


# Remove Connection header and all headers with underlying connection-tokens as per section 8.1.3 of RFC2616 spec
# Add Via header as per section 14.45 of RFC2616 spec
def format_request_headers(headers):
    if 'Connection' in headers:
        for connection_token in headers.get('Connection', []):
            headers.pop(connection_token, None)
        headers.pop('Connection', None)
    headers = add_via_header(headers)
    return headers


class AsyncProxy(object):
    def __init__(self):
        self.bytes_received = 0
        self.start_time = datetime.now()

    async def handle(self, request):
        url = request.query.get('url')
        range_header = request.headers.get('Range', None)
        range_param = request.query.get('range', None)
        headers = format_request_headers(request.headers.copy())

        if not validate_range(range_header, range_param):
            return web.Response(text='Range header and query parameter are inconsistent', content_type='text/html',
                                status=416)

        if range_param:
            headers['Range'] = range_param

        print(request.headers)
        # print(headers)
        async with ClientSession(headers=headers, connector=TCPConnector(family=socket.AF_INET)) as session:
            async with session.get(url) as resp:
                num_bytes = resp.content._size
                self.bytes_received += int(num_bytes)
                text = await resp.text()
                response_headers = resp.headers.copy()
                response_headers = add_via_header(response_headers)
                # print(response_headers)
                # print(resp.status)
                # print(text)
                return web.Response(text=text, headers=response_headers, status=resp.status)

    async def get_stats(self, request):
        text = f'Total bytes transferred: {self.bytes_received} <br> Total time up: {datetime.now() - self.start_time}'
        return web.Response(text=text, content_type='text/html', status=200)


def create_app():
    app = web.Application()
    async_proxy = AsyncProxy()
    app.add_routes([web.get('/', async_proxy.handle), web.get('/stats', async_proxy.get_stats)])
    return app


async_proxy_app = create_app()
print("Running...")
web.run_app(async_proxy_app)
