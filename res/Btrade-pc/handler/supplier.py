#coding:utf8
from base import BaseHandler
from utils import *
import config,re
import os,time
from urllib import urlencode
from alipay import *
import tornado.web
import random
class SupplierHandler(BaseHandler):
    def get(self):
        query = self.get_argument("query", None)
        page = self.get_argument("page", 0)
        page = (int(page) - 1) if page > 0 else 0

        varietyid=""
        if query:
            varieties = self.db.get("select id from variety where name = %s", query)
            if varieties:
                varietyid=varieties["id"]

        user_count=self.db.execute_rowcount("select id from users where type not in(1,2,9)")
        supplier_count=self.db.execute_rowcount("select id from supplier where pushstatus!=2")
        total=user_count+supplier_count
        membernum=self.db.execute_rowcount("select id from member where type=2")

        suppliers=[]
        conditionu=""
        conditions=""
        if varietyid!="":
            conditionu=" and find_in_set(%s,varietyids)"%(varietyid)
            conditions=" and find_in_set(%s,variety)"%(varietyid)
        ordercondition=",case when id in (SELECT userid from member where type=2) then 4 " \
                       " when id in (SELECT userid from member where type=1) then 3 " \
                       "when id in (SELECT userid from quality_supplier) then 2 " \
                       "when id in (select q.userid from transaction t left join quote q on t.quoteid=q.id) then 1 " \
                       "else 0 end ordernum "#优先显示药销通会员和认证的，其次是有交易记录的

        usersnum=self.db.execute_rowcount("select id from users where type not in(1,2,9) %s"%conditionu)
        suppliernum=self.db.execute_rowcount("select id from supplier where pushstatus!=2 %s"%conditions)
        #分页中一部分显示user一部分显示supplier
        if (page+1) * config.conf['POST_NUM']>usersnum and page* config.conf['POST_NUM']<usersnum:
             t1=self.db.query("select * "+ordercondition+"from users where type not in(1,2,9) %s"%conditionu+" order by ordernum desc limit %s,%s",
                                          page * config.conf['POST_NUM'], config.conf['POST_NUM'])
             for item in t1:
                 supplier={"userid":item["id"],"name":item["name"],"variety":item["varietyids"],"introduce":item["introduce"]}
                 suppliers.append(supplier)
             t2 = self.db.query("select * from supplier where pushstatus!=2 %s"%conditions+"limit %s,%s",
                                          0, (page+1) * config.conf['POST_NUM']-usersnum)
             for item in t2:
                 if item["name"]!="":
                     name=item["name"]
                 else:
                     name=item["company"]
                 supplier={"userid":-1,"name":name,"variety":item["variety"],"introduce":""}
                 suppliers.append(supplier)
        #分页只显示user或只显示supplier
        else :
            if (page+1) * config.conf['POST_NUM']<=usersnum:
                t1 = self.db.query("select * "+ordercondition+" from users where type not in(1,2,9) %s"%conditionu+" order by ordernum desc limit %s,%s",
                                          page * config.conf['POST_NUM'], config.conf['POST_NUM'])
                for item in t1:
                    supplier = {"userid": item["id"], "name": item["name"], "variety": item["varietyids"],
                            "introduce": item["introduce"]}
                    suppliers.append(supplier)
            else:
                t2 = self.db.query("select * from supplier where  pushstatus!=2 %s"%conditions+"limit %s,%s",
                                          page * config.conf['POST_NUM']-usersnum, config.conf['POST_NUM'])
                for item in t2:
                    if item["name"] != "":
                        name = item["name"]
                    else:
                        name = item["company"]
                    supplier = {"userid": -1, "name": name, "variety": item["variety"], "introduce": ""}
                    suppliers.append(supplier)
        for item in suppliers:
            variety_list = item["variety"].split(",")
            vl=[]
            for v in variety_list:
                if v!="":
                    vl.append(v)
            supply_variety_name = []
            if vl!=[]:
                ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
                for r in ret:
                    supply_variety_name.append(r.name)
            item["supply_variety_name"]=supply_variety_name
            if item["userid"]!=-1:
                member=self.db.get("select * from member where userid=%s and type in (1,2)",item["userid"])
                if member:
                    item["ismember"]=1
                else:
                    item["ismember"] = 0
                quality_supplier=self.db.get("select * from quality_supplier where userid=%s",item["userid"])
                if quality_supplier:
                    item["isquality"]=1
                    item["qid"]=quality_supplier["id"]
                else:
                    item["isquality"] = 0
                    item["qid"]=-1

                quotids = self.db.query("select id from quote where userid=%s", item["userid"])
                transactions = []
                if quotids:
                    quotids = [str(q["id"]) for q in quotids]
                    transactions = self.db.query(
                        "select id,purchaseinfoid,quoteid,quantity,unity,price,total,createtime from transaction where status=1 and quoteid in (%s)" % ",".join(
                            quotids))
                    if transactions:
                        purchaseinfoids = [str(t["purchaseinfoid"]) for t in transactions]
                        purchaseinfos = self.db.query(
                            "select p.userid,pi.id, pi.name,pi.specification from purchase_info pi left join purchase p on pi.purchaseid=p.id where pi.id in(%s)" % ",".join(
                                purchaseinfoids))
                        puserids = [str(p["userid"]) for p in purchaseinfos]
                        purchaseinfomap = dict((i.id, [i.userid, i.name, i.specification]) for i in purchaseinfos)

                        puserinfos = self.db.query(
                            "select id, name,nickname from users where id in (%s)" % ",".join(puserids))
                        pusermap = dict((i.id, [i.name, i.nickname]) for i in puserinfos)

                        for transac in transactions:
                            transac["varietyname"] = purchaseinfomap[transac["purchaseinfoid"]][1]
                            transac["specification"] = purchaseinfomap[transac["purchaseinfoid"]][2]
                            transac["purchasename"] = pusermap[purchaseinfomap[transac["purchaseinfoid"]][0]][0]
                            transac["purchasenick"] = pusermap[purchaseinfomap[transac["purchaseinfoid"]][0]][1]
                            transac["createtime"] = time.strftime("%Y-%m-%d", time.localtime(float(transac["createtime"])))
                item["quote"]=len(quotids)
                item["transactions"]=transactions
            else:
                item["ismember"] = 0
                item["isquality"] = 0
                item["qid"] = -1
                item["quote"] =0
                item["transactions"] =[]
        query_str={}
        if query:
            query_str["query"] = query.encode('utf8')
        nav = {
            'model': 'supplier',
            'cur': page + 1,
            'num': usersnum+suppliernum,
            'query': "%s" % urlencode(query_str),
            'total':usersnum+suppliernum,
        }
        #热门品种
        hot=self.db.query("select varietyid ,name,count(varietyid) as num from purchase_info group by varietyid order by num desc limit 0,10")
        hot=[h.name for h in hot]

        #供货排行榜
        rankuser=self.db.query("select q.userid,count(q.userid) as count from transaction t left join quote q on t.quoteid=q.id group by q.userid order by count desc limit 0,10 ")
        userids=[str(u.userid) for u in rankuser]
        userinfos = self.db.query(
            "select id, name,nickname from users where id in (%s)" % ",".join(userids))
        usermap = dict((i.id, [i.name, i.nickname]) for i in userinfos)

        quanlityinfos = self.db.query("select id,userid from quality_supplier where userid in (%s)" % ",".join(userids))
        quanlitymap=dict((i.userid, i.id) for i in quanlityinfos)

        memberinfos=self.db.query("select * from member where userid in (%s) and type in(1,2)" % ",".join(userids))
        membermap=dict((i.userid, i.id) for i in memberinfos)

        for rank in rankuser:
            rank.name=usermap[rank.userid][0]
            rank.qid=quanlitymap.get(rank.userid,-1)
            rank.member= membermap.get(rank.userid, -1)

        self.render("supplier_list.html",query=query,total=total,membernum=membernum,suppliers=suppliers,nav=nav,hot=hot,rankuser=rankuser)

    def post(self):
        pass

