# hello_asyncio_multi.py
import asyncio
import tornado.ioloop
import tornado.httpserver
import tornado.web
import tornado.gen
from tornado.httpclient import AsyncHTTPClient

try:
    import aioredis
except ImportError:
    print("Please install aioredis: pip install aioredis")
    exit(0)

class AsyncRequestHandler(tornado.web.RequestHandler):
    """Base class for request handlers with `asyncio` coroutines support.
    It runs methods on Tornado's ``AsyncIOMainLoop`` instance.

    Subclasses have to implement one of `get_async()`, `post_async()`, etc.
    Asynchronous method should be decorated with `@asyncio.coroutine`.

    Usage example::

        class MyAsyncRequestHandler(AsyncRequestHandler):
            @asyncio.coroutine
            def get_async(self):
                html = yield from self.application.http.get('http://python.org')
                self.write({'html': html})

    You may also just re-define `get()` or `post()` methods and they will be simply run
    synchronously. This may be convinient for draft implementation, i.e. for testing
    new libs or concepts.
    """
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        """Handle GET request asyncronously, delegates to
        ``self.get_async()`` coroutine.
        """
        yield self._run_method('get', *args, **kwargs)

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        """Handle POST request asyncronously, delegates to
        ``self.post_async()`` coroutine.
        """
        yield self._run_method('post', *args, **kwargs)

    @asyncio.coroutine
    def _run_async(self, coroutine, future_, *args, **kwargs):
        """Perform coroutine and set result to ``Future`` object."""

        try:
            result = yield from coroutine(*args, **kwargs)
            future_.set_result(result)
        except Exception as e:
            future_.set_exception(e)
            print(traceback.format_exc())

    def _run_method(self, method_, *args, **kwargs):
        """Run ``get_async()`` / ``post_async()`` / etc. coroutine
        wrapping result with ``tornado.concurrent.Future`` for
        compatibility with ``gen.coroutine``.
        """
        coroutine = getattr(self, '%s_async' % method_, None)

        if not coroutine:
            raise tornado.web.HTTPError(405)

        future_ = tornado.concurrent.Future()
        asyncio.async(
            self._run_async(coroutine, future_, *args, **kwargs)
        )

        return future_


class MainHandler(AsyncRequestHandler):
    @asyncio.coroutine
    def get_async(self):
        redis = self.application.redis
        yield from redis.set('my-key', 'OK')
        val = yield from redis.get('my-key')
        self.write('Hello asyncio.coroutine: %s' % val)


class Application(tornado.web.Application):
    def __init__(self):
        # Prepare IOLoop class to run instances on asyncio
        tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')

        handlers = [
            (r"/", MainHandler),
        ]

        super().__init__(handlers)

    def init_with_loop(self, loop):
        self.redis = loop.run_until_complete(
            aioredis.create_redis(('localhost', 6379), loop=loop)
        )


if __name__ == "__main__":
    print("Run hello_asyncio_multi ... http://127.0.0.1:8888")
    # Prepare application server
    application = Application()
    server = tornado.httpserver.HTTPServer(application)
    server.bind(8888, '127.0.0.1')

    # Fork
    server.start(0)

    # Instantiate and run loop
    loop = asyncio.get_event_loop()
    application.init_with_loop(loop)
    loop.run_forever()
