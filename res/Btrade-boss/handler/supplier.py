# -*- coding: utf-8 -*-
import tornado.web
from base import BaseHandler
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
               search_condition.append("CONCAT(name,company,mobile) like '%%%%%s%%%%'" % search_str)
           if variety_name:
               varieties = self.db.query("select id from variety where name = %s or find_in_set(%s,alias)",
                                         variety_name, variety_name)
               if len(varieties) == 1:
                   search_condition.append("find_in_set(%s,variety)" % varieties[0].id)
               else:
                   # 返回查询不到的页面
                    pass
           page_show_num=6
           conditionstr = ""
           if search_condition:
               conditionstr = ("where " + (" and ".join(search_condition)))
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

           querystr=[]
           if search_str:
               querystr.append("search=%s"%search_str)
           if variety_name:
                querystr.append("variety=%s" % variety_name)
           if querystr:
                nav = {
                    'model': 'supplier/supplierlist',
                    'cur': page,
                    'num': self.db.execute_rowcount("select * from  supplier " + conditionstr),
                    'query':"&".join(querystr)
                }
           else:
               nav = {
                   'model': 'supplier/supplierlist',
                   'cur': page,
                   'num': self.db.execute_rowcount("select * from  supplier " + conditionstr),
               }

           if search_str==None:
               search_str=""
           if variety_name == None:
               variety_name = ""
           self.render("supplier.html",suppliers=suppliers,nav=nav,search_str=search_str,variety_name=variety_name)

class SupplierInsertHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("supplier.html")

class SupplierDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("supplier_detail.html")
