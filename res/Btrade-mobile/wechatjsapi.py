# -*- coding: utf-8 -*-

import time
import random
import string
import hashlib,requests,json
import config
import logging

class WechartJSAPI:
    def __init__(self, database):
        self.db = database

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self, url,gettype=1):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.getTicket(gettype),
            'timestamp': self.__create_timestamp(),
            'url': url
        }
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        if gettype==1:
            self.ret["appId"] = config.appid
        else:
            self.ret["appId"] = config.purchase_appid
        return self.ret

    def getAccessToken(self,gettype=1):
        keyname="access_token"
        if gettype==2:
            keyname="access_token_2"
        conf = self.db.get("select * from config where `key`=%s", keyname)
        if conf and int(conf['expires_time']) > int(time.time()) and conf['value']:
            return conf["value"]
        else:
            appid =config.appid
            secret=config.secret
            if gettype==2:
                appid=config.purchase_appid
                secret = config.purchase_secret
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appid, secret)
            res = requests.get(url)
            conf = json.loads(res.text.encode("utf-8"))

            self.db.execute("delete from config where `key` = %s", keyname)
            self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)", keyname, conf["access_token"], int(conf["expires_in"])+int(time.time()), int(time.time()))
            return conf["access_token"]
    def getRefeshAccessToken(self,gettype=1):
        appid = config.appid
        secret = config.secret
        keyname = "access_token"
        if gettype == 2:
            appid = config.purchase_appid
            secret = config.purchase_secret
            keyname = "access_token_2"
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
            appid, secret)
        res = requests.get(url)
        conf = json.loads(res.text.encode("utf-8"))
        self.db.execute("delete from config where `key` = %s", keyname)
        self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)",
                        keyname, conf["access_token"], int(conf["expires_in"]) + int(time.time()),
                        int(time.time()))
        return conf["access_token"]

    def getTicket(self,gettype=1):
        keyname="jsapi_ticket"
        if gettype==2:
            keyname="jsapi_ticket_2"
        config = self.db.get("select * from config where `key`=%s", keyname)
        if config and int(config['expires_time']) > int(time.time()) and config['value']:
            return config["value"]
        else:
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (self.getAccessToken(gettype))
            res = requests.get(url)
            logging.info(res)
            data = json.loads(res.text.encode("utf-8"))
            errorCode = data.get("errcode", None)
            if errorCode:
                access_token = self.getRefeshAccessToken(gettype)
                url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (access_token)
                res = requests.get(url)
                logging.info(res)
            config = json.loads(res.text.encode("utf-8"))
            self.db.execute("delete from config where `key` = %s", keyname)
            self.db.execute("insert into config (`key`, `value`, expires_time, createtime)value(%s, %s, %s, %s)", keyname, config["ticket"], int(config["expires_in"])+int(time.time()), int(time.time()))
            return config["ticket"]

if __name__ == '__main__':
    # 注意 URL 一定要动态获取，不能 hardcode
    wechart = WechartJSAPI('jsapi_ticket')
    print wechart.sign('http://example.com')