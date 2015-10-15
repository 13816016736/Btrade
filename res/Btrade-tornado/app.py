import os.path
import tornado.autoreload
import tornado.web
import tornado.ioloop
import session
from controller.main import *
from controller.login import *

class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "blog_title": u"Tornado Btrade",
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "xsrf_cookies": True,
            "login_url": "/login",
            "cookie_secret": "e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
            "session_secret": "3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            "session_timeout": 60,
            "store_options": {
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_pass': '',
            },
        }

        handlers = [
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
        ];
        tornado.web.Application.__init__(self, handlers, **settings)

        self.session_manager = session.SessionManager(settings["session_secret"], settings["store_options"], settings["session_timeout"])

if __name__ == "__main__":
    app = Application()
    app.listen("8888")
    print "start on port 8888..."
    tornado.ioloop.IOLoop.instance().start()