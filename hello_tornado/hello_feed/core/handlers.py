import tornado.gen
from .models import Feed

# Handlers in Tornado like Views in Django
class FeedHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        feed = yield Feed.fetch()
        self.write(feed)
