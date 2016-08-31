# -*- coding: utf-8 -*-

import tornado.web
from base import *
import config
import json, os, datetime
import time,utils,re
from collections import defaultdict
from utils import *
from wechatjsapi import *
from webbasehandler import purchase_push_trace

class MainHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        varieties = []
        quotevariety = []
        userid = self.session.get("userid")
        if userid:
            user = self.db.get("select varietyids from users where id = %s", userid)
            if user["varietyids"]:
                varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")

            #用户报过价的品种
            quotevariety =self.db.query("select pi.varietyid from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where userid = %s and pi.varietyid is not null",userid)
            if quotevariety:
                quotevarietyids=[str(item["varietyid"]) for item in quotevariety ]
                quotevariety = self.db.query("select name from variety where id in (%s) group by name  " % ",".join(quotevarietyids))
            #quotevariety = self.db.query(
            #    "select v.name name from (select pi.varietyid from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where userid = %s and pi.varietyid is not null) t"
            #    " left join variety v on t.varietyid = v.id group by name", userid)

        self.render("index.html", varieties=varieties, quotevariety=quotevariety)


    def post(self):
        pass

class YaocaigouHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        showtype=self.get_argument("type",1)
        if int(showtype) == 1:
            self.render("yaocaigou.html")
        else:
            self.render("purchase_yaocaigou.html")
class AboutHandler(BaseHandler):
    def get(self):
        accept_purchaseinfo = self.db.query("select distinct purchaseinfoid from quote where state=1")
        accept_company_num = 0
        accept_purchaseinfoids = []
        if accept_purchaseinfo:
            accept_purchaseinfoids = [str(item["purchaseinfoid"]) for item in accept_purchaseinfo]
            accept_company_num = self.db.execute_rowcount(
                "select distinct p.userid from purchase p left join  purchase_info pi on p.id=pi.purchaseid where pi.id in (%s)" % (
                ",".join(accept_purchaseinfoids)))
        accept_quote_user_num = self.db.execute_rowcount("select distinct userid  from quote where state=1")
        accept_num = len(accept_purchaseinfoids)
        sum_quantity = 0
        sum_price = 0
        for item in accept_purchaseinfoids:
            purchaseinfo = self.db.get("select quantity,unit from purchase_info where id=%s", item)
            if purchaseinfo:
                quoteinfo = self.db.get(
                    "select price from quote where purchaseinfoid=%s and state=1 order by price desc limit 0,1", item)
                if purchaseinfo["unit"] == u"公斤":
                    sum_quantity += int(purchaseinfo["quantity"]) / 1000
                    sum_price += int(purchaseinfo["quantity"]) * float(quoteinfo["price"])

                elif purchaseinfo["unit"] == u"吨":
                    sum_quantity += int(purchaseinfo["quantity"])
                    sum_price += int(purchaseinfo["quantity"]) * float(quoteinfo["price"]) * 1000

        user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9)")
        supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2")
        total = user_count + supplier_count
        show_data = {"accept_company_num": accept_company_num, "accept_quote_user_num": accept_quote_user_num,"total":total,
                         "accept_num": accept_num, "sum_quantity": sum_quantity, "sum_price": int(sum_price / 10000)}
        self.render("about.html",data=show_data)

class CenterHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        showtype=self.get_argument("type",1)
        user = self.db.get("select * from users where id = %s", userid)
        member=None
        if showtype==1:
            member=self.db.get("select * from member where userid = %s and type=2 and status=1", userid)
        else:
            member=self.db.get("select * from member where userid = %s and type=3 and status=1", userid)
        news = self.db.query("select * from notification where receiver = %s order by createtime desc", userid)

        unread = 0
        unreadtype = 0
        sell = []
        purchase = []
        quoteid = []
        for new in news:
            if new.status == 0:
                unread += 1
                unreadtype = new.type
            if new.type == 1:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                if new["content"].isdigit():
                    quoteid.append(new["content"])
                sell.append(new)
            if new.type == 2:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                purchase.append(new)
        #更新session中未读信息数
        self.session["notification"] = unread
        self.session.save()

        #报价收到回复消息的表情
        results = []
        if quoteid:
            results = self.db.query("select id,state from quote where userid = %s and id in ("+",".join(quoteid)+")", userid)
        faces = {}
        for result in results:
            faces[str(result["id"])] = int(result["state"])
        #print faces
        #最近一周报价次数 去掉统计最近一周了，全部统计所有
        # t = time.time()
        # week_begin = get_week_begin(t,0)
        # week_end = get_week_begin(t,1)
        #我对别人的采购单进行的报价
        quotestat = self.db.get("select count(id) quotenum,count(if(state!=0,true,null )) replynum from quote where userid = %s"
                                 , self.session.get("userid"))
        quotenum = quotestat["quotenum"]
        replynum = quotestat["replynum"]
        #统计一周的采购批次
        purchases = self.db.query("select id from purchase where userid = %s", userid)
        unreadquote = 0
        purchaseinfos = []
        quotes = []
        if purchases:
            purchaseinfos = self.db.query("select id from purchase_info where purchaseid in (%s)" % ",".join([str(p["id"]) for p in purchases]))
            #我的采购单收到的报价
            if purchaseinfos:
                quotes = self.db.query("select id,state from quote where purchaseinfoid in (%s)" % ",".join([str(pi["id"]) for pi in purchaseinfos]))
                unreadquote = 0
                for q in quotes:
                    if q["state"] == 0:
                        unreadquote += 1

        if int(showtype)==1:
            self.render("center.html", user=user, unread=unread, unreadtype=unreadtype, sell=sell, purchase=purchase, faces=faces
                    , quotenum=quotenum, replynum=replynum, purchaseinfos=purchaseinfos, quotes=quotes, unreadquote=unreadquote,member=member)
        else:
            self.render("purchase_center.html", user=user, unread=unread, unreadtype=unreadtype, sell=sell, purchase=purchase,
                        faces=faces
                        , quotenum=quotenum, replynum=replynum, purchaseinfos=purchaseinfos, quotes=quotes,
                        unreadquote=unreadquote, member=member)

    @tornado.web.authenticated
    def post(self):
        pass

class UserAttentionHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("select varietyids from users where id = %s", userid)
        varieties = []
        if user["varietyids"]:
            varieties = self.db.query("select id,name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_attention.html", varieties=varieties)

class UserInfoHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        user = self.db.get("SELECT * FROM users where id = %s", self.session.get("userid"))
        varieties = []
        if user["varietyids"]:
            varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_info.html", user=user, varieties=varieties)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        pass

class NewsHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, type):
        news = self.db.query("select * from notification where receiver = %s order by createtime desc", self.session.get("userid"))
        unread = {}
        sell = []
        purchase = []
        grow = []
        system = []
        quoteid = []
        for new in news:
            if new.status == 0:
                if new.type == 1:
                    unread["sell"] = True
                elif new.type == 2:
                    unread["purchase"] = True
                elif new.type == 3:
                    unread["grow"] = True
                elif new.type == 4:
                    unread["system"] = True
            if new.type == 1:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                if new["content"].isdigit():
                    quoteid.append(new["content"])
                sell.append(new)
            if new.type == 2:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                purchase.append(new)
            if new.type == 3:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                grow.append(new)
            if new.type == 4:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                system.append(new)
        #报价收到回复消息的表情
        results = []
        if quoteid:
            results = self.db.query("select id,state from quote where userid = %s and id in ("+",".join(quoteid)+")", self.session.get("userid"))
        faces = {}
        for result in results:
            faces[str(result["id"])] = int(result["state"])
        #print faces
        self.render("news.html", type=int(type), unread=unread, sell=sell, purchase=purchase, grow=grow, system=system, faces=faces)

    @tornado.web.authenticated
    def post(self):
        pass

class ArticleHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, articleid):
        article = self.db.get("select * from notification where receiver = %s and id = %s", self.session.get("userid"), articleid)
        result = self.db.execute("update notification set status = 1 where receiver = %s and id = %s", self.session.get("userid"), articleid)
        #print result
        article["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(article["createtime"])))
        self.render("article.html", article=article)

    @tornado.web.authenticated
    def post(self):
        pass

class UserUpdatePasswordHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        self.render('update_password.html')

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        userid = self.session.get("userid")
        author = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        if not author:
            self.api_response({'status':'faile','message':'用户名不存在'})
        elif self.get_argument("oldpassword") == "" or self.get_argument("password") == "" or self.get_argument("passwordconfirm") == "":
            self.api_response({'status':'fail','message':'新旧密码必须填写'})
        elif self.get_argument("password") != self.get_argument("passwordconfirm"):
            self.api_response({'status':'fail','message':'新密码和确认密码不一致'})
        elif md5(str(self.get_argument("oldpassword")+config.salt)) != author.password:
            self.api_response({'status':'fail','message':'旧密码不对'})
        else:
            self.db.update("UPDATE users SET password = %s  WHERE id = %s", md5(str(self.get_argument("password")+config.salt)), userid)
            self.api_response({'status':'success','message':'更新成功'})

class UserUpdateNicknameHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        self.render('update_nickname.html', user=user)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        nickname = self.get_argument("nickname")
        if nickname:
            self.db.update("UPDATE users SET nickname = %s  WHERE id = %s", nickname, self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.api_response({'status':'fail','message':'个人称呼必填'})

class UserCategoryHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        self.render('category.html', user=user)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        type = self.get_argument("type")
        if type:
            self.db.update("UPDATE users SET type = %s  WHERE id = %s", type, self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.api_response({'status':'fail','message':'请选择经营类型'})

class WxcbHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if checkSignature(signature, timestamp, nonce):
            self.api_response(echostr)
        else:
            self.api_response("check signature fail")

class WechartConfigHandler(BaseHandler):
    @purchase_push_trace
    def post(self):
        wechart = WechartJSAPI(self.db).sign(self.get_argument("url",None))
        if wechart:
            self.api_response({'status':'success','message':'获取微信配置成功','data':wechart})
        else:
            self.api_response({'status':'fail','message':'获取微信配置失败'})

class ForgetPwdHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        self.render("find_password.html")

    @purchase_push_trace
    def post(self):
        smscode = self.get_argument("smscode")
        phone = self.get_argument("phone")
        if self.db.get("select * from users where phone = %s" , phone):
            # 验证手机验证码
            if self.session.get("smscode") == smscode:
                self.session["phone"] = phone
                self.session.save()
                self.render("find_password_2.html", smscode=smscode)
            else:
                self.error("手机验证码错误","/forgetpwd")
        else:
            self.error("手机号不存在","/forgetpwd")

class SetPwdHandler(BaseHandler):
    @purchase_push_trace
    def post(self):
        smscode = self.get_argument("smscode")
        password = self.get_argument("password")
        repassword = self.get_argument("repassword")
        phone = self.session.get("phone")
        if password is None and repassword is None and password <> repassword:
            self.error("密码和确认密码填写错误","/forgetpwd")
        user = self.db.get("select id from users where phone = %s", phone)
        if len(user) == 1:
            # 验证手机验证码
            if self.session.get("smscode") == smscode:
                self.db.update("update users set password = %s where id = %s", utils.md5(str(password + config.salt)), user["id"])
                self.success("操作成功","/")
            else:
                self.error("手机验证码错误","/forgetpwd")
        else:
            self.error("手机号存在异常，请联系客服人员","/forgetpwd")

class GetSmsCodeForPwdHandler(BaseHandler):
    @purchase_push_trace
    def post(self):
        phone = self.get_argument("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount == 0:
            self.api_response({'status':'fail','message':'此手机号暂未注册'})
            return
        smscode = ''.join(random.sample(['0','1','2','3','4','5','6','7','8','9'], 6))
        message = utils.getSmsCode(phone, smscode)
        import json
        message = json.loads(message.encode("utf-8"))
        if message["result"]:
            self.session["smscode"] = smscode
            self.session.save()
            self.api_response({'status':'success','message':'短信验证码发送成功，请注意查收'})
        else:
            self.api_response({'status':'fail','message':'短信验证码发送失败，请稍后重试'})

class ReplayHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        # 我所有的采购批次
        purchases = self.db.query("select id from purchase where userid = %s", userid)
        unreadquote = 0
        purchaseinfos = []
        quotes = []
        if purchases:
            purchaseinfos = self.db.query(
                "select id from purchase_info where purchaseid in (%s)" % ",".join([str(p["id"]) for p in purchases]))
            # 我的采购单收到的报价
            if purchaseinfos:
                quotes = self.db.query("select id,state from quote where purchaseinfoid in (%s)" % ",".join([str(pi["id"]) for pi in purchaseinfos]))
                unreadquote = 0
                for q in quotes:
                    if q["state"] == 0:
                        unreadquote += 1
        self.render("reply.html", purchaseinfos=purchaseinfos, quotes=quotes, unreadquote=unreadquote)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        userid = self.session.get("userid")
        number = int(self.get_argument("number")) if self.get_argument("number") > 0 else 0
        purchaseinf = defaultdict(list)
        purchases = self.db.query("select id,term,status,createtime from purchase where userid = %s order by createtime desc limit %s,%s", userid, number, config.conf['POST_NUM'])
        if purchases:
            purchaseids = [str(purchase["id"]) for purchase in purchases]
            purchaseinfos = self.db.query(
                "select p.id,p.purchaseid,p.name,p.status,p.specification,q.id qid,count(q.id) quotecount,count(if(q.state=0,true,null )) unreply "
                "from purchase_info p left join quote q on p.id = q.purchaseinfoid where p.purchaseid in (%s) group by p.id"%",".join(purchaseids))
            for purchaseinfo in purchaseinfos:
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
            for purchase in purchases:
                purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
                if purchase["term"] != 0:
                    purchase["expire"] = float(purchase["createtime"]) + purchase["term"]*24*60*60
                    # purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days
            self.api_response({'status': 'success', 'list': purchases, 'message': '请求成功'})
        else:
            self.api_response({'status': 'nomore', 'message': '没有更多的采购订单'})


class ReplayDetailHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        #更新通知状态为已读
        nid = self.get_argument("nid", None)
        if nid:
            self.db.execute("update notification set status = 1 where id = %s", nid)
        userid = self.session.get("userid")
        pid = self.get_argument("pid")
        #查询采购单详细信息包括user,area信息

        purchaseinfo = self.db.get("select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
                                   "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
                                   "pi.views from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s",pid)

        ret = self.db.get("select position from area where id =%s", purchaseinfo["areaid"])
        if ret:
            purchaseinfo["position"] = ret.position
        else:
            purchaseinfo["position"] = ""


        #purchaseinfo = self.db.get("select t.*,a.position,a.parentid from "
        #                           "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
        #                           "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
       #                            "pi.views from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid",
       #                            pid)
        if userid != purchaseinfo["userid"]:
            self.error("这个采购单不属于你哦！","/reply")
        # 获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", pid)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain + attachment["attachment"][
                                                           attachment["attachment"].find("static"):].replace(base,
                                                                                                             base + "_thumb")
        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(purchaseinfo["createtime"])))
        if purchaseinfo["term"] != 0:
            purchaseinfo["expire"] = datetime.datetime.fromtimestamp(
                float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments
        #此采购单收到报价情况
        ordercondition = ",case when q.userid in (SELECT userid from member where type=2) then 4 " \
                         " when q.userid in (SELECT userid from member where type=1) then 3 " \
                         "when q.userid in (SELECT userid from quality_supplier) then 2 " \
                         "else 0 end ordernum "

        quotes = self.db.query("select q.id,userid,q.price,q.quality,q.state,q.message,q.createtime,u.name uname,u.nickname,u.type usertype,u.phone "+ordercondition+
                               "from quote q left join users u on q.userid = u.id where q.purchaseinfoid = %s",pid)
        quoteids = []
        quoteuserids = []
        if quotes:
            for quote in quotes:
                quoteids.append(str(quote.id))
                quoteuserids.append(str(quote.userid))
                quote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(quote["createtime"])))
                quote["unit"] = purchaseinfo["unit"]
            quoteattachments = self.db.query("select * from quote_attachment where quoteid in (" + ",".join(quoteids) + ")")
            myquoteattachments = {}
            for quoteattachment in quoteattachments:
                base, ext = os.path.splitext(os.path.basename(quoteattachment.attachment))
                quoteattachment.attachment = config.img_domain + quoteattachment.attachment[
                                                                 quoteattachment.attachment.find("static"):].replace(
                    base, base + "_thumb")
                if myquoteattachments.has_key(quoteattachment.quoteid):
                    myquoteattachments[quoteattachment.quoteid].append(quoteattachment)
                else:
                    myquoteattachments[quoteattachment.quoteid] = [quoteattachment]

            memberinfos = self.db.query("select * from member where userid in (%s) and type in(1,2)" % ",".join(quoteuserids))
            membermap = dict((m.userid, m.id) for m in memberinfos)

            qualities = self.db.query("select * from quality_supplier where userid in (%s)" % ",".join(quoteuserids))
            qualitymap = dict((i.userid, i.id) for i in qualities)

            for mq in quotes:
                mq.ismember = membermap.get(mq.userid, -1)
                mq.qid = qualitymap.get(mq.userid, -1)

                if myquoteattachments.has_key(mq.id):
                    mq["attachments"] = myquoteattachments[mq.id]
                else:
                    mq["attachments"] = []
        self.render("reply_detail.html", purchase=purchaseinfo, quotes=quotes)

    @tornado.web.authenticated
    def post(self):
        pass

class RemovePurchaseHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        if self.db.query("SELECT count(*) FROM purchase WHERE userid = %s and id = %s", self.session.get("userid"), self.get_argument("pid")):
            self.db.execute("UPDATE purchase SET status = 0 WHERE userid = %s and id = %s", self.session.get("userid"), self.get_argument("pid"))
            self.api_response({'status':'success','message':'请求成功'})
        else:
            self.api_response({'status':'fail','message':'请求失败，此采购订单不属于你'})

class UpdateQuoteStateHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        userid = self.session.get("userid")
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
            purchasesinfos=self.db.query("select q.id,q.price qprice,q.userid quoteuserid ,pi.purchaseid,pi.varietyid,pi.price from"
                                         " quote q left join purchase_info pi on q.purchaseinfoid = pi.id where q.id in (%s)"%qid)
            if purchasesinfos:
                purchaseinfoids=[str(purchasesinfo["purchaseid"]) for purchasesinfo in purchasesinfos]
                purchaseinfoids=list(set(purchaseinfoids))#去重采购单id
                #获取采购单的采购人的信息
                purchases=self.db.query("select p.id,u.phone,u.id userid,u.name,u.nickname from purchase p left join users u on p.userid=u.id where p.id in(%s)"%",".join(purchaseinfoids))
                purchaseuserinfo = dict((i.id,[i.phone,i.userid,i.name,i.nickname]) for i in purchases)
                quoteuserids=[str(purchasesinfo["quoteuserid"]) for purchasesinfo in purchasesinfos]
                #获取报价人的信息
                quoteusers=self.db.query("select id,phone,openid from users where id in (%s)"%",".join(quoteuserids))
                quoteusersinfo=dict((i.id,[i.phone,i.openid]) for i in quoteusers)
                variteyids=[str(purchasesinfo["varietyid"]) for purchasesinfo in purchasesinfos]
                variteyids=list(set(variteyids))#去重品种id
                #获取品种信息
                variteyinfo=self.db.query("select id,name from variety where id in (%s)" %",".join(variteyids))
                variteys = defaultdict(list)
                for item in variteyinfo:
                    variteys[item.id]=item.name
                #封装报价人和采购人的信息
                for purchase in purchasesinfos:
                    purchase["quotephone"] = quoteusersinfo[purchase.quoteuserid][0]
                    purchase["quoteopenid"] = quoteusersinfo[purchase.quoteuserid][1]
                    purchase["variety"]=variteys[purchase.varietyid]
                    purchase["phone"]=purchaseuserinfo[purchase.purchaseid][0]
                    purchase["userid"] = purchaseuserinfo[purchase.purchaseid][1]
                    purchase["name"]=purchaseuserinfo[purchase.purchaseid][2]
                    purchase["nickname"]=purchaseuserinfo[purchase.purchaseid][3]

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
                self.db.execute("update users set pushscore=pushscore+1 where id=%s", purchase["userid"])

                if int(state) == 1:
                    #为供货商积分：
                    self.db.execute("update users set pushscore=pushscore+1 where id=%s", purchase["quoteuserid"])

                    acceptQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, purchase["phone"])
                    acceptQuoteWx(purchase["quoteopenid"], purchase["id"], purchase["name"], purchase["variety"], purchase["qprice"], purchase["nickname"], purchase["phone"], today)
                elif int(state) == 2:
                    rejectQuote(purchase["quotephone"], purchase["name"], purchase["variety"], str(purchase["qprice"]), config.unit, message)
                    rejectQuoteWx(purchase["quoteopenid"], purchase["id"], purchase["name"], purchase["variety"], purchase["qprice"], message, today)
                    pass
            self.db.executemany("insert into notification(sender,receiver,type,title,content,status,createtime)values(%s, %s, %s, %s, %s, %s, %s)",params)
            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})