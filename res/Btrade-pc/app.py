import sys,os
sys.path.append(os.path.join(sys.path[0],"../Btrade-public"))
sys.path.append(os.path.join(sys.path[0],"../Btrade-public/handler"))


import tornado.autoreload
import tornado.web
import tornado.ioloop
import logging
import logging.handlers
import session,platform
from tornado.options import options
from config import settings, handlers, log, log_file
from uimodule import uimodule

class Application(tornado.web.Application):
    def __init__(self):
        logger = logging.getLogger()
        if log and 'Linux' in platform.system():
            options.log_file_prefix = log_file
            timelog = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', 1, 0)
            logger.addHandler(timelog)
        options.parse_command_line()
        settings['ui_modules'] = uimodule
        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_manager = session.SessionManager(settings["session_secret"], settings["store_options"], settings["session_timeout"])

if __name__ == "__main__":
    app = Application()
    app.listen("8888", address='0.0.0.0')
    print "start on port 8888..."
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()