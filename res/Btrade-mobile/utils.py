# -*- coding: utf-8 -*-
import time
import random

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

if __name__ == "__main__":
    t = time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_day_begin(t,1)))
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_week_begin(t,1)))
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_month_begin(t,-3)))
    print get_purchaseid()