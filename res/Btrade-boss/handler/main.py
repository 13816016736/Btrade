# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import config, time
from utils import *

class MainHandler(BaseHandler):
    def get(self):
        self.redirect('/users/userlist')
        # self.render("main.html")

class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        query = self.get_argument("query", None)
        page=self.get_argument("page",0)
        condition = ""
        if query:
            condition = " where phone = '%s'" % query
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'users/userlist',
            'cur': page + 1,
            'num': self.db.execute_rowcount("SELECT * FROM users" + condition),
            'style':0,
            'query': "query=%s" % query if query else "",
        }
        users = self.db.query("SELECT * FROM users" + condition + " LIMIT %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        self.render("userlist.html", users=users, nav=nav, query=query)

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
            user = self.db.query("select * from users where phone = %s and id != %s", self.get_argument("phone"), self.get_argument("userid"))
            if user:
                self.api_response({'status':'fail','message':'此手机号已被他人注册过'})
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
            purchases = self.db.query("select u.phone quotephone,u.openid quoteopenid,ta.* from (select u.name,u.phone,u.nickname,tab.id,tab.quoteuserid,tab.userid,tab.name variety,tab.qprice,tab.price from "
                          "(select ta.id,ta.quoteuserid,ta.qprice,ta.price,ta.name,p.userid from (select t.id,t.userid quoteuserid,t.purchaseid,t.qprice,t.price,v.name from "
                          "(select q.id,q.price qprice,q.userid,pi.purchaseid,pi.varietyid,pi.price from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where q.id in ("+qid+")) t left join variety v on t.varietyid = v.id)"
                          " ta left join purchase p on ta.purchaseid = p.id) tab left join users u on tab.userid = u.id) ta left join users u on ta.quoteuserid = u.id")
            params = []
            for purchase in purchases:
                purchase["name"] = purchase["name"].encode('utf-8') if isinstance(purchase["name"], unicode) else purchase["name"]
                purchase["variety"] = purchase["variety"].encode('utf-8') if isinstance(purchase["variety"], unicode) else purchase["variety"]
                purchase["quotephone"] = purchase["quotephone"].encode('utf-8') if isinstance(purchase["quotephone"], unicode) else purchase["quotephone"]
                purchase["phone"] = purchase["phone"].encode('utf-8') if isinstance(purchase["phone"], unicode) else purchase["phone"]
                message = message.encode('utf-8') if isinstance(message, unicode) else message
                title = purchase["name"] + "回复了您的报价【" + purchase["variety"] + " "+ str(purchase["price"]) + "】"
                # title = purchase["name"].encode('utf-8') + "回复了您的报价【" + purchase["variety"].encode('utf-8') + " "+ str(purchase["price"]) + "】"
                today = time.time()
                params.append([purchase["userid"],purchase["quoteuserid"],1,title,purchase["id"],0,int()])
                if int(state) == 1:
                    acceptQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, purchase["phone"])
                    acceptQuoteWx(purchase["quoteopenid"], purchase["id"], purchase["name"], purchase["variety"], purchase["qprice"], purchase["nickname"], purchase["phone"], today)
                elif int(state) == 2:
                    rejectQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, message)
                    rejectQuoteWx(purchase["quoteopenid"], purchase["id"], purchase["name"], purchase["variety"], purchase["qprice"], message, today)
            self.db.executemany("insert into notification(sender,receiver,type,title,content,status,createtime)values(%s, %s, %s, %s, %s, %s, %s)",params)

            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})



class AdminListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        query = self.get_argument("query", None)
        page=self.get_argument("page",0)
        condition = ""
        if query:
            condition = " where username ='%s'" % query
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'users/adminlist',
            'cur': page + 1,
            'num': self.db.execute_rowcount("SELECT * FROM admin" + condition),
            'style':0,
            'query': "query=%s" % query if query else "",
        }
        users = self.db.query("SELECT * FROM admin" + condition + " LIMIT %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        for item in users:
            timeArray = time.localtime(float(item["createtime"]))
            item["createtime"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        self.render("adminlist.html", users=users, nav=nav, query=query)
    def post(self):
        pass

class UpdateAdminStatusHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",-1)
        status=self.get_argument("status",1)
        self.db.execute("update admin set status=%s where id = %s", status,id)
        self.redirect('/users/adminlist')
class AdminResetHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",-1)
        self.db.execute("update admin set password=%s where id = %s", md5(str("123456" + config.salt)),id)
        self.redirect('/users/adminlist')
class AdminUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",None)
        user=None
        if id:
            user=self.db.get("select * from admin where id=%s",id)
        self.render("adminuser.html",id=id,user=user)
        pass

    @tornado.web.authenticated
    def post(self):
        username=self.get_argument("username",None)
        newpwd=self.get_argument("newpwd",None)
        oldpwd=self.get_argument("oldpwd",None)
        id=self.get_argument("id",None)
        if newpwd=="":
            self.api_response({'status': 'fail', 'message': '添加失败', 'data': '密码不能为空'})
        else:
            if id:
                user = self.db.get("select * from admin where id=%s", id)
                if user.password==md5(str(oldpwd + config.salt)):
                    self.db.execute("update admin set password=%s where id=%s", md5(str(newpwd + config.salt)), id)
                    self.api_response({'status': 'success', 'message': '修改成功'})
                else:
                    self.api_response({'status': 'fail', 'message': '旧密码不正确'})
            else:
                if username=="":
                    self.api_response({'status': 'fail', 'message': '用户名不能为空'})
                else:
                    user = self.db.get("select * from admin where username=%s", username)
                    if user:
                        self.api_response({'status': 'fail', 'message': '用户名不能重名'})
                    else:
                        self.db.execute("insert into admin (username,password,createtime) value(%s,%s,%s)",username,md5(str(newpwd + config.salt)),int(time.time()))
                        self.api_response({'status': 'success', 'message': '添加成功'})

