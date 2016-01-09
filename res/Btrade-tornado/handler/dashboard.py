# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
from utils import *
import config
from collections import defaultdict

class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/main.html")


class AccountHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        users = self.db.query("SELECT * FROM users WHERE id = %s", self.session.get("userid"))
        user_info = self.db.query("SELECT * FROM user_info WHERE userid = %s", self.session.get("userid"))
        if users and user_info:
            users[0].update(user_info[0])
        else:
            users[0]["name"] = ""
        city = []
        varietyids = []
        area = defaultdict(list)
        if users[0].has_key("areaid") and users[0].get("areaid") != 0:
            area = self.db.query("SELECT id,parentid FROM area WHERE id = %s", users[0].get("areaid"))
            city = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", area[0].get("parentid"))
        if users[0].has_key("varietyids") and users[0].get("varietyids") != "":
            varietyids = self.db.query("SELECT id,name FROM variety WHERE id in ("+users[0].get("varietyids")+")")
        self.render("dashboard/account.html", user=users[0], provinces=provinces, city=city, area=area[0], varietyids=varietyids)

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
            else:
                if not author:
                    self.api_response({'status':'faile','message':'用户名不存在'})
                if md5(str(self.get_argument("oldpassword")+config.salt)) != author.password:
                    self.api_response({'status':'fail','message':'旧密码不对'})
                password = self.get_argument("password")

        if self.get_argument("oldphone", None) is None and self.get_argument("phone", None) is None and self.get_argument("verifycode", None) is None:
            phone = ""
        else:
            if self.get_argument("oldphone") == "" or self.get_argument("phone") == "" or self.get_argument("verifycode") == "":
                self.api_response({'status':'fail','message':'新旧手机号和短信验证码必须填写'})
            else:
                #短信验证码是否正确self.get_argument("verifycode")
                if not author:
                    self.api_response({'status':'fail','message':'用户名不存在'})
                if self.get_argument("oldphone") != author.phone:
                    self.api_response({'status':'fail','message':'旧手机号不对'})
                phone = self.get_argument("phone")

        if password and phone:
            self.db.update("UPDATE users SET nickname = %s, password = %s, phone = %s  WHERE id = %s", nickname, password, phone, userid)
            self.api_response({'status':'success','message':'更新成功'})
        elif password:
            self.db.update("UPDATE users SET nickname = %s, password = %s  WHERE id = %s", nickname, password, userid)
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
            if self.db.query("select * from user_info where userid = %s", self.session.get("userid")):
                self.db.update("update user_info SET name = %s where userid = %s", self.get_argument("name"), self.session.get("userid"))
            else:
                self.db.update("insert into user_info (userid, name)value(%s, %s)", self.session.get("userid"), self.get_argument("name"))
            self.api_response({'status':'success','message':'更新成功'})

class UpdateUserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        sql = []
        varietyids = []
        varietyname = []
        for variety in self.get_arguments("varietyid"):
            if variety == "":
                break
            varietyid = self.db.query("SELECT id FROM variety WHERE name = %s", variety)
            if varietyid:
                varietyids.append(str(varietyid[0].id))
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
