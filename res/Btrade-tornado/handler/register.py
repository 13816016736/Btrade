# -*- coding: utf-8 -*-

from base import BaseHandler
from uimodule import geetest

#极验证
BASE_URL = "api.geetest.com/get.php?gt="
captcha_id = "9a601256e290cc2001027f5f701a48fb"
private_key = "c7ec51a45463e93b924f0ae462e0cdaa"
product = "embed"

class RegisterHandler(BaseHandler):
    def get(self):
        gt = geetest.geetest(captcha_id, private_key)
        url = ""
        httpsurl = ""
        try:
            challenge = gt.geetest_register()
        except:
            challenge = ""
        if len(challenge) == 32:
            url = "http://%s%s&challenge=%s&product=%s" % (BASE_URL, captcha_id, challenge, product)
            httpsurl = "https://%s%s&challenge=%s&product=%s" % (BASE_URL, captcha_id, challenge, product)
	    self.render("register.html", url=url)

    def post(self):
        # self.set_secure_cookie("user", self.get_argument("username"))
        self.session["user"] = self.get_argument("username")
        self.session.save()
        #self.success('成功的提示')
        self.redirect(self.get_argument('next_url', '/'))

