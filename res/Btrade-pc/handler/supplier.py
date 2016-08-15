#coding:utf8
from base import BaseHandler
from utils import *
import config,re
import os,time
from urllib import urlencode
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
        usersnum=self.db.execute_rowcount("select id from users where type not in(1,2,9) %s"%conditionu)
        suppliernum=self.db.execute_rowcount("select id from supplier where pushstatus!=2 %s"%conditions)
        if (page+1) * config.conf['POST_NUM']>usersnum and page* config.conf['POST_NUM']<usersnum:
             t1=self.db.query("select * from users where type not in(1,2,9) %s"%conditionu+" limit %s,%s",
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
        else :
            if (page+1) * config.conf['POST_NUM']<usersnum:
                t1 = self.db.query("select * from users where type not in(1,2,9) %s"%conditionu+" limit %s,%s",
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
                member=self.db.get("select * from member where userid=%s and type=2",item["userid"])
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
        }


        self.render("supplier_list.html",query=query,total=total,membernum=membernum,suppliers=suppliers,nav=nav)

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
        else:
            user=self.db.get("select id,name,nickname,varietyids,scale,introduce from users where id=%s",quanlity["userid"])
            variety_list = user.varietyids.split(",")
            vl=[]
            for v in variety_list:
                if v!="":
                    vl.append(v)
            ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
            supply_variety_name = []
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
