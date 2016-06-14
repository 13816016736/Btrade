# -*- coding: utf-8 -*-
import random,thread,config
from sendsms import *
from sendwechart import *

def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''

def get_day_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当天的起始时间戳，N为负数时前数N天，N为正数是后数N天
    """
    return int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime(ts)),'%Y-%m-%d'))) + 86400*N

def get_week_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当周的开始时间戳，N为负数时前数N周，N为整数是后数N周，此函数将周一作为周的第一天
    """
    w = int(time.strftime('%w',time.localtime(ts)))
    """
    w表示星期几（0-6），当时星期天时w为0，则计算出来的时候一周起始时间为下周的周一，比如今天是2016年2月21日星期天，
    正常是当周第一天时2016年2月15日星期一，但是这里w为0的话，则把2016年2月22日当成当周第一天，则有问题，故当w为0时把该值改成7
    """
    w = 7 if w == 0 else w
    return get_day_begin(int(ts - (w-1)*86400)) + N*604800

def get_month_begin(ts = time.time(),N = 0):
    """
    N为0时获取时间戳ts当月的开始时间戳，N为负数前数N月，N为正数后数N月
    """
    month_day = {1:31,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    cur_y,cur_m,cur_d = [int(x) for x in time.strftime('%Y-%m-%d',time.localtime(ts)).split('-')]
    if (cur_y%4 == 0 and cur_y%100 != 0) or cur_y%400 == 0:
        month_day[2] = 29
    else:
        month_day[2] = 28
    t = get_day_begin(ts) - (cur_d-1)*86400
    real_month = N + cur_m
    if real_month == cur_m:
        return t
    if N > 0:
        if real_month <= 12:
            for x in xrange(cur_m,real_month):
                t += month_day[x]*86400
        if real_month > 12:
            for x in xrange(cur_m,13):
                t += month_day[x]*86400
            t = get_month_begin(t,real_month - 13)
    if N < 0:
        if real_month >= 1:
            for x in xrange(real_month,cur_m):
                t -= month_day[x]*86400
        if real_month < 1:
            for x in xrange(1,cur_m):
                t -= month_day[x]*86400
            t -= month_day[12]*86400
            t = get_month_begin(t,real_month)
    return t

def get_purchaseid():
    rand = ''.join(random.sample(['0','1','2','3','4','5','6','7','8','9'], 2))
    return int(str(int(time.time())) + rand)

#!/usr/bin/env python
#coding=utf-8
'''
Created on 2016-2-22

@author: kevin
'''
import os
import glob
import time
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def make_thumb(path, thumb_path, w, h):
    """生成缩略图"""
    img = Image.open(path)
    width, height = img.size
    # 裁剪图片成正方形
    if width > height:
        delta = (width - height) / 2
        box = (delta, 0, width - delta, height)
        region = img.crop(box)
    elif height > width:
        delta = (height - width) / 2
        box = (0, delta, width, height - delta)
        region = img.crop(box)
    else:
        region = img

    # 缩放
    thumb = region.resize((w, h), Image.ANTIALIAS)

    base, ext = os.path.splitext(os.path.basename(path))
    filename = os.path.join(thumb_path, '%s_thumb%s' % (base,ext))
    print filename
    # 保存
    thumb.save(filename, quality=70)

def getSmsCode(phone, code):
    templateId = 776
    phone = phone
    vars = '{"%code%":"'+code+'"}'
    return send(templateId, phone, vars)

def sendRegInfo(phone, username, password):
    templateId = 815
    phone = phone
    vars = '{"%username%":"'+username+'","%password%":"'+password+'"}'
    thread.start_new_thread(send, (templateId, phone, vars))

def regInfo(phone, name, password):
    templateId = 861
    phone = phone
    vars = '{"%name%":"'+name+'","%password%":"'+password+'"}'
    thread.start_new_thread(send, (templateId, phone, vars.encode("utf-8")))

def regSuccess(phone, name, username):
    templateId = 862
    phone = phone
    vars = '{"%name%":"'+name+'","%username%":"'+username+'"}'
    thread.start_new_thread(send, (templateId, phone, vars.encode("utf-8")))

def acceptQuote(phone, name, variety, price, unit, number):
    templateId = 865
    phone = phone
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+str(price)+'","%unit%":"'+unit+'","%phone%":"'+number+'"}'
    thread.start_new_thread(send, (templateId, phone, vars))

def rejectQuote(phone, name, variety, price, unit, message):
    templateId = 868
    phone = phone
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+str(price)+'","%unit%":"'+unit+'","%message%":"'+message+'"}'
    thread.start_new_thread(send, (templateId, phone, vars))

def merge_thumb(files, output_file):
    """合并图片"""
    imgs = []
    width = 0
    height = 0

    # 计算总宽度和长度
    for file in files:
        img = Image.open(file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        imgs.append(img)
        if img.size[0] > width:
            width = img.size[0]
        height += img.size[1]

    # 新建一个白色底的图片
    merge_img = Image.new('RGB', (width, height), 0xffffff)
    cur_height = 0
    for img in imgs:
        # 把图片粘贴上去
        merge_img.paste(img, (0, cur_height))
        cur_height += img.size[1]

    merge_img.save(output_file, quality=70)

import MySQLdb

def purchasetransaction(self, data):
    if self.db._db is None:
        self.db._ensure_connected()
    self.db._db.begin()
    cursor = self.db._cursor()
    status = True
    try:
        purchaseid = get_purchaseid()
        cursor.execute("insert into purchase (id, userid, areaid, invoice, pay, payday, payinfo,"
                                                  " send, receive, accept, other, supplier, remark, limited, term, createtime)"
                                                  "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                  (purchaseid, self.session.get("userid"), data["address"], data['invoice'], data['paytype'],
                                                  data['payday'], data['payinfo'], data['sample'], data['contact'],
                                                  data['demand'], data['replenish'], data['permit'], data['others'],0,
                                                  data['deadline'], int(time.time())))
        #存储采购品种信息
        varids = []
        for i,purchase in data['purchases'].iteritems():
            varids.append(purchase["nVarietyId"])
            purchase['nPrice'] = purchase['nPrice'] if purchase['nPrice'] else 0
            cursor.execute("insert into purchase_info (purchaseid, varietyid, name, specification, quantity, unit,"
                            " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                             (purchaseid, purchase["nVarietyId"], purchase['nVariety'], purchase['nRank'],
                            purchase['nQuantity'], purchase['nUnit'], ",".join([ q for q in purchase['nQuality'] if q != '' ]),
                            ",".join([ a for a in purchase['nArea'] if a != '' ]), purchase['nPrice']))
            print cursor.lastrowid
            #插入图片
            if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(i):
                for attachment in self.session.get("uploadfiles")[i]:
                    cursor.execute("insert into purchase_attachment (purchase_infoid, attachment)"
                                      "value(%s, %s)", (cursor.lastrowid, attachment))
                self.session["uploadfiles"] = {}
                self.session.save()
        self.db._db.commit()
    except MySQLdb.OperationalError, e:
        self.db._db.rollback()
        status = False
        raise Exception(e.args[1], e.args[0])
    finally:
        cursor.close()
    return status,purchaseid,varids

