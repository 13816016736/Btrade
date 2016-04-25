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
    thread.start_new_thread(send, (templateId, phone, vars.encode("utf-8")))

def rejectQuote(phone, name, variety, price, unit, message):
    templateId = 868
    phone = phone
    vars = '{"%name%":"'+name+'","%variety%":"'+variety+'","%price%":"'+price+'","%unit%":"'+unit+'","%message%":"'+message+'"}'
    thread.start_new_thread(send, (templateId, phone, vars.encode("utf-8")))

def pushPurchase(phones, purchase):
    templateId = 870
    for (k,v) in purchase.items():
        purchase["%"+k+"%"] = purchase.pop(k).encode('utf-8') if isinstance(purchase[k], unicode) else purchase.pop(k)
    for phone in phones:
        phone["phone"] = phone["phone"].encode('utf-8') if isinstance(phone["phone"], unicode) else phone["phone"]
        phone["vars"] = purchase
    thread.start_new_thread(sendx, (templateId, phones))