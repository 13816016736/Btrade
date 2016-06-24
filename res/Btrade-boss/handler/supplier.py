# -*- coding: utf-8 -*-
import tornado.web
from base import BaseHandler
class SupplierHandler(BaseHandler):
       @tornado.web.authenticated
       def get(self,page=0):
           search_str=self.get_argument("search",None)
           variety_name=self.get_argument("variety",None)
           page = (int(page) - 1) if page > 0 else 0
           search_condition = []
           if variety_name:
               varieties = self.db.query("select id from variety where name = %s or find_in_set(%s,alias)", variety_name,variety_name)
               if len(varieties)==1:
                   search_condition.append("find_in_set(%s,variety)" + varieties[0].id)
               else:
                   # 返回查询不到的页面
                   pass

           search_condition=[]
           if search_str:
               search_condition.append("CONCAT('name','company','mobile') like %%%s%%" + search_str)

           page_show_num=6

           conditionstr = ""
           if search_condition:
               conditionstr = ("where " + (" and ".join(search_condition)))
           suppliers=self.db.query("select * from supplier" + conditionstr+" order by createtime desc limit %s, %s",
                                   page *  page_show_num, page_show_num)
           querystr=[]
           if search_str:
               querystr.append("search_str=%s"%search_str)
           if variety_name:
                querystr.append("variety_name=%s" % variety_name)
           if querystr:
                nav = {
                    'model': '/supplier/supplierlist/',
                    'cur': page + 1,
                    'num': self.db.execute_rowcount("select * from purchase supplier " + conditionstr),
                    'query':"?" +"&".join(querystr)
                }
           else:
               nav = {
                   'model': 'supplier/supplierlist',
                   'cur': page + 1,
                   'num': self.db.execute_rowcount("select * from purchase supplier " + conditionstr),
               }

           self.render("supplier.html",suppliers=suppliers,nav=nav,search_str=search_str,variety_name=variety_name)

class SupplierInsertHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("supplier.html")

class SupplierDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("supplier_detail.html")
