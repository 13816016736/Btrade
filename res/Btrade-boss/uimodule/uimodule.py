# -*- coding: utf-8 -*-

import tornado.web
from config import conf

class PageNav(tornado.web.UIModule):
    """分页导航
    只有一页时不显示分页
    当分页过多时应该只显示部分，但似乎这不是问题，是我多虑了，哈哈！
    """
    def render(self, nav, show=False):
        if show:
            if nav['num'] % conf['POST_NUM'] != 0:
                nav['num'] = nav['num'] // conf['POST_NUM'] + 1
            else:
                nav['num'] = nav['num'] // conf['POST_NUM']
            if nav['num'] != 1:
                return self.render_string("uimodule/page-nav.html", nav=nav)
            else:
                return ''