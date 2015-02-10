import json
import tornado.gen
from tornado.httpclient import AsyncHTTPClient

# Model layer example
class Feed:
    @classmethod
    @tornado.gen.coroutine
    def fetch(cls):
        http_client = AsyncHTTPClient()
        url = 'http://httpbin.org/delay/1'
        response = yield http_client.fetch(url)
        body = response.body.decode('utf-8')
        return json.loads(body)