class SupplierDetailHandler(BaseHandler):
    def get(self):
        qid=self.get_argument("qid", "")
        user=None
        transactions=None
        quanlity = self.db.get("select * from quality_supplier where id=%s", qid)
        if quanlity==None:
            self.error(u"没找到该用户","/supplier")
            return
        else:
            user=self.db.get("select id,name,nickname,varietyids,scale,introduce from users where id=%s",quanlity["userid"])
            variety_list = user.varietyids.split(",")
            vl=[]
            for v in variety_list:
                if v!="":
                    vl.append(v)
            supply_variety_name=[]
            if vl!=[]:
                ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
                for r in ret:
                    supply_variety_name.append(r.name)
            user.supply_variety_name = supply_variety_name
            quotids=self.db.query("select id from quote where userid=%s",quanlity["userid"])
            if quotids:
                quotids=[str(item["id"]) for item in quotids]
                transactions =self.db.query("select id,purchaseinfoid,quoteid,quantity,unity,price,total,createtime from transaction where status=1 and quoteid in (%s)"%",".join(quotids))
                if transactions:
                    purchaseinfoids = [str(item["purchaseinfoid"]) for item in transactions]
                    purchaseinfos = self.db.query(
                        "select p.userid,pi.id, pi.name,pi.specification from purchase_info pi left join purchase p on pi.purchaseid=p.id where pi.id in(%s)" % ",".join(
                            purchaseinfoids))
                    puserids = [str(item["userid"]) for item in purchaseinfos]
                    purchaseinfomap = dict((i.id, [i.userid, i.name, i.specification]) for i in purchaseinfos)

                    puserinfos = self.db.query(
                        "select id, name,nickname from users where id in (%s)" % ",".join(puserids))
                    pusermap = dict((i.id, [i.name, i.nickname]) for i in puserinfos)



                    for item in transactions:
                        item["varietyname"] = purchaseinfomap[item["purchaseinfoid"]][1]
                        item["specification"] = purchaseinfomap[item["purchaseinfoid"]][2]
                        item["purchasename"] = pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][0]
                        item["purchasenick"] = pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][1]
                        item["createtime"] = time.strftime("%Y-%m-%d", time.localtime(float(item["createtime"])))

                        transactionattachments = self.db.query(
                            "select * from transaction_attachment where transaction_id=%s", item["id"])
                        for attachment in transactionattachments:
                            base, ext = os.path.splitext(os.path.basename(attachment.attachment))
                            attachment.attachment = config.img_domain + attachment.attachment[
                                                                        attachment.attachment.find("static"):].replace(
                                base,
                                base + "_thumb")
                        item["attachments"] = transactionattachments

            varietyimg = self.db.query(
                "select * from quality_attachment where quality_id=%s and type=2", quanlity["id"])
            for qualityattachment in varietyimg:
                base, ext = os.path.splitext(os.path.basename(qualityattachment.attachment))
                qualityattachment.attachment = config.img_domain + qualityattachment.attachment[
                                                                   qualityattachment.attachment.find(
                                                                     "static"):].replace(base, base + "_thumb")
            quanlity["varietyimg"] = varietyimg

            otherimg = self.db.query(
                "select * from quality_attachment where quality_id=%s and type=3", quanlity["id"])

            for qualityattachment in otherimg:
                base, ext = os.path.splitext(os.path.basename(qualityattachment.attachment))
                qualityattachment.attachment = config.img_domain + qualityattachment.attachment[
                                                                   qualityattachment.attachment.find(
                                                                     "static"):].replace(base, base + "_thumb")
            quanlity["otherimg"] = otherimg
        self.render("supplier.html",quanlity=quanlity,user=user,transactions=transactions)
    def post(self):
        pass

class PaymentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user=self.db.get("select * from users where id=%s",self.session.get("userid"))
        self.render("payment.html",user=user)
        pass
    def post(self):
        userid=self.session.get("userid")
        name=self.get_argument("name",None)
        if name:
            if name=="alipay":
                rand = ''.join(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 4))
                payid=time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))+rand
                tn = payid
                #插入一条交易记录
                self.db.execute(
                    "insert into payment (userid,paytype,paymode,money,payid,createtime) value(%s,%s,%s,%s,%s,%s)", userid,
                    1, 1,config.deposit,payid,int(time.time()) )
                subject = u'（药材购）阳光速配诚信保证金'
                body = ''
                bank = ""
                tf = '%.2f' % config.deposit
                url = create_direct_pay_by_user(tn, subject, body, bank, tf)

                self.api_response({'status': 'success', 'url': url })
        else:
            self.api_response({'status': 'fail', 'message': '不支持的支付方式'})
        pass

class AlipayReturnHandler(BaseHandler):
    def get(self):
        params=self.request.arguments
        ks = params.keys()
        newparams = {}
        for k in ks:
            v = params[k][0]
            newparams[k]=v
        if notify_verify(newparams):
            tn = self.get_argument('out_trade_no')
            trade_no = self.get_argument('trade_no')
            trade_status = self.get_argument('trade_status')

            if trade_status == 'TRADE_SUCCESS':#支付成功
                self.db.execute("update payment set status=%s,tradeno=%s where payid=%s",1,trade_no,tn)
                payment=self.db.get("select * from payment where payid=%s",tn)
                if payment:
                    userid=payment["userid"]
                    status=payment["status"]
                    membertype=2
                    if payment.paytype == 1:
                        membertype=3
                    elif payment.paytype == 2:
                        membertype = 2
                    if status==1:
                        member = self.db.get("select * from member where userid=%s", userid)
                        if member==None:
                            self.db.execute(
                                "insert into member (userid,term,upgradetime,type,expiredtime) value(%s,%s,%s,%s,%s)",
                                userid, 0, int(time.time()),membertype,"")

            else:
                self.db.execute("update payment set status=%s,tradeno=%s where payid=%s",0, trade_no, tn)
        self.redirect("/sunshine")
        pass

