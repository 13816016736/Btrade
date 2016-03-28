# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
from utils import *
import config,re
from collections import defaultdict

class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/main.html")


class AccountHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        user = self.db.get("SELECT * FROM users WHERE id = %s", self.session.get("userid"))
        # user_info = self.db.get("SELECT * FROM user_info WHERE userid = %s", self.session.get("userid"))
        # if users and user_info:
        #     user.update(user_info)
        # else:
        #     user["name"] = ""
        city = []
        varietyids = []
        area = defaultdict(list)
        if user.has_key("areaid") and user.get("areaid") != 0:
            area = self.db.get("SELECT id,parentid FROM area WHERE id = %s", user.get("areaid"))
            city = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", area.get("parentid"))
        if user.has_key("varietyids") and user.get("varietyids") != "" and user.get("varietyids") is not None:
            varietyids = self.db.query("SELECT id,name FROM variety WHERE id in ("+user.get("varietyids")+")")
        self.render("dashboard/account.html", user=user, provinces=provinces, city=city, area=area, varietyids=varietyids)

class UpdateUserHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        print self.get_argument("oldpassword", None)
        nickname = self.get_argument("nickname")
        userid = self.session.get("userid")
        author = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        if self.get_argument("oldpassword", None) is None and self.get_argument("password", None) is None:
            password = ""
        else:
            if self.get_argument("oldpassword") == "" or self.get_argument("password") == "":
                self.api_response({'status':'fail','message':'新旧密码必须填写'})
                return
            else:
                #判断新密码格式是否是字母加数字
                pattern = re.compile(r'^[0-9a-zA-Z]{6,20}$')
                match = pattern.match(self.get_argument("password"))
                if match is None:
                    self.api_response({'status':'faile','message':'密码必须是6-20位字符'})
                    return
                if not author:
                    self.api_response({'status':'faile','message':'用户名不存在'})
                    return
                if md5(str(self.get_argument("oldpassword")+config.salt)) != author.password:
                    self.api_response({'status':'fail','message':'旧密码不对'})
                    return
                password = self.get_argument("password")

        if self.get_argument("oldphone", None) is None and self.get_argument("phone", None) is None and self.get_argument("verifycode", None) is None:
            phone = ""
        else:
            if self.get_argument("oldphone") == "" or self.get_argument("phone") == "" or self.get_argument("verifycode") == "":
                self.api_response({'status':'fail','message':'新旧手机号和短信验证码必须填写'})
                return
            else:
                #短信验证码是否正确self.get_argument("verifycode")
                if not author:
                    self.api_response({'status':'fail','message':'用户名不存在'})
                    return
                if self.get_argument("oldphone") != author.phone:
                    self.api_response({'status':'fail','message':'旧手机号不对'})
                    return
                phone = self.get_argument("phone")

        if password and phone:
            self.db.update("UPDATE users SET nickname = %s, password = %s, phone = %s  WHERE id = %s", nickname, md5(str(password + config.salt)), phone, userid)
            self.api_response({'status':'success','message':'更新成功'})
        elif password:
            self.db.update("UPDATE users SET nickname = %s, password = %s  WHERE id = %s", nickname, md5(str(password + config.salt)), userid)
            self.api_response({'status':'success','message':'更新成功'})
        elif phone:
            self.db.update("UPDATE users SET nickname = %s, phone = %s  WHERE id = %s", nickname, phone, userid)
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.db.update("UPDATE users SET nickname = %s  WHERE id = %s", nickname, userid)
            self.api_response({'status':'success','message':'更新成功'})

class UpdateUserNameHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("name", None) is None:
            self.api_response({'status':'fail','message':'经营主体必填'})
        else:
            # if self.db.query("select * from user_info where userid = %s", self.session.get("userid")):
            #     self.db.update("update users_info SET name = %s where userid = %s", self.get_argument("name"), self.session.get("userid"))
            # else:
            #     self.db.update("insert into user_info (userid, name)value(%s, %s)", self.session.get("userid"), self.get_argument("name"))
            self.db.update("update users SET name = %s where id = %s", self.get_argument("name"), self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})

class UpdateUserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        sql = []
        varietyids = []
        varietyname = []
        for variety in self.get_arguments("varietyid"):
            if variety == "":
                continue
            varietyid = self.db.get("SELECT id FROM variety WHERE name = %s", variety)
            if varietyid:
                varietyids.append(str(varietyid.id))
            else:
                varietyname.append(variety)
        print varietyname
        if varietyname:
            self.api_response({'status':'fail','message':u'不存在的品种'+','.join(varietyname)})
            return
        if self.get_argument("type"):
            sql.append("type = "+self.get_argument("type"))
        if varietyids:
            sql.append("varietyids = \""+",".join(varietyids)+"\"")
        if self.get_argument("city"):
            sql.append("areaid = "+self.get_argument("city"))
        self.db.update("UPDATE users SET "+",".join(sql)+" WHERE id = %s", self.session.get("userid"))
        self.api_response({'status':'success','message':'更新成功'})

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
                title = purchase["name"].encode('utf-8') + "回复了您的报价【" + purchase["variety"] + " "+ str(purchase["price"]) + "】"
                params.append([purchase["userid"],purchase["quoteuserid"],1,title,purchase["id"],0,int(time.time())])
                if int(state) == 1:
                    acceptQuote(purchase["quotephone"].encode('utf-8'), purchase["name"].encode('utf-8'), purchase["variety"], purchase["price"], config.unit, purchase["phone"].encode('utf-8'))
                elif int(state) == 2:
                    rejectQuote(purchase["quotephone"].encode('utf-8'), purchase["name"].encode('utf-8'), purchase["variety"], purchase["price"], config.unit, message.encode('utf-8'))
            self.db.executemany("insert into notification(sender,receiver,type,title,content,status,createtime)values(%s, %s, %s, %s, %s, %s, %s)",params)

            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})