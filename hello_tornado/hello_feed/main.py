# hello_feed/main.py
import tornado.ioloop
import tornado.web
from .core.handlers import FeedHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", FeedHandler),
        ]
        settings = {'debug': True}
        super().__init__(handlers, **settings)


if __name__ == "__main__":
    application = Application() 
    application.listen(8888)

    # This is like "while True:" with callbacks
    # for READ, WRITE and ERROR
    tornado.ioloop.IOLoop.instance().start()