class SunshineHandler(BaseHandler):
    def get(self):
        memberinfo=None
        membernum=self.db.execute_rowcount("select * from member where type=3")
        if self.session.has_key('user'):
            userid = self.session.get("userid")
            memberinfo=self.db.get("select * from member where userid=%s and type=3",userid)
            if memberinfo:
                purchasesinfocout = self.db.execute_rowcount(
                    "select * from purchase p  left join purchase_info pi on p.id=pi.purchaseid where userid = %s ",
                    userid)
                memberinfo.purchasesinfonum=purchasesinfocout
                #payment=self.db.get("select * from payment where userid=%s and status=1",userid)

        query = self.get_argument("query", None)
        page = self.get_argument("page", 0)
        page = (int(page) - 1) if page > 0 else 0

        varietyid=""
        if query:
            varieties = self.db.get("select id from variety where name = %s", query)
            if varieties:
                varietyid=varieties["id"]

        user_count=self.db.execute_rowcount("select id from users where type not in(1,2,9)")
        supplier_count=self.db.execute_rowcount("select id from supplier where pushstatus!=2")
        total=user_count+supplier_count
        suppliers=[]
        conditionu=""
        if varietyid!="":
            conditionu=" and find_in_set(%s,varietyids)"%(varietyid)

        ordercondition = ",case when id in (SELECT userid from member where type=2) then 4 " \
                         " when id in (SELECT userid from member where type=1) then 3 " \
                         "else 0 end ordernum "  # 优先显示药销通会员和认证的，其次是有交易记录的
        suppliers = self.db.query(
            "select id as userid,name,varietyids as variety " + ordercondition + "from users where id in (SELECT userid from member where type in(1,2)) %s" % conditionu + " order by ordernum desc limit %s,%s",
            page * config.conf['POST_NUM'], config.conf['POST_NUM'])

        for item in suppliers:
            variety_list = item["variety"].split(",")
            vl=[]
            for v in variety_list:
                if v!="":
                    vl.append(v)
            supply_variety_name = []
            if vl!=[]:
                ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
                for r in ret:
                    supply_variety_name.append(r.name)
            item["supply_variety_name"]=supply_variety_name
            member=self.db.get("select * from member where userid=%s and type in (1,2)",item["userid"])
            if member:
                item["ismember"]=1
            else:
                item["ismember"] = 0
            quality_supplier=self.db.get("select * from quality_supplier where userid=%s",item["userid"])
            if quality_supplier:
                item["isquality"]=1
                item["qid"]=quality_supplier["id"]
            else:
                item["isquality"] = 0
                item["qid"]=-1

            quotids = self.db.query("select id from quote where userid=%s", item["userid"])
            acceptnum=self.db.execute_rowcount("select id from quote where userid=%s and state=1", item["userid"])
            item["acceptnum"]=acceptnum
            transactions = []
            if quotids:
                quotids = [str(q["id"]) for q in quotids]
                transactions = self.db.query(
                        "select * from transaction where status=1 and quoteid in (%s)" % ",".join(
                            quotids))
                if transactions:
                    purchaseinfoids = [str(t["purchaseinfoid"]) for t in transactions]
                    purchaseinfos = self.db.query(
                            "select p.userid,pi.id, pi.name,pi.specification from purchase_info pi left join purchase p on pi.purchaseid=p.id where pi.id in(%s)" % ",".join(
                                purchaseinfoids))
                    puserids = [str(p["userid"]) for p in purchaseinfos]
                    purchaseinfomap = dict((i.id, [i.userid, i.name, i.specification]) for i in purchaseinfos)

                    puserinfos = self.db.query(
                            "select id, name,nickname from users where id in (%s)" % ",".join(puserids))
                    pusermap = dict((i.id, [i.name, i.nickname]) for i in puserinfos)

                    for transac in transactions:
                        transac["varietyname"] = purchaseinfomap[transac["purchaseinfoid"]][1]
                        transac["specification"] = purchaseinfomap[transac["purchaseinfoid"]][2]
                        transac["purchasename"] = pusermap[purchaseinfomap[transac["purchaseinfoid"]][0]][0]
                        transac["purchasenick"] = pusermap[purchaseinfomap[transac["purchaseinfoid"]][0]][1]
                        transac["createtime"] = time.strftime("%Y-%m-%d", time.localtime(float(transac["createtime"])))
            item["quote"]=len(quotids)
            item["transactions"]=transactions
            img = self.db.query(
                    "select * from quality_attachment where quality_id=%s and type in (2,3)", item["qid"])
            for qualityattachment in img:
                base, ext = os.path.splitext(os.path.basename(qualityattachment.attachment))
                qualityattachment.attachment = config.img_domain + qualityattachment.attachment[
                                                                       qualityattachment.attachment.find(
                                                                           "static"):].replace(base, base + "_thumb")
            item["attachment"]=img
        query_str={}
        if query:
            query_str["query"] = query.encode('utf8')
        num=self.db.execute_rowcount("select id from users where id in (SELECT userid from member where type=1)")
        nav = {
            'model': 'sunshine',
            'cur': page + 1,
            'num': num,
            'query': "%s" % urlencode(query_str),
        }

        #开通品种
        hot=self.db.query("select id ,name from variety where state=1")
        if hot:
            hot=[h.name for h in hot]
        else:
            hot=[]

        #最新交易意向
        newpurchaseinfo=self.db.query("select pi.id, pi.name,pi.quantity,pi.purchaseid,q.userid as quserid,q.updatetime from purchase_info pi  left join quote q on q.purchaseinfoid=pi.id where q.state=1 order by q.updatetime desc limit 0,10")
        purchaseids=[]
        quserids=[]
        for p in newpurchaseinfo:
            if p["purchaseid"] not in purchaseids:
                purchaseids.append(str(p["purchaseid"]))
            if p["quserid"] not in quserids:
                quserids.append(str(p["quserid"]))
        purchaseusers=self.db.query("select p.id,u.name from purchase p left join users u on p.userid=u.id where p.id in(%s)"%",".join(purchaseids))
        purchaseusermap = dict((i.id, i.name) for i in purchaseusers)
        quoteusers=self.db.query("select id,name from users where id in(%s)"%",".join(quserids))
        quoteusermap= dict((i.id, i.name) for i in quoteusers)
        for p in newpurchaseinfo:
            p["purchaseusername"]=purchaseusermap[p["purchaseid"]]
            p["quoteusername"]=quoteusermap[p["quserid"]]
            p["time"]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(p["updatetime"])))








        self.render("sunshine.html",member=memberinfo,hot=hot,nav=nav,suppliers=suppliers,query=query,total=total,newpurchaseinfo=newpurchaseinfo,membernum=membernum)