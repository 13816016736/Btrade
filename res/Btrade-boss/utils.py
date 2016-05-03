# -*- coding: utf-8 -*-

import thread
from sendsms import *

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
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+price+'","%unit%":"'+unit+'","%number%":"'+number+'"}'
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