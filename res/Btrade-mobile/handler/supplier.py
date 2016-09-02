#coding:utf8
from base import BaseHandler
from utils import *
import config,re
import os,time
from urllib import urlencode
import tornado.web
import random
from wxpay import *
#import requests
import logging
from webbasehandler import purchase_push_trace

class SupplierDetailHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        qid=self.get_argument("qid", "")
        user=None
        transactions=None
        quanlity = self.db.get("select * from quality_supplier where id=%s", qid)
        if quanlity==None:
            self.error(u"没找到该用户","/")
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

class SunshineHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        pid=self.get_argument("pid", None)
        next="/"
        if pid:
            next="/purchase/purchaseinfo/%s"%pid
        memberinfo = None
        if self.session.has_key('user'):
            userid = self.session.get("userid")
            memberinfo = self.db.get("select * from member where userid=%s and type=2 and status=1", userid)#阳光匹配供货商
        #开通品种
        hot=self.db.query("select id ,name from variety where state=1")
        if hot:
            hot=[h.name for h in hot]
        else:
            hot=[]
        self.render("sunshine.html",memberinfo=memberinfo,hot=hot,next=next)
        pass

class PaymentHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        pass
    def post(self):
        userid=self.session.get("userid")
        user=self.db.get("select id,openid from users where id=%s",userid)
        rand = ''.join(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 4))
        payid=time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))+rand
        #插入一条交易记录
        self.db.execute(
                "insert into payment (userid,paytype,paymode,money,payid,createtime) value(%s,%s,%s,%s,%s,%s)", userid,
                2, 2,config.sdeposit,payid,int(time.time()) )
        body=u"速采科技-保证金"
        money = int(float(config.sdeposit) * 100)

        jsApi = JsApi_pub()
        unifiedOrder = UnifiedOrder_pub()
        unifiedOrder.setParameter("openid", user.openid)  # 商品描述
        unifiedOrder.setParameter("body", body)  # 商品描述
        #timeStamp = time.time()
        out_trade_no = payid
        unifiedOrder.setParameter("out_trade_no", out_trade_no)  # 商户订单号
        unifiedOrder.setParameter("total_fee", str(money))  # 总金额
        unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL)  # 通知地址
        unifiedOrder.setParameter("trade_type", "JSAPI")  # 交易类型
        #unifiedOrder.setParameter("attach", "支付测试")  # 附件数据，可分辨不同商家(string(127))
        jsApiParameters=""
        try:
            prepay_id = unifiedOrder.getPrepayId()
            jsApi.setPrepayId(prepay_id)
            jsApiParameters = jsApi.getParameters()
        except Exception as e:
            logging.info(e)

        self.api_response({'status': 'success', 'params': jsApiParameters})

        pass