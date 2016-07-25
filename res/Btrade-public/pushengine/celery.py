# -*- coding:utf-8 -*-
from __future__ import absolute_import
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
from celery import Celery, platforms

celerysever = Celery('pushengine', include=['pushengine.tasks'])
platforms.C_FORCE_ROOT = True

celerysever.config_from_object('pushengine.config')

if __name__ == '__main__':
    celerysever.start()
