# -*- coding:utf-8 -*-

from __future__ import absolute_import

#CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/5'
#BROKER_URL = 'redis://127.0.0.1:6379/6'

CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": "jobs",
    "taskmeta_collection": "stock_taskmeta_collection",
}
BROKER_URL = 'mongodb://localhost:27017/jobs'

from celery.schedules import crontab
#定时任务
CELERYBEAT_SCHEDULE = {
    'analysis_record': {
         'task': 'pushengine.tasks.analysis_record',
         'schedule':  crontab(hour=10,minute=0),
         'args': ()
    },
    'analysis_notify': {
        'task': 'pushengine.tasks.analysis_notify',
        'schedule':  crontab(hour=10,minute=0),
        'args': ()
    },
    'monitor_click': {
        'task': 'pushengine.tasks.monitor_click',
        'schedule': crontab(hour=10, minute=0),
        'args': ()
    },

}
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_FORCE_EXECV = True
