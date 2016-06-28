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
            format = "%Y-%m-%d"
            date_str="%s-%s-%s"%(year,month,'1')
            dt=datetime.strptime(date_str, format)
            dayOfWeek = dt.weekday()
            #print dayOfWeek
            # 偶数月显示带上个月的那周，奇熟月份只显示本月的
            regions = []
            start_date=""
            format_regions = []
            if int(month)%2==0:
                start_date=dt+timedelta(days=(-1*(dayOfWeek)))
                end_date = start_date + timedelta(days=35)

                region = {"start_time": start_date.strftime("%Y-%m-%d"), "end_time": end_date.strftime("%Y-%m-%d")}
                regions.append(region)

                for i in range(0,5):
                    end_date = start_date + timedelta(days=7)
                    region={"start_time":start_date.strftime("%Y-%m-%d"),"end_time":end_date.strftime("%Y-%m-%d")}
                    regions.append(region)
                    region = {"start_time": start_date.strftime("%m.%d"), "end_time": end_date.strftime("%m.%d")}
                    format_regions.append(region)
                    start_date = start_date + timedelta(days=7)


            else:
                start_date = dt+timedelta(days=7 - dayOfWeek)
                end_date = start_date + timedelta(days=28)

                region = {"start_time": start_date.strftime("%Y-%m-%d"), "end_time": end_date.strftime("%Y-%m-%d")}
                regions.append(region)
                for i in range(0, 4):
                    end_date = start_date + timedelta(days=7)
                    region={"start_time":start_date.strftime("%Y-%m-%d"),"end_time":end_date.strftime("%Y-%m-%d")}
                    regions.append(region)
                    region = {"start_time": start_date.strftime("%m.%d"), "end_time": end_date.strftime("%m.%d")}
                    format_regions.append(region)
                    start_date = start_date + timedelta(days=7)

            user_statistics=[]
            for item in regions:
                #print item
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
                #print "采购单数"+str(len(purchase_id_list))

                purchaseinfo_num=0
                quote_rate=0
                quote_average =0
                firt_quote_cost=0
                quote_accepte_rate=0

                if (len(purchase_id_list) != 0):
                    purchaseinfo_list=self.db.query("select * from purchase_info where  purchaseid in (%s)"% ",".join(purchase_id_list))
                    purchaseinfo_num = len(purchaseinfo_list)
                    #print "新发布采购批次数"+str(purchaseinfo_num)
                    #新发布采购批次数

                    purchaseinfo_id_list=[]
                    for pi in purchaseinfo_list:
                        purchaseinfo_id_list.append(str(pi.id))

                    quote_list=self.db.query("select * from quote where purchaseinfoid in (%s) group by purchaseinfoid"% ",".join(purchaseinfo_id_list))
                    quote_rate=round((len(quote_list)/(purchaseinfo_num*1.0))*100, 2)
                    #print "报价率"+str(quote_rate)
                    #报价率

                    quote_accepte_list = self.db.query(
                        "select * from quote where  purchaseinfoid in (%s) and state=1 group by purchaseinfoid" % ",".join(purchaseinfo_id_list))
                    #print (len(quote_accepte_list) / (purchaseinfo_num * 1.0))
                    quote_accepte_rate = round((len(quote_accepte_list) / (purchaseinfo_num * 1.0)) * 100, 2)
                    #认可率
                    #print "认可率"+str(quote_accepte_rate)

                    ret = self.db.get(
                        "select count(*) as num from quote where  purchaseinfoid in (%s)" % ",".join(
                            purchaseinfo_id_list))

                    quote_num =  ret.num#收到报价总数
                    #print "收到的报价总数"+str(quote_num)
                    if(len(quote_list)!=0):
                        quote_average=round(quote_num/((len(quote_list)*1.0)), 2)
                    else:
                        quote_average =0

                    #print "平均收到的报价数"+str(quote_average)
                    #平均收到的报价个数
                    first_quote_list = self.db.query(
                        "select distinct purchaseinfoid,createtime from quote where purchaseinfoid in (%s) order by cast(createtime as unsigned)" % ",".join(purchaseinfo_id_list))
                    if(len(first_quote_list)!=0):
                        total_cost=0
                        not_count=0
                        for qut in first_quote_list:
                            pId=qut.purchaseinfoid
                            quote_time=qut.createtime
                            purchase_info=self.db.get("select * from purchase_info  where id=%d" % pId)
                            purchase=self.db.get("select * from purchase  where id=%s ",purchase_info.purchaseid)
                            purchase_time=purchase.createtime
                            cost=int(quote_time)-int(purchase_time)
                            if(cost<0):
                                not_count = not_count+1
                            total_cost=cost+total_cost
                        #print total_cost
                        firt_quote_cost=round((total_cost*1.0)/((len(first_quote_list)-not_count)*(60*60)),2)

                    #print "收到第一个报价平均耗时"+str(firt_quote_cost)
                    #收到第一个报价平均耗时

                #报价
                all_quoto_list = self.db.query(
                    "select * from quote where cast(createtime as unsigned)  between %d and %d " % (
                    start_time, end_time))
                all_quoto_num=len(all_quoto_list)
                #print "报价个数"+str(all_quoto_num)
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
                    #print "答复率" + str(replay_quote_rate)

                    replay_aceept_quote_list = self.db.query(
                        "select * from quote where id in (%s) and state=1 " % ",".join(all_quoto_id_list))
                    replay_aceept_quote_rate = round((len(replay_aceept_quote_list) / (all_quoto_num * 1.0)) * 100, 2)
                    #print "认可率" + str(replay_aceept_quote_rate)
                    if(len(replay_quote_list)!=0):
                        total_cost=0
                        for qut in replay_quote_list:
                            q_time=qut.createtime
                            r_time=qut.updatetime
                            cost=int( r_time)-int(q_time)
                            total_cost=cost+total_cost
                        print total_cost
                        replay_quote_cost=round((total_cost*1.0)/(len(replay_quote_list)*(60*60)),2)
                    #print "平均答复时间"+str(replay_quote_cost)


                region_item={"new_user_count":new_user_count.num,"new_purchase":new_purchase.num,"new_quote":new_quote.num,
                             "purchaseinfo_num":purchaseinfo_num,"quote_rate":quote_rate,"quote_average":quote_average,"firt_quote_cost":firt_quote_cost,"quote_accepte_rate":quote_accepte_rate,
                             "all_quoto_num":all_quoto_num,"replay_quote_rate":replay_quote_rate,"replay_aceept_quote_rate":replay_aceept_quote_rate,"replay_quote_cost": replay_quote_cost
                             }
                user_statistics.append(region_item)
            self.render("statistics.html",regions=format_regions,statistics=user_statistics,month=month)
        else:
            self.send_error(404)

class MonitorBusinessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,type=0, starttime=0, endtime=0):

        year = strftime("%Y", localtime())
        mon = strftime("%m", localtime())
        day = strftime("%d", localtime())

        format = "%Y-%m-%d %H:%M"
        if starttime!="" and endtime!="":
            #查指定时间段内的数据
            try:
                if(len(starttime.split(':'))==2):
                    starttime = datetime.strptime(str(starttime), "%Y-%m-%d %H:%M")
                else:
                    starttime = datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S")
                if(len(endtime.split(':'))==2):
                    endtime = datetime.strptime(str(endtime), "%Y-%m-%d %H:%M")
                else:
                    endtime = datetime.strptime(str(endtime), "%Y-%m-%d %H:%M:%S")
            except:
                self.send_error(404)
        else:
            if type=='0':
                starttime=datetime.strptime("%s-%s-%s 00:00" % (year,  mon , day), format)
                endtime=starttime + timedelta(days=1)
            elif type=='1':
                now=datetime.strptime("%s-%s-%s 00:00" % (year,  mon , day), format)
                dayOfWeek = now.weekday()
                starttime=now+timedelta(days=(-1*(dayOfWeek)))
                endtime=starttime + timedelta(days=7)
            elif type=='2':
                starttime=datetime.strptime("%s-%s-%s 00:00" % (year,  mon , '1'), format)
                endtime=starttime + timedelta(days=30)
            else:
                starttime =""
                endtime =""
        purchaseinfo_num=0
        user_num=0
        variety_num=0

        quote_num=0
        quote_rate=0

        not_quote_num=0
        not_quote_rate=0

        no_reply_num=0
        no_reply_rate=0

        accept_num=0
        accept_rate=0

        no_accept_num=0
        no_accept_rate=0

        max_view=0
        average_view=0

        max_quote=0
        average_quote=0

        min_cost=0
        firt_quote_cost=0

        ############
        all_quoto_num=0
        apply_user_num=0
        supply_variety_num=0

        replay_quote_num=0
        replay_quote_rate=0

        no_replay_quote_num=0
        no_replay_quote_rate=0

        replay_aceept_quote_num=0
        replay_aceept_quote_rate=0

        replay_refuse_quote_num=0
        replay_refuse_quote_rate=0

        high_price_num=0
        high_price_rate=0

        low_quality_num=0
        low_quality_rate=0

        replay_quote_cost=0
        min_reply_cost=0

        # 采购情况
        if starttime!="" and endtime!="":
            start_time = int(time.mktime(starttime.timetuple()))
            end_time = int(time.mktime(endtime.timetuple()))
            date_between="and cast(createtime as unsigned) between %d and %d " % (start_time, end_time)
        else:
            date_between =""

        purchase_list = self.db.query(
                "select * from purchase where 1=1 %s" %(date_between))
        purchase_num=len(purchase_list)
        #print "发布采购单"+str(purchase_num)

        if purchase_num!=0:
            purchase_id_list = []
            for p in purchase_list:
                purchase_id_list.append(str(p.id))

            ret=self.db.get("select count(distinct userid) as num from purchase where 1=1 %s" %(date_between))
            user_num=ret.num
            #print "采购商"+str(user_num)

            purchaseinfo_list = self.db.query(
                "select * from purchase_info where  purchaseid in (%s)" % ",".join(purchase_id_list))
            purchaseinfo_id_list = []

            purchaseinfo_num = len(purchaseinfo_list)
            #print "发布采购单批次" + str(purchaseinfo_num)

            for pi in purchaseinfo_list:
                purchaseinfo_id_list.append(str(pi.id))

            ret = self.db.get("select count(distinct varietyid) as num from purchase_info where  purchaseid in (%s)" % ",".join(purchase_id_list))
            variety_num = ret.num
            #print "品种" + str(variety_num)

            quote_list = self.db.query(
                "select * from quote where purchaseinfoid in (%s) group by purchaseinfoid  " % ",".join(purchaseinfo_id_list))
            quote_num=len(quote_list)
            quote_rate=round((quote_num / (len(purchaseinfo_list) * 1.0)) * 100, 2)
            #print "收到报价"+str(quote_num)
            all_quoto_id_list = []
            for aqil in  quote_list:
                all_quoto_id_list.append(str(aqil.id))

            ret = self.db.query("select views  from purchase_info where  purchaseid in (%s) order by views desc" % ",".join(purchase_id_list))
            max_view= ret[0].views
            #print "被查看次数最多的是" + str(max_view)
            total_view = 0
            for item in ret:
                total_view = total_view + item.views
            average_view = round(total_view / (len(ret) * 1.0), 2)
            #print "平均查看次数" + str(average_view)

            if quote_num!=0:
                ret = self.db.get(
                    "select count(distinct purchaseinfoid) as num from quote where  purchaseinfoid in (%s)" % ",".join(purchaseinfo_id_list))
                not_quote_num=len(purchaseinfo_list)-ret.num
                not_quote_rate = round((not_quote_num / (len(purchaseinfo_list) * 1.0)) * 100, 2)
                print "未收到报价"+str(not_quote_num)



                ret = self.db.get(
                    "select count(distinct purchaseinfoid) as num,id from quote where  purchaseinfoid in (%s) and state=1 " % ",".join(purchaseinfo_id_list))
                accept_num=ret.num
                accept_rate = round((accept_num/ (len(purchaseinfo_list) * 1.0)) * 100, 2)
                print "认可的报价" + str(accept_num)

                ret = self.db.query(
                    "select distinct purchaseinfoid  from quote where  purchaseinfoid in (%s) and state=1 " % ",".join(
                        purchaseinfo_id_list))
                accept_purchaseinfoid=[]
                for item in ret:
                    accept_purchaseinfoid.append(str(item.purchaseinfoid))

                if accept_num!=0:
                    ret = self.db.get(
                    "select count(distinct purchaseinfoid) as num from quote where purchaseinfoid in (%s)  and state=%d and purchaseinfoid not in (%s) " % (",".join(purchaseinfo_id_list),2,",".join(accept_purchaseinfoid)))
                    no_accept_num=ret.num
                    no_accept_rate = round((no_accept_num/ (len(purchaseinfo_list) * 1.0)) * 100, 2)
                    print "没有认可的报价" + str(no_accept_num)
                else:
                    ret = self.db.get(
                    "select count(distinct purchaseinfoid) as num from quote where purchaseinfoid in (%s)  and state=%d " % (",".join(purchaseinfo_id_list),2))
                    no_accept_num=ret.num
                    no_accept_rate = round((no_accept_num/ (len(purchaseinfo_list) * 1.0)) * 100, 2)
                    print "没有认可的报价" + str(no_accept_num)


                #ret = self.db.get(
                #    "select count(distinct purchaseinfoid) as num from quote where  purchaseinfoid in (%s) and state=0 and purchaseinfoid not in (%s)" %(",".join(purchaseinfo_id_list),",".join(purchaseinfo_id_list)))
                no_reply_num=quote_num-accept_num-no_accept_num
                no_reply_rate = round((no_reply_num/ (len(purchaseinfo_list) * 1.0)) * 100, 2)
                print "没有答复到报价" + str(no_reply_num)


                ret = self.db.query(
                    "select distinct purchaseinfoid  from quote where  purchaseinfoid in (%s)" % ",".join(purchaseinfo_id_list))
                has_quote_purchaseinfo_list=[]
                for item in ret:
                    has_quote_purchaseinfo_list.append(str(item.purchaseinfoid))

                ret = self.db.query(
                    "SELECT count(*) as num from quote where purchaseinfoid in (%s) GROUP BY purchaseinfoid ORDER BY num desc  " % ",".join(has_quote_purchaseinfo_list))
                max_quote=ret[0].num
                total_quote=0
                for item in ret:
                    total_quote =total_quote+item.num
                average_quote=round(total_quote/ (len(ret) * 1.0), 2)

                #print "平均报价个数"+str(average_quote)
                #print "报价个数最多" + str(max_quote)

                first_quote_list = self.db.query(
                    "select distinct purchaseinfoid,createtime from quote where purchaseinfoid in (%s) order by cast(createtime as unsigned)" % ",".join(
                        purchaseinfo_id_list))
                min_cost=0
                firt_quote_cost=0
                if (len(first_quote_list) != 0):
                    total_cost = 0
                    not_count_num=0
                    for qut in first_quote_list:
                        pId = qut.purchaseinfoid
                        quote_time = qut.createtime
                        purchase_info = self.db.get("select * from purchase_info  where id=%d" % pId)
                        purchase = self.db.get("select * from purchase  where id=%s ", purchase_info.purchaseid)
                        purchase_time = purchase.createtime
                        cost = int(quote_time) - int(purchase_time)
                        if cost<0:
                            not_count_num =not_count_num+1
                        if min_cost==0:
                            min_cost = cost
                        if cost<min_cost and cost>0:
                            min_cost=cost
                        total_cost = cost + total_cost
                    firt_quote_cost = round((total_cost * 1.0) / ((len(first_quote_list)-not_count_num) * (60 * 60)), 2)
                    min_cost=round((min_cost * 1.0) / (60 * 60), 2)
                    #print "平均耗时"+str(firt_quote_cost)
                    #print "最快耗时"+str(min_cost)


        #报价情况
        all_quoto_list = self.db.query(
            "select * from quote where 1=1 %s" %(date_between))
        all_quoto_num = len(all_quoto_list)
        #print "收到报价" + str(all_quoto_num)
        all_quoto_id_list = []
        for aqil in all_quoto_list:
            all_quoto_id_list.append(str(aqil.id))
        ret = self.db.get(
            "select count(distinct userid) as num from quote where 1=1 %s" % (date_between))
        apply_user_num = ret.num
        #print "供货商" + str(apply_user_num)

        quoto_purchinfo_list=self.db.query(
            "select distinct purchaseinfoid from quote where 1=1 %s" %(date_between))
        all_quoto_purchinfo_list = []
        for aqil in quoto_purchinfo_list:
            all_quoto_purchinfo_list.append(str(aqil.purchaseinfoid))
        if(len(all_quoto_purchinfo_list)!=0):
            ret = self.db.get(
                "select count(distinct varietyid) as num from purchase_info where id in (%s)" % ",".join(
                all_quoto_purchinfo_list))
            supply_variety_num = ret.num
            #print "品种" + str(supply_variety_num)

        if (all_quoto_num != 0):
            replay_quote_list = self.db.query(
                "select * from quote where id in (%s) and state!=0 " % ",".join(all_quoto_id_list))
            replay_quote_num=len(replay_quote_list)
            replay_quote_rate = round((replay_quote_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "答复率" + str(replay_quote_rate)

            no_replay_quote_num = all_quoto_num-replay_quote_num
            no_replay_quote_rate = round((no_replay_quote_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "没有答复率" + str(no_replay_quote_rate)



            replay_aceept_quote_list = self.db.query(
                "select * from quote where id in (%s) and state=1 " % ",".join(all_quoto_id_list))
            replay_aceept_quote_num=len(replay_aceept_quote_list)
            replay_aceept_quote_rate = round((replay_aceept_quote_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "认可率" + str(replay_aceept_quote_rate)

            replay_refuse_quote_num = replay_quote_num-replay_aceept_quote_num
            replay_refuse_quote_rate = round((replay_refuse_quote_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "被拒绝" + str(replay_refuse_quote_rate)

            ret = self.db.get(
                "select count(*) as num from quote where id in (%s) and find_in_set('价格偏高',message) " % ",".join(all_quoto_id_list))
            high_price_num=ret.num
            high_price_rate= round((high_price_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "价格偏高"+str(high_price_rate)



            ret = self.db.get(
                "select count(*) as num from quote where id in (%s) and find_in_set('质量不符',message) " % ",".join(
                    all_quoto_id_list))
            low_quality_num = ret.num
            low_quality_rate=round((low_quality_num / (all_quoto_num * 1.0)) * 100, 2)
            #print "质量不符"+str(low_quality_rate)



            min_reply_cost=0
            if (len(replay_quote_list) != 0):
                total_cost = 0
                not_count_num = 0
                for qut in replay_quote_list:
                    q_time = qut.createtime
                    r_time = qut.updatetime
                    cost = int(r_time) - int(q_time)
                    total_cost = cost + total_cost
                    if cost < 0:
                        not_count_num = not_count_num + 1
                    if min_reply_cost == 0:
                        min_reply_cost= cost
                    if cost < min_reply_cost:
                        min_reply_cost = cost

                replay_quote_cost = round((total_cost * 1.0) / ((len(replay_quote_list)-not_count_num) * (60 * 60)), 2)
                #print "平均答复时间" + str(replay_quote_cost)
                min_reply_cost= round((min_reply_cost * 1.0) / (60 * 60), 2)
                #print "最快答复"+str(min_reply_cost)
        purchase_step={
            "purchaseinfo_num":purchaseinfo_num,"user_num":user_num,"variety_num":variety_num,"quote_num":quote_num,"quote_rate":quote_rate,
            "not_quote_num":not_quote_num,"not_quote_rate":not_quote_rate,"no_reply_num":no_reply_num,"no_reply_rate":no_reply_rate,
            "accept_num":accept_num,"accept_rate":accept_rate,"no_accept_num":no_accept_num,"no_accept_rate":no_accept_rate,"max_view":max_view,
            "average_view":average_view,"max_quote":max_quote,"average_quote":average_quote,"min_cost":min_cost,"firt_quote_cost":firt_quote_cost
        }
        quote_step={
            "all_quoto_num":all_quoto_num,"apply_user_num":apply_user_num,"supply_variety_num":supply_variety_num,"replay_quote_num":replay_quote_num,
            "replay_quote_rate":replay_quote_rate,"no_replay_quote_num":no_replay_quote_num,"no_replay_quote_rate":no_replay_quote_rate,"replay_aceept_quote_num":replay_aceept_quote_num,
            "replay_aceept_quote_rate":replay_aceept_quote_rate,"replay_refuse_quote_num":replay_refuse_quote_num,"replay_refuse_quote_rate":replay_refuse_quote_rate,
            "high_price_num":high_price_num,"high_price_rate":high_price_rate,"low_quality_num":low_quality_num,"low_quality_rate":low_quality_rate,"replay_quote_cost":replay_quote_cost,
            "min_reply_cost":min_reply_cost
        }

        self.render("business.html",purchase_step=purchase_step,quote_step=quote_step,type=type,starttime=starttime, endtime=endtime)