def updatepurchase(self, id, data):
    if self.db._db is None:
        self.db._ensure_connected()
    self.db._db.begin()
    cursor = self.db._cursor()
    status = True
    try:
        cursor.execute("update purchase set areaid=%s, invoice=%s, pay=%s, payday=%s, payinfo=%s,"
                                                  " send=%s, receive=%s, accept=%s, other=%s, supplier=%s, remark=%s,"
                                                  " limited=%s, term=%s, createtime=%s where id = %s and userid = %s",
                                                  (data["address"], data['invoice'], data['paytype'], data['payday'],
                                                  data['payinfo'], data['sample'], data['contact'], data['demand'],
                                                  data['replenish'], data['permit'], data['others'], 0,
                                                  data['deadline'], int(time.time()), id, self.session.get("userid")))
        #搜出当前采购单中的品种，以备下面插入新采购单后删除
        cursor.execute("select id from purchase_info where purchaseid = %s" % (id))
        purchaseinfoids = [str(purchaseinfo[0]) for purchaseinfo in cursor.fetchall()]
        #存储采购品种信息
        varids = []
        for i,purchase in data['purchases'].iteritems():
            varids.append(purchase["nVarietyId"])
            purchase['nPrice'] = purchase['nPrice'] if purchase['nPrice'] else 0
            cursor.execute("insert into purchase_info (purchaseid, varietyid, name, specification, quantity, unit,"
                            " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (id, purchase["nVarietyId"], purchase['nVariety'], purchase['nRank'],
                            purchase['nQuantity'], purchase['nUnit'], ",".join([ q for q in purchase['nQuality'] if q != '' ]),
                            ",".join([ a for a in purchase['nArea'] if a != '' ]), purchase['nPrice']))
            #插入图片
            if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(i):
                for attachment in self.session.get("uploadfiles")[i]:
                    cursor.execute("insert into purchase_attachment (purchase_infoid, attachment)"
                                      "value(%s, %s)", (cursor.lastrowid, attachment))
        self.session["uploadfiles"] = {}
        self.session.save()
        #删除采购品种带的附件
        cursor.execute("select attachment from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
        # try:
        #     for attachment in cursor.fetchall():
        #         os.remove(attachment[0])
        # except Exception,ex:
        #     print Exception,":",ex
        cursor.execute("delete from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
        #删除采购品种
        cursor.execute("delete from purchase_info where id in ("+",".join(purchaseinfoids)+")")
        self.db._db.commit()
    except MySQLdb.OperationalError, e:
        self.db._db.rollback()
        status = False
        raise Exception(e.args[1], e.args[0])
    finally:
        cursor.close()
    return status,varids

"""
判断unicode码是否为中文字符.
"""
def is_cn(check_unicode):
    bool = True
    for ch in check_unicode:
        if ch < u'\u4e00' or ch > u'\u9fff':
            return False
    return bool

def regSuccessWx(openid, name, username):
    templateId = 'R49JXzySURAo-dgzpGtH1EDYXzgxgWVPYg3rQcuNzes'
    link = 'm.yaocai.pro'
    data = {
        "first": {
           "value":"%s，欢迎成为药材购会员！" % name,
           "color":"#173177"
        },
        "keyword1":{
           "value":username,
           "color":"#173177"
        },
        "keyword2": {
           "value":"****",
           "color":"#173177"
        },
        "remark":{
           "value":"点击“详情”，设置您的关注品种，为您推送药厂、饮片厂实时采购单，随时随地报价。",
           "color":"#173177"
        }
    }
    thread.start_new_thread(sendwx, (templateId, openid, link, data))

#采购方对报价进行回复（认可报价）,通知给供应方
def acceptQuoteWx(openid, quoteid, name, variety, price, nickname, phone, qtime):
    openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    variety = variety.encode('utf-8') if isinstance(variety, unicode) else variety
    price = price.encode('utf-8') if isinstance(price, unicode) else price
    nickname = nickname.encode('utf-8') if isinstance(nickname, unicode) else nickname
    phone = phone.encode('utf-8') if isinstance(phone, unicode) else phone
    templateId = 'cMVE072AVpbdV03yKQMTRPc619n8JmtGuUgOpiaFkdA'
    link = 'http://m.yaocai.pro/quotedetail/quoteid/%s/nid/0' % quoteid
    data = {
        "first": {
           "value":"报价被认可，请尽快联系",
           "color":"#173177"
        },
        "keyword1": {
           "value":name,
           "color":"#173177"
        },
        "keyword2":{
           "value":time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
           "color":"#173177"
        },
        "keyword3": {
           "value":"对您%s {%s元/%s}的报价感兴趣。请尽快联系：%s，%s" % (variety,price,config.unit,phone,nickname),
           "color":"#173177"
        },

        "remark":{
           "value":"点击“详情”立即查看，并请尽快答复！及早答复报价，将为您累计信用，能收到更多优质报价。",
           "color":"#173177"
        }
    }
    thread.start_new_thread(sendwx, (templateId, openid, link, data))

#采购方对报价进行回复（拒绝报价）,通知给供应方
def rejectQuoteWx(openid, quoteid, name, variety, price, message, qtime):
    openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    variety = variety.encode('utf-8') if isinstance(variety, unicode) else variety
    price = price.encode('utf-8') if isinstance(price, unicode) else price
    message = message.encode('utf-8') if isinstance(message, unicode) else message
    templateId = 'cMVE072AVpbdV03yKQMTRPc619n8JmtGuUgOpiaFkdA'
    link = 'http://m.yaocai.pro/quotedetail/quoteid/%s/nid/0' % quoteid
    data = {
        "first": {
           "value":"报价被拒绝",
           "color":"#173177"
        },
        "keyword1": {
           "value":name,
           "color":"#173177"
        },
        "keyword2":{
           "value":time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
           "color":"#173177"
        },
        "keyword3": {
           "value":"对您%s {%s元/%s}的报价表示不合适，理由：%s" % (variety,price,config.unit,message),
           "color":"#173177"
        },

        "remark":{
           "value":"点击“详情”立即查看，并请尽快答复！及早答复报价，将为您累计信用，能收到更多优质报价。",
           "color":"#173177"
        }
    }
    thread.start_new_thread(sendwx, (templateId, openid, link, data))

if __name__ == '__main__':
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    IMG_PATH = os.path.join(ROOT_PATH, 'img')
    THUMB_PATH = os.path.join(IMG_PATH, 'thumbs')
    if not os.path.exists(THUMB_PATH):
        os.makedirs(THUMB_PATH)

    # 生成缩略图
    files = glob.glob(os.path.join(IMG_PATH, '*.jpg'))
    begin_time = time.clock()
    for file in files:
        make_thumb(file, THUMB_PATH, 90)
    end_time = time.clock()
    print ('make_thumb time:%s' % str(end_time - begin_time))

    # 合并图片
    files = glob.glob(os.path.join(THUMB_PATH, '*_thumb.jpg'))
    merge_output = os.path.join(THUMB_PATH, 'thumbs.jpg')
    begin_time = time.clock()
    merge_thumb(files, merge_output)
    end_time = time.clock()
    print ('merge_thumb time:%s' % str(end_time - begin_time))

    t = time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_day_begin(t,1)))
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_week_begin(t,1)))
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_month_begin(t,-3)))
    print get_purchaseid()