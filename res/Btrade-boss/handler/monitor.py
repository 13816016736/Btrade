# -*- coding: utf-8 -*-
import tornado.web
from base import BaseHandler
import config
from time import strftime, localtime
from datetime import timedelta,datetime
import time
from utils import *

class MonitorStatisticsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,month):
        year = strftime("%Y", localtime())
        if int(month)<=12 and int(month)>=0:
            if month=='0':
                month = strftime("%m", localtime())
            format = "%Y-%m-%d";
            date_str="%s-%s-%s"%(year,month,'1')
            dt=datetime.strptime(date_str, format)
            dayOfWeek = dt.weekday()
            print dayOfWeek
            # 偶数月显示带上个月的那周，奇熟月份只显示本月的
            regions = []
            start_date=""
            format_regions = []
            if int(month)%2==0:
                start_date=dt+timedelta(days=(-1*(dayOfWeek)))
                for i in range(0,5):
                    end_date = start_date + timedelta(days=6)
                    region={"start_time":start_date.strftime("%Y-%m-%d"),"end_time":end_date.strftime("%Y-%m-%d")}
                    regions.append(region)
                    region = {"start_time": start_date.strftime("%m.%d"), "end_time": end_date.strftime("%m.%d")}
                    format_regions.append(region)
                    start_date = start_date + timedelta(days=7)
            else:
                start_date = dt+timedelta(days=7 - dayOfWeek)
                for i in range(0, 4):
                    end_date = start_date + timedelta(days=6)
                    region={"start_time":start_date.strftime("%Y-%m-%d"),"end_time":end_date.strftime("%Y-%m-%d")}
                    regions.append(region)
                    region = {"start_time": start_date.strftime("%m.%d"), "end_time": end_date.strftime("%m.%d")}
                    format_regions.append(region)
                    start_date = start_date + timedelta(days=7)

            user_statistics=[]
            for item in regions:
                start= datetime.strptime(item["start_time"], format)
                end=datetime.strptime(item["end_time"], format)
                start_time=int(time.mktime(start.timetuple()))
                end_time=int( time.mktime(end.timetuple()))

                # 会员数据
                new_user_count=self.db.get("select count(*) as num from users where cast(createtime as unsigned) between %d and %d"%(start_time,end_time))
                #新注册会员数

                new_purchase=self.db.get("select count(distinct userid) as num from purchase where cast(createtime as unsigned)  between %d and %d  "%(start_time,end_time))
                #当周发采购的会员数

                new_quote = self.db.get(
                    "select count(distinct userid) as num from quote where cast(createtime as unsigned)  between %d and %d  " % (
                    start_time, end_time))
                #当周报价的会员数

                # 采购
                purchase_list=self.db.query("select * from purchase where cast(createtime as unsigned)  between %d and %d "%(start_time,end_time))
                purchase_id_list=[]
                for p in purchase_list:
                    purchase_id_list.append(str(p.id))
                print "采购单数"+str(len(purchase_id_list))

                purchaseinfo_num=0
                quote_rate=0
                quote_average =0
                firt_quote_cost=0
                quote_accepte_rate=0

                if (len(purchase_id_list) != 0):
                    purchaseinfo_list=self.db.query("select * from purchase_info where  purchaseid in (%s)"% ",".join(purchase_id_list))
                    purchaseinfo_num = len(purchaseinfo_list)
                    print "新发布采购批次数"+str(purchaseinfo_num)
                    #新发布采购批次数

                    purchaseinfo_id_list=[]
                    for pi in purchaseinfo_list:
                        purchaseinfo_id_list.append(str(pi.id))

                    quote_list=self.db.query("select * from quote where purchaseinfoid in (%s)"% ",".join(purchaseinfo_id_list))
                    quote_rate=round((len(quote_list)/(purchaseinfo_num*1.0))*100, 2)
                    print "报价率"+str(quote_rate)
                    #报价率

                    quote_accepte_list = self.db.query(
                        "select * from quote where  purchaseinfoid in (%s) and state=1" % ",".join(purchaseinfo_id_list))
                    print (len(quote_accepte_list) / (purchaseinfo_num * 1.0))
                    quote_accepte_rate = round((len(quote_accepte_list) / (purchaseinfo_num * 1.0)) * 100, 2)
                    #认可率
                    print "认可率"+str(quote_accepte_rate)


                    quote_average=round((len(quote_list)/(purchaseinfo_num*1.0)), 2)
                    print "平均收到的报价数"+str(quote_average)
                    #平均收到的报价个数
                    first_quote_list = self.db.query(
                        "select distinct purchaseinfoid,createtime from quote where purchaseinfoid in (%s) order by cast(createtime as unsigned)" % ",".join(purchaseinfo_id_list))
                    if(len(first_quote_list)!=0):
                        total_cost=0
                        for qut in first_quote_list:
                            pId=qut.purchaseinfoid
                            quote_time=qut.createtime
                            purchase_info=self.db.get("select * from purchase_info  where id=%d" % pId)
                            purchase=self.db.get("select * from purchase  where id=%s ",purchase_info.purchaseid)
                            purchase_time=purchase.createtime
                            cost=int(quote_time)-int(purchase_time)
                            total_cost=cost+total_cost
                        print total_cost
                        firt_quote_cost=round((total_cost*1.0)/(len(first_quote_list)*(60*60)),2)

                    print "收到第一个报价平均耗时"+str(firt_quote_cost)
                    #收到第一个报价平均耗时

                #报价
                all_quoto_list = self.db.query(
                    "select * from quote where cast(createtime as unsigned)  between %d and %d " % (
                    start_time, end_time))
                all_quoto_num=len(all_quoto_list)
                print "报价个数"+str(all_quoto_num)
                all_quoto_id_list=[]
                for aqil in all_quoto_list:
                    all_quoto_id_list.append(str(aqil.id))
                replay_quote_rate=0
                replay_aceept_quote_rate=0
                replay_quote_cost = 0
                if(all_quoto_num!=0):
                    replay_quote_list = self.db.query(
                        "select * from quote where id in (%s) and state!=0 " % ",".join(all_quoto_id_list))
                    replay_quote_rate = round((len(replay_quote_list) / (all_quoto_num * 1.0)) * 100, 2)
                    print "答复率" + str(replay_quote_rate)

                    replay_aceept_quote_list = self.db.query(
                        "select * from quote where id in (%s) and state=1 " % ",".join(all_quoto_id_list))
                    replay_aceept_quote_rate = round((len(replay_aceept_quote_list) / (all_quoto_num * 1.0)) * 100, 2)
                    print "认可率" + str(replay_aceept_quote_rate)
                    if(len(replay_quote_list)!=0):
                        total_cost=0
                        for qut in replay_quote_list:
                            q_time=qut.createtime
                            r_time=qut.updatetime
                            cost=int( r_time)-int(q_time)
                            total_cost=cost+total_cost
                        print total_cost
                        replay_quote_cost=round((total_cost*1.0)/(len(replay_quote_list)*(60*60)),2)
                    print "平均答复时间"+str(replay_quote_cost)


                region_item={"new_user_count":new_user_count.num,"new_purchase":new_purchase.num,"new_quote":new_quote.num,
                             "purchaseinfo_num":purchaseinfo_num,"quote_rate":quote_rate,"quote_average":quote_average,"firt_quote_cost":firt_quote_cost,"quote_accepte_rate":quote_accepte_rate,
                             "all_quoto_num":all_quoto_num,"replay_quote_rate":replay_quote_rate,"replay_aceept_quote_rate":replay_aceept_quote_rate,"replay_quote_cost": replay_quote_cost
                             }
                user_statistics.append(region_item)

            total_new_user_count=0
            total_new_purchase=0
            total_new_qute=0
            total_purchaseinfo_num=0
            total_quote_rate=0
            total_quote_average=0
            total_quote_accepte_rate=0
            total_firt_quote_cost=0
            total_all_quoto_num=0
            total_replay_quote_rate=0
            total_replay_aceept_quote_rate=0
            total_replay_quote_cost=0

            for item in  user_statistics:
                total_new_user_count=total_new_user_count+item["new_user_count"]
                total_new_purchase=total_new_purchase+item["new_purchase"]
                total_new_qute=total_new_qute+item["new_quote"]
                total_purchaseinfo_num = total_purchaseinfo_num + item["purchaseinfo_num"]
                total_quote_rate =  total_quote_rate + item["quote_rate"]
                total_quote_average = total_quote_average  + item["quote_average"]
                total_quote_accepte_rate= total_quote_accepte_rate + item["quote_accepte_rate"]
                total_firt_quote_cost= total_firt_quote_cost + item["firt_quote_cost"]
                total_all_quoto_num = total_all_quoto_num + item["all_quoto_num"]
                total_replay_quote_rate =total_replay_quote_rate + item["replay_quote_rate"]
                total_replay_aceept_quote_rate =total_replay_aceept_quote_rate  + item["replay_aceept_quote_rate"]
                total_replay_quote_cost = total_replay_quote_cost + item["replay_quote_cost"]
            total_quote_rate=total_quote_rate/4
            total_quote_average=total_quote_average/4
            total_firt_quote_cost=total_firt_quote_cost/4
            total_replay_quote_rate=total_replay_quote_rate/4
            total_replay_aceept_quote_rate=total_replay_aceept_quote_rate/4
            total_replay_quote_cost=total_replay_quote_cost/4
            total_quote_accepte_rate=total_quote_accepte_rate/4



            total = {"new_user_count": total_new_user_count, "new_purchase": total_new_purchase,
                           "new_quote": total_new_qute,
                           "purchaseinfo_num": total_purchaseinfo_num, "quote_rate": total_quote_rate,
                           "quote_average": total_quote_average, "firt_quote_cost": total_firt_quote_cost,
                           "quote_accepte_rate": total_quote_accepte_rate,
                           "all_quoto_num": total_all_quoto_num, "replay_quote_rate": total_replay_quote_rate,
                           "replay_aceept_quote_rate": total_replay_aceept_quote_rate, "replay_quote_cost": total_replay_quote_cost
                           }

            self.render("statistics.html",regions=format_regions,statistics=user_statistics,total=total,month=month)
        else:
            self.send_error(404)

class MonitorBusinessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("business.html")