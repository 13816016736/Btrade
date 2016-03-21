# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import config, time

class MainHandler(BaseHandler):
    def get(self):
        self.redirect('/users/userlist')
        # self.render("main.html")

class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'users/userlist',
            'num': self.db.execute_rowcount("SELECT * FROM users"),
        }
        users = self.db.query("SELECT * FROM users LIMIT %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        self.render("userlist.html", users=users, nav=nav)

class UserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, userid):
        user = self.db.get("SELECT * FROM users where id = %s", userid)
        self.render("userinfo.html", user=user)

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("userid") is None or self.get_argument("nickname") is None or self.get_argument("type") is None or self.get_argument("name") is None or self.get_argument("phone") is None:
            self.api_response({'status':'fail','message':'请完整填写表单'})
        else:
            self.db.execute("update users set nickname=%s,type=%s,name=%s,phone=%s where id = %s",
                            self.get_argument("nickname"), self.get_argument("type"), self.get_argument("name"),
                            self.get_argument("phone"), self.get_argument("userid"))
            self.api_response({'status':'success','message':'提交成功'})

class UserRecoverHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=1 where id = %s", userid)
        self.redirect('/users/userlist')

class UserRemoveHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=0 where id = %s", userid)
        self.redirect('/users/userlist')

class UpdateQuoteStateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        qid = self.get_argument("qid", 0)
        state = self.get_argument("state", 0)
        message = self.get_argument("message", "")
        if qid != 0 and state !=0:
            if qid.isdigit() and int(state) == 2 and message != "":
                self.db.execute("update quote set state=%s,message=%s,updatetime=%s where id = %s", state, message, int(time.time()), qid)
            else:
                self.db.execute("update quote set state=%s,updatetime=%s where id in ("+qid+")", state, int(time.time()))
            #回复供应商的报价后，要通知供应商
            purchases = self.db.query("select u.phone quotephone,ta.* from (select u.name,u.phone,tab.id,tab.quoteuserid,tab.userid,tab.name variety,tab.price from "
                          "(select ta.id,ta.quoteuserid,ta.price,ta.name,p.userid from (select t.id,t.userid quoteuserid,t.purchaseid,t.price,v.name from "
                          "(select q.id,q.userid,pi.purchaseid,pi.varietyid,pi.price from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where q.id in ("+qid+")) t left join variety v on t.varietyid = v.id)"
                          " ta left join purchase p on ta.purchaseid = p.id) tab left join users u on tab.userid = u.id) ta left join users u on ta.quoteuserid = u.id")
            params = []
            for purchase in purchases:
                title = purchase["name"].encode('utf-8') + "回复了您的报价【" + purchase["variety"].encode('utf-8') + " "+ str(purchase["price"]) + "】"
                params.append([purchase["userid"],purchase["quoteuserid"],1,title,purchase["id"],0,int(time.time())])
                if int(state) == 1:
                    config.acceptQuote(purchase["quotephone"], purchase["name"], purchase["variety"], purchase["price"], config.unit, purchase["phone"])
                elif int(state) == 2:
                    config.rejectQuote(purchase["quotephone"], purchase["name"], purchase["variety"], purchase["price"], config.unit, message)
            self.db.executemany("insert into notification(sender,receiver,type,title,content,status,createtime)values(%s, %s, %s, %s, %s, %s, %s)",params)

            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})