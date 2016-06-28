# -*- coding: utf-8 -*-
import tornado.web
from base import BaseHandler
import json
from urllib import urlencode
class SupplierHandler(BaseHandler):
       @tornado.web.authenticated
       def get(self):
           search_str=self.get_argument("search",None)
           variety_name=self.get_argument("variety",None)
           page=self.get_argument("page",None)
           if page==None:
               page=1
           else:
               page=int(page)
           search_condition = []
           if search_str:
               search_condition.append("CONCAT(supplier.name,supplier.company,supplier.mobile) like '%%%%%s%%%%'" % search_str)
           if variety_name:
               varieties = self.db.query("select id from variety where name = %s or find_in_set(%s,alias)",
                                         variety_name, variety_name)
               if len(varieties) == 1:
                   search_condition.append("find_in_set(%s,variety)" % varieties[0].id)
               else:
                   # 返回查询不到的页面
                   search_condition.append("find_in_set(%s,variety)" % -1)
                   pass
           page_show_num=10
           conditionstr = ""
           if search_condition:
               conditionstr = ("where " + (" and ".join(search_condition)))
           #print conditionstr
           suppliers=self.db.query("select * from supplier "+conditionstr+" order by createtime desc limit %s, %s",
                                   (page-1)*page_show_num, page_show_num)
           for item in suppliers:
               variety_list=item.variety.split(",")
               vl=[]
               for v in variety_list:
                   if(v!=""):
                        vl.append(str(v))
               ret=self.db.query("select name from variety where id in (%s) "%','.join(vl))
               supply_variety_name=[]
               for r in ret:
                   supply_variety_name.append(r.name)
               item["supply_variety_name"]=supply_variety_name

           querystr={}
           if search_str:
               querystr["search"]=search_str.encode('utf8')
           if variety_name:
               querystr["variety"] = variety_name.encode('utf8')
           result_num=self.db.execute_rowcount("select * from  supplier " + conditionstr)
           page_num=0
           if result_num%page_show_num==0:
               page_num= (result_num/page_show_num)
           else:
               page_num = (result_num/page_show_num)+1
           if querystr!={}:
                nav = {
                    'model': 'supplier/supplierlist',
                    'cur': page,
                    'num': result_num,
                    'query':urlencode(querystr),
                    'style':0,
                    'total': result_num
                }
           else:
               nav = {
                   'model': 'supplier/supplierlist',
                   'cur': page,
                   'num': result_num,
                   'style': 0,
                   'total':result_num
               }

           if search_str==None:
               search_str=""
           if variety_name == None:
               variety_name = ""
           self.render("supplier.html",suppliers=suppliers,nav=nav,search_str=search_str,variety_name=variety_name)

class SupplierInsertHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",None)
        sponsor=None
        if id:
            sponsor=self.db.get("select * from users where id=%s",id)
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 100000")
        cities=self.db.query("SELECT id,areaname FROM area WHERE parentid = %s",provinces[0].id)#默认取第一个省份的城市
        self.render("supplier_add.html",provinces=provinces ,cities=cities,sponsor=sponsor)
    def post(self):
        data=self.get_argument("data",None)
        if data:
            user=json.loads(data)
            #print user
            mobile=user["mobile"]
            name=user["linkman"]
            varietys=user["varietys"]
            company = user["name"]
            businessplace=user["province"]+','+user["city"]
            if user.has_key("address"):
                address=user["address"]
            else:
                address =""
            if user.has_key("scale"):
                scale=user["scale"]
            else:
                scale =""
            if user.has_key("tel"):
                phone = user["tel"]
            else:
                phone= ""
            if user.has_key("remark"):
                remark = user["remark"]
            else:
                remark= ""
            if  self.session["adminid"]:
                record =self.session["adminid"]
            else:
                record = ""
            if user.has_key("note"):
                sponsor = int(user["note"])
            else:
                sponsor= 0
            if sponsor==0:
                source="manual_record"
            else:
                source = "manual_recommend"
            try:
                lastrowid = self.db.execute_lastrowid(
                "insert into supplier (mobile, variety, company, name,businessplace,address,scale,phone,remark,record,sponsor,source)"
                    "value(%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)",
                    mobile, varietys, company, name,businessplace,address,scale,phone,remark,record,sponsor,source)
                self.api_response({'status': 'success', 'message': '添加供应商成功', 'supplier': {'current_id': lastrowid,"last_id":sponsor}})
            except Exception,ex:
                self.api_response({'status': 'success', 'message': '添加供应商失败（str(ex)）'})






class SupplierEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",None)
        sponsor=None
        if id:
            supplier=self.db.get("select * from supplier where id=%s",id)
            if supplier:
                sponsor_id=supplier.sponsor
                if sponsor_id!=0:
                    sponsor=self.db.get("select * from users where id=%s",sponsor_id)
                provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 100000")
                if supplier.businessplace!="":
                    business=supplier.businessplace.split(",")
                    cities = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", business[0])
                else:
                    cities = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", provinces[0].id)

                variety_list = supplier.variety.split(",")
                vl = []
                for v in variety_list:
                    if (v != ""):
                        vl.append(str(v))
                supply_variety_name = self.db.query("select name,id from variety where id in (%s) " % ','.join(vl))
                supplier["supply_variety_name"] = supply_variety_name
                if supplier.record:
                    ret=self.db.get("select username from admin where id=%s",supplier.record)
                    if ret:
                        supplier["record_name"]=ret.username
                    else:
                        supplier["record_name"] =""
                else:
                    supplier["record_name"] = ""
                self.render("supplier_edit.html",provinces=provinces ,cities=cities,sponsor=sponsor,supplier=supplier)
            else:
                self.send_error(404)
        else:
            self.send_error(404)
    def post(self):
        data=self.get_argument("data",None)
        if data:
            user=json.loads(data)
            mobile=user["mobile"]
            name=user["linkman"]
            varietys=user["varietys"]
            company = user["name"]
            businessplace=user["province"]+','+user["city"]
            if user.has_key("address"):
                address=user["address"]
            else:
                address =""
            if user.has_key("scale"):
                scale=user["scale"]
            else:
                scale =""
            if user.has_key("tel"):
                phone = user["tel"]
            else:
                phone= ""
            if user.has_key("remark"):
                remark = user["remark"]
            else:
                remark= ""
            try:
                self.db.execute(
                "update supplier set mobile=%s, variety=%s, company=%s, name=%s,businessplace=%s,address=%s,scale=%s,phone=%s,remark=%s where id=%s",
                    mobile, varietys, company, name,businessplace,address,scale,phone,remark,user["id"])
                self.api_response({'status': 'success', 'message': '修改供应商成功'})
            except Exception,ex:
                self.api_response({'status': 'success', 'message': '修改供应商失败（str(ex)）'})




class SupplierResultHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        current_id=self.get_argument("current_id",None)
        last_id=self.get_argument("last_id",None)
        rtype=self.get_argument("rtype",None)
        if current_id:
            current_id=int(current_id)
        else:
            current_id=0
        if last_id:
            last_id=int(last_id)
        else:
            last_id=0
        self.render("supplier_result.html",current_id=current_id,last_id=last_id,rtype=rtype)



class SupplierDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        supplier_id = self.get_argument("id", None)
        if supplier_id:
            supplier=self.db.get("select * from supplier where id = %s" ,supplier_id)
            if supplier:
                variety_list = supplier.variety.split(",")
                vl = []
                for v in variety_list:
                    if (v != ""):
                        vl.append(str(v))
                ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
                supply_variety_name = []
                for r in ret:
                    supply_variety_name.append(r.name)
                supplier["supply_variety_name"] = supply_variety_name
                if supplier.sponsor!=None:
                    sponsor = self.db.get("select * from users where id = %s", supplier.sponsor)
                    if sponsor:
                        sponsor_name=sponsor.name+ '(%s)'%sponsor.nickname
                        supplier["sponsor_name"] = sponsor_name
                    else:
                        supplier["sponsor_name"]=""
                if supplier.businessplace!="":
                   pos=supplier.businessplace.split(',')
                   area = self.db.query("select areaname from area where id in(%s)"%','.join(pos))
                   businessplace_name=[]
                   for item in area:
                       businessplace_name.append(item.areaname)
                   supplier["businessplace_name"] = businessplace_name
                else:
                   supplier["businessplace_name"] = []
                if supplier.record:
                    ret=self.db.get("select username from admin where id=%s",supplier.record)
                    if ret:
                        supplier["record_name"]=ret.username
                    else:
                        supplier["record_name"] =""
                else:
                    supplier["record_name"] = ""
                self.render("supplier_detail.html",supplier=supplier)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

class SupplierMobileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        mobile=self.get_argument("mobile",None)
        if mobile:
            supplier = self.db.get("select * from supplier where mobile = %s", mobile)
            self.api_response({"status":"success","supplier":supplier})
        else:
            self.api_response({"data":"没有mobile参数","status":"fail"})
class SupplierSearchHandler(BaseHandler):#改为用户查询
    @tornado.web.authenticated
    def get(self):
        search=self.get_argument("search",None)
        if search:
            suppliers= self.db.query("select * from users where CONCAT(users.name,users.phone,users.nickname) like '%%%%%s%%%%' limit 0,10"% search)
            if len(suppliers)!=0:
                self.api_response({"status":"success","suppliers":suppliers})
            else:
                self.api_response({"status": "null", "suppliers": suppliers})
        else:
            self.api_response({"data":"参数不能为空","status":"fail"})
class SupplierAreaHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        parentId=self.get_argument("parentId",None)
        if parentId:
            area=self.db.query("select * from area where parentid=%s",parentId)
            self.api_response({"status": "success", "area": area})
        else:
            self.api_response({"data": "parentId不能为空", "status": "fail"})
class SupplierVarietyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        varietyName=self.get_argument("varietyName",None)
        if varietyName:
            varieties=self.db.query("select * from variety where name like '%%%%%s%%%%' or find_in_set('%s',alias)" %(varietyName,varietyName))
            if len(varieties)!=0:
                self.api_response({"status": "success", "varieties": varieties})
            else:
                self.api_response({"status": "notsupport", "varieties": varieties})
        else:
            self.api_response({"data": "varietyName不能为空", "status": "fail"})
