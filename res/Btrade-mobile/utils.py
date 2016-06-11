# -*- coding: utf-8 -*-
import random,thread,config,config,time
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

def getSmsCode(phone, code):
    templateId = 776
    phone = phone
    vars = '{"%code%":"'+code+'"}'
    return send(templateId, phone, vars)

def regSuccess(phone, name, username):
    templateId = 863
    phone = phone
    vars = '{"%name%":"'+name+'","%username%":"'+username+'"}'
    thread.start_new_thread(send, (templateId, phone, vars.encode("utf-8")))

def quoteSms(phone, variety, name, price, unit):
    variety = variety.encode('utf-8') if isinstance(variety, unicode) else variety
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    price = price.encode('utf-8') if isinstance(price, unicode) else price
    unit = unit.encode('utf-8') if isinstance(unit, unicode) else unit
    templateId = 864
    phone = phone.encode('utf-8') if isinstance(phone, unicode) else phone
    vars = '{"%variety%":"'+variety+'","%name%":"'+name+'","%price%":"'+price+'","%unit%":"'+unit+'"}'
    thread.start_new_thread(send, (templateId, phone, vars))

import hashlib

def checkSignature(signature, timestamp, nonce):
    token = config.token
    tmpArr = [token, timestamp, nonce].sort()
    tmpStr = hashlib.sha1("".join(tmpArr)).hexdigest()
    return (tmpStr == signature)

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
    openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    username = username.encode('utf-8') if isinstance(username, unicode) else username
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

#供应商报价,通知给采购方
def quoteWx(openid, purchaseinfoid, variety, name, price, unit, quality, qtime):
    openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
    variety = variety.encode('utf-8') if isinstance(variety, unicode) else variety
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    price = price.encode('utf-8') if isinstance(price, unicode) else price
    unit = unit.encode('utf-8') if isinstance(unit, unicode) else unit
    quality = quality.encode('utf-8') if isinstance(quality, unicode) else quality
    templateId = 'aUADL3alEqWYfs5pEM1X5dtm3pstmrxMt1ktrMNs1qk'
    link = 'www.yaocai.pro/mypurchase/info/%s' % purchaseinfoid
    data = {
        "first": {
           "value":"您好，%s收到新报价" % variety,
           "color":"#173177"
        },
        "keyword1":{
           "value":time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
           "color":"#173177"
        },
        "keyword2": {
           "value":name,
           "color":"#173177"
        },
        "keyword3": {
           "value":variety,
           "color":"#173177"
        },
        "keyword4": {
           "value":"%s元/%s，%s" % (price, unit, quality),
           "color":"#173177"
        },
        "remark":{
           "value":"点击“详情”立即查看，并请尽快答复！及早答复报价，将为您累计信用，能收到更多优质报价。",
           "color":"#173177"
        }
    }
    thread.start_new_thread(sendwx, (templateId, openid, link, data))

#供应商报价,通知给供应商报价成功
def quoteSuccessWx(openid, name, variety, spec, quantity, price, unit, quality, qtime):
    openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
    name = name.encode('utf-8') if isinstance(name, unicode) else name
    variety = variety.encode('utf-8') if isinstance(variety, unicode) else variety
    spec = spec.encode('utf-8') if isinstance(spec, unicode) else spec
    quantity = quantity.encode('utf-8') if isinstance(quantity, unicode) else quantity
    price = price.encode('utf-8') if isinstance(price, unicode) else price
    unit = unit.encode('utf-8') if isinstance(unit, unicode) else unit
    quality = quality.encode('utf-8') if isinstance(quality, unicode) else quality
    templateId = 'RGAztJ6ocuwvJosRCsCCJd8imGif6TT8B7vXYPa_KGs'
    link = 'm.yaocai.pro'
    data = {
        "first": {
           "value":"报价成功",
           "color":"#173177"
        },
        "keyword1": {
           "value":"%s 采购 %s（%s）%s%s" % (name,variety,spec,quantity,unit),
           "color":"#173177"
        },
        "keyword2": {
           "value":quality,
           "color":"#173177"
        },
        "keyword3": {
           "value":"%s元/%s" % (price, config.unit),
           "color":"#173177"
        },
        "keyword4":{
           "value":time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
           "color":"#173177"
        },
        "remark":{
           "value":"药材购已通知采购商尽快查看并给您答复！点击“详情”可以查看更多您在经营品种的采购单，立刻报价",
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