# hello_world.py
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.httpclient import AsyncHTTPClient


class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient()
        url = 'http://httpbin.org/delay/3'
        response = yield http_client.fetch(url)
        self.write(response.body)


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
