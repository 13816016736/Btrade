import tornado.autoreload
import tornado.web
import tornado.ioloop
from controller.main import *

application = tornado.web.Application([
    (r"/", MainHandler),
	(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
])

if __name__ == "__main__":
    application.listen(8888)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()