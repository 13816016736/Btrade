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
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 100000")
        user = self.db.get("SELECT * FROM users WHERE id = %s", self.session.get("userid"))
        # user_info = self.db.get("SELECT * FROM user_info WHERE userid = %s", self.session.get("userid"))
        # if users and user_info:
        #     user.update(user_info)
        # else:
        #     user["name"] = ""
        city = []
        district = []
        varietyids = []
        area = defaultdict(list)
        if user.has_key("areaid") and user.get("areaid") != 0:
            area = self.db.get("SELECT id,parentid,areaname FROM area WHERE id = %s", user.get("areaid"))
            district = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", area.get("parentid"))
            city = self.db.query("SELECT c.id,c.areaname,a.parentid FROM area c,(SELECT id,parentid,areaname FROM area WHERE id = %s) a WHERE a.parentid = c.parentid", area.get("parentid"))
            area["gparentid"] = city[0]["parentid"]
        if user.has_key("varietyids") and user.get("varietyids") != "" and user.get("varietyids") is not None:
            varietyids = self.db.query("SELECT id,name FROM variety WHERE id in ("+user.get("varietyids")+")")
        self.render("dashboard/account.html", user=user, provinces=provinces, city=city, district=district, area=area, varietyids=varietyids)

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
        if self.get_argument("area"):
            sql.append("areaid = "+self.get_argument("area"))
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
            #purchases = self.db.query("select u.phone quotephone,u.openid quoteopenid,ta.* from (select u.name,u.phone,u.nickname,tab.id,tab.quoteuserid,tab.userid,tab.name variety,tab.qprice,tab.price from "
            #              "(select ta.id,ta.quoteuserid,ta.qprice,ta.price,ta.name,p.userid from (select t.id,t.userid quoteuserid,t.purchaseid,t.qprice,t.price,v.name from "
            #              "(select q.id,q.price qprice,q.userid,pi.purchaseid,pi.varietyid,pi.price from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where q.id in ("+qid+")) t left join variety v on t.varietyid = v.id)"
            #              " ta left join purchase p on ta.purchaseid = p.id) tab left join users u on tab.userid = u.id) ta left join users u on ta.quoteuserid = u.id")
            #获取报价信息
            purchasesinfos = self.db.query(
                    "select q.id,q.price qprice,q.userid quoteuserid ,pi.purchaseid,pi.varietyid,pi.price from"
                    " quote q left join purchase_info pi on q.purchaseinfoid = pi.id where q.id in (%s)" % qid)
            if purchasesinfos:
                purchaseinfoids = [str(purchasesinfo["purchaseid"]) for purchasesinfo in purchasesinfos]
                purchaseinfoids = list(set(purchaseinfoids))  # 去重采购单id
                # 获取采购单的采购人的信息
                purchases = self.db.query(
                    "select p.id,u.phone,u.id userid,u.name,u.nickname from purchase p left join users u on p.userid=u.id where p.id in(%s)" % ",".join(
                    purchaseinfoids))
                purchaseuserinfo = dict((i.id, [i.phone, i.userid, i.name, i.nickname]) for i in purchases)
                quoteuserids = [str(purchasesinfo["quoteuserid"]) for purchasesinfo in purchasesinfos]
                # 获取报价人的信息
                quoteusers = self.db.query("select id,phone,openid from users where id in (%s)" % ",".join(quoteuserids))
                quoteusersinfo = dict((i.id, [i.phone, i.openid]) for i in quoteusers)
                variteyids = [str(purchasesinfo["varietyid"]) for purchasesinfo in purchasesinfos]
                variteyids = list(set(variteyids))  # 去重品种id
                # 获取品种信息
                variteyinfo = self.db.query("select id,name from variety where id in (%s)" % ",".join(variteyids))
                variteys = defaultdict(list)
                for item in variteyinfo:
                    variteys[item.id] = item.name
                # 封装报价人和采购人的信息
                for purchase in purchasesinfos:
                    purchase["quotephone"] = quoteusersinfo[purchase.quoteuserid][0]
                    purchase["quoteopenid"] = quoteusersinfo[purchase.quoteuserid][1]
                    purchase["variety"] = variteys[purchase.varietyid]
                    purchase["phone"] = purchaseuserinfo[purchase.purchaseid][0]
                    purchase["userid"] = purchaseuserinfo[purchase.purchaseid][1]
                    purchase["name"] = purchaseuserinfo[purchase.purchaseid][2]
                    purchase["nickname"] = purchaseuserinfo[purchase.purchaseid][3]
            params = []
            for purchase in purchasesinfos:
                purchase["name"] = purchase["name"].encode('utf-8') if isinstance(purchase["name"], unicode) else purchase["name"]
                purchase["variety"] = purchase["variety"].encode('utf-8') if isinstance(purchase["variety"], unicode) else purchase["variety"]
                purchase["quotephone"] = purchase["quotephone"].encode('utf-8') if isinstance(purchase["quotephone"], unicode) else purchase["quotephone"]
                purchase["phone"] = purchase["phone"].encode('utf-8') if isinstance(purchase["phone"], unicode) else purchase["phone"]
                message = message.encode('utf-8') if isinstance(message, unicode) else message
                title = purchase["name"] + "回复了您的报价【" + purchase["variety"] + " "+ str(purchase["qprice"]) + "】"
                today = time.time()
                params.append([purchase["userid"],purchase["quoteuserid"],1,title,purchase["id"],0,int(today)])
                # 为采购商积分：
                self.db.execute("update users set push_score=push_score+1 where id=%s", purchase["userid"])

                if int(state) == 1:
                    # 为供货商积分：
                    self.db.execute("update users set push_score=push_score+1 where id=%s", purchase["quoteuserid"])

                    acceptQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, purchase["phone"])
                    acceptQuoteWx(purchase["quoteopenid"], purchase["id"],purchase["name"], purchase["variety"], purchase["qprice"], purchase["nickname"], purchase["phone"], today)
                elif int(state) == 2:
                    rejectQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, message)
                    rejectQuoteWx(purchase["quoteopenid"], purchase["id"],purchase["name"], purchase["variety"], purchase["qprice"], message, today)
                    pass
            self.db.executemany("insert into notification(sender,receiver,type,title,content,status,createtime)values(%s, %s, %s, %s, %s, %s, %s)",params)

            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})
