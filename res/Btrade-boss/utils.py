# -*- coding: utf-8 -*-

import thread,config
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

def acceptQuote(phone, name, variety, price, unit, number):
    templateId = 865
    phone = phone
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+price+'","%unit%":"'+unit+'","%phone%":"'+number+'"}'
    print vars
    thread.start_new_thread(send, (templateId, phone, vars))

def rejectQuote(phone, name, variety, price, unit, message):
    templateId = 868
    phone = phone
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+price+'","%unit%":"'+unit+'","%message%":"'+message+'"}'
    thread.start_new_thread(send, (templateId, phone, vars))

def pushPurchase(phones, purchase):
    templateId = 870
    for (k,v) in purchase.items():
        purchase[k] = purchase[k].encode('utf-8') if isinstance(purchase[k], unicode) else purchase[k]
    vars = '{"%purchaseinfoid%":"'+str(purchase["purchaseinfoid"])+'","%variety%":"'+purchase["variety"]+'","%name%":"'+purchase["name"]+'","%specification%":"'+purchase["specification"]+'","%quantity%":"'+purchase["quantity"]+'","%unit%":"'+purchase["unit"]+'"}'
    tos = []
    for phone in phones:
        phone = phone.encode('utf-8') if isinstance(phone, unicode) else phone
        tos.append('{"phone": "'+phone+'", "vars": '+vars+'}')
    tos = "["+",".join(tos)+"]"
    thread.start_new_thread(sendx, (templateId, tos))

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
           "value":"点击“详情”，立即联系采购商",
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
           "value":"点击“详情”，您可重新报价",
           "color":"#173177"
        }
    }
    thread.start_new_thread(sendwx, (templateId, openid, link, data))

def pushPurchaseWx(openids, purchase):
    templateId = 'OxXsRhlyc17kt6ubwV7F0fD8ffRl12rGGS3mnpvpoU4'
    link = 'http://m.yaocai.pro/purchase/purchaseinfo/%s' % purchase["purchaseinfoid"]
    qtime = int(purchase["createtime"])
    purchase["name"] = purchase["name"].encode('utf-8') if isinstance(purchase["name"], unicode) else purchase["name"]
    purchase["variety"] = purchase["variety"].encode('utf-8') if isinstance(purchase["variety"], unicode) else purchase["variety"]
    purchase["specification"] = purchase["specification"].encode('utf-8') if isinstance(purchase["specification"], unicode) else purchase["specification"]
    purchase["origin"] = purchase["origin"].encode('utf-8') if isinstance(purchase["origin"], unicode) else purchase["origin"]
    purchase["quality"] = purchase["quality"].encode('utf-8') if isinstance(purchase["quality"], unicode) else purchase["quality"]
    purchase["quantity"] = purchase["quantity"].encode('utf-8') if isinstance(purchase["quantity"], unicode) else purchase["quantity"]
    purchase["unit"] = purchase["unit"].encode('utf-8') if isinstance(purchase["unit"], unicode) else purchase["unit"]
    for openid in openids:
        openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
        data = {
            "first": {
               "value":"%s 邀请您报价" % purchase["name"],
               "color":"#173177"
            },
            "keyword1": {
               "value":"%s（%s），产地：%s，%s" % (purchase["variety"],purchase["specification"],purchase["origin"],purchase["quality"]),
               "color":"#173177"
            },
            "keyword2": {
               "value":"%s%s" % (purchase["quantity"],purchase["unit"]),
               "color":"#173177"
            },
            "keyword3":{
               "value":time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
               "color":"#173177"
            },
            "remark":{
               "value":"点击“详情”，立即报价",
               "color":"#173177"
            }
        }
        thread.start_new_thread(sendwx, (templateId, openid, link, data))
        time.sleep(5)