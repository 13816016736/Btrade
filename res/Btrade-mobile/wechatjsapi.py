# -*- coding: utf-8 -*-

import time
import random
import string
import hashlib,requests,json
import config

class WechartJSAPI:
    def __init__(self, database):
        self.db = database

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.getTicket(),
            'timestamp': self.__create_timestamp(),
            'url': url
        }
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        self.ret["appId"] = config.appid
        return self.ret

    def getAccessToken(self):
        conf = self.db.get("select * from config where `key`=%s", "access_token")
        if conf and int(conf['expires_time']) > int(time.time()) and conf['value']:
            return conf["value"]
        else:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (config.appid, config.secret)
            res = requests.get(url)
            conf = json.loads(res.text.encode("utf-8"))
            self.db.execute("delete from config where `key` = %s", "access_token")
            self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)", "access_token", conf["access_token"], int(conf["expires_in"])+int(time.time()), int(time.time()))
            return conf["access_token"]
    def getRefeshAccessToken(self):
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        config.appid, config.secret)
        res = requests.get(url)
        conf = json.loads(res.text.encode("utf-8"))
        self.db.execute("delete from config where `key` = %s", "access_token")
        self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)",
                        "access_token", conf["access_token"], int(conf["expires_in"]) + int(time.time()),
                        int(time.time()))
        return conf["access_token"]

    def getTicket(self):
        config = self.db.get("select * from config where `key`=%s", "jsapi_ticket")
        if config and int(config['expires_time']) > int(time.time()) and config['value']:
            return config["value"]
        else:
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (self.getAccessToken())
            res = requests.get(url)
            config = json.loads(res.text.encode("utf-8"))
            self.db.execute("delete from config where `key` = %s", "jsapi_ticket")
            self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)", "jsapi_ticket", config["ticket"], int(config["expires_in"])+int(time.time()), int(time.time()))
            return config["ticket"]

if __name__ == '__main__':
    # 注意 URL 一定要动态获取，不能 hardcode
    wechart = WechartJSAPI('jsapi_ticket')
    print wechart.sign('http://example.com')