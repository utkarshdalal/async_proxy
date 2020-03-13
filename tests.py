from multidict import CIMultiDict

from proxy_server import AsyncProxy
import pytest
from aiohttp import web
from freezegun import freeze_time
from unittest.mock import MagicMock, ANY


@pytest.fixture
def cli(loop, aiohttp_client, freezer):
    with freeze_time('2020-02-01 00:00:00'):
        app = web.Application()
        async_proxy = AsyncProxy()
        app.router.add_get('/', async_proxy.handle)
        app.router.add_get('/stats', async_proxy.get_stats)
        return loop.run_until_complete(aiohttp_client(app))


@pytest.mark.freeze_time
async def test_get_stats(cli, freezer, mocker):
    with freeze_time('2020-02-02 01:00:00'):
        mocker.patch('aiohttp.ClientSession.get',
                     return_value=MockResponse(mock_text_response, mock_headers, mock_status))
        await cli.get('/?url=http://www.google.com')
        await cli.get('/?url=http://www.facebook.com')
        resp = await cli.get('/stats')
        assert resp.status == 200
        assert await resp.text() == 'Total bytes transferred: 3118 <br> Total time up: 1 day, 1:00:00'


@pytest.mark.asyncio
async def test_headers(cli, mocker):
    mocked_session = mocker.patch('aiohttp.ClientSession.__init__', return_value=None)
    await cli.get('/?url=http://www.google.com',
                  headers={'Hi': 'Hey', 'Connection': 'keep-alive, die', 'keep-alive': 'yes', 'die': 'no'})
    expected_headers = CIMultiDict()
    expected_headers['Hi'] = 'Hey'
    expected_headers['Accept'] = '*/*'
    expected_headers['Accept-Encoding'] = 'gzip, deflate'
    expected_headers['User-Agent'] = 'Python/3.8 aiohttp/3.6.2'
    expected_headers['Via'] = '1.1 asyncproxy'
    mocked_session.assert_called_with(connector=ANY, headers=expected_headers)


@pytest.mark.asyncio
async def test_get(cli, mocker):
    mocker.patch('aiohttp.ClientSession.get', return_value=MockResponse(mock_text_response, mock_headers, mock_status))
    resp = await cli.get('/?url=http://www.google.com',
                         headers={'Hi': 'Hey', 'Connection': 'keep-alive', 'keep-alive': 'yes'})
    assert await resp.text() == mock_text_response
    assert resp.status == mock_status
    assert resp.headers['Content-Type'] == 'text/html; charset=UTF-8'
    assert resp.headers['Referrer-Policy'] == 'no-referrer'
    assert resp.headers['Content-Length'] == '1561'
    assert resp.headers['Date'] == 'Thu, 12 Mar 2020 11:59:02 GMT'
    assert resp.headers['Via'] == '1.1 asyncproxy'
    assert resp.headers['Server'] == 'Python/3.8 aiohttp/3.6.2'
    assert len(resp.headers) == 6


@pytest.mark.asyncio
async def test_range_1(cli):
    resp = await cli.get('/?url=http://www.google.com&range=bytes:0-999', headers={'Range': 'bytes:0-666'})
    assert await resp.text() == 'Range header and query parameter are inconsistent'
    assert resp.status == 416


@pytest.mark.asyncio
async def test_range_2(cli, mocker):
    mocked_session = mocker.patch('aiohttp.ClientSession.__init__', return_value=None)
    await cli.get('/?url=http://www.google.com&range=bytes:0-999',
                  headers={'Hi': 'Hey', 'Connection': 'keep-alive, die', 'keep-alive': 'yes'})
    expected_headers = CIMultiDict()
    expected_headers['Hi'] = 'Hey'
    expected_headers['Accept'] = '*/*'
    expected_headers['Accept-Encoding'] = 'gzip, deflate'
    expected_headers['User-Agent'] = 'Python/3.8 aiohttp/3.6.2'
    expected_headers['Via'] = '1.1 asyncproxy'
    expected_headers['Range'] = 'bytes:0-999'
    mocked_session.assert_called_with(connector=ANY, headers=expected_headers)


@pytest.mark.asyncio
async def test_range_3(cli, mocker):
    mocked_session = mocker.patch('aiohttp.ClientSession.__init__', return_value=None)
    await cli.get('/?url=http://www.google.com',
                  headers={'Hi': 'Hey', 'Connection': 'keep-alive, die', 'keep-alive': 'yes', 'Range': 'bytes:0-666'})
    expected_headers = CIMultiDict()
    expected_headers['Hi'] = 'Hey'
    expected_headers['Range'] = 'bytes:0-666'
    expected_headers['Accept'] = '*/*'
    expected_headers['Accept-Encoding'] = 'gzip, deflate'
    expected_headers['User-Agent'] = 'Python/3.8 aiohttp/3.6.2'
    expected_headers['Via'] = '1.1 asyncproxy'
    mocked_session.assert_called_with(connector=ANY, headers=expected_headers)


mock_text_response = """<!DOCTYPE html>
<html lang=en>
  <meta charset=utf-8>
  <meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">
  <title>Error 404 (Not Found)!!1</title>
  <style>
    *{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body
    {margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > 
    body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}
    p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and 
    (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo
    {background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) 
    no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url
    (//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;
    -moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}
    @media only screen and (-webkit-min-device-pixel-ratio:2)
    {#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 
    no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}
  </style>
  <a href=//www.google.com/><span id=logo aria-label=Google></span></a>
  <p><b>404.</b> <ins>That’s an error.</ins>
  <p>The requested URL <code>/</code> was not f"""

mock_headers = {'Content-Type': 'text/html; charset=UTF-8', 'Referrer-Policy': 'no-referrer',
                'Content-Length': 'irrelevant number',
                'Date': 'Thu, 12 Mar 2020 11:59:02 GMT', 'Content-Encoding': 'xyz', 'Transfer-Encoding': 'chunked'}

mock_status = 200


class MockResponse:
    def __init__(self, text, headers, status):
        self._text = text
        self.status = status
        self.headers = headers
        size = len(text)
        content = MagicMock()
        content._size = size
        self.content = content

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class MockSession:
    def __init__(self, text, headers, status):
        self.get_response = MockResponse(text, headers, status)

    async def get(self, url):
        return self.get_response